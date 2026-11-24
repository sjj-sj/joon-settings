# Ubuntu 한글 입력 및 X11 클립보드 복원

Ubuntu 24.04.5 LTS/X11에서 진행한 IBus에서 kime로의 전환 및
연관 장애 대응 기록. 최초 목적은 **Alacritty에서 IBus Hangul 사용 시 발생한
자음/모음 순서 및 띄어쓰기 순서 깨짐 해결**. 이후 Zed의 XIM 조합 표시,
Zellij 아래에서 남아 있던 간헐적 공백 순서 문제, Zellij 자동 복사,
GUI 앱 실행 스크립트의 입력기 환경변수 문제까지 대응.

## 적용 범위 및 검증 상태

- 기존 작업 기록
  - kime v3.2.0 설치 및 패치한 `kime-xim`의 사용자 경로 설치, 데몬 재시작 완료
  - 실행 중 XIM 서버의 `~/.local/bin/kime-xim` 사용 확인
  - 오래된 `DISPLAY=:0`에서 복사 래퍼를 통한 클립보드 쓰기/읽기 확인
  - 추가 공백 수정 후 Xvfb의 Zellij 입력 시험 10회 모두 정상, 단독 Alacritty 3회 정상
  - 공백 수정을 포함한 새 바이너리의 실제 데스크톱 설치 및 kime 재시작 완료 기록
- 문서화 시점 재확인
  - 원본 패치, 실행 래퍼, `~/.xinputrc`, kime 및 Zellij 설정의 실제 파일 확인
  - `~/.xinputrc`의 `run_im kime`, kime 로그 레벨 `WARN` 확인
  - 추가 갱신에서 설치된 바이너리, 빌드 결과 및 실행 중 XIM 서버의 SHA-256 일치 확인
- **미완료**
  - Zed 완전 종료 및 재실행 후 실제 한글 조합, 멈춤 해소 확인
  - 실행 중 Zellij 세션에서 마우스 드래그 자동 복사 확인
  - ChatGPT 완전 종료 및 재실행 후 실제 한글 입력 확인
  - Chrome의 동일 증상 재현 및 수정 후 입력 확인
  - 공백 수정 적용 후 실제 화면에서 Alacritty 및 Zellij에 직접 입력하는 확인
    - Xvfb 결과는 화면에 보이지 않는 테스트이며 실제 화면 검증과 별개
- 범위 제한
  - Wayland 환경 미검증, 아래 디스플레이 탐색 및 `xsel`은 X11 전용
  - kime 패치의 upstream 보고 및 반영 미완료
  - 이 문서 추가는 설정 보관 작업이며 현재 머신의 재설치나 GUI 검증 완료를 의미하지 않음

## 보관 파일 및 출처

| 저장소 파일 | 용도 및 원본 |
|---|---|
| [kime 패치](../patches/kime/kime-xim-preedit-callbacks.patch) | Zed callback 수정 및 공백 Commit 묶음을 포함한 로컬 최신 패치 |
| [kime 설정](../files/config/kime/config.yaml) | `~/.config/kime/config.yaml` 스냅샷, 개인 단축키 포함 |
| [입력기 변수](../files/shell/kime-env.sh) | GUI 래퍼에 반영할 세 환경변수 |
| [복사 래퍼](../files/bin/zellij-copy) | `~/.local/bin/zellij-copy` 스냅샷 |
| [kime 라이선스](../patches/kime/LICENSE) | 원본 kime의 GPL-3.0, 패치 대상 패키지의 `GPL-3.0-or-later` 표시 참조 |

