# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**MusiMist 2.0**

---

## 2. Goal / Task

MusiMist ranks a fixed song catalog for a listener. The listener gives a few preferences: favorite genre, favorite mood, target energy level, and other numeric dials (valence, danceability, acousticness, tempo). The model scores every song against those preferences and returns the top-k matches (default 5), each with a short, deterministic reason like "energy match, genre match."

On top of that ranking, each recommendation now gets a natural-language explanation generated through a small retrieval-augmented generation (RAG) pipeline: relevant notes are retrieved from a local knowledge base, a Claude model drafts a 1-2 sentence explanation grounded in those notes and the computed match reasons, and a groundedness check verifies the explanation before it's shown. If the API key is missing, the call fails, or the explanation isn't grounded, the system falls back to a deterministic, template-based explanation instead. The project is usable either through a CLI runner (`src/main.py`) or a Streamlit web UI (`src/app.py`).

It does not predict future listens or learn from behavior. It only ranks and explains the catalog it already has, based on the preferences given in that moment.

---

## 3. Data Used

The catalog is `data/songs.csv`. It has 30 songs. Each song has a title, artist, genre, mood, and five numeric features: energy, tempo, valence, danceability, and acousticness.

The catalog covers 27 genres and 26 moods, including afrobeats, ambient, bossa nova, classical, edm, folk, hip hop, jazz, k-pop, lofi, pop, r&b, rock, and more. I added about 20 songs and a sample user profile to the original starter catalog.

A second, smaller dataset was added to support explanations: `data/knowledge/` holds three JSON note files — one per-song note (30), one per-genre note (27), and one per-mood note (26). These are short, hand-written text snippets that ground the RAG explanations; they are retrieved by TF-IDF similarity in `src/retrieval.py`, not learned.

**Limits:** With only 30 songs across so many genres and moods, most genre/mood combinations have just one or two matching songs. There's no real listener data — no play counts, skip rates, lyrics, language, or popularity. The model also can't represent a listener whose taste blends two genres or moods at once. The knowledge-base notes are hand-written and limited to the 30 songs/27 genres/26 moods already in the catalog, so explanations can't draw on anything outside that fixed set.

---

## 4. Algorithm Summary

**Ranking.** Every song has five "dials": energy, valence, danceability, acousticness, and tempo. The listener sets target values for the same dials, plus a favorite genre and mood.

For each dial, the model checks how close the song's value is to the listener's target. A perfect match earns full points; the score shrinks as the gap grows. Dials don't count equally: energy is weighted highest at 0.4615, valence and danceability each get 0.1538, and acousticness and tempo each get 0.1154. (These are the weights from the Section 6 sensitivity experiment — energy's original weight was doubled and the rest renormalized — which were then kept as the final weights.) Adding up the weighted dials gives a base score from 0 to 1.

On top of that, a song gets a +0.075 bonus if its genre matches the listener's favorite genre (halved from the original +0.15 bonus, also from the Section 6 experiment), and a +0.05 bonus if its mood matches. The final score is capped at 0–1. Whenever a dial or bonus lines up closely, the model records a plain-language reason (like "tempo match") so each pick can be explained.

The model scores the whole catalog, sorts it high to low, and returns the top k.

**Explanation (RAG).** For each recommended song, `src/retrieval.py` retrieves the song's own note plus the most similar genre/mood notes (TF-IDF cosine similarity) from the local knowledge base. `src/explain.py` sends those notes, the listener's preferences, and the computed match reasons to a Claude model (`claude-haiku-5-5`), instructed to explain the pick in 1-2 sentences using only those facts. `src/groundedness.py` then checks what fraction of the generated explanation's meaningful words are actually backed by that allowed vocabulary; if the score falls below a 0.6 threshold — or the API key is missing, or the call fails, or the response is empty — the system substitutes a deterministic, template-based explanation built directly from the match reasons, so a result is never shown ungrounded.

---

## 5. Observed Behavior / Biases

**Mood barely matters.** Mood is worth only a small +0.05 bonus, while the five numeric dials make up most of the score. For example, "Gym Hero" (mood: intense) tied for the #1 pick for a listener who asked for mood "happy," just because its energy, danceability, and tempo were a near-perfect fit. Mood acts more like a tie-breaker than a real filter.

**Genre can crowd out fit.** Because genre match is a flat bonus, results can skew toward one genre even when the underlying dials are a mediocre fit for that listener. This is more pronounced now that the genre bonus has been halved (0.15 → 0.075; see Section 6), so genre carries even less weight relative to the numeric dials than before.

**Fixed weights favor energy-driven tastes, and this is now baked in permanently.** Energy is weighted at 0.4615 — the highest of any dial by a wide margin — so listeners whose taste hinges on tempo or acousticness are underserved relative to listeners whose taste hinges on energy and valence. The Section 6 experiment that raised energy's weight and lowered the genre bonus was adopted as the final configuration, which sharpens this bias rather than correcting it.

**Underrepresented genres get thin results.** Genres with only one or two songs (e.g., choral, pacific fusion, world fusion) can't produce a strong top-5 no matter how good the match is.

**RAG explanations inherit the ranking's blind spots, but add their own failure mode.** Because explanations are grounded only in the song's note, genre/mood notes, and the computed match reasons, an explanation can faithfully describe *why the scorer* picked a song (e.g., "strong energy and tempo match") even when that pick is a poor fit for what the listener actually meant (e.g., matching on energy while ignoring a requested mood). The groundedness check catches hallucinated facts, not bad recommendations — it cannot tell the listener that the underlying rank itself may be a poor fit.

---

## 6. Evaluation Process

