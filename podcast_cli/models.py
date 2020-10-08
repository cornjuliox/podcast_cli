from peewee import (Model, SqliteDatabase, CharField, TimestampField)  # type: ignore


db = SqliteDatabase('datastore.db')


class PodcastModel(Model):
    title = CharField(unique=True)
    description = CharField(null=True)
    # Is there a URLfield somewhere?
    link = CharField(unique=True)
    guid = CharField(null=True)

    class Meta:
        database = db


class EpisodeModel(Model):
    title = CharField()
    description = CharField(null=True)
    # Is there a URLfield somewhere?
    link = CharField(unique=True)
    guid = CharField(unique=True)
    pubDate = TimestampField()

    class Meta:
        database = db
