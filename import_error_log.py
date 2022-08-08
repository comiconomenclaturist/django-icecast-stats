import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stats.settings")
import django

django.setup()

filepath = sys.argv[1]
filename = os.path.basename(filepath)

if filename.startswith("error.log"):
    pass
