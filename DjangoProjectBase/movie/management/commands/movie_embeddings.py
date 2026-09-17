import os

import numpy as np
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from dotenv import load_dotenv
from openai import OpenAI

from movie.models import Movie


class Command(BaseCommand):
    help = "Generate and store embeddings for all movies"

    def handle(self, *args, **kwargs):
        env_path = settings.BASE_DIR / "openAI.env"
        load_dotenv(env_path)

        api_key = os.getenv("openai_apikey")

        if not api_key:
            raise CommandError(
                f"OpenAI API key not found in {env_path}"
            )

        client = OpenAI(api_key=api_key)
        movies = list(Movie.objects.order_by("id"))

        if not movies:
            raise CommandError(
                "There are no movies in the database."
            )

        self.stdout.write(
            f"Found {len(movies)} movies in the database"
        )

        texts = [
            (movie.description or movie.title)
            .replace("\n", " ")
            .strip()
            for movie in movies
        ]

        self.stdout.write(
            "Requesting embeddings from OpenAI..."
        )

        try:
            response = client.embeddings.create(
                input=texts,
                model="text-embedding-3-small",
            )
        except Exception as error:
            raise CommandError(
                f"Failed to generate embeddings: {error}"
            ) from error

        if len(response.data) != len(movies):
            raise CommandError(
                "The number of returned embeddings does not "
                "match the number of movies."
            )

        with transaction.atomic():
            for movie, embedding_data in zip(
                movies,
                response.data,
            ):
                embedding = np.asarray(
                    embedding_data.embedding,
                    dtype=np.float32,
                )

                movie.emb = embedding.tobytes()

            Movie.objects.bulk_update(
                movies,
                ["emb"],
            )

        for movie in movies:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Embedding stored for: {movie.title}"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Finished generating embeddings for "
                f"{len(movies)} movies."
            )
        )