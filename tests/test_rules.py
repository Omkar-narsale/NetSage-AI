"""
Unit Test Suite for NetSage AI Deterministic Rule Engine.
Tests all 6 core rules across PASS, FAIL, and UNKNOWN evaluation states.
"""

import unittest
from rules.checker import RuleChecker
from rules.rule_models import RuleStatus, RuleResult
from rules.interface_rules import check_interface_down
from rules.ip_rules import check_duplicate_ip, check_subnet_mask, check_default_gateway
from rules.vlan_rules import check_missing_vlan
from rules.routing_rules import check_missing_route


class TestInterfaceRules(unittest.TestCase):
    """Test suite for Rule IF-001: Interface Down Check."""

    def test_if001_fail_admin_down(self):
        evidence = {
            "interfaces": [
                {"name": "GigabitEthernet0/0", "status": "up", "protocol": "up"},
                {"name": "GigabitEthernet0/1", "status": "administratively down", "protocol": "down"}
            ]
        }
        res = check_interface_down(evidence)
        self.assertEqual(res.status, RuleStatus.FAIL)
        self.assertEqual(res.rule_id, "IF-001")
        self.assertIn("GigabitEthernet0/1", res.message)

    def test_if001_pass_all_up(self):
        evidence = {
            "interfaces": [
                {"name": "GigabitEthernet0/0", "status": "up", "protocol": "up"},
                {"name": "GigabitEthernet0/1", "status": "up", "protocol": "up"}
            ]
        }
        res = check_interface_down(evidence)
        self.assertEqual(res.status, RuleStatus.PASS)

    def test_if001_unknown_missing_data(self):
        evidence = {}
        res = check_interface_down(evidence)
        self.assertEqual(res.status, RuleStatus.UNKNOWN)


class TestDuplicateIPRules(unittest.TestCase):
    """Test suite for Rule IP-001: Duplicate IP Check."""

    def test_ip001_fail_duplicate(self):
        evidence = {
            "hosts": [
                {"device": "PC-1", "ip": "192.168.1.10"},
                {"device": "PC-2", "ip": "192.168.1.10"}
            ]
        }
        res = check_duplicate_ip(evidence)
        self.assertEqual(res.status, RuleStatus.FAIL)
        self.assertIn("192.168.1.10", res.message)
        self.assertIn("PC-1", res.message)

    def test_ip001_pass_unique(self):
        evidence = {
            "hosts": [
                {"device": "PC-1", "ip": "192.168.1.10"},
                {"device": "PC-2", "ip": "192.168.1.20"}
            ]
        }
        res = check_duplicate_ip(evidence)
        self.assertEqual(res.status, RuleStatus.PASS)

    def test_ip001_unknown_no_data(self):
        evidence = {"hosts": []}
        res = check_duplicate_ip(evidence)
        self.assertEqual(res.status, RuleStatus.UNKNOWN)


class TestSubnetRules(unittest.TestCase):
    """Test suite for Rule IP-002: Wrong Subnet Mask Check."""

    def test_ip002_pass_correct_subnet(self):
        evidence = {
            "host_ip": "192.168.10.25",
            "subnet_mask": "255.255.255.0",
            "expected_subnet": "192.168.10.0/24"
        }
        res = check_subnet_mask(evidence)
        self.assertEqual(res.status, RuleStatus.PASS)

    def test_ip002_fail_wrong_subnet(self):
        evidence = {
            "host_ip": "192.168.10.25",
            "subnet_mask": "255.255.255.0",
            "expected_subnet": "192.168.20.0/24"
        }
        res = check_subnet_mask(evidence)
        self.assertEqual(res.status, RuleStatus.FAIL)
        self.assertIn("outside expected subnet", res.message)

    def test_ip002_unknown_missing_info(self):
        evidence = {"host_ip": "192.168.10.25"}
        res = check_subnet_mask(evidence)
        self.assertEqual(res.status, RuleStatus.UNKNOWN)


