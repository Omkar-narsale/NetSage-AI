# NetSage AI - Networking Fault Troubleshooting Guide

Welcome to the **NetSage AI Networking Fault Guide**. This document serves as a foundational reference for junior network engineers and automated troubleshooting systems working with Cisco-style Packet Tracer and lab environments.

Each section breaks down a fundamental networking category, explaining the underlying concepts, common failure modes, diagnostic Cisco `show` commands, key evidence to inspect, OSI layer mapping, severity levels, and concrete troubleshooting scenarios.

---

## Table of Contents

1. [VLAN (Virtual Local Area Network)](#1-vlan-virtual-local-area-network)
2. [Default Gateway](#2-default-gateway)
3. [DHCP (Dynamic Host Configuration Protocol)](#3-dhcp-dynamic-host-configuration-protocol)
4. [DNS (Domain Name System)](#4-dns-domain-name-system)
5. [Routing](#5-routing)
6. [ACL (Access Control List)](#6-acl-access-control-list)
7. [NAT (Network Address Translation)](#7-nat-network-address-translation)
8. [Wireless (WLAN / Wi-Fi)](#8-wireless-wlan--wi-fi)

---

## 1. VLAN (Virtual Local Area Network)

### What the Problem Means
A VLAN (Virtual Local Area Network) logically partitions a single physical Layer 2 switch into multiple broadcast domains. Devices in different VLANs cannot communicate directly at Layer 2 without a Layer 3 routing device (Router-on-a-Stick or Layer 3 Switch SVI). 

A VLAN fault occurs when access ports are assigned to the wrong VLAN ID, VLANs are missing from the switch database, or inter-switch trunk links misconfigure 802.1Q tagging or allowed VLAN lists.

### Typical Symptoms
* Host cannot communicate with other hosts in its intended department/subnet.
* Traffic drops between switches across trunk links.
* Host receives an IP address from the wrong subnet (wrong VLAN assignment).
* Inter-VLAN pings fail despite routing configuration being active.

### Possible Root Causes
* Switch access port assigned to the wrong VLAN or default VLAN 1.
* VLAN ID has not been created in the switch database (`vlan <id>`).
* Trunk link native VLAN mismatch between adjacent switches.
* VLAN explicitly pruned or omitted from trunk link allowed VLAN list (`switchport trunk allowed vlan`).
* Port configured as access mode instead of trunk mode on an inter-switch connection.

### Useful Cisco/Show Commands
* `show vlan brief` — Displays all configured VLANs and their assigned switch ports.
* `show interfaces switchport` — Shows detailed switchport state (mode, operational VLAN, native VLAN).
* `show interfaces trunk` — Displays active 802.1Q trunk links, native VLANs, and allowed VLAN lists.
* `show running-config interface <interface-id>` — Displays interface-specific configuration lines.

### What Evidence to Look For
* Check `show vlan brief`: Is the host's physical port (e.g., `Fa0/5`) assigned to the correct VLAN ID?
* Check `show interfaces trunk`: Is the target VLAN listed under "Vlans allowed on trunk"?
* Check native VLAN consistency across trunk links (e.g., mismatch warnings or differing native VLAN IDs).

### Typical OSI Layer
* **Layer 2 — Data Link Layer**

### Typical Severity
* **Medium to High** (Affects single host connectivity up to entire switch trunk isolation).

### Example Troubleshooting Scenario
* **Scenario**: PC-A on Switch-1 Port `Fa0/5` cannot reach Server-A on Switch-2 in VLAN 20.
* **Troubleshooting Steps**:
  1. Engineer runs `show vlan brief` on Switch-1.
  2. Output reveals Port `Fa0/5` is currently assigned to `VLAN 1 (default)` instead of `VLAN 20 (Sales)`.
  3. **Fix**: Enter interface configuration mode for `Fa0/5` and execute `switchport access vlan 20`.

---

## 2. Default Gateway

### What the Problem Means
The default gateway is the Layer 3 IP address of a router interface or Layer 3 switch SVI on the local subnet. Hosts use the default gateway to forward IP packets destined for networks outside their local subnet (e.g., remote offices or the Internet).

A default gateway fault occurs when a host has an incorrect gateway IP, the gateway interface is shut down, or the router interface IP is configured in a different subnet than the host.

### Typical Symptoms
* Host can ping other devices in its local subnet (e.g., pings `192.168.1.20` successfully).
* Host CANNOT ping any remote IP address outside its local subnet (e.g., pings to `10.0.0.1` or `8.8.8.8` fail with "Destination host unreachable" or timeout).
* Web browsing to external sites fails completely.

### Possible Root Causes
* Incorrect default gateway IP entered manually on the host NIC settings.
* Default gateway IP misconfigured in the local DHCP server scope.
* Router interface or sub-interface acting as the gateway is in `shutdown` or `administratively down` state.
* Subnet mask mismatch between host and gateway router interface.
* Router SVI (Switch Virtual Interface) for the VLAN is not active (`down/down`).

### Useful Cisco/Show Commands
* `ipconfig /all` (Windows Client) / `show ip interface brief` (Router) — Inspect host IP settings and router interface status.
* `show ip interface <interface-id>` — Checks line protocol, status, and IP subnet of gateway interface.
* `show interfaces <interface-id>` — Validates physical layer and link status.
* `show running-config interface <interface-id>` — Verifies interface IP configuration.

### What Evidence to Look For
* Compare host Default Gateway address against router interface IP address: Do they match exactly?
* Check `show ip interface brief`: Is the gateway interface status `up` and protocol `up`?
* Verify subnet alignment: Is the gateway IP within the host's subnet boundaries?

### Typical OSI Layer
* **Layer 3 — Network Layer**

### Typical Severity
* **High** (Completely blocks all outbound/remote traffic for affected hosts).

### Example Troubleshooting Scenario
* **Scenario**: PC-102 (`192.168.1.15/24`) cannot ping remote server `10.0.0.50`.
* **Troubleshooting Steps**:
  1. On PC-102, run `ipconfig /all`. Default Gateway is listed as `192.168.1.254`.
  2. Log into local router R1 and run `show ip interface brief`. Interface `GigabitEthernet0/0/0` is configured with IP `192.168.1.1/24`.
  3. **Root Cause**: Host default gateway points to non-existent IP `192.168.1.254`.
  4. **Fix**: Change PC-102 default gateway configuration to `192.168.1.1`.

---

## 3. DHCP (Dynamic Host Configuration Protocol)

### What the Problem Means
DHCP automatically assigns IP addresses, subnet masks, default gateways, and DNS server settings to client devices. 

A DHCP fault occurs when clients fail to obtain a valid IP configuration, resulting in an APIPA (Automatic Private IP Addressing) address (`169.254.x.x`) or network unreachability.

### Typical Symptoms
* Workstation receives an APIPA address starting with `169.254.x.x`.
* Host displays "No Internet Access" or "Identifying Network...".
* Multiple hosts report duplicate IP address conflicts.
* Newly connected devices fail to get any network connectivity.

### Possible Root Causes
* Central DHCP server located in a different VLAN, but `ip helper-address` (DHCP Relay) is missing on the local router gateway sub-interface/SVI.
* Cisco IOS DHCP pool exhausted (no available IP addresses left in scope).
* DHCP service disabled globally (`no service dhcp` on router).
* Excluded address ranges misconfigured or overlapping with static assignments.
* PortFast not enabled on edge switchports, causing DHCP request timeout during Spanning Tree listening/learning states.

### Useful Cisco/Show Commands
* `show ip dhcp binding` — Lists currently active DHCP IP leases and MAC address mappings.
* `show ip dhcp pool` — Displays pool statistics, total addresses, leased addresses, and excluded ranges.
* `show ip dhcp conflict` — Shows IP addresses flagged due to ARP conflict detection.
* `show running-config | section dhcp` — Inspects DHCP pool definitions and helper addresses.
* `show ip interface <interface-id>` — Checks if `ip helper-address` is configured.

### What Evidence to Look For
* Check client IP address: Is it `169.254.x.x`? (Indicates client DHCP request failed).
* Check `show ip dhcp pool`: Are leased addresses equal to total addresses? (Pool exhaustion).
* Check sub-interface configuration: If DHCP server is remote, is `ip helper-address <dhcp-server-ip>` present under the client VLAN interface?

### Typical OSI Layer
* **Layer 7 — Application Layer** (operating over Layer 4 UDP ports 67 server / 68 client).

### Typical Severity
* **High** (Prevents dynamic clients from gaining network connectivity).

### Example Troubleshooting Scenario
* **Scenario**: Workstations in VLAN 30 (`172.16.30.0/24`) get APIPA IP `169.254.45.12`. DHCP server is at `172.16.10.100` (VLAN 10).
* **Troubleshooting Steps**:
  1. Inspect Router sub-interface `Gig0/0.30` with `show running-config interface Gig0/0.30`.
  2. Notice `ip address 172.16.30.1 255.255.255.0` is configured, but `ip helper-address` is absent.
  3. Broadcast DHCP requests from VLAN 30 clients are dropped by the router boundary.
  4. **Fix**: Apply `ip helper-address 172.16.10.100` on interface `GigabitEthernet0/0.30`.

---

## 4. DNS (Domain Name System)

### What the Problem Means
DNS translates human-friendly domain names (e.g., `server.corp.local` or `google.com`) into numerical IP addresses needed for IP routing.

A DNS fault leaves IP routing fully operational, but domain resolution fails, preventing users from accessing applications via names/URLs.

### Typical Symptoms
* Direct ping to IP address succeeds (e.g., `ping 10.1.1.50` works fine).
* Ping or web request to domain name fails (e.g., `ping app.corp.local` gives "Ping request could not find host").
* Web browsers display "Server Not Found" or "DNS_PROBE_FINISHED_NXDOMAIN".

### Possible Root Causes
* Incorrect DNS server IP configured on host network adapter or distributed via DHCP scope.
* Primary DNS server unreachable due to routing or firewall ACL blocking UDP port 53.
* DNS server service stopped or DNS record missing/misconfigured on the server.
* Cisco IOS device missing `ip name-server` configuration or `ip domain lookup` disabled.

### Useful Cisco/Show Commands
* `nslookup <domain-name>` (Host CLI) — Tests domain name resolution against specific DNS servers.
* `ipconfig /all` (Host CLI) — Verifies configured DNS server IP addresses.
* `show running-config | include name-server` (Cisco IOS) — Checks configured name servers.
* `show hosts` (Cisco IOS) — Displays local host name-to-address cache.

### What Evidence to Look For
* `nslookup` output: Does `nslookup <domain>` return "DNS request timed out"?
* Compare `nslookup` default server IP with the real DNS server IP on the network.
* Run `ping <IP>` vs `ping <hostname>`: If IP ping works but hostname ping fails, DNS is the issue.

### Typical OSI Layer
* **Layer 7 — Application Layer** (operating over Layer 4 UDP/TCP port 53).

### Typical Severity
* **Medium** (Network connectivity exists, but user applications relying on domain names fail).

### Example Troubleshooting Scenario
* **Scenario**: PC user cannot open `http://intranet.local`. Direct IP ping to `10.1.1.50` succeeds.
* **Troubleshooting Steps**:
  1. On PC, run `nslookup intranet.local`. Output shows "Default Server: Unknown", IP `192.168.1.250`, followed by request timeout.
  2. Network documentation indicates real DNS server IP is `10.1.1.53`.
  3. **Root Cause**: Host DNS server IP `192.168.1.250` is invalid/unreachable.
  4. **Fix**: Update host DNS settings (or DHCP scope) to point to `10.1.1.53`.

---

## 5. Routing

### What the Problem Means
Routing is the Layer 3 process of forwarding IP packets across interconnected networks based on destination IP address routing table lookup. Routing can be configured statically (`ip route`) or dynamically (OSPF, EIGRP, RIP, BGP).

A routing fault occurs when a router lacks a route entry for a destination network, has an incorrect next-hop IP address, or experiences dynamic routing protocol neighbor failure.

### Typical Symptoms
* Traceroute command stops at an intermediate router hop.
* Router drops packets with message "Destination net unreachable".
* Unidirectional ping: Packets reach destination, but return packets fail due to missing reverse route (asymmetric routing fault).
* OSPF/EIGRP route flapping or missing routes in routing table.

### Possible Root Causes
* Missing static route for destination network.
* Static route configured with incorrect next-hop IP address or interface.
* Dynamic routing protocol (OSPF/EIGRP) missing `network` statement under router process.
* OSPF neighbor adjacency failure due to area ID mismatch, hello/dead timer mismatch, MTU mismatch, or subnet mask mismatch.
* Passive interface command applied to active router link interface.

### Useful Cisco/Show Commands
* `show ip route` — Displays active routing table (Connected, Static, OSPF, EIGRP routes).
* `show ip protocols` — Displays active routing protocol configurations and network statements.
* `show ip ospf neighbor` / `show ip eigrp neighbors` — Inspects dynamic routing neighbor state.
* `show ip ospf interface` — Verifies OSPF timers, area assignment, and hello/dead intervals.
* `traceroute <destination-ip>` — Traces exact hop-by-hop path taken by packets.

### What Evidence to Look For
* Inspect `show ip route`: Is there an explicit route entry or valid default route (`0.0.0.0/0`) covering the destination IP?
* Check status of next-hop IP: Is the next-hop IP directly reachable in `show ip route`?
* For OSPF: Is `show ip ospf neighbor` showing state `FULL/BDR` or `FULL/DR`? (If blank or `INIT`, neighbor state is broken).

### Typical OSI Layer
* **Layer 3 — Network Layer**

### Typical Severity
* **High** (Disrupts communication between distinct subnets and remote sites).

### Example Troubleshooting Scenario
* **Scenario**: Router R2 (Branch) cannot communicate with HQ subnet `10.10.0.0/16`.
* **Troubleshooting Steps**:
  1. Log into R2 and execute `show ip route`.
  2. Routing table shows connected subnets `192.168.20.0/24` and `10.0.0.0/30`, but NO route entry for `10.10.0.0/16`.
  3. Execute `show ip ospf neighbor` — output is blank. OSPF neighbor relationship with HQ router R1 is not established.
  4. **Fix**: Correct OSPF area and `network 10.0.0.0 0.0.0.3 area 0` command on R2 to form OSPF adjacency and exchange routes.

---

## 6. ACL (Access Control List)

### What the Problem Means
Access Control Lists (ACLs) are ordered rule sets applied to router or switch interfaces to permit or deny IP traffic based on criteria such as source IP, destination IP, protocol, and port numbers.

An ACL fault occurs when an unexpected rule permits unauthorized traffic or (more commonly) blocks legitimate application traffic due to explicit deny lines or the implicit `deny ip any any` at the end of every ACL.

### Typical Symptoms
* Ping (ICMP) to server succeeds, but HTTP (port 80) or SSH (port 22) connection is refused or times out.
* Traffic from specific subnet is blocked while adjacent subnets can communicate normally.
* Inter-VLAN traffic works in one direction but drops in the reverse direction.

### Possible Root Causes
* Explicit `deny` rule matches target traffic before reaching a `permit` statement.
* Implicit `deny ip any any` at end of ACL drops traffic because no explicit `permit` rule matched.
* ACL applied in wrong direction (`in` vs `out`) on interface.
* ACL bound to wrong physical or sub-interface (`ip access-group <name> <in|out>`).
* Wildcard mask miscalculated (e.g., `0.255.255.255` instead of `0.0.0.255`).

### Useful Cisco/Show Commands
* `show access-lists` — Displays all configured ACLs with rule line numbers and match packet counters.
* `show ip interface <interface-id>` — Displays inbound and outbound ACLs applied to interface.
* `show running-config | section access-list` — Inspects full ACL definition syntax.

### What Evidence to Look For
* Run `show access-lists`: Look at match counters `(matches)` next to `deny` statements. Do counters increment when testing traffic?
* Run `show ip interface <interface-id>`: Verify whether `Inbound access list` or `Outbound access list` is configured on the intended interface.
* Verify rule sequence: ACLs evaluate top-to-bottom. Is a broad `deny` rule sitting above a specific `permit` rule?

### Typical OSI Layer
* **Layer 3 / Layer 4 — Network and Transport Layers** (Filters IP addresses and TCP/UDP ports).

### Typical Severity
* **Medium** (Restricts specific services, ports, or host groups).

### Example Troubleshooting Scenario
* **Scenario**: Workstations in HR subnet `192.168.10.0/24` can ping Payroll Server `10.0.5.20`, but web browser access to `http://10.0.5.20` fails.
* **Troubleshooting Steps**:
  1. On Router R1, run `show ip interface Gig0/0/1` (interface facing Payroll server). Output shows `Outbound access list is 101`.
  2. Run `show access-lists 101`. Line 10 states: `deny tcp 192.168.10.0 0.0.0.255 host 10.0.5.20 eq www (156 matches)`.
  3. **Root Cause**: ACL 101 explicitly denies TCP port 80 traffic from HR subnet to Payroll server.
  4. **Fix**: Modify ACL 101 to replace line 10 with `permit tcp 192.168.10.0 0.0.0.255 host 10.0.5.20 eq www`.

---

## 7. NAT (Network Address Translation)

### What the Problem Means
NAT (Network Address Translation) modifies IP address headers in transit. It commonly translates private, non-routable IPv4 addresses (RFC 1918) from an internal LAN into a public routable IPv4 address (PAT / NAT Overload) for Internet access.

A NAT fault occurs when internal hosts cannot access external networks because address translation is not taking place, translation pools are exhausted, or internal/external interfaces are misidentified.

### Typical Symptoms
* Internal hosts can ping local router gateway, but cannot ping public Internet IP addresses (e.g., `8.8.8.8`).
* Packet captures on WAN interface show packets leaving with private source IPs (`192.168.x.x`), which ISP routers immediately drop.
* Inbound static NAT mapping for an internal server (e.g., web server) fails from external networks.

### Possible Root Causes
* Router interface facing LAN missing `ip nat inside` directive.
* Router interface facing WAN/ISP missing `ip nat outside` directive.
* Access list referenced in `ip nat inside source list <acl> interface <wan-int> overload` excludes client subnet.
* Dynamic NAT pool exhausted (insufficient public IP addresses).
* Incorrect static NAT configuration syntax (`ip nat inside source static <local-ip> <global-ip>`).

### Useful Cisco/Show Commands
* `show ip nat translations` — Displays active translation table entries (Inside Local, Inside Global, Outside Local, Outside Global).
* `show ip nat statistics` — Shows total translations, pool usage, miss counts, and inside/outside interface designations.
* `show ip interface brief` / `show ip interface <interface-id>` — Identifies which interfaces have `ip nat inside` or `ip nat outside`.
* `show running-config | include nat` — Inspects active NAT rules.

### What Evidence to Look For
* Run `show ip nat translations`: Is the table blank when internal hosts attempt external traffic? (Indicates NAT is not triggering).
* Run `show ip nat statistics`: Inspect `Outside interfaces` and `Inside interfaces`. Are both LAN and WAN interfaces properly assigned?
* Check NAT ACL: Does the ACL referenced by the NAT statement permit the host's subnet?

### Typical OSI Layer
* **Layer 3 / Layer 4 — Network and Transport Layers** (Translates IP addresses and port numbers).

### Typical Severity
* **High** (Blocks Internet/external connectivity for internal network users).

### Example Troubleshooting Scenario
* **Scenario**: Host PC-1 (`192.168.1.10`) cannot access public server `203.0.113.50`. Pings to local gateway `192.168.1.1` succeed.
* **Troubleshooting Steps**:
  1. On Router R1, generate web traffic from PC-1 and execute `show ip nat translations`. Output is completely empty.
  2. Run `show ip interface Gig0/0/0` (facing LAN) and `show ip interface Gig0/0/1` (facing ISP).
  3. `Gig0/0/1` has `ip nat outside enabled`, but `Gig0/0/0` lacks `ip nat inside`.
  4. **Root Cause**: LAN interface is not flagged as `ip nat inside`, so traffic is never sent to the NAT engine.
  5. **Fix**: Enter interface configuration mode for `Gig0/0/0` and execute `ip nat inside`.

---

## 8. Wireless (WLAN / Wi-Fi)

### What the Problem Means
Wireless LANs (WLANs) provide mobile network access using IEEE 802.11 radio standards. Wireless Access Points (APs) and Wireless LAN Controllers (WLCs) bridge wireless client traffic onto the wired Ethernet infrastructure.

A wireless fault occurs when clients fail 802.11 association, WPA2/WPA3 authentication, or fail to receive network connectivity due to underlying VLAN/DHCP mapping issues on the WLAN.

### Typical Symptoms
* Wireless device fails to connect to SSID ("Unable to connect to this network" or authentication prompt loop).
* Client connects to Wi-Fi signal, but displays "Connected, no Internet" (fails to obtain IP address).
* Wireless clients can access local resources but are isolated from internet access.
* APs fail to join the Wireless LAN Controller (WLC).

### Possible Root Causes
* WPA2 Pre-Shared Key (PSK) or WPA3 security passphrase mismatch between client and WLC/AP configuration.
* WLAN mapped to a VLAN ID that does not exist on connected switch trunk links.
* Switch port connected to Access Point configured incorrectly (e.g., set to access mode instead of trunk mode, or missing native VLAN).
* DHCP server pool for the target wireless VLAN not configured or exhausted.
* AP radio interface disabled or operating on conflicting non-overlapping channels.

### Useful Cisco/Show Commands
* `show wlan summary` (WLC) — Displays configured WLAN IDs, SSIDs, security policies, and VLAN assignments.
* `show ap summary` (WLC) — Lists connected Access Points, IP addresses, operational status, and slots.
* `show client summary` (WLC) — Shows connected wireless client MACs, WLAN IDs, IPs, and status.
* `show interfaces trunk` (Switch) — Verifies switchport connected to AP permits wireless client VLANs.

### What Evidence to Look For
* Check WLC `show wlan summary`: Which VLAN ID is mapped to the target SSID?
* Check Switch `show vlan brief`: Does that VLAN ID exist in the switch database?
* Check AP switchport mode: Is the switchport connected to the AP trunking the wireless client VLAN?

### Typical OSI Layer
* **Layer 1 / Layer 2 — Physical and Data Link Layers** (802.11 wireless frame framing, association, and bridging).

### Typical Severity
* **Medium** (Impacts wireless client access while wired users remain unaffected).

### Example Troubleshooting Scenario
* **Scenario**: Laptops connecting to SSID "Guest-WiFi" associate successfully but receive no IP address.
* **Troubleshooting Steps**:
  1. On WLC, run `show wlan summary`. WLAN 2 (`Guest-WiFi`) is mapped to `VLAN ID: 99`.
  2. Log into edge switch connected to AP and execute `show vlan brief`.
  3. VLAN 99 is NOT listed in the switch VLAN database.
  4. **Root Cause**: WLAN traffic tagged with VLAN 99 is dropped by the switch because VLAN 99 does not exist on the Layer 2 switch.
  5. **Fix**: On the switch, enter global configuration mode and create `vlan 99` with `name Guest-VLAN`.

---
