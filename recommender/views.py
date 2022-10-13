
from recommender.forms import SearchForm
from django.shortcuts import render
from django.http import Http404
from .models import Musicdata
from .forms import SearchForm
import random


def find_albums(artist, from_year = None, to_year = None):
    query = Musicdata.objects.filter(track_artist__contains = artist)
    if from_year is not None:
        query = query.filter(track_album_release_date__gte = from_year)
    if to_year is not None:
        query = query.filter(track_album_release_date__lte = to_year)
    return list(query.order_by('-track_popularity').values('track_id'))
    

def find_album_by_name(album):
    query = Musicdata.objects.filter(track_name__contains = album).values('track_id')
    resp = list(query)
    # Randomize to get different results each time
    random.shuffle(resp) 
    # Return the id of up to 3 albums
    return { 
        'albums': [item['track_id'] for item in resp[:3]]
    }


def get_artist(request):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SearchForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            from_year = None if form.cleaned_data['from_year'] == None else int(form.cleaned_data['from_year'])
            to_year = None if form.cleaned_data['to_year'] == None else int(form.cleaned_data['to_year'])
            albums = find_albums(
                    form.cleaned_data['artist'],
                    from_year,
                    to_year
                )
            
            # Random 3 of top 10 popular albums
            answer = albums[:10]
            random.shuffle(answer)
            answer = list(answer)[:3] 
            return render(request, 'recommender/artist.html', {'form': form, 'albums': answer })
        else:
            raise Http404('Something went wrong')
    else:
        form = SearchForm()
        return render(request, 'recommender/artist.html', {'form': form})

def get_album(request):
    if request.method == 'GET':
        album = request.GET.get('album', None)
        if album is None:
            return render(request, "recommender/album.html", {})
        else:
            albums = {}
            if album != "":
                albums = find_album_by_name(album)
            return render(request, "recommender/results.html", albums)
  
