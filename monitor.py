#!/usr/bin/env python3

import psutil, time, logging, json, argparse
from pathlib import Path
from logging.handlers import RotatingFileHandler

log_dir = Path("~/testing/system-health-monitor/logs").expanduser()

formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt="%Y-%m-%d %H:%M:%S")

# Main health log - rotates at 5MB, keeps 3 backups
health_handler = RotatingFileHandler(
    log_dir / "system_health.log",
    maxBytes=5 * 1024 * 1024,  # 5 MB
    backupCount=3
)
health_handler.setFormatter(formatter)

alert_formatter = logging.Formatter('%(asctime)s [ALERT] %(message)s', datefmt="%Y-%m-%d %H:%M:%S")

# alert log - rotates at 5MB, keeps 3 backups
alert_handler = RotatingFileHandler(
    log_dir / "alerts.log",
    maxBytes=5 * 1024 * 1024, #5 MB
    backupCount=3
)
alert_handler.setFormatter(alert_formatter)

# Main logger
logger = logging.getLogger("system_health")
logger.setLevel(logging.INFO)
logger.addHandler(health_handler)

# alerts logger
alert_logger = logging.getLogger("alerts.log")
alert_logger.setLevel(logging.WARNING)
alert_logger.addHandler(alert_handler)
alert_logger.propagate = False

config_file = Path("config.json")

parser = argparse.ArgumentParser()
parser.add_argument("--cpu", type=int)
parser.add_argument("--memory", type=int)
parser.add_argument("--disk", type=int)
parser.add_argument("--interval", type=int, default=5)
parser.add_argument("--once", action="store_true")
parser.add_argument("--config", action="store_true")
args = parser.parse_args()


# Load config if it exists
if config_file.exists() and config_file.stat().st_size > 0:
    with open(config_file) as f:
        config = json.load(f)

else:
    config = {"cpu": 80, "memory": 80, "disk": 80, "interval": 5}

if args.cpu:
    config["cpu"] = args.cpu
if args.memory:
    config["memory"] = args.memory
if args.disk:
    config["disk"] = args.disk
if args.interval:
    config["interval"] = args.interval

with open(config_file, "w") as f:
    json.dump(config, f)


def run_check():

    disk_usage_percent = psutil.disk_usage("/").percent
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage_percent = psutil.virtual_memory().percent
    system_uptime = time.time() - psutil.boot_time()
    readable_uptime = time.strftime("%dd %Hh %Mm ", time.gmtime(system_uptime))

    # Initialize CPU usage measurement
    for proc in psutil.process_iter():
        try:
            proc.cpu_percent(interval=None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    time.sleep(1) # Wait to allow CPU usage calculation

    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    top_processes = sorted(processes, key=lambda p: p['cpu_percent'], reverse=True)[:5]

    print(f"disk usage: {disk_usage_percent}%")
    print(f"cpu usage: {cpu_usage}%")
    print(f"memory usage: {memory_usage_percent}%")
    print(f"system uptime: {readable_uptime}")
    print("Top 5 CPU-consuming processes:")
    for p in top_processes:
        print(f"PID: {p['pid']:<6} Name: {p['name']:<20} CPU: {p['cpu_percent']:>5}")

    logger.info(f"CPU: {cpu_usage}% | MEM: {memory_usage_percent}% | DISK: {disk_usage_percent}% | UPTIME: {readable_uptime}")

    if cpu_usage > config["cpu"]:
        logger.warning(f"CPU threshold exceeded: {config['cpu']}")
        alert_logger.warning(f"CPU usage is over {config['cpu']}%")

    if memory_usage_percent > config["memory"]:
        logger.warning(f"MEMORY threshold exceeded: {config['memory']}")
        alert_logger.warning(f"Memory usage is over {config['memory']}%")

    if disk_usage_percent > config["disk"]:
        logger.warning(f"DISK threshold exceeded: {config['disk']}")
        alert_logger.warning(f"Disk usage is over {config['disk']}%")


if args.once:
    run_check()
elif args.config:
    print(f"cpu threshold: {config['cpu']}")
    print(f"memory threshold: {config['memory']}")
    print(f"disk threshold: {config['disk']}")
    print(f"interval time: {config['interval']} minutes")
else:
    while(True):
        run_check()
        time.sleep(args.interval * 60)

