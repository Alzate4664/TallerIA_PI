import re
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from movie.models import Movie


class Command(BaseCommand):
    help = "Update movie images from the delivered images folder"

    def handle(self, *args, **kwargs):
        source_folder = (
            settings.BASE_DIR
            / "images_workshop3"
            / "images"
        )

        destination_folder = (
            Path(settings.MEDIA_ROOT)
            / "movie"
            / "images"
        )

        if not source_folder.exists():
            self.stderr.write(
                self.style.ERROR(
                    f"Images folder not found: {source_folder}"
                )
            )
            return

        destination_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        special_files = {
            "Fairyland: A Kingdom of Fairies":
                source_folder / "m_Fairyland",
            "The Avenging Conscience: or 'Thou Shalt Not Kill'":
                source_folder / "m_The Avenging Conscience",
        }

        movies = Movie.objects.order_by("id")
        updated_count = 0
        skipped_count = 0

        self.stdout.write(
            f"Found {movies.count()} movies in the database"
        )

        for movie in movies:
            expected_file = (
                source_folder / f"m_{movie.title}.png"
            )

            if expected_file.exists():
                source_file = expected_file
                destination_name = expected_file.name

            elif movie.title in special_files:
                source_file = special_files[movie.title]
                destination_name = self.safe_filename(
                    movie.title
                )

            else:
                skipped_count += 1
                self.stderr.write(
                    self.style.WARNING(
                        f"Image not found, keeping current image: "
                        f"{movie.title}"
                    )
                )
                continue

            try:
                destination_file = (
                    destination_folder / destination_name
                )

                shutil.copy2(
                    source_file,
                    destination_file,
                )

                movie.image = (
                    f"movie/images/{destination_name}"
                )
                movie.save(update_fields=["image"])

                updated_count += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Updated image: {movie.title}"
                    )
                )

            except Exception as error:
                skipped_count += 1
                self.stderr.write(
                    self.style.ERROR(
                        f"Failed for {movie.title}: {error}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Finished updating {updated_count} movie images."
            )
        )

        self.stdout.write(
            self.style.WARNING(
                f"Movies keeping their current image: "
                f"{skipped_count}"
            )
        )

    def safe_filename(self, title):
        sanitized_title = re.sub(
            r'[<>:"/\\|?*]',
            " - ",
            title,
        )

        sanitized_title = re.sub(
            r"\s+",
            " ",
            sanitized_title,
        ).strip()

        sanitized_title = sanitized_title.replace(
            "'",
            "",
        )

        return f"m_{sanitized_title}.png"