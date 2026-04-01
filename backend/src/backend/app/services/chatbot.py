"""Gemini-powered chat service with retrieval over the IDSL payload."""

from __future__ import annotations

from dataclasses import dataclass, field
from textwrap import dedent
from typing import Dict, List, Optional
import json

import google.generativeai as genai

from ... import constants
from ..idsl.repository import IDSLRepository
from ..models.chat import ChatActionPlan, ChatRequest, ChatResponse
from ..models.simulator import PredictiveSuggestion, Severity, TwinSnapshot
from .simulator import SimPyDigitalTwinSimulator


@dataclass(slots=True)
class ChatContext:
    asset_name: Optional[str] = None
    asset_location: Optional[str] = None
    latest_alerts: List[str] = field(default_factory=list)
    predictive: List[PredictiveSuggestion] = field(default_factory=list)
    guidelines: Optional[str] = None
    sop_excerpt: Optional[str] = None
    maintenance_notes: List[str] = field(default_factory=list)


class GeminiChatService:
    """RAG-powered chatbot using Google Gemini to answer questions about the digital twin."""

    def __init__(self, repo: IDSLRepository, simulator: SimPyDigitalTwinSimulator) -> None:
        self.repo = repo
        self.simulator = simulator
        
        # Configure Gemini API
        genai.configure(api_key=constants.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(constants.GEMINI_MODEL)

    def generate_response(self, request: ChatRequest) -> ChatResponse:
        context = self._build_context(request)
        
        # Build RAG context for Gemini
        rag_context = self._build_rag_context(request, context)
        
        # Call Gemini with the user's question and context
        reply = self._call_gemini(request.message, rag_context)
        
        references = self._build_references(context)
        actions = self._extract_actions_from_reply(reply, context)
        action_plan = self._build_action_plan(context, actions)
        suggested_faults = [s.suggestion_id for s in context.predictive]
        sop_links = ["SOP Sample - VFD Troubleshooting"] if context.sop_excerpt else []

        return ChatResponse(
            reply=reply,
            confidence=0.85,
            references=references,
            suggestedFaults=suggested_faults,
            sopLinks=sop_links,
            recommendedActions=actions,
            actionPlan=action_plan,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _build_context(self, request: ChatRequest) -> ChatContext:
        snapshot = self.simulator.current_snapshot()
        asset = self._find_asset(request.asset_id, request.tag_name)

        latest_alerts = [alert.message for alert in snapshot.alerts][:5]
        predictive = self._filter_predictive(snapshot, request)
        guidelines = self.repo.guidelines()[0].content if self.repo.guidelines() else None
        sop_excerpt = self._prepare_sop_excerpt()
        maintenance_notes = self._matching_maintenance_records(asset, request.tag_name)

        return ChatContext(
            asset_name=asset.name if asset else None,
            asset_location=asset.location if asset else None,
            latest_alerts=latest_alerts,
            predictive=predictive,
            guidelines=guidelines,
            sop_excerpt=sop_excerpt,
            maintenance_notes=maintenance_notes,
        )

    def _find_asset(self, asset_id: Optional[str], tag_name: Optional[str]):
        assets = self.repo.assets()
        if asset_id:
            for asset in assets:
                if asset.asset_id.lower() == asset_id.lower():
                    return asset
        if tag_name:
            for asset in assets:
                if tag_name.lower().split("_")[0] in (asset.name or "").lower():
                    return asset
        return None

    def _filter_predictive(self, snapshot: TwinSnapshot, request: ChatRequest) -> List[PredictiveSuggestion]:
        if request.tag_name:
            return [
                suggestion
                for suggestion in snapshot.predictive_suggestions
                if request.tag_name.lower() in suggestion.description.lower()
            ] or snapshot.predictive_suggestions[:2]
        return snapshot.predictive_suggestions[:3]

    def _prepare_sop_excerpt(self) -> Optional[str]:
        if not self.repo.sop_documents():
            return None
        sop = self.repo.sop_documents()[0]
        return "\n".join(sop.content.splitlines()[:15])

    def _matching_maintenance_records(self, asset, tag_name: Optional[str]) -> List[str]:
        notes: List[str] = []
        for record in self.repo.maintenance_records():
            if asset and asset.location and record.area and asset.location.lower().split(",")[0] in record.area.lower():
                notes.append(f"{record.equipment}: {record.issue} -> {record.action_taken}")
            elif tag_name and record.equipment and tag_name.lower().split("_")[0] in record.equipment.lower():
                notes.append(f"{record.equipment}: {record.issue} -> {record.action_taken}")
        return notes[:5]

    def _compose_reply(self, request: ChatRequest, context: ChatContext) -> str:
        header = "Here's what I see." if context.latest_alerts else "No active alerts detected, but here's a readiness check."
        asset_line = (
            f"Asset **{context.asset_name}** at {context.asset_location} is under review."
            if context.asset_name
            else "Target asset not explicitly identified; using plant-wide insights."
        )

        alerts_block = "\n".join(f"- {alert}" for alert in context.latest_alerts) or "- No high-priority alarms right now."

        predictive_block = "\n".join(
            f"- {suggestion.title}: {suggestion.description}" for suggestion in context.predictive
        ) or "- No predictive advisories triggered."

        maintenance_block = (
            "\n".join(f"- {note}" for note in context.maintenance_notes)
            if context.maintenance_notes
            else "- No recent incident records tied to this scope."
        )

        recommendation_summary = dedent(
            f"""
            {header}
            {asset_line}

            **Live alerts**
            {alerts_block}

            **Predictive guidance**
            {predictive_block}

            **Historical notes**
            {maintenance_block}
            """
        ).strip()

        if context.sop_excerpt:
            recommendation_summary += "\n\n**SOP Extract**\n" + context.sop_excerpt

        return recommendation_summary

    def _build_rag_context(self, request: ChatRequest, context: ChatContext) -> str:
        """Build comprehensive context for RAG from IDSL and simulator state."""
        parts = []
        
        # Asset information
        if context.asset_name:
            # When specific asset is selected, show detailed information
            parts.append(f"**Target Asset:** {context.asset_name} at {context.asset_location}")
            
            # Find the full asset details
            asset = self._find_asset(request.asset_id, request.tag_name)
            if asset:
                parts.append("\n**Asset Details:**")
                if asset.status:
                    parts.append(f"- Status: {asset.status}")
                if asset.performance_pct is not None:
                    parts.append(f"- Performance: {asset.performance_pct}%")
                if asset.downtime_hours is not None:
                    parts.append(f"- Downtime: {asset.downtime_hours} hours")
                if asset.temperature_c is not None:
                    parts.append(f"- Temperature: {asset.temperature_c}°C")
                if asset.energy_usage_kwh is not None:
                    parts.append(f"- Energy Usage: {asset.energy_usage_kwh} kWh")
                if asset.last_maintenance:
                    parts.append(f"- Last Maintenance: {asset.last_maintenance.strftime('%Y-%m-%d')}")
                if asset.next_maintenance:
                    parts.append(f"- Next Maintenance: {asset.next_maintenance.strftime('%Y-%m-%d')}")
        else:
            # When no specific asset is selected, provide overview of all assets
            parts.append("**Scope:** Plant-wide analysis (All Assets)")
            parts.append("\n**Available Assets (Detailed):**")
            assets = self.repo.assets()
            for asset in assets[:15]:  # Increased to 15 assets
                parts.append(f"\n{asset.name} ({asset.asset_id}):")
                if asset.location:
                    parts.append(f"  • Location: {asset.location}")
                if asset.status:
                    parts.append(f"  • Status: {asset.status}")
                if asset.performance_pct is not None:
                    parts.append(f"  • Performance: {asset.performance_pct}%")
                if asset.downtime_hours is not None:
                    parts.append(f"  • Downtime: {asset.downtime_hours} hours")
                if asset.temperature_c is not None:
                    parts.append(f"  • Temperature: {asset.temperature_c}°C")
                if asset.energy_usage_kwh is not None:
                    parts.append(f"  • Energy Usage: {asset.energy_usage_kwh} kWh")
                if asset.last_maintenance:
                    parts.append(f"  • Last Maintenance: {asset.last_maintenance.strftime('%Y-%m-%d')}")
                if asset.next_maintenance:
                    parts.append(f"  • Next Maintenance: {asset.next_maintenance.strftime('%Y-%m-%d')}")
            
            # Add current snapshot summary
            snapshot = self.simulator.current_snapshot()
            if snapshot.kpis:
                parts.append("\n**Overall Plant KPIs:**")
                for kpi in snapshot.kpis:
                    parts.append(f"- {kpi.name}: {kpi.value}{kpi.unit or ''} (Status: {kpi.status})")
        
        # Current alerts
        if context.latest_alerts:
            parts.append("\n**Active Alerts:**")
            for alert in context.latest_alerts:
                parts.append(f"- {alert}")
        else:
            parts.append("\n**Active Alerts:** None")
        
        # Predictive suggestions
        if context.predictive:
            parts.append("\n**Predictive Maintenance Advisories:**")
            for suggestion in context.predictive:
                parts.append(f"- {suggestion.title}: {suggestion.description}")
                if suggestion.recommended_actions:
                    for action in suggestion.recommended_actions:
                        parts.append(f"  * {action}")
        
        # Historical maintenance records
        if context.maintenance_notes:
            parts.append("\n**Recent Maintenance History:**")
            for note in context.maintenance_notes[:3]:
                parts.append(f"- {note}")
        
        # SOP documentation
        if context.sop_excerpt:
            parts.append("\n**Relevant SOP Extract:**")
            parts.append(context.sop_excerpt)
        
        # Guidelines
        if context.guidelines:
            parts.append("\n**Guidelines:**")
            parts.append(context.guidelines[:500])  # Limit to 500 chars
        
        return "\n".join(parts)
    
    def _call_gemini(self, user_message: str, rag_context: str) -> str:
        """Call Gemini API with user question and RAG context."""
        system_prompt = (
            "You are Phoenix, an expert industrial AI assistant for a digital twin monitoring a manufacturing plant. "
            "Answer concisely in 2-4 sentences. Reference specific values from the provided data. "
            "If data is missing, say so briefly. Prioritize safety."
        )

        prompt = f"{system_prompt}\n\n**Plant Data:**\n{rag_context}\n\n**Question:** {user_message}\n\n**Answer (2-4 sentences):**"

        try:
            config = genai.GenerationConfig(max_output_tokens=200, temperature=0.4)
            response = self.model.generate_content(prompt, generation_config=config)
            return response.text.strip()
        except Exception:
            return self._compose_reply_fallback(user_message, rag_context)

    
    def _compose_reply_fallback(self, user_message: str, rag_context: str) -> str:
        """Fallback response if Gemini API fails."""
        return f"""I encountered an issue connecting to the AI service, but here's what I can share based on current data:

{rag_context}

**Regarding your question:** "{user_message}"

Please review the context above. For detailed troubleshooting, consult the SOP documentation or contact a supervisor."""
    
    def _extract_actions_from_reply(self, reply: str, context: ChatContext) -> List[str]:
        """Extract or generate recommended actions from the LLM reply or context."""
        actions: List[str] = []
        
        # Try to extract action items from the reply
        lines = reply.split('\n')
        in_action_section = False
        for line in lines:
            line_lower = line.lower().strip()
            if any(keyword in line_lower for keyword in ['action', 'step', 'recommend', 'should']):
                in_action_section = True
            if in_action_section and line.strip().startswith(('-', '*', '•', '1.', '2.', '3.')):
                action = line.strip().lstrip('-*•0123456789. ')
                if action and len(action) > 10:
                    actions.append(action)
        
        # If no actions extracted, fall back to context-based recommendations
        if not actions:
            if context.latest_alerts:
                actions.append("Acknowledge active alarms and document response in alert console.")
            if context.predictive:
                actions.append("Validate sensor readings against historian to confirm deviation persists.")
                actions.append("Check resource pool availability and align maintenance slot with production planner.")
            if context.sop_excerpt:
                actions.append("Follow SOP section: Diagnostic checks for VFD to confirm root cause.")
            actions.append("Log findings in compliance register and route for approver sign-off before execution.")
        
        return actions[:5]  # Limit to 5 actions

    def _build_references(self, context: ChatContext) -> List[str]:
        references: List[str] = []
        if context.asset_name:
            references.append(f"Asset Register > {context.asset_name}")
        if context.guidelines:
            references.append("Digital Twin Guidelines (IDSL)")
        if context.sop_excerpt:
            references.append("SOP Sample - VFD Troubleshooting")
        return references

    def _build_action_plan(self, context: ChatContext, actions: List[str]) -> ChatActionPlan:
        immediate = actions[:2]
        long_term = actions[2:] if len(actions) > 2 else [
            "Review long-term mitigation options with SME and update SOP repository."
        ]
        approvals = [
            "Maintenance Supervisor",
            "Compliance Officer",
        ]
        return ChatActionPlan(
            immediateActions=immediate,
            longTermActions=long_term,
            approvalsRequired=approvals,
        )


