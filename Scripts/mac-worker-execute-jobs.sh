#!/usr/bin/env bash
# Poll for cloud-agent job files under .cursor/jobs/ and run on the Mac worker.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
JOB_JSON="$ROOT/.cursor/jobs/mix-tune.json"
[[ "$(uname -s)" == "Darwin" ]] || { echo "Darwin only" >&2; exit 1; }

cd "$ROOT"
git fetch origin cursor/mac-mix-tune-vocals-c66d 2>/dev/null || true
git checkout cursor/mac-mix-tune-vocals-c66d 2>/dev/null || git checkout -B cursor/mac-mix-tune-vocals-c66d

if [[ ! -f "$JOB_JSON" ]]; then
  echo "No mix-tune job file."
  exit 0
fi

status="$(python3 -c "import json; print(json.load(open('$JOB_JSON')).get('status',''))")"
if [[ "$status" != "pending" ]]; then
  echo "Job status=$status (nothing to do)."
  exit 0
fi

RESULT="$ROOT/.cursor/jobs/mix-tune.result.jsonl"
chmod +x "$ROOT/Scripts/mac-balance-mix-tune-vocals.sh"
./Scripts/mac-balance-mix-tune-vocals.sh 2>&1 | tee -a "$RESULT" || true
python3 - <<'PY'
import json, datetime, pathlib
job = pathlib.Path(".cursor/jobs/mix-tune.json")
data = json.loads(job.read_text())
data["status"] = "done"
data["finished_at_utc"] = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
job.write_text(json.dumps(data, indent=2) + "\n")
PY

echo "Mix/tune job completed. See $RESULT"