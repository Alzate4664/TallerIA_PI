from django.shortcuts import render
from django.http import HttpResponse
from .models import Movie

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import io
import base64

# Create your views here.

def home(request):
    searchTerm = request.GET.get('searchMovie')

    if searchTerm:
        movies = Movie.objects.filter(title__icontains=searchTerm)
    else:
        movies = Movie.objects.all()

    return render(request,'home.html',{
        'name': 'Miguel Alzate',
        'searchTerm': searchTerm,
        'movies': movies
    }
)

def about(request):
    #return HttpResponse('<h1>Welcome to About Page</h1>')
    return render(request, 'about.html')

def statistics_view(request):
    all_movies = Movie.objects.all()

    movie_counts_by_year = {}

    for movie in all_movies:
        year = movie.year if movie.year else "None"

        if year in movie_counts_by_year:
            movie_counts_by_year[year] += 1
        else:
            movie_counts_by_year[year] = 1

    bar_width = 0.5
    bar_positions = range(len(movie_counts_by_year))

    plt.figure(figsize=(10, 6))

    plt.bar(
        bar_positions,
        movie_counts_by_year.values(),
        width=bar_width,
        align='center'
    )

    plt.title('Movies per year')
    plt.xlabel('Year')
    plt.ylabel('Number of movies')

    plt.xticks(
        bar_positions,
        movie_counts_by_year.keys(),
        rotation=90
    )

    plt.subplots_adjust(bottom=0.3)

    buffer = io.BytesIO()

    plt.savefig(
        buffer,
        format='png',
        bbox_inches='tight'
    )

    buffer.seek(0)
    plt.close()

    image_png = buffer.getvalue()
    buffer.close()

    graphic = base64.b64encode(image_png).decode('utf-8')

    return render(request, 'statistics.html', {
        'graphic': graphic
    })

def genre_statistics_view(request):
    all_movies = Movie.objects.all()

    movie_counts_by_genre = {}

    for movie in all_movies:
        if movie.genre:
            first_genre = movie.genre.split(',')[0].strip()
        else:
            first_genre = "None"

        if first_genre in movie_counts_by_genre:
            movie_counts_by_genre[first_genre] += 1
        else:
            movie_counts_by_genre[first_genre] = 1

    bar_positions = range(len(movie_counts_by_genre))

    plt.figure(figsize=(10, 6))

    plt.bar(
        bar_positions,
        movie_counts_by_genre.values(),
        width=0.5,
        align='center'
    )

    plt.title('Movies per genre')
    plt.xlabel('Genre')
    plt.ylabel('Number of movies')

    plt.xticks(
        bar_positions,
        movie_counts_by_genre.keys(),
        rotation=90
    )

    plt.subplots_adjust(bottom=0.3)

    buffer = io.BytesIO()

    plt.savefig(
        buffer,
        format='png',
        bbox_inches='tight'
    )

    buffer.seek(0)
    plt.close()

    image_png = buffer.getvalue()
    buffer.close()

    graphic = base64.b64encode(image_png).decode('utf-8')

    return render(request, 'genre_statistics.html', {
        'graphic': graphic
    })