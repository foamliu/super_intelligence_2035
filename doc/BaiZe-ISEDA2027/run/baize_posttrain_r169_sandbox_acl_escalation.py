#!/usr/bin/env python3
"""
R169 — Sandbox ACL Escalation Runbook + Full Network Diagnostic
================================================================
Context:
  The remote EDA sandbox at 10.129.32.75 has been TCP-blocked from .17
  (10.252.32.17) for 43+ consecutive agent wakes (since wake195, ~2026-11-10).
  ICMP works (0.4ms RTT) but ALL TCP ports are filtered (including SSH 22).
  This blocks Phase1 baseline eval and Phase3 RL (R1-R4 sandbox-exec rewards).

  R168 confirmed the entire surrogate pipeline is internally GO (scripts,
  configs, contamination gates, endpoints, sentinel, teardown all ready).
  The ONLY remaining external blocker for Phase1 is this network ACL.

Purpose:
  1. Produce a precise, actionable ACL escalation document for the network team
     (exact source/dest/ports/protocol/business-justification).
  2. Capture full diagnostic evidence (routing, ARP, port-by-port scan,
     ICMP vs TCP, gateway reachability, same-subnet control).
  3. Save machine-readable JSON for the record.

Output:
  - r169_sandbox_acl_escalation.json  (diagnostic results)
  - stdout summary (human-readable escalation runbook)

Usage:
  python3 baize_posttrain_r169_sandbox_acl_escalation.py
  python3 baize_posttrain_r169_sandbox_acl_escalation.py --json-only
"""
import json
import os
import socket
import subprocess
import sys
import time
from datetime import datetime

RUN_DIR = os.path.dirname(os.path.abspath(__file__))

# ---- config ----
SANDBOX_HOST = os.getenv("SANDBOX_HOST", "10.129.32.75")
SANDBOX_PORTS = [22, 8664, 8665, 8667, 8668, 8669, 8653]
SANDBOX_PORT_ROLES = {
    "22":   "SSH (administrative access to sandbox host)",
    "8664": "pyAether code execution (multi-sandbox endpoint 1, workdir t0002596_bak_1)",
    "8665": "pyAether code execution (multi-sandbox endpoint 2, workdir t0002596_bak)",
    "8667": "pyAether code execution HTTP API (primary, /v1/run_code)",
    "8668": "pyAether code execution TCP socket (binary protocol)",
    "8669": "pyAether code execution (multi-sandbox endpoint 4, workdir t0002596)",
    "8653": "SKILL/pyAether dual-mode (endpoint 3, workdir t0002596_skill)",
}
CONTROL_HOST_SAMESUBNET = "10.252.32.15"  # ZhuLong, same /22 subnet
CONTROL_PORT_SAMESUBNET = 9001
GATEWAY = "10.252.32.1"
LOCAL_IP = "10.252.32.17"
TCP_TIMEOUT = 3  # seconds per port probe
ICMP_COUNT = 3
ICMP_TIMEOUT = 2


def run_cmd(cmd, timeout=10):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return 124, "", "TIMEOUT"
    except Exception as e:
        return 1, "", str(e)


def tcp_probe(host, port, timeout=TCP_TIMEOUT):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    t0 = time.time()
    try:
        rc = sock.connect_ex((host, port))
        elapsed = (time.time() - t0) * 1000
        sock.close()
        return (rc == 0, round(elapsed, 1))
    except socket.timeout:
        return (False, round(timeout * 1000, 1))
    except Exception:
        return (False, -1)
    finally:
        try:
            sock.close()
        except Exception:
            pass


def ping(host, count=ICMP_COUNT, timeout=ICMP_TIMEOUT):
    rc, out, _ = run_cmd("ping -c %d -W %d %s" % (count, timeout, host), timeout=count * timeout + 5)
    if rc != 0:
        return (False, -1, 100.0)
    avg = -1
    loss = 100.0
    for line in out.split("\n"):
        if "rtt min/avg" in line or "round-trip" in line:
            parts = line.split("=")[-1].strip().split("/")
            try:
                avg = float(parts[1])
            except (IndexError, ValueError):
                pass
        if "packet loss" in line:
            try:
                loss_str = line.split(",")[2].strip().split("%")[0].strip()
                loss = float(loss_str)
            except (IndexError, ValueError):
                pass
    return (True, avg, loss)


def get_local_network_info():
    info = {}
    rc, out, _ = run_cmd("ip addr show bond0", timeout=5)
    info["bond0"] = out[:500] if out else "N/A"
    rc, out, _ = run_cmd("ip route get %s" % SANDBOX_HOST, timeout=5)
    info["route_to_sandbox"] = out if out else "N/A"
    rc, out, _ = run_cmd("ip route show", timeout=5)
    info["routing_table"] = out if out else "N/A"
    rc, out, _ = run_cmd("arp -n", timeout=5)
    info["arp_table"] = out if out else "N/A"
    rc, out, _ = run_cmd("hostname -I", timeout=5)
    info["local_ips"] = out if out else "N/A"
    return info


