from __future__ import annotations

import logging
import time
from typing import Iterable

from .launcher import ChromeLauncher, ManagedInstance


class ProcessMonitor:
    def __init__(
        self,
        launcher: ChromeLauncher,
        logger: logging.Logger,
        relaunch_delay_seconds: float,
        check_interval_seconds: float,
    ) -> None:
        self.launcher = launcher
        self.logger = logger
        self.relaunch_delay_seconds = relaunch_delay_seconds
        self.check_interval_seconds = check_interval_seconds
        self.instances: dict[int, ManagedInstance | None] = {}
        self._next_relaunch_ts: dict[int, float] = {}
        self._should_stop = False

    def start(self, instance_ids: Iterable[int]) -> None:
        for instance_id in instance_ids:
            self.instances[instance_id] = None
            self._next_relaunch_ts[instance_id] = 0.0
            self._launch_instance(instance_id, relaunch=False)

    def run_forever(self) -> None:
        self.logger.info(
            "Watchdog started (check every %.2fs, relaunch delay %.2fs)",
            self.check_interval_seconds,
            self.relaunch_delay_seconds,
        )
        try:
            while not self._should_stop:
                self._check_instances()
                time.sleep(self.check_interval_seconds)
        except KeyboardInterrupt:
            self.logger.info("Shutdown signal received. Stopping managed instances.")
            self.stop_all()
        finally:
            self.logger.info("Watchdog stopped.")

    def stop_all(self) -> None:
        self._should_stop = True
        for managed in self.instances.values():
            if managed is None:
                continue
            if managed.process.poll() is None:
                managed.process.terminate()
        for managed in self.instances.values():
            if managed is None:
                continue
            if managed.process.poll() is None:
                try:
                    managed.process.wait(timeout=5)
                except Exception:  # noqa: BLE001
                    managed.process.kill()

    def _check_instances(self) -> None:
        now = time.time()
        for instance_id, managed in list(self.instances.items()):
            if managed is None:
                if now >= self._next_relaunch_ts.get(instance_id, 0.0):
                    self._launch_instance(instance_id, relaunch=True)
                continue

            code = managed.process.poll()
            if code is None:
                continue

            self.logger.warning(
                "Instance %s exited with code %s. Relaunching after %.2fs.",
                instance_id,
                code,
                self.relaunch_delay_seconds,
            )
            self.instances[instance_id] = None
            self._next_relaunch_ts[instance_id] = now + self.relaunch_delay_seconds

    def _launch_instance(self, instance_id: int, relaunch: bool) -> None:
        try:
            self.instances[instance_id] = self.launcher.launch(instance_id, relaunch=relaunch)
            self._next_relaunch_ts[instance_id] = 0.0
        except Exception as exc:  # noqa: BLE001
            self.instances[instance_id] = None
            self._next_relaunch_ts[instance_id] = time.time() + self.relaunch_delay_seconds
            self.logger.error(
                "Failed to launch instance %s (%s). Next retry in %.2fs.",
                instance_id,
                exc,
                self.relaunch_delay_seconds,
            )
