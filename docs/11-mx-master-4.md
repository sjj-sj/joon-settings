# Ubuntu에서 MX Master 4 설정

Ubuntu 24.04.5, GNOME 46/X11, Logi Bolt, Solaar 1.1.17에서 사용한 설정입니다.

| 입력 | 동작 | Solaar 키 입력 |
| --- | --- | --- |
| 제스처 버튼 짧게 누르기 | GNOME 활동 개요 | `Super_L` |
| 제스처 버튼을 누른 채 왼쪽으로 이동 후 놓기 | 이전 작업공간 | `Super_L`, `Page_Up` |
| 제스처 버튼을 누른 채 오른쪽으로 이동 후 놓기 | 다음 작업공간 | `Super_L`, `Page_Down` |
| 제스처 버튼을 누른 채 위로 이동 후 놓기 | 현재 창 최대화 | `Super_L`, `Up` |
| 제스처 버튼을 누른 채 아래로 이동 후 놓기 | 최대화 해제 | `Super_L`, `Down` |
| 햅틱 패널 누르기 | GNOME 캡처 화면 열기 | `Print` |

## Solaar에서 적용

1. **Key/Button Diversion**에서 `Mouse Gesture Button`을 `Mouse Gestures`, `Haptic`을 `Diverted`로 지정.
2. **Rule Editor**에서 MX Master 4 장치 조건과 표의 동작을 추가. 짧게 누르기는 `Mouse Gesture Button`만 지정하고 방향을 생략. 햅틱 패널은 `Haptic`의 누름 이벤트 사용.
3. [Solaar 규칙 예시](../files/config/solaar/mx-master-4.rules.yaml)를 직접 사용할 경우 `~/.config/solaar/rules.yaml`에 병합 후 Solaar 재시작. 같은 버튼의 기존 규칙은 새로 추가하기 전에 확인.

GNOME 키보드 단축키를 바꿨다면 표의 키 입력을 해당 단축키에 맞춥니다. 캡처 화면에서 영역을 지정한 뒤 하단의 원형 셔터를 클릭하거나 `Enter`를 눌러 촬영합니다.

[Solaar 규칙 문서](https://pwr-solaar.github.io/Solaar/rules/) / [GNOME 캡처 도움말](https://help.gnome.org/gnome-help/screen-shot-record.html)
