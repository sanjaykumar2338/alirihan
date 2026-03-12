# Chrome Profile Manager (Windows)

Config-driven Python tool to launch and monitor multiple Chrome windows with dedicated user-data directories.

## Features

- Detects existing profile folders in `profiles_root`
- Creates missing profile folders when less than `instances`
- Supports two profile strategies:
  - `cycle_existing_profiles=true`: manage all detected profiles
  - `cycle_existing_profiles=false`: manage first `instances` profiles
- Loads one or more unpacked Chrome extensions from folder paths
- Validates extension folders (`manifest.json` must exist)
- Optional proxy support with normalized `--proxy-server`
- Watchdog relaunches closed browsers using the same profile mapping
- Optional cache cleanup at startup
- File + console logging

## File Layout

- `main.py` - app entry point
- `chrome_profile_manager/config.py` - config parsing and validation
- `chrome_profile_manager/launcher.py` - profile discovery and Chrome command launch
- `chrome_profile_manager/monitor.py` - watchdog and relaunch loop
- `chrome_profile_manager/cache_cleaner.py` - startup cache cleanup helper
- `chrome_profile_manager/logger_setup.py` - logger initialization
- `config.example.json` - example configuration

## Requirements

- Windows 10/11
- Python 3.10 or newer
- Google Chrome installed

## Setup

1. Copy `config.example.json` to `config.json`.
2. Update `chrome_path` with your Chrome executable path.
3. Choose `profiles_root` where profile folders should be stored.
4. Add optional extension folders and proxy settings.
5. Run the app.

## Config Example

```json
{
  "chrome_path": "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "instances": 3,
  "profiles_root": "./profiles",
  "profile_mode": "auto_detect",
  "cycle_existing_profiles": true,
  "extension_folders": [],
  "use_proxy": false,
  "proxy_server": "",
  "window_width": 1280,
  "window_height": 800,
  "cleanup_cache_on_start": true,
  "relaunch_delay_seconds": 2,
  "check_interval_seconds": 2,
  "extra_chrome_flags": [
    "--disable-notifications",
    "--mute-audio"
  ],
  "log_file": "./logs/chrome_profile_manager.log"
}
```

## Profile Detection Behavior

- `profile_mode` is currently `auto_detect`.
- On startup, the tool scans subfolders inside `profiles_root`.
- If existing profiles are fewer than `instances`, it creates additional folders like `profile_01`, `profile_02`, etc.
- If more profiles exist than `instances`:
  - `cycle_existing_profiles=true`: all existing profiles are managed
  - `cycle_existing_profiles=false`: only the first `instances` profiles are managed
- If a managed browser closes, watchdog relaunches the same profile folder.

## Extension Folders

- `extension_folders` accepts one or more folder paths.
- Each folder must exist and contain `manifest.json`.
- Invalid extension folders are logged and skipped.
- Chrome is launched with:
  - `--load-extension=path1,path2,path3`
- Only unpacked extension folders are supported.
- `.crx` files are not supported by this tool.

## Proxy

- Proxy is disabled by default (`use_proxy=false`).
- Enable with `use_proxy=true` and set `proxy_server`.
- Supported formats include:
  - `127.0.0.1:8080`
  - `socks5://127.0.0.1:9050`
  - `http://127.0.0.1:8080`
- Invalid or empty proxy values cause config validation errors when proxy is enabled.

## Run

```bash
python main.py --config config.json
```

Stop with `Ctrl + C`.

## Notes / Limitations

- Windows-only tool.
- This project focuses on profile management, extension loading, proxy arguments, and watchdog relaunch behavior.
- It does not provide anti-detect, fingerprint spoofing, or fingerprint bypass guarantees.
