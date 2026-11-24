# 오디오 도구

`listen`은 터미널에서 YouTube 오디오를 찾아 재생하고, 좋아하는 곡을 Markdown으로 기록합니다.

```bash
scripts/install-listen.sh
```

설치기는 `~/.local/bin/listen`을 [`files/listen/listen`](../files/listen/listen)에 연결합니다. 실행에는 Bash, Python 3, Node.js, `yt-dlp`, VLC의 `cvlc`가 필요합니다. `fzf`가 있으면 재생 이력에서 곡을 선택할 수 있습니다.

```bash
listen "곡명 또는 URL"
listen add
listen history
listen --likes
```

재생 중 `Space`로 일시정지 또는 재개, 좌우 화살표로 5초 이동, 위아래 화살표로 볼륨 조절, `a`로 곡 기록, `q`로 종료합니다.

- 재생 이력 및 볼륨은 `${XDG_STATE_HOME:-$HOME/.local/state}/listen/`에 저장.
- 음악 노트는 기본적으로 `${XDG_DATA_HOME:-$HOME/.local/share}/listen/music/`에 저장. 기존 음악 노트가 있다면 `LISTEN_LIKE_DIR`을 `music/`의 상위 디렉터리로 지정.
