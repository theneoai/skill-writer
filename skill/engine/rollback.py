"""Rollback and snapshot management for skill evolution."""

from __future__ import annotations

import tarfile
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class SnapshotInfo:
    path: Path
    skill_name: str
    timestamp: float
    reason: str


class RollbackManager:
    def __init__(
        self,
        snapshot_dir: Path | None = None,
        max_snapshots: int = 10,
    ) -> None:
        self.snapshot_dir = snapshot_dir or Path.home() / ".skill" / "snapshots"
        self.max_snapshots = max_snapshots

    def create_snapshot(
        self,
        skill_file: Path,
        reason: str = "auto",
    ) -> Path:
        if not skill_file.exists():
            raise FileNotFoundError(f"Skill file not found: {skill_file}")

        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S%f")
        import uuid

        unique_id = uuid.uuid4().hex[:8]
        snapshot_name = f"skill_{timestamp_str}_{reason}_{unique_id}"
        skill_name = skill_file.stem
        snapshot_dir = self.snapshot_dir / skill_name
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        snapshot_path = snapshot_dir / f"{snapshot_name}.tar.gz"

        with tarfile.open(snapshot_path, "w:gz") as tar:
            tar.add(skill_file, arcname=skill_file.name)

        self.cleanup_snapshots()
        return snapshot_path

    def list_snapshots(self, limit: int = 20) -> list[Path]:
        if not self.snapshot_dir.exists():
            return []

        snapshots = sorted(
            self.snapshot_dir.rglob("*.tar.gz"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        return snapshots[:limit]

    def rollback_to(
        self,
        snapshot_path: Path,
        skill_file: Path,
    ) -> None:
        if not snapshot_path.exists():
            raise FileNotFoundError(f"Snapshot not found: {snapshot_path}")

        skill_parent = skill_file.parent
        with tarfile.open(snapshot_path, "r:gz") as tar:
            tar.extractall(skill_parent)

    def rollback_to_latest(self, skill_file: Path) -> bool:
        snapshots = self.list_snapshots(limit=1)
        if not snapshots:
            return False

        latest = snapshots[0]
        self.rollback_to(latest, skill_file)
        return True

    def rollback_to_date(
        self,
        date_str: str,
        skill_file: Path,
    ) -> bool:
        pattern = f"skill_{date_str}_*.tar.gz"
        snapshots = sorted(
            self.snapshot_dir.rglob(pattern),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        if not snapshots:
            return False

        self.rollback_to(snapshots[0], skill_file)
        return True

    def cleanup_snapshots(self) -> None:
        if not self.snapshot_dir.exists():
            return

        all_snapshots = sorted(
            self.snapshot_dir.rglob("*.tar.gz"),
            key=lambda p: p.stat().st_mtime,
        )

        if len(all_snapshots) > self.max_snapshots:
            to_remove = all_snapshots[: len(all_snapshots) - self.max_snapshots]
            for snapshot in to_remove:
                snapshot.unlink()

    def check_auto_rollback(
        self,
        current_score: float,
        previous_score: float,
        format_valid: bool = True,
        skill_file: Path | None = None,
    ) -> bool:
        if not format_valid:
            if skill_file:
                self.rollback_to_latest(skill_file)
            return True

        regression = previous_score - current_score
        if regression > 20:
            if skill_file:
                self.rollback_to_latest(skill_file)
            return True

        return False
