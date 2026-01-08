import instaloader
import re
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os

IG_USERNAME = os.getenv("IG_USERNAME")
IG_PASSWORD = os.getenv("IG_PASSWORD")

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

POST_URL = os.getenv("POST_URL")

spotify = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    )
)

PATTERNS = [
    r'"(.+?)"',
    r'(.+?) - (.+)',
    r'(.+?) by (.+)',
]

def extract_songs(text):
    found = set()
    for p in PATTERNS:
        for m in re.findall(p, text, re.IGNORECASE):
            if isinstance(m, tuple):
                found.add(" ".join(m))
            else:
                found.add(m)
    return found

def spotify_link(query):
    result = spotify.search(q=query, type="track", limit=1)
    tracks = result["tracks"]["items"]
    if tracks:
        return tracks[0]["external_urls"]["spotify"]
    return None

def run():
    L = instaloader.Instaloader()
    L.login(IG_USERNAME, IG_PASSWORD)

    shortcode = POST_URL.split("/p/")[1].strip("/")
    post = instaloader.Post.from_shortcode(L.context, shortcode)

    results = {}

    for c in post.get_comments():
        for s in extract_songs(c.text):
            if s not in results:
                link = spotify_link(s)
                if link:
                    results[s] = link

    for song, link in results.items():
        print(f"{song} → {link}")

run()
