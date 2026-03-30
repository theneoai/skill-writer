"""Resource management for skill evolution."""

from __future__ import annotations

import gzip
import re
import shutil
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


DEFAULT_MAX_SNAPSHOTS = 10
DEFAULT_MAX_USAGE_DAYS = 30
DEFAULT_MAX_LOG_DAYS = 14


class ResourceManager:
    def __init__(
        self,
        snapshot_dir: Path | None = None,
        usage_dir: Path | None = None,
        log_dir: Path | None = None,
        max_snapshots: int = DEFAULT_MAX_SNAPSHOTS,
        max_usage_days: int = DEFAULT_MAX_USAGE_DAYS,
        max_log_days: int = DEFAULT_MAX_LOG_DAYS,
    ) -> None:
        self.snapshot_dir = snapshot_dir or Path.home() / ".skill" / "snapshots"
        self.usage_dir = usage_dir or Path.home() / ".skill" / "evolution" / "usage"
        self.log_dir = log_dir or Path.home() / ".skill" / "logs"
        self.max_snapshots = max_snapshots
        self.max_usage_days = max_usage_days
        self.max_log_days = max_log_days

    def cleanup_snapshots(
        self,
        skill_name: str | None = None,
        max: int | None = None,
    ) -> dict[str, int]:
        max_keep = max or self.max_snapshots
        snapshot_dir = self.snapshot_dir
        if skill_name:
            snapshot_dir = snapshot_dir / skill_name

        if not snapshot_dir.exists():
            return {"removed": 0, "remaining": 0}

        snapshots = sorted(
            snapshot_dir.glob("*.tar.gz"),
            key=lambda p: p.stat().st_mtime,
        )

        if len(snapshots) <= max_keep:
            return {"removed": 0, "remaining": len(snapshots)}

        to_remove = snapshots[: len(snapshots) - max_keep]
        for snapshot in to_remove:
            snapshot.unlink()

        remaining = len(list(snapshot_dir.glob("*.tar.gz")))
        return {"removed": len(to_remove), "remaining": remaining}

    def cleanup_usage_files(
        self,
        max_days: int | None = None,
        skill_name: str | None = None,
    ) -> dict[str, int]:
        max_d = max_days or self.max_usage_days
        usage_dir = self.usage_dir
        if skill_name:
            usage_dir = usage_dir / f"usage_{skill_name}"

        if not usage_dir.exists():
            return {"removed": 0}

        cutoff = datetime.now() - timedelta(days=max_d)
        cutoff_str = cutoff.strftime("%Y%m%d")

        removed = 0
        for file in usage_dir.glob("*.jsonl"):
            match = re.search(r"(\d{8})", file.name)
            if match:
                file_date = match.group(1)
                if file_date < cutoff_str:
                    file.unlink()
                    removed += 1

        return {"removed": removed}

    def cleanup_logs(
        self,
        max_days: int | None = None,
        log_dir: Path | None = None,
    ) -> dict[str, int]:
        max_d = max_days or self.max_log_days
        target_dir = log_dir or self.log_dir

        if not target_dir.exists():
            return {"cleaned": 0, "compressed": 0}

        cutoff = datetime.now() - timedelta(days=max_d)
        cutoff_str = cutoff.strftime("%Y%m%d")

        cleaned = 0
        compressed = 0

        for log_file in target_dir.glob("*.log"):
            match = re.search(r"(\d{8})", log_file.name)
            if not match:
                continue
            file_date = match.group(1)

            if file_date < cutoff_str:
                gz_path = Path(str(log_file) + ".gz")
                if not gz_path.exists():
                    with open(log_file, "rb") as f_in:
                        with gzip.open(gz_path, "wb") as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    compressed += 1
                    log_file.unlink()
                else:
                    log_file.unlink()
                cleaned += 1

        for gz_file in target_dir.glob("*.log.gz"):
            mtime = datetime.fromtimestamp(gz_file.stat().st_mtime)
            if mtime < cutoff:
                gz_file.unlink()
                cleaned += 1

        return {"cleaned": cleaned, "compressed": compressed}

    def cleanup_all(
        self,
        skill_name: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        result: dict[str, Any] = {}

        result["snapshots"] = {"would_clean": 0}
        if not dry_run:
            result["snapshots"] = self.cleanup_snapshots(skill_name)

        result["usage"] = {"would_clean": 0}
        if not dry_run:
            result["usage"] = self.cleanup_usage_files(
                max_days=self.max_usage_days,
                skill_name=skill_name,
            )

        result["logs"] = {"would_clean": 0}
        if not dry_run:
            result["logs"] = self.cleanup_logs(
                max_days=self.max_log_days,
                log_dir=self.log_dir,
            )

        return result

    def get_disk_usage(self, skill_name: str | None = None) -> dict[str, str]:
        result = {}

        def get_size(path: Path) -> str:
            if not path.exists():
                return "N/A"
            try:
                size = subprocess.check_output(
                    ["du", "-sh", str(path)],
                    stderr=subprocess.DEVNULL,
                    text=True,
                )
                return size.split()[0]
            except (subprocess.SubprocessError, IndexError):
                return "N/A"

        snapshot_path = self.snapshot_dir
        if skill_name:
            snapshot_path = snapshot_path / skill_name
        result["snapshots"] = get_size(snapshot_path)
        result["usage"] = get_size(self.usage_dir)
        result["logs"] = get_size(self.log_dir)

        return result
