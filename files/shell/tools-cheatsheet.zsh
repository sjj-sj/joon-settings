# `tools` — 설치/등록한 CLI 도구와 단축키 치트시트.
#   tools            전체 보기
#   tools <키워드>   해당 키워드 포함 행만 (예: tools git, tools 이동)
# 새 도구 추가하면 아래 rows 배열에 "카테고리|명령|설명" 한 줄 추가.
tools() {
  local filter="$1"
  local CAT=$'\e[1;95m' CMD=$'\e[93m' DIM=$'\e[2m' HEAD=$'\e[1;96m' R=$'\e[0m'
  local -a rows=(
    "이동|z <dir>|자주 간 폴더로 점프 (zsh-z)"
    "이동|z -|직전 폴더 (cd - 처럼)"
    "파일|ll  /  la|상세목록 / +숨김 (eza)"
    "파일|lg|+git 상태 컬럼 (eza --git)"
    "파일|ltree|트리 2단계 (eza --tree)"
    "파일|bat <file>|문법 하이라이트+줄번호 cat"
    "파일|bat -A / -r 5:20|공백표시 / 줄범위"
    "검색|fd <pat>|파일 찾기 (.gitignore 존중, 빠름)"
    "검색|fd -e py <pat>|확장자 필터 (-H=숨김포함)"
    "검색|rg <pat>|파일 내용 grep (ripgrep)"
    "검색|Ctrl-R|명령 히스토리 fzf 검색"
    "검색|Ctrl-T|파일 골라 커맨드라인에 삽입 (fzf)"
    "git|git diff / show / log -p|delta로 렌더 (자동 설정됨)"
    "git|delta: n / N|다음/이전 변경파일로 점프"
    "터미널|zj|zellij (별칭)"
    "터미널|zl|quad 4분할 레이아웃 새 세션"
    "터미널|zj -n <layout>|레이아웃으로 항상 새 세션"
    "터미널|zj a <sess>|세션 attach  (zj ls=목록)"
    "터미널|ztoy|현재 Zellij 오른쪽을 cava 위 / 시계 아래로 분할"
    "터미널|ztoy off|현재 탭의 cava + 시계 pane 닫기"
    "터미널|zcava|현재 탭 왼쪽 아래 tiled Cava 켜기/끄기"
    "터미널|Alt+h/j/k/l|팬/탭 포커스 이동"
    "화면/토이|saver [이름]|스크린세이버 런처 (인자 없으면 랜덤, saver help=목록)"
    "화면/토이|saverwall [위] [아래]|두 모니터 전체화면 위/아래 saver (인자 없으면 랜덤)"
    "화면/토이|pclock|화면에 맞춰 커지는 컬러 디지털 시계"
    "화면/토이|tclock|가운데 정렬된 고전 터미널 시계"
    "화면/토이|weather [지역] / wx|현재 날씨와 3일 예보 (기본 수원)"
    "화면/토이|wxn [지역]|현재 날씨 한 줄"
    "화면/토이|wxt [지역]|현재 날씨와 오늘 예보"
    "화면/토이|weathr|실제 날씨 기반 ASCII 애니메이션"
    "화면/토이|figlet <text>|큰 ASCII 배너 (| lolcat 로 무지개)"
    "화면/토이|toilet <text>|컬러 ASCII 배너 (-f 폰트)"
    "미디어|listen <곡명/URL>|YouTube 오디오 검색 및 터미널 재생"
    "미디어|listen add|마지막으로 들은 곡을 like에 추가"
    "미디어|listen history|최근 재생 목록에서 골라 like에 추가"
    "미디어|listen --likes|기록한 음악 목록 보기"
    "내 alias|rm <f>|trash-put (휴지통, 영구삭제 아님!)"
    "내 alias|ff|fastfetch (시스템 정보 배너)"
    "내 alias|ports / port <N>|리스닝 포트 / 특정 포트 누가 쓰나"
    "내 alias|k|kubectl"
    "내 alias|uvr|uv run"
    "내 alias|activate|source .venv/bin/activate"
    "도움말|tldr <cmd>|예제 위주 요약 man (오프라인)"
    "도움말|tools [kw]|이 치트시트"
  )

  printf '%s╭─ tools ─ 내 CLI 치트시트 %s%s(tools <키워드>로 필터)%s\n' "$HEAD" "$DIM" "" "$R"

  # 최대 명령 폭 계산 (정렬용)
  local w=0 row cmd
  for row in "${rows[@]}"; do
    cmd="${${row#*|}%|*}"
    (( ${#cmd} > w )) && w=${#cmd}
  done

  local prev="" cat rest desc
  for row in "${rows[@]}"; do
    cat="${row%%|*}"; rest="${row#*|}"; cmd="${rest%%|*}"; desc="${rest#*|}"
    if [[ -n "$filter" ]]; then
      [[ "${row:l}" == *"${filter:l}"* ]] || continue   # 대소문자 무시
    fi
    if [[ "$cat" != "$prev" ]]; then
      printf '\n%s%s%s\n' "$CAT" "$cat" "$R"
      prev="$cat"
    fi
    printf '  %s%-*s%s  %s%s%s\n' "$CMD" "$w" "$cmd" "$R" "$DIM" "$desc" "$R"
  done
  printf '\n'
}
