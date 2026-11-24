# 셸과 oh-my-zsh

`oh-my-zsh`에서 Git, 자동 제안, 구문 강조, 디렉터리 이동과 압축 해제 플러그인을 사용하는 설정입니다.

```bash
scripts/install-omz.sh
```

설치기는 기존 `.zshrc`를 보존하고 [플러그인 목록](../files/shell/plugins.txt)에 있는 플러그인을 가져옵니다. [셸 설정 예시](../files/shell/zshrc.sample)에서 쓸 항목을 `~/.zshrc`에 옮깁니다.

- `Ctrl+Space`로 현재 자동 제안 수락
- `~/.local/bin`을 `PATH` 앞에 두어 사용자 런처 실행
- `~/.zsh/my-zshrc/`에 있는 `.zsh` 모듈 로드
- `ports`로 리스닝 포트 확인, `port <번호>`로 해당 포트의 프로세스 확인

테마를 고정하려면 `ZSH_THEME`에 이름을 지정합니다. `rm` 별칭에는 `trash-cli`, `ff`에는 `fastfetch`가 필요합니다. `saver`와 `tools` 모듈은 [터미널 도구 설치기](08-terminal-fun.md)에서 설치합니다.
