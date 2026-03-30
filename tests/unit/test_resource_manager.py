"""Tests for resource manager module."""

from __future__ import annotations

import gzip
import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from skill.engine.resource_manager import ResourceManager


class TestResourceManager:
    """Test suite for ResourceManager class."""

    def test_initialization(self, tmp_path: Path):
        """Test ResourceManager initializes correctly."""
        rm = ResourceManager(
            snapshot_dir=tmp_path / "snapshots",
            usage_dir=tmp_path / "usage",
            log_dir=tmp_path / "logs",
        )
        assert rm.snapshot_dir == tmp_path / "snapshots"
        assert rm.usage_dir == tmp_path / "usage"
        assert rm.log_dir == tmp_path / "logs"

    def test_cleanup_snapshots_under_max(self, tmp_path: Path):
        """Test no cleanup when under max snapshots."""
        rm = ResourceManager(
            snapshot_dir=tmp_path / "snapshots",
            max_snapshots=5,
        )
        snapshot_dir = tmp_path / "snapshots"
        snapshot_dir.mkdir(parents=True)
        for i in range(3):
            (snapshot_dir / f"skill_{i}.tar.gz").touch()

        result = rm.cleanup_snapshots()
        assert result["removed"] == 0
        assert result["remaining"] == 3

    def test_cleanup_snapshots_over_max(self, tmp_path: Path):
        """Test cleanup removes oldest snapshots."""
        rm = ResourceManager(
            snapshot_dir=tmp_path / "snapshots",
            max_snapshots=3,
        )
        snapshot_dir = tmp_path / "snapshots"
        snapshot_dir.mkdir(parents=True)
        for i in range(5):
            (snapshot_dir / f"skill_{i}.tar.gz").touch()

        result = rm.cleanup_snapshots()
        assert result["removed"] == 2
        assert result["remaining"] == 3

    def test_cleanup_snapshots_skill_specific(self, tmp_path: Path):
        """Test cleanup for specific skill subdirectory."""
        rm = ResourceManager(
            snapshot_dir=tmp_path / "snapshots",
            max_snapshots=2,
        )
        snapshot_dir = tmp_path / "snapshots"
        skill_dir = snapshot_dir / "skill1"
        skill_dir.mkdir(parents=True)
        (skill_dir / "skill1_0.tar.gz").touch()
        (skill_dir / "skill1_1.tar.gz").touch()
        (skill_dir / "skill1_2.tar.gz").touch()
        (snapshot_dir / "skill2_0.tar.gz").touch()

        result = rm.cleanup_snapshots(skill_name="skill1")
        assert result["removed"] == 1
        assert result["remaining"] == 2

    def test_cleanup_snapshots_empty_dir(self, tmp_path: Path):
        """Test cleanup with no snapshots."""
        rm = ResourceManager(snapshot_dir=tmp_path / "snapshots")
        result = rm.cleanup_snapshots()
        assert result["removed"] == 0
        assert result["remaining"] == 0

    def test_cleanup_usage_files(self, tmp_path: Path):
        """Test cleanup of old usage files."""
        rm = ResourceManager(
            usage_dir=tmp_path / "usage",
            max_usage_days=7,
        )
        usage_dir = tmp_path / "usage"
        usage_dir.mkdir(parents=True)
        old_date = (datetime.now() - timedelta(days=10)).strftime("%Y%m%d")
        new_date = datetime.now().strftime("%Y%m%d")
        (usage_dir / f"usage_test_{old_date}.jsonl").touch()
        (usage_dir / f"usage_test_{new_date}.jsonl").touch()

        result = rm.cleanup_usage_files()
        assert result["removed"] == 1
        assert (usage_dir / f"usage_test_{new_date}.jsonl").exists()
        assert not (usage_dir / f"usage_test_{old_date}.jsonl").exists()

    def test_cleanup_logs_compress(self, tmp_path: Path):
        """Test log cleanup compresses old logs."""
        rm = ResourceManager(
            log_dir=tmp_path / "logs",
            max_log_days=7,
        )
        log_dir = tmp_path / "logs"
        log_dir.mkdir(parents=True)
        old_date = (datetime.now() - timedelta(days=10)).strftime("%Y%m%d")
        log_file = log_dir / f"test_{old_date}.log"
        log_file.write_text("old log content")

        result = rm.cleanup_logs()
        assert result["cleaned"] == 1
        assert result["compressed"] == 1
        assert (log_dir / f"test_{old_date}.log.gz").exists()
        assert not log_file.exists()

    def test_cleanup_logs_skip_recent(self, tmp_path: Path):
        """Test log cleanup skips recent logs."""
        rm = ResourceManager(
            log_dir=tmp_path / "logs",
            max_log_days=7,
        )
        log_dir = tmp_path / "logs"
        log_dir.mkdir(parents=True)
        new_date = datetime.now().strftime("%Y%m%d")
        log_file = log_dir / f"test_{new_date}.log"
        log_file.write_text("recent log")

        result = rm.cleanup_logs()
        assert result["cleaned"] == 0
        assert log_file.exists()

    def test_cleanup_logs_delete_old_gz(self, tmp_path: Path):
        """Test old gzipped logs are deleted."""
        import os

        rm = ResourceManager(
            log_dir=tmp_path / "logs",
            max_log_days=7,
        )
        log_dir = tmp_path / "logs"
        log_dir.mkdir(parents=True)
        old_date = (datetime.now() - timedelta(days=10)).strftime("%Y%m%d")
        gz_file = log_dir / f"test_{old_date}.log.gz"
        with gzip.open(gz_file, "wt") as f:
            f.write("old compressed log")
        old_mtime = (datetime.now() - timedelta(days=10)).timestamp()
        os.utime(gz_file, (old_mtime, old_mtime))

        result = rm.cleanup_logs()
        assert result["cleaned"] == 1
        assert not gz_file.exists()

    def test_cleanup_all(self, tmp_path: Path):
        """Test cleanup_all runs all cleanups."""
        rm = ResourceManager(
            snapshot_dir=tmp_path / "snapshots",
            usage_dir=tmp_path / "usage",
            log_dir=tmp_path / "logs",
            max_snapshots=2,
            max_usage_days=7,
            max_log_days=7,
        )
        snapshot_dir = tmp_path / "snapshots"
        snapshot_dir.mkdir(parents=True)
        for i in range(5):
            (snapshot_dir / f"skill_{i}.tar.gz").touch()

        old_date = (datetime.now() - timedelta(days=10)).strftime("%Y%m%d")
        usage_dir = tmp_path / "usage"
        usage_dir.mkdir(parents=True)
        (usage_dir / f"usage_test_{old_date}.jsonl").touch()

        log_dir = tmp_path / "logs"
        log_dir.mkdir(parents=True)
        log_file = log_dir / f"test_{old_date}.log"
        log_file.write_text("old log")

        result = rm.cleanup_all(dry_run=True)
        assert "snapshots" in result
        assert "usage" in result
        assert "logs" in result


class TestDiskUsage:
    """Test suite for disk usage reporting."""

    def test_get_disk_usage(self, tmp_path: Path):
        """Test getting disk usage."""
        rm = ResourceManager(
            snapshot_dir=tmp_path / "snapshots",
            usage_dir=tmp_path / "usage",
            log_dir=tmp_path / "logs",
        )
        snapshot_dir = tmp_path / "snapshots"
        snapshot_dir.mkdir(parents=True)
        (snapshot_dir / "test.tar.gz").write_text("x" * 1000)

        usage = rm.get_disk_usage()
        assert "snapshots" in usage
        assert "usage" in usage
        assert "logs" in usage
