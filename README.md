# 🎵 Music Recommender with Grounded AI Explanations

## Original Project

This project builds on **Music Recommender Simulation**, my project from Modules 1–3. The
original goal was a pure content-based filtering recommender: it represents songs and a
user "taste profile" as weighted audio features (energy, valence, danceability,
acousticness, tempo) plus genre/mood bonuses, scores every song in a small catalog against
a profile, and returns the top matches with a short list of deterministic "match reasons"
(e.g. `"energy match, genre match"`). It also included a multi-profile evaluation,
including adversarial edge cases, to probe where the simple scoring logic breaks down.

---

## Title and Summary

**Music Recommender with Grounded AI Explanations** takes that original scorer and adds a
retrieval-augmented generation (RAG) layer on top: instead of only printing a terse,
rule-based reason for each recommendation, it now asks Claude to explain the
recommendation in plain language — but only using facts retrieved from a small local
knowledge base, and only after checking that the generated text is actually grounded in
those facts. This matters because natural-language explanations make recommendations more
trustworthy and easier to act on, but an ungrounded LLM explanation (one that invents
details about a fictional song or artist) would be worse than no explanation at all. The
system is built so that it degrades safely: if there's no API key, the API fails, or the
generated text isn't grounded, the user still gets a correct, if plainer, explanation
instead of a crash or a hallucination.

---

## Architecture Overview

See [`diagrams/architecture.mmd`](diagrams/architecture.mmd) for the full diagram. At a
high level:

1. **Input**: a user's listening profile (genre, mood, numeric feature targets) and the
   song catalog (`data/songs.csv`), entered via the CLI (`src/main.py`) or the Streamlit
   UI (`src/app.py`).
2. **Score**: `recommender.recommend_songs()` scores and ranks every song using the
   feature-weighted similarity described below, producing a score and a list of match
   reasons per song.
3. **Retrieve**: for each recommended song, `retrieval.KnowledgeBase` uses TF-IDF
   (scikit-learn) over a small local corpus (`data/knowledge/*.json` — one note per song,
   genre, and mood) to pull the most relevant notes.
4. **Generate**: `explain.py` builds a prompt from *only* the retrieved notes, the
   computed score, and the computed match reasons, and asks Claude to explain the
   recommendation in 1–2 sentences.
5. **Verify**: `groundedness.py` checks what fraction of the generated explanation's
   words are actually backed by the retrieved notes and match reasons. Below a threshold
   (`0.6`), the explanation is discarded.
6. **Fallback**: a deterministic, LLM-free explanation (built straight from the
   computed match reasons) is always available and is used whenever the API key is
   missing, the API call fails, the model returns nothing, or the groundedness check
   fails.
7. **Output**: the final recommendation + explanation is returned to the user, and every
   step (retrieval, generation, fallback, groundedness score) is logged to
   `logs/app.log` for auditing.

---

## Setup Instructions

1. Create and activate a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac/Linux
   .venv\Scripts\activate         # Windows
   ```
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
3. (Optional) Enable AI-generated explanations by setting an Anthropic API key:

   ```bash
   export ANTHROPIC_API_KEY="your-key-here"   # Mac/Linux
   set ANTHROPIC_API_KEY=your-key-here        # Windows
   ```

   This step is optional — without a key, the app still runs correctly and prints a
   deterministic, rule-based explanation for every recommendation.
4. Run the CLI app (evaluates several built-in user profiles, including adversarial
   edge cases):

   ```bash
   PYTHONPATH=src python src/main.py
   ```
5. Or run the Streamlit web UI:

   ```bash
   PYTHONPATH=src streamlit run src/app.py
   ```
6. Run the test suite (all tests run offline, no API key required):

   ```bash
   pytest
   ```

---

## Sample Interactions

**1. High-Energy Pop profile, with `ANTHROPIC_API_KEY` set (grounded LLM explanation):**

```
Input profile: {'genre': 'pop', 'mood': 'happy', 'energy': 0.9, 'valence': 0.85,
                 'danceability': 0.9, 'acousticness': 0.1, 'tempo': 128}

1. Sunrise City (by Neon Echo)
   Score:   1.00
   Reasons: energy match, valence match, danceability match, acousticness match,
            tempo match, genre match, mood match
   Explanation: "Sunrise City is a near-perfect match for your high-energy, happy
   pop taste — it lines up with your preferred energy, valence, danceability,
   acousticness, and tempo, and matches both your genre and mood."
```

**2. Chill Lofi profile, no `ANTHROPIC_API_KEY` set (deterministic fallback):**

```
Input profile: {'genre': 'lofi', 'mood': 'relaxed', 'energy': 0.2, 'valence': 0.5,
                 'danceability': 0.3, 'acousticness': 0.7, 'tempo': 75}

