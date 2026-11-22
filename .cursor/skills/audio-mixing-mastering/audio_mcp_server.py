"""
Audio MCP Server — reference implementation
Tools: analyze_audio, diagnose_mix, apply_mastering_chain, render_master, qc_check
Deps: pip install mcp soundfile librosa pyloudnorm numpy scipy
Run:  python audio_mcp_server.py
"""

import json
import os
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf
import pyloudnorm as pyln
import librosa
from scipy.signal import butter, filtfilt

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# ---------- Knowledge base (subset — full in mixing_mastering_schema.json) ----------

GENRE_TARGETS = {
    "pop":       {"lufs": (-10, -8), "dbtp": -1.0, "plr": (7, 10)},
    "hip_hop":   {"lufs": (-9, -7),  "dbtp": -1.0, "plr": (6, 9)},
    "rock":      {"lufs": (-11, -9), "dbtp": -1.0, "plr": (8, 11)},
    "electronic":{"lufs": (-9, -7),  "dbtp": -1.0, "plr": (6, 9)},
    "rnb":       {"lufs": (-11, -9), "dbtp": -1.0, "plr": (8, 10)},
    "acoustic":  {"lufs": (-14, -11),"dbtp": -1.0, "plr": (10, 14)},
    "classical": {"lufs": (-20, -16),"dbtp": -1.0, "plr": (12, 20)},
    "ambient":   {"lufs": (-18, -14),"dbtp": -1.0, "plr": (14, 20)},
    "latin":     {"lufs": (-10, -8), "dbtp": -1.0, "plr": (6, 9)},
}

# ---------- Audio helpers ----------

def load_audio(path):
    audio, sr = sf.read(path, always_2d=True)
    audio = audio.astype(np.float64)
    if audio.shape[1] > 2:
        audio = audio[:, :2]
    return audio, sr


def true_peak_db(audio, sr, oversample=4):
    """Interpolated peak estimate (simplified ITU-R BS.1770)."""
    y = librosa.resample(audio.T, orig_sr=sr, target_sr=sr * oversample)
    return 20 * np.log10(np.max(np.abs(y)) + 1e-12)


def lufs_integrated(audio, sr):
    meter = pyln.Meter(sr)
    return meter.integrated_loudness(audio)


def peak_to_loudness(audio, sr):
    lufs = lufs_integrated(audio, sr)
    peak = 20 * np.log10(np.max(np.abs(audio)) + 1e-12)
    return peak - lufs


def mono_loss_db(audio, sr, low_hz=120):
    """Loss when summing to mono, in low band."""
    if audio.shape[1] < 2:
        return 0.0
    mid = (audio[:, 0] + audio[:, 1]) / 2
    b, a = butter(4, low_hz / (sr / 2), btype="low")
    lo_mid = filtfilt(b, a, mid)
    lo_l = filtfilt(b, a, audio[:, 0])
    lo_r = filtfilt(b, a, audio[:, 1])
    stereo_power = np.mean(lo_l**2 + lo_r**2)
    mono_power = np.mean(lo_mid**2) * 2
    if stereo_power <= 0:
        return 0.0
    return 10 * np.log10(stereo_power / (mono_power + 1e-12))


def phase_corr(audio):
    if audio.shape[1] < 2:
        return 1.0
    return float(np.corrcoef(audio[:, 0], audio[:, 1])[0, 1])


def has_clipping(audio):
    return bool(np.any(np.abs(audio) >= 1.0))


# ---------- Tool implementations ----------

def analyze_audio(file_path, measurements=None):
    audio, sr = load_audio(file_path)
    result = {"file": file_path, "sample_rate": sr, "channels": audio.shape[1],
              "duration_s": round(audio.shape[0] / sr, 2)}
    if not measurements or "lufs" in measurements:
        result["lufs_i"] = round(lufs_integrated(audio, sr), 2)
    if not measurements or "dbtp" in measurements:
        result["true_peak_dbtp"] = round(true_peak_db(audio, sr), 2)
    if not measurements or "plr" in measurements:
        result["plr"] = round(peak_to_loudness(audio, sr), 2)
    if not measurements or "phase" in measurements:
        result["phase_corr"] = round(phase_corr(audio), 3)
    if not measurements or "mono" in measurements:
        result["mono_loss_db_100hz"] = round(mono_loss_db(audio, sr), 2)
    if not measurements or "peak" in measurements:
        result["clipping"] = has_clipping(audio)
    return result


