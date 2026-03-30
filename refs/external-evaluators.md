# External Skill Evaluation Tools

Comprehensive catalog of external evaluation tools from commercial providers, research institutions, and open-source projects for cross-reference and comparison.

## Overview

This document catalogs external evaluation tools. When evaluating skills with this project, you can compare results against these tools for reference and validation.

---

## 1. OpenAI Evals

**Provider**: OpenAI  
**Documentation**: https://platform.openai.com/docs/guides/evals  
**Repository**: https://github.com/openai/evals  
**Type**: Cloud API + Open Source Framework

### Core Features

| Feature | Description |
|---------|-------------|
| Data Sources | JSONL files with custom schema |
| Testing Criteria | String check, pattern match, model-graded |
| Graders | Built-in + custom grader functions |
| Model Support | GPT-4.1, o-series, custom fine-tuned |
| Deployment | API + Dashboard |
| Registry | 100+ pre-built evaluation benchmarks |

### Evaluation Types

- **String Check**: Exact match validation
- **Pattern Match**: Regex-based validation
- **Model Graded**: LLM-as-judge evaluation
- **Classification**: Accuracy metrics
- **Embedding Distance**: Cosine similarity

### Quick Start

```python
from openai import OpenAI
client = OpenAI()

eval_obj = client.evals.create(
    name="Skill Quality Eval",
    data_source_config={
        "type": "custom",
        "item_schema": {
            "type": "object",
            "properties": {
                "skill_content": {"type": "string"},
                "quality_score": {"type": "number"}
            }
        }
    },
    testing_criteria=[{
        "type": "string_check",
        "input": "{{ sample.output_text }}",
        "operation": "eq",
        "reference": "{{ item.quality_score }}"
    }]
)
```

### Integration Status

| Aspect | Status |
|--------|--------|
| API Available | ✅ Yes |
| Free Tier | ⚠️ Limited (1000 eval items/month) |
| Custom Graders | ✅ Yes |
| Batch Evaluation | ✅ Yes |
| Open Source | ✅ Yes (eval logic) |

---

## 2. LangSmith Evaluation

**Provider**: LangChain (Anthropic-backed)  
**Documentation**: https://docs.smith.langchain.com/evaluation  
**Repository**: https://github.com/langchain-ai/langsmith-sdk  
**Type**: Cloud + SDK

### Core Features

| Feature | Description |
|---------|-------------|
| Tracing | Full execution trace capture |
| Datasets | CSV/JSONL test datasets |
| Evaluators | Built-in (accuracy, toxicity, relevance) + custom |
| Comparators | A/B model/prompt testing |
| Feedback | Human annotation + automated |
| Online Eval | Real-time production monitoring |
| Offline Eval | Pre-deployment dataset testing |

### Evaluation Types

```python
from langsmith.evaluation import evaluate

def my_evaluator(run, example):
    return {"score": run.outputs["quality"] > 0.8}

evaluate(
    dataset_name="skill-eval-dataset",
    data_type="executor",
    evaluators=[my_evaluator],
)
```

### Integrations

| Aspect | Status |
|--------|--------|
| Python SDK | ✅ Yes |
| JS/TS SDK | ✅ Yes |
| OpenAI Compatible | ✅ Yes |
| On-Premise | ❌ Cloud only |
| LangChain Native | ✅ Yes |

---

## 3. Anthropic Claude Evaluation

**Provider**: Anthropic  
**Documentation**: https://docs.anthropic.com/en/docs/build-with-claude/evaluation  
**Type**: Platform + API

### Core Features

| Feature | Description |
|---------|-------------|
| Skills | Markdown-based skill definitions |
| Evaluation | Built-in quality metrics |
| Security | CWE-based security scanning |
| Multi-model | Claude 3.5 Sonnet, Opus, Haiku |
| Prompt Engineering | Interactive playground |

### Evaluation Criteria

- **Clarity**: Skill documentation quality
- **Completeness**: All required fields present
- **Correctness**: Functional accuracy
- **Safety**: Security baseline compliance (CWE)

### Status

| Aspect | Status |
|--------|--------|
| Documentation | ⚠️ Region-limited |
| API Access | via Anthropic Platform |
| Open Source | ❌ Proprietary |
| Skills Framework | ✅ Yes |

