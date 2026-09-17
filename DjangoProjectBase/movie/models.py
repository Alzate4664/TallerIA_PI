from django.db import models


class Movie(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='movie/images/')
    url = models.URLField(blank=True)

    genre = models.CharField(max_length=100, blank=True)
    year = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.title