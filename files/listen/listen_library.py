#!/usr/bin/env python3

import argparse
from datetime import date, datetime
import json
from pathlib import Path
import re
import unicodedata


def clean(value):
    return "".join(
        character for character in value if character >= " " and character != "\x7f"
    ).strip()


def normalize_record(record):
    record = {key: clean(value) for key, value in record.items()}
    video_title = record.get("video_title", "")
    artist = record.get("artist", "")
    track = record.get("track", "")

    if not track:
        match = re.match(r"^\s*(.+?)\s+-\s+(.+?)\s*$", video_title)
        if match:
            artist = artist or match.group(1).strip()
            track = match.group(2).strip()
        else:
            track = video_title

    suffix = r"\s*[\(\[]\s*(?:official(?:\s+music)?\s+video|official\s+audio|audio|lyrics?|hq|hd|4k)\b[^\)\]]*[\)\]]\s*$"
    track = re.sub(suffix, "", track, flags=re.IGNORECASE).strip() or video_title
    record["artist"] = artist
    record["track"] = track
    return record


def legacy_last(state_dir):
    path = state_dir / "last-played"
    if not path.exists():
        return None
    values = path.read_text().splitlines()
    values += [""] * (5 - len(values))
    return {
        "played_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "video_title": values[0],
        "artist": values[1],
        "track": values[2],
        "uploader": values[3],
        "source_url": values[4],
    }


def load_last(state_dir):
    path = state_dir / "last.json"
    if path.exists():
        return json.loads(path.read_text())
    return legacy_last(state_dir)


def load_history(state_dir):
    path = state_dir / "history.jsonl"
    records = []
    if path.exists():
        for line in path.read_text().splitlines():
            if line:
                records.append(json.loads(line))
    if not records:
        record = legacy_last(state_dir)
        if record:
            records.append(record)

    unique = []
    seen = set()
    for record in reversed(records):
        key = record.get("source_url") or record.get("video_title")
        if key in seen:
            continue
        seen.add(key)
        unique.append(normalize_record(record))
    return unique


def display_name(record):
    if record.get("artist"):
        return f"{record['artist']} - {record['track']}"
    return record["track"]


def remember(args):
    state_dir = Path(args.state_dir)
    state_dir.mkdir(parents=True, exist_ok=True)
    history_path = state_dir / "history.jsonl"
    previous_record = legacy_last(state_dir) if not history_path.exists() else None
    record = {
        "played_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "video_title": args.video_title,
        "artist": args.artist,
        "track": args.track,
        "uploader": args.uploader,
        "source_url": args.source_url,
    }
    record = {key: clean(value) for key, value in record.items()}
    serialized = json.dumps(record, ensure_ascii=False)
    (state_dir / "last.json").write_text(serialized + "\n")
    with history_path.open("a") as history_file:
        if previous_record:
            history_file.write(json.dumps(previous_record, ensure_ascii=False) + "\n")
        history_file.write(serialized + "\n")


def slugify(value):
    normalized = unicodedata.normalize("NFKC", value).lower()
    slug = re.sub(r"[^\w\s-]", "", normalized)
    return re.sub(r"[-\s]+", "-", slug).strip("-_") or "liked-song"


def add_record(record, music_dir):
    record = normalize_record(record)
    artist = record.get("artist", "")
    track = record["track"]
    source_url = record.get("source_url", "")
    note_path = music_dir / f"{slugify(track)}.md"
    created = not note_path.exists()

    if created:
        lines = [f"# {track}", ""]
        if artist:
            lines.append(f"- 아티스트: {artist}")
        lines.extend(
            [
                f"- 기록한 날: {date.today().isoformat()}",
                f"- 원본: {source_url}",
                "",
                "## 좋아한 이유",
                "",
            ]
        )
        note_path.write_text("\n".join(lines))

    readme_path = music_dir / "README.md"
    content = readme_path.read_text() if readme_path.exists() else "# 좋아하는 음악\n"
    if "## 곡" not in content.splitlines():
        content = content.rstrip() + "\n\n## 곡\n"
    escaped_title = track.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")
    bullet = f"- [{escaped_title}]({note_path.name})"
    if f"]({note_path.name})" not in content:
        section_start = content.index("## 곡") + len("## 곡")
        next_heading = content.find("\n## ", section_start)
        if next_heading == -1:
            content = content.rstrip() + "\n\n" + bullet + "\n"
        else:
            prefix = content[:next_heading].rstrip()
            suffix = content[next_heading:].lstrip("\n")
            content = prefix + "\n" + bullet + "\n\n" + suffix
        readme_path.write_text(content)

    status = "추가됨" if created else "이미 등록됨"
    print(f"{status}: {display_name(record)}")
    print(note_path)


def add_last(args):
    state_dir = Path(args.state_dir)
    record = load_last(state_dir)
    if not record:
        raise SystemExit("최근 재생 기록이 없음. 먼저 listen으로 곡을 재생해 주세요.")
    add_record(record, Path(args.music_dir))


def history_lines(args):
    records = load_history(Path(args.state_dir))
    if not records:
        raise SystemExit("재생 기록이 없음. 먼저 listen으로 곡을 재생해 주세요.")
    for index, record in enumerate(records, start=1):
        played_at = record.get("played_at", "")[:16].replace("T", " ")
        print(f"{index}\t{played_at}\t{display_name(record)}")


def add_history(args):
    records = load_history(Path(args.state_dir))
    music_dir = Path(args.music_dir)
    for index in args.indices:
        if index < 1 or index > len(records):
            raise SystemExit(f"history 번호가 범위를 벗어남: {index}")
        add_record(records[index - 1], music_dir)


def parser():
    root = argparse.ArgumentParser()
    commands = root.add_subparsers(dest="command", required=True)

    remember_parser = commands.add_parser("remember")
    remember_parser.add_argument("state_dir")
    remember_parser.add_argument("video_title")
    remember_parser.add_argument("artist")
    remember_parser.add_argument("track")
    remember_parser.add_argument("uploader")
    remember_parser.add_argument("source_url")
    remember_parser.set_defaults(run=remember)

    add_last_parser = commands.add_parser("add-last")
    add_last_parser.add_argument("state_dir")
    add_last_parser.add_argument("music_dir")
    add_last_parser.set_defaults(run=add_last)

    history_parser = commands.add_parser("history-lines")
    history_parser.add_argument("state_dir")
    history_parser.set_defaults(run=history_lines)

    add_history_parser = commands.add_parser("add-history")
    add_history_parser.add_argument("state_dir")
    add_history_parser.add_argument("music_dir")
    add_history_parser.add_argument("indices", nargs="+", type=int)
    add_history_parser.set_defaults(run=add_history)
    return root


def main():
    args = parser().parse_args()
    args.run(args)


if __name__ == "__main__":
    main()
