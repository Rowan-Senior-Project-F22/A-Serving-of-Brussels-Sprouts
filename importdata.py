import csv
from recommender.models import Musicdata

# songs_header = [
#     'track_id','track_name','track_artist','track_popularity',
#     'track_album_id','track_album_name','track_album_release_date',
#     'playlist_name','playlist_id','playlist_genre','playlist_subgenre',
#     'danceability','energy','key','loudness','mode','speechiness',
#     'acousticness','instrumentalness','liveness','valence','tempo',
#     'duration_ms'
# ]

def import_data():
    print("Please input csv file name: ")
    filename = input()
    songs = open(filename, encoding='utf-8')
    csvfile = csv.DictReader(songs)

    id = 1
    for row in csvfile:
        row['id'] = id
        row['track_album_release_date'] = int(row['track_album_release_date'].split("-")[0])
        song = Musicdata(**row)
        song.save()
        id = id + 1

import_data()
