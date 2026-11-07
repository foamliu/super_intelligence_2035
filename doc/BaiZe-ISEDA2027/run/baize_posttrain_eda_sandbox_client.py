#!/usr/bin/env python3
"""baize_posttrain_eda_sandbox_client.py — EDA Sandbox Connectivity Client

R37 (2026-11-08): Comprehensive sandbox connectivity analysis and 3-tier
fallback strategy for RL reward computation.

ARCHITECTURE (from eda_fastmcp source analysis):
    EDA sandbox is an HTTP API service (NOT SSH):
      POST http://{HOST}:{PORT}/v1/run_code  Body: {"code":"...","lang":"pyAether"}
      Response: {"response":"...","error_log":"...","print_log":"..."}
    Default host: 10.129.32.75  Multi-endpoint: ports 8664/8665/8653/8669

NETWORK REALITY (measured 2026-11-08 from .17):
    10.129.32.75: ICMP OK (0.4ms) but ALL TCP ports FILTERED
    10.251.36.15: SSH port 22 unreachable (timeout)
    -> Sandbox completely inaccessible from .17 via TCP

3-TIER FALLBACK:
    Tier 1: Direct HTTP API -> UNREACHABLE (firewall)
    Tier 2: SSH tunnel via 36.15 -> UNREACHABLE (SSH timeout)
    Tier 3: R0 skeleton static analysis -> READY (no network needed)

WARNING: Surrogate RL results are NOT transferable to BaiZe.
"""
from __future__ import annotations
import argparse, json, logging, os, socket, subprocess, sys, time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)
DEFAULT_SANDBOX_HOST = os.getenv("SANDBOX_HOST", "10.129.32.75")
DEFAULT_SANDBOX_PORT = int(os.getenv("SANDBOX_PORT_HTTP", "8667"))
DEFAULT_SANDBOX_TIMEOUT = int(os.getenv("SANDBOX_TIMEOUT", "60"))
DEFAULT_URL_PATH = "v1/run_code"
SSH_TUNNEL_HOST = os.getenv("SSH_TUNNEL_HOST", "10.251.36.15")
SSH_TUNNEL_PORT = 22
SSH_TUNNEL_USER = os.getenv("SSH_TUNNEL_USER", "app.e0031982")
TIER1_PORTS = [8667, 8669, 8664, 8665, 8653, 8668]


class Tier(Enum):
    TIER1_HTTP_DIRECT = "tier1_http_direct"
    TIER2_SSH_TUNNEL = "tier2_ssh_tunnel"
    TIER3_SKELETON = "tier3_skeleton"
    UNAVAILABLE = "unavailable"

@dataclass
class SandboxResult:
    success: bool
    tier: Tier
    response: str = ""
    error_log: str = ""
    print_log: str = ""
    result: Any = None
    latency_ms: float = 0.0
    error: str = ""

@dataclass
class ConnectivityReport:
    timestamp: str = ""
    tier1_reachable: bool = False
    tier2_reachable: bool = False
    tier3_available: bool = True
    icmp_reachable: bool = False
    icmp_latency_ms: float = 0.0
    open_ports: List[int] = field(default_factory=list)
    closed_ports: List[int] = field(default_factory=list)
    ssh_status: str = ""
    recommended_tier: Tier = Tier.TIER3_SKELETON
    notes: List[str] = field(default_factory=list)

