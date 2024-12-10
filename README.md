# QuietCool Client

A Python client for controlling QuietCool Wireless RF Control Kit fans via Bluetooth Low Energy (BLE).

## Overview

This client allows you to interact with QuietCool whole house fans that use the Wireless RF Control Kit. It provides functionality to:

- Pair with fans
- Get fan information and status
- Control fan settings
- Monitor temperature and humidity
- Manage presets

## Installation

### From PyPI

You can install the package directly from PyPI using pip:

```bash
pip install quietcool
```

### From Source

1. Clone the repository:

   ```bash
   git clone https://github.com/emerose/quietcool.git
   cd quietcool
   ```

2. Install the package:
   ```bash
   pip install .
   ```

### Development Setup

1. Clone the repository as above
2. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install package in editable mode:
   ```bash
   pip install -e .
   ```

## Prerequisites

- Python 3.10 or higher
- A QuietCool fan with Wireless RF Control Kit
- Bluetooth Low Energy (BLE) support on your device
- [bleak](https://github.com/hbldh/bleak) - A GATT client software, used for Bluetooth Low Energy communication

## Getting Started

### 1. API ID Setup

The client requires an API ID to authenticate with the fan. You can provide it in several ways (checked in this order):

1. Command line argument: `--id YOUR_API_ID`
2. Environment variable: `QUIETCOOL=YOUR_API_ID`
3. Config files (first found is used):
   - `/etc/quietcool`
   - `~/.quietcool`
   - `./.quietcool`

### 2. Pairing

Before using the client, you need to pair it with your fan:

1. Put your fan in pairing mode (using another device or the controller's "Pair" button)
2. Run:

```bash
quietcool pair
```

### 3. Basic Usage

Get fan information:

```bash
quietcool info
```

Example output:

```json
{
  "faninfo": {
    "name": "sunroom fan",
    "model": "7",
    "serial_num": "RSE2008539"
  },
  "params": {
    "mode": "Idle",
    "fan_type": "THREE",
    "temp_high": 120,
    "temp_medium": 100,
    "temp_low": 80,
    "humidity_high": 90,
    "humidity_low": 255,
    "humidity_range": "LOW",
    "hour": 1,
    "minute": 0,
    "time_range": "MEDIUM"
  },
  "version": {
    "version": "IT-BLT-ATTICFAN_V2.6",
    "protect_temp": 182,
    "create_date": "2023.07.25",
    "create_mode": "online",
    "hw_version": "A"
  },
  "presets": [
    {
      "name": "Summer",
      "temp_high": 120,
      "temp_med": 100,
      "temp_low": 80,
      "humidity_off": 90,
      "humidity_on": 255,
      "humidity_speed": "LOW"
    },
    {
      "name": "Winter",
      "temp_high": 255,
      "temp_med": 255,
      "temp_low": 255,
      "humidity_off": 255,
      "humidity_on": 255,
      "humidity_speed": "LOW"
    }
  ],
  "workstate": {
    "mode": "Idle",
    "range": "CLOSE",
    "sensor_state": "OK",
    "temperature": 71.3,
    "humidity": 36
  }
}
```

## Command Line Options

usage:

```bash
quietcool [-h] [--id ID] [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [command]
```

Commands:

- `info`: Dumps detailed information about the connected fan
- `pair`: Pairs the client with a fan (fan must be in pairing mode)

Options:

- `--id ID`: API ID string
- `--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}`: Set logging level (default: WARNING)
- `-h, --help`: Show help message

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
