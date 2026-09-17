import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from dotenv import load_dotenv
from openai import OpenAI

from movie.models import Movie


class Command(BaseCommand):
    help = "Update the description of the first movie using OpenAI"

    def handle(self, *args, **kwargs):
        env_path = settings.BASE_DIR / "openAI.env"
        load_dotenv(env_path)

        api_key = os.getenv("openai_apikey")

        if not api_key:
            raise CommandError(
                f"OpenAI API key not found in {env_path}"
            )

        client = OpenAI(api_key=api_key)

        def get_completion(prompt, model="gpt-3.5-turbo"):
            messages = [
                {
                    "role": "user",
                    "content": prompt,
                }
            ]

            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0,
            )

            return response.choices[0].message.content.strip()

        instruction = (
            "Vas a actuar como un aficionado del cine que sabe describir "
            "de forma clara, concisa y precisa cualquier película en menos "
            "de 200 palabras. La descripción debe incluir el género de la "
            "película y cualquier información adicional que sirva para crear "
            "un sistema de recomendación."
        )

        movies = Movie.objects.order_by("id")
        self.stdout.write(f"Found {movies.count()} movies")

        for movie in movies:
            self.stdout.write(f"Processing: {movie.title}")

            try:
                prompt = (
                    f"{instruction} "
                    f"Vas a actualizar la descripción "
                    f"'{movie.description}' de la película "
                    f"'{movie.title}'."
                )

                self.stdout.write(
                    f"Original description: {movie.description}"
                )

                updated_description = get_completion(prompt)

                self.stdout.write(
                    f"Updated description: {updated_description}"
                )

                movie.description = updated_description
                movie.save(update_fields=["description"])

                self.stdout.write(
                    self.style.SUCCESS(f"Updated: {movie.title}")
                )

            except Exception as error:
                self.stderr.write(
                    self.style.ERROR(
                        f"Failed for {movie.title}: {error}"
                    )
                )

            # No eliminar: el taller exige procesar una sola película.
            break