---

## 4. Google Vertex AI Agent Evaluation

**Provider**: Google Cloud  
**Documentation**: https://cloud.google.com/vertex-ai/generative-ai/docs/learn/about-ai-platform  
**Type**: Enterprise Cloud

### Core Features

| Feature | Description |
|---------|-------------|
| Agent Builder | No-code agent creation |
| Evaluation | Automated quality scoring |
| Benchmarking | Industry standard benchmarks |
| Enterprise | SOC2, HIPAA compliant |
| Model Garden | 150+ pre-trained models |

### Evaluation Metrics

- Task completion rate
- Response accuracy
- Safety policy compliance
- Latency benchmarking

### Status

| Aspect | Status |
|--------|--------|
| API Available | ✅ Yes |
| Enterprise Focus | ✅ Yes |
| Free Tier | ❌ Enterprise only |
| GCP Integration | ✅ Yes |

---

## 5. Microsoft Azure AI Studio

**Provider**: Microsoft  
**Documentation**: https://azure.microsoft.com/products/ai-studio  
**Type**: Enterprise Cloud + On-Premise

### Core Features

| Feature | Description |
|---------|-------------|
| Evaluation | Automated + human-in-loop |
| Safety | Built-in content filtering |
| Metrics | Accuracy, groundedness, relevance |
| RAI | Responsible AI metrics |
| Flow Evaluation | Copilot Studio integration |

### Evaluation Types

- **Automated**: Model-graded evaluation
- **Human-in-loop**: Manual review workflows
- **Responsible AI**: Bias detection, fairness metrics

### Status

| Aspect | Status |
|--------|--------|
| API Available | ✅ Yes |
| Enterprise Focus | ✅ Yes |
| On-Premise | ✅ Yes (AI Infrastructure) |
| Azure Integration | ✅ Yes |

---

## 6. Arize Phoenix (Open Source)

**Provider**: Arize AI  
**Documentation**: https://docs.arize.com/phoenix  
**Repository**: https://github.com/Arize-ai/phoenix  
**Type**: Open Source + Cloud

### Core Features

| Feature | Description |
|---------|-------------|
| LLM Tracing | OpenTelemetry-based trace collection |
| Evals | Built-in + custom evaluators |
| Datasets | CSV/JSONL test datasets |
| Hallucination Detection | RAG-specific metrics |
| Drift Detection | Data and model drift monitoring |

### Evaluation Types

- **LLM as Judge**: Automated grading
- **Code-based**: Deterministic validation
- **Reference-free**: Safety, toxicity checks
- **Reference-based**: Ground truth comparison

### Quick Start

```python
import phoenix as px

# Start Phoenix
px.launch_app()

# Define evaluator
from phoenix.evals import llm_classify

results = llm_classify(
    dataframe=df,
    model=gpt-4,
    template=template,
)
```

### Integration Status

| Aspect | Status |
|--------|--------|
| Python SDK | ✅ Yes |
| Open Source | ✅ Yes |
| Cloud Platform | ✅ Yes (Arize AX) |
| LangChain Integration | ✅ Yes |

---

## 7. Weights & Biases (W&B) Evaluation

**Provider**: Weights & Biases  
**Documentation**: https://docs.wandb.ai  
**Type**: Cloud + Self-hosted

### Core Features

| Feature | Description |
|---------|-------------|
| Experiment Tracking | Hyperparameter logging |
| Model Evaluation | Automated eval pipelines |
| Artifacts | Dataset and model versioning |
| Sweeps | Hyperparameter optimization |
| Reports | Collaborative analysis |

### Evaluation Integration

```python
import wandb

wandb.init(project="skill-eval")

# Log evaluation metrics
wandb.log({
    "accuracy": 0.95,
    "f1": 0.92,
    "latency_ms": 45,
})
```

### Status

| Aspect | Status |
|--------|--------|
| Free Tier | ✅ Yes (500GB) |
| Enterprise | ✅ Yes |
| Self-hosted | ✅ Yes |
| OpenAI Evals Integration | ✅ Yes |

---

## 8. Scale AI Platform

**Provider**: Scale AI  
**Documentation**: https://scale.com/ai-evaluation-harness  
**Type**: Enterprise Platform

