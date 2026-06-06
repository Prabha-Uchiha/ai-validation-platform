# AI Validation Platform

AI-native autonomous validation infrastructure.

This repository is NOT:

* a chatbot
* an AutoGPT clone
* a toy framework
* an unrestricted autonomous system
* a prompt-engineering demo

This repository IS:

* deterministic
* replayable
* observable
* sandboxed
* infrastructure-aware
* execution-centric
* event-driven
* failure-intelligent

---

# CORE ENGINEERING PHILOSOPHY

Deterministic systems execute.
Agents reason.

Execution must remain:

* reproducible
* observable
* replayable
* auditable
* deterministic
* bounded
* sandboxed

The platform prioritizes:

* failure diagnosis
* execution correctness
* replayability
* infra awareness
* observability
* workflow determinism

NOT:

* unrestricted autonomy
* recursive agent loops
* free-form orchestration

---

# CORE ENGINEERING PRINCIPLES

1. Deterministic execution
2. Replayable workflows
3. Typed contracts
4. Event-driven orchestration
5. Sandboxed execution
6. Infrastructure-aware diagnosis
7. Explicit state transitions
8. Strong observability
9. Bounded retries
10. Structured outputs
11. Execution lineage preservation
12. OpenTelemetry-first tracing
13. Idempotent operations
14. Modular architecture
15. Domain-oriented services

---

# ARCHITECTURE RULES

## NEVER:

* execute unrestricted shell commands
* bypass typed execution tools
* create recursive autonomous loops
* directly mutate infrastructure
* use arbitrary sleeps
* create giant monolithic agents
* skip tracing/logging
* skip replay checkpoints
* bypass workflow state machines
* create hidden mutable state
* introduce nondeterministic transitions

---

# ALWAYS:

* use typed Pydantic contracts
* use async Python
* add structured logs
* add OpenTelemetry spans
* preserve replayability
* preserve determinism
* preserve execution lineage
* preserve event auditability
* preserve state-machine constraints
* validate transitions explicitly

---

# REPOSITORY ARCHITECTURE

This repository uses:

* modular monorepo
* distributed domain services
* event-driven orchestration
* Redis Streams
* PostgreSQL
* OpenTelemetry
* sandboxed execution
* replayable workflows
* domain isolation
* MCP-compatible interfaces

---

# SERVICE BOUNDARIES

## coordinator_service

Responsible ONLY for:

* deterministic orchestration
* workflow state transitions
* checkpoints
* replay lifecycle
* execution lineage

NEVER:

* execute tools directly
* run shell commands
* mutate infrastructure
* bypass event bus

---

## tool_execution_service

Responsible ONLY for:

* sandboxed execution
* resource constraints
* typed execution contracts
* isolated execution runtime

NEVER:

* orchestrate workflows
* make retry decisions
* modify workflow state directly

---

# WORKFLOW RULES

Workflow transitions MUST remain explicit.

Allowed states:

INITIALIZED
ANALYZING
PLANNING
PROVISIONING
EXECUTING
DIAGNOSING
RETRYING
REPORTING
COMPLETED
FAILED

Never introduce implicit workflow transitions.

All transitions MUST be validated.

---

# OBSERVABILITY RULES

Every major operation MUST:

* emit structured logs
* emit OpenTelemetry spans
* preserve correlation IDs
* preserve execution lineage
* preserve replay metadata

Never add execution logic without observability.

Observability is mandatory infrastructure.

---

# SANDBOX RULES

Execution MUST remain sandboxed.

Never allow:

* unrestricted subprocess execution
* unrestricted Docker access
* unrestricted filesystem access
* unrestricted network access

All execution MUST:

* use typed interfaces
* enforce timeouts
* enforce quotas
* preserve execution isolation

---

# EVENT BUS RULES

The platform uses event-driven execution.

All workflow-critical operations MUST:

* emit events
* preserve event lineage
* support replay
* remain idempotent

Never use hidden in-memory coordination.

---

# DATABASE RULES

Persistence is authoritative.

Workflow state MUST:

* persist transitions
* preserve checkpoints
* support replay
* support auditability

Never rely exclusively on ephemeral memory.

---

# CODING STANDARDS

* Python 3.12+
* Strict MyPy
* Ruff formatting
* Async-first design
* SQLAlchemy 2.0
* Pydantic v2
* Explicit typing everywhere

Avoid:

* implicit typing
* giant utility files
* cyclic dependencies
* mutable global state

---

# TESTING STANDARDS

Every deterministic subsystem requires:

* unit tests
* replay validation
* transition validation
* idempotency checks
* observability validation

Never merge untested orchestration logic.

---

# REPLAYABILITY REQUIREMENTS

Execution must always remain:

* replayable
* inspectable
* auditable

Never introduce:

* hidden mutable state
* nondeterministic orchestration
* hidden retries
* hidden transitions

Replayability is a core system requirement.

---

# AI AGENT RULES (FUTURE PHASES)

Agents are:

* bounded
* tool-constrained
* observable
* capability-scoped

Agents NEVER:

* directly execute infrastructure mutations
* bypass typed execution tools
* run unrestricted shell commands
* create uncontrolled recursion

---

# MCP RULES (FUTURE PHASES)

MCP servers expose:

* typed interfaces
* allowlisted capabilities
* structured responses
* bounded tools

Never expose:

* unrestricted filesystem access
* unrestricted Docker access
* unrestricted shell execution

---

# PRIORITY HIERARCHY

Infrastructure
→ Execution Runtime
→ Workflow Engine
→ Event Bus
→ Observability
→ Replayability
→ Diagnosis
→ Agents
→ LLMs

LLMs are the LAST layer, not the foundation.

---

# IMPLEMENTATION PRIORITY

Build in this exact order:

1. schemas
2. observability
3. event bus
4. persistence
5. state machine
6. replay checkpoints
7. sandbox runtime
8. workflow orchestration
9. diagnosis
10. agents
11. MCP
12. automation

Never skip foundational layers.

---

# PHASE 1 GOAL

Phase 1 builds:

* deterministic orchestration
* typed contracts
* replayability
* observability
* event lineage
* sandbox execution
* state persistence

NO agents yet.
NO autonomous reasoning yet.
NO LangGraph yet.

Execution substrate first.
