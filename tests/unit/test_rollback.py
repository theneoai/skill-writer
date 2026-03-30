"""Tests for rollback module."""

from __future__ import annotations

import tarfile
import tempfile
from pathlib import Path

import pytest

from skill.engine.rollback import RollbackManager, SnapshotInfo


class TestSnapshotInfo:
    """Test suite for SnapshotInfo dataclass."""

    def test_snapshot_info_creation(self):
        """Test SnapshotInfo stores all fields."""
        info = SnapshotInfo(
            path=Path("/path/to/snapshot.tar.gz"),
            skill_name="test_skill",
            timestamp=1234567890.0,
            reason="auto",
        )
        assert info.path == Path("/path/to/snapshot.tar.gz")
        assert info.skill_name == "test_skill"
        assert info.timestamp == 1234567890.0
        assert info.reason == "auto"


class TestRollbackManager:
    """Test suite for RollbackManager class."""

    def test_initialization(self, tmp_path: Path):
        """Test RollbackManager initializes correctly."""
        rm = RollbackManager(snapshot_dir=tmp_path / "snapshots")
        assert rm.snapshot_dir == tmp_path / "snapshots"

    def test_create_snapshot(self, tmp_path: Path):
        """Test creating a snapshot."""
        rm = RollbackManager(snapshot_dir=tmp_path / "snapshots")
        skill_file = tmp_path / "test.md"
        skill_file.write_text("# Test Skill")

        snapshot_path = rm.create_snapshot(skill_file, reason="test")
        assert snapshot_path.exists()
        assert str(snapshot_path).endswith(".tar.gz")

    def test_create_snapshot_file_not_found(self, tmp_path: Path):
        """Test creating snapshot for non-existent file."""
        rm = RollbackManager(snapshot_dir=tmp_path / "snapshots")
        skill_file = tmp_path / "nonexistent.md"

        with pytest.raises(FileNotFoundError):
            rm.create_snapshot(skill_file, reason="test")

    def test_create_snapshot_extracts_correctly(self, tmp_path: Path):
        """Test snapshot contains correct content."""
        rm = RollbackManager(snapshot_dir=tmp_path / "snapshots")
        skill_file = tmp_path / "test.md"
        skill_file.write_text("# Original Content")

        snapshot_path = rm.create_snapshot(skill_file, reason="test")

        extract_dir = tmp_path / "extract"
        extract_dir.mkdir()
        with tarfile.open(snapshot_path, "r:gz") as tar:
            tar.extractall(extract_dir)

        extracted = extract_dir / "test.md"
        assert extracted.exists()
        assert extracted.read_text() == "# Original Content"

    def test_list_snapshots_empty(self, tmp_path: Path):
        """Test listing snapshots when none exist."""
        rm = RollbackManager(snapshot_dir=tmp_path / "snapshots")
        snapshots = rm.list_snapshots()
        assert snapshots == []

    def test_list_snapshots(self, tmp_path: Path):
        """Test listing snapshots."""
        rm = RollbackManager(snapshot_dir=tmp_path / "snapshots")
        skill_file = tmp_path / "test.md"
        skill_file.write_text("# Test")
        rm.create_snapshot(skill_file, reason="test")
        rm.create_snapshot(skill_file, reason="test")

        snapshots = rm.list_snapshots()
        assert len(snapshots) == 2

    def test_list_snapshots_limits(self, tmp_path: Path):
        """Test listing snapshots is limited and cleanup enforced."""
        rm = RollbackManager(
            snapshot_dir=tmp_path / "snapshots",
            max_snapshots=30,
        )
        skill_file = tmp_path / "test.md"
        skill_file.write_text("# Test")
        for i in range(25):
            rm.create_snapshot(skill_file, reason=f"test{i}")

        snapshots = rm.list_snapshots(limit=20)
        assert len(snapshots) == 20
        for s in snapshots[:20]:
            assert s.exists()

    def test_cleanup_enforced(self, tmp_path: Path):
        """Test cleanup removes old snapshots beyond max."""
        rm = RollbackManager(
            snapshot_dir=tmp_path / "snapshots",
            max_snapshots=10,
        )
        skill_file = tmp_path / "test.md"
        skill_file.write_text("# Test")
        for i in range(25):
            rm.create_snapshot(skill_file, reason=f"test{i}")

        snapshots = rm.list_snapshots()
        assert len(snapshots) == 10

    def test_rollback_to(self, tmp_path: Path):
        """Test rolling back to a snapshot."""
        rm = RollbackManager(snapshot_dir=tmp_path / "snapshots")
        skill_file = tmp_path / "test.md"
        skill_file.write_text("# Original")

        snapshot_path = rm.create_snapshot(skill_file, reason="test")

        skill_file.write_text("# Modified")
        assert skill_file.read_text() == "# Modified"

        rm.rollback_to(snapshot_path, skill_file)
        assert skill_file.read_text() == "# Original"

    def test_rollback_to_nonexistent(self, tmp_path: Path):
        """Test rollback to non-existent snapshot."""
        rm = RollbackManager(snapshot_dir=tmp_path / "snapshots")
        skill_file = tmp_path / "test.md"
        skill_file.write_text("# Test")

        with pytest.raises(FileNotFoundError):
            rm.rollback_to(tmp_path / "nonexistent.tar.gz", skill_file)

    def test_rollback_to_latest(self, tmp_path: Path):
        """Test rolling back to latest snapshot."""
        rm = RollbackManager(snapshot_dir=tmp_path / "snapshots")
        skill_file = tmp_path / "test.md"
        skill_file.write_text("# Original")

        rm.create_snapshot(skill_file, reason="first")

        skill_file.write_text("# Modified")

        result = rm.rollback_to_latest(skill_file)
        assert result is True
        assert skill_file.read_text() == "# Original"

    def test_rollback_to_latest_none_exist(self, tmp_path: Path):
        """Test rollback to latest when no snapshots exist."""
        rm = RollbackManager(snapshot_dir=tmp_path / "snapshots")
        skill_file = tmp_path / "test.md"

        result = rm.rollback_to_latest(skill_file)
        assert result is False

    def test_rollback_to_date(self, tmp_path: Path):
        """Test rolling back to specific date."""
        rm = RollbackManager(snapshot_dir=tmp_path / "snapshots")
        skill_file = tmp_path / "test.md"
        skill_file.write_text("# Original")

        snapshot_path = rm.create_snapshot(skill_file, reason="test")

        skill_file.write_text("# Modified")

        snapshot_name = snapshot_path.stem
        date_str = snapshot_name.split("_")[1]

        result = rm.rollback_to_date(date_str, skill_file)
        assert result is True
        assert skill_file.read_text() == "# Original"

    def test_rollback_to_date_not_found(self, tmp_path: Path):
        """Test rollback to date with no matching snapshot."""
        rm = RollbackManager(snapshot_dir=tmp_path / "snapshots")
        skill_file = tmp_path / "test.md"

        result = rm.rollback_to_date("19990101", skill_file)
        assert result is False

    def test_cleanup_snapshots(self, tmp_path: Path):
        """Test cleanup of old snapshots."""
        rm = RollbackManager(
            snapshot_dir=tmp_path / "snapshots",
            max_snapshots=3,
        )
        skill_file = tmp_path / "test.md"
        skill_file.write_text("# Test")
        for i in range(5):
            rm.create_snapshot(skill_file, reason=f"test{i}")

        snapshots = rm.list_snapshots()
        assert len(snapshots) == 3


