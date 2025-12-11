"""
Safety Manager
Coordinates safety guardrails and logs safety events.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import json
import os

from .input_guardrail import InputGuardrail
from .output_guardrail import OutputGuardrail


class SafetyManager:
    """
    Manages safety guardrails for the multi-agent system.

    Coordinates input and output guardrails, logs safety events,
    and handles violations according to configured policies.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize safety manager.

        Args:
            config: Safety configuration dictionary
        """
        self.config = config
        self.enabled = config.get("enabled", True)
        self.log_events = config.get("log_events", True)
        self.logger = logging.getLogger("safety")

        # Safety event log
        self.safety_events: List[Dict[str, Any]] = []

        # Prohibited categories
        self.prohibited_categories = config.get("prohibited_categories", [
            "harmful_content",
            "personal_attacks",
            "misinformation",
            "off_topic_queries"
        ])

        # Violation response strategy
        self.on_violation = config.get("on_violation", {})

        # Initialize input and output guardrails
        if self.enabled:
            self.input_guardrail = InputGuardrail(config)
            self.output_guardrail = OutputGuardrail(config)
            self.logger.info("Safety guardrails initialized")
        else:
            self.input_guardrail = None
            self.output_guardrail = None
            self.logger.info("Safety guardrails disabled")

        # Ensure logs directory exists
        log_file = config.get("safety_log_file", "logs/safety_events.log")
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

    def check_input_safety(self, query: str) -> Dict[str, Any]:
        """
        Check if input query is safe to process.

        Args:
            query: User query to check

        Returns:
            Dictionary with:
            - safe: Boolean indicating if input is safe
            - violations: List of violations found
            - sanitized_input: Cleaned version of input (if applicable)
        """
        if not self.enabled or not self.input_guardrail:
            return {"safe": True, "violations": [], "sanitized_input": query}

        # Validate input using input guardrail
        result = self.input_guardrail.validate(query)

        is_safe = result["valid"]
        violations = result["violations"]

        # Log safety event if violations found
        if not is_safe and self.log_events:
            self._log_safety_event("input", query, violations, is_safe)

        return {
            "safe": is_safe,
            "violations": violations,
            "sanitized_input": result.get("sanitized_input", query)
        }

    def check_output_safety(self, response: str, sources: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Check if output response is safe to return.

        Args:
            response: Generated response to check
            sources: Optional list of sources used

        Returns:
            Dictionary with:
            - safe: Boolean indicating if output is safe
            - violations: List of violations found
            - response: Final response (sanitized or refused if unsafe)
        """
        if not self.enabled or not self.output_guardrail:
            return {"safe": True, "violations": [], "response": response}

        # Validate output using output guardrail
        result = self.output_guardrail.validate(response, sources)

        is_safe = result["valid"]
        violations = result["violations"]

        # Log safety event if violations found
        if not is_safe and self.log_events:
            self._log_safety_event("output", response, violations, is_safe)

        final_response = response

        # Apply violation handling strategy
        if not is_safe:
            action = self.on_violation.get("action", "sanitize")

            if action == "sanitize":
                final_response = result.get("sanitized_output", response)
                self.logger.info("Output sanitized due to safety violations")
            elif action == "refuse":
                final_response = self.on_violation.get(
                    "message",
                    "I cannot provide this response due to safety policies."
                )
                self.logger.warning("Output refused due to safety violations")
            else:  # "redirect" or other actions
                final_response = result.get("sanitized_output", response)

        return {
            "safe": is_safe,
            "violations": violations,
            "response": final_response
        }

    def _sanitize_response(self, response: str, violations: List[Dict[str, Any]]) -> str:
        """
        Sanitize response by removing or redacting unsafe content.

        Args:
            response: Original response
            violations: List of violations to sanitize

        Returns:
            Sanitized response

        Note: This method is deprecated - sanitization is now handled
        by the OutputGuardrail class directly.
        """
        # Delegate to output guardrail if available
        if self.output_guardrail:
            return self.output_guardrail._sanitize(response, violations)

        return response

    def _log_safety_event(
        self,
        event_type: str,
        content: str,
        violations: List[Dict[str, Any]],
        is_safe: bool
    ):
        """
        Log a safety event.

        Args:
            event_type: "input" or "output"
            content: The content that was checked
            violations: List of violations found
            is_safe: Whether content passed safety checks
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "safe": is_safe,
            "violations": violations,
            "content_preview": content[:100] + "..." if len(content) > 100 else content
        }

        self.safety_events.append(event)
        self.logger.warning(f"Safety event: {event_type} - safe={is_safe}")

        # Write to safety log file if configured
        log_file = self.config.get("safety_log_file")
        if log_file and self.log_events:
            try:
                with open(log_file, "a") as f:
                    f.write(json.dumps(event) + "\n")
            except Exception as e:
                self.logger.error(f"Failed to write safety log: {e}")

    def get_safety_events(self) -> List[Dict[str, Any]]:
        """Get all logged safety events."""
        return self.safety_events

    def get_safety_stats(self) -> Dict[str, Any]:
        """
        Get statistics about safety events.

        Returns:
            Dictionary with safety statistics
        """
        total = len(self.safety_events)
        input_events = sum(1 for e in self.safety_events if e["type"] == "input")
        output_events = sum(1 for e in self.safety_events if e["type"] == "output")
        violations = sum(1 for e in self.safety_events if not e["safe"])

        return {
            "total_events": total,
            "input_checks": input_events,
            "output_checks": output_events,
            "violations": violations,
            "violation_rate": violations / total if total > 0 else 0
        }

    def clear_events(self):
        """Clear safety event log."""
        self.safety_events = []
