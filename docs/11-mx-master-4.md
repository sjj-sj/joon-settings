# MX Master 4 설정

## Ubuntu

Ubuntu 24.04.5, GNOME 46/X11, Logi Bolt, Solaar 1.1.17에서 사용한 설정입니다.

| 입력 | 동작 | Solaar 키 입력 |
| --- | --- | --- |
| 제스처 버튼 짧게 누르기 | GNOME 활동 개요 | `Super_L` |
| 제스처 버튼을 누른 채 왼쪽으로 이동 후 놓기 | 이전 작업공간 | `Super_L`, `Page_Up` |
| 제스처 버튼을 누른 채 오른쪽으로 이동 후 놓기 | 다음 작업공간 | `Super_L`, `Page_Down` |
| 제스처 버튼을 누른 채 위로 이동 후 놓기 | 현재 창 최대화 | `Super_L`, `Up` |
| 제스처 버튼을 누른 채 아래로 이동 후 놓기 | 최대화 해제 | `Super_L`, `Down` |
| 햅틱 패널 누르기 | GNOME 캡처 화면 열기 | `Print` |

### Solaar에서 적용

1. **Key/Button Diversion**에서 `Mouse Gesture Button`을 `Mouse Gestures`, `Haptic`을 `Diverted`로 지정.
2. **Rule Editor**에서 MX Master 4 장치 조건과 표의 동작을 추가. 짧게 누르기는 `Mouse Gesture Button`만 지정하고 방향을 생략. 햅틱 패널은 `Haptic`의 누름 이벤트 사용.
3. [Solaar 규칙 예시](../files/config/solaar/mx-master-4.rules.yaml)를 직접 사용할 경우 `~/.config/solaar/rules.yaml`에 병합 후 Solaar 재시작. 같은 버튼의 기존 규칙은 새로 추가하기 전에 확인.

GNOME 키보드 단축키를 바꿨다면 표의 키 입력을 해당 단축키에 맞춥니다. 캡처 화면에서 영역을 지정한 뒤 하단의 원형 셔터를 클릭하거나 `Enter`를 눌러 촬영합니다.

[Solaar 규칙 문서](https://pwr-solaar.github.io/Solaar/rules/) / [GNOME 캡처 도움말](https://help.gnome.org/gnome-help/screen-shot-record.html)

## macOS

MacBook의 MX Master 4 Special Edition에서 Logi Options+와 Rectangle을 사용한 창 배치 설정. 방향 제스처는 엄지 쪽 빨간 제스처 버튼을 누른 채 마우스를 움직인 후 버튼을 놓아 실행.

| 입력 | 동작 | 키 입력 |
| --- | --- | --- |
| 제스처 버튼을 누른 채 왼쪽으로 이동 | 창을 왼쪽 절반에 배치 | `Control + Option + ←` |
| 제스처 버튼을 누른 채 오른쪽으로 이동 | 창을 오른쪽 절반에 배치 | `Control + Option + →` |
| 제스처 버튼을 누른 채 위로 이동 | 창 최대화 | `Control + Option + ↑` |
| 제스처 버튼을 누른 채 아래로 이동 | 이전 창 크기와 위치로 복원 | `Control + Option + ⌫` |
| 제스처 버튼 짧게 누르기 | Mission Control | — |
| 엄지 받침의 햅틱 패널 누르기 | Actions Ring 열기 | — |

### Logi Options+와 Rectangle에서 적용

1. Rectangle의 **키보드 단축키**에서 **왼쪽 절반**, **오른쪽 절반**, **최대화**, **복원**을 표의 키 조합으로 지정.
2. Logi Options+에서 **MX Master 4 → 버튼 → 빨간 제스처 버튼 → 제스처 → 사용자 지정** 선택. 네 방향에 **키보드 바로가기 키**로 표의 키 조합을 등록하고, **클릭**에 **Mission Control** 지정.
3. **글로벌 설정**, **Google Chrome**, **Visual Studio Code** 프로필에 같은 제스처 적용. 엄지 받침의 햅틱 패널에 **Actions Ring 표시** 지정.

[Logitech 제스처 버튼 안내](https://support.logi.com/hc/ko/articles/43003663765911-Getting-Started-MX-Master-4-Special-Edition) / [Rectangle](https://github.com/rxhanson/Rectangle)
