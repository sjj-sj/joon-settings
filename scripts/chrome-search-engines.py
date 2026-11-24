#!/usr/bin/env python3

import argparse
import json
import os
import shutil
import sqlite3
import tempfile
import uuid
from datetime import UTC, datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = REPO_ROOT / "files/chrome/search-engines.json"
DEFAULT_USER_DATA = Path(
    os.environ.get("CHROME_USER_DATA_DIR", "~/.config/google-chrome")
).expanduser()


def active_profile(user_data: Path, requested: str | None) -> str:
    if requested:
        return requested
    state = json.loads((user_data / "Local State").read_text())
    return state["profile"]["last_used"]


def web_data_path(user_data: Path, profile: str | None) -> tuple[str, Path]:
    profile = active_profile(user_data, profile)
    path = user_data / profile / "Web Data"
    if not path.exists():
        raise SystemExit(f"Web Data가 없습니다: {path}\nChrome 프로필을 한 번 연 뒤 종료하세요.")
    return profile, path


def chrome_is_running() -> bool:
    names = {"chrome", "google-chrome", "google-chrome-stable", "chromium", "chromium-browser"}
    for cmdline in Path("/proc").glob("[0-9]*/cmdline"):
        try:
            executable = cmdline.read_bytes().split(b"\0", 1)[0]
        except (FileNotFoundError, PermissionError):
            continue
        if Path(os.fsdecode(executable)).name in names:
            return True
    return False


def chrome_time() -> int:
    return int(datetime.now(UTC).timestamp() * 1_000_000) + 11_644_473_600_000_000


def open_export_snapshot(path: Path) -> tuple[tempfile.TemporaryDirectory[str], sqlite3.Connection]:
    journal = path.with_name(path.name + "-journal")
    tmp = tempfile.TemporaryDirectory()
    snapshot = Path(tmp.name) / path.name
    for _ in range(5):
        before = (path.stat().st_mtime_ns, path.stat().st_size)
        journal_before = journal.stat().st_size if journal.exists() else 0
        shutil.copy2(path, snapshot)
        after = (path.stat().st_mtime_ns, path.stat().st_size)
        journal_after = journal.stat().st_size if journal.exists() else 0
        if before == after and journal_before == journal_after == 0:
            connection = sqlite3.connect(snapshot)
            if connection.execute("pragma quick_check").fetchone()[0] == "ok":
                return tmp, connection
            connection.close()
    tmp.cleanup()
    raise SystemExit("Chrome가 Web Data를 갱신 중입니다. Chrome를 완전히 종료한 뒤 다시 실행하세요.")


def export_engines(args: argparse.Namespace) -> None:
    profile, path = web_data_path(args.user_data, args.profile)
    tmp, connection = open_export_snapshot(path)
    with tmp, connection:
        columns = {row[1] for row in connection.execute("pragma table_info(keywords)")}
        wanted = [
            name
            for name in (
                "short_name",
                "keyword",
                "url",
                "favicon_url",
                "suggest_url",
                "input_encodings",
                "originating_url",
            )
            if name in columns
        ]
        conditions = ["starter_pack_id = 0", "prepopulate_id = 0", "created_by_policy = 0"]
        parameters: list[str] = []
        if args.shortcuts:
            placeholders = ",".join("?" for _ in args.shortcuts)
            conditions.append(f"keyword in ({placeholders})")
            parameters.extend(args.shortcuts)
        else:
            conditions.extend(["instr(keyword, '.') = 0", "keyword not like '@%'"])
        query = (
            f"select {','.join(wanted)} from keywords "
            f"where {' and '.join(conditions)} order by id"
        )
        engines = []
        for row in connection.execute(query, parameters):
            data = dict(zip(wanted, row))
            engines.append(
                {
                    "name": data.pop("short_name"),
                    "shortcut": data.pop("keyword"),
                    **data,
                }
            )

    payload = {"version": 1, "source_profile": profile, "engines": engines}
    args.config.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(f"{len(engines)}개 저장: {args.config}")


