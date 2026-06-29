#!/usr/bin/env python3
"""
Sanitise captured NATS events for use as test fixtures.

Replaces real values with deterministic fakes so the file is safe to commit:
  - IPv4 addresses (172.x, 10.x)        -> 10.0.0.1
  - Fly IPv6 fdaa: addresses            -> fdaa:0:0:0:0:0:0:1
  - long hex instance IDs               -> inst-000, inst-001, ...
  - short hex host IDs                  -> host-000, host-001, ...
  - short hex zone IDs                  -> zone-000, zone-001, ...
  - emnify endpoint numeric IDs in URLs -> 00001, 00002, ...
  - cdn.emnify.net                      -> cdn.example.com
  - app names and log message text      -> kept (shape matters for tests)
"""
import json
import re
from pathlib import Path

src = Path(__file__).parent.parent / 'out' / 'captured-mgf.jsonl'
dst = Path(__file__).parent / 'captured-mgf.jsonl'

counters = {'host': 0, 'instance': 0, 'zone': 0, 'endpoint': 0}
maps = {k: {} for k in counters}


def fake(field, value):
    if value not in maps[field]:
        maps[field][value] = f'{field}-{counters[field]:03d}'
        counters[field] += 1
    return maps[field][value]


def sanitise_message_text(text):
    # IPv4 private ranges
    text = re.sub(r'\b172\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '10.0.0.1', text)
    # Fly IPv6 fdaa: addresses
    text = re.sub(r'fdaa:[a-f0-9:]+', 'fdaa:0:0:0:0:0:0:1', text)
    # emnify endpoint numeric IDs
    text = re.sub(r'endpoint/(\d+)/', lambda m: f'endpoint/{fake("endpoint", m.group(1))}/', text)
    text = re.sub(r'endpoint/(\d+)\?', lambda m: f'endpoint/{fake("endpoint", m.group(1))}?', text)
    # emnify domain
    text = text.replace('cdn.emnify.net', 'cdn.example.com')
    return text


def sanitise_event(event):
    try:
        inner = json.loads(event['message'])
    except (json.JSONDecodeError, KeyError, TypeError):
        return event

    # structured fields
    if 'fly' in inner and isinstance(inner['fly'], dict):
        fly = inner['fly']
        if 'app' in fly and 'instance' in fly['app']:
            fly['app']['instance'] = fake('instance', fly['app']['instance'])
        if 'zone' in fly:
            fly['zone'] = fake('zone', fly['zone'])
        # .region and .app.name kept (region is just 'lhr', app names are the test signal)

    if 'host' in inner:
        inner['host'] = fake('host', inner['host'])

    # app-specific message text
    if 'message' in inner and isinstance(inner['message'], str):
        inner['message'] = sanitise_message_text(inner['message'])

    event['message'] = json.dumps(inner, separators=(',', ':'))
    return event


def main():
    real_events = []      # production app logs
    self_log_events = []  # log shipper's own logs (used for the `abort` test)
    with src.open() as fin:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            event = json.loads(line)
            try:
                inner = json.loads(event['message'])
                app = inner.get('fly', {}).get('app', {}).get('name', '')
            except (json.JSONDecodeError, KeyError, TypeError):
                app = ''
            if app.startswith('fly-log-shipper'):
                self_log_events.append(event)
            else:
                real_events.append(event)

    with dst.open('w') as fout:
        for event in real_events:
            event = sanitise_event(event)
            fout.write(json.dumps(event, separators=(',', ':')) + '\n')
        # keep exactly one self-log (for the abort test)
        if self_log_events:
            event = sanitise_event(self_log_events[0])
            fout.write(json.dumps(event, separators=(',', ':')) + '\n')

    print(f'wrote {dst}')
    print(f'  {dst.stat().st_size} bytes')
    print(f'  {len(real_events)} real events + 1 self-log = {len(real_events) + 1} total')
    for k, v in counters.items():
        print(f'  {v:3d} unique {k}s faked')


if __name__ == '__main__':
    main()
