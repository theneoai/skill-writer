import pytest
from skill.orchestrator.loongflow import LoongFlowOrchestrator
from skill.agents.evolution_memory import EvolutionMemory


class TestLoongFlowOrchestrator:
    def test_loongflow_with_boad(self):
        from skill.agents.boad import BOADOptimizer
        memory = EvolutionMemory()
        orchestrator = LoongFlowOrchestrator(memory=memory)
        optimizer = BOADOptimizer()
        orchestrator.set_agent_optimizer(optimizer)
        assert orchestrator.optimizer is optimizer

    def test_loongflow_with_road(self):
        from skill.engine.road import ROADRecover
        memory = EvolutionMemory()
        orchestrator = LoongFlowOrchestrator(memory=memory)
        road = ROADRecover()
        orchestrator.set_error_recovery(road)
        assert orchestrator.error_recovery is road

    def test_init(self):
        memory = EvolutionMemory()
        orchestrator = LoongFlowOrchestrator(memory=memory)
        assert orchestrator.memory is memory

    def test_run_full_loop(self):
        memory = EvolutionMemory()
        orchestrator = LoongFlowOrchestrator(memory=memory)
        result = orchestrator.run("Create a weather skill")
        assert result.success is True
        completed = orchestrator.collector.get_completed()
        assert len(completed) == 1
        assert completed[0].task_type == "CREATE"
        assert completed[0].outcome == "success"