def diagnose_mix(file_path, target_genre, reference_files=None):
    audio, sr = load_audio(file_path)
    lufs = lufs_integrated(audio, sr)
    tp = true_peak_db(audio, sr)
    plr = peak_to_loudness(audio, sr)
    mloss = mono_loss_db(audio, sr)
    corr = phase_corr(audio)
    clip = has_clipping(audio)

    issues = []
    target = GENRE_TARGETS.get(target_genre, {})

    if clip:
        issues.append({"category": "clipping", "severity": "critical",
                       "description": "Samples at 0 dBFS",
                       "recommended_fix": "Re-export with -6 dBFS headroom"})
    if lufs < (target.get("lufs", (-99, 99))[0] - 1):
        issues.append({"category": "loudness", "severity": "warning",
                       "description": f"{lufs:.1f} LUFS below genre target",
                       "recommended_fix": "Apply mastering chain with target LUFS"})
    if lufs > (target.get("lufs", (-99, 99))[1] + 1):
        issues.append({"category": "loudness", "severity": "warning",
                       "description": f"{lufs:.1f} LUFS above genre target",
                       "recommended_fix": "Reduce limiter drive"})

    if plr < target.get("plr", (0, 99))[0]:
        issues.append({"category": "dynamics", "severity": "warning",
                       "description": f"PLR {plr:.1f} below genre minimum — crushed",
                       "recommended_fix": "Reduce compression/limiting"})

    if mloss > 3.0:
        issues.append({"category": "phase", "severity": "critical",
                       "location_hz": 100,
                       "description": f"Mono loss {mloss:.1f} dB at 100 Hz",
                       "recommended_fix": "Check bass phase; mono the sub"})

    if corr < 0:
        issues.append({"category": "phase", "severity": "warning",
                       "description": f"Negative phase correlation {corr:.2f}",
                       "recommended_fix": "Inspect stereo widening; check phase invert"})

    return_to_mix = any(i["severity"] == "critical" for i in issues)

    return {
        "issues": issues,
        "return_to_mix_required": return_to_mix,
        "reason": "critical issues detected" if return_to_mix else "acceptable",
        "metrics": {"lufs_i": round(lufs, 2), "dbtp": round(tp, 2),
                    "plr": round(plr, 2), "mono_loss_db": round(mloss, 2),
                    "phase_corr": round(corr, 3)}
    }


def apply_mastering_chain(file_path, genre, target_lufs=None, target_dbtp=-1.0):
    audio, sr = load_audio(file_path)
    target = GENRE_TARGETS.get(genre, {})
    if target_lufs is None:
        target_lufs = sum(target.get("lufs", (-12, -12))) / 2

    # 1. HPF (30 Hz butterworth, skip classical)
    if genre != "classical":
        b, a = butter(4, 30 / (sr / 2), btype="high")
        audio = filtfilt(b, a, audio, axis=0)

    # 2. Mono bass <100 Hz
    if audio.shape[1] == 2:
        b, a = butter(4, 100 / (sr / 2), btype="low")
        low = filtfilt(b, a, audio, axis=0)
        mid = audio - low
        mono_low = np.mean(low, axis=1, keepdims=True)
        audio = mid + np.repeat(mono_low, 2, axis=1)

    # 3. Loudness normalize to target
    current = lufs_integrated(audio, sr)
    gain_db = target_lufs - current
    audio *= 10 ** (gain_db / 20)

    # 4. True-peak safety (limiter approximation)
    tp = true_peak_db(audio, sr)
    if tp > target_dbtp:
        ceiling_lin = 10 ** (target_dbtp / 20)
        audio = np.tanh(audio / ceiling_lin) * ceiling_lin

    final_lufs = lufs_integrated(audio, sr)
    final_tp = true_peak_db(audio, sr)

    return {
        "chain_applied": ["hpf_30hz", "mono_bass_100hz",
                          "loudness_normalize", "true_peak_limit"],
        "final_lufs": round(final_lufs, 2),
        "final_dbtp": round(final_tp, 2),
        "gain_applied_db": round(gain_db, 2),
        "warnings": [] if final_tp <= target_dbtp + 0.2
                    else [f"TP {final_tp:.2f} exceeds ceiling {target_dbtp}"]
    }


def render_master(source_file, output_path, delivery_spec="streaming_master",
                  dither=True):
    audio, sr = load_audio(source_file)

    spec = {
        "streaming_master": {"bit_depth": 24, "tp": -1.0},
        "cd_master":        {"bit_depth": 16, "tp": -0.3, "resample": 44100},
        "vinyl_premaster":  {"bit_depth": 24, "tp": -3.0},
        "club_dj":          {"bit_depth": 24, "tp": -0.5},
        "instrumental_tv":  {"bit_depth": 24, "tp": None},
        "stems":            {"bit_depth": 24, "tp": None},
    }.get(delivery_spec, {"bit_depth": 24, "tp": -1.0})

    tp = true_peak_db(audio, sr)
    if spec["tp"] is not None and tp > spec["tp"]:
        ceiling_lin = 10 ** (spec["tp"] / 20)
        audio = np.tanh(audio / ceiling_lin) * ceiling_lin

    out_sr = spec.get("resample", sr)
    if out_sr != sr:
        audio = librosa.resample(audio.T, orig_sr=sr, target_sr=out_sr).T

    out_bits = spec["bit_depth"]
    if dither and out_bits == 16:
        audio += (np.random.randn(*audio.shape) * (1 / 32768)) / 3

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    sf.write(output_path, audio, out_sr, subtype=f"PCM_{out_bits}")

    return {
        "rendered": True,
        "output_path": output_path,
        "final_lufs": round(lufs_integrated(audio, out_sr), 2),
        "final_dbtp": round(true_peak_db(audio, out_sr), 2),
        "bit_depth": out_bits,
        "sample_rate": out_sr
    }


