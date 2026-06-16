#!/usr/bin/env bash
# deploy.sh — 산출물 갱신 후 GitHub 에 배포
#
#   ./deploy.sh                 # 벤치마크 재실행 → docs/ 갱신 → 커밋 → main 푸시
#   ./deploy.sh -m "메시지"      # 커밋 메시지 지정
#   ./deploy.sh --no-run        # 재측정 없이 현재 docs/ 그대로 커밋·푸시
#
# 푸시되면 .github/workflows/deploy.yml 이 자동으로 돌아
# GitHub Pages( https://techgit01.github.io/tts-bmt-poc/ )로 배포됩니다.
set -euo pipefail

cd "$(dirname "$0")"
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

MSG=""
DO_RUN=1
while [[ $# -gt 0 ]]; do
  case "$1" in
    -m|--message) MSG="${2:-}"; shift 2 ;;
    --no-run)     DO_RUN=0; shift ;;
    *) echo "알 수 없는 옵션: $1" >&2; exit 1 ;;
  esac
done

# 사전 점검 -----------------------------------------------------------
if [[ ! -d .git ]]; then
  echo "✗ git 저장소가 아닙니다. 먼저 'git init' 후 origin 을 설정하세요." >&2
  exit 1
fi
if ! git remote get-url origin >/dev/null 2>&1; then
  echo "✗ origin 원격이 없습니다. 'git remote add origin <URL>' 후 다시 실행하세요." >&2
  exit 1
fi

# 1) 산출물 갱신 ------------------------------------------------------
if [[ "$DO_RUN" -eq 1 ]]; then
  if ! command -v uv >/dev/null 2>&1; then
    echo "✗ uv 가 없습니다. 먼저 ./setup.sh 를 실행하거나 --no-run 으로 실행하세요." >&2
    exit 1
  fi
  echo "==> [1/3] 벤치마크 실행 → docs/ 갱신"
  uv run tts-bmt run
else
  echo "==> [1/3] 재측정 건너뜀 (--no-run)"
fi

# 2) 커밋 -------------------------------------------------------------
echo "==> [2/3] 변경사항 커밋"
git add docs
if git diff --cached --quiet; then
  echo "    docs/ 변경 없음 → 빈 커밋 없이 푸시만 진행"
else
  if [[ -z "$MSG" ]]; then
    MSG="Deploy: refresh benchmark results and demo"
  fi
  git commit -q -m "$MSG"
  echo "    커밋: $MSG"
fi

# 3) 푸시 (Actions 가 Pages 배포) ------------------------------------
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
echo "==> [3/3] origin/${BRANCH} 푸시 → GitHub Actions 가 Pages 배포"
git push origin "$BRANCH"

echo
echo "✓ 푸시 완료. 배포 진행 상황: $(git remote get-url origin | sed 's/\.git$//')/actions"
echo "✓ 배포 URL: https://techgit01.github.io/tts-bmt-poc/"
