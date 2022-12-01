import random
import os
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials


def read_playlist(playlist_id):
    load_dotenv()

    client_id = os.getenv("CLIENT_ID", "")
    client_secret = os.getenv("CLIENT_SECRET", "")
    # OUTPUT_FILE_NAME = "track_info.csv"

    auth_manager = SpotifyClientCredentials(
        client_id=client_id, client_secret=client_secret
    )

    # create spotify session object
    session = spotipy.Spotify(auth_manager=auth_manager)

    # get uri from https link
    playlist_uri = "spotify:user:spotify:playlist:" + playlist_id

    # get list of tracks in a given playlist (note: max playlist length 100)
    tracks = session.playlist_items(playlist_uri)["items"]
    playlist = {}
    for track in tracks:
        id = track['track']['id']
        if id == None:
            continue
        features = session.audio_features(id)[0]
        features["artist"] = track['track']['artists'][0]['name'].split(',')
        playlist[track['track']['name']] = features
    return playlist



def p_like_artist(artist, played_data):
    count_like = 0
    count_dislike = 0
    count = 0
    for song in played_data.values():
        if artist[0] in song["artist"]:
            if song["played"] > 50:
                count_like += 1
            else:
                count_dislike += 1
            count += 1
    if count == 0:
        return 0
    return round(count_like / (count_like + count_dislike), 2)


def p_like_tempo(tempo, played_data):
    count_like = 0
    count_dislike = 0
    count = 0
    for song in played_data.values():
        if song["tempo"] == tempo:
            if song["played"] > 50:
                count_like += 1
            else:
                count_dislike += 1
    if count == 0:
        return 0
    return round(count_like / (count_like + count_dislike), 2)


def shuffle_music(playlist_id, played_music):
    new_p = read_playlist(playlist_id)

    ls = []
    for name, song in new_p.items():
        art = p_like_artist(song["artist"], played_music)
        temp = p_like_tempo(song["tempo"], played_music)
        ls.append([name, (art * 0.65 + temp * 0.35)])
    ls = [elem[0] for elem in sorted(ls, key=lambda x: x[1])]

    sorted_d = {}
    for i in ls:
        v = new_p[i]
        for art in v["artist"]:
            if art not in sorted_d:
                sorted_d[art] = []
            sorted_d[art].append(i)
    sorted_ls = [v for v in sorted_d.values()]

    for i in range(len(sorted_ls)):
        n = len(sorted_ls[i])
        tail_i = n - (n // 4)
        for j in range(tail_i, n):
            num = random.randint(1, tail_i - 1)
            sorted_ls[i][j], sorted_ls[i][num] = sorted_ls[i][num], sorted_ls[i][j]
    final = []
    vals = []
    for i in range(len(sorted_ls)):
        n = len(sorted_ls[i])
        final += sorted_ls[i]
        init_offset = random.uniform(0, 1/n)
        offsets = [random.uniform(-0.1/n, 0.1/n) for j in range(n)]
        vals += [j / n + init_offset + offsets[j] for j in range(n)]
    res = [s[1] for s in sorted((zip(vals, final)))]

    return res