**Ranking evaluation.** I tested seven user profiles through `src/main.py`: three realistic listeners (High-Energy Pop, Chill Lofi, Deep Intense Rock) and four adversarial edge cases (conflicting energy/mood, out-of-range feature values, empty preferences, and an unknown genre/mood).

For each profile, I checked three things: did the requested genre/mood show up near the top, did the listed reasons match the song's real attributes, and were scores sorted correctly.

I also compared profiles pairwise. Opposite-taste profiles (e.g., High-Energy Pop vs. Chill Lofi) shared almost no songs, which is expected. Similar-energy profiles with different genres (High-Energy Pop vs. Deep Intense Rock) overlapped somewhat but still diverged on valence, which is also expected.

Two adversarial cases broke the model the same way: out-of-range values (e.g., danceability of 2.0) and empty preferences both caused every song to score 0.00, with no warning to the user that the result was meaningless. An unknown genre/mood did not break anything — it just fell back to pure numeric similarity.

**Weight sensitivity experiment.** As a follow-up, I doubled energy's weight (0.30 → 0.60 before renormalizing) and halved the genre bonus (0.15 → 0.075), then re-ran all seven profiles. Energy-extreme profiles barely changed at the top. The low-energy Chill Lofi profile got worse: genre-matching lofi tracks slipped down in favor of tracks that were merely energy-closer. This confirmed the bias in Section 5 — favoring energy weighting doesn't make results more accurate, just different. These shifted weights (`FEATURE_WEIGHTS` and `GENRE_BONUS` in `src/recommender.py`) were ultimately kept as the production configuration, for reasons the Section 8 reflection discusses.

No formal ranking metrics (precision/recall) were computed, since there's no ground-truth ranking to compare against. Ranking evaluation was done by checking plausibility across profiles.

**RAG explanation evaluation.** The explanation pipeline is covered by automated tests in `tests/test_retrieval.py`, `tests/test_groundedness.py`, and `tests/test_explain.py`, which check that: the knowledge base loads all three note types, TF-IDF retrieval ranks the relevant genre note highly for a query, a song's own note is always included in its context, a grounded explanation scores high on the groundedness check, a fabricated explanation scores low, and `generate_explanation` falls back to the deterministic explanation when the API key is missing, the API call raises, or the generated text fails the groundedness check. I also ran the same seven profiles through `src/main.py` and `src/app.py` to confirm both entry points produce explanations and correctly label each one as LLM-generated or fallback.

---

## 7. Ideas for Improvement

1. **Let users weight their own preferences.** Right now one fixed weight set applies to everyone. User-adjustable weights would reduce the energy bias in Section 5.
2. **Validate inputs.** Reject or clamp out-of-range values instead of silently returning a meaningless 0.00 ranking.
3. **Add diversity re-ranking.** Penalize multiple songs from the same artist or genre in one top-k list, so results don't collapse into a single narrow cluster.
4. **Let the explanation surface ranking weaknesses, not just justify the pick.** Since groundedness only checks that an explanation's claims are supported, not that the pick itself is a good fit, a more honest explanation could note when a song matches on some dials (e.g., energy) but misses the listener's stated genre or mood.
5. **Expand the knowledge base beyond the fixed catalog.** The RAG notes only cover the 30 songs/27 genres/26 moods already in `data/songs.csv`; broader notes (artist background, lyrical themes) would let explanations say more without risking ungrounded claims.

---

## 8. Reflection and Ethics: Thinking Critically About Your AI

### Limitations and Biases

* see point 5

### Potential Misuse and Prevention

* **Groundedness check as a guardrail against hallucinated or manipulated output.** Because `score_groundedness` only lets an explanation through if most of its meaningful words trace back to the song's note, the computed match reasons, or the listener's own stated preferences, it blocks the model from inventing unsupported claims about a song or artist — whether that's an honest hallucination or an attempt (via a crafted title/prompt) to get the model to say something it wasn't given grounds for. It can't catch everything (a short, low-content injected phrase could slip past the word-overlap check), but it closes off the most obvious path to unchecked LLM output reaching the listener.


* **Deterministic fallback as a guaranteed safe default.** Whenever the groundedness check fails, the API key is missing, the call raises, or the response is empty, `generate_explanation` always returns the template-based explanation built only from the computed match reasons — never a half-trusted or partially-grounded LLM output. This means the system has no code path where an ungrounded or unavailable LLM response reaches the user unfiltered: worst case, they get a flat but reliably accurate explanation.


### Surprises in Reliability Testing

Two things suprised me. 

- I was suprised by AI's ability to read the sentences in song_notes.json and paraphrase them without hallucinating. I had never used RAG before and this suprised me to see AI not making things up.
- However, I was also shocked by AI's failure to produce an output sometimes. On different runs it doesn't give an output. And this has taught me the importance of guardrails in AI-Native development. This might be a small scale project, but on a larger scale, if no guardrails in place, AI can backfire.

### Collaboration with AI

**Overview of collaboration:**

* Claude helped me to identify the best way and functionality to implement RAG, test it and set guardrails. I knew I wanted to work on the music recommender simulation project, but I wasn't sure of what functionality to implement and Claude helped me identify one, which ended up being the explanation of the suggestions. This was the best implementation since we could collect information on the songs in separate documents (json files).

**A suggestion I accepted:**

* Claude suggested to add in a groundedness check to make sure that if we have a way to verify that the model did not hallucinate i.e the explanation passes only if its words trace back to the songs_notes.json. This allowed me to add a fallback response.

**A suggestion I did not accept as written (and why):**

* Claude suggested not to use APIs to call an LLM on song_notes.json and rather use a local based retrieval. I did not accept this because I wanted to test wether the LLM will hallucinate and not retrieve well the information on songs I have created. So, I chose to use an API to claude's Haiku 5.5 model.
