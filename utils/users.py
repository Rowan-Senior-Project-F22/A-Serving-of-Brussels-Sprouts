import json


def init_users_preferences(request, available_genre_seeds):
    # Retrieve the current user, parse their preferences given the available
    # genre seeds and ensure genre seeds are in the list of Spotify genre seeds.
    current_user = request.user
    try:
        users_preferences = json.loads(current_user.preferences)
        if 'likes' not in users_preferences:
            users_preferences['likes'] = []
        if 'dislikes' not in users_preferences:
            users_preferences['dislikes'] = []
        users_preferences['likes'] = list(filter(lambda x: x in available_genre_seeds, users_preferences['likes']))
        users_preferences['dislikes'] = list(
            filter(lambda x: x in available_genre_seeds, users_preferences['dislikes']))
    except any as E:
        users_preferences = {
            "likes": [],
            "dislikes": []
        }
    return users_preferences
