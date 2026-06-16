# 한국어 TTS 벤치마크 POC

> 중국 개발 엔진 제외 · 상업용 무료(MIT 계열) · 한국어 지원
> **uv + Python 3.12** 로 로컬 측정 → **GitHub Pages** 정적 데모로 결과/오디오 공개

🔊 **라이브 데모:** https://techgit01.github.io/tts-bmt-poc/
📦 **저장소:** https://github.com/techgit01/tts-bmt-poc

카드사 FDS(부정거래 탐지) 음성 상담을 가정한 한국어 문장으로, 오픈소스 TTS 4종을
같은 조건에서 합성하고 속도 지표를 측정합니다. 무거운 추론은 로컬에서 미리 돌려
오디오(`.wav`)와 측정 결과(`benchmark.json`)를 만들고, GitHub Pages에는 그 **정적
산출물만** 올려 브라우저에서 재생·비교합니다. (Pages는 서버 코드를 실행하지 않음)

---

## 비교 대상 4종

| # | 엔진 | 개발 | 라이선스 | 한국어 | 비고 |
|---|------|------|---------|--------|------|
| 1 | **Supertonic 3** | Supertone (KR) | MIT(code) + OpenRAIL-M(model) | 기본 지원 | 온디바이스 ~99M ONNX, CPU 실시간 |
| 2 | **piper-plus** | ayutaz (JP) | MIT | 8개 언어 중 포함 | VITS, 운율 주입, 음성 클로닝 |
| 3 | **kr-custom-tts** | seastar105 (KR) | MIT | 전용 | ESPnet, Colab 자가학습 |
| 4 | **SCE-TTS** | yunho0130 (KR) | MIT | 전용 | Tacotron2, Colab 가이드 |

> **라이선스 주의**
> - **MeloTTS는 의도적으로 제외**했습니다. MIT지만 MyShell.ai(중국 계열) 개발이라 "중국 제외" 기준에 해당합니다.
> - **XTTS v2(Coqui)도 제외**했습니다. CPML 라이선스는 **비상업용만** 허용 → 상업 서비스 불가.
> - **Supertonic 3 모델은 OpenRAIL-M**입니다. 상업적 사용은 가능하나 사용 기반 제한과 저작자 표시 의무가 있어 MIT와 동일하지 않습니다. 배포 전 원문 검토를 권합니다.

---

## 빠른 시작

### 가장 빠른 길 — 스크립트 (새 PC 그대로 OK)
```bash
git clone https://github.com/techgit01/tts-bmt-poc.git
cd tts-bmt-poc
./setup.sh            # uv 자동 설치 + Python 3.12 고정 + 의존성 설치
./run.sh --serve      # 벤치마크 실행 후 http://localhost:8000 로 데모 미리보기
```
> `./setup.sh --full` 은 실측 엔진(supertonic, piper)까지 설치합니다.
> `./run.sh --list` 는 엔진/설치 상태만 출력합니다.

### 또는 수동으로

#### 1) uv 설치
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 2) 프로젝트 준비 (Python 3.12 LTS 고정)
```bash
uv python pin 3.12     # .python-version 에 3.12 기록
uv sync                # 코어 의존성만 설치 (가벼움)
```

#### 3) 벤치마크 실행
```bash
uv run tts-bmt list    # 4개 엔진과 설치 상태 확인
uv run tts-bmt run     # 측정 -> docs/results/benchmark.json + docs/audio/*.wav
```

#### 4) 로컬에서 데모 미리보기
```bash
cd docs && python3 -m http.server 8000
# 브라우저에서 http://localhost:8000
```

> 엔진을 설치하지 않으면 **시뮬레이션 모드**(검증용 합성 신호)로 동작해
> 파이프라인 전체를 끝까지 돌려볼 수 있습니다. 실제 음질 비교는 아래 "실측 모드"를 참고하세요.

---

## 실측 모드 (실제 음질 비교)

각 엔진을 설치하면 어댑터가 자동으로 실측(real) 모드로 전환됩니다.

```bash
# Supertonic (PyPI 제공)
uv sync --extra supertonic

# piper-plus (PyPI 제공) — 한국어 음성 모델(.onnx) 별도 준비 필요
uv sync --extra piper
```

`kr-custom-tts` / `SCE-TTS` 는 **학습형**입니다. Google Colab(무료 GPU)에서
자가 음성으로 학습한 모델 산출물을 받아 어댑터에 경로를 지정하세요.
(`src/tts_bmt/engines.py` 의 각 엔진 `model_path` 참고)

---

## GitHub 배포 -> 온라인 확인

### A. 자동 (권장) — GitHub Actions
1. 이 저장소를 GitHub에 푸시
2. **Settings -> Pages -> Source: GitHub Actions** 선택
3. `main` 브랜치 푸시 시 `.github/workflows/deploy.yml` 이
   `uv run tts-bmt run` 실행 -> `docs/` 산출물 갱신 -> Pages 배포
4. 배포 URL: https://techgit01.github.io/tts-bmt-poc/

### B. 수동 — 정적 파일만
1. 로컬에서 `uv run tts-bmt run` 으로 `docs/` 채우기
2. 커밋/푸시
3. **Settings -> Pages -> Source: Deploy from a branch -> `main` / `docs`**

> `docs/.nojekyll` 가 포함되어 있어 Jekyll 처리를 건너뜁니다.

---

## 측정 지표

| 지표 | 의미 |
|------|------|
| **RTF** (Real-Time Factor) | 합성시간 / 오디오길이. **낮을수록 빠름** (0.1 = 1초 오디오를 0.1초에 생성) |
| **문자/초** | 초당 처리한 한국어 글자 수. 높을수록 빠름 |
| **모드** | `real`(실측) / `simulated`(엔진 미설치 폴백) |

테스트 문장은 평서·의문·긴급·차분·영문혼합 5종으로,
FDS 상담 시 필요한 억양 변화를 포함합니다. (`src/tts_bmt/benchmark.py`)

---

## 구조

```
tts-bmt-poc/
├─ setup.sh                # 새 PC 환경 준비 (uv 설치 + sync)
├─ run.sh                  # 벤치마크 실행 (+ --serve 데모 미리보기)
├─ pyproject.toml          # uv 프로젝트 (requires-python >=3.12,<3.13)
├─ .python-version         # 3.12 고정
├─ src/tts_bmt/
│  ├─ engines.py           # 공통 어댑터 + 4종 + 시뮬레이션 폴백
│  ├─ benchmark.py         # 측정 실행 -> JSON/오디오 산출
│  └─ cli.py               # tts-bmt run|list
├─ docs/                   # <- GitHub Pages 서빙 루트
│  ├─ index.html           # 정적 데모 (오디오 재생 + 파형 + 비교)
│  ├─ results/benchmark.json
│  ├─ audio/<engine>/*.wav
│  └─ .nojekyll
└─ .github/workflows/deploy.yml
```

## 한계

- 음소 단위 "말 꼬리 음정/감정 톤" 정밀 제어는 오픈소스 TTS 전반의 약점입니다.
  정형 알림 문장은 문장부호 기반 억양과 piper-plus 운율 주입으로 커버되지만,
  자유로운 감정 연기는 상용(SSML) 영역에 가깝습니다.
- 시뮬레이션 모드 수치는 파이프라인 검증용이며 실제 음질이 아닙니다.

## 라이선스
코드: MIT. 각 TTS 엔진/모델의 라이선스는 위 표 및 원 저장소를 따릅니다.
