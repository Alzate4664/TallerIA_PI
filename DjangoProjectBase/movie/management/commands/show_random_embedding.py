import numpy as np
from django.core.management.base import BaseCommand, CommandError

from movie.models import Movie


class Command(BaseCommand):
    help = "Display the embedding of a random movie"

    def handle(self, *args, **kwargs):
        movie = (
            Movie.objects
            .exclude(emb__isnull=True)
            .order_by("?")
            .first()
        )

        if movie is None or not movie.emb:
            raise CommandError(
                "There are no movies with stored embeddings."
            )

        embedding = np.frombuffer(
            movie.emb,
            dtype=np.float32,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Random movie: {movie.title}"
            )
        )
        self.stdout.write(
            f"Embedding dimensions: {len(embedding)}"
        )
        self.stdout.write(
            "First 20 embedding values:"
        )
        self.stdout.write(
            np.array2string(
                embedding[:20],
                precision=6,
                separator=", ",
            )
        )