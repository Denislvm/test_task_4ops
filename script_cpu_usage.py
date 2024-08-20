#!/usr/bin/env python3

import psutil
import datetime

cpu_usage = psutil.cpu_percent(interval=1)
ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

with open('/var/log/cpu_usage.log', 'a') as log:
    log.write(f'{ts} - CPU Usage: {cpu_usage}%\n')
