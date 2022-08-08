import os, re, sys, traceback

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stats.settings")
import django

django.setup()
from django.contrib.auth.models import User
from stats.settings import *

import requests
import xml.etree.ElementTree as ET

from listener.models import Stream, IngestParameters

params = IngestParameters.objects.get_or_create()

url = "http://%s:%s/admin/listmounts" % (ICECAST_AUTH["host"], ICECAST_AUTH["port"])
r = requests.get(url, auth=(ICECAST_AUTH["username"], ICECAST_AUTH["password"]))

tree = ET.fromstring(r.text)
sources = [elem.attrib.get("mount") for elem in tree.findall(".//source")]

for source in sources:

    if "lo" in source:
        bitrate = 48
    else:
        bitrate = 192

    stream = Stream.objects.get_or_create(mountpoint=source, bitrate=bitrate)

if not User.objects.filter(username=SUPERUSER["name"]):
    user = User.objects.create_user(SUPERUSER["name"], password=SUPERUSER["pass"])
    user.is_superuser = True
    user.is_staff = True
    user.save()
