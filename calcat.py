#!/usr/bin/env python3

import requests
from urllib.parse import urlparse, urlunparse
import sys
import icalendar
import click
import itertools
import arrow


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


def opaquify(event, whitelist=('DTSTART', 'DTEND', 'UID')):
    """Get a version of the event with all the identifying information
    removed (i.e., just show that you're busy then).
    """
    e = icalendar.cal.Event()
    for key in whitelist:
        e[key] = event[key]
    return e


def describe_events(events):
    """Summarize a list of events in English, generating lines for
    output.
    """
    for event in events:
        # Ignore it if we don't have a start and end time.
        if 'DTSTART' in event and 'DTEND' in event:
            start = arrow.get(event.decoded('DTSTART'))
            end = arrow.get(event.decoded('DTEND'))
            line = '* {} to {}'.format(start.humanize(), end.humanize())
            if 'SUMMARY' in event:
                title = str(event['SUMMARY'])
                line += ': {}'.format(title)
            yield line


@click.command()
@click.argument('calendars', nargs=-1)
@click.option('--opaque', '-o', is_flag=True)
@click.option('--describe', '-d', is_flag=True)
def calcat(calendars, opaque, describe):
    cals = (parse_calendar(read(path)) for path in calendars)
    events = itertools.chain.from_iterable(events_in(cal) for cal in cals)
    if opaque:
        events = map(opaquify, events)
    if describe:
        for line in describe_events(events):
            click.echo(line)
    else:
        merged = make_calendar(events)
        click.echo(merged.to_ical(), nl=False)


if __name__ == '__main__':
    calcat()
