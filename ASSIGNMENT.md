# Take-Home: Own, Harden, Debug, **and Push Beyond** a Multi-Agent Research Assistant

## Read this first

You will **not** build an agent from scratch. This repository already contains a
working-ish multi-agent research assistant (LangGraph) of the kind an AI coding
tool produces. It runs, it demos, and it has the problems AI-generated code
usually has.

This exercise has two halves:

- **Foundation (Pillar A)** — make it production-grade, find what's broken,
  prove it works. This is *table stakes*: it qualifies you.
- **Frontier (Pillar B)** — take it somewhere we **didn't** ask for. Invent,
  research, and self-challenge. This is what we remember.

We are hiring for curiosity, originality, research instinct, and drive — not
just the ability to make a thing run. The Frontier is where you show us those.

## On AI use — read carefully

AI tools (Claude, Codex, Cursor, …) are **allowed and expected**, with one
distinction that is the whole point of this exercise:

> **AI is an accelerator, not a substitute for thinking.**

- Use AI to move faster on things you already understand.
- We are **not** impressed by anything an AI could have produced on its own —
  generic, shallow, unsourced, or un-owned work scores **low**, however polished.
- We **are** impressed by the human delta: original ideas, real research,
  things you taught yourself, judgment under ambiguity, and work you can defend
  live.

**Effort, research, and self-challenge are non-negotiable. Cutting corners or
outsourcing the thinking is disqualifying.** We read your git timestamps, we
**verify your citations**, and we ask you to modify your own code **on camera**.
Own your work.

## Timebox & shape

This is larger than a typical screen — on purpose. Suggested **2 day window**,
**~10 hours of actual work**. *Please don't exceed it* — we read commit
timestamps and value sustainable focus over marathons. Rough split:

- ~40% Foundation · ~50% Frontier + research · ~10% write-ups + video.

Depth in one direction beats shallow breadth.

---

# Pillar A — Foundation (qualifier)

The `README.md` *claims* the system supports multi-turn conversation,
human-in-the-loop clarification, confidence-based routing, and a validation
loop. **Assume nothing else is correct or production-ready. Verify the claims.**

### A1 — Make it production-grade
Resilience (timeouts, bounded retry/backoff, graceful degradation — the search
API *will* fail), a configurable **per-query cost/token budget**, bounded
context, a **reproducible/mocked** run mode for testing, clean config & secrets,
and observability you could debug a bad run with.

### A2 — Bug hunt (`BUGREPORT.md`)
The baseline contains **several deliberately planted defects** — a few crash,
most are *silent* (conversation memory, interrupt/resume, routing thresholds,
the validation loop, untrusted search content). For each: location
(`file:line`), symptom, **root cause**, your fix, and how you'd prevent the
class. Root-cause reasoning matters more than count. (More than five exist.)

### A3 — Prove it works (`EVAL.md`)
Build an evaluation harness with a labeled test set *you* create: routing
correctness (incl. boundary cases), groundedness/hallucination, cost, latency.
One command should catch a regression.

---

# Pillar B — Frontier (the part that matters most)

### B1 — Invent an original capability (`FRONTIER.md`)
Conceive and build **one capability we did not ask for** that makes this
assistant meaningfully better, smarter, or different. Build a **working slice**
(it need not be complete) plus a design rationale.

Rules that force originality and research:
- **Ground it in research** — see B2. Your approach must be informed, not guessed.
- **Be non-obvious** — if your idea is the first thing an AI suggests or a
  standard tutorial, it will not score well. Include a *"Why this is non-obvious"*
  note and *"What I'd build next."*
- **Originality is verified** — if it's inspired by prior art, cite it and
  explain your novel twist. Lifting work without attribution is an integrity
  failure.
- **Declare your stretch** — state the hardest thing you attempted and whether
  you fully pulled it off. **We reward ambitious partial success over safe,
  trivial completeness.**

*Sparks (do NOT just pick one verbatim — the best submissions invent beyond this
list):* self-correcting agents, confidence calibration from eval feedback,
cross-source agreement for hallucination detection, multi-agent debate for
validation, cost-aware adaptive routing, a retrieval/knowledge cache, agent
memory/personalization, eval-driven prompt optimization, a novel
human-in-the-loop UX.

### B2 — Research brief (`RESEARCH.md`)
A **critical synthesis**, not a link dump, for the problem your Frontier feature
tackles: what is the current state of the art, what did you read, what do you
**agree/disagree** with and why, and what is **your** point of view. Cite **≥3
real, verifiable sources** (papers, docs, engineering blogs, real systems) —
**we check every one.** Fabricated or non-existent citations are an automatic
integrity failure.

### B3 — Roads not taken (in `FRONTIER.md` or `EXPLORATION.md`)
2–3 ideas or approaches you **tried and rejected**, with *why*. Show iteration,
taste, and that you didn't just accept the first thing AI proposed.

---

# Growth & process artifacts (intrinsic-signal — keep them honest)

- **`DECISIONS.md`** — your 6–10 most important engineering decisions as
  *context → options → choice → trade-off*. Include the spec ambiguities you
  noticed (parts of this brief are intentionally under-specified) and how you
  resolved them.
- **`JOURNAL.md`** — three short sections:
  1. **Learning log** — at least one tool/technique you'd **not used before**:
     the learning curve, what confused you, how you got unstuck.
  2. **AI collaboration & overrides** — 4–6 moments where AI helped, and
     crucially where you **distrusted or overrode it** and why.
  3. **Honest self-assessment** — what's solid, what's half-baked, what you'd
     never ship. *Owning a gap scores well; overclaiming is penalized.*

---

# Pillar C — Video (single take, unscripted, ~10 min)

Record screen + webcam + audio in **one continuous take, no cuts/edits**:

1. **(~3 min) Architecture** — your system after your fixes: state, routing,
   interrupt/resume.
2. **(~3 min) Live edit** — implement this **on camera**, talking as you go:
   *"Add a guard that aborts a query and returns a graceful message if the
   projected token cost would exceed the configured budget, and log when it
   fires."* Run it. If it breaks, debug it live — we *want* that.
3. **(~3 min) Frontier pitch** — sell your invention: what it is, why it's
   non-obvious, what the research says, what you'd build next.
4. **(~2 min) Reasoning** — unscripted: *"Your agent's cost-per-query 5×'d in
   production overnight with no deploy. How do you diagnose it?"*

Cuts, edits, or a read-aloud script disqualify this section. A messy, real,
single take scores far higher than a polished, edited one.

---

## Deliverables (single ZIP, reply to the email — no GitHub/YouTube links)

1. The full repo **including `.git` history** (commit as you work).
2. Foundation: `BUGREPORT.md`, `EVAL.md`, `RUN.md` (build/seed/run/eval in <10 min).
3. Frontier: `FRONTIER.md`, `RESEARCH.md` (verifiable sources), roads-not-taken.
4. Growth: `DECISIONS.md`, `JOURNAL.md`.
5. The single-take video (file or private link).
