"""
Output Guardrail
Checks system outputs for safety violations.
"""

from typing import Dict, Any, List
import re
import logging


class OutputGuardrail:
    """
    Guardrail for checking output safety.

    Implements comprehensive output validation including:
    - PII detection and redaction
    - Harmful content detection
    - Bias detection
    - Citation verification
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize output guardrail.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger("output_guardrail")

        # Harmful content keywords
        self.harmful_keywords = [
            "violent", "harmful", "dangerous", "illegal", "weapon",
            "drug", "explosive", "poison", "hack", "steal"
        ]

        # Bias-related terms to flag
        self.bias_keywords = [
            "always", "never", "all", "none", "every", "only",
            "obviously", "clearly", "undoubtedly"
        ]

    def validate(self, response: str, sources: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Validate output response.

        Args:
            response: Generated response to validate
            sources: Optional list of sources used (for fact-checking)

        Returns:
            Dictionary with validation results:
            - valid: Boolean indicating if response passed all checks
            - violations: List of validation violations
            - sanitized_output: Cleaned version of response
        """
        violations = []

        # Run all validation checks
        violations.extend(self._check_pii(response))
        violations.extend(self._check_harmful_content(response))
        violations.extend(self._check_bias(response))

        if sources:
            violations.extend(self._check_factual_consistency(response, sources))

        is_valid = len(violations) == 0

        # Log violations
        if not is_valid:
            self.logger.warning(f"Output validation failed with {len(violations)} violations")
            for v in violations:
                self.logger.debug(f"  - {v['validator']}: {v['reason']}")

        return {
            "valid": is_valid,
            "violations": violations,
            "sanitized_output": self._sanitize(response, violations) if violations else response
        }

    def _check_pii(self, text: str) -> List[Dict[str, Any]]:
        """
        Check for personally identifiable information.

        Args:
            text: Output text to check

        Returns:
            List of PII violations found
        """
        violations = []

        # Regex patterns for common PII
        patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b(?:\+?1[-.]?)?\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
            "credit_card": r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            "ip_address": r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        }

        for pii_type, pattern in patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                violations.append({
                    "validator": "pii",
                    "pii_type": pii_type,
                    "reason": f"Contains {pii_type}",
                    "severity": "high",
                    "matches": matches
                })

        return violations

    def _check_harmful_content(self, text: str) -> List[Dict[str, Any]]:
        """
        Check for harmful or inappropriate content.

        Args:
            text: Output text to check

        Returns:
            List of harmful content violations found
        """
        violations = []
        text_lower = text.lower()

        # Check for harmful keywords
        found_harmful = []
        for keyword in self.harmful_keywords:
            if keyword in text_lower:
                found_harmful.append(keyword)

        if found_harmful:
            violations.append({
                "validator": "harmful_content",
                "reason": f"May contain harmful content: {', '.join(found_harmful)}",
                "severity": "medium",
                "keywords": found_harmful
            })

        return violations

    def _check_factual_consistency(
        self,
        response: str,
        sources: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Check if response is consistent with sources.

        Args:
            response: Generated response
            sources: List of sources used

        Returns:
            List of consistency violations found

        Note: This is a basic implementation. A production system
        would use LLM-based verification for better accuracy.
        """
        violations = []

        # Basic check: ensure response has citations if sources were provided
        if sources and len(sources) > 0:
            # Look for citation markers (common patterns)
            has_citations = any([
                '(' in response and ')' in response,  # (Author, Year)
                '[' in response and ']' in response,  # [1], [Source]
                'http://' in response or 'https://' in response,  # URLs
                'et al' in response.lower(),  # Academic citations
            ])

            if not has_citations:
                violations.append({
                    "validator": "factual_consistency",
                    "reason": "Response lacks citations despite sources being available",
                    "severity": "low",
                    "suggestion": "Ensure claims are properly cited"
                })

        return violations

    def _check_bias(self, text: str) -> List[Dict[str, Any]]:
        """
        Check for biased language.

        Args:
            text: Output text to check

        Returns:
            List of bias violations found
        """
        violations = []
        text_lower = text.lower()

        # Check for absolutist language that may indicate bias
        found_bias = []
        for keyword in self.bias_keywords:
            # Use word boundaries to avoid false positives
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text_lower):
                found_bias.append(keyword)

        # Only flag if multiple bias indicators are present
        if len(found_bias) >= 3:
            violations.append({
                "validator": "bias",
                "reason": f"Response contains absolutist language: {', '.join(found_bias[:3])}",
                "severity": "low",
                "keywords": found_bias,
                "suggestion": "Consider using more nuanced language"
            })

        return violations

    def _sanitize(self, text: str, violations: List[Dict[str, Any]]) -> str:
        """
        Sanitize text by removing/redacting violations.

        Args:
            text: Original text
            violations: List of violations to sanitize

        Returns:
            Sanitized text with violations redacted
        """
        sanitized = text

        # Redact PII
        for violation in violations:
            if violation.get("validator") == "pii":
                pii_type = violation.get("pii_type", "PII")
                for match in violation.get("matches", []):
                    sanitized = sanitized.replace(match, f"[{pii_type.upper()}_REDACTED]")

        # Note: For harmful content and bias, we log but don't auto-sanitize
        # as it requires human judgment or more sophisticated NLP

        return sanitized
