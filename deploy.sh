#!/usr/bin/env bash
# deploy.sh — 변경사항을 커밋하고 main 에 푸시 → GitHub Actions 가 빌드·배포
#
#   ./deploy.sh                 # 보류 중인 변경 커밋 후 main 푸시
#   ./deploy.sh -m "메시지"      # 커밋 메시지 지정
#   ./deploy.sh --preview       # 푸시 없이 로컬에서 docs/ 만 생성해 미리보기 안내
#
# 데모 음성(docs/audio, docs/results)은 Google Colab 에서 Supertonic 실측으로
# 생성해 '커밋'합니다. CI(.github/workflows/deploy.yml)는 재생성하지 않고
# 커밋된 docs/ 를 그대로 Pages 로 게시합니다. 배포 = main 푸시.
set -euo pipefail

cd "$(dirname "$0")"
for env_file in "$HOME/.local/bin/env" "$HOME/.cargo/env"; do
  [ -f "$env_file" ] && . "$env_file"
done
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

MSG="Deploy: update site"
PREVIEW=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    -m|--message)
      [[ $# -ge 2 ]] || { echo "✗ -m/--message 에 커밋 메시지가 필요합니다." >&2; exit 1; }
      MSG="$2"; shift 2 ;;
    --preview) PREVIEW=1; shift ;;
    -h|--help) grep '^#' "$0" | grep -v '^#!' | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "✗ 알 수 없는 옵션: $1" >&2; exit 1 ;;
  esac
done

# 로컬 미리보기 모드: 푸시 없이 docs/ 만 생성 안내 -----------------
if [[ "$PREVIEW" -eq 1 ]]; then
  command -v uv >/dev/null 2>&1 || { echo "✗ uv 가 없습니다. ./setup.sh 먼저." >&2; exit 1; }
  uv run tts-bmt run
  echo "✓ docs/ 생성 완료. 미리보기: ./run.sh --serve"
  exit 0
fi

# 사전 점검 (git 자체로 판별 — worktree/submodule 안전) ---------------
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "✗ git 저장소가 아닙니다. 'git init' 후 origin 을 설정하세요." >&2
  exit 1
fi
if ! git remote get-url origin >/dev/null 2>&1; then
  echo "✗ origin 원격이 없습니다. 'git remote add origin <URL>' 후 다시 실행하세요." >&2
  exit 1
fi

# 커밋 (보류 중 변경이 있을 때만) ------------------------------------
echo "==> 변경사항 커밋"
git add -A
if git diff --cached --quiet; then
  echo "    커밋할 변경 없음 → 푸시만 진행 (CI 재배포 트리거)"
else
  git commit -q -m "$MSG"
  echo "    커밋: $MSG"
fi

# 푸시 → Actions 가 빌드·배포 ----------------------------------------
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
echo "==> origin/${BRANCH} 푸시 → GitHub Actions 빌드·배포"
git push origin "$BRANCH"

REPO_URL="$(git remote get-url origin | sed -e 's/\.git$//' -e 's#git@github.com:#https://github.com/#')"
echo
echo "✓ 푸시 완료. 배포 진행: ${REPO_URL}/actions"
echo "✓ 배포 URL: https://techgit01.github.io/tts-bmt-poc/"
echo
echo "  ℹ️  .github/workflows/ 를 처음 푸시할 때는 토큰에 'workflow' 스코프가 필요합니다"
echo "     (gh auth refresh -s workflow). 이후 일반 푸시는 추가 스코프 불필요."
