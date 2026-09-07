# Narrated demo — approximately 2:50

Prepare and rehearse before recording. Commands below use Bash from the repository root, an existing authenticated Rote installation, Python 3.11+, and the already installed, inspected 0.1.0 Play. Do not install adapters or change the registered Play. Registry execution may require confirmation and process-execution eligibility; resolve those before recording. Do not bypass a policy denial.

## Setup off camera

```bash
python3 --version
rote play inspect harshapriyag123/shaktisafe-brief@0.1.0 --json
REPO_ROOT="$(git rev-parse --show-toplevel)"
PLAY='harshapriyag123/shaktisafe-brief@0.1.0'
DEMO_ROOT="$REPO_ROOT/rote/shaktisafe-brief/output/demo-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$DEMO_ROOT/scratch"
export TMPDIR="$DEMO_ROOT/scratch"
PS1='demo> '
```

Keep this shell open. The absolute directory variables avoid runner-relative path ambiguity; do not print their values on camera. Outputs use the repository's existing ignored output directory. Choose a fresh session directory for each rehearsal. Setting `TMPDIR` keeps the offline demo's temporary baseline inside the repository. The existing Play runtime manages its own execution records; do not record its private paths or account details.

The local name `shaktisafe-brief` must already resolve to the inspected published artifact for the DAG shot. Check its identity in rehearsal. The CLI supports `--dry-run` for local targets, not registry targets. If the local name does not resolve, omit that command and use a previously captured, verified DAG screenshot; do not fabricate a runtime view.

## 0:00 — Problem hook

**Say:** “Before leaving, I check the forecast, air quality, and warnings. Checking again means remembering what I saw before. ShaktiSafe Brief asks one useful question: what changed before I leave?”

**Screen:** Project title and a readable brief. Use a generic city, not a home address.

## 0:20 — Inspect the public Play

```bash
rote play inspect "$PLAY"
```

**Say:** “This is the published, pinned Community Play. Inspect it before running. Its Python process contacts environmental data providers and writes local reports and baselines.”

**Screen:** Public page and cropped inspection showing name, version and eligibility. Show the runtime disclosure in `resources/USAGE.md` or the public presentation. Do not interpret a generic ‘no services/no writes’ card as the complete effects disclosure.

## 0:40 — Houston first run

```bash
rote play run "$PLAY" city=Houston country=US location_id=4699066 start=next-hour duration=2 output_dir="$DEMO_ROOT/houston" baseline_dir="$DEMO_ROOT/baseline"
```

**Say:** “For Houston, I choose a two-hour outing starting next hour. Three source checks run after destination resolution, then the Play composes a brief and saves a baseline.”

**Screen:** Five-stage completion ledger, then Markdown preview of the session's `houston/brief.md`. Expect context and reports, source timestamps/status, and first-run baseline creation. NWS may return no matching alerts; that is not an all-clear. Live success depends on source availability.

## 1:10 — Same-outing refresh

```bash
rote play run "$PLAY" context="$DEMO_ROOT/houston/context.json" output_dir="$DEMO_ROOT/houston-refresh" baseline_dir="$DEMO_ROOT/baseline"
```

**Say:** “This refresh reuses the exact destination and time window. It compares each successful source with the saved baseline. No changes is a useful answer too.”

**Screen:** Preview `houston-refresh/brief.md`; highlight change text and timestamps. Do not promise changing live conditions or substitute a synthetic delta without labeling it.

## 1:35 — Chennai degraded coverage

```bash
rote play run "$PLAY" city=Chennai country=IN location_id=1264527 start=next-hour duration=2 output_dir="$DEMO_ROOT/chennai" baseline_dir="$DEMO_ROOT/baseline"
```

**Say:** “Worldwide destinations are supported for weather and modeled air quality where providers have data. Here in Chennai, official alerts are explicitly unsupported. Missing alerts never mean all clear.”

**Screen:** `chennai/brief.md`, especially `unsupported` alerts. Weather or air failures must remain visible if they occur. This is a coverage limitation, not a simulated network failure.

## 1:55 — Simulated failure and stale data

```bash
(cd "$REPO_ROOT/rote/shaktisafe-brief" && python3 -B demo.py)
```

**Say:** “This next example is synthetic, not live conditions. After a successful baseline and changed readings, a simulated weather timeout retains last-successful values clearly labeled stale.”

**Screen:** Preview `rote/shaktisafe-brief/demo-output/02-changed.md`, then `03-source-failure.md`. Keep “SYNTHETIC DEMO — NOT LIVE CONDITIONS,” timeout reason and **STALE** label visible. The fixture demonstrates +4°C maximum temperature and +8 µg/m³ maximum PM2.5 changes; these are invented test readings, not observed Houston changes. This command exercises the Python logic, not a live Rote source outage.

## 2:15 — Rote journey and parallel stages

```bash
rote play run shaktisafe-brief --dry-run city=Houston country=US location_id=4699066 start=next-hour duration=2 output_dir="$DEMO_ROOT/dag-preview" baseline_dir="$DEMO_ROOT/baseline"
```

**Say:** “The execution plan has three levels: resolve, three parallel source checks, then compose. The reusable workflow avoids asking an agent to reconstruct these steps each time. Recorded checkpoint recovery restored four completed stages and reran composition.”

**Screen:** Crop the real dry-run dependency plan. Pair it with the five-stage ledger from the live run. A dry run shows structure, not measured parallel speedup. If using a saved recovery image, label it historical evidence. Do not invent a journey command or expose a private viewer URL.

## 2:35 — Link, impact, close

**Say:** “One repeatable check, honest missing-data labels, and a comparison for the same outing. Find ShaktiSafe Brief on Community: what changed before I leave?”

**Screen:** [Pinned public Play](https://play.modiqo.ai/harshapriyag123/shaktisafe-brief@0.1.0). Closing caption: “Modeled air quality. US official alerts only. Missing alerts ≠ all clear.”

Actual network runs can exceed these shot windows. Record full real runs beforehand, then edit with visible ‘elapsed time condensed’ captions. Never imply a measured end-to-end latency or hide source failures. Finish around 2:50.
