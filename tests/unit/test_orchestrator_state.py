import pytest
from skill.orchestrator.state import OrchestratorState, get_orchestrator_state


class TestOrchestratorState:
    def test_initial_state_values(self):
        state = OrchestratorState()
        assert state.initial_prompt == ""
        assert state.target_skill_file == ""
        assert state.target_tier == "BRONZE"
        assert state.max_iterations == 20
        assert state.current_section == 0
        assert state.evaluation_count == 0
        assert state.last_score == 0
        assert state.iteration_count == 0
        assert state.creator_sourced == 0
        assert state.evaluator_sourced == 0
        assert state.dry_run == 0
        assert state.verbose == 0

    def test_set_prompt(self):
        state = OrchestratorState()
        state.set_prompt("Create a skill")
        assert state.initial_prompt == "Create a skill"

    def test_set_target_file(self):
        state = OrchestratorState()
        state.set_target_file("/path/to/skill.md")
        assert state.target_skill_file == "/path/to/skill.md"

    def test_set_tier(self):
        state = OrchestratorState()
        state.set_tier("GOLD")
        assert state.target_tier == "GOLD"

    def test_inc_iteration(self):
        state = OrchestratorState()
        state.inc_iteration()
        assert state.iteration_count == 1
        state.inc_iteration()
        assert state.iteration_count == 2

    def test_inc_evaluation(self):
        state = OrchestratorState()
        state.inc_evaluation()
        assert state.evaluation_count == 1

    def test_inc_section(self):
        state = OrchestratorState()
        state.inc_section()
        assert state.current_section == 1

    def test_set_last_score(self):
        state = OrchestratorState()
        state.set_last_score(85)
        assert state.last_score == 85

    def test_get_context(self):
        state = OrchestratorState()
        state.set_prompt("Create a skill")
        state.set_tier("SILVER")
        state.current_section = 2
        state.iteration_count = 5
        state.evaluation_count = 3
        context = state.get_context()
        assert context["user_prompt"] == "Create a skill"
        assert context["current_section"] == 2
        assert context["target_tier"] == "SILVER"
        assert context["iteration"] == 5
        assert context["eval_count"] == 3

    def test_dump(self):
        state = OrchestratorState()
        state.set_prompt("Test prompt")
        state.set_target_file("/path/to/skill.md")
        state.set_tier("GOLD")
        state.current_section = 1
        state.evaluation_count = 2
        state.last_score = 75
        state.iteration_count = 3
        dump = state.dump()
        assert "PROMPT: Test prompt" in dump
        assert "TARGET: /path/to/skill.md" in dump
        assert "TIER: GOLD" in dump
        assert "SECTION: 1" in dump
        assert "EVAL_COUNT: 2" in dump
        assert "LAST_SCORE: 75" in dump
        assert "ITERATION: 3" in dump

    def test_singleton_get_orchestrator_state(self):
        state1 = get_orchestrator_state()
        state2 = get_orchestrator_state()
        assert state1 is state2
