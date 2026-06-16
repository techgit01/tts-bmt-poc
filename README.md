# 한국어 TTS 벤치마크 POC

> 중국 개발 엔진 제외 · 상업용 무료(MIT 계열) · 한국어 지원
> **uv + Python 3.12** · 무거운 추론은 **Google Colab**에서 → **GitHub Pages** 정적 데모로 공개

🔊 **라이브 데모:** https://techgit01.github.io/tts-bmt-poc/
📦 **저장소:** https://github.com/techgit01/tts-bmt-poc

카드사 FDS(부정거래 탐지) 음성 상담을 가정한 한국어 문장으로, 오픈소스 TTS 4종을
같은 조건에서 합성하고 속도 지표를 측정합니다. 무거운 추론(Supertonic/ESPnet)은
**Colab에서 미리 돌려** 오디오(`.wav`)와 측정 결과(`benchmark.json`)를 만들어 커밋하고,
GitHub Pages에는 그 **정적 산출물만** 올려 브라우저에서 재생·비교합니다.
(Pages는 서버 코드를 실행하지 않음)

**현재 데모: 4종 중 3종이 실제 한국어 음성** — Supertonic ✅ · kr-custom-tts ✅ · SCE-TTS ✅ ·
piper-plus 만 시뮬레이션 톤(호환 한국어 모델 부재). 데모 우측 상단 **`? 도움말`** 에서
모드·지표 설명을 볼 수 있습니다.

---

## 비교 대상 4종

| # | 엔진 | 개발 | 라이선스 | 한국어 | 데모 음성 | 비고 |
|---|------|------|---------|--------|-----------|------|
| 1 | **Supertonic 3** | Supertone (KR) | MIT(code) + OpenRAIL-M(model) | 기본 지원 | ✅ real | 온디바이스 ~99M ONNX, CPU 실시간 |
| 2 | **piper-plus** | ayutaz (JP) | MIT | 8개 언어 중 포함 | ⏳ simulated | VITS. 깔끔한 한국어 onnx 모델 부재(KSS는 pygoruut 의존) |
| 3 | **kr-custom-tts** | seastar105 (KR) | MIT | 전용 | ✅ real | ESPnet. 데모는 **KSS 사전학습 JETS** (자가학습 시 본인 음성) |
| 4 | **SCE-TTS** | yunho0130 (KR) | MIT | 전용 | ✅ real | 원본 Tacotron2 자가학습. 데모는 **KSS 사전학습 VITS(ESPnet)** |

> **데모 음성 출처/데이터셋**:
> - **Supertonic** — Supertone 자체 데이터(비공개), 다국어, 데모 보이스 `F1`
> - **kr-custom-tts / SCE-TTS** — **KSS**(Korean Single Speaker, 여성 1인 ~12h) ESPnet 사전학습(JETS / VITS)
> - **piper-plus** — 현재 시뮬레이션(합성 톤, 학습 데이터 없음)
>
> ⚠️ **KSS 는 CC BY-NC-SA 4.0 — 비상업용**입니다. kr-custom·SCE 데모 음성은 **데모 용도**이며
> **상업 배포 불가**입니다. 상업적으로 쓰려면 본인/상업 가능 데이터로 파인튜닝하세요.
> (엔진 코드는 MIT지만 *데이터셋·모델* 라이선스는 별개) · 실제 생성·게시는
> [Colab 노트북](notebooks/tts_bmt_colab.ipynb)에서.

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
> `./setup.sh --full` 은 Supertonic(실측) + piper 패키지까지 설치합니다.
> kr-custom/SCE 의 ESPnet(KSS)은 무거워 **Colab 권장** (`uv sync --extra espnet`, piper와 공존 불가).
> `./run.sh --list` 는 엔진/설치 상태만 출력합니다.

### 또는 수동으로

#### 1) uv 설치
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 2) 프로젝트 준비 (Python 3.12 고정)
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