def qc_check(file_path, genre, delivery_spec="streaming_master"):
    audio, sr = load_audio(file_path)
    lufs = lufs_integrated(audio, sr)
    tp = true_peak_db(audio, sr)
    plr = peak_to_loudness(audio, sr)
    mloss = mono_loss_db(audio, sr)
    corr = phase_corr(audio)
    target = GENRE_TARGETS.get(genre, {})

    checks = [
        {"name": "mono_loss", "pass": mloss <= 3.0, "value": f"{mloss:.2f} dB"},
        {"name": "phase_corr", "pass": corr >= 0, "value": f"{corr:.3f}"},
        {"name": "true_peak", "pass": tp <= -1.0, "value": f"{tp:.2f} dBTP"},
        {"name": "lufs_in_range", "pass":
            target.get("lufs", (-99, 99))[0] <= lufs <= target.get("lufs", (-99, 99))[1],
         "value": f"{lufs:.2f} LUFS"},
        {"name": "plr_in_range", "pass":
            target.get("plr", (0, 99))[0] <= plr <= target.get("plr", (0, 99))[1],
         "value": f"{plr:.2f}"},
        {"name": "no_clipping", "pass": not has_clipping(audio),
         "value": str(has_clipping(audio))},
    ]
    return {"checks": checks,
            "ready_for_delivery": all(c["pass"] for c in checks)}


# ---------- MCP wiring ----------

app = Server("audio-mixing-mastering-agent")

TOOLS = [
    Tool(name="analyze_audio",
         description="Measure LUFS, true peak, PLR, phase, mono compatibility",
         inputSchema={
             "type": "object",
             "properties": {
                 "file_path": {"type": "string"},
                 "measurements": {"type": "array", "items": {"type": "string"}}
             },
             "required": ["file_path"]
         }),
    Tool(name="diagnose_mix",
         description="Structured diagnostic report with fix recommendations",
         inputSchema={
             "type": "object",
             "properties": {
                 "file_path": {"type": "string"},
                 "target_genre": {"type": "string"}
             },
             "required": ["file_path", "target_genre"]
         }),
    Tool(name="apply_mastering_chain",
         description="Apply HPF + mono bass + loudness + TP limit per genre",
         inputSchema={
             "type": "object",
             "properties": {
                 "file_path": {"type": "string"},
                 "genre": {"type": "string"},
                 "target_lufs": {"type": "number"},
                 "target_dbtp": {"type": "number"}
             },
             "required": ["file_path", "genre"]
         }),
    Tool(name="render_master",
         description="Render master per delivery spec with dither",
         inputSchema={
             "type": "object",
             "properties": {
                 "source_file": {"type": "string"},
                 "output_path": {"type": "string"},
                 "delivery_spec": {"type": "string"},
                 "dither": {"type": "boolean"}
             },
             "required": ["source_file", "output_path"]
         }),
    Tool(name="qc_check",
         description="Final QC before delivery",
         inputSchema={
             "type": "object",
             "properties": {
                 "file_path": {"type": "string"},
                 "genre": {"type": "string"},
                 "delivery_spec": {"type": "string"}
             },
             "required": ["file_path", "genre"]
         }),
]


@app.list_tools()
async def list_tools():
    return TOOLS


@app.call_tool()
async def call_tool(name, arguments):
    try:
        if name == "analyze_audio":
            r = analyze_audio(arguments["file_path"],
                              arguments.get("measurements"))
        elif name == "diagnose_mix":
            r = diagnose_mix(arguments["file_path"], arguments["target_genre"])
        elif name == "apply_mastering_chain":
            r = apply_mastering_chain(
                arguments["file_path"], arguments["genre"],
                arguments.get("target_lufs"), arguments.get("target_dbtp", -1.0))
        elif name == "render_master":
            r = render_master(arguments["source_file"],
                              arguments["output_path"],
                              arguments.get("delivery_spec", "streaming_master"),
                              arguments.get("dither", True))
        elif name == "qc_check":
            r = qc_check(arguments["file_path"], arguments["genre"],
                         arguments.get("delivery_spec", "streaming_master"))
        else:
            r = {"error": f"unknown tool {name}"}
    except Exception as e:
        r = {"error": str(e)}

    return [TextContent(type="text", text=json.dumps(r, indent=2, ensure_ascii=False))]


async def main():
    async with stdio_server() as (read, write):
        await app.run(read, write, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
