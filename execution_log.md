# Execution Log

Reproducible, literal command output captured on **2026-11-18**, committed as evidence
that the CLI, the RAG/groundedness pipeline, and the test suite actually run as
described in `README.md` and `model_card.md`. Nothing below is hand-edited — it's the
real stdout of each command.

---

## 1. CLI run with `ANTHROPIC_API_KEY` set (live Claude API calls)

Command:

```bash
PYTHONPATH=src python src/main.py
```

With a valid `ANTHROPIC_API_KEY` exported, every recommendation attempts a live call to
`claude-haiku-5-5` for its explanation. Explanations tagged `(LLM)` came back from the
API and passed the groundedness check; explanations tagged
`(LLM [UNGROUNDED, reverted to fallback])` came back from the API but were rejected by
`groundedness.py` and swapped for the deterministic fallback text, exactly as described
in the "Verify" / "Fallback" steps of the architecture overview.

```
==================================================
TOP RECOMMENDATIONS — High-Energy Pop
==================================================
Profile: {'genre': 'pop', 'mood': 'happy', 'energy': 0.9, 'valence': 0.85, 'danceability': 0.9, 'acousticness': 0.1, 'tempo': 128}

1. Sunrise City (by Neon Echo)
   Score:   1.00
   Reasons: energy match, valence match, danceability match, acousticness match, tempo match, genre match, mood match
   AI Explanation (LLM): "Sunrise City" by Neon Echo is a pop song with a happy mood that matches your preferences on every measure, including energy, danceability, valence, acousticness, and tempo, for a perfect 1.00 score. It's described as a bright, bouncy pop anthem that's good for starting the day on an upbeat note.

2. Gym Hero (by Max Pulse)
   Score:   1.00
   Reasons: energy match, valence match, danceability match, acousticness match, tempo match, genre match
   AI Explanation (LLM): "Gym Hero" by Max Pulse is a perfect 1.00 match: it lines up with your preferences for pop genre, energy, valence, danceability, acousticness, and tempo. It is a high-energy pop track whose tempo fits your target of 128, though its intense mood differs from the happy mood you listed.

3. Pulse Horizon (by Kai Nakamura)
   Score:   0.97
   Reasons: energy match, valence match, danceability match, acousticness match, tempo match
   AI Explanation (LLM [UNGROUNDED, reverted to fallback]): Recommended based on: energy match, valence match, danceability match, acousticness match, tempo match.

4. Noche Eterna (by Raul Mendoza)
   Score:   0.94
   Reasons: energy match, valence match, danceability match, acousticness match
   AI Explanation (LLM [UNGROUNDED, reverted to fallback]): Recommended based on: energy match, valence match, danceability match, acousticness match.

5. Lagos Nights (by Ngozi Adeyemi)
   Score:   0.94
   Reasons: energy match, valence match, danceability match, acousticness match, tempo match
   AI Explanation (LLM): "Lagos Nights" by Ngozi Adeyemi is a strong match (score 0.94) because it lines up with your preferences for energy, valence, danceability, acousticness, and tempo, and its jubilant mood fits your happy mood. Its afrobeats sound blends West African rhythms with pop sensibility, so it may appeal to your pop taste even though the genres differ.

==================================================


==================================================
TOP RECOMMENDATIONS — Chill Lofi
==================================================
Profile: {'genre': 'lofi', 'mood': 'relaxed', 'energy': 0.2, 'valence': 0.5, 'danceability': 0.3, 'acousticness': 0.7, 'tempo': 75}

1. Library Rain (by Paper Lanterns)
   Score:   0.93
   Reasons: energy match, valence match, tempo match, genre match
   AI Explanation (LLM): "Library Rain" by Paper Lanterns matches your taste in lofi, and its energy, valence, and tempo line up with your preferences. It's a soft, rain-soaked lofi instrumental meant for quiet study or winding down.

2. Still Waters (by Mei Lin Zhao)
   Score:   0.93
   Reasons: energy match, valence match, danceability match, tempo match
   AI Explanation (LLM [UNGROUNDED, reverted to fallback]): Recommended based on: energy match, valence match, danceability match, tempo match.

3. Midnight Coding (by LoRoom)
   Score:   0.91
   Reasons: valence match, acousticness match, tempo match, genre match
   AI Explanation (LLM): "Midnight Coding" by LoRoom matches your taste for lofi, with a close fit on valence, acousticness, and tempo. It's a mellow, warm, unobtrusive lofi loop, which suits a relaxed listening session.

4. Focus Flow (by LoRoom)
   Score:   0.91
   Reasons: valence match, acousticness match, tempo match, genre match
   AI Explanation (LLM): "Focus Flow" by LoRoom is a lofi track that matches your preferred genre, and its valence, acousticness, and tempo also line up with what you like. It's a warm, mellow loop, though its focused mood differs from the relaxed mood you listed.

5. Emerald Hills (by Siobhan O'Malley)
   Score:   0.90
   Reasons: energy match, valence match, danceability match, tempo match
   AI Explanation (LLM): "Emerald Hills" by Siobhan O'Malley earned a 0.90 match score because its energy, valence, danceability, and tempo fit your preferences, even though it's folk with a nostalgic mood rather than lofi with a relaxed one. It's a gentle acoustic folk song steeped in nostalgia for home and the past.

==================================================


==================================================
TOP RECOMMENDATIONS — Deep Intense Rock
==================================================
Profile: {'genre': 'rock', 'mood': 'intense', 'energy': 0.95, 'valence': 0.4, 'danceability': 0.4, 'acousticness': 0.05, 'tempo': 150}

1. Storm Runner (by Voltline)
   Score:   1.00
   Reasons: energy match, valence match, acousticness match, tempo match, genre match, mood match
   AI Explanation (LLM): "Storm Runner" by Voltline is a strong match for you because it hits your rock genre and intense mood, and its energy, valence, acousticness, and tempo all line up closely with your preferences. It's a driving, guitar-forward track with stormy intensity, built for high-energy moments.

2. Iron Reckoning (by Bjorn Eriksson)
   Score:   0.94
   Reasons: energy match, valence match, danceability match, acousticness match, tempo match
   AI Explanation (LLM): "Iron Reckoning" by Bjorn Eriksson scored 0.94 for you, matching your preferences on energy, valence, danceability, acousticness, and tempo. It's a heavy, distortion-driven metal track with tense, aggressive energy, so it fits your high-energy taste even though its genre is metal rather than rock.

3. Gym Hero (by Max Pulse)
   Score:   0.89
   Reasons: energy match, acousticness match, tempo match, mood match
   AI Explanation (LLM): "Gym Hero" by Max Pulse matches your preferences on energy, acousticness, tempo, and intense mood, though its pop genre differs from the rock you listed. It's a high-intensity workout anthem built to push through a tough gym set.

4. Shadow Walk (by Tyrese Banks)
   Score:   0.85
   Reasons: energy match, valence match, acousticness match, tempo match
   AI Explanation (LLM): "Shadow Walk" by Tyrese Banks is a heavy, bass-driven track with a rebellious edge, and it matches your taste on energy, valence, acousticness, and tempo, earning a 0.85 match score. Its trap genre and rebellious mood differ from your preferred rock genre and intense mood, so the match rests on how it sounds rather than on those labels.

5. Pulse Horizon (by Kai Nakamura)
   Score:   0.83
   Reasons: energy match, acousticness match
   AI Explanation (LLM): "Pulse Horizon" by Kai Nakamura matches your preferences on energy and acousticness, and it's a high-energy EDM track that builds toward a triumphant drop. Its genre and mood differ from your rock and intense picks, so the match rests on those two qualities rather than on style.

==================================================


==================================================
TOP RECOMMENDATIONS — Adversarial: Conflicting Energy/Mood
==================================================
Profile: {'genre': 'pop', 'mood': 'sad', 'energy': 0.9, 'valence': 0.1, 'danceability': 0.85, 'acousticness': 0.05, 'tempo': 140}

1. Gym Hero (by Max Pulse)
   Score:   0.95
   Reasons: energy match, danceability match, acousticness match, tempo match, genre match
   AI Explanation (LLM): "Gym Hero" by Max Pulse is a strong match at 0.95, mainly because it's pop like your preferred genre and lines up with your energy, danceability, acousticness, and tempo preferences. Its intense mood differs from the sad mood you listed, so that is the one preference it doesn't match.

2. Shadow Walk (by Tyrese Banks)
   Score:   0.89
   Reasons: energy match, danceability match, acousticness match, tempo match
   AI Explanation (LLM): "Shadow Walk" by Tyrese Banks scored 0.89 for you because its energy, danceability, acousticness, and tempo fit your preferences, even though its trap genre and rebellious mood differ from your pop and sad picks. It's a heavy, bass-driven track with a defiant edge.

3. Storm Runner (by Voltline)
   Score:   0.89
   Reasons: energy match, acousticness match, tempo match
   AI Explanation (LLM): "Storm Runner" by Voltline was recommended mainly for its energy, acousticness, and tempo, which match your preferences (score 0.89). It's a driving, guitar-forward rock track with an intense mood, so its genre and mood differ from the pop and sad mood you listed.

4. Sunrise City (by Neon Echo)
   Score:   0.88
   Reasons: energy match, danceability match, acousticness match, genre match
   AI Explanation (LLM [UNGROUNDED, reverted to fallback]): Recommended based on: energy match, danceability match, acousticness match, genre match.

5. Iron Reckoning (by Bjorn Eriksson)
   Score:   0.87
   Reasons: energy match, acousticness match
   AI Explanation (LLM): "Iron Reckoning" earned a match score of 0.87 because its energy and acousticness fit your preferences, even though it's a tense metal track rather than pop with a sad mood. It's a heavy, distortion-driven song with high intensity and very low acousticness.

==================================================


==================================================
TOP RECOMMENDATIONS — Adversarial: Out-of-Range Values
==================================================
Profile: {'genre': 'edm', 'mood': 'euphoric', 'energy': 1.5, 'valence': -0.3, 'danceability': 2.0, 'acousticness': 0.0, 'tempo': 999}

1. Sunrise City (by Neon Echo)
   Score:   0.00
   Reasons: no strong matches
   AI Explanation (LLM [UNGROUNDED, reverted to fallback]): Recommended based on: no strong matches.

2. Midnight Coding (by LoRoom)
   Score:   0.00
   Reasons: no strong matches
   AI Explanation (LLM): "Midnight Coding" is a poor match for your taste: it scored 0.00 with no strong matches, since it's a chill lofi track and you're looking for euphoric EDM. It's a warm, unobtrusive loop built for late-night focus sessions, which is quite different from the dancefloor sound you prefer.

3. Storm Runner (by Voltline)
   Score:   0.00
   Reasons: acousticness match
   AI Explanation (LLM [UNGROUNDED, reverted to fallback]): Recommended based on: acousticness match.

4. Library Rain (by Paper Lanterns)
   Score:   0.00
   Reasons: no strong matches
   AI Explanation (LLM): "Library Rain" by Paper Lanterns is a soft, rain-soaked lofi instrumental with a chill mood, meant for quiet study or winding down. It's a weak fit for your taste, since its lofi genre and chill mood don't match your EDM and euphoric preferences, and it scored 0.00 with no strong matches.

5. Gym Hero (by Max Pulse)
   Score:   0.00
   Reasons: acousticness match
   AI Explanation (LLM [UNGROUNDED, reverted to fallback]): Recommended based on: acousticness match.

==================================================


==================================================
TOP RECOMMENDATIONS — Adversarial: Empty Preferences
==================================================
Profile: {}

1. Sunrise City (by Neon Echo)
   Score:   0.00
   Reasons: no strong matches
   AI Explanation (LLM [UNGROUNDED, reverted to fallback]): Recommended based on: no strong matches.

2. Midnight Coding (by LoRoom)
   Score:   0.00
   Reasons: no strong matches
   AI Explanation (LLM [UNGROUNDED, reverted to fallback]): Recommended based on: no strong matches.

3. Storm Runner (by Voltline)
   Score:   0.00
   Reasons: no strong matches
   AI Explanation (LLM [UNGROUNDED, reverted to fallback]): Recommended based on: no strong matches.

4. Library Rain (by Paper Lanterns)
   Score:   0.00
   Reasons: no strong matches
   AI Explanation (LLM [UNGROUNDED, reverted to fallback]): Recommended based on: no strong matches.

5. Gym Hero (by Max Pulse)
   Score:   0.00
   Reasons: no strong matches
   AI Explanation (LLM): This pick has no strong match with your preferences, since your profile is empty and the match score is 0.00. It's a pop track with an intense mood, described as a high-intensity workout anthem built to push through a tough gym set.

==================================================


==================================================
TOP RECOMMENDATIONS — Adversarial: Unknown Genre/Mood
==================================================
Profile: {'genre': 'death-polka', 'mood': 'ecstatic-fear', 'energy': 0.5, 'valence': 0.5, 'danceability': 0.5, 'acousticness': 0.5, 'tempo': 110}

1. Dust Road Letters (by Marcus Bellweather)
   Score:   0.92
   Reasons: energy match, valence match, danceability match
   AI Explanation (LLM): "Dust Road Letters" scored 0.92 because its energy, valence, and danceability match your preferences. It's a wistful country track about long drives and old letters, though its genre and mood differ from the death-polka and ecstatic-fear you listed.

2. Monsoon Heart (by Priya Nair)
   Score:   0.92
   Reasons: energy match, danceability match, acousticness match
   AI Explanation (LLM [UNGROUNDED, reverted to fallback]): Recommended based on: energy match, danceability match, acousticness match.

3. Velvet Hours (by Jamal Whitfield)
   Score:   0.88
   Reasons: energy match, danceability match, acousticness match
   AI Explanation (LLM): "Velvet Hours" by Jamal Whitfield scored 0.88 mainly because its energy, danceability, and acousticness match your preferences, even though its r&b genre and sensual mood differ from what you listed. It's a smooth, slow-groove track with an intimate feel.

4. Tears in the Hallway (by Keisha Johnson)
   Score:   0.88
   Reasons: energy match, valence match, danceability match, acousticness match
   AI Explanation (LLM): "Tears in the Hallway" by Keisha Johnson earned a 0.88 match score because it lines up with your preferences for energy, valence, danceability, and acousticness. It is a raw, emotive soul ballad with a melancholic weight, so its genre and mood differ from the death-polka and ecstatic-fear you listed.

5. Midnight Coding (by LoRoom)
   Score:   0.88
   Reasons: energy match, valence match, danceability match
   AI Explanation (LLM [UNGROUNDED, reverted to fallback]): Recommended based on: energy match, valence match, danceability match.

==================================================
```

Note on the `[UNGROUNDED, reverted to fallback]` cases above: these show the
groundedness guardrail working as designed — the Claude API returned text, but
`groundedness.py` scored it below the `0.6` threshold (word-overlap with the
retrieved notes/match reasons was too low), so the system discarded it and showed
the deterministic fallback instead, never the ungrounded text itself. A sample of
the real warnings logged during this run (from `logs/app.log`, gitignored locally):

```
WARNING explain: Generated explanation for song 16 failed groundedness check (score=0.56); using fallback
WARNING explain: Generated explanation for song 12 failed groundedness check (score=0.58); using fallback
WARNING explain: Generated explanation for song 1 failed groundedness check (score=0.59); using fallback
```

---

## 2. Test suite run (offline, no API key required)

Command:

```bash
pytest
```

Output:

```
.................                                                        [100%]
17 passed in 1.18s
```

---

## How to reproduce

```bash
PYTHONPATH=src python src/main.py   # with ANTHROPIC_API_KEY set, for live LLM explanations
pytest                               # offline, deterministic
```
