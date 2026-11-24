# Chrome site-search shortcuts

Chrome 주소창의 사용자 검색 단축키를 JSON으로 보관하고 새 프로필에 병합한다.

## 파일

- [검색 단축키 JSON](../files/chrome/search-engines.json)은 검색 이름, 단축키, URL을 보관.
- [내보내기 및 복원 도구](../scripts/chrome-search-engines.py)는 Chrome 프로필의 검색 엔진을 읽거나 병합.

## 단축키 내보내기

현재 Chrome 프로필에서 사용자 단축키를 다시 읽는다. Chrome가 DB를 갱신 중이면 완전히
종료한 뒤 재실행한다.

```bash
scripts/chrome-search-engines.py export yt nv map hg translate st
```

내보낸 JSON을 공유할 때는 검색 URL과 프로필 이름을 확인.

## 새 프로필에 복원

Chrome를 한 번 실행해 프로필을 생성한 뒤 완전히 종료한다.

```bash
scripts/chrome-search-engines.py import
```

`Local State`의 최근 프로필을 자동 선택한다. 다른 프로필은 명시할 수 있다.

```bash
scripts/chrome-search-engines.py --profile 'Profile 2' import
```

같은 단축키가 있으면 갱신하고, 없으면 추가한다. 변경 전 `Web Data.backup-날짜`를 같은
프로필 디렉터리에 만든다. Chrome 전체 `Web Data` 파일을 이 저장소에 복사하지 않는다.
그 DB에는 검색 단축키 외의 자동완성 데이터도 들어 있다.
