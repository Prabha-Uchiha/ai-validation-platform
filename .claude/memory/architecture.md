# Architecture Memory

This repository implements:

AI-native autonomous validation infrastructure.

Architecture style:

* modular monorepo
* distributed domain services
* event-driven orchestration
* deterministic workflows
* replayable execution

Core infrastructure:

* PostgreSQL
* Redis Streams
* OpenTelemetry
* FastAPI
* Docker

Execution model:

* deterministic state machine
* explicit transitions
* replay checkpoints
* sandbox runtime

Primary engineering priority:
execution correctness over autonomy.
