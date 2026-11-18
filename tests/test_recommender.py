from src.recommender import Song, UserProfile, Recommender, score_song, recommend_songs

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


# --- Tests for the actual production scoring/ranking logic used by src/main.py
# and src/app.py: score_song() and recommend_songs(). The Recommender class above
# is an unused stub and is not exercised by the app, so these are tested separately.

SONG_POP = {
    "id": "1", "title": "Pop Perfect", "artist": "Test Artist",
    "genre": "pop", "mood": "happy",
    "energy": "0.9", "valence": "0.85", "danceability": "0.9",
    "acousticness": "0.1", "tempo_bpm": "128",
}
SONG_LOFI = {
    "id": "2", "title": "Lofi Mismatch", "artist": "Test Artist",
    "genre": "lofi", "mood": "relaxed",
    "energy": "0.2", "valence": "0.5", "danceability": "0.3",
    "acousticness": "0.7", "tempo_bpm": "75",
}


def test_score_song_perfect_match_scores_one_with_all_reasons():
    user_prefs = {
        "genre": "pop", "mood": "happy", "energy": 0.9, "valence": 0.85,
        "danceability": 0.9, "acousticness": 0.1, "tempo": 128,
    }
    score, reasons = score_song(user_prefs, SONG_POP)

    assert score == 1.0
    assert reasons == [
        "energy match", "valence match", "danceability match",
        "acousticness match", "tempo match", "genre match", "mood match",
    ]


def test_score_song_only_scores_features_present_in_user_prefs():
    user_prefs = {"energy": 0.9}
    score, reasons = score_song(user_prefs, SONG_POP)

    assert reasons == ["energy match"]
    assert round(score, 4) == round(0.4615 * 1.0, 4)


def test_score_song_genre_and_mood_mismatch_gives_no_bonus():
    user_prefs = {"genre": "pop", "mood": "happy"}
    score, reasons = score_song(user_prefs, SONG_LOFI)

    assert reasons == []
    assert score == 0.0


def test_score_song_clamps_out_of_range_inputs_to_zero_one():
    user_prefs = {
        "genre": "edm", "mood": "euphoric", "energy": 1.5, "valence": -0.3,
        "danceability": 2.0, "acousticness": 0.0, "tempo": 999,
    }
    score, reasons = score_song(user_prefs, SONG_POP)

    assert 0.0 <= score <= 1.0
    assert isinstance(reasons, list)


def test_score_song_empty_preferences_scores_zero_with_no_reasons():
    score, reasons = score_song({}, SONG_POP)

    assert score == 0.0
    assert reasons == []


def test_recommend_songs_sorts_by_score_descending_and_formats_reasons():
    user_prefs = {
        "genre": "pop", "mood": "happy", "energy": 0.9, "valence": 0.85,
        "danceability": 0.9, "acousticness": 0.1, "tempo": 128,
    }
    results = recommend_songs(user_prefs, [SONG_LOFI, SONG_POP], k=5)

    assert [song["title"] for song, _, _ in results] == ["Pop Perfect", "Lofi Mismatch"]
    scores = [score for _, score, _ in results]
    assert scores == sorted(scores, reverse=True)
    top_song, top_score, top_reasons = results[0]
    assert top_score == 1.0
    assert isinstance(top_reasons, str)
    assert "genre match" in top_reasons


def test_recommend_songs_respects_k_limit():
    user_prefs = {"genre": "pop"}
    results = recommend_songs(user_prefs, [SONG_LOFI, SONG_POP], k=1)

    assert len(results) == 1
    assert results[0][0]["title"] == "Pop Perfect"
