# Architecture

```text
               Expo iOS / Android / Web
                         |
                 Edge Safety Layer
                         |
       Battery | Privacy | Offline State
                         |
                    FastAPI API
                         |
               Safety Orchestrator
                         |
    Journey | Cyber | Evidence | Resource | Privacy
                         |
        Deterministic Escalation Engine
                         |
        PostgreSQL/PostGIS/Redis (roadmap)
```

## Safety principle
- LLM/AI: interpretation, summarization, classification support.
- Deterministic code: escalation level, session lifecycle, permission behavior.
- Verified provider data: hospitals, police, emergency/support resources.
- User remains in control of escalation choices.
