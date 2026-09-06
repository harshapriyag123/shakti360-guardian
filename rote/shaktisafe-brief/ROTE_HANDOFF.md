# Rote recording and Community submission

This package contains tested application code. It must be recorded, exported, linted, replayed, and published through Rote before it constitutes a hackathon submission.

Development workspace status: Rote 0.80.0 was installed, but workspace creation returned `rote requires login` (exit 77). No trace or public URI is included. Sign in through Rote's own supported login flow; never paste credentials into chat.

Official workflow: https://www.modiqo.ai/docs/create-your-first-play

## In your Codespace

Install the official field kit and complete account sign-in:

```bash
curl -fsSL https://getrote.dev/playoffs/install.sh | sh
```

Open Codex in the project directory. Paste the following prompt into Codex (not the shell):

```text
$play Create a reusable ShaktiSafe Brief Play from this tested project.

Read README.md, VALIDATION.md, and shaktisafe.py. Inspect the installed Rote
instructions and command help. Run the tests. Create a recorded workspace.

Record actual executions of these separate stages using rote proc run:
1. python3 shaktisafe.py resolve --city Chennai --country IN --location-id 1264527
2. python3 shaktisafe.py weather --context output/context.json
3. python3 shaktisafe.py air --context output/context.json
4. python3 shaktisafe.py alerts --context output/context.json
5. python3 shaktisafe.py compose --context output/context.json

Each source should be a distinct captured reading. Source steps depend on
resolve; compose depends on all three. Declare file as well as value edges.
Run a second check for the same outing and verify comparison. Verify Houston
and London, source failure, and the explicitly labeled synthetic demo.

Keep a pending stub. Export the actual successful trace with typed city,
country, location_id, start, duration, output, and baseline inputs.
Handle optional location_id explicitly; do not silently select an ambiguous
city. The next-hour default is for initial planning; reuse context for refresh.

Bundle the required Python helper with the Play. Use per-run output paths
and a declared persistent baseline location. Do not retain an author-only
absolute path. Surface source status, timestamps and coverage in the output.
Declare network hosts and local reads/writes. Keep credentials, private logs,
personal baselines and development outputs out of the public package.

Inspect, lint, and replay using commands supported by this installation.
Show the publication contents and effects. After I select Community, publish
and verify the exact public URI by pulling/running it from a clean directory.
If authentication is needed, tell me the precise sign-in step. Do not claim
publication, token savings, or a recorded correction without evidence.
```

When the destination choice appears, **Community** publishes the hackathon entry. A GitHub repository alone is not the submission.

## Manual recorded exploration

After checking your installed CLI help, these commands follow the official documented recording pattern. Execute from this project directory. They record a new live run; they do not pretend the earlier development runs were recorded.

```bash
rote init shaktisafe-brief --seq
rote proc run python3 shaktisafe.py resolve --city Chennai --country IN --location-id 1264527
rote proc run python3 shaktisafe.py weather --context output/context.json
rote proc run python3 shaktisafe.py air --context output/context.json
rote proc run python3 shaktisafe.py alerts --context output/context.json
rote proc run python3 shaktisafe.py compose --context output/context.json
```

Export and publication should use the actual installed instructions and generated artifact paths; neither a public namespace nor a Play URI is invented here.
