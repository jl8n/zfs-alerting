from multiprocessing import pool
import subprocess
import re
import yaml
from pprint import pprint
from time import time
from gotify import Gotify

ALERT_FREQ = 6  # hours

# TODO move to gitsecret - not a big deal now since Gotify runs on a local IP
GOTIFY = Gotify(
    base_url='http://192.168.1.103:8070',
    app_token='A1.8rb02h3a4nJO',
)

output = subprocess.run(['zpool', 'status'], capture_output=True).stdout.decode('utf-8')


def parse_data(data):
    parts = re.split(r'(?:\n|^)\s*(\w*):\s*', data.strip(), re.MULTILINE)[1:]
    parsed = dict(zip(parts[::2], parts[1::2]))
    return parsed
    # return {**parsed, 'config': parse_config(parsed.get('config', ''))}


def parse_config(data):
    lines = [v.strip().split() for v in data.splitlines() if v.strip()]
    if lines:
        return [dict(zip(lines[0], v)) for v in lines[1:]]
    return []


def notify(title: str, msg: str, priority: int):
    print(msg, time())
    GOTIFY.create_message(
        msg,
        title=title,
        priority=priority,
    )


def main():
    zpool: dict = parse_data(output)
    pool: str = zpool['pool']
    status: str = zpool['status'].replace('\n', ' ').replace('  ', '')
    # status = [i for i in range(100) if i % 2 == 0]

    match zpool['state']:
        case 'DEGRADED':
            notify('Warning!', f'Pool {pool} is DEGRADED', 9)
        case 'FAULTED':
            notify('Warning!', f'Pool {pool} has FAULTED', 9)


if __name__ == '__main__':
    main()
