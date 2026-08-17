"""
Central Rule Engine for NetSage AI.
Orchestrates execution of deterministic networking rules.
"""

from typing import Dict, Any, List, Optional, Callable
from .rule_models import RuleResult, RuleStatus
from .interface_rules import check_interface_down
from .ip_rules import check_duplicate_ip, check_subnet_mask, check_default_gateway
from .vlan_rules import check_missing_vlan
from .routing_rules import check_missing_route


class RuleChecker:
    """
    Central RuleChecker engine.
    Registers deterministic networking rules and executes them against evidence payloads.
    """

    def __init__(self):
        self._rules: Dict[str, Callable[[Dict[str, Any]], RuleResult]] = {}
        self._register_default_rules()

    def _register_default_rules(self):
        """Registers the six core Phase 3 deterministic rules."""
        self.register_rule("IF-001", check_interface_down)
        self.register_rule("IP-001", check_duplicate_ip)
        self.register_rule("IP-002", check_subnet_mask)
        self.register_rule("GW-001", check_default_gateway)
        self.register_rule("VLAN-001", check_missing_vlan)
        self.register_rule("ROUTE-001", check_missing_route)

    def register_rule(self, rule_id: str, rule_func: Callable[[Dict[str, Any]], RuleResult]):
        """Registers a custom or additional rule function."""
        self._rules[rule_id] = rule_func

    def get_registered_rules(self) -> List[str]:
        """Returns list of registered rule IDs."""
        return list(self._rules.keys())

    def run_rule(self, rule_id: str, evidence: Dict[str, Any]) -> RuleResult:
        """Executes a single specified rule by rule_id."""
        if rule_id not in self._rules:
            return RuleResult(
                rule_id=rule_id,
                rule_name="Unregistered Rule",
                status=RuleStatus.UNKNOWN,
                severity="Low",
                message=f"Rule ID '{rule_id}' is not registered in the engine.",
                evidence=f"Registered rules: {list(self._rules.keys())}",
                recommendation="Register rule handler before execution."
            )

        try:
            return self._rules[rule_id](evidence)
        except Exception as exc:
            # Graceful error handling for unexpected exceptions during evaluation
            return RuleResult(
                rule_id=rule_id,
                rule_name=f"Rule {rule_id}",
                status=RuleStatus.UNKNOWN,
                severity="Medium",
                message=f"Unhandled exception during rule execution: {str(exc)}",
                evidence=f"Exception type: {type(exc).__name__}",
                recommendation="Inspect evidence formatting and rule implementation."
            )

    def run_all(self, evidence: Dict[str, Any]) -> List[RuleResult]:
        """
        Executes all registered rules against the provided evidence dictionary.
        Returns a list of RuleResult objects.
        """
        results = []
        for rule_id in self._rules:
            result = self.run_rule(rule_id, evidence)
            results.append(result)
        return results

    def run_applicable(self, evidence: Dict[str, Any]) -> List[RuleResult]:
        """
        Executes all rules and returns only those that evaluate to PASS or FAIL
        (filtering out UNKNOWN results when evidence is irrelevant).
        """
        all_results = self.run_all(evidence)
        return [r for r in all_results if r.status != RuleStatus.UNKNOWN]
