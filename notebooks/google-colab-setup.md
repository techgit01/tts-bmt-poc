# Google Colab 무료 계정 생성 & 시작 가이드

이 프로젝트의 **학습형 엔진**(kr-custom-tts, SCE-TTS)은 무료 GPU가 필요해 Google Colab에서 돌립니다.
Colab은 **별도 가입 절차 없이 Google 계정만 있으면** 무료로 사용할 수 있습니다.

---

## 1. Google 계정 준비

Colab 전용 가입은 없습니다. **Google 계정 = Colab 계정** 입니다.

### 이미 Gmail/Google 계정이 있다면
→ 바로 [2단계](#2-colab-열기)로 가세요.

### 계정이 없다면 (무료 생성)
1. https://accounts.google.com/signup 접속
2. 이름 입력 → 사용할 **사용자 이름(이메일 주소)** 과 **비밀번호** 설정
3. 휴대폰 번호로 본인 확인 (SMS 인증)
4. 약관 동의 → 완료

> 무료 계정으로 Colab의 무료 등급(주로 T4 GPU)을 쓸 수 있습니다. 신용카드가 필요 없습니다.

---

## 2. Colab 열기

1. https://colab.research.google.com 접속
2. 우측 상단 **로그인** → 위에서 만든 Google 계정으로 로그인
3. 처음이면 "Colab에 오신 것을 환영합니다" 소개 노트북이 열립니다

---

## 3. 이 프로젝트 노트북 바로 열기

아래 배지를 누르면 이 저장소의 학습 노트북이 Colab에서 바로 열립니다.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/techgit01/tts-bmt-poc/blob/main/notebooks/tts_bmt_colab.ipynb)

또는 Colab 메뉴에서: **파일 > 노트 열기 > GitHub 탭** →
`techgit01/tts-bmt-poc` 검색 → `notebooks/tts_bmt_colab.ipynb` 선택

---

## 4. GPU 켜기 (학습형 엔진에 필수)

1. 상단 메뉴 **런타임 > 런타임 유형 변경**
2. **하드웨어 가속기 → GPU (T4)** 선택 → **저장**
3. 노트북 첫 셀(`!nvidia-smi`)을 실행해 GPU가 잡혔는지 확인

> 추론형(Supertonic, piper-plus)만 쓸 거면 GPU 없이 CPU 런타임으로도 됩니다.
> 학습형(kr-custom-tts, SCE-TTS)은 반드시 GPU를 켜세요.

---

## 5. 셀 실행 방법

- 셀 왼쪽 **▶ (실행)** 버튼 클릭, 또는 셀 선택 후 **Shift + Enter**
- 위에서부터 순서대로 실행하세요
- 결과 파일은 좌측 **📁 파일** 패널에서 확인/다운로드할 수 있습니다

---

## 무료 등급에서 알아둘 점

| 항목 | 무료(Free) 등급 |
|------|----------------|
| GPU | 주로 NVIDIA T4 (가용량에 따라 변동, 미보장) |
| 세션 시간 | 최대 약 12시간, **유휴 시 끊김** (탭을 켜둬야 유지) |
| 디스크 | 임시(런타임 종료 시 초기화) → 결과물은 꼭 다운로드하거나 Google Drive에 저장 |
| 동시 세션 | 제한 있음 |

> 긴 학습은 중간 산출물을 **Google Drive에 저장**해 두면 세션이 끊겨도 이어갈 수 있습니다.
> Drive 연결: 노트북에서 `from google.colab import drive; drive.mount('/content/drive')`

---

## 학습이 끝나면

1. 학습된 모델 파일을 **다운로드** (노트북 6번 셀 `files.download(...)`)
2. 로컬 저장소에 두고 `src/tts_bmt/engines.py` 의 해당 엔진 `model_path` 로 연결
3. `./run.sh` 로 실측(real) 모드 측정 → `./deploy.sh` 로 배포

자세한 학습 절차는 [`tts_bmt_colab.ipynb`](tts_bmt_colab.ipynb) 와 각 엔진 업스트림 가이드를 따르세요.
