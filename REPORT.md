# 1. Architecture

The system separates discovery from production execution.

During discovery, a Gemini-powered agent receives a natural-language goal and repeatedly observes the current application state, chooses one allowed action, and executes that action through a surface abstraction backed by Playwright.

The successful workflow is represented as a typed `CapabilityArtifact`. Production execution uses a deterministic replay engine that consumes this artifact and invocation parameters without putting an LLM in the decision loop.

The main boundaries are:

- `BrowserSurface`: perception and interaction with the UI.
- `DiscoveryAgent`: LLM-driven observe → decide → act loop.
- `CapabilityArtifact`: reusable capability contract.
- `ReplayEngine`: deterministic execution.
- `Policy`: domain and action allowlists.
- `HandoffManager`: automation/human control transfer.
- `Logger`: structured evidence.

I intentionally kept the implementation single-process. Queues, distributed workers, databases, and orchestration infrastructure would add complexity without improving the core demonstration.

The central design principle is: the model discovers; the artifact captures the learned procedure; deterministic replay executes it.


# 2. Artifact schema

The artifact is a typed, versioned Pydantic model rather than a raw LLM transcript.

A capability contains:

- schema and capability versions,
- capability name and description,
- target application and entry URL,
- typed invocation parameters,
- typed outputs,
- ordered actions,
- locator information,
- expected states,
- a success checkpoint,
- allowed domains and actions,
- metadata.

For example, `member_id` is represented as an input parameter rather than embedding a concrete member identifier in the reusable workflow.

Recorded steps can therefore contain:

`{{member_id}}`

which is resolved using invocation parameters during replay.

Locators are also represented explicitly instead of storing arbitrary Playwright code. The current implementation supports strategies such as label, role, text, and CSS.

The preferred locator hierarchy is semantic targeting such as accessible label/role first, structural selectors second, and coordinates only as a last resort in a future surface adapter.

This keeps the artifact understandable to a reviewer and independent from the original model transcript.


# 3. Determinism & error handling

Replay does not invoke Gemini.

The replay engine loads the artifact, validates policy, substitutes invocation parameters, executes the recorded actions in order, verifies the success checkpoint, and extracts declared outputs.

The demo distinguishes three conceptual result classes:

1. `SUCCESS` — the workflow completed and outputs were extracted.
2. `BUSINESS_OUTCOME` — the application produced a legitimate domain result such as `MEMBER_NOT_FOUND`.
3. `FAILURE` — execution could not safely complete.

This distinction is important because "member not found" is meaningful information for the calling agent rather than an automation crash.

The implementation also captures failure evidence when execution raises an exception or a checkpoint cannot be verified.

A production version would expand recoverable conditions into explicit typed policies, for example:

- retry transient loading failures,
- dismiss known interstitials,
- re-authenticate after session expiry where policy permits,
- stop on permission denial,
- escalate unknown dialogs.

The current implementation intentionally goes deep on the success/business-outcome distinction rather than building a large retry framework.

UI drift is secondary in this environment, but semantic locators and checkpoints provide basic protection against blindly executing after the expected state changes.


# 4. Heterogeneity & multi-tenant

The artifact is intentionally separated from the mechanism used to operate the surface.

`BrowserSurface` currently implements web interaction through Playwright, but the same capability concepts can be implemented through other adapters.

For legacy web applications, an adapter could combine accessibility information, DOM structure, frames, text anchors, screenshots, and coordinates.

For native desktop applications, another adapter could use operating-system accessibility APIs and coordinate-based interaction while preserving the same higher-level actions and checkpoints.

This creates the seam:

`Capability Artifact → Surface Adapter → Concrete UI`

For multi-tenant deployment, I would separate a vendor-level base capability from tenant-specific configuration.

For example:

`Vendor Capability + App Version + Tenant Overrides`

A shared capability could define the common workflow while tenant overrides supply differences such as entry routes, labels, branding-specific locators, or known dialogs.

Artifacts would carry vendor/application version metadata and replay telemetry. Repeated checkpoint or locator failures for a particular tenant/version would mark that specialization as unhealthy and route it for review or rediscovery.

This avoids maintaining an entirely independent recording for every institution while still allowing safe specialization where configurations differ.


# 5. Escalation & handoff

The handoff mechanism models explicit ownership of the live session.

The control states are:

`AUTOMATION → PAUSED → HUMAN → AUTOMATION → COMPLETE`

When automation reaches a condition it should not resolve itself, `HandoffManager` creates an intervention event containing the reason and captures a screenshot.

The browser remains alive.

The human then operates the same browser session manually. After the operator signals completion, control returns to automation without creating a new browser context.

The handoff log records control-transfer events and timestamps, and screenshots preserve evidence before and after intervention.

The demo uses the terminal as the minimal operator interface. This was deliberate: building a real-time co-browsing console would add substantial UI work without changing the underlying control-transfer design.

In production, the same mechanism could expose the browser through a remote session viewer and use authenticated operator actions plus a lease/lock so exactly one actor owns control at any time.


# 6. Safety

Safety is enforced independently from the LLM.

The current implementation uses explicit domain and action allowlists. Replay validates the target before navigation and validates each action before execution.

Sensitive invocation values are parameterized rather than stored inside reusable artifacts.

Replay evidence redacts the member identifier instead of persisting the supplied value.

Secrets are loaded from `.env`, which is excluded from source control.

The demo capability is intentionally read-only and reversible: it searches for a member and reads a balance. No transaction or account mutation is performed.

For real financial workflows, actions would additionally carry a risk classification such as:

- safe/reversible,
- sensitive,
- irreversible.

Irreversible actions such as submitting a transaction would require explicit approval/checkpoint policy before execution.

The main limitation of the current guardrail implementation is that it demonstrates the enforcement seam rather than a complete financial authorization system.


# 7. Cuts

I deliberately prioritized a thin but complete vertical slice over production infrastructure.

I did not build:

- distributed workers or queues,
- persistent databases,
- a full operator console,
- desktop automation,
- authentication/session management,
- automatic cross-tenant specialization,
- sophisticated retry/backoff logic,
- production secrets management,
- unrestricted LLM recovery during replay.

These were intentionally cut because the core assessment is about the boundaries between discovery, artifact generation, deterministic execution, safety, error semantics, and human intervention.

With more time, I would first strengthen runtime error classification and automated recovery, then add artifact approval states and replay stability scoring.

After that, I would implement vendor-level capability inheritance with tenant/version overrides and demonstrate the same capability against two slightly different application variants.

The final production direction would preserve the same principle used in this prototype: use model reasoning to discover or repair workflows, but keep normal execution deterministic, policy-constrained, observable, and reviewable.