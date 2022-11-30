#!/usr/bin/python3

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import *
from musicshuffle import shuffle_music
import time
import random


# App config
app = Flask(__name__)

app.secret_key = 'ahfkEjkfd93F'
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'
TOKEN_INFO = "token_info"

@app.route('/')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    print(auth_url)
    return redirect(auth_url)


@app.route('/authorize')
def authorize():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect("/choosePlaylist")


@app.route('/choosePlaylist', methods=["GET", "POST"])
def choose_playlist():
    session[TOKEN_INFO], authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/')
    sp = spotipy.Spotify(auth=session.get(TOKEN_INFO).get('access_token'))
    results = {}
    iter = 0
    while True:
        offset = iter * 50
        iter += 1
        curGroup = sp.current_user_playlists(limit=50, offset=offset)['items']
        for item in curGroup:
            results[item["name"]] = item["id"]
        if len(curGroup) < 50:
            break
    if request.method == "POST":
        playlist = request.form.get("playlist")
        session["playlist"] = playlist
        playlist_id = results[playlist]
        session["playlist_id"] = playlist_id
        return redirect("/showTracks")
    return render_template("home.html", playlists=list(results.keys()))


@app.route("/calibrate", methods=["GET", "POST"])
def calibrate():
    tracks = shuffle_music.read_playlist(session.get("playlist_id", None))
    titles = list(tracks)
    n = 8 if len(titles) > 8 else len(titles)
    select_songs = random.sample(titles, n)
    if request.method == "POST":
        values = request.form.getlist("test")
        session["weights"] = list(zip(select_songs, values))
        return redirect("/shuffleTracks")
    return render_template("calibrate.html", select_songs=select_songs)


@app.route("/shuffleTracks", methods=["GET", "POST"])
def shuffle():
    tracks = shuffle_music.read_playlist(session.get("playlist_id", None))
    weights = session.get("weights", None)
    played_music = {}
    for song in weights:
        artists = tracks[song[0]]["artist"]
        n_tempo = tracks[song[0]]["tempo"]
        tempo = "s"
        if 80 < float(n_tempo) < 120:
            tempo = "m"
        else:
            tempo = "f"
        if song[0] not in played_music:
            played_music[song[0]] = {"artist": artists, "played": random.randint(int(song[1]) * 20 - 19, int(song[1]) * 20), "tempo": tempo}
    return render_template("display.html", playlist=session.get("playlist", None), shuffled=shuffle_music.shuffle_music(session.get("playlist_id", None), played_music))



@app.route("/showTracks", methods=["GET", "POST"])
def show_tracks():
    if request.method == "POST":
        return redirect('/calibrate')
    tracks = shuffle_music.read_playlist(session.get("playlist_id", None))
    return render_template("selected.html", tracks=tracks, playlist=session.get("playlist", None))


@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')


# Checks to see if token is valid and gets a new token if not
def get_token():
    token_valid = False
    token_info = session.get(TOKEN_INFO, {})

    # Checking if the session already has a token stored
    if not (session.get(TOKEN_INFO, False)):
        token_valid = False
        return token_info, token_valid

    # Checking if token has expired
    now = int(time.time())
    is_token_expired = session.get(TOKEN_INFO).get('expires_at') - now < 60

    # Refreshing token if it has expired
    if (is_token_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(session.get(TOKEN_INFO).get('refresh_token'))

    token_valid = True
    return token_info, token_valid


def create_spotify_oauth():
    return SpotifyOAuth(
        client_id="fae2d9d7e5f34629b24ec27f02146dab",
        client_secret="8aa1ddddcbb244ea9756d8384d3060e5",
        redirect_uri=url_for('authorize', _external=True),
        scope="user-library-read")


def main():
    app.run()