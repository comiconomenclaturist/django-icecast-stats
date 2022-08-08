import os
import re
import sys
import gzip
import traceback

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stats.settings")
import django

django.setup()

from django.utils import timezone
from django.db.models import Sum
from psycopg2.extras import DateTimeTZRange
from datetime import datetime, timedelta
from dateutil.parser import parse
from urllib.parse import unquote
from listener.models import Listener, Stream, IngestParameters
from useragent.utils import get_user_agent, get_location


def update_listeners(listener):
    prev = None

    for i, l in enumerate(listeners[:]):
        if (
            listener.ip_address == l.ip_address
            and listener.stream == l.stream
            and listener.user_agent == l.user_agent
        ):
            if prev:
                threshold = l.session.lower - timedelta(
                    seconds=params.session_threshold
                )
                if prev[1].session.upper > threshold:
                    listeners[prev[0]].session = DateTimeTZRange(
                        min(prev[1].session.lower, l.session.lower),
                        max(prev[1].session.upper, l.session.upper),
                    )
                    listeners[prev[0]].duration = min(
                        prev[1].duration + l.duration,
                        listeners[prev[0]].session.upper
                        - listeners[prev[0]].session.lower,
                    )
                    del listeners[i]
                    return True
            prev = (i, l)
    return False


def update_db_listeners(listeners):
    for l in listeners:
        existing_listeners = Listener.objects.filter(
            ip_address=l.ip_address,
            stream=l.stream,
            user_agent=l.user_agent,
            session__overlap=DateTimeTZRange(
                l.session.lower - timedelta(seconds=params.session_threshold),
                l.session.upper,
            ),
        )

        if existing_listeners:
            connected_at = min(
                [el.session.lower for el in existing_listeners] + [l.session.lower]
            )
            disconnected_at = max(
                [el.session.upper for el in existing_listeners] + [l.session.upper]
            )
            duration = min(
                existing_listeners.aggregate(sum=Sum("duration"))["sum"] + l.duration,
                disconnected_at - connected_at,
            )

            for i, el in enumerate(existing_listeners):
                if i == 0:
                    el.session = DateTimeTZRange(connected_at, disconnected_at)
                    el.duration = duration
                    el.save()
                else:
                    el.delete()
            listeners.remove(l)
            return True

    return False


# These first 5 fields should be consistent
ip_addr = "^(?P<ip_addr>[(\d\.)]+)"
date = " - - \[(?P<date>\d{1,2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2} \+\d{4})\]"
request = ' "(?P<request>\w+)'
url = " (?P<url>\\/.*?) "
bytes_sent = '.*?" \d+ (?P<bytes>\d+) '

regex = re.compile((ip_addr + date + request + url + bytes_sent))
streams = Stream.objects.all()
params = IngestParameters.objects.all().first()

try:
    for root, dirs, files in sorted(os.walk("./icecast-logs/2020")):
        listeners = []
        files.sort()

        for f in files:
            if f.startswith("access.log"):
                filepath = os.path.join(root, f)

                with gzip.open(filepath, "rt", encoding="ISO-8859-1") as log_file:
                    for line in log_file:
                        try:
                            match = re.match(regex, line)

                            if match:
                                m = match.groupdict()

                                # The rest of the log file line can be truncated at 1024 characters if there is a long referer/user agent string.
                                # User Agent strings can also contain double quotes (eg in 4" screen)
                                # Let's first split by double-quote, space, double-quote. Referer should be the first list item.
                                # Then we split by trailing digits (duration), if present.
                                remaining = re.split('" "', line[match.end() :])
                                referer = remaining[0].strip('"')
                                if len(remaining) > 1:
                                    user_agent = re.split('" \d+$', remaining[1])[0]
                                    duration = re.findall(".* (\d+)$", remaining[1])
                                else:
                                    user_agent = ""
                                    duration = None

                                if (
                                    m["ip_addr"] != "127.0.0.1"
                                    and m["request"] == "GET"
                                    and m["url"]
                                    in streams.values_list("mountpoint", flat=True)
                                ):

                                    stream = streams.get(mountpoint=m["url"])

                                    # If we didn't parse a duration from the original string, calculate it from the bytes sent.
                                    # Note that this is not backwards compatible with the previous bitrates (128kbps) - when did this change?
                                    if duration:
                                        duration = int(duration[0])
                                    else:
                                        duration = int(
                                            int(m["bytes"]) / (stream.bitrate * 128)
                                        )

                                    if duration >= params.minimum_duration:
                                        duration = timedelta(seconds=duration)
                                        disconnected_at = parse(
                                            m["date"].replace(":", " ", 1)
                                        ).astimezone()
                                        connected_at = disconnected_at - duration
                                        session = DateTimeTZRange(
                                            connected_at, disconnected_at
                                        )
                                        user_agent = get_user_agent(unquote(user_agent))
                                        location = get_location(m["ip_addr"])

                                        listener = Listener(
                                            ip_address=m["ip_addr"],
                                            stream=stream,
                                            referer=unquote(referer.replace("-", ""))[
                                                :255
                                            ],
                                            session=session,
                                            duration=duration,
                                            user_agent=user_agent,
                                            country=location["country_code"],
                                            city=location["city"],
                                            latitude=location["latitude"],
                                            longitude=location["longitude"],
                                        )

                                        listeners.append(listener)

                                        while update_listeners(listener):
                                            update_listeners(listener)

                            if not match:
                                print("Not imported: %s" % line)
                        except Exception as e:
                            print(traceback.format_exc())
                            print("Exception in file: %s, line: %s" % (f, line))
                            sys.exit(1)

        while update_db_listeners(listeners):
            update_db_listeners(listeners)

        try:
            Listener.objects.bulk_create(listeners)
        except Exception as e:
            print(traceback.format_exc())
            print("Exception with this day/directory %s" % (root))
            for l in listeners:
                print(
                    "Listener: %s "
                    % ", ".join(
                        (
                            l.ip_address,
                            l.session.lower.strftime("%Y/%m/%d %H:%M:%S"),
                            l.session.upper.strftime("%Y/%m/%d %H:%M:%S"),
                            str(l.duration.total_seconds()),
                            l.referer,
                            l.user_agent.__str__(),
                        )
                    )
                )
            sys.exit(1)

except Exception:
    from pprint import pprint

    print(traceback.format_exc())
    print(pprint(locals()))