1. Midnight Coding (by LoRoom)
   Score:   1.00
   Reasons: valence match, acousticness match, tempo match, genre match
   Explanation: "Recommended based on: valence match, acousticness match, tempo
   match, genre match."
```

**3. Adversarial: Conflicting Energy/Mood (`mood: "sad"` paired with `energy: 0.9`)
— shows the recommender taking the inputs at face value even when they contradict
each other:**

```
Input profile: {'genre': 'pop', 'mood': 'sad', 'energy': 0.9, 'valence': 0.1,
                 'danceability': 0.85, 'acousticness': 0.05, 'tempo': 140}

1. Gym Hero (by Max Pulse)
   Score:   0.99
   Reasons: energy match, danceability match, acousticness match, tempo match,
            genre match
   Explanation: "Gym Hero matches your target energy, danceability, acousticness,
   tempo, and genre, though your stated mood doesn't factor as strongly into the
   score as the numeric features do."
```

More profiles, including out-of-range values and empty preferences, are logged in
`logs/app.log` and summarized in `model_card.md`.

---

## Design Decisions

- **Pure content-based filtering over collaborative filtering**: with a small, fictional
  catalog and no real user history to draw on, comparing a song's own features to a
  user's stated preferences is the only signal actually available, so the system doesn't
  pretend to do collaborative filtering it can't support.
- **Separating the scoring rule from the retrieval/generation/verification pipeline**:
  `recommender.py` only ever decides *which* songs to recommend and *why* (in a handful
  of fixed, auditable reason strings). `explain.py` is a thin layer on top that turns
  those reasons into prose — it never influences ranking. This keeps the core
  recommendation logic deterministic and testable independent of whether an LLM is
  available at all.
- **Retrieval before generation**: the LLM is given a small, explicit set of retrieved
  notes rather than being asked to freely describe a (fictional) song and artist. This
  bounds what it's plausible for the model to say and makes the groundedness check
  meaningful — there is a concrete, finite vocabulary to check against.
- **A deterministic fallback is always available, never optional**: every failure mode
  (no API key, network/API error, empty model output, failed groundedness check) routes
  to the same `_deterministic_explanation()` function built directly from the computed
  match reasons. The trade-off is a plainer, more mechanical explanation in those cases,
  but it is always correct and never requires the LLM to be available — explanation
  quality degrades gracefully instead of the app crashing or showing nothing.
- **A fixed groundedness threshold (0.6) rather than per-call human review**: this makes
  the acceptance gate automatic and testable (see `tests/test_explain.py`), at the cost of
  being a blunter instrument than a human reviewer — a generated explanation that is true
  but phrased unusually could, in principle, score below the threshold and get swapped
  for the fallback unnecessarily.

---

## Testing Summary

- **What worked**: the deterministic scoring and ranking logic (`recommender.py`) is
  fully unit tested and behaves predictably, including the adversarial edge cases
  (out-of-range values, empty preferences, unknown genre/mood) worked through in the
  original Module 1–3 evaluation. The retrieval step (`retrieval.py`) and groundedness
  scoring (`groundedness.py`) are both deterministic and unit tested offline. End-to-end,
  the CLI and Streamlit app both run correctly with and without an `ANTHROPIC_API_KEY` set.
- **What didn't work / had to be handled**: during testing, the Claude API call
  occasionally returned a response with **no usable text content** (an empty
  `response.content` of text blocks, typically tied to how the model used its available
  output), which would otherwise have surfaced as a blank or broken explanation shown to
  the user. `src/explain.py` now explicitly checks for this (`if not generated_text:`),
  logs it as a warning, and swaps in the same deterministic fallback explanation used for
  a missing API key or a failed call — this is directly tested in
  `tests/test_explain.py`. The same fallback path also had to handle outright exceptions
  (e.g. network errors) and ungrounded text (e.g. a fabricated fact like "recorded live in
  Tokyo in 1998"), both of which are separately tested.
- **What I learned**: an LLM call has at least three distinct failure modes that all look
  different in code (no key, a raised exception, and a "successful" call that returns
  nothing usable or something ungrounded), and each needs its own explicit check rather
  than a single generic `try/except`. Building the fallback as the *default* path that
  every failure mode routes to — rather than bolting it on only for exceptions — made the
  system much easier to reason about and test, since "no LLM available" and "LLM available
  but failed verification" end up producing the exact same safe behavior for the user.

---

## Reflection

Before this course started, I was worried about AI taking our jobs as software engineers. Though a part of it is true, I learned a deeper truth: we still need to learn how to code! AI is a good companion as it streamlines the coding process and help me generate ideas and summarize information but you still need to learn how to troubleshoot it. 

Problem-solving is still the key of software engineering and this is what sets apart an avid and amateur developers. 

<!-- left intentionally empty -->
