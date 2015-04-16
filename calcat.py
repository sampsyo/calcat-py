#!/usr/bin/env python3

import requests
from urllib.parse import urlparse, urlunparse
import sys
import icalendar
import click
import itertools


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


def events_in(cal):
    """Generate a sequence of `Event`s in a `Calendar`."""
    for component in cal.subcomponents:
        if isinstance(component, icalendar.cal.Event):
            yield component


def make_calendar(events):
    """Create a `Calendar` containing the sequence of `Event`s."""
    cal = icalendar.Calendar()
    for event in events:
        cal.add_component(event)
    return cal


@click.command()
@click.argument('calendars', nargs=-1)
def calcat(calendars):
    cals = (parse_calendar(read(path)) for path in calendars)
    events = itertools.chain.from_iterable(events_in(cal) for cal in cals)
    merged = make_calendar(events)
    sys.stdout.buffer.write(merged.to_ical())


if __name__ == '__main__':
    calcat()