- 패치 기준: [Riey/kime](https://github.com/Riey/kime)의 v3.2.0
  - 정확한 소스 커밋: `2539caf368cf7a5a4a13ccaced3acf61f6a9ba42`
  - 대상: `src/frontends/xim/src/handler.rs`의 `handle_set_ic_values` 및 `handle_forward_event`
  - 파일명은 유지하되 최신 패치는 Zed 수정과 아래 공백 수정을 모두 포함

## kime 설치 및 세션 전환

- Ubuntu 24.04 amd64용 kime v3.2.0 패키지 사용
  - [고정 릴리스](https://github.com/Riey/kime/releases/tag/v3.2.0)의 배포판/아키텍처 일치 여부 확인
  - 전체 GTK/Qt 모듈은 배포 패키지로 설치, 이후 XIM 실행 파일만 패치 버전으로 교체
- 복원 예시, 저장소 루트에서 시작

```bash
sudo apt install /path/to/kime-v3.2.0_amd64_ubuntu-24.04.deb
im-config -n kime
mkdir -p ~/.config/kime
# 기존 파일이 있으면 별도 백업 후 필요한 값만 병합
cp -i files/config/kime/config.yaml ~/.config/kime/config.yaml
```

- 완전 로그아웃 및 재로그인 후 세션의 입력기 환경 확인
  - `GTK_IM_MODULE=kime`, `QT_IM_MODULE=kime`, `XMODIFIERS=@im=kime`
  - `~/.xinputrc`에 `run_im kime` 존재 확인
  - 환경변수 참고 파일: `files/shell/kime-env.sh`
  - 셸에서만 `source`하면 해당 셸의 자식에게만 적용되므로 데스크톱 세션과 별개
- 스냅샷의 개인 설정
  - 기본 Latin, 앱별 모드 상태, 두벌식
  - `Super-Space`, `AltR`, `Hangul` 등의 한영 전환키
  - `Noto Sans CJK KR` 폰트 사용, 대상 머신의 폰트 설치 여부 확인

## Zed 조합 표시 멈춤 및 kime-xim 패치

- 기존 조사에서 확인한 동작
  - Zed는 앱이 조합 문자열을 직접 그리는 `XIM PREEDIT_CALLBACKS` 사용
  - kime-xim은 `SetIcValues` 수신마다 preedit를 지우고 다시 그리는 동작
  - 조합 지움 → Zed 커서 이동 → 새 위치 통지 → preedit 재작성의 반복
    - x 좌표 `1039`와 `1055` 왕복, 4분간 `SetIcValues` 약 4.5만 회 기록
  - 한글 모드에서 멈춤, 조합 글자 미표시, 영어 전환 시 확정 글자 표시
  - 기존 기록상 Alacritty는 해당 callback 경로를 사용하지 않아 이 루프의 영향 없음
- 패치의 의도
  - 입력 스타일에 `PREEDIT_CALLBACKS`가 있으면 `handle_set_ic_values`에서 즉시 반환
  - callback 클라이언트의 위치 갱신에 따른 preedit 지움/재작성 차단
  - 다른 입력 스타일은 기존 `clear_preedit` 및 `preedit` 경로 유지
  - 실제 Zed 입력에 대한 효과는 미검증

## Alacritty 및 Zellij의 간헐적 공백 순서 문제

- kime 전환 후 추가 조사에서 확인한 별도 입력 순서 문제
  - 공백으로 조합을 끝내면 kime가 확정 글자 `요`를 Commit으로 전송하고 공백 키를 Alacritty로 반환
  - 추가 조사 기록상 Alacritty가 두 입력을 처리하는 순서가 간헐적으로 역전
  - 입력 추적에서 Alacritty가 Zellij에 전달한 바이트에 이미 순서 역전 존재
    - 해당 재현의 원인은 Zellij 및 kitty keyboard protocol 이전 경로로 판단
  - Zellij의 많은 화면 갱신이 Alacritty의 부하를 높여 더 자주 발생한다는 설명은 **추정, 미검증**
- 적용한 수정
  - `handle_forward_event`에서 공백 입력 후 다음 조건을 모두 만족하는 경우 처리
    - `KeyCode::Space`, `state.is_empty()`
    - 결과에 `HAS_COMMIT` 존재, `HAS_PREEDIT` 및 `CONSUMED` 부재
  - preedit 정리 후 확정 문자열과 공백을 합친 단일 Commit `요 ` 전송
  - 엔진의 commit 버퍼 정리 및 `engine_ready` 갱신 후 이벤트 소비, 공백의 이중 전송 방지
  - 조건 밖의 입력은 기존 `process_input_result` 경로 유지
- 중간 시도 및 최종 선택 이유
  - 공백을 별도 Commit으로 보내는 시도에서도 두 Commit 사이의 순서 역전 발생
  - 별도 Commit 방식의 Zellij 시험 10회 중 4회 실패, 최종 패치에는 미포함

### Xvfb 검증 기록

아래 수치는 사용자가 전달한 추가 조사 결과이며 각 셀은 **실패 횟수/시도 횟수**.
수정 전 Zellij는 전달받은 두 묶음의 결과를 그대로 표기.

| 조건 | Zellij 아래 Alacritty | 단독 Alacritty |
|---|---|---|
| 수정 전 | 3/10 실패, 3/10 실패 | 0/10 실패 |
| 공백을 별도 Commit으로 전송 | 4/10 실패 | 0/3 실패 |
| 확정 글자와 공백을 단일 Commit으로 전송, 적용본 | 0/10 실패 | 0/3 실패 |

- 화면에 보이지 않는 Xvfb 테스트에서 최종 적용본의 정상 입력 확인 기록
- 테스트용 Xvfb 환경 종료 완료 기록
- **실제 화면에서 직접 입력하는 확인은 미완료**, 위 결과를 데스크톱 수동 검증으로 해석하지 않음

## 통합 패치 빌드 및 운영

### 고정 소스에 패치 적용 및 빌드

Rust/Cargo 및 C 컴파일러, `pkg-config`, `libclang` 등은 고정 소스의
`README.md` 빌드 종속성 참조. 아래는 전체 GTK/Qt 재빌드 없이 XIM 패키지만 빌드하는 경로.
이 저장소 루트에서 실행하고, `kime_src`는 소스를 받을 새 디렉터리로 지정.

```bash
(
set -eu
setup_repo="$PWD"
kime_src="$HOME/kime-v3.2.0-source"
git clone --branch v3.2.0 --depth 1 https://github.com/Riey/kime.git "$kime_src"
cd "$kime_src"
test "$(git rev-parse HEAD)" = 2539caf368cf7a5a4a13ccaced3acf61f6a9ba42
git apply --check "$setup_repo/patches/kime/kime-xim-preedit-callbacks.patch"
git apply "$setup_repo/patches/kime/kime-xim-preedit-callbacks.patch"
cargo build --release --locked -p kime-xim
mkdir -p ~/.local/bin
# 기존 사용자 바이너리가 있으면 먼저 별도 백업
install -m 755 target/release/kime-xim ~/.local/bin/kime-xim
)
```

- 데몬이 상속한 `PATH`에서 `~/.local/bin`이 `/usr/bin`보다 앞에 있어야 하는 조건
  - 데몬 소스의 모듈 실행은 절대경로 대신 실행 파일 이름 사용
  - 셸의 `command -v kime-xim` 확인만으로 데몬의 실제 실행 경로를 보장할 수 없음
- 조합 중 작업을 마친 뒤 기존 kime 데몬 종료 및 재실행
  - 재로그인으로 세션 환경까지 갱신하는 경로 권장
  - 데몬 재시작은 기존 앱의 XIM 연결을 끊으므로 Zed도 완전히 종료 후 재실행 필요
- 실제 실행 파일 확인

```bash
pgrep -u "$USER" -a -x kime-xim
for pid in $(pgrep -u "$USER" -x kime-xim); do
    readlink "/proc/$pid/exe"
done
```

### 로그 및 업그레이드, 롤백

- 기본 로그 레벨은 스냅샷의 `log.global_level: WARN` 유지
  - 기존 DEBUG 조사에서 `/run/user/$UID/kime.err`가 4분에 약 15MB 증가
  - `/run/user/$UID`는 RAM 기반 tmpfs, DEBUG는 짧은 재현 구간에만 사용 후 원복
- **apt 업그레이드 후에도 사용자 바이너리가 시스템 바이너리보다 우선하는 조건**
  - 새 버전에 패치가 필요한지 먼저 확인 후 재빌드 또는 사용자 override 해제 필요
  - 기존 패치를 다른 버전에 그대로 적용해도 안전하다는 보장 없음
- override 롤백
  - `~/.local/bin/kime-xim`을 별도 백업 경로로 이동
  - kime 데몬과 XIM 클라이언트 완전 재시작 후 `/proc/<pid>/exe`가 `/usr/bin/kime-xim`인지 확인
- IBus로 전체 전환을 되돌릴 경우
  - `im-config -n ibus`, 앱 래퍼의 세 변수를 `ibus`, `ibus`, `@im=ibus`로 복원
  - 로그아웃/재로그인 및 장기 실행 Zellij 세션, GUI 앱 재시작 필요
  - 최초 Alacritty 입력 순서 문제가 다시 나타날 가능성

## Zellij 드래그 자동 복사

- 기존 장애 원인
  - 기존 Zellij 서버가 재로그인 전 `DISPLAY=:0` 환경을 계속 보유
  - 현재 X 서버는 `:1`, 기존 `copy_command`의 `xsel` 연결 실패
  - `Ctrl+Shift` 드래그 및 `Ctrl+Shift+C`는 Alacritty가 직접 처리하므로 정상 동작
- 선택한 대응
  - 현재 DISPLAY 연결이 실패하면 본인 소유 `/tmp/.X11-unix/X*` 소켓을 순회
  - `xdpyinfo`로 실제 연결 가능한 DISPLAY를 찾은 뒤 `xsel --clipboard --input` 실행
  - 연결 가능한 디스플레이가 없으면 xsel 실패를 그대로 반환
  - 기존 Alacritty OSC52 회피 방침 유지
- 복원 예시

```bash
sudo apt install xsel x11-utils
install -Dm755 files/bin/zellij-copy ~/.local/bin/zellij-copy
```

`~/.config/zellij/config.kdl`의 기존 활성 항목을 아래 값으로 교체 또는 병합.
중복 `copy_command` 추가 금지. Zellij 서버 PATH에 `~/.local/bin` 포함 필요.

```kdl
copy_command "zellij-copy"
copy_on_select true
```

- 기존 `scripts/install-zellij-clipboard.py`는 직접 xsel 실행 설정을 추가하는 이전 경로
  - 현재 복원 절차의 래퍼 설치 및 설정 병합을 별도로 적용할 필요
  - 기존 사용자 `copy_command`가 있으면 보존하는 스크립트 동작 유지
- 한계
  - `XAUTHORITY`는 상속값 사용, 인증 파일도 오래되었으면 DISPLAY 탐색만으로 복구 불가
  - 여러 X 세션이 동시에 연결 가능하면 첫 번째 연결 가능 소켓 선택, 원하는 세션 보장 불가
  - Wayland의 `wl-copy` 대체 기능 미포함
- 기존 서버의 설정 재반영 및 드래그 복사는 미확인
  - 작업을 정리한 후 기존 Zellij 세션 재생성으로 환경 갱신 권장
  - 오래된 서버에서 새 셸을 열어도 DISPLAY 및 입력기 변수를 계속 상속할 수 있는 조건

## GUI 앱의 입력기 환경변수

- 앱 실행 스크립트가 `GTK_IM_MODULE`, `QT_IM_MODULE`, `XMODIFIERS`를 IBus로 고정하면 세션의 kime 설정을 덮어쓰는 문제 발생
- 해당 스크립트의 기존 `exec` 전에 아래 세 줄 반영
  - 환경변수 참고 파일 `files/shell/kime-env.sh`와 동일한 내용
  - 기존 앱 실행 옵션은 보존하고 입력기 변수만 변경

```bash
export GTK_IM_MODULE=kime
export QT_IM_MODULE=kime
export XMODIFIERS=@im=kime
```

- 기존 실행 앱에는 변경 미적용
  - 백그라운드 프로세스를 포함한 완전 종료 후 재실행 필요
  - 이번 문서화에서 앱 강제 종료 및 재실행 미수행

## 수동 확인 항목

- Alacritty: 한글 문장 입력, 빠른 자음/모음 연속 입력, 띄어쓰기 및 한영 전환 시 순서 확인
- Zed: 완전 재실행 후 조합 중 글자 표시, 커서 이동, 한영 전환, 장시간 멈춤 여부 확인
- Zellij: 한글 조합 끝의 공백 순서 및 반복 입력 확인, 마우스 드래그 후 일반 GUI 앱에 붙여넣기, 새 세션의 DISPLAY 확인
- ChatGPT 및 Chrome: 완전 재실행 후 조합, 확정, 띄어쓰기 확인
- 문제 재발 시 짧게 DEBUG 로그 수집 후 WARN 복원
  - 앱 버전, X11/Wayland, 실행 경로, 프로세스 환경변수, XIM 실제 경로 함께 기록