### Core Features

| Feature | Description |
|---------|-------------|
| Eval Harness | Pre-built evaluation frameworks |
| Data Annotation | Human annotation at scale |
| Model Fine-tuning | Quality-focused fine-tuning |
| Enterprise | SOC2, HIPAA compliant |

### Evaluation Areas

- **NLP**: Text classification, summarization, QA
- **Vision**: Image classification, object detection
- **Multimodal**: VLM evaluation

### Status

| Aspect | Status |
|--------|--------|
| API Available | ✅ Yes |
| Enterprise Focus | ✅ Yes |
| Free Tier | ❌ Enterprise only |
| Custom Evals | ✅ Yes |

---

## 9. LM Evaluation Harness

**Provider**: EleutherAI  
**Repository**: https://github.com/EleutherAI/lm-evaluation-harness  
**Documentation**: https://github.com/EleutherAI/lm-evaluation-harness#readme  
**Type**: Open Source

### Core Features

| Feature | Description |
|---------|-------------|
| Models | 200+ models supported |
| Tasks | 460+ benchmark tasks |
| Interface | CLI + Python API |
| Backends | HF, vLLM, SGLang, GPTQ |

### Quick Start

```bash
lm_eval --model hf \
    --model_args pretrained=gpt-j-6B \
    --tasks hellaswag \
    --device cuda:0 \
    --batch_size 8
```

### Supported Task Categories

- **Reasoning**: GSM8K, ARC, BOOLQ
- **Knowledge**: MMLU, TriviaQA
- **Code**: HumanEval, MBPP
- **Multilingual**: Belebele, xStoryCloze

### Status

| Aspect | Status |
|--------|--------|
| Open Source | ✅ Yes (Apache 2.0) |
| Free | ✅ Yes |
| GPU Support | ✅ Yes |
| API Models | ✅ Yes |

---

## 10. Academic Benchmarks

### 10.1 BIG-bench

**Provider**: Google, Stanford, MIT  
**Repository**: https://github.com/google/BIG-bench  
**Type**: Academic benchmark

| Metric | Description |
|--------|-------------|
| Task Coverage | 200+ tasks |
| Languages | 50+ languages |
| Evaluation | Token-based scoring |

### 10.2 HELM (Holistic Evaluation of Language Models)

**Provider**: Stanford CRFM  
**Repository**: https://github.com/stanford-crfm/helm  
**Type**: Academic benchmark

| Metric | Description |
|--------|-------------|
| Coverage | 42 scenarios |
| Metrics | Accuracy, robustness, fairness |
| Updates | Quarterly releases |

### 10.3 MMLU (Massive Multitask Language Understanding)

**Provider**: Multiple institutions  
**Type**: Academic benchmark

| Metric | Description |
|--------|-------------|
| Subjects | 57 domains |
| Questions | 15,908 questions |
| Accuracy | Single-model comparison |

---

## 11. Fiddler AI

**Provider**: Fiddler AI  
**Documentation**: https://www.fiddler.ai/model-monitoring  
**Type**: Enterprise Platform

### Core Features

| Feature | Description |
|---------|-------------|
| Model Monitoring | Production model performance |
| Drift Detection | Data and prediction drift |
| Explainability | Feature importance analysis |
| Compliance | Audit trail logging |

### Status

| Aspect | Status |
|--------|--------|
| Open Source | ❌ Proprietary |
| Enterprise | ✅ Yes |
| Free Tier | ⚠️ Limited |

---

## 12. MLflow Evaluation

**Provider**: Databricks (Apache 2.0)  
**Repository**: https://github.com/mlflow/mlflow  
**Documentation**: https://mlflow.org/docs/latest/models.html#evaluation  
**Type**: Open Source

### Core Features

| Feature | Description |
|---------|-------------|
| Evaluation API | Standardized model evaluation |
| Metrics | Built-in + custom metrics |
| UI Integration | MLflow tracking server |
| LLM Support | Chat model evaluation |

### Quick Start

```python
import mlflow

with mlflow.start_run():
    mlflow.evaluate(
        model="gpt-4",
        data=test_df,
        targets="ground_truth",
        model_type="text",
    )
```

### Status