class TestGatewayRules(unittest.TestCase):
    """Test suite for Rule GW-001: Default Gateway Mismatch Check."""

    def test_gw001_pass_correct_gateway(self):
        evidence = {
            "host_ip": "192.168.1.20",
            "subnet_mask": "255.255.255.0",
            "default_gateway": "192.168.1.1",
            "expected_gateway_ip": "192.168.1.1"
        }
        res = check_default_gateway(evidence)
        self.assertEqual(res.status, RuleStatus.PASS)

    def test_gw001_fail_outside_subnet(self):
        evidence = {
            "host_ip": "192.168.1.20",
            "subnet_mask": "255.255.255.0",
            "default_gateway": "192.168.2.1"
        }
        res = check_default_gateway(evidence)
        self.assertEqual(res.status, RuleStatus.FAIL)
        self.assertIn("outside host subnet", res.message)

    def test_gw001_fail_mismatched_router_ip(self):
        evidence = {
            "host_ip": "192.168.1.20",
            "subnet_mask": "255.255.255.0",
            "default_gateway": "192.168.1.254",
            "expected_gateway_ip": "192.168.1.1"
        }
        res = check_default_gateway(evidence)
        self.assertEqual(res.status, RuleStatus.FAIL)
        self.assertIn("does not match expected router gateway IP", res.message)

    def test_gw001_unknown_missing_gateway(self):
        evidence = {"host_ip": "192.168.1.20"}
        res = check_default_gateway(evidence)
        self.assertEqual(res.status, RuleStatus.UNKNOWN)


class TestVlanRules(unittest.TestCase):
    """Test suite for Rule VLAN-001: Missing VLAN Check."""

    def test_vlan001_pass_exists(self):
        evidence = {
            "required_vlan": 30,
            "vlans": [10, 20, 30]
        }
        res = check_missing_vlan(evidence)
        self.assertEqual(res.status, RuleStatus.PASS)

    def test_vlan001_fail_missing(self):
        evidence = {
            "required_vlan": 30,
            "vlans": [10, 20]
        }
        res = check_missing_vlan(evidence)
        self.assertEqual(res.status, RuleStatus.FAIL)
        self.assertIn("Required VLAN 30 is missing", res.message)

    def test_vlan001_unknown_no_evidence(self):
        evidence = {"required_vlan": 30}
        res = check_missing_vlan(evidence)
        self.assertEqual(res.status, RuleStatus.UNKNOWN)


class TestRoutingRules(unittest.TestCase):
    """Test suite for Rule ROUTE-001: Missing Route Check."""

    def test_route001_pass_exists(self):
        evidence = {
            "required_destination": "10.10.20.0/24",
            "routes": ["10.10.10.0/24", "10.10.20.0/24", "192.168.1.0/24"]
        }
        res = check_missing_route(evidence)
        self.assertEqual(res.status, RuleStatus.PASS)

    def test_route001_fail_missing(self):
        evidence = {
            "required_destination": "10.10.20.0/24",
            "routes": ["10.10.10.0/24", "192.168.1.0/24"]
        }
        res = check_missing_route(evidence)
        self.assertEqual(res.status, RuleStatus.FAIL)
        self.assertIn("missing a route for destination 10.10.20.0/24", res.message)

    def test_route001_unknown_no_routes(self):
        evidence = {"required_destination": "10.10.20.0/24"}
        res = check_missing_route(evidence)
        self.assertEqual(res.status, RuleStatus.UNKNOWN)


class TestRuleCheckerEngine(unittest.TestCase):
    """Test suite for RuleChecker orchestration engine."""

    def setUp(self):
        self.checker = RuleChecker()

    def test_registered_rules(self):
        rules = self.checker.get_registered_rules()
        self.assertIn("IF-001", rules)
        self.assertIn("IP-001", rules)
        self.assertIn("IP-002", rules)
        self.assertIn("GW-001", rules)
        self.assertIn("VLAN-001", rules)
        self.assertIn("ROUTE-001", rules)

    def test_run_all_returns_six_results(self):
        evidence = {
            "required_vlan": 30,
            "vlans": [10, 20]
        }
        results = self.checker.run_all(evidence)
        self.assertEqual(len(results), 6)
        vlan_res = next(r for r in results if r.rule_id == "VLAN-001")
        self.assertEqual(vlan_res.status, RuleStatus.FAIL)

    def test_run_applicable(self):
        evidence = {
            "required_vlan": 30,
            "vlans": [10, 20]
        }
        applicable = self.checker.run_applicable(evidence)
        self.assertTrue(all(r.status != RuleStatus.UNKNOWN for r in applicable))
        self.assertTrue(any(r.rule_id == "VLAN-001" for r in applicable))


if __name__ == "__main__":
    unittest.main()
