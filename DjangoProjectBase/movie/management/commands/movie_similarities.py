import os

import numpy as np
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from dotenv import load_dotenv
from openai import OpenAI

from movie.models import Movie


class Command(BaseCommand):
    help = "Compare movies and a prompt using cosine similarity"

    def handle(self, *args, **kwargs):
        env_path = settings.BASE_DIR / "openAI.env"
        load_dotenv(env_path)

        api_key = os.getenv("openai_apikey")

        if not api_key:
            raise CommandError(
                f"OpenAI API key not found in {env_path}"
            )

        client = OpenAI(api_key=api_key)

        movie1 = Movie.objects.get(
            title="Frankenstein",
        )
        movie2 = Movie.objects.get(
            title="The House of the Devil",
        )

        if not movie1.emb or not movie2.emb:
            raise CommandError(
                "The selected movies do not have embeddings."
            )

        embedding1 = np.frombuffer(
            movie1.emb,
            dtype=np.float32,
        )
        embedding2 = np.frombuffer(
            movie2.emb,
            dtype=np.float32,
        )

        similarity = self.cosine_similarity(
            embedding1,
            embedding2,
        )

        prompt = (
            "película de terror sobre monstruos "
            "y hechos sobrenaturales"
        )

        response = client.embeddings.create(
            input=[prompt],
            model="text-embedding-3-small",
        )

        prompt_embedding = np.asarray(
            response.data[0].embedding,
            dtype=np.float32,
        )

        prompt_movie1 = self.cosine_similarity(
            prompt_embedding,
            embedding1,
        )
        prompt_movie2 = self.cosine_similarity(
            prompt_embedding,
            embedding2,
        )

        self.stdout.write(
            f"Movie 1: {movie1.title}"
        )
        self.stdout.write(
            f"Movie 2: {movie2.title}"
        )
        self.stdout.write(
            f"Prompt: {prompt}"
        )
        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                f"Cosine similarity between movies: "
                f"{similarity:.4f}"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Prompt vs {movie1.title}: "
                f"{prompt_movie1:.4f}"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Prompt vs {movie2.title}: "
                f"{prompt_movie2:.4f}"
            )
        )

    def cosine_similarity(self, vector_a, vector_b):
        denominator = (
            np.linalg.norm(vector_a)
            * np.linalg.norm(vector_b)
        )

        if denominator == 0:
            raise CommandError(
                "Cannot calculate similarity with a zero vector."
            )

        return float(
            np.dot(vector_a, vector_b) / denominator
        )