# FRONTIER.md

## The capability: cross-source agreement as a check on self-reported confidence

Right now, `research_node` does two things in a single LLM call: read the
search results, and rate its own confidence (0–10) that the findings are
good enough. That confidence score is the thing routing decisions are built
on (`route_after_research`, then the validator loop). Nothing independently
checks whether that self-rating is justified.

I added a second, cheap signal: **how much do the independent search results
actually agree with each other on the claims being made**, and used that to
adjust the LLM's self-reported score rather than trusting it blindly.

Concretely: the existing `ResearchResult` structured-output schema (the same
single LLM call that already produces `findings` and a confidence score) is
extended to also identify the key factual claims in those findings and
report how many of the distinct sources (tagged by URL in the prompt)
actually support each one, producing an `agreement_ratio` (0–1) in the same
call. No second LLM call — the agreement check rides along in the one call
that already existed. The score that drives routing is `confidence_score =
round(raw_confidence_score * agreement_ratio)`, with `raw_confidence_score`
and `agreement_ratio` both kept in state for observability. A model that's
confident but only one source backs it up gets pulled down. A model that's
already unconfident doesn't get artificially inflated by agreement —
`agreement_ratio` can only pull the score down or leave it, never boost it
past the model's own ceiling, because the failure mode I'm targeting is
overconfidence, not underconfidence.

Both the raw self-reported score and the agreement ratio are kept in state
and logged, so a person debugging a bad run can see *why* the routing
decision happened — was it the model's self-report, the agreement check, or
both — instead of one opaque number.

## Why this is non-obvious

The standard fixes for unreliable verbalized confidence that I found in the
literature (self-consistency sampling, distractor-based recalibration,
multi-model ensembles — see RESEARCH.md) all work by spending *more* LLM
calls to manufacture an independent signal: ask the same model again, ask a
different claim, ask a different model. That's the move an AI coding
assistant or a tutorial would reach for first if asked "improve confidence
calibration" — generate more samples, check consistency.

This system doesn't need to manufacture redundancy — it already has it. Every
research pass fetches `max_search_results` independent sources from Tavily,
and none of that redundancy is currently used for anything except being
concatenated into one big prompt. The non-obvious move is noticing that the
ingredients for an agreement-based calibration signal were already being
paid for and thrown away, rather than reaching for the textbook answer of
sampling the LLM more times.

## What I'd build next

- **Validate it actually helps.** Right now I haven't proven
  `agreement_ratio` correlates with ground-truth correctness — only that it's
  a more independent signal than self-report alone. The honest next step is
  building a small labeled set (queries with known-correct answers) and
  checking whether the blended score predicts correctness better than
  `raw_confidence_score` alone. Without that, this is a structurally
  reasonable idea, not a proven one.
- **Use disagreement, not just agreement, as a signal.** Right now
  contradicting sources and silent sources are both just "doesn't support the
  claim." A source that actively contradicts another is a stronger and
  different signal (possible outdated info, possible misinformation) than one
  that's simply about a different topic — worth surfacing to the user
  directly ("sources disagree on X") rather than only folding it into a
  number.
- **Feed agreement data into the validator**, instead of having the validator
  re-derive its own sufficiency judgment from scratch. Right now the
  validator doesn't see `agreement_ratio` at all.
- **Track this over time per query type**, so the system could eventually
  learn which kinds of questions (e.g. recent news vs. established facts)
  tend to produce low agreement, and adjust `max_search_results` or routing
  defaults accordingly — this starts to resemble the "eval-driven prompt
  optimization" idea from the assignment's own spark list, but grounded in a
  real signal instead of just iterating on prompts by feel.

## My stretch, and whether I pulled it off

The hardest part of this was designing the agreement check to be genuinely
cheap. Every paper I read used N extra calls — sample the same model multiple
times, or call a second/third model. I didn't want to add a separate call at
all, so I folded the agreement check into the *same* structured-output call
that already produces `findings` and the confidence score, by extending that
one schema to also report `agreement_ratio`. That's actually cheaper than my
original plan (which still used a second call) — zero additional LLM calls,
not just one fewer than the literature's approach. I think the design is
sound and the cost story is real. What I have **not** fully pulled off under
this timebox is rigorous validation that the resulting blended score is
actually *better calibrated* than the original — I'm fairly confident it's
*more independent*, which is a necessary but not sufficient condition for
*better calibrated*. I'm flagging that gap directly rather than claiming more
than I've shown.

## Roads not taken

1. **Multi-model ensemble confidence** (rejected). Closest prior art (see the
   clinical-trial protocol source in RESEARCH.md) — average confidence across
   three different LLMs. Rejected because it multiplies LLM cost by 3x per
   research pass, directly fighting the per-query budget constraint this
   assignment also asks for. Doesn't fit this project's actual constraints,
   even though it's a legitimate approach in a less cost-constrained setting.

2. **Self-consistency sampling** (rejected). Ask the same LLM the same
   question N times, check agreement between the N answers. This is the
   single most common calibration technique in the papers I read. Rejected
   for the same reason as above (N extra LLM calls per pass), and because it
   checks whether the *model* is consistent with itself, not whether the
   *evidence* actually supports the claim — a model can be very consistently
   wrong if it has a strong, mistaken prior. Cross-source agreement checks
   against external evidence instead, which felt like a better fit for a
   research/retrieval system specifically, as opposed to a closed-book QA
   setting where self-consistency methods are usually evaluated.

3. **Hidden-state / probability-based confidence** (rejected). A couple of
   the papers I read use internal model signals (token probabilities, hidden
   states) rather than asking the model to verbalize confidence at all. I
   rejected this immediately as impractical for this project: this system
   uses the OpenAI API via LangChain, which doesn't expose hidden states, and
   token-level logprobs for structured output don't map cleanly onto "is
   this finding correct." It's a real approach in the literature, just not
   one available at this layer of the stack.
