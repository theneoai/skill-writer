import pytest
from unittest.mock import patch, MagicMock
from skill.orchestrator.workflow import WorkflowOrchestrator


class TestWorkflowOrchestrator:
    def test_init(self):
        orchestrator = WorkflowOrchestrator()
        assert orchestrator.evaluator_feedback == ""

    @patch("pathlib.Path.mkdir")
    @patch("skill.orchestrator.workflow.get_orchestrator_state")
    def test_init_workflow(self, mock_get_state, mock_mkdir):
        mock_state = MagicMock()
        mock_get_state.return_value = mock_state

        orchestrator = WorkflowOrchestrator()
        orchestrator.init_workflow(
            user_prompt="Create a skill", output_file="/path/to/skill.md"
        )

        mock_state.set_prompt.assert_called_once_with("Create a skill")
        mock_state.set_target_file.assert_called_once_with("/path/to/skill.md")

    @patch("skill.orchestrator.workflow.get_orchestrator_state")
    def test_append_content_normal(self, mock_get_state):
        mock_state = MagicMock()
        mock_state.target_skill_file = "/tmp/skill.md"
        mock_state.dry_run = 0
        mock_get_state.return_value = mock_state

        orchestrator = WorkflowOrchestrator()
        result = orchestrator.append_content("new content")

        assert result is True

    @patch("skill.orchestrator.workflow.get_orchestrator_state")
    def test_append_content_empty(self, mock_get_state):
        mock_state = MagicMock()
        mock_get_state.return_value = mock_state

        orchestrator = WorkflowOrchestrator()
        result = orchestrator.append_content("")
        assert result is False

        result = orchestrator.append_content("{}")
        assert result is False

    @patch("skill.orchestrator.workflow.get_orchestrator_state")
    def test_append_content_dry_run(self, mock_get_state):
        mock_state = MagicMock()
        mock_state.target_skill_file = "/tmp/skill.md"
        mock_state.dry_run = 1
        mock_get_state.return_value = mock_state

        orchestrator = WorkflowOrchestrator()
        result = orchestrator.append_content("new content")

        assert result is True

    @patch("skill.orchestrator.workflow.get_orchestrator_state")
    def test_run_workflow_stops_at_max_iterations(self, mock_get_state):
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_file = os.path.join(tmpdir, "skill.md")

            mock_state = MagicMock()
            mock_state.max_iterations = 2
            mock_state.current_section = 0
            mock_state.target_skill_file = skill_file
            mock_state.dry_run = 1
            mock_state.last_score = 0

            iteration_count = [0]

            def inc_iteration():
                iteration_count[0] += 1

            mock_state.inc_iteration.side_effect = inc_iteration
            mock_state.evaluation_count = 0

            def get_iteration_count():
                return iteration_count[0]

            type(mock_state).iteration_count = property(
                lambda self: get_iteration_count()
            )
            mock_get_state.return_value = mock_state

            orchestrator = WorkflowOrchestrator()
            orchestrator.init_workflow("test prompt", skill_file)

            result = orchestrator.run_workflow()

            assert mock_state.inc_iteration.call_count == 2

    @patch("skill.orchestrator.workflow.get_orchestrator_state")
    def test_final_evaluate(self, mock_get_state):
        mock_state = MagicMock()
        mock_get_state.return_value = mock_state

        mock_state.target_skill_file = "/tmp/skill.md"
        mock_state.iteration_count = 5

        orchestrator = WorkflowOrchestrator()
        orchestrator.state = mock_state

        result = orchestrator.final_evaluate()

        assert "final_score" in result
        assert "final_tier" in result
        assert "iterations" in result
