from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
import threading
from pathlib import Path


class ParallelOrchestrator:
    def execute(
        self,
        cmd1: str,
        cmd2: str,
        result_file1: str = "",
        result_file2: str = "",
    ) -> bool:
        if not cmd1 or not cmd2:
            print("Error: Commands cannot be empty", file=__import__("sys").stderr)
            return False

        dangerous_pattern = r"[;&|`$]"
        if re.search(dangerous_pattern, cmd1) or re.search(dangerous_pattern, cmd2):
            print("Error: Dangerous characters in parallel commands", file=__import__("sys").stderr)
            return False

        p1 = None
        p2 = None

        if result_file1:
            with open(result_file1, "w") as f:
                p1 = subprocess.Popen(cmd1, shell=True, stdout=f, stderr=subprocess.DEVNULL)
        else:
            p1 = subprocess.Popen(
                cmd1, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )

        if result_file2:
            with open(result_file2, "w") as f:
                p2 = subprocess.Popen(cmd2, shell=True, stdout=f, stderr=subprocess.DEVNULL)
        else:
            p2 = subprocess.Popen(
                cmd2, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )

        p1.wait()
        exit1 = p1.returncode

        p2.wait()
        exit2 = p2.returncode

        return exit1 == 0 and exit2 == 0

    def run_parallel_evaluation(self, skill_file: str) -> str:
        temp_dir = tempfile.mkdtemp(prefix="parallel_eval_")
        result_file = Path(temp_dir) / "result.json"

        eval_pid_file = Path(temp_dir) / "eval.pid"
        result_path_file = Path(temp_dir) / "result_path"

        def run_evaluator() -> None:
            pass

        thread = threading.Thread(target=run_evaluator)
        thread.start()

        eval_pid_file.write_text("")
        result_path_file.write_text(str(result_file))

        return temp_dir

    def wait_for_evaluation(self, temp_dir: str) -> str:
        eval_pid_file = Path(temp_dir) / "eval.pid"
        result_path_file = Path(temp_dir) / "result_path"

        if eval_pid_file.exists():
            eval_pid_file.read_text()

        result = ""
        if result_path_file.exists():
            result_file = result_path_file.read_text().strip()
            if result_file and Path(result_file).exists():
                result = Path(result_file).read_text()

        temp_path = Path(temp_dir)
        if temp_path.exists():
            shutil.rmtree(temp_dir)

        return result
