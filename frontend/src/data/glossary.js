// Plain-english definitions of security concepts used throughout the app.
// Each entry: { term, short, full, category, related_commands? }

export const GLOSSARY = [
  // ── Shells & Access ──────────────────────────────────────────────────
  {
    term: "reverse shell",
    short: "A connection where the target machine calls back to the attacker.",
    full: "Normally you connect TO a server. A reverse shell flips this — the compromised machine connects OUT to the attacker's machine. This is useful because firewalls often block incoming connections but allow outgoing ones. The attacker sets up a listener, the target runs a one-liner, and suddenly the attacker has a terminal on the target.",
    category: "shells",
    related_commands: ["nc", "mkfifo", "bash", "socat", "python3"],
  },
  {
    term: "bind shell",
    short: "A shell that waits for an incoming connection on an open port.",
    full: "The opposite of a reverse shell. The compromised machine opens a port and waits. The attacker connects TO that port and gets a terminal. Less common than reverse shells because firewalls usually block new incoming ports.",
    category: "shells",
    related_commands: ["nc", "socat"],
  },
  {
    term: "TTY",
    short: "A real interactive terminal — as opposed to a dumb pipe.",
    full: "Many reverse shells give you a limited 'dumb' connection where Ctrl+C kills the shell, tab completion doesn't work, and interactive programs (like sudo) fail. Upgrading to a TTY means getting a proper interactive terminal. The classic trick: python3 -c 'import pty; pty.spawn(\"/bin/bash\")'",
    category: "shells",
    related_commands: ["python3", "stty", "tty"],
  },

  // ── Privilege & Access Control ───────────────────────────────────────
  {
    term: "privilege escalation",
    short: "Going from a low-privilege user to a higher one — ideally root.",
    full: "After landing on a machine as a regular user, the next goal is usually to become root (the all-powerful administrator). Privilege escalation exploits misconfigurations (like sudo rules), SUID binaries, kernel vulnerabilities, or weak file permissions to gain higher access.",
    category: "privilege",
    related_commands: ["sudo", "find", "chmod", "chroot", "python3", "awk"],
  },
  {
    term: "SUID",
    short: "A file permission bit that makes a program run as its owner, not you.",
    full: "Normally a program runs with YOUR permissions. If the SUID bit is set, it runs with the file OWNER's permissions — often root. This is intentional for things like 'passwd' (which needs to edit /etc/shadow) but dangerous when attackers find SUID binaries that can be abused.",
    category: "privilege",
    related_commands: ["chmod", "find", "install"],
  },
  {
    term: "root",
    short: "The all-powerful administrator account on Linux.",
    full: "Root (UID 0) has no restrictions — it can read any file, kill any process, change any permission, and install anything. Getting root on a machine means full control. Most attacks aim to escalate to root after initial access.",
    category: "privilege",
    related_commands: ["sudo", "su"],
  },
  {
    term: "GTFOBins",
    short: "A list of Unix binaries that can be abused for privilege escalation.",
    full: "GTFOBins (gtfobins.github.io) catalogs common Linux tools that can be misused to escalate privileges, escape restricted shells, or read/write files. If 'sudo -l' shows you can run 'awk', 'find', 'python3', or dozens of others as root, GTFOBins has a one-liner to get a root shell.",
    category: "privilege",
    related_commands: ["sudo", "find", "awk", "python3", "tee", "sed"],
  },
  {
    term: "lateral movement",
    short: "Moving from one machine to another inside a network after initial access.",
    full: "Once inside a network, attackers move sideways — from the web server to the database server, from a workstation to a domain controller. Common techniques include using stolen SSH keys, passing password hashes, or abusing trust relationships between machines.",
    category: "privilege",
    related_commands: ["ssh", "find", "nc"],
  },

  // ── Payloads & Evasion ───────────────────────────────────────────────
  {
    term: "payload",
    short: "The malicious code that actually does the damage.",
    full: "The payload is the part of an attack that executes on the target. A reverse shell command is a payload. Ransomware is a payload. The delivery mechanism (email, exploit) gets the payload there; the payload itself does the work.",
    category: "payloads",
    related_commands: ["base64", "base32", "nc", "python3", "wget", "curl"],
  },
  {
    term: "obfuscation",
    short: "Making code or data harder to read so security tools don't recognize it.",
    full: "IDS, antivirus, and firewalls look for known bad patterns. Obfuscation changes the appearance of a payload without changing what it does — base64-encoding a command, splitting a string, or using unusual syntax all obscure the true intent from pattern matchers.",
    category: "payloads",
    related_commands: ["base64", "base32", "xxd", "tr"],
  },
  {
    term: "sandbox evasion",
    short: "Tricks to make malware behave normally in an automated analysis environment.",
    full: "Security vendors run suspicious files in 'sandboxes' — automated analysis environments — to see what they do. Smart malware checks for signs of a sandbox (low RAM, single CPU, no user files, unusual uptime) and stays quiet until it is confident it is on a real machine.",
    category: "payloads",
    related_commands: ["sleep", "nproc", "uptime", "date", "stdbuf"],
  },
  {
    term: "C2 / command and control",
    short: "The attacker's server that sends instructions to compromised machines.",
    full: "After compromising a machine, attackers need a way to send it commands. The C2 server is that channel. Malware phones home to the C2 to receive instructions, send stolen data, and signal that it is still alive. HTTPS C2 traffic blends in with normal web traffic.",
    category: "payloads",
    related_commands: ["curl", "wget", "nc", "socat", "nohup"],
  },
  {
    term: "fileless attack",
    short: "An attack that runs entirely in memory, leaving no files on disk.",
    full: "Traditional malware writes files to disk where antivirus can find them. Fileless attacks run entirely in memory — downloading and executing code in a single pipeline without ever writing to disk. 'curl http://... | bash' is the simplest example.",
    category: "payloads",
    related_commands: ["curl", "wget", "python3", "bash"],
  },

  // ── Recon & Discovery ────────────────────────────────────────────────
  {
    term: "reconnaissance",
    short: "Gathering information about a target before attacking.",
    full: "Before attacking, you need to understand the target — what machines exist, what ports are open, what software is running, who works there. Recon can be passive (searching public info) or active (sending probes like nmap scans).",
    category: "recon",
    related_commands: ["nmap", "curl", "wget", "nc", "hostname", "whoami"],
  },
  {
    term: "enumeration",
    short: "Systematically listing everything on a system after you have access.",
    full: "Once inside a machine, enumeration means cataloguing everything: users, groups, running processes, network connections, installed software, SUID binaries, scheduled jobs, environment variables. The more you enumerate, the more paths to escalation you find.",
    category: "recon",
    related_commands: ["find", "sudo", "env", "top", "whoami", "hostname", "id"],
  },
  {
    term: "port scanning",
    short: "Probing a machine to find which network ports are open.",
    full: "Every network service listens on a numbered port (SSH=22, HTTP=80, HTTPS=443). Port scanning sends packets to every port to find which ones respond — revealing what services are running and potentially exploitable.",
    category: "recon",
    related_commands: ["nmap", "nc"],
  },
  {
    term: "attack surface",
    short: "Every possible entry point an attacker could use.",
    full: "The attack surface is the total set of ways an attacker could reach your system — every open port, every running service, every web form, every user account. Reducing the attack surface (closing ports, removing services) is one of the most effective defenses.",
    category: "recon",
  },

  // ── Persistence ──────────────────────────────────────────────────────
  {
    term: "persistence",
    short: "Techniques to maintain access after a reboot or session end.",
    full: "Getting access once is not enough if it disappears when the machine reboots. Persistence means planting something that survives — a cron job, a modified startup script, an SSH authorized key, a new user account, or a systemd service that re-establishes the connection.",
    category: "persistence",
    related_commands: ["nohup", "cron", "echo", "tee", "ln"],
  },
  {
    term: "backdoor",
    short: "A secret way back into a system, left by an attacker.",
    full: "After compromising a system, attackers often plant a hidden access method — an extra SSH key, a hidden user, a listening service on an unusual port — so they can return even if the original vulnerability is patched.",
    category: "persistence",
    related_commands: ["mkfifo", "nc", "nohup", "echo"],
  },

  // ── Exfiltration & Evidence ──────────────────────────────────────────
  {
    term: "exfiltration",
    short: "Stealing data out of a network without being detected.",
    full: "After finding sensitive data, attackers need to get it out of the network. Exfiltration channels range from obvious (uploading to a web server) to subtle (encoding data in DNS queries, hiding it in HTTPS traffic, or drip-feeding small chunks over time to avoid volume alerts).",
    category: "exfil",
    related_commands: ["nc", "curl", "wget", "dd", "split", "base64", "tcpdump"],
  },
  {
    term: "anti-forensics",
    short: "Covering your tracks to hinder post-incident investigation.",
    full: "After an attack, incident responders look for evidence — log files, deleted file remnants, network traces, process history. Anti-forensics is any technique that makes this harder: wiping logs, overwriting deleted file data, clearing shell history, or timestomping (changing file timestamps).",
    category: "exfil",
    related_commands: ["shred", "truncate", "dd", "unlink"],
  },

  // ── Network Concepts ─────────────────────────────────────────────────
  {
    term: "port forwarding",
    short: "Tunneling traffic from one port/machine to another.",
    full: "Port forwarding takes traffic arriving at one port and redirects it to a different port or machine. Attackers use it to access internal services from outside — for example, forwarding a local port to an internal database through a compromised SSH bastion host.",
    category: "network",
    related_commands: ["ssh", "socat", "nc"],
  },
  {
    term: "pivoting",
    short: "Using a compromised machine as a stepping stone to reach others.",
    full: "Pivoting means routing your attack traffic through an already-compromised machine to reach parts of the network you cannot access directly. The compromised machine acts as a proxy — you connect to it, it connects to the real target.",
    category: "network",
    related_commands: ["ssh", "socat", "nc"],
  },
  {
    term: "SOCKS proxy",
    short: "A general-purpose network proxy that tunnels any TCP traffic.",
    full: "SOCKS is a protocol that lets you route any network connection through an intermediary. 'ssh -D 1080' creates a SOCKS proxy through an SSH tunnel — all traffic you send through port 1080 emerges from the SSH server's network, useful for pivoting.",
    category: "network",
    related_commands: ["ssh", "curl", "nc"],
  },

  // ── Cryptography & Hashing ───────────────────────────────────────────
  {
    term: "hash",
    short: "A one-way fingerprint of data — you cannot reverse it to get the original.",
    full: "A hash function takes any input and produces a fixed-length output (the hash). The same input always gives the same hash, but you cannot go backwards from hash to input. Passwords are stored as hashes — attackers crack them by hashing millions of guesses and comparing.",
    category: "crypto",
    related_commands: ["sha256sum", "md5sum", "sha1sum", "b2sum", "john"],
  },
  {
    term: "encoding vs encryption",
    short: "Encoding is reversible by anyone. Encryption needs a key.",
    full: "Base64 and base32 are ENCODING — anyone can decode them instantly with no secret. Encryption (AES, RSA) requires a key to decrypt. Attackers use encoding to bypass pattern-matching filters; they use encryption to hide C2 traffic from network monitors.",
    category: "crypto",
    related_commands: ["base64", "base32", "openssl"],
  },
  {
    term: "password cracking",
    short: "Recovering original passwords from their stored hashes.",
    full: "Password cracking means guessing the original password by hashing guesses and comparing to the stored hash. Dictionary attacks use wordlists (rockyou.txt has 14 million real passwords). Rule-based attacks mangle words (Password → P@ssw0rd). Brute force tries every combination.",
    category: "crypto",
    related_commands: ["john", "hydra", "md5sum", "sha256sum"],
  },
  {
    term: "brute force",
    short: "Trying every possible combination until one works.",
    full: "Brute force is the blunt instrument of hacking — try every password, every key, every combination. It always works eventually; the question is whether it takes seconds or centuries. Rate limiting, lockouts, and long passwords all raise the cost of brute force.",
    category: "crypto",
    related_commands: ["hydra", "john"],
  },

  // ── Standards & Frameworks ───────────────────────────────────────────
  {
    term: "MITRE ATT&CK",
    short: "A public framework that catalogs real attacker tactics and techniques.",
    full: "MITRE ATT&CK (att.mitre.org) is a knowledge base of how real attackers operate, organized into Tactics (the goal — e.g. Persistence) and Techniques (the method — e.g. T1053 Scheduled Task). Security teams use it to describe attacks, test defenses, and prioritize coverage.",
    category: "frameworks",
  },
  {
    term: "CVE",
    short: "A unique ID for a publicly known security vulnerability.",
    full: "CVE (Common Vulnerabilities and Exposures) is a standardized numbering system for vulnerabilities. CVE-2021-3156 tells you exactly which flaw is being discussed. When you see a CVE number, you can look it up for technical details, severity scores, and available patches.",
    category: "frameworks",
  },
  {
    term: "pentest",
    short: "An authorized simulated attack to find security weaknesses before real attackers do.",
    full: "A penetration test (pentest) is when an organization hires someone to attack their own systems — with permission — to find vulnerabilities before real attackers do. The difference between a pentester and an attacker is a signed contract.",
    category: "frameworks",
  },
  {
    term: "threat level",
    short: "How dangerous a command or technique is in an attacker's hands.",
    full: "The threat level in this app is a 1-5 scale: 1 (info) = informational, mostly harmless. 3 (medium) = dual-use, potential for misuse. 5 (critical) = direct offensive capability, should not exist on production systems without strong justification.",
    category: "frameworks",
  },

  // ── Linux Concepts ───────────────────────────────────────────────────
  {
    term: "named pipe",
    short: "A special file that connects the output of one process to the input of another.",
    full: "A named pipe (created with mkfifo) is a file that acts like a two-way channel between processes. Unlike regular pipes ('|'), named pipes persist on the filesystem and can connect processes that are not related. The classic reverse shell uses a named pipe to connect netcat's output back to bash's input.",
    category: "linux",
    related_commands: ["mkfifo", "nc", "bash"],
  },
  {
    term: "environment variables",
    short: "Key-value pairs stored in your shell session, often containing secrets.",
    full: "Environment variables are named values passed to every process — things like PATH (where to find programs) and HOME (your home directory). Applications often store secrets here: DATABASE_URL, API_KEY, AWS_SECRET. Running 'env' or 'printenv' dumps them all.",
    category: "linux",
    related_commands: ["env", "printenv", "export"],
  },
  {
    term: "stdin / stdout / stderr",
    short: "The three standard data streams every Linux process has.",
    full: "Every Linux process has three streams: stdin (input, fd 0), stdout (output, fd 1), and stderr (error output, fd 2). Redirection ('>', '<', '2>&1') and pipes ('|') connect these streams between programs. Reverse shells work by connecting all three to a network socket.",
    category: "linux",
    related_commands: ["tee", "stdbuf", "mkfifo"],
  },
  {
    term: "file descriptor",
    short: "A number that identifies an open file or connection in a process.",
    full: "In Linux, everything is a file — including network sockets, pipes, and terminals. A file descriptor (fd) is just a number that refers to an open resource. 0=stdin, 1=stdout, 2=stderr. Attackers redirect file descriptors to connect bash's input/output to a network socket.",
    category: "linux",
    related_commands: ["mkfifo", "bash", "nc"],
  },
]

// index by term (lowercase) for fast lookup
export const GLOSSARY_INDEX = Object.fromEntries(
  GLOSSARY.map((e) => [e.term.toLowerCase(), e])
)

// all terms as a sorted array for the UI
export const ALL_TERMS = [...GLOSSARY].sort((a, b) => a.term.localeCompare(b.term))

export const CATEGORIES = [
  { id: 'all',        label: 'All Concepts' },
  { id: 'shells',     label: 'Shells & Access' },
  { id: 'privilege',  label: 'Privilege & Access Control' },
  { id: 'payloads',   label: 'Payloads & Evasion' },
  { id: 'recon',      label: 'Recon & Discovery' },
  { id: 'persistence',label: 'Persistence' },
  { id: 'exfil',      label: 'Exfiltration & Evidence' },
  { id: 'network',    label: 'Network Concepts' },
  { id: 'crypto',     label: 'Cryptography & Hashing' },
  { id: 'frameworks', label: 'Standards & Frameworks' },
  { id: 'linux',      label: 'Linux Concepts' },
]
