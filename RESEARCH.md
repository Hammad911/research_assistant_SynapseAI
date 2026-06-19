# RESEARCH.md

## The problem

This system asks an LLM to self-report a `confidence_score` (0–10) on its own
research findings, and uses that score to route between "go straight to
synthesis" and "send to the validator for another pass." That number is the
single most important signal in the whole control flow — it decides whether
the user gets an answer immediately or whether the system spends more
time/tokens checking itself. So: how much should we actually trust an LLM's
own verbalized confidence?

Short answer from the literature: not much, on its own.

## What I read

**1. "Calibrating Verbalized Confidence with Self-Generated Distractors"**
(Wang & Stengel-Eskin, UT Austin, arXiv:2509.25532, 2025)
https://arxiv.org/pdf/2509.25532

This paper's starting premise is exactly the failure mode I care about:
verbalized LLM confidence is empirically miscalibrated, with models reporting
high confidence on claims they get wrong. Their explanation is interesting —
they attribute this to "suggestibility": when a model has weak internal
knowledge about a topic, it tends to just adopt whatever framing or claim is
in front of it as true, rather than genuinely assessing it. Their fix
(DINCO) has the model rate confidence across several self-generated
*alternative* claims and normalizes across them.

*Where I agree*: the suggestibility framing matches what I'd expect from this
assistant's own research agent — it's asked to read search results and then
immediately rate its own confidence in the same call, with the search content
sitting right there in context. There's no independent check.

*Where I diverge*: DINCO fixes this by generating distractor claims and
re-querying the same LLM multiple times (their paper notes 10 DINCO calls
beat 100 self-consistency samples — still meaningfully more LLM calls).
That's a reasonable trade for a research benchmark, but it conflicts directly
with this project's own cost-budget requirement (A1). I wanted a calibration
signal that doesn't multiply LLM calls.

**2. "The Illusion of Confidence: Why Asking Your LLM 'Are You Sure?' Is a
Terrible Idea"** (Jasleen, Medium / Data Science Collective, Oct 2025)
https://medium.com/data-science-collective/the-illusion-of-confidence-why-asking-your-llm-are-you-sure-is-a-terrible-idea-84eb5859fc26

Not a peer-reviewed source, but useful as a concrete, citable data point: it
reports GPT-4 assigning its highest possible confidence score to roughly 87%
of its responses, including ones that were factually wrong. The article's
explanation — that asking for confidence is "predicting the next most likely
token," not introspection — is the layperson version of the suggestibility
argument above. I'm treating this as illustrative rather than load-bearing;
the arXiv papers are doing the actual evidentiary work.

*Where I agree*: this is consistent with what I'd expect to see if I logged
this system's own `confidence_score` outputs over many runs — a small,
informal thing I did not have time to do rigorously, which I'm flagging
honestly rather than claiming I validated it on this codebase.

**3. "Graph-based Confidence Calibration for Large Language Models"**
(arXiv:2411.02454)
https://arxiv.org/pdf/2411.02454

This paper's framing is the one that most directly shaped my design choice.
It notes that self-consistency-based calibration — generating multiple
responses from the *same model* and checking agreement between them — already
shows a strong correlation with actual correctness, but that naive
self-consistency uses hand-crafted features and doesn't calibrate well on its
own; their contribution is a learned graph model over response-similarity to
improve on plain self-consistency.

*Where I agree*: agreement-based signals (does the model agree with itself,
or with independent sources) are a stronger and cheaper signal than
verbalized self-report.

*Where I diverge*: their agreement signal is built by sampling the *same* LLM
multiple times on the *same* question. That's still N extra LLM calls. I
wanted to get an agreement signal "for free" using something this system
already produces — the multiple independent search results from Tavily —
rather than spending more LLM budget to manufacture agreement data.

**4. "Mitigating Automation Bias in Physician-LLM Diagnostic Reasoning Using
Behavioral Nudges"** (clinical trial protocol, NCT07328815)
https://cdn.clinicaltrials.gov/large-docs/15/NCT07328815/Prot_SAP_000.pdf

This is a clinical-trial protocol document, not a typical ML paper, but it's
directly relevant: their rationale section explicitly rejects single-model
self-assessment in favor of an *ensemble* of three LLMs, averaging their
confidence as a less-biased signal, specifically because single-model
self-report is unreliable in a high-stakes (medical) decision context.

*Where I agree*: ensembling is a legitimate way to de-bias a single model's
self-report, and it's the closest prior art to my own approach in spirit —
both replace "trust one model's self-rating" with "trust an aggregate signal
derived from multiple independent things."

*Where I diverge, and where my idea comes from*: their ensemble is three
*models*. I don't have budget (per A1's cost constraint) to call three
different LLMs per research pass. But this system's `research_node` already
fetches `max_search_results` independent search results per query — and
nothing currently checks whether those sources actually agree with each other
on the facts the findings claim. That's an existing, already-paid-for source
of redundancy that nobody is using as a calibration signal.

**5. "Confidence-Calibrated Small-Large Language Model Collaboration for
Cost-Efficient Reasoning"** (arXiv:2603.03752)
https://arxiv.org/pdf/2603.03752

Useful mainly for its literature summary (section 2.2): it categorizes
calibration approaches into (a) verbalized confidence via prompting — varies
significantly by task/template — and (b) introspection via hidden
states/auxiliary classifiers — doesn't generalize out-of-distribution. Neither
category is "look at whether your independent evidence sources actually
agree with each other," which reinforced that this was a gap worth filling
rather than something already well-covered.

## My point of view

Every approach I found for fixing unreliable verbalized confidence pays for
it with more LLM calls: self-consistency sampling, distractor generation, or
multi-model ensembles. That's a reasonable trade in a research setting, but
it's in direct tension with a production constraint this assignment itself
imposes — a per-query token/cost budget.

My take: **for a system like this one, which already does multi-source
retrieval, cross-source agreement is a confidence signal that's sitting on
the table unused, and it's nearly free** — the sources are already fetched
and paid for, and the agreement check rides along inside the same
structured-output call that already produces `findings` and a confidence
score, rather than adding any new LLM call. It won't be as rigorous as a
proper calibration method trained against ground truth, but it directly
targets the suggestibility failure mode from source 1: a model that's
"adopting whatever's in front of it" as true will, by definition, fail to
notice when only one source out of five actually supports the claim it's
making — because it isn't currently being asked to check.

## What I'd build with more time

Properly evaluate this against a labeled set (does agreement_ratio actually
correlate with whether findings were later judged correct/sufficient by a
human, not just by the validator LLM — which has the same self-report problem
one level up). Right now I'm trading one unverified self-report for a
slightly-less-unverified one; I haven't proven the new signal is better, only
that it's structurally more independent. That's the most important caveat
on this whole feature and I want to say it plainly rather than overclaim it.
