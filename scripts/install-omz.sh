#!/usr/bin/env bash
# Install oh-my-zsh + the custom plugins listed in files/shell/plugins.txt. Idempotent.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ ! -d "$HOME/.oh-my-zsh" ]; then
  echo ">> installing oh-my-zsh"
  RUNZSH=no KEEP_ZSHRC=yes sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
else
  echo ">> oh-my-zsh already present"
fi

ZC="${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}"
mkdir -p "$ZC/plugins"
# read "name  url" lines from plugins.txt (skip comments/blanks)
grep -vE '^\s*(#|$)' "$HERE/files/shell/plugins.txt" | while read -r name url _; do
  dest="$ZC/plugins/$name"
  if [ -d "$dest/.git" ]; then
    echo ">> $name already cloned"
  else
    echo ">> cloning $name"
    git clone --depth 1 "$url" "$dest"
  fi
done

echo ">> done. Now cherry-pick files/shell/zshrc.sample into ~/.zshrc"
