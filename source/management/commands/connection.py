from django.core.management.base import BaseCommand
from psycopg2.extras import DateTimeTZRange
from datetime import datetime
from source.models import Disconnection
from listener.models import Stream


class Command(BaseCommand):
    help = "Log an Icecast mountpount connection to the database"

    def add_arguments(self, parser):
        parser.add_argument("mountpoint", nargs=1, type=str)

    def handle(self, *args, **options):
        mountpoint = options["mountpoint"][0]

        streams = Stream.objects.filter(mountpoint=mountpoint)

        if streams:
            stream = streams.get()

            disconnection = Disconnection.objects.filter(
                stream__mountpoint=mountpoint,
            ).first()

            disconnection.period = DateTimeTZRange(
                disconnection.period.lower, datetime.now().astimezone()
            )

            disconnection.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully saved {mountpoint} connection at {disconnection.period.upper}"
                )
            )
