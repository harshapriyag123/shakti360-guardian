# Architecture Pro

```text
                     iOS / Android / Web
                             |
                      Expo Safety UI
                             |
        +--------------------+--------------------+
        |                    |                    |
 Battery Guardian      Privacy Guardian      Offline State
        |                    |                    |
        +--------------------+--------------------+
                             |
                         FastAPI
                             |
                    Safety Orchestrator
                             |
 +---------+---------+-------+-------+---------+----------+
 |         |         |       |       |         |          |
Journey  Context   SafeWord Cyber Evidence  Pattern   Resources
 |         |         |       |       |         |          |
 +---------+---------+-------+-------+---------+----------+
                             |
                   Deterministic Policy
                             |
               +-------------+-------------+
               |                           |
        Trusted Circle              Emergency Options
```

## Why this matters
LLMs are useful for interpretation and organization, but emergency state transitions should remain deterministic, auditable and testable.
