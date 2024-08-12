from django.db import models


class Artist(models.Model):
    name = models.CharField(max_length=100)
    img_url = models.CharField(max_length=200)


class Album(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.RESTRICT)
    title = models.CharField(max_length=100)
    img_url = models.CharField(max_length=200)
    pub_date = models.DateField()


class Song(models.Model):
    title = models.CharField(max_length=100)
    album = models.ForeignKey(Album, on_delete=models.RESTRICT)