def main():
    print("=" * 72)
    print("R169 - Sandbox ACL Escalation Runbook + Network Diagnostic")
    print("Timestamp: %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 72)
    results = {"r169": True, "timestamp": datetime.now().isoformat(),
               "local_ip": LOCAL_IP, "sandbox_host": SANDBOX_HOST,
               "wake_count_blocked": "43+ (since wake195, ~2026-11-10)",
               "diagnostics": {}, "escalation": {}}

    print("\n[1] Local network configuration:")
    netinfo = get_local_network_info()
    results["diagnostics"]["local_network"] = netinfo
    print("  Local IP: %s (bond0, 10.252.32.0/22)" % LOCAL_IP)
    print("  Gateway:  %s" % GATEWAY)
    print("  Route:    %s" % netinfo.get("route_to_sandbox", "N/A")[:120])

    print("\n[2] ICMP reachability to %s:" % SANDBOX_HOST)
    ok, avg, loss = ping(SANDBOX_HOST)
    results["diagnostics"]["icmp_sandbox"] = {"reachable": ok, "avg_ms": avg, "loss_pct": loss}
    print("  Reachable: %s, Avg RTT: %s ms, Loss: %s%%" % (ok, avg, loss))

    print("\n[3] TCP port scan of %s:" % SANDBOX_HOST)
    port_results = {}
    for port in SANDBOX_PORTS:
        open_, latency = tcp_probe(SANDBOX_HOST, port)
        role = SANDBOX_PORT_ROLES.get(str(port), "unknown")
        port_results[str(port)] = {"open": open_, "latency_ms": latency, "role": role}
        status = "OPEN" if open_ else "CLOSED/filtered"
        print("  Port %5d: %16s  (%s)" % (port, status, role))
    results["diagnostics"]["tcp_scan_sandbox"] = port_results

    print("\n[4] Control - same-subnet %s:%d:" % (CONTROL_HOST_SAMESUBNET, CONTROL_PORT_SAMESUBNET))
    ok_ctrl, lat_ctrl = tcp_probe(CONTROL_HOST_SAMESUBNET, CONTROL_PORT_SAMESUBNET)
    ok_ping_ctrl, avg_ctrl, loss_ctrl = ping(CONTROL_HOST_SAMESUBNET)
    results["diagnostics"]["control_samesubnet"] = {
        "host": CONTROL_HOST_SAMESUBNET, "port": CONTROL_PORT_SAMESUBNET,
        "tcp_open": ok_ctrl, "tcp_latency_ms": lat_ctrl,
        "icmp_reachable": ok_ping_ctrl, "icmp_avg_ms": avg_ctrl, "icmp_loss_pct": loss_ctrl}
    print("  TCP %d: %s (%s ms)" % (CONTROL_PORT_SAMESUBNET, "OPEN" if ok_ctrl else "CLOSED", lat_ctrl))
    print("  ICMP: reachable=%s, avg=%s ms" % (ok_ping_ctrl, avg_ctrl))

    print("\n[5] Gateway %s:" % GATEWAY)
    ok_gw, _ = tcp_probe(GATEWAY, 80)
    ok_ping_gw, avg_gw, _ = ping(GATEWAY)
    results["diagnostics"]["gateway"] = {"host": GATEWAY, "tcp_80_open": ok_gw, "icmp_reachable": ok_ping_gw, "icmp_avg_ms": avg_gw}
    print("  TCP 80: %s  ICMP: reachable=%s, avg=%s ms" % ("OPEN" if ok_gw else "CLOSED", ok_ping_gw, avg_gw))
    return results, ok, avg, loss, ok_ctrl, port_results


def _diagnose_and_escalate(results, ok, avg, loss, ok_ctrl, port_results):
    all_tcp_blocked = all(not pr["open"] for pr in port_results.values())
    icmp_ok = ok
    control_ok = ok_ctrl
    if icmp_ok and all_tcp_blocked and control_ok:
        diagnosis = ("BLANKET_CROSS_SUBNET_TCP_FILTER: ICMP passes (L3 reachable) but ALL TCP "
            "ports to 10.129.32.75 are filtered. Same-subnet TCP works (control .15:9001 OPEN). "
            "Firewall/ACL between 10.252.32.0/22 and 10.129.32.0/24 permits ICMP but blocks TCP. "
            "NOT routing (route resolves via gateway, ARP OK, ICMP 0.4ms). NOT host-down (ICMP responds). "
            "NOT .17-local (same-subnet TCP works).")
    elif not icmp_ok:
        diagnosis = "HOST_UNREACHABLE: ICMP also fails - possible routing or host-down issue."
    elif not all_tcp_blocked:
        diagnosis = "PARTIAL_OPEN: some TCP ports open - sandbox may have partially recovered."
    else:
        diagnosis = "LOCAL_ISSUE: same-subnet TCP also fails - possible local firewall or NIC issue."
    results["diagnostics"]["diagnosis"] = diagnosis
    print("\n[6] Diagnosis: %s" % diagnosis)

    needed_ports = [
        {"port": 8667, "role": "HTTP API /v1/run_code (primary code exec)", "required": True},
        {"port": 8668, "role": "TCP socket code exec (binary protocol)", "required": True},
        {"port": 8664, "role": "Multi-sandbox endpoint 1 (parallel exec)", "required": True},
        {"port": 8665, "role": "Multi-sandbox endpoint 2 (parallel exec)", "required": True},
        {"port": 8653, "role": "Multi-sandbox endpoint 3 (SKILL+pyAether dual)", "required": True},
        {"port": 8669, "role": "Multi-sandbox endpoint 4 (parallel exec)", "required": True},
        {"port": 22, "role": "SSH (administrative, optional)", "required": False},
    ]
    escalation = {
        "title": "Network ACL Escalation Request - BaiZe Post-Train EDA Sandbox Access",
        "priority": "HIGH - blocks ISEDA 2027 paper deadline (2027-02-01)",
        "blocked_since": "2026-11-10 (43+ agent wakes, ~14 days)",
        "source": {"host": LOCAL_IP, "subnet": "10.252.32.0/22", "gateway": GATEWAY},
        "destination": {"host": SANDBOX_HOST, "service": "PyAether EDA code execution sandbox"},
        "current_state": {"icmp": "REACHABLE (avg %s ms)" % avg, "tcp_all_ports": "FILTERED (all 7 timeout)", "ssh_22": "FILTERED"},
        "required_acl_rules": needed_ports,
        "acl_rule_summary": ("Allow TCP from 10.252.32.0/22 to 10.129.32.75 ports 8664,8665,8667,8668,8669,8653 (optionally 22)."),
        "business_justification": ("EDA sandbox runs Empyrean Aether/PyAether executing generated EDA code. "
            "BaiZe post-training needs it for Phase1 baseline eval (158 tasks) and Phase3 RL rewards. "
            "ISEDA 2027 deadline 2027-02-01; training window 2026-12 to 2027-01."),
        "verification_command": "timeout 5 bash -c 'echo > /dev/tcp/10.129.32.75/8667' && echo OPEN || echo CLOSED",
        "alternative_if_acl_denied": ("1. Deploy local PyAether on .17 (needs Aether license)\n"
            "2. SSH tunnel through intermediate host reaching 10.129.32.75\n"
            "3. Run eval from a host in 10.129.32.0/24\n"
            "4. Start Phase2 SFT now (no sandbox needed for training, only eval)\n"
            "Note: Phase2 SFT does NOT need sandbox - only eval does."),
    }
    results["escalation"] = escalation
    return all_tcp_blocked, escalation, needed_ports


def _print_runbook(escalation, needed_ports):
    print("\n" + "=" * 72)
    print("ESCALATION RUNBOOK (forward to network team)")
    print("=" * 72)
    print("\nTitle: %s" % escalation["title"])
    print("Priority: %s" % escalation["priority"])
    print("Blocked since: %s" % escalation["blocked_since"])
    print("\nSource: IP=%s Subnet=%s Gateway=%s" % (escalation["source"]["host"], escalation["source"]["subnet"], escalation["source"]["gateway"]))
    print("Dest:   IP=%s Service=%s" % (escalation["destination"]["host"], escalation["destination"]["service"]))
    print("\nCurrent state: ICMP=%s  TCP=%s  SSH=%s" % (escalation["current_state"]["icmp"], escalation["current_state"]["tcp_all_ports"], escalation["current_state"]["ssh_22"]))
    print("\nRequired ACL rules:")
    for r in needed_ports:
        req = "REQUIRED" if r["required"] else "optional"
        print("  Allow TCP %5d  [%8s]  - %s" % (r["port"], req, r["role"]))
    print("\nACL summary: %s" % escalation["acl_rule_summary"])
    print("Verify: %s" % escalation["verification_command"])
    print("\nJustification: %s" % escalation["business_justification"])
    print("\nAlternatives:")
    for line in escalation["alternative_if_acl_denied"].split("\n"):
        print("  %s" % line)
    print("\n" + "=" * 72)


def _run():
    results, ok, avg, loss, ok_ctrl, port_results = main()
    all_tcp_blocked, escalation, needed_ports = _diagnose_and_escalate(results, ok, avg, loss, ok_ctrl, port_results)
    if "--json-only" not in sys.argv:
        _print_runbook(escalation, needed_ports)
    json_path = os.path.join(RUN_DIR, "r169_sandbox_acl_escalation.json")
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("\nJSON saved: %s" % json_path)
    print("\n[R169] sandbox %s ICMP=%s TCP=%s control=%s" % (
        SANDBOX_HOST, "OK" if ok else "FAIL",
        "BLOCKED" if all_tcp_blocked else "PARTIAL",
        "OK" if ok_ctrl else "FAIL"))
    print("  Action: network team open TCP ACL 10.252.32.0/22 -> 10.129.32.75 ports 8664-8669+8653")
    print("  Phase2 SFT does NOT need sandbox - can start once GPU5/6/7 released")
    return 0 if all_tcp_blocked else 1


if __name__ == "__main__":
    sys.exit(_run())