추론형 엔진은 패키지를 설치하고, 모델 의존 엔진은 `--model KEY=PATH` 로
모델 산출물 경로를 주면 실측(real) 모드로 측정됩니다.

```bash
# Supertonic — pip 추론
uv sync --extra supertonic

# kr-custom-tts / SCE-TTS — ESPnet + KSS 사전학습 (Colab 권장: 무거움)
uv sync --extra espnet          # espnet 과 piper 는 공존 불가(상호 배타 extra)
uv run tts-bmt run              # kr_custom=JETS, sce_tts=VITS 자동 사용

# (선택) 자가학습 모델로 교체 — 본인 음성 산출물 경로 주입
uv run tts-bmt run --model kr_custom=models/kr_exp --model sce_tts=models/sce_exp
```

> `mode` 는 엔진 설치 여부가 아니라 **실제로 합성된 결과**로 판정됩니다.
> 엔진이 있어도 실제 합성이 아직 폴백(시뮬레이션)이면 `simulated` 로 정직하게 표기됩니다.

`kr-custom-tts` / `SCE-TTS` 는 데모에서 **공개 KSS 단일화자 ESPnet 사전학습 모델**을
자동으로 사용합니다(학습 불필요). 본인 음성으로 바꾸려면 자가학습 산출물 경로를
`--model kr_custom=<경로>` 로 주입하세요. (`src/tts_bmt/engines.py` 의
`_EspnetKssEngine` / `all_engines(model_paths=...)` 참고)

> 🧪 **Colab 노트북 (실음성 생성·게시):** [`notebooks/tts_bmt_colab.ipynb`](notebooks/tts_bmt_colab.ipynb)
> [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/techgit01/tts-bmt-poc/blob/main/notebooks/tts_bmt_colab.ipynb)
> 셀 하나로 Supertonic + ESPnet KSS(kr-custom JETS / SCE VITS) 실음성을 생성 → 미리듣기 →
> `docs/` 커밋·푸시까지 안내합니다. (자가학습은 선택 셀로 분리)
>
> 📘 **Colab 무료 계정 생성/시작 가이드:** [`notebooks/google-colab-setup.md`](notebooks/google-colab-setup.md)

---

## GitHub 배포 -> 온라인 확인

**데모 음성은 Colab 에서 만들고, CI 는 커밋된 `docs/` 를 그대로 게시합니다.**

1. **데모 음성 생성** — [`notebooks/tts_bmt_colab.ipynb`](notebooks/tts_bmt_colab.ipynb) 에서
   Supertonic + ESPnet KSS(3종) 실측으로 `docs/audio` + `docs/results` 생성 후 커밋
2. **Settings -> Pages -> Source: GitHub Actions** (한 번만 설정)
3. `main` 푸시 시 `.github/workflows/deploy.yml` 이 **재생성 없이 커밋된 `docs/` 를 Pages 로 게시**
4. 배포 URL: https://techgit01.github.io/tts-bmt-poc/

> **스크립트 한 줄 배포:** `./deploy.sh`
> 보류 중인 변경을 커밋하고 `main` 에 푸시 → Actions 가 게시합니다.
> (`-m "메시지"` 커밋 메시지 지정, `--preview` 푸시 없이 로컬 `docs/` 만 생성해 미리보기)
>
> ℹ️ `docs/audio/`, `docs/results/` 는 **Colab 실측 음성**이라 의도적으로 커밋합니다.
> CI 가 재생성하지 않으므로(엔진 미설치) 시뮬레이션 톤으로 덮어쓰이지 않습니다.
> 로컬에서 빠르게 시뮬레이션으로 미리보려면 `./run.sh --serve`.
>
> 🔑 `.github/workflows/` 를 **처음 푸시**할 때는 토큰에 `workflow` 스코프가 필요합니다
> (`gh auth refresh -s workflow`). 이후 일반 푸시는 추가 스코프가 필요 없습니다.

---

## 측정 지표

