# System-health-monitor

## What the script does
the script should be run in the background, it shows you:
- current cpu usage
- current memory usage
- current disk usage
- systems uptime
- top 5 processes by cpu

it logs info into a the file "system_health.log"
any time the cpu, memory and/or disk usage goes over the configured threshold it sends
 a warning log into "system_health.log" and an alert message to "alerts.log"

you have a few arguments to use:  
`--cpu`        sets the cpu threshold  
`--memory`     sets the memory threshold  
`--disk`       sets the disk threshold  
`--interval`   sets the time between each status update  
`--once`       runs the scripts once  
`--config`     shows the threshold settings  

## Usage
```bash
python monitor.py --cpu 80 --memory 80 --disk 90 --interval 5
python monitor.py --once
```

## Installation
requirements.txt has the dependencies:
`pip install -r requirements.txt` 

## Project structure
```
system-health-monitor/
├── monitor.py
├── requirements.txt
├── README.md
├── config.json
└── logs/
    ├── system_health.log
    └── alerts.log
```
