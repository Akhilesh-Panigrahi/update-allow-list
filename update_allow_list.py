#update allow list

#!/usr/bin/env python3
"""
update_allow_list.py

An object-oriented IP Address Allow List Manager.
Manages access control by maintaining a file-based allow list
and providing methods to add, remove, and audit IP addresses.
"""

import argparse
import ipaddress
import logging
import os
from datetime import datetime


# ---------------------------------------------------------------------------
# Logging setup — writes to console AND a log file automatically
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    handlers=[
        logging.StreamHandler(),                        # prints to terminal
        logging.FileHandler("allow_list_changes.log"),  # saves to a log file
    ],
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helper: validate an IP address string
# ---------------------------------------------------------------------------
def _is_valid_ip(ip: str) -> bool:
    """Return True if the string is a valid IPv4 or IPv6 address."""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


# ===========================================================================
# Core class
# ===========================================================================
class AllowListManager:
    """
    Manages a file-based IP address allow list.

    Think of this like a C++ class:
      - __init__  →  constructor
      - self      →  this pointer
      - _<name>   →  private/protected convention (no true private in Python)

    Internal data structure
    -----------------------
    The IP addresses are stored in a Python `set` (like std::unordered_set in
    C++).  This gives O(1) average-case lookup and removal, which is much
    faster than scanning a list (O(n)) for large allow lists.

    The set is only converted back to a list when we need to write the file,
    so all in-memory operations stay fast.
    """

    def __init__(self, filepath: str):
        """
        Constructor.  Loads the allow list from disk into a set.

        Parameters
        ----------
        filepath : str
            Path to the .txt file that holds one IP address per line.
        """
        self._filepath: str = filepath          # where the file lives on disk
        self._allow_set: set[str] = set()       # our fast in-memory data structure
        self._load()                            # populate the set from the file

    # ------------------------------------------------------------------
    # Private helpers  (convention: leading underscore = "private")
    # ------------------------------------------------------------------

    def _load(self) -> None:
        """Read the allow-list file and populate the internal set."""
        if not os.path.exists(self._filepath):
            # File doesn't exist yet — start with an empty set (new company setup)
            logger.warning(
                "File '%s' not found. Starting with an empty allow list.",
                self._filepath,
            )
            return

        with open(self._filepath, "r") as f:
            raw = f.read()

        # Split on any whitespace (spaces, newlines, tabs)
        raw_ips = raw.split()

        valid, invalid = [], []
        for ip in raw_ips:
            if _is_valid_ip(ip):
                valid.append(ip)
            else:
                invalid.append(ip)

        self._allow_set = set(valid)  # sets automatically deduplicate

        logger.info("Loaded %d IP address(es) from '%s'.", len(self._allow_set), self._filepath)
        if invalid:
            logger.warning(
                "Skipped %d invalid entr(ies) in file: %s", len(invalid), invalid
            )

    def _save(self) -> None:
        """Write the current in-memory set back to the file (sorted for readability)."""
        sorted_ips = sorted(self._allow_set)          # sorted() on a set returns a list
        content = "\n".join(sorted_ips)

        with open(self._filepath, "w") as f:
            f.write(content)

        logger.info(
            "Saved %d IP address(es) to '%s'.", len(self._allow_set), self._filepath
        )

    # ------------------------------------------------------------------
    # Public API  (these are the methods other code / CLI will call)
    # ------------------------------------------------------------------

    def remove_ips(self, remove_list: list[str]) -> dict:
        """
        Remove a list of IP addresses from the allow list and save the file.

        Parameters
        ----------
        remove_list : list[str]
            IP addresses to revoke access for (e.g. from a security incident).

        Returns
        -------
        dict with keys:
            'removed'     – IPs that were actually removed
            'not_found'   – IPs in the remove list that weren't on the allow list
            'invalid'     – entries in the remove list that aren't valid IPs
        """
        removed, not_found, invalid = [], [], []

        for ip in remove_list:
            if not _is_valid_ip(ip):
                invalid.append(ip)
                logger.warning("Skipping invalid IP in remove list: '%s'", ip)
                continue

            if ip in self._allow_set:        # O(1) set lookup  ← the key improvement
                self._allow_set.discard(ip)  # discard never raises KeyError (safe remove)
                removed.append(ip)
                logger.info("REMOVED: %s", ip)
            else:
                not_found.append(ip)
                logger.info("NOT FOUND (already absent): %s", ip)

        if removed:
            self._save()   # only write to disk if something actually changed
        else:
            logger.info("No changes made — allow list unchanged.")

        return {"removed": removed, "not_found": not_found, "invalid": invalid}

    def add_ips(self, add_list: list[str]) -> dict:
        """
        Add new IP addresses to the allow list.

        Parameters
        ----------
        add_list : list[str]
            IP addresses to grant access to.

        Returns
        -------
        dict with keys:
            'added'    – IPs that were newly added
            'existing' – IPs that were already on the allow list (no duplicates added)
            'invalid'  – entries that aren't valid IP addresses
        """
        added, existing, invalid = [], [], []

        for ip in add_list:
            if not _is_valid_ip(ip):
                invalid.append(ip)
                logger.warning("Skipping invalid IP in add list: '%s'", ip)
                continue

            if ip in self._allow_set:
                existing.append(ip)
                logger.info("ALREADY EXISTS (no duplicate added): %s", ip)
            else:
                self._allow_set.add(ip)
                added.append(ip)
                logger.info("ADDED: %s", ip)

        if added:
            self._save()
        else:
            logger.info("No new IPs added — allow list unchanged.")

        return {"added": added, "existing": existing, "invalid": invalid}

    def contains(self, ip: str) -> bool:
        """Check whether a single IP address is currently on the allow list — O(1)."""
        return ip in self._allow_set

    def get_all(self) -> list[str]:
        """Return a sorted list of all currently allowed IP addresses."""
        return sorted(self._allow_set)

    def size(self) -> int:
        """Return the number of IP addresses currently on the allow list."""
        return len(self._allow_set)

    def export_snapshot(self, output_path: str | None = None) -> str:
        """
        Save a dated snapshot/backup of the current allow list.

        Parameters
        ----------
        output_path : str, optional
            Where to write the snapshot.  Defaults to
            'allow_list_snapshot_YYYYMMDD_HHMMSS.txt' in the current directory.

        Returns
        -------
        str : path of the written snapshot file.
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"allow_list_snapshot_{timestamp}.txt"

        sorted_ips = sorted(self._allow_set)
        with open(output_path, "w") as f:
            f.write("\n".join(sorted_ips))

        logger.info("Snapshot saved to '%s'.", output_path)
        return output_path

    # ------------------------------------------------------------------
    # Dunder (magic) methods — like operator overloading in C++
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        """Allows:  len(manager)"""
        return self.size()

    def __contains__(self, ip: str) -> bool:
        """Allows:  '10.0.0.1' in manager"""
        return self.contains(ip)

    def __repr__(self) -> str:
        """Developer-friendly string representation."""
        return f"AllowListManager(file='{self._filepath}', entries={self.size()})"


# ===========================================================================
# CLI entry point  (runs when you call: python update_allow_list.py ...)
# ===========================================================================
def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="IP Address Allow List Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples
--------
  # Remove specific IPs (e.g. after a security incident)
  python update_allow_list.py --file allow_list.txt remove 192.168.1.5 10.0.0.3

  # Add new IPs
  python update_allow_list.py --file allow_list.txt add 10.0.0.99 172.16.0.1

  # Check if an IP is on the list
  python update_allow_list.py --file allow_list.txt check 192.168.1.5

  # Print the full current allow list
  python update_allow_list.py --file allow_list.txt list

  # Save a timestamped backup snapshot
  python update_allow_list.py --file allow_list.txt snapshot
        """,
    )

    parser.add_argument(
        "--file",
        default="allow_list.txt",
        help="Path to the allow list .txt file (default: allow_list.txt)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- remove ---
    remove_p = subparsers.add_parser("remove", help="Remove IPs from the allow list")
    remove_p.add_argument("ips", nargs="+", help="IP addresses to remove")

    # --- add ---
    add_p = subparsers.add_parser("add", help="Add IPs to the allow list")
    add_p.add_argument("ips", nargs="+", help="IP addresses to add")

    # --- check ---
    check_p = subparsers.add_parser("check", help="Check if an IP is on the allow list")
    check_p.add_argument("ip", help="IP address to look up")

    # --- list ---
    subparsers.add_parser("list", help="Print all current allowed IPs")

    # --- snapshot ---
    snap_p = subparsers.add_parser("snapshot", help="Save a dated backup of the allow list")
    snap_p.add_argument("--output", default=None, help="Custom output path for snapshot")

    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    manager = AllowListManager(args.file)

    if args.command == "remove":
        result = manager.remove_ips(args.ips)
        print(f"\nSummary → Removed: {result['removed']} | "
              f"Not found: {result['not_found']} | Invalid: {result['invalid']}")

    elif args.command == "add":
        result = manager.add_ips(args.ips)
        print(f"\nSummary → Added: {result['added']} | "
              f"Already existed: {result['existing']} | Invalid: {result['invalid']}")

    elif args.command == "check":
        found = manager.contains(args.ip)
        status = "✅ ON the allow list" if found else "❌ NOT on the allow list"
        print(f"\n{args.ip}  →  {status}")

    elif args.command == "list":
        all_ips = manager.get_all()
        print(f"\nAllow list ({len(all_ips)} entries):")
        for ip in all_ips:
            print(f"  {ip}")

    elif args.command == "snapshot":
        path = manager.export_snapshot(args.output)
        print(f"\nSnapshot saved to: {path}")


if __name__ == "__main__":
    main()