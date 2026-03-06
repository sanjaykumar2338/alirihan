# Chrome Profile Manager (Windows)

Config-driven Python tool to launch, monitor, and auto-restart multiple Chrome instances with separate profile folders.

## Features

- Config-based instance count (`instances`)
- Separate `--user-data-dir` per managed instance
- Auto-load one or more unpacked extension folders
- Optional proxy support (`use_proxy` + `proxy_server`)
- Watchdog loop with auto-relaunch for closed instances
- Basic startup cache cleanup for managed profiles
- Basic launch logging and error reporting

## File Layout

- `main.py` - entry point
- `chrome_profile_manager/config.py` - config loading and validation
- `chrome_profile_manager/launcher.py` - Chrome command construction and process launch
- `chrome_profile_manager/monitor.py` - watchdog/relaunch logic
- `chrome_profile_manager/cache_cleaner.py` - cache cleanup helper
- `chrome_profile_manager/logger_setup.py` - logger setup
- `config.example.json` - sample config

## Requirements

- Windows
- Python 3.10+
- Installed Google Chrome

## Setup

1. Copy `config.example.json` to `config.json`.
2. Update `chrome_path`, `profiles_root`, and `extension_folders`.
3. Adjust instance count and optional settings as needed.

## Run

```bash
python main.py --config config.json
```

## Notes

- This tool is focused on profile/process management and reliability.
- It does not implement or guarantee anti-detection/fingerprint bypass behavior.
- Stop the manager with `Ctrl + C`.