def backup_database(connection: sqlite3.Connection, path: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = path.with_name(f"{path.name}.backup-{stamp}")
    with sqlite3.connect(backup_path) as backup:
        connection.backup(backup)
    return backup_path


def insert_engine(
    connection: sqlite3.Connection,
    columns: set[str],
    engine: dict[str, object],
) -> None:
    now = chrome_time()
    values: dict[str, object] = {
        "id": connection.execute("select coalesce(max(id), 0) + 1 from keywords").fetchone()[0],
        "short_name": engine["name"],
        "keyword": engine["shortcut"],
        "favicon_url": engine.get("favicon_url", ""),
        "url": engine["url"],
        "safe_for_autoreplace": 0,
        "originating_url": engine.get("originating_url", ""),
        "date_created": now,
        "usage_count": 0,
        "input_encodings": engine.get("input_encodings", ""),
        "suggest_url": engine.get("suggest_url", ""),
        "prepopulate_id": 0,
        "created_by_policy": 0,
        "last_modified": now,
        "sync_guid": str(uuid.uuid4()),
        "alternate_urls": "[]",
        "image_url": "",
        "search_url_post_params": "",
        "suggest_url_post_params": "",
        "image_url_post_params": "",
        "new_tab_url": "",
        "last_visited": 0,
        "created_from_play_api": 0,
        "is_active": 1,
        "starter_pack_id": 0,
        "enforced_by_policy": 0,
        "featured_by_policy": 0,
        "url_hash": None,
    }
    values = {key: value for key, value in values.items() if key in columns}
    names = ",".join(values)
    placeholders = ",".join("?" for _ in values)
    connection.execute(
        f"insert into keywords ({names}) values ({placeholders})",
        list(values.values()),
    )


def update_engine(connection: sqlite3.Connection, engine: dict[str, object]) -> None:
    connection.execute(
        """
        update keywords
        set short_name = ?, url = ?, favicon_url = ?, suggest_url = ?,
            input_encodings = ?, originating_url = ?, last_modified = ?,
            safe_for_autoreplace = 0, is_active = 1, url_hash = null
        where keyword = ?
        """,
        (
            engine["name"],
            engine["url"],
            engine.get("favicon_url", ""),
            engine.get("suggest_url", ""),
            engine.get("input_encodings", ""),
            engine.get("originating_url", ""),
            chrome_time(),
            engine["shortcut"],
        ),
    )


def import_engines(args: argparse.Namespace) -> None:
    if chrome_is_running():
        raise SystemExit("Chrome가 실행 중입니다. 완전히 종료한 뒤 다시 실행하세요.")
    profile, path = web_data_path(args.user_data, args.profile)
    payload = json.loads(args.config.read_text())
    if payload["version"] != 1:
        raise SystemExit(f"지원하지 않는 파일 버전입니다: {payload['version']}")

    with sqlite3.connect(path) as connection:
        backup_path = backup_database(connection, path)
        columns = {row[1] for row in connection.execute("pragma table_info(keywords)")}
        added = 0
        updated = 0
        for engine in payload["engines"]:
            exists = connection.execute(
                "select 1 from keywords where keyword = ? limit 1",
                (engine["shortcut"],),
            ).fetchone()
            if exists:
                update_engine(connection, engine)
                updated += 1
            else:
                insert_engine(connection, columns, engine)
                added += 1

    print(f"{profile}: {added}개 추가, {updated}개 갱신")
    print(f"DB 백업: {backup_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Chrome 사이트 검색 단축키 백업/복원")
    parser.add_argument("--user-data", type=Path, default=DEFAULT_USER_DATA)
    parser.add_argument("--profile", help="예: Default, 'Profile 2'; 생략 시 최근 프로필")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    commands = parser.add_subparsers(dest="command", required=True)
    export = commands.add_parser("export", help="검색 단축키를 JSON으로 저장")
    export.add_argument("shortcuts", nargs="*", help="저장할 단축키, 생략 시 사용자 항목 자동 선택")
    export.set_defaults(func=export_engines)
    restore = commands.add_parser("import", help="JSON을 현재 Chrome 프로필에 병합")
    restore.set_defaults(func=import_engines)
    args = parser.parse_args()
    args.user_data = args.user_data.expanduser()
    args.config = args.config.expanduser().resolve()
    return args


if __name__ == "__main__":
    arguments = parse_args()
    arguments.func(arguments)
