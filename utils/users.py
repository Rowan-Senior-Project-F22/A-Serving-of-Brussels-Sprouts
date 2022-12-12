import ast
import json
import random

from recommender.models import User


def init_users_preferences(request, available_genre_seeds):
    # Retrieve the current user, parse their preferences given the available
    # genre seeds and ensure genre seeds are in the list of Spotify genre seeds.
    # Sanitize the input and commit changes to the user in the database.
    current_user = request.user
    try:
        users_preferences = ast.literal_eval(current_user.preferences)
        if 'friends' not in users_preferences:
            users_preferences['friends'] = 'Default'
        if available_genre_seeds is not None:
            if 'likes' not in users_preferences:
                users_preferences['likes'] = []
            if 'dislikes' not in users_preferences:
                users_preferences['dislikes'] = []
            users_preferences['likes'] = list(filter(lambda x: x in available_genre_seeds, users_preferences['likes']))
            users_preferences['dislikes'] = list(
                filter(lambda x: x in available_genre_seeds, users_preferences['dislikes']))
            current_user.preferences = users_preferences
            current_user.save()
    except BaseException as E:
        users_preferences = {
            "likes": [],
            "dislikes": []
        }
    return users_preferences


def generate_friend_recommendations(request, preference, search_query=None):
    """Generates a list of friend recommendations given a user preference. Retrieves
    all user objects. Then, for each user, appends a 3-tuple of the user's email,
    likes and dislikes to be matched against the primary user's preferences. There
    will be a limit of 12 users at a time.

    Not efficient but works.

    """
    raw_users = User.objects.all()
    result_set = []
    current_users_preferences = ast.literal_eval(request.user.preferences)
    initialized_users = []
    for user in raw_users:
        try:
            preferences = ast.literal_eval(user.preferences)
            if 'likes' in preferences and 'dislikes' in preferences:
                initialized_users.append((user, preferences['likes'], preferences['dislikes']))
        except:
            continue
    if preference == 'Similar':
        result_set = list(filter(lambda x: any(y in x[1] for y in current_users_preferences['likes'])
                                        or any(z in x[2] for z in current_users_preferences['dislikes']),
                              initialized_users))
        # At least one similar genre exists between users.
    elif preference == 'Opposite':
        # One genre that a user dislikes the other user likes.
        result_set = list(filter(lambda x: any(y in x[2] for y in current_users_preferences['likes'])
                                        or any(z in x[1] for z in current_users_preferences['dislikes']),
                              initialized_users))
    elif preference == 'Disparate':
        # No similar genres at all between users.
        result_set = list(filter(lambda x: not any(y in x[1] for y in current_users_preferences['likes'])
                                        and not any(z in x[2] for z in current_users_preferences['dislikes']),
                              initialized_users))
    elif preference == 'Default':
        # 2 users who share a like, 1 who share a dislike
        # Fetch as many as possible up to a multiple of 2 for likes.
        # Then, fetch 1 user for every 2 that were found in the likes.
        result_set = []
        similar_likes_users = list((filter(lambda x: any(y in x[1] for y in current_users_preferences['likes']), initialized_users)))
        similar_dislikes_users = list((filter(lambda x: any(y in x[2] for y in current_users_preferences['dislikes']), initialized_users)))
        num_likes_users = 0		
        num_dislikes_users = 0		
        for i in range(0, 9):		
             if len(similar_likes_users) == 0 and len(similar_dislikes_users) == 0:		
                 break		
             if i < 2 or (num_likes_users / num_dislikes_users != 2 and len(similar_likes_users) > 0):		
                 new_user = similar_likes_users[random.randint(0, len(similar_likes_users) - 1)]		
                 similar_likes_users.remove(new_user)		
                 result_set.append(new_user)		
                 num_likes_users += 1		
             elif len(similar_dislikes_users) > 0:		
                 new_user = similar_dislikes_users[random.randint(0, len(similar_dislikes_users) - 1)]		
                 similar_dislikes_users.remove(new_user)		
                 result_set.append(new_user)		
                 num_dislikes_users += 1

    full_results = list(map(lambda x: x[0], result_set))

    return full_results
