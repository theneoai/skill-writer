import pytest
from unittest.mock import patch, MagicMock
from skill.orchestrator.actions import ActionsOrchestrator


class TestActionsOrchestrator:
    def test_get_next_action_platinum(self):
        orchestrator = ActionsOrchestrator()
        action = orchestrator.get_next_action(95, "PLATINUM")
        assert action == "done"

    @patch("skill.orchestrator.actions.get_orchestrator_state")
    def test_get_next_action_gold_high_score(self, mock_get_state):
        mock_state = MagicMock()
        mock_state.max_iterations = 20
        mock_state.iteration_count = 5
        mock_get_state.return_value = mock_state

        orchestrator = ActionsOrchestrator()
        action = orchestrator.get_next_action(950, "GOLD")
        assert action == "done"

    @patch("skill.orchestrator.actions.get_orchestrator_state")
    def test_get_next_action_silver_high_score(self, mock_get_state):
        mock_state = MagicMock()
        mock_state.max_iterations = 20
        mock_state.iteration_count = 5
        mock_get_state.return_value = mock_state

        orchestrator = ActionsOrchestrator()
        action = orchestrator.get_next_action(850, "SILVER")
        assert action == "done"

    @patch("skill.orchestrator.actions.get_orchestrator_state")
    def test_get_next_action_bronze_high_score(self, mock_get_state):
        mock_state = MagicMock()
        mock_state.max_iterations = 20
        mock_state.iteration_count = 5
        mock_get_state.return_value = mock_state

        orchestrator = ActionsOrchestrator()
        action = orchestrator.get_next_action(750, "BRONZE")
        assert action == "done"

    @patch("skill.orchestrator.actions.get_orchestrator_state")
    def test_get_next_action_max_iterations(self, mock_get_state):
        mock_state = MagicMock()
        mock_state.max_iterations = 20
        mock_state.iteration_count = 20
        mock_get_state.return_value = mock_state

        orchestrator = ActionsOrchestrator()
        action = orchestrator.get_next_action(50, "BRONZE")
        assert action == "done"

    @patch("skill.orchestrator.actions.get_orchestrator_state")
    def test_get_next_action_score_improved(self, mock_get_state):
        mock_state = MagicMock()
        mock_state.max_iterations = 20
        mock_state.iteration_count = 5
        mock_state.last_score = 50
        mock_get_state.return_value = mock_state

        orchestrator = ActionsOrchestrator()
        action = orchestrator.get_next_action(60, "BRONZE")
        assert action == "continue"

    @patch("skill.orchestrator.actions.get_orchestrator_state")
    def test_get_next_action_needs_improvement(self, mock_get_state):
        mock_state = MagicMock()
        mock_state.max_iterations = 20
        mock_state.iteration_count = 5
        mock_state.last_score = 60
        mock_get_state.return_value = mock_state

        orchestrator = ActionsOrchestrator()
        action = orchestrator.get_next_action(50, "BRONZE")
        assert action == "improve"

    @patch("skill.orchestrator.actions.get_orchestrator_state")
    def test_check_evolution_trigger_new_phase(self, mock_get_state):
        mock_state = MagicMock()
        mock_state.evaluation_count = 20
        mock_get_state.return_value = mock_state

        orchestrator = ActionsOrchestrator()
        result = orchestrator.check_evolution_trigger()
        assert result is False

    @patch("skill.orchestrator.actions.get_orchestrator_state")
    def test_check_evolution_trigger_growing_phase(self, mock_get_state):
        mock_state = MagicMock()
        mock_state.evaluation_count = 100
        mock_get_state.return_value = mock_state

        orchestrator = ActionsOrchestrator()
        result = orchestrator.check_evolution_trigger()
        assert result is True

    @patch("skill.orchestrator.actions.get_orchestrator_state")
    def test_check_evolution_trigger_no_trigger(self, mock_get_state):
        mock_state = MagicMock()
        mock_state.evaluation_count = 5
        mock_get_state.return_value = mock_state

        orchestrator = ActionsOrchestrator()
        result = orchestrator.check_evolution_trigger()
        assert result is False

    def test_log_verbose_enabled(self):
        orchestrator = ActionsOrchestrator()
        orchestrator.verbose = 1
        with patch("sys.stderr") as mock_stderr:
            orchestrator.log_verbose("test message")
            assert mock_stderr.write.called

    def test_log_verbose_disabled(self):
        orchestrator = ActionsOrchestrator()
        orchestrator.verbose = 0
        with patch("sys.stderr") as mock_stderr:
            orchestrator.log_verbose("test message")
            mock_stderr.write.assert_not_called()
