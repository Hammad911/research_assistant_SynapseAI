# Take-Home: Own, Harden, Debug & Defend a Multi-Agent Research Assistant

## Read this first

You will **not** build an agent from scratch. This repository already contains a
working-ish multi-agent research assistant (LangGraph) of the kind an AI coding
tool produces. It runs, it demos, and it has the problems AI-generated code
usually has.

**Your job is the part AI can't do for you:** make it production-grade, find
what's wrong with it, prove it works, extend it, and defend your decisions.

This mirrors the actual job. Most code you touch here is AI-drafted; we hire
people who can *own, harden, and reason about* that code — not people who can
prompt it into existence.

## Ground rules

- **AI tools are fully allowed and expected.** Use Claude, Codex, Cursor,
  whatever you like. We assume you will. We grade *your judgment on top of the
  AI*, so make that judgment visible (see deliverables).
- **Timebox: ~6–8 focused hours.** We mean it. Do **not** gold-plate. A smaller,
  deeper, well-reasoned submission beats a sprawling one. Anything you don't
  finish, write down in `DECISIONS.md` under "What I'd do with more time" — we
  grade that too.
- **Authenticity matters more than polish.** One deliverable (the video) is
  unscripted and single-take *on purpose*. If you understand your code it's
  easy; if you don't it's impossible. Plan accordingly.
- Individual work only. Don't post this prompt or repo publicly.

## What you're starting with

The repo runs on the happy path and its `README.md` *claims* it supports
multi-turn conversation, human-in-the-loop clarification, confidence-based
routing, and a validation loop. **Assume nothing else about it is correct or
production-ready.** Verify the claims yourself.

## Your tasks

### Task A — Make it production-grade (hardening)

Bring the system to a standard you'd ship. At minimum:

- **Resilience** — the search API *will* time out, rate-limit, and occasionally
  return junk. The system must degrade gracefully (timeouts, bounded retries
  with backoff, partial-result handling) and never hang or crash a conversation.
- **Cost & token discipline** — enforce a configurable **per-query cost/token
  budget**. The context sent to the model must not grow without bound. Make the
  trade-off you choose explicit.
- **Determinism for testing** — provide a way to run the system reproducibly
  (seeded/mocked) so behaviour can be tested without hitting live APIs.
- **Config & secrets** — no hardcoded or leaked keys; sane configuration; clear
  failure when misconfigured.
- **Observability** — structured logs/traces sufficient to debug a bad run in
  production. Tracing (e.g. LangSmith) is a plus, not required.

### Task B — Bug hunt (code review)

This baseline contains **several deliberately planted defects** — a few are
crashes, but most are *silent* correctness bugs in exactly the areas the README
brags about (conversation memory, interrupt/resume, routing thresholds, the
validation loop, and how untrusted search content is handled). Find as many as
you can.

Deliver **`BUGREPORT.md`**. For **each** bug: location (`file:line`), the
symptom, the **root cause**, your fix, and how you'd prevent the whole class of
bug from recurring. We care about root-cause reasoning, not raw count. (There
are more than five. We won't say how many.)

### Task C — Prove it works (evaluation harness)

Anyone can *claim* their agent is good. **Show us how you know.** Build a small
evaluation harness with a labeled test set *you* create. At minimum measure:

- **Routing correctness** — on known inputs (including boundary cases), does
  each agent route to the correct next node?
- **Groundedness / hallucination** — does synthesis only assert what the
  research supports?
- **Cost and latency** per query.

Wire it so a regression is caught by running one command. Put results and a
short interpretation in **`EVAL.md`**.

### Task D — Curveball extension (multi-company comparison)

Add **multi-company comparative research**: a user can ask, e.g. *"Compare the
financial health of Stripe and Adyen,"* and the system researches both and
synthesizes a structured comparison. Do this *within* the existing architecture
— we're watching whether you understand the graph well enough to extend it
cleanly (state, routing, parallelism, cost) rather than bolting on a hack. If
you scope something out, justify it in `DECISIONS.md`.

### Task E — Decisions & AI-collaboration log

- **`DECISIONS.md`** — the 6–10 most important engineering decisions, each as
  *context → options → choice → trade-off*. Include any spec ambiguities you
  noticed and how you resolved them. (Parts of this assignment are intentionally
  under-specified. Spotting and resolving ambiguity is part of the test.)
- **`AI_LOG.md`** — **not** a prompt dump. For 4–6 key moments, show the prompt,
  **what the AI got wrong or shallow**, and how you caught and corrected it. The
  corrections are the point.

### Task F — Live walkthrough video (single take, unscripted, ~10 min)

Record screen + webcam + audio in **one continuous take, no cuts/edits**:

1. **(~3 min) Architecture** — walk us through *your* system: state schema,
   routing, and how interrupt/resume works after your fixes.
2. **(~4 min) Live edit** — implement this change **on camera**, talking as you
   go: *"Add a guard that aborts a query and returns a graceful message if the
   projected token cost would exceed the configured budget, and log a line when
   it triggers."* Run it. If it breaks, debug it live — we *want* to see that.
3. **(~3 min) Reasoning** — answer out loud, unscripted: *"Your agent's
   cost-per-query 5×'d in production overnight with no deploy. Walk us through
   how you'd diagnose it."*

Cuts, edits, or a read-aloud script disqualify this section. A messy, real,
single take scores far higher than a polished, edited one.

## Deliverables (single ZIP, reply to the email — no GitHub/YouTube links)

1. The full repo **including `.git` history** (commit as you work — we read it).
2. `BUGREPORT.md`, `EVAL.md`, `DECISIONS.md`, `AI_LOG.md`.
3. `RUN.md` — lets us build, seed, run, and execute your eval suite in under 10
   minutes.
4. The single-take video (file or private link).

## How we grade (full transparency)

We score 12 dimensions: system design, correctness/routing, resilience,
**evaluation rigor**, **debugging**, observability, security, the extension,
code craft, engineering judgment, live defense, and **authorship authenticity**.

**Working features are table stakes.** Points come from depth: did you find the
silent bugs, can you prove quality, can you defend your choices, and can you
modify your own code live. We'd rather see three tasks done with real depth than
six done shallowly.