class TestAutoRollback:
    """Test suite for auto-rollback functionality."""

    def test_check_auto_rollback_invalid_format(self, tmp_path: Path):
        """Test auto rollback on invalid format."""
        rm = RollbackManager(snapshot_dir=tmp_path / "snapshots")
        skill_file = tmp_path / "test.md"
        skill_file.write_text("# Original")
        rm.create_snapshot(skill_file, reason="test")

        result = rm.check_auto_rollback(
            current_score=50,
            previous_score=80,
            format_valid=False,
        )
        assert result is True

    def test_check_auto_rollback_large_regression(self, tmp_path: Path):
        """Test auto rollback on large score regression."""
        rm = RollbackManager(snapshot_dir=tmp_path / "snapshots")
        skill_file = tmp_path / "test.md"
        skill_file.write_text("# Original")
        rm.create_snapshot(skill_file, reason="test")

        result = rm.check_auto_rollback(
            current_score=60,
            previous_score=90,
            format_valid=True,
        )
        assert result is True

    def test_check_auto_rollback_small_regression(self, tmp_path: Path):
        """Test no auto rollback on small regression."""
        rm = RollbackManager(snapshot_dir=tmp_path / "snapshots")
        skill_file = tmp_path / "test.md"
        skill_file.write_text("# Original")
        rm.create_snapshot(skill_file, reason="test")

        result = rm.check_auto_rollback(
            current_score=80,
            previous_score=90,
            format_valid=True,
        )
        assert result is False

    def test_check_auto_rollback_improvement(self, tmp_path: Path):
        """Test no auto rollback on score improvement."""
        rm = RollbackManager(snapshot_dir=tmp_path / "snapshots")
        skill_file = tmp_path / "test.md"
        skill_file.write_text("# Original")
        rm.create_snapshot(skill_file, reason="test")

        result = rm.check_auto_rollback(
            current_score=90,
            previous_score=80,
            format_valid=True,
        )
        assert result is False
