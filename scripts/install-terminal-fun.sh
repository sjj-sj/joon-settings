#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:/usr/local/bin:/usr/bin:$PATH"

install_if_absent() {
  local mode="$1" source="$2" destination="$3"
  mkdir -p "$(dirname "$destination")"
  if [[ -e "$destination" ]]; then
    if cmp -s "$source" "$destination"; then
      printf '>> already current: %s\n' "$destination"
    else
      printf '>> preserving existing: %s (compare with %s)\n' "$destination" "$source"
    fi
    return
  fi
  install -m "$mode" "$source" "$destination"
  printf '>> installed: %s\n' "$destination"
}

for name in saver saverwall ztoy zcava weather pclock tclock wx wxn wxt; do
  install_if_absent 0755 "$HERE/files/bin/$name" "$HOME/.local/bin/$name"
done

install_if_absent 0644 "$HERE/files/shell/saver.zsh" "$HOME/.zsh/my-zshrc/saver.zsh"
install_if_absent 0644 "$HERE/files/shell/tools-cheatsheet.zsh" "$HOME/.zsh/my-zshrc/tools-cheatsheet.zsh"
install_if_absent 0644 "$HERE/files/config/peaclock/config" "$HOME/.config/peaclock/config"
install_if_absent 0644 "$HERE/files/config/weathr/config.toml" "$HOME/.config/weathr/config.toml"
install_if_absent 0644 "$HERE/files/config/cava/zcava.conf" "$HOME/.config/cava/zcava.conf"
python3 "$HERE/scripts/install-zellij-clipboard.py" "$HOME/.config/zellij/config.kdl"

desktop_tmp="$(mktemp)"
trap 'rm -f "$desktop_tmp"' EXIT
awk '{ gsub(/@HOME@/, ENVIRON["HOME"]); print }' "$HERE/files/applications/saverwall.desktop.in" > "$desktop_tmp"
install_if_absent 0644 "$desktop_tmp" "$HOME/.local/share/applications/saverwall.desktop"
install_if_absent 0644 "$HERE/files/icons/saverwall.svg" "$HOME/.local/share/icons/hicolor/scalable/apps/saverwall.svg"

command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$HOME/.local/share/applications"
command -v gtk-update-icon-cache >/dev/null 2>&1 && gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" >/dev/null 2>&1 || true

missing=()
for name in alacritty cava curl jq peaclock python3 tmux tty-clock xsel zellij; do
  command -v "$name" >/dev/null 2>&1 || missing+=("$name")
done
if ! python3 -c 'import Xlib' >/dev/null 2>&1; then
  missing+=(python3-xlib)
fi

if (( ${#missing[@]} )); then
  printf '>> settings installed; missing optional runtime tools: %s\n' "${missing[*]}"
  printf '>> see docs/08-terminal-fun.md\n'
else
  printf '>> terminal fun settings ready\n'
fi
