from django.contrib.gis.geoip2 import GeoIP2
from django.core.exceptions import ObjectDoesNotExist
from geoip2.errors import AddressNotFoundError
from user_agents import parse
from .models import Device, OS, Browser, UserAgent


def get_user_agent(string, user_agent=None, device=None, os=None, browser=None):

    if string != "-":
        string = string[:255]

        try:
            user_agent = UserAgent.objects.get(string=string)

        except ObjectDoesNotExist:
            ua = parse(string)

            if ua.device.family != "Other":
                device = Device.objects.get_or_create(
                    family=ua.device.family,
                    brand=ua.device.brand,
                    model=ua.device.model,
                )[0]
            if ua.os.family != "Other":
                os = OS.objects.get_or_create(
                    family=ua.os.family, version=ua.os.version_string
                )[0]
            if ua.browser.family != "Other":
                browser = Browser.objects.get_or_create(
                    family=ua.browser.family, version=ua.browser.version_string
                )[0]

            user_agent = UserAgent.objects.get_or_create(
                device=device,
                os=os,
                browser=browser,
                string=string,
                is_mobile=ua.is_mobile,
                is_tablet=ua.is_tablet,
                is_bot=ua.is_bot,
            )[0]

    return user_agent


def get_location(ip_address):
    try:
        location = GeoIP2().city(ip_address)
    except AddressNotFoundError:
        location = {
            "country_code": None,
            "city": None,
            "latitude": None,
            "longitude": None,
        }

    return location
