import base64
import os
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from dotenv import load_dotenv
from openai import OpenAI

from movie.models import Movie


class Command(BaseCommand):
    help = "Generate an image with OpenAI for the first movie"

    def handle(self, *args, **kwargs):
        env_path = settings.BASE_DIR / "openAI.env"
        load_dotenv(env_path)

        api_key = os.getenv("openai_apikey")

        if not api_key:
            raise CommandError(
                f"OpenAI API key not found in {env_path}"
            )

        client = OpenAI(api_key=api_key)

        images_folder = (
            Path(settings.MEDIA_ROOT) / "movie" / "images"
        )
        images_folder.mkdir(parents=True, exist_ok=True)

        movies = Movie.objects.order_by("id")
        self.stdout.write(f"Found {movies.count()} movies")

        for movie in movies:
            try:
                image_relative_path = self.generate_and_save_image(
                    client=client,
                    movie_title=movie.title,
                    save_folder=images_folder,
                )

                movie.image = image_relative_path
                movie.save(update_fields=["image"])

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Saved and updated image for: {movie.title}"
                    )
                )

            except Exception as error:
                self.stderr.write(
                    self.style.ERROR(
                        f"Failed for {movie.title}: {error}"
                    )
                )

            # No eliminar: solamente se procesa la primera película.
            break

        self.stdout.write(
            self.style.SUCCESS(
                "Process finished (only first movie updated)."
            )
        )

    def generate_and_save_image(
        self,
        client,
        movie_title,
        save_folder,
    ):
        prompt = (
            "Create an original cinematic poster for a fictional "
            "high-speed street-racing action movie. Show sports cars "
            "racing through a city at night, dramatic lighting, motion "
            "blur and an intense action atmosphere. Do not include people, "
            "movie titles, text, logos, brands or existing characters."
        )

        response = client.images.generate(
            model="gpt-image-2.5-sunburst",
            prompt=prompt,
            size="1024x1024",
            quality="low",
            n=1,
        )

        image_base64 = response.data[0].b64_json

        if not image_base64:
            raise ValueError(
                "The API did not return generated image data."
            )

        image_bytes = base64.b64decode(image_base64)
        image_filename = f"m_{movie_title}.png"
        image_path = save_folder / image_filename

        image_path.write_bytes(image_bytes)

        return f"movie/images/{image_filename}"