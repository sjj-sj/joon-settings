#!/usr/bin/env python3
import re
import shutil
import sys
from pathlib import Path


config_path = Path(sys.argv[1]).expanduser()
if not config_path.exists():
    print(f">> skipping Zellij clipboard setup; config not found: {config_path}")
    raise SystemExit

if shutil.which("xsel") is None:
    print(">> skipping Zellij clipboard setup; xsel is not installed")
    raise SystemExit

config = config_path.read_text()
wanted = 'copy_command "xsel --clipboard --input"'
if re.search(rf"^\s*{re.escape(wanted)}\s*$", config, re.MULTILINE):
    print(f">> Zellij xsel clipboard command already current: {config_path}")
    raise SystemExit

existing = re.search(r'^\s*copy_command\s+"[^"]+"\s*$', config, re.MULTILINE)
if existing is not None:
    print(f">> preserving existing Zellij copy_command: {config_path}")
    raise SystemExit

config_path.write_text(config.rstrip() + "\n\n" + wanted + "\n")
print(f">> installed Zellij xsel clipboard command: {config_path}")
