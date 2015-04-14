#!/usr/bin/env python3

import requests
from urllib.parse import urlparse, urlunparse
import sys
import icalendar


def is_url(s):
    return bool(urlparse(s).scheme)


def read(path_or_url):
    url_parts = urlparse(path_or_url)
    if url_parts.scheme:
        # This is a URL. Replace "webcal" with http.
        if url_parts.scheme == 'webcal':
            parts = list(url_parts)
            parts[0] = 'http'
            path_or_url = urlunparse(parts)
        return requests.get(path_or_url).text
    else:
        with open(path_or_url) as f:
            return f.read()


def parse_calendar(text):
    return icalendar.Calendar.from_ical(text)


def merge(cals):
    merged = icalendar.Calendar()
    for cal in cals:
        for component in cal.subcomponents:
            if component.name == 'VEVENT':
                merged.add_component(component)
    return merged


if __name__ == '__main__':
    cal = merge(parse_calendar(read(arg)) for arg in sys.argv[1:])
    sys.stdout.buffer.write(cal.to_ical())
