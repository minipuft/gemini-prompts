#!/usr/bin/env python3
"""
Gemini SessionStart Hook - No-op placeholder.

Dev-sync is not needed for Gemini:
- Developers: Link install means source changes are live
- Users: npm package is source of truth, no dev source to sync
"""
import json


def main():
    # Output empty JSON for Gemini hook protocol
    print(json.dumps({}))


if __name__ == "__main__":
    main()
