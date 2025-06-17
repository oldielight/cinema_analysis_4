# Cinema Analysis Project

영화 분석을 위한 컴퓨터 비전 및 자연어 처리 프로젝트입니다.

## 프로젝트 구조

```
cinema_analysis_4/
├── main_project/          # 메인 분석 프로젝트
│   ├── data/             # 데이터 저장소
│   ├── notebooks/        # Jupyter 노트북
│   ├── scripts/          # 분석 스크립트
│   └── requirements.txt  # 의존성 패키지
├── new_project/          # 새로운 분석 프로젝트
│   ├── data/            # 데이터 저장소
│   ├── notebooks/       # Jupyter 노트북
│   ├── scripts/         # 분석 스크립트
│   └── requirements.txt # 의존성 패키지
└── model/               # 외부 모델 (gitignore)
```

## 주요 기능

### 1. 얼굴 인식 및 감정 분석
- DeepFace를 이용한 얼굴 인식
- 감정 분석 (기쁨, 슬픔, 분노 등)
- 인물 식별 시스템

### 2. 영상 분석
- 프레임 추출
- 객체 추적 (YOLO)
- 장면 분할

### 3. 자막 분석
- 자막 데이터 처리
- 감정과 대사 연관성 분석

## 설치 및 실행

### 1. 환경 설정
```bash
# 가상환경 생성
conda create -n cinema_env python=3.8
conda activate cinema_env

# 의존성 설치
pip install -r main_project/requirements.txt
```

### 2. 데이터 준비
- 영상 파일을 `main_project/data/raw/` 에 배치
- 자막 파일을 `new_project/data/raw/` 에 배치

### 3. 분석 실행
```bash
# 프레임 추출
python main_project/scripts/05.28_extract_frame.py

# 감정 분석
python new_project/scripts/0608(2).emotion_analysis_groq.py
```

## 주요 스크립트

### main_project/
- `05.28_extract_frame.py`: 영상에서 프레임 추출
- `05.28_merge_with_subs.py`: 자막과 프레임 데이터 병합
- `0616.scene_shot_analysis.py`: 장면 및 샷 분석

### new_project/
- `extract_frames.py`: 프레임 추출 (새 버전)
- `0608(2).emotion_analysis_groq.py`: Groq API를 이용한 감정 분석
- `consolidate_json.py`: JSON 결과 통합

## 분석 결과

분석 결과는 다음 형태로 저장됩니다:
- CSV 파일: 구조화된 데이터 (감정, 인물, 시간 정보)
- JSON 파일: 상세 분석 결과
- 이미지 파일: 시각화 결과

## 주의사항

- 대용량 파일 (영상, 모델 가중치)은 Git에 포함되지 않습니다
- 개인 얼굴 데이터베이스는 보안상 제외됩니다
- Azure API 키 등 민감한 정보는 별도 관리가 필요합니다

## 라이선스

이 프로젝트는 연구 목적으로 제작되었습니다. 