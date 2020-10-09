from peewee import Model                # type: ignore
from peewee import SqliteDatabase       # type: ignore
from peewee import CharField            # type: ignore
from peewee import TimestampField       # type: ignore
from peewee import ForeignKeyField      # type: ignore
# ^^This is the only way to do it while
# respecting flake8's limits on line length.


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
    podcast = ForeignKeyField(PodcastModel)

    class Meta:
        database = db
