#!/usr/bin/env python3

import argparse
from contextlib import suppress
import os
from pathlib import Path
import re
import select
import shutil
import socket
import subprocess
import sys
import tempfile
import termios
import time
import tty


def parser():
    result = argparse.ArgumentParser()
    result.add_argument("title")
    result.add_argument("source_url")
    result.add_argument("media_url")
    result.add_argument("state_dir")
    result.add_argument("music_dir")
    result.add_argument("state_helper")
    return result


def connect_control(socket_path, process):
    control = socket.socket(socket.AF_UNIX)
    for _ in range(60):
        if process.poll() is not None:
            raise RuntimeError("VLC가 재생을 시작하지 못했습니다.")
        try:
            control.connect(socket_path)
            control.setblocking(False)
            return control
        except (FileNotFoundError, ConnectionRefusedError):
            time.sleep(0.05)
    raise RuntimeError("VLC 제어 소켓에 연결하지 못했습니다.")


def receive(control, timeout):
    chunks = []
    deadline = time.monotonic() + timeout
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        readable, _, _ = select.select([control], [], [], remaining)
        if not readable:
            break
        chunk = control.recv(8192)
        if not chunk:
            break
        chunks.append(chunk)
    return b"".join(chunks).decode(errors="replace")


def command(control, value, timeout=0.08):
    receive(control, 0.001)
    control.sendall((value + "\n").encode())
    return receive(control, timeout)


def numeric_response(response):
    values = re.findall(r"(?m)^(\d+)\r?$", response)
    return int(values[-1]) if values else None


def format_time(seconds):
    seconds = max(0, seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


def clipped(value, width):
    if len(value) <= width:
        return value
    return value[: max(1, width - 1)] + "…"


def load_volume(state_dir):
    volume_path = Path(state_dir) / "volume"
    if not volume_path.exists():
        return 100
    return min(100, max(0, int(volume_path.read_text().strip())))


def save_volume(state_dir, volume):
    state_path = Path(state_dir)
    state_path.mkdir(parents=True, exist_ok=True)
    (state_path / "volume").write_text(f"{volume}\n")


def vlc_volume(volume):
    return round(volume * 256 / 100)


def draw(title, source_url, position, duration, paused, volume, message):
    width = shutil.get_terminal_size((80, 24)).columns
    bar_width = min(60, max(10, width - 18))
    ratio = min(1.0, position / duration) if duration else 0
    filled = round(bar_width * ratio)
    bar = "█" * filled + "░" * (bar_width - filled)
    state = "⏸ 일시정지" if paused else "▶ 재생 중"
    timing = f"{format_time(position)} / {format_time(duration)}"
    lines = [
        clipped(f"♫ {title}", width),
        "",
        clipped(f"{state}  {timing}  볼륨 {volume}%", width),
        clipped(f"[{bar}]", width),
        clipped(f"URL  {source_url}", width),
        "",
        clipped("Space 일시정지/재개   ←/→ 5초   ↑/↓ 볼륨   a like 추가   q 종료", width),
    ]
    if message:
        lines.extend(["", clipped(message, width)])
    sys.stdout.write("\033[H" + "\n".join(lines) + "\033[J")
    sys.stdout.flush()


def add_like(args):
    result = subprocess.run(
        [
            sys.executable,
            args.state_helper,
            "add-last",
            args.state_dir,
            args.music_dir,
        ],
        capture_output=True,
        text=True,
    )
    output = result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
    return output.splitlines()[0] if output else "like 추가 실패"


def run(args):
    with tempfile.TemporaryDirectory(prefix="listen-") as temporary_dir:
        socket_path = str(Path(temporary_dir) / "vlc.sock")
        process = subprocess.Popen(
            [
                "cvlc",
                "--intf",
                "oldrc",
                "--rc-fake-tty",
                "--rc-unix",
                socket_path,
                "--play-and-exit",
                "--no-video",
                "--network-caching=2500",
                "--quiet",
                args.media_url,
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        control = connect_control(socket_path, process)
        volume = load_volume(args.state_dir)
        command(control, f"volume {vlc_volume(volume)}")
        input_fd = os.open("/dev/tty", os.O_RDONLY | os.O_NONBLOCK)
        previous_terminal = termios.tcgetattr(input_fd)
        position = 0
        duration = 0
        paused = False
        message = ""
        message_until = 0.0

        sys.stdout.write("\033[?1049h\033[?25l")
        sys.stdout.flush()
        tty.setcbreak(input_fd)

        try:
            while process.poll() is None:
                current = numeric_response(command(control, "get_time"))
                length = numeric_response(command(control, "get_length"))
                if current is not None:
                    position = current
                if length is not None:
                    duration = length
                if message and time.monotonic() >= message_until:
                    message = ""
                draw(
                    args.title,
                    args.source_url,
                    position,
                    duration,
                    paused,
                    volume,
                    message,
                )

                readable, _, _ = select.select([input_fd], [], [], 0.08)
                if not readable:
                    continue
                key = os.read(input_fd, 1).decode(errors="ignore")
                if key == "\x1b":
                    readable, _, _ = select.select([input_fd], [], [], 0.02)
                    if readable:
                        key += os.read(input_fd, 2).decode(errors="ignore")

                if key in ("q", "Q"):
                    break
                if key == " ":
                    command(control, "pause")
                    paused = not paused
                elif key in ("\x1b[D", "h"):
                    was_paused = paused
                    if was_paused:
                        command(control, "pause")
                    command(control, f"seek {max(0, position - 5)}")
                    if was_paused:
                        command(control, "pause")
                elif key in ("\x1b[C", "l"):
                    was_paused = paused
                    if was_paused:
                        command(control, "pause")
                    destination = position + 5
                    if duration:
                        destination = min(duration, destination)
                    command(control, f"seek {destination}")
                    if was_paused:
                        command(control, "pause")
                elif key == "\x1b[A":
                    volume = min(100, volume + 5)
                    command(control, f"volume {vlc_volume(volume)}")
                    save_volume(args.state_dir, volume)
                elif key == "\x1b[B":
                    volume = max(0, volume - 5)
                    command(control, f"volume {vlc_volume(volume)}")
                    save_volume(args.state_dir, volume)
                elif key in ("a", "A"):
                    message = add_like(args)
                    message_until = time.monotonic() + 3
        finally:
            termios.tcsetattr(input_fd, termios.TCSADRAIN, previous_terminal)
            os.close(input_fd)
            with suppress(OSError):
                command(control, "quit", timeout=0.02)
            control.close()
            with suppress(subprocess.TimeoutExpired):
                process.wait(timeout=1)
            if process.poll() is None:
                process.terminate()
                with suppress(subprocess.TimeoutExpired):
                    process.wait(timeout=1)
            if process.poll() is None:
                process.kill()
            sys.stdout.write("\033[?25h\033[?1049l")
            sys.stdout.flush()


def main():
    run(parser().parse_args())


if __name__ == "__main__":
    main()