| 지표 | 의미 |
|------|------|
| **RTF** (Real-Time Factor) | 합성시간 / 오디오길이. **낮을수록 빠름** (0.1 = 1초 오디오를 0.1초에 생성) |
| **문자/초** | 초당 처리한 한국어 글자 수. 높을수록 빠름 |
| **모드** | `real`(실제 합성 성공) / `simulated`(폴백 — 합성 신호, 음질 아님). 설치 여부가 아니라 실제 합성 결과로 판정 |

테스트 문장은 평서·의문·긴급·차분·영문혼합 5종으로,
FDS 상담 시 필요한 억양 변화를 포함합니다. (`src/tts_bmt/benchmark.py`)

---

## 구조

```
tts-bmt-poc/
├─ setup.sh                # 새 PC 환경 준비 (uv 설치 + sync)
├─ run.sh                  # 벤치마크 실행 (+ --serve 데모 미리보기)
├─ deploy.sh               # 소스 커밋 → main 푸시 (Actions 가 빌드·배포)
├─ notebooks/
│  ├─ tts_bmt_colab.ipynb       # Colab 실음성 생성·게시 노트북 (사전학습 KSS)
│  └─ google-colab-setup.md     # Colab 무료 계정 생성/시작 가이드
├─ pyproject.toml          # uv 프로젝트 (extras: supertonic/piper/espnet, piper⊥espnet)
├─ .python-version         # 개발 환경 3.12 고정
├─ src/tts_bmt/
│  ├─ engines.py           # 공통 어댑터 + Supertonic/piper/ESPnet KSS + 시뮬레이션 폴백
│  ├─ benchmark.py         # 측정 실행 -> JSON/오디오 산출
│  └─ cli.py               # tts-bmt run [--model KEY=PATH] | list
├─ docs/                   # <- GitHub Pages 서빙 루트
│  ├─ index.html           # 정적 데모 (재생 + 파형 + 모드 표시 + 도움말 모달)  [소스]
│  ├─ .nojekyll            # Jekyll 건너뜀                          [소스]
│  ├─ results/benchmark.json   # Colab 실측 결과 (커밋, CI 가 그대로 게시)
│  └─ audio/<engine>/*.wav     # Colab 실측 음성 (커밋, CI 가 그대로 게시)
└─ .github/workflows/deploy.yml
```

## 한계

- **piper-plus 는 현재 시뮬레이션**입니다. 공개된 유일한 한국어 piper 모델(KSS)이
  piper-plus 가 지원하지 않는 `pygoruut` phonemizer를 써서 깔끔하게 로드되지 않습니다.
  (강제 매핑 시 발음기호 누락으로 품질 보장 불가)
- kr-custom-tts / SCE-TTS 데모 음성은 **본인 음성이 아니라 공개 KSS 단일화자**
  사전학습 모델입니다. 원 프로젝트는 자가학습이 전제이며, 본인 음성은 선택 셀로 학습/교체합니다.
- 음소 단위 "말 꼬리 음정/감정 톤" 정밀 제어는 오픈소스 TTS 전반의 약점입니다.
  자유로운 감정 연기는 상용(SSML) 영역에 가깝습니다.
- 시뮬레이션 모드 수치는 파이프라인 검증용이며 실제 음질이 아닙니다.

## 라이선스
- **이 저장소의 소스 코드/데모 스캐폴딩: MIT** ([LICENSE](LICENSE)).
- **각 TTS 엔진/모델**의 라이선스는 위 표 및 원 저장소를 따릅니다.
- ⚠️ **생성된 오디오 산출물**(`docs/audio/*.wav`)은 MIT가 아니라 **이를 만든 엔진/모델/
  데이터셋의 라이선스**를 따릅니다:
  - **Supertonic 모델: OpenRAIL-M** (사용 기반 제한 + 저작자 표시 의무)
  - **kr-custom-tts / SCE-TTS 데모 음성: KSS = CC BY-NC-SA 4.0 (비상업)** → **데모 한정, 상업 배포 불가**
  - 상업 이용 전 각 원문 약관을 검토하고, 필요하면 상업 가능 데이터로 파인튜닝하세요.
