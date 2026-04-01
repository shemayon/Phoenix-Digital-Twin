"""Pydantic schemas for the Gemini-style chat assistant."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .simulator import Severity


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    message: str
    asset_id: Optional[str] = Field(default=None, alias="assetId")
    tag_name: Optional[str] = Field(default=None, alias="tagName")
    severity: Optional[Severity] = None
    include_plan: bool = Field(default=True, alias="includePlan")


class ChatActionPlan(BaseModel):
    immediate_actions: List[str] = Field(default_factory=list, alias="immediateActions")
    long_term_actions: List[str] = Field(default_factory=list, alias="longTermActions")
    approvals_required: List[str] = Field(default_factory=list, alias="approvalsRequired")


class ChatResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    reply: str
    confidence: float = 0.6
    references: List[str] = Field(default_factory=list)
    suggested_faults: List[str] = Field(default_factory=list, alias="suggestedFaults")
    sop_links: List[str] = Field(default_factory=list, alias="sopLinks")
    recommended_actions: List[str] = Field(default_factory=list, alias="recommendedActions")
    action_plan: ChatActionPlan = Field(default_factory=ChatActionPlan, alias="actionPlan")


