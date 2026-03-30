import pytest
import time
from skill.agents.evolution_memory import MemoryEntry, EvolutionMemory


class TestMemoryEntry:
    def test_create_entry(self):
        entry = MemoryEntry(
            timestamp=time.time(),
            task_type="CREATE",
            trajectory=[{"action": "step1", "result": "success"}],
            outcome="success",
            reward=1.0,
            lessons=["Lesson 1"],
        )
        assert entry.outcome == "success"
        assert entry.reward == 1.0

    def test_get_similar(self):
        memory = EvolutionMemory()
        memory.add(MemoryEntry(time.time(), "CREATE", [{"a": 1}], "success", 1.0, []))
        memory.add(MemoryEntry(time.time(), "CREATE", [{"a": 2}], "success", 0.8, []))
        memory.add(MemoryEntry(time.time(), "EVALUATE", [{"a": 3}], "success", 0.9, []))

        similar = memory.get_similar("CREATE", k=2)
        assert len(similar) == 2
