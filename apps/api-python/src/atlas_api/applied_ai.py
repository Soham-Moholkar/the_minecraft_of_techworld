"""Typed evidence for the bounded Phase 7 applied-AI compatibility suite."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from atlas_api.machine_learning import TrainingPoint

TaskName = Literal["computer_vision", "time_series", "nlp_attention", "recommendation"]


class AppliedExperimentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    name: str = Field(min_length=2, max_length=120)


class AppliedTaskEvidence(BaseModel):
    task: TaskName
    architecture: str = Field(min_length=2, max_length=80)
    baseline: str = Field(min_length=2, max_length=80)
    metric: Literal["accuracy", "mae", "hit_rate_at_3"]
    higher_is_better: bool
    model_score: float = Field(allow_inf_nan=False)
    baseline_score: float = Field(allow_inf_nan=False)
    training_curve: list[TrainingPoint] = Field(min_length=1, max_length=60)
    train_examples: int = Field(gt=0, le=1000)
    test_examples: int = Field(gt=0, le=1000)

    @model_validator(mode="after")
    def score_domain(self) -> "AppliedTaskEvidence":
        if self.metric in {"accuracy", "hit_rate_at_3"} and not (
            0 <= self.model_score <= 1 and 0 <= self.baseline_score <= 1
        ):
            raise ValueError("classification and ranking scores must be rates")
        if self.metric == "mae" and min(self.model_score, self.baseline_score) < 0:
            raise ValueError("MAE cannot be negative")
        return self


class AppliedReport(BaseModel):
    suite: Literal["phase7_applied_ai"] = "phase7_applied_ai"
    random_seed: Literal[42] = 42
    torch_version: str
    tasks: list[AppliedTaskEvidence] = Field(min_length=4, max_length=4)
    caveats: list[str] = Field(min_length=1, max_length=8)

    @model_validator(mode="after")
    def complete_suite(self) -> "AppliedReport":
        expected: set[TaskName] = {
            "computer_vision",
            "time_series",
            "nlp_attention",
            "recommendation",
        }
        if {task.task for task in self.tasks} != expected:
            raise ValueError("applied AI suite is incomplete")
        return self


class AppliedExperimentSummary(BaseModel):
    id: UUID
    name: str
    created_at: datetime
    tasks: int
    improved_tasks: int


class AppliedExperimentRead(AppliedExperimentSummary):
    report: AppliedReport
