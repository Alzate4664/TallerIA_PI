import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from movie.models import Movie


class Command(BaseCommand):
    help = "Update movie descriptions in the database from a CSV file"

    def handle(self, *args, **kwargs):
        csv_file = settings.BASE_DIR / "updated_movie_descriptions.csv"

        if not csv_file.exists():
            self.stderr.write(
                self.style.ERROR(f"CSV file not found: {csv_file}")
            )
            return

        updated_count = 0
        not_found_count = 0

        with csv_file.open(
            mode="r",
            encoding="utf-8-sig",
            newline="",
        ) as file:
            reader = csv.DictReader(file)
            rows = list(reader)

        self.stdout.write(f"Found {len(rows)} movies in CSV")

        for row in rows:
            title = row["Title"].strip()
            new_description = row["Updated Description"].strip()

            self.stdout.write(f"Processing: {title}")

            try:
                movie = Movie.objects.get(title=title)

                movie.description = new_description
                movie.save(update_fields=["description"])

                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Updated: {title}")
                )

            except Movie.DoesNotExist:
                not_found_count += 1
                self.stderr.write(
                    self.style.WARNING(f"Movie not found: {title}")
                )

            except Movie.MultipleObjectsReturned:
                self.stderr.write(
                    self.style.ERROR(
                        f"Multiple movies found with title: {title}"
                    )
                )

            except Exception as error:
                self.stderr.write(
                    self.style.ERROR(
                        f"Failed to update {title}: {error}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Finished updating {updated_count} movies from CSV."
            )
        )

        if not_found_count:
            self.stdout.write(
                self.style.WARNING(
                    f"Movies not found: {not_found_count}"
                )
            )