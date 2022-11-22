import random
import uuid

import spotipy as spotipy

from recommender.models import *

cid = '2de1575d99b14786ae4f7e46e33e494e'
secret = 'fbf315776bda4ea2aaeeeb1ec559de7d'
client_credentials = spotipy.oauth2.SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials)


def generate_user_random(previous_user_id=None, index=0):
    """Generates 22 random users with random Genre seeds from spotify.

    """
    if index > 22:
        return
    random_uuid = uuid.uuid4()
    genre_list = list(sp.recommendation_genre_seeds().values())
    user_prefs_dict = {
        "likes": [],
        "dislikes": []
    }
    for i in range(0, 5):
        # Append 5 likes and 5 dislikes to the user preferences.
        rand = random.Random()
        user_prefs_dict['likes'].append(genre_list[rand.randint(0, len(genre_list))])
        user_prefs_dict['dislikes'].append(genre_list[rand.randint(0, len(genre_list))])
    user = User(
        email=f"testuser{random_uuid}@email.com",
        first_name="Test",
        last_name=f"User{random_uuid}",
        password="TESTPASSWORD123!",
        preferences=user_prefs_dict
    )
    user.save()
    if index % 2 == 0:
        # Generate a DM thread with random messages every 2
        # iterations.
        generate_dm_thread(user.id, previous_user_id)
    generate_user_random(user.id, index + 1)


def generate_random_post_data(user_id):
    pass


def generate_dm_thread(sender_user, receiver_user):
    """Generates a DM thread between two users.

    """
    pass


def populate_test_data():
    generate_user_random()
