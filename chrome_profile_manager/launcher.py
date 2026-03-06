from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .config import AppConfig


_BASE_PERFORMANCE_FLAGS = [
    "--disable-background-networking",
    "--disable-default-apps",
    "--disable-sync",
    "--disable-component-update",
    "--disable-features=Translate,OptimizationHints",
    "--metrics-recording-only",
    "--no-first-run",
    "--no-default-browser-check",
    "--disk-cache-size=104857600",
    "--media-cache-size=20971520",
]


@dataclass(slots=True)
class ManagedInstance:
    instance_id: int
    profile_dir: Path
    process: subprocess.Popen[str]


class ChromeLauncher:
    def __init__(self, config: AppConfig, logger: logging.Logger) -> None:
        self.config = config
        self.logger = logger

    def get_profile_dir(self, instance_id: int) -> Path:
        profile_dir = self.config.profiles_root / f"profile_{instance_id:02d}"
        profile_dir.mkdir(parents=True, exist_ok=True)
        return profile_dir

    def launch(self, instance_id: int, relaunch: bool = False) -> ManagedInstance:
        profile_dir = self.get_profile_dir(instance_id)
        command = self._build_command(profile_dir)
        process = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
        )

        action = "Relaunched" if relaunch else "Launched"
        self.logger.info(
            "%s instance %s (PID=%s, profile=%s)",
            action,
            instance_id,
            process.pid,
            profile_dir,
        )
        return ManagedInstance(instance_id=instance_id, profile_dir=profile_dir, process=process)

    def _build_command(self, profile_dir: Path) -> list[str]:
        args = [
            str(self.config.chrome_path),
            f"--user-data-dir={profile_dir}",
            f"--window-size={self.config.window_width},{self.config.window_height}",
            *_BASE_PERFORMANCE_FLAGS,
        ]

        if self.config.extension_folders:
            extension_arg = ",".join(str(path) for path in self.config.extension_folders)
            args.append(f"--load-extension={extension_arg}")

        if self.config.use_proxy and self.config.proxy_server:
            args.append(f"--proxy-server={self.config.proxy_server}")

        args.extend(self.config.extra_chrome_flags)
        args.append("about:blank")
        return args

