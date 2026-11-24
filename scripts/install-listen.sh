#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="$HERE/files/listen/listen"
DESTINATION="$HOME/.local/bin/listen"
LIKE_DIR="${LISTEN_LIKE_DIR:-${XDG_DATA_HOME:-$HOME/.local/share}/listen}"

mkdir -p "$HOME/.local/bin"

if [[ -L "$DESTINATION" ]]; then
  current="$(readlink -f "$DESTINATION" 2>/dev/null || true)"
  if [[ "$current" == "$SOURCE" ]]; then
    echo ">> listen launcher already current: $DESTINATION"
  elif [[ "$current" == "$LIKE_DIR/bin/listen" && -f "$current" ]] && cmp -s "$current" "$SOURCE"; then
    ln -sfn "$SOURCE" "$DESTINATION"
    echo ">> migrated listen launcher: $DESTINATION -> $SOURCE"
  else
    echo ">> preserving existing listen launcher: $DESTINATION -> $current"
  fi
elif [[ -e "$DESTINATION" ]]; then
  echo ">> preserving existing listen command: $DESTINATION"
else
  ln -s "$SOURCE" "$DESTINATION"
  echo ">> installed listen launcher: $DESTINATION -> $SOURCE"
fi

if [[ -z "${LISTEN_LIKE_DIR:-}" ]]; then
  mkdir -p "$LIKE_DIR/music"
fi

if [[ -d "$LIKE_DIR/music" ]]; then
  echo ">> listen likes directory: $LIKE_DIR/music"
else
  echo ">> warning: listen likes directory not found: $LIKE_DIR/music"
  echo ">> restore it or set LISTEN_LIKE_DIR to a directory containing music/"
fi

missing=()
for command_name in cvlc fzf node python3 yt-dlp; do
  if ! command -v "$command_name" >/dev/null 2>&1 &&
     [[ ! -x "$HOME/.local/bin/$command_name" ]] &&
     [[ ! -x "$HOME/.fzf/bin/$command_name" ]]; then
    missing+=("$command_name")
  fi
done

if (( ${#missing[@]} > 0 )); then
  echo ">> missing listen dependencies: ${missing[*]}"
  echo ">> see docs/09-audio-tools.md"
else
  echo ">> listen dependencies present"
fi
