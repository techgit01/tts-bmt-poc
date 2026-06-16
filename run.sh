#!/usr/bin/env bash
# run.sh — 벤치마크 실행 + (옵션) 로컬 데모 미리보기
#
#   ./run.sh                    # 벤치마크 실행 → docs/results, docs/audio 갱신
#   ./run.sh --serve [PORT]     # 실행 후 로컬 웹서버로 데모 미리보기 (기본 8000)
#   ./run.sh --list             # 엔진 목록/설치 상태만 출력
#
# 플래그는 순서 무관이며, 알 수 없는 옵션은 오류로 알립니다.
set -euo pipefail

cd "$(dirname "$0")"

# uv 설치 위치 보강 (env 파일 우선 + 흔한 경로 fallback)
for env_file in "$HOME/.local/bin/env" "$HOME/.cargo/env"; do
  [ -f "$env_file" ] && . "$env_file"
done
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
if ! command -v uv >/dev/null 2>&1; then
  echo "✗ uv 가 없습니다. 먼저 ./setup.sh 를 실행하세요." >&2
  exit 1
fi

# --- 인자 파싱 (순서 무관 / 오타 감지) -------------------------------
SERVE=0
LIST=0
PORT=8000
while [[ $# -gt 0 ]]; do
  case "$1" in
    --list)  LIST=1; shift ;;
    --serve) SERVE=1; shift
             # --serve 다음 토큰이 숫자면 포트로 사용
             if [[ "${1:-}" =~ ^[0-9]+$ ]]; then PORT="$1"; shift; fi ;;
    -h|--help)
      grep '^#' "$0" | grep -v '^#!' | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "✗ 알 수 없는 옵션: $1 (사용법: ./run.sh --help)" >&2; exit 1 ;;
  esac
done

if [[ "$LIST" -eq 1 ]]; then
  uv run tts-bmt list
  exit 0
fi

echo "==> 벤치마크 실행"
uv run tts-bmt run

if [[ "$SERVE" -eq 1 ]]; then
  echo
  echo "==> 데모 미리보기: http://localhost:${PORT}  (Ctrl+C 로 종료)"
  cd docs && uv run python -m http.server "${PORT}"
fi
