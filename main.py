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
    print(msg)

    with open('last_alert.yaml') as f:
        last_alert = yaml.load(f, Loader=yaml.FullLoader)

    if abs(last_alert['time'] - time()) >= 60 * 60 * ALERT_FREQ:
        # last message was at least 6 hours ago
        GOTIFY.create_message(
            msg,
            title=title,
            priority=priority,
        )

        # only update last_alert.yaml if alert was sent
        last_alert['title'] = title
        last_alert['message'] = msg
        last_alert['priority'] = priority
        last_alert['time'] = time()  # update last time

    with open('last_alert.yaml', 'w') as file:
        yaml.dump(last_alert, file)


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
