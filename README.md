# 🔐 IP Address Allow List Manager

> A Python tool for automating IP-based access control — built for security teams and IT administrators.

---

## 📌 Overview

**IP Address Allow List Manager** is an object-oriented Python tool that manages a file-based IP address allow list for any organization. It automates granting and revoking network access, validates every IP address, logs all changes, and works both as a **command-line tool** and an **importable Python module**.

No external libraries required — pure Python 3.10+ standard library.

---

## ✨ Features

- ✅ Add or remove one or many IP addresses in a single command
- ✅ O(1) lookup and removal using a `set` data structure
- ✅ Validates every IP (IPv4 & IPv6) before making any change
- ✅ Automatic duplicate removal when loading the allow list
- ✅ Persistent, timestamped logging to `allow_list_changes.log`
- ✅ One-command snapshot/backup of the current allow list
- ✅ Configurable file path — works with any `.txt` allow list file
- ✅ Clean summary output after every operation

---

## 🗂️ Repository Structure

```
📦 your-repo/
 ┣ 📜 update_allow_list.py     # AllowListManager class + CLI entry point
 ┣ 📄 allow_list.txt           # Your company's allow list (one IP per line)
 ┗ 📋 allow_list_changes.log   # Auto-generated on first run
```

---

## ⚙️ How It Works

The core of this project is the `AllowListManager` class. Here's what happens under the hood every time you use it:

```
  Instantiate
      │
      ▼
  _load()  ──── reads allow_list.txt
               splits into tokens
               validates each IP        ──── invalid entries are warned & skipped
               stores valid IPs in a set ──── duplicates are auto-collapsed
      │
      ▼
  Operate  ──── remove_ips() / add_ips() / contains() / get_all()
               all lookups are O(1) via the internal set
      │
      ▼
  _save()  ──── only called when something actually changed
               sorts IPs for readability
               overwrites allow_list.txt
      │
      ▼
  Logging  ──── every action written to terminal + allow_list_changes.log
```

### Why a `set`?

IP addresses are stored internally as a Python `set`. This means:
- **Lookup** — `"10.0.0.1" in manager` → O(1) average
- **Remove** — `manager.remove_ips([...])` → O(1) per address
- **No duplicates** — adding the same IP twice has no effect
- **Scales** — performs the same whether your list has 100 or 100,000 entries

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
```

### 2. Set up your allow list

Edit `allow_list.txt` and add your approved IP addresses, one per line:

```
192.168.1.1
192.168.1.2
10.0.0.5
172.16.0.10
```

### 3. Run it

```bash
python update_allow_list.py --help
```

---

## 💻 CLI Usage

The `--file` flag specifies your allow list. It defaults to `allow_list.txt` in the current directory, so you can omit it if using the default name.

### Remove IPs (e.g. after a security incident)

```bash
python update_allow_list.py remove 192.168.1.5 10.0.0.3
```

### Add new IPs (e.g. onboarding employees)

```bash
python update_allow_list.py add 10.0.0.99 172.16.0.1
```

### Check if an IP is currently allowed

```bash
python update_allow_list.py check 192.168.1.5
```

```
192.168.1.5  →  ✅ ON the allow list
```

### Print the full current allow list

```bash
python update_allow_list.py list
```

### Save a timestamped backup

```bash
python update_allow_list.py snapshot
```

```
Snapshot saved to: allow_list_snapshot_20250301_143022.txt
```

### Use a custom file path

```bash
python update_allow_list.py --file /etc/security/approved_hosts.txt remove 10.0.0.3
```

---

## 🐍 Module Usage

You can import `AllowListManager` directly into any Python script or pipeline:

```python
from update_allow_list import AllowListManager

# Load your company's allow list
manager = AllowListManager("allow_list.txt")

# Remove IPs flagged in a security incident report
result = manager.remove_ips(["192.168.25.6", "192.168.25.14"])
print(result)
# → {'removed': ['192.168.25.6', '192.168.25.14'], 'not_found': [], 'invalid': []}

# Grant access to a new employee
manager.add_ips(["10.0.0.45"])

# Check access for a specific IP
if "10.0.0.45" in manager:
    print("Access granted")

# See total number of allowed IPs
print(len(manager))

# Back up before a bulk change
manager.export_snapshot()
```

### Full API Reference

| Method | Description | Returns |
|---|---|---|
| `AllowListManager(filepath)` | Constructor — loads the file into memory | instance |
| `remove_ips(list)` | Remove a list of IPs, save, and log | `dict` — removed / not_found / invalid |
| `add_ips(list)` | Add a list of IPs, save, and log | `dict` — added / existing / invalid |
| `contains(ip)` | Check if a single IP is on the list | `bool` |
| `get_all()` | Return sorted list of all allowed IPs | `list[str]` |
| `size()` | Number of IPs currently on the list | `int` |
| `export_snapshot(path?)` | Save a dated backup of the allow list | `str` — path written to |
| `len(manager)` | Same as `size()` | `int` |
| `"x.x.x.x" in manager` | Same as `contains()` | `bool` |

---

## 📋 Logging

Every operation is automatically logged to both your terminal and `allow_list_changes.log`:

```
2025-03-01 14:30:22  [INFO]   Loaded 48 IP address(es) from 'allow_list.txt'.
2025-03-01 14:30:22  [INFO]   REMOVED: 192.168.25.6
2025-03-01 14:30:22  [INFO]   REMOVED: 192.168.25.14
2025-03-01 14:30:22  [WARNING] NOT FOUND (already absent): 10.0.0.99
2025-03-01 14:30:22  [INFO]   Saved 46 IP address(es) to 'allow_list.txt'.
```

---

## 🛠️ Requirements

- Python 3.10 or higher
- No third-party packages — uses only the standard library (`argparse`, `ipaddress`, `logging`, `os`, `datetime`)