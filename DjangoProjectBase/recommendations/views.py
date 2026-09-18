import os

import numpy as np
from django.conf import settings
from django.shortcuts import render
from dotenv import load_dotenv
from openai import OpenAI

from movie.models import Movie


def cosine_similarity(vector_a, vector_b):
    denominator = np.linalg.norm(vector_a) * np.linalg.norm(vector_b)

    if denominator == 0:
        return -1.0

    return float(np.dot(vector_a, vector_b) / denominator)


def recommendation(request):
    prompt = request.GET.get("prompt", "").strip()

    recommended_movie = None
    best_similarity = None
    error = None

    if prompt:
        env_path = settings.BASE_DIR / "openAI.env"
        load_dotenv(env_path)

        api_key = os.getenv("openai_apikey")

        if not api_key:
            error = "OpenAI API key not found."
        else:
            try:
                client = OpenAI(api_key=api_key)

                response = client.embeddings.create(
                    input=[prompt],
                    model="text-embedding-3-small",
                )

                prompt_embedding = np.asarray(
                    response.data[0].embedding,
                    dtype=np.float32,
                )

                max_similarity = -1.0

                movies = Movie.objects.exclude(emb__isnull=True)

                for movie in movies:
                    if not movie.emb:
                        continue

                    movie_embedding = np.frombuffer(
                        movie.emb,
                        dtype=np.float32,
                    )

                    if movie_embedding.shape != prompt_embedding.shape:
                        continue

                    similarity = cosine_similarity(
                        prompt_embedding,
                        movie_embedding,
                    )

                    if similarity > max_similarity:
                        max_similarity = similarity
                        recommended_movie = movie

                if recommended_movie:
                    best_similarity = max_similarity
                else:
                    error = "No movies with valid embeddings were found."

            except Exception as exception:
                error = (
                    "Could not generate the recommendation: "
                    f"{exception}"
                )

    return render(
        request,
        "recommendations/recommendation.html",
        {
            "prompt": prompt,
            "recommended_movie": recommended_movie,
            "similarity": best_similarity,
            "error": error,
        },
    )
