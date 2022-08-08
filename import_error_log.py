import os
import re
import sys
import gzip

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stats.settings")
import django

django.setup()

from dateutil.parser import parse
from source.models import Source
from listener.models import Stream
from psycopg2.extras import DateTimeTZRange


d = "^\[(?P<date>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\]"
e = "(?P<event>source/source_shutdown|connection/_handle_source_request)"
m = '"(?P<mountpoint>/.+)"'
regex = re.compile((d + " INFO " + e + ".+ at (mountpoint )?" + m))

filepath = sys.argv[1]
filename = os.path.basename(filepath)

if filename.startswith("error.log"):
    with gzip.open(filepath, "rt", encoding="ISO-8859-1") as log_file:
        for line in log_file:
            match = re.match(regex, line)

            if match:
                m = match.groupdict()
                date = parse(m.get("date"))
                event = m.get("event")
                mountpoint = m.get("mountpoint")

                stream = Stream.objects.get(mountpoint=mountpoint)

                if event == "connection/_handle_source_request":
                    source = Source.objects.create(
                        stream=stream,
                        disconnection=DateTimeTZRange(date.astimezone()),
                    )
                if event == "source/source_shutdown":
                    source = Source.objects.filter(stream__mountpoint=mountpoint).last()
                    if source:
                        pass
