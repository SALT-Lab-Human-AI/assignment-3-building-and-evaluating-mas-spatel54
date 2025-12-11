"""
Input Guardrail
Checks user inputs for safety violations.
"""

from typing import Dict, Any, List
import re
import logging


class InputGuardrail:
    """
    Guardrail for checking input safety.

    Implements comprehensive input validation including:
    - Length validation
    - Toxic language detection
    - Prompt injection detection
    - Topic relevance checking
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize input guardrail.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger("input_guardrail")

        # Configuration
        self.min_length = config.get("min_length", 5)
        self.max_length = config.get("max_length", 2000)
        self.topic = config.get("topic", "HCI Research")

        # Toxic language patterns (simple keyword-based approach)
        self.toxic_keywords = [
            "hate", "kill", "violence", "abuse", "offensive",
            "racist", "sexist", "discriminat"
        ]

        # Topic-relevant keywords for HCI research
        self.hci_keywords = [
            "user", "interface", "design", "usability", "ux", "ui",
            "interaction", "hci", "human", "computer", "experience",
            "accessibility", "prototype", "visualization", "mobile",
            "web", "app", "software", "system", "evaluation", "study"
        ]

    def validate(self, query: str) -> Dict[str, Any]:
        """
        Validate input query.

        Args:
            query: User input to validate

        Returns:
            Dictionary with validation results:
            - valid: Boolean indicating if query passed all checks
            - violations: List of validation violations
            - sanitized_input: Cleaned version of input
        """
        violations = []

        # Run all validation checks
        violations.extend(self._check_length(query))
        violations.extend(self._check_toxic_language(query))
        violations.extend(self._check_prompt_injection(query))
        violations.extend(self._check_relevance(query))

        # Determine validity
        is_valid = len(violations) == 0

        # Log violations
        if not is_valid:
            self.logger.warning(f"Input validation failed with {len(violations)} violations")
            for v in violations:
                self.logger.debug(f"  - {v['validator']}: {v['reason']}")

        return {
            "valid": is_valid,
            "violations": violations,
            "sanitized_input": query.strip()
        }

    def _check_length(self, query: str) -> List[Dict[str, Any]]:
        """
        Check if query length is within acceptable bounds.

        Args:
            query: Input query to check

        Returns:
            List of violations (empty if valid)
        """
        violations = []

        if len(query.strip()) < self.min_length:
            violations.append({
                "validator": "length",
                "reason": f"Query too short (min {self.min_length} characters)",
                "severity": "low"
            })

        if len(query) > self.max_length:
            violations.append({
                "validator": "length",
                "reason": f"Query too long (max {self.max_length} characters)",
                "severity": "medium"
            })

        return violations

    def _check_toxic_language(self, text: str) -> List[Dict[str, Any]]:
        """
        Check for toxic/harmful language.

        Args:
            text: Input text to check

        Returns:
            List of violations found
        """
        violations = []
        text_lower = text.lower()

        # Check for toxic keywords
        found_toxic = []
        for keyword in self.toxic_keywords:
            if keyword in text_lower:
                found_toxic.append(keyword)

        if found_toxic:
            violations.append({
                "validator": "toxic_language",
                "reason": f"Contains potentially toxic language: {', '.join(found_toxic)}",
                "severity": "high",
                "keywords": found_toxic
            })

        return violations

    def _check_prompt_injection(self, text: str) -> List[Dict[str, Any]]:
        """
        Check for prompt injection attempts.

        Args:
            text: Input text to check

        Returns:
            List of violations found
        """
        violations = []
        text_lower = text.lower()

        # Common prompt injection patterns
        injection_patterns = [
            "ignore previous instructions",
            "disregard",
            "forget everything",
            "system:",
            "sudo",
            "override",
            "jailbreak",
            "pretend you are",
            "act as",
            "role play"
        ]

        found_patterns = []
        for pattern in injection_patterns:
            if pattern in text_lower:
                found_patterns.append(pattern)

        if found_patterns:
            violations.append({
                "validator": "prompt_injection",
                "reason": f"Potential prompt injection detected: {', '.join(found_patterns)}",
                "severity": "high",
                "patterns": found_patterns
            })

        return violations

    def _check_relevance(self, query: str) -> List[Dict[str, Any]]:
        """
        Check if query is relevant to the system's purpose (HCI research).

        Args:
            query: Input query to check

        Returns:
            List of violations found
        """
        violations = []
        query_lower = query.lower()

        # Check if query contains any HCI-related keywords
        has_relevant_keyword = any(
            keyword in query_lower for keyword in self.hci_keywords
        )

        # Additional heuristic: check for question-like structure
        is_question = any(
            query.strip().startswith(q) or q in query_lower
            for q in ["what", "how", "why", "when", "where", "who", "which", "can", "does", "is", "are"]
        )

        # Only flag as off-topic if it's clearly not research-related
        # Be lenient - don't block queries that might be tangentially related
        if not has_relevant_keyword and len(query.split()) > 3:
            # Only flag longer queries that have no relevant keywords
            violations.append({
                "validator": "relevance",
                "reason": f"Query may not be relevant to {self.topic}",
                "severity": "low",  # Low severity - just a warning
                "suggestion": "Consider focusing on HCI, UX, or design-related topics"
            })

        return violations