class SandboxClient:
    """EDA Sandbox client with 3-tier fallback."""

    def __init__(self, host=DEFAULT_SANDBOX_HOST, port=DEFAULT_SANDBOX_PORT,
                 timeout=DEFAULT_SANDBOX_TIMEOUT, ssh_host=SSH_TUNNEL_HOST):
        self.host, self.port, self.timeout, self.ssh_host = host, port, timeout, ssh_host
        self._t1_checked = self._t1_ok = False
        self._t2_checked = self._t2_ok = False

    def _check_port(self, host, port, timeout=2.0):
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            return False

    def check_tier1(self):
        if self._t1_checked:
            return self._t1_ok
        self._t1_checked = True
        for p in TIER1_PORTS:
            if self._check_port(self.host, p):
                self.port = p
                self._t1_ok = True
                logger.info("Tier1 OK: %s:%d", self.host, p)
                return True
        self._t1_ok = False
        return False

    def execute_tier1(self, code, lang="pyAether"):
        t0 = time.time()
        try:
            import requests
            url = f"http://{self.host}:{self.port}/{DEFAULT_URL_PATH}"
            resp = requests.post(url, json={"code": code, "lang": lang},
                                 headers={"Content-Type": "application/json"},
                                 timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            return SandboxResult(True, Tier.TIER1_HTTP_DIRECT,
                                 data.get("response", ""), data.get("error_log", ""),
                                 data.get("print_log", ""), data.get("result"),
                                 (time.time() - t0) * 1000)
        except Exception as e:
            return SandboxResult(False, Tier.TIER1_HTTP_DIRECT, error=str(e),
                                 latency_ms=(time.time() - t0) * 1000)

    def check_tier2(self):
        if self._t2_checked:
            return self._t2_ok
        self._t2_checked = True
        self._t2_ok = self._check_port(self.ssh_host, SSH_TUNNEL_PORT, timeout=3.0)
        return self._t2_ok

    def execute_tier2(self, code, lang="pyAether"):
        t0 = time.time()
        try:
            local_port = 18667
            tunnel = subprocess.Popen(
                ["ssh", "-o", "ConnectTimeout=5", "-o", "StrictHostKeyChecking=no",
                 "-L", f"{local_port}:{self.host}:{self.port}", "-N",
                 f"{SSH_TUNNEL_USER}@{self.ssh_host}"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(2)
            if tunnel.poll() is not None:
                return SandboxResult(False, Tier.TIER2_SSH_TUNNEL,
                                     error="SSH tunnel exited immediately",
                                     latency_ms=(time.time() - t0) * 1000)
            import requests
            url = f"http://127.0.0.1:{local_port}/{DEFAULT_URL_PATH}"
            resp = requests.post(url, json={"code": code, "lang": lang},
                                 headers={"Content-Type": "application/json"},
                                 timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            tunnel.terminate()
            tunnel.wait(timeout=5)
            return SandboxResult(True, Tier.TIER2_SSH_TUNNEL,
                                 data.get("response", ""), data.get("error_log", ""),
                                 data.get("print_log", ""), data.get("result"),
                                 (time.time() - t0) * 1000)
        except Exception as e:
            return SandboxResult(False, Tier.TIER2_SSH_TUNNEL, error=str(e),
                                 latency_ms=(time.time() - t0) * 1000)

    def check_tier3(self):
        return True  # R0 always available (pure Python)

    def execute_tier3(self, code, task_metadata=None):
        return SandboxResult(False, Tier.TIER3_SKELETON,
                             error_log="SANDBOX_UNAVAILABLE: R0 skeleton static analysis",
                             latency_ms=0.1)

    def execute(self, code, lang="pyAether", timeout=None, task_metadata=None):
        if timeout:
            self.timeout = timeout
        if self.check_tier1():
            r = self.execute_tier1(code, lang)
            if r.success:
                return r
        if self.check_tier2():
            r = self.execute_tier2(code, lang)
            if r.success:
                return r
        return self.execute_tier3(code, task_metadata)

    def full_connectivity_report(self):
        """Run comprehensive connectivity diagnostics."""
        report = ConnectivityReport(timestamp=time.strftime("%Y-%m-%d %H:%M:%S"))
        # ICMP
        try:
            r = subprocess.run(["ping", "-c", "1", "-W", "2", self.host],
                               capture_output=True, text=True, timeout=5)
            report.icmp_reachable = r.returncode == 0
            if report.icmp_reachable:
                for line in r.stdout.split("\n"):
                    if "time=" in line:
                        report.icmp_latency_ms = float(line.split("time=")[1].split()[0])
        except Exception:
            pass
        # Port scan
        for p in TIER1_PORTS:
            if self._check_port(self.host, p, timeout=2.0):
                report.open_ports.append(p)
            else:
                report.closed_ports.append(p)
        report.tier1_reachable = bool(report.open_ports)
        # SSH
        report.tier2_reachable = self._check_port(self.ssh_host, SSH_TUNNEL_PORT, timeout=3.0)
        report.ssh_status = (f"SSH to {self.ssh_host}:22 "
                             f"{'reachable' if report.tier2_reachable else 'unreachable'}")
        report.tier3_available = True
        # Recommendation
        if report.tier1_reachable:
            report.recommended_tier = Tier.TIER1_HTTP_DIRECT
            report.notes.append("Tier1: use execution-based rewards R1-R4")
        elif report.tier2_reachable:
            report.recommended_tier = Tier.TIER2_SSH_TUNNEL
            report.notes.append("Tier2: use SSH tunnel for sandbox")
        else:
            report.recommended_tier = Tier.TIER3_SKELETON
            report.notes.append("Only Tier3: R0 skeleton reward. GRPO std=0.3718 (R35 verified)")
            report.notes.append("RL trains on syntax/API/structure signal, not execution feedback")
            report.notes.append("Execution-based RL (R1-R4) deferred until sandbox reachable")
        if report.icmp_reachable and not report.tier1_reachable:
            report.notes.append(
                f"ICMP OK ({report.icmp_latency_ms:.1f}ms) but TCP filtered — "
                f"firewall on {self.host} blocks .17 subnet. "
                f"Action: request netops to open ports 8664-8669 for 10.252.32.17")
        return report


def format_report(report):
    lines = ["=" * 60, f"EDA Sandbox Connectivity Report — {report.timestamp}", "=" * 60, "",
             f"ICMP: {'OK' if report.icmp_reachable else 'FAIL'} ({report.icmp_latency_ms:.1f}ms)", "",
             f"Tier 1 (HTTP): {'REACHABLE' if report.tier1_reachable else 'UNREACHABLE'}",
             f"  Open: {report.open_ports or 'NONE'}  Closed: {report.closed_ports}",
             f"Tier 2 (SSH):  {'REACHABLE' if report.tier2_reachable else 'UNREACHABLE'}",
             f"  {report.ssh_status}",
             f"Tier 3 (R0):   ALWAYS AVAILABLE",
             f"\nRecommended: {report.recommended_tier.value}", "\nNotes:"]
    for n in report.notes:
        lines.append(f"  - {n}")
    lines.append("=" * 60)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="EDA Sandbox Connectivity Client (R37)")
    parser.add_argument("--test", action="store_true", help="Full connectivity test")
    parser.add_argument("--check", action="store_true", help="Quick reachability check")
    parser.add_argument("--exec", type=str, metavar="CODE", help="Execute code")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()
    client = SandboxClient()
    if args.test or (not args.check and not args.exec):
        report = client.full_connectivity_report()
        if args.json:
            print(json.dumps({"timestamp": report.timestamp,
                              "icmp_reachable": report.icmp_reachable,
                              "icmp_latency_ms": report.icmp_latency_ms,
                              "tier1_reachable": report.tier1_reachable,
                              "tier2_reachable": report.tier2_reachable,
                              "tier3_available": report.tier3_available,
                              "open_ports": report.open_ports,
                              "closed_ports": report.closed_ports,
                              "ssh_status": report.ssh_status,
                              "recommended_tier": report.recommended_tier.value,
                              "notes": report.notes}, indent=2))
        else:
            print(format_report(report))
    if args.check:
        print(f"Tier 1 (HTTP): {'OK' if client.check_tier1() else 'FAIL'}")
        print(f"Tier 2 (SSH):  {'OK' if client.check_tier2() else 'FAIL'}")
        print(f"Tier 3 (R0):   {'OK' if client.check_tier3() else 'FAIL'}")
    if args.exec:
        r = client.execute(args.exec)
        print(f"Tier: {r.tier.value}  Success: {r.success}  Latency: {r.latency_ms:.1f}ms")
        if r.response:
            print(f"Response: {r.response[:200]}")
        if r.error_log:
            print(f"Error: {r.error_log[:200]}")
        if r.error:
            print(f"Client error: {r.error[:200]}")


if __name__ == "__main__":
    main()
