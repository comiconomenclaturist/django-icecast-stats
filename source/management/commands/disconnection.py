from django.core.management.base import BaseCommand
from source.models import Source
from listener.models import Stream


class Command(BaseCommand):
    help = "Log an Icecast mountpount disconnection to the database"

    def add_arguments(self, parser):
        parser.add_argument("mountpoint", nargs=1, type=str)

    def handle(self, *args, **options):
        mountpoint = options["mountpoint"][0]
        streams = Stream.objects.filter(mountpoint=mountpoint)

        if streams:
            stream = streams.get()

            source = Source.objects.create(stream=stream, connection=False)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully saved {mountpoint} disconnection at {source.timestamp}"
                )
            )
