import uuid

from django.db import models


class Artist(models.Model):
    mdbId = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    img_url = models.CharField(max_length=200)

    def __str__(self):
        return "{id} [{mdbId}] {name}".format(id=self.id, mdbId=self.mdbId, name=self.name)


class Album(models.Model):
    mdbId = models.UUIDField(default=uuid.uuid4, editable=False)
    artist = models.ForeignKey(Artist, on_delete=models.RESTRICT)
    title = models.CharField(max_length=100)
    img_url = models.CharField(max_length=200)
    pub_date = models.DateField()

    def __str__(self):
        return "{id} [{mdbId}] {title}".format(id=self.id, mdbId=self.mdbId, title=self.title)


class Song(models.Model):
    mdbId = models.UUIDField(default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    album = models.ForeignKey(Album, on_delete=models.RESTRICT)

    def __str__(self):
        return "{id} [{mdbId}] {title}".format(id=self.id, mdbId=self.mdbId, title=self.title)