| Aspect | Status |
|--------|--------|
| Open Source | ✅ Yes (Apache 2.0) |
| Free | ✅ Yes |
| Enterprise | ✅ Yes (Databricks) |

---

## Comparison Matrix

| Tool | Provider | Type | Free | API | Security | Multi-LLM |
|------|----------|------|------|-----|----------|-----------|
| **This Project** | Neo | Open Source | ✅ | ✅ | CWE-based | ✅ |
| OpenAI Evals | OpenAI | Cloud+OSS | ⚠️ Limited | ✅ | ❌ | ⚠️ |
| LangSmith | LangChain | Cloud | ⚠️ Limited | ✅ | ❌ | ✅ |
| Claude Eval | Anthropic | Platform | ❌ | ✅ | ✅ | ✅ |
| Vertex AI | Google | Enterprise | ❌ | ✅ | ✅ | ✅ |
| Azure AI | Microsoft | Enterprise | ❌ | ✅ | ✅ | ✅ |
| Arize Phoenix | Arize AI | OSS+Cloud | ✅ | ✅ | ❌ | ✅ |
| W&B | Weights & Biases | Cloud | ✅ | ✅ | ⚠️ | ✅ |
| Scale AI | Scale | Enterprise | ❌ | ✅ | ✅ | ✅ |
| LM Harness | EleutherAI | Open Source | ✅ | ⚠️ | ❌ | ❌ |
| MLflow | Databricks | Open Source | ✅ | ⚠️ | ❌ | ⚠️ |
| BIG-bench | Google | Academic | ✅ | ❌ | ❌ | ❌ |
| HELM | Stanford | Academic | ✅ | ❌ | ❌ | ❌ |

---

## Integration Guide

### Using External Tools for Comparison

When evaluating a skill with this project, you can also run external evaluations:

```python
# 1. Evaluate with this project
from skill.evaluator import Evaluator
result = Evaluator.evaluate("skill.md")
print(f"Internal Score: {result.f1}")

# 2. Compare with OpenAI Evals
# Upload same skill to OpenAI Eval API

# 3. Compare with LangSmith
# Run same dataset through LangSmith evaluator

# 4. Compare with LM Harness
# Evaluate underlying model with academic benchmarks

# 5. Cross-reference results
```

### Benchmarking Protocol

1. **Prepare Dataset**: Create JSONL with skill samples
2. **Run Internal Eval**: This project's evaluator
3. **Run External Evals**: OpenAI, LangSmith, LM Harness, etc.
4. **Calculate Correlation**: Compare scores across tools
5. **Report Discrepancies**: Flag divergent results for analysis

### Cross-Reference Methodology

| Step | Action |
|------|--------|
| 1 | Define gold standard dataset |
| 2 | Run this project's evaluation |
| 3 | Run external tool evaluation |
| 4 | Calculate score correlation |
| 5 | Analyze divergence cases |
| 6 | Adjust scoring if needed |

---

## References

### Commercial Platforms
- OpenAI Evals: https://platform.openai.com/docs/guides/evals
- LangSmith: https://docs.smith.langchain.com/evaluation
- Anthropic: https://docs.anthropic.com/en/docs/build-with-claude/evaluation
- Google Vertex AI: https://cloud.google.com/vertex-ai
- Azure AI Studio: https://azure.microsoft.com/products/ai-studio
- Arize AX: https://arize.com/generative-ai/
- Weights & Biases: https://wandb.ai
- Scale AI: https://scale.com

### Open Source Tools
- LM Evaluation Harness: https://github.com/EleutherAI/lm-evaluation-harness
- Arize Phoenix: https://github.com/Arize-ai/phoenix
- MLflow: https://github.com/mlflow/mlflow
- OpenAI Evals (Legacy): https://github.com/openai/evals

### Academic Benchmarks
- BIG-bench: https://github.com/google/BIG-bench
- HELM: https://github.com/stanford-crfm/helm
- MMLU: https://github.com/hendrycks/test

### Additional Resources
- LLM Evaluation Guide: https://arize.com/llm-evaluation/
- Weights & Biases Evals: https://docs.wandb.ai/guides/track/evals
- Prompt Engineering Guide: https://www.promptingguide.ai/evaluation
