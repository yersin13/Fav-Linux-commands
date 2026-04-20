import re
from pytubefix import Playlist, YouTube
from youtube_transcript_api import YouTubeTranscriptApi

_ytt = YouTubeTranscriptApi()

LINUX_COMMANDS = [
    "ls", "cd", "pwd", "mkdir", "rmdir", "rm", "cp", "mv", "touch", "cat",
    "less", "more", "head", "tail", "grep", "find", "locate", "which", "whereis",
    "chmod", "chown", "chgrp", "umask", "ln", "tar", "gzip", "gunzip", "zip",
    "unzip", "wget", "curl", "ssh", "scp", "rsync", "ping", "ifconfig", "ip",
    "netstat", "ss", "nmap", "ps", "top", "htop", "kill", "killall", "jobs",
    "bg", "fg", "nohup", "screen", "tmux", "cron", "crontab", "at", "systemctl",
    "service", "journalctl", "dmesg", "lsof", "strace", "ldd", "nm", "objdump",
    "strings", "file", "stat", "du", "df", "mount", "umount", "fdisk", "parted",
    "mkfs", "fsck", "dd", "lsblk", "blkid", "free", "vmstat", "iostat", "sar",
    "uptime", "w", "who", "whoami", "id", "su", "sudo", "passwd", "useradd",
    "userdel", "usermod", "groupadd", "groupdel", "groups", "env", "export",
    "unset", "alias", "unalias", "history", "echo", "printf", "read", "set",
    "source", "exec", "eval", "test", "expr", "let", "awk", "sed", "sort",
    "uniq", "cut", "paste", "join", "tr", "wc", "diff", "patch", "xargs",
    "tee", "bash", "sh", "zsh", "fish", "vim", "vi", "nano", "emacs",
    "man", "info", "apropos", "whatis", "date", "cal", "time", "sleep",
    "wait", "exit", "return", "break", "continue", "shift", "getopts", "trap",
    "iptables", "ufw", "firewalld", "tcpdump", "nc", "netcat", "telnet",
    "ftp", "sftp", "git", "make", "gcc", "g++", "python", "python3",
    "pip", "pip3", "npm", "node", "java", "javac", "docker", "docker-compose",
    "kubectl", "helm", "ansible", "terraform", "vagrant", "virtualenv",
    "conda", "apt", "apt-get", "yum", "dnf", "pacman", "brew", "snap",
    "flatpak", "dpkg", "rpm", "lsmod", "modprobe", "insmod", "rmmod",
    "uname", "hostname", "hostnamectl", "timedatectl", "nmcli",
    "iwconfig", "iwlist", "route", "arp", "traceroute", "mtr",
    "dig", "nslookup", "host", "whois", "openssl", "gpg",
    "md5sum", "sha256sum", "sha1sum", "base64", "xxd", "hexdump",
    "od", "strip", "ar", "ranlib", "readelf", "size", "gdb",
    "valgrind", "perf", "ltrace", "lsattr", "chattr", "getfacl",
    "setfacl", "getcap", "setcap", "ulimit", "nice", "renice",
    "ionice", "taskset", "chroot", "nsenter", "unshare", "tc",
    "ethtool", "bridge", "brctl", "wg", "sshd", "rsyslog",
    "logrotate", "anacron", "inotifywait", "auditctl", "ausearch",
    "aureport", "sestatus", "getenforce", "setenforce",
]


def fetch_playlist_videos(playlist_id: str) -> list:
    playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
    playlist = Playlist(playlist_url)

    videos = []
    for video in playlist.videos:
        try:
            videos.append({
                "id": video.video_id,
                "title": video.title,
                "url": f"https://www.youtube.com/watch?v={video.video_id}",
            })
        except Exception:
            continue

    return videos


def extract_commands_from_text(text: str) -> list:
    text_lower = text.lower()
    found = []
    for cmd in LINUX_COMMANDS:
        if re.search(r'\b' + re.escape(cmd) + r'\b', text_lower):
            found.append(cmd)
    return found


def extract_flags_from_text(text: str) -> list:
    pattern = r'(?:^|\s)(--?[a-zA-Z][a-zA-Z0-9_-]*(?:=[^\s]*)?)'
    flags = re.findall(pattern, text)
    cleaned = [f.strip() for f in flags if len(f.strip()) >= 2]
    seen = {}
    for f in cleaned:
        seen[f] = seen.get(f, 0) + 1
    # Return flags sorted by frequency
    return [f for f, _ in sorted(seen.items(), key=lambda x: -x[1])]


def process_video(video_id: str) -> dict:
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    yt = YouTube(video_url)
    title = yt.title

    transcript_entries = _ytt.fetch(video_id)
    full_text = " ".join(entry.text for entry in transcript_entries)

    commands = extract_commands_from_text(full_text)
    primary_command = commands[0] if commands else title.split()[0].lower().strip(":")

    flags = extract_flags_from_text(full_text)

    return {
        "video_id": video_id,
        "title": title,
        "command": primary_command,
        "all_commands": commands[:15],
        "transcript": full_text,
        "flags": flags[:25],
        "video_url": video_url,
    }
