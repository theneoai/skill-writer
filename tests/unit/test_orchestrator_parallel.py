import pytest
from skill.orchestrator.parallel import ParallelOrchestrator


class TestParallelOrchestrator:
    def test_execute_empty_commands(self):
        orchestrator = ParallelOrchestrator()
        result = orchestrator.execute("", "echo test")
        assert result is False

        result = orchestrator.execute("echo test", "")
        assert result is False

    def test_execute_dangerous_characters(self):
        orchestrator = ParallelOrchestrator()

        dangerous_commands = [
            ("echo `ls`", "echo test"),
            ("echo $HOME", "echo test"),
            ("echo | cat", "echo test"),
            ("echo &", "echo test"),
            ("echo ;", "echo test"),
        ]

        for cmd1, cmd2 in dangerous_commands:
            result = orchestrator.execute(cmd1, cmd2)
            assert result is False, f"Should reject dangerous command: {cmd1}"

    def test_execute_valid_commands(self):
        orchestrator = ParallelOrchestrator()
        result = orchestrator.execute("echo hello", "echo world")
        assert result is True

    def test_execute_with_result_files(self, tmp_path):
        result_file1 = tmp_path / "result1.txt"
        result_file2 = tmp_path / "result2.txt"

        orchestrator = ParallelOrchestrator()
        result = orchestrator.execute(
            "echo hello", "echo world", str(result_file1), str(result_file2)
        )

        assert result is True
        assert result_file1.read_text().strip() == "hello"
        assert result_file2.read_text().strip() == "world"

    def test_execute_first_command_fails(self):
        orchestrator = ParallelOrchestrator()
        result = orchestrator.execute("exit 1", "echo success")
        assert result is False

    def test_execute_second_command_fails(self):
        orchestrator = ParallelOrchestrator()
        result = orchestrator.execute("echo success", "exit 1")
        assert result is False

    def test_run_parallel_evaluation(self):
        orchestrator = ParallelOrchestrator()
        temp_dir = orchestrator.run_parallel_evaluation("/tmp/skill.md")

        assert temp_dir is not None
        from pathlib import Path

        temp_path = Path(temp_dir)
        assert temp_path.exists()
        assert (temp_path / "eval.pid").exists()
        assert (temp_path / "result_path").exists()

        import shutil

        shutil.rmtree(temp_dir)

    def test_wait_for_evaluation(self):
        orchestrator = ParallelOrchestrator()
        temp_dir = orchestrator.run_parallel_evaluation("/tmp/skill.md")

        result = orchestrator.wait_for_evaluation(temp_dir)

        from pathlib import Path

        assert not Path(temp_dir).exists()
