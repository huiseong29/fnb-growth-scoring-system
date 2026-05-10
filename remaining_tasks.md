# Remaining Tasks

이 문서는 현재 프로젝트에서 남은 작업을 실행 순서대로 정리한다.

프로젝트 주제는 **AI 기반 F&B 성장 유망 매장 스코어링 시스템**이며, 차별점은 **외부 상권 데이터와 Growth Alpha를 활용해 상권·브랜드·카테고리 효과를 보정한 성장 유망 매장 선별**이다.

## 1. 현재 완료된 작업

### 데이터 및 마트 구축

- 제공 데이터 구조 확인
- 내부 데이터 결합률 확인
- 서울시 외부 상권 데이터 다운로드 및 결합 가능성 검증
- `store_month_panel.csv` 생성

### EDA

- 성장 라벨별 주문/리뷰/답글률 비교
- 브랜드·카테고리별 성장 라벨 분포 확인
- Growth Alpha 상하위 매장 확인
- EDA 시각화 생성
- EDA 시각화 해석 문서 작성

### 모델링

- Baseline 모델 학습
- Growth Alpha 포함 모델 학습
- Baseline vs Growth Alpha 성능 비교
- 서울 내부 모델 vs 서울 외부 상권 결합 모델 비교
- 모델링 결과 문서화

### 스코어링

- GroMong Score 산출
- A/B/C/D 등급 부여
- 매장별 설명 근거 생성
- 스코어링 시각화 생성
- 시각화 해석 문서 작성

### 문서화

- `project_plan.md`
- `project_proposal.md`
- `analysis_outputs/visualization_guide.md`
- `score_design_rationale.md`

## 2. 남은 작업 목록

## Task 0. 중간발표 1등 퀄리티 보강 로드맵

상태: **작성 완료**

산출물:

- `midterm_quality_boost_plan.md`
- `analysis_outputs/quality_boost/charts/quality_boost_roadmap.svg`
- `analysis_outputs/quality_boost/quality_boost_visualization_guide.md`

핵심 보강 과제:

1. 리뷰 텍스트 감성/키워드 분석
2. 스코어 가중치 민감도 분석
3. 처치 전후 효과 분석
4. 브랜드/카테고리 보정 점수 추가
5. 외부데이터 확장 후보 조사

중간발표 전 최소 필수 보강:

- 리뷰 텍스트 감성/키워드 분석: **진행 중**
- 스코어 가중치 민감도 분석

## Task 1. 매장 ID 입력형 데모 구현

상태: **완료**

목적:

- PDF 필수 요구사항인 “매장 ID 입력 → 스코어 출력 데모”를 구현한다.

필수 기능:

- 매장 ID 입력
- 매장 기본 정보 출력
- GroMong Score 출력
- A/B/C/D 등급 출력
- 성장 확률 출력
- Growth Alpha 출력
- 주요 근거 3개 출력
- 서울 매장은 외부 상권 지표 출력

필수 시각화:

- 점수 게이지
- 점수 구성요소 bar chart
- 등급 배지
- 서울 매장일 경우 상권 객단가 비교 시각화

필수 문서 업데이트:

- `project_plan.md`
- `project_proposal.md`
- `remaining_tasks.md`
- `final_outputs_index.md`
- `analysis_outputs/visualization_guide.md`

예상 산출물:

- `app.py`
- `analysis_outputs/demo/`
- 데모 스크린샷 또는 화면 설명 이미지
- 데모 사용 설명 문서

실제 산출물:

- `app.py`
- `analysis_outputs/demo/demo_guide.md`
- `analysis_outputs/demo/demo_visualization_guide.md`
- `analysis_outputs/demo/demo_validation.md`

## Task 2. 데모 검증

상태: **완료**

검증 항목:

- 실제 존재하는 매장 ID 입력 테스트
- 없는 매장 ID 입력 시 예외 처리
- A/B/C/D 등급별 샘플 매장 테스트
- 서울 매장 입력 시 외부 상권 지표 출력 확인
- 비서울 매장 입력 시 외부 상권 항목 처리 확인
- 점수 구성요소와 최종 점수 일관성 확인

필수 시각화:

- 데모 화면 캡처
- 등급별 샘플 화면 캡처

필수 문서:

- 데모 검증 결과 문서
- 데모 화면/이미지 설명 문서

실제 산출물:

- `analysis_outputs/demo/demo_validation.md`
- `analysis_outputs/demo/demo_visualization_guide.md`

## Task 3. 최종 발표용 결과 정리

상태: **일부 완료**

정리할 내용:

- 문제 정의
- 데이터 구성과 한계
- 외부 데이터 사용 이유
- Growth Alpha 차별점
- EDA 핵심 결과
- 모델 성능 비교
- 외부 상권 데이터 효과
- GroMong Score 결과
- 데모 시연 흐름
- 한계와 확장 방향

필수 시각화 후보:

- 성장/비성장 평균 주문수 비교
- 성장/비성장 평균 리뷰수 비교
- Growth Alpha 비교
- 브랜드/카테고리별 성장 비율
- Baseline vs Growth Alpha 모델 성능 비교
- 서울 외부 상권 모델 성능 비교
- 등급별 매장 수
- Top 20 추천 매장

필수 문서:

- 발표용 핵심 표 정리
- 발표용 그래프 목록
- 그래프별 발표 멘트

## Task 4. 최종 보고서/발표 스토리라인 작성

상태: **대기**

권장 흐름:

```text
문제 정의
→ 제공 데이터 한계
→ 외부 상권 데이터 결합
→ Growth Alpha 차별점
→ EDA 결과
→ 모델 비교
→ 외부 데이터 효과 검증
→ GroMong Score 산출
→ 데모
→ 한계와 확장 방향
```

필수 포함 논리:

- 제공 데이터는 전체 F&B 시장의 완전한 대표 표본이 아니다.
- 본 프로젝트는 실제 운영 데이터 기반 파일럿 검증으로 해석한다.
- 브랜드와 카테고리 효과는 통제하고, Growth Alpha로 초과 성장성을 본다.
- 외부 상권 데이터는 서울 매장 211개에서 성능 개선 근거를 보였다.
- 최종 스코어는 투자 확정이 아니라 우선 검토 후보군 선별 도구다.

## Task 5. 한계와 방어 논리 정리

상태: **대기**

반드시 정리할 한계:

- 브랜드가 본그룹/굽네치킨 중심
- 전체 F&B 대표 표본은 아님
- 외부 상권 데이터는 서울 211개 매장에 안정 결합
- 행정동/좌표 단위 결합은 아직 아님
- 실제 기업 제공 성장/하락 정답 라벨은 없음
- 댓글 유형이 AI/직접/마케팅으로 완전히 분리되어 있지 않음

방어 논리:

```text
본 프로젝트는 전체 F&B 시장을 완전히 일반화하는 최종 모델이 아니라,
제공된 실제 운영 데이터를 기반으로 성장 유망 매장 스코어링 방법론을 파일럿 검증한 것이다.
```

```text
데이터의 브랜드 편향을 숨기지 않고,
브랜드·카테고리 보정 Growth Alpha를 통해 같은 조건 대비 초과 성장 매장을 찾는 방향으로 재정의했다.
```

현재 반영된 문서:

- `score_design_rationale.md`

남은 작업:

- 최종 발표용 문장만 따로 추려 `limitations_and_defense.md`로 정리

## 3. 앞으로의 작업 운영 원칙

앞으로 작업을 하나 완료할 때마다 반드시 다음을 수행한다.

1. 결과 파일 생성
2. 시각화 파일 생성
3. 시각화 해석 문서 작성 또는 업데이트
4. `project_plan.md` 업데이트
5. `project_proposal.md` 업데이트
6. `remaining_tasks.md` 업데이트
7. `final_outputs_index.md` 업데이트

시각화가 생성될 경우 반드시 다음 내용을 함께 작성한다.

- 그래프 목적
- 핵심 수치
- 해석
- 발표용 문장
- 주의점 또는 한계

## 4. 바로 다음 작업

바로 다음 작업은 **최종 발표용 결과 정리**이다.

이제 분석 결과물과 데모가 모두 만들어졌으므로, 발표자료에 바로 넣을 핵심 표, 그래프, 발표 문장을 정리해야 한다.
## 2026-05-08 작업 현황 업데이트

완료된 보강 작업:

- 리뷰 텍스트 감성/키워드 분석: **완료**
- 리뷰 NLP 시각화 생성: **완료**
- 리뷰 NLP 시각화 설명 문서 작성: **완료**

생성된 주요 파일:

- `analysis_outputs/nlp/review_sentiment_summary.csv`
- `analysis_outputs/nlp/review_category_sentiment_summary.csv`
- `analysis_outputs/nlp/positive_keyword_top50.csv`
- `analysis_outputs/nlp/negative_keyword_top50.csv`
- `analysis_outputs/nlp/rating_sentiment_mismatch_examples.csv`
- `analysis_outputs/nlp/review_nlp_visualization_guide.md`
- `analysis_outputs/nlp/charts/`

다음 우선 작업:

1. GroMong Score 가중치 민감도 분석
2. 가중치 시나리오별 Top 매장 안정성 비교
3. 가중치 민감도 시각화 생성
4. 가중치 민감도 시각화 설명 문서 작성
5. `project_plan.md`, `project_proposal.md`, `remaining_tasks.md`, `final_outputs_index.md`, `analysis_outputs/visualization_guide.md`, `score_design_rationale.md` 업데이트

다음 작업의 발표 목적:

```text
현재 점수 기준이 임의로 보이지 않도록, 5개 지수의 가중치를 바꿔도 상위 추천 매장이 얼마나 안정적으로 유지되는지 검증한다.
```
## 2026-05-08 추가 작업 현황 업데이트

완료된 보강 작업:

- GroMong Score 가중치 민감도 분석: **완료**
- 가중치 시나리오별 Top100 겹침률 계산: **완료**
- 가중치 시나리오별 순위 상관 계산: **완료**
- 가중치 시나리오별 등급 분포 시각화: **완료**
- 가중치 민감도 시각화 설명 문서 작성: **완료**

생성된 주요 파일:

- `analysis_outputs/sensitivity/score_sensitivity_summary.csv`
- `analysis_outputs/sensitivity/score_sensitivity_detail.csv`
- `analysis_outputs/sensitivity/top100_stability.csv`
- `analysis_outputs/sensitivity/score_sensitivity_report.md`
- `analysis_outputs/sensitivity/score_sensitivity_visualization_guide.md`
- `analysis_outputs/sensitivity/charts/`

다음 우선 작업:

1. 브랜드/카테고리 보정 점수 생성
2. 카테고리 내부 Top 매장 추출
3. 전체 순위와 카테고리 내부 순위 비교 시각화
4. 브랜드/카테고리 보정 설명 문서 작성
5. 모든 관리 MD 업데이트

다음 작업의 발표 목적:

```text
제공 데이터가 본그룹과 굽네치킨 중심이라는 한계를 정면으로 인정하고, 전체 순위뿐 아니라 브랜드/카테고리 내부에서 상대적으로 우수한 매장을 제시해 공정성과 설명력을 높인다.
```
## 2026-05-08 브랜드/카테고리 보정 작업 현황

완료된 작업:

- 브랜드 내부 percentile 점수 생성: **완료**
- 카테고리 내부 percentile 점수 생성: **완료**
- 보정 점수 생성: **완료**
- 카테고리별 Top10 후보 추출: **완료**
- 브랜드별 Top10 후보 추출: **완료**
- 기존 Top100과 보정 Top100 겹침률 계산: **완료**
- 보정 점수 시각화 생성: **완료**
- 보정 점수 시각화 설명 문서 작성: **완료**

생성된 주요 파일:

- `analysis_outputs/calibrated_score/calibrated_store_scores.csv`
- `analysis_outputs/calibrated_score/category_top10_calibrated.csv`
- `analysis_outputs/calibrated_score/brand_top10_calibrated.csv`
- `analysis_outputs/calibrated_score/calibration_group_summary.csv`
- `analysis_outputs/calibrated_score/top100_calibration_overlap.csv`
- `analysis_outputs/calibrated_score/calibrated_score_report.md`
- `analysis_outputs/calibrated_score/calibrated_score_visualization_guide.md`
- `analysis_outputs/calibrated_score/charts/`

다음 우선 작업:

1. 최종 발표용 결과 정리
2. 발표에 사용할 핵심 그래프 선별
3. 그래프별 발표 멘트 작성
4. 한계와 방어 논리 문서화
5. 최종 보고서/발표자료 초안 작성

다음 작업의 발표 목적:

```text
지금까지 만든 EDA, 외부 상권, 모델링, 스코어링, 리뷰 NLP, 가중치 민감도, 보정 점수를 하나의 발표 흐름으로 묶어 교수님이 요구한 차별점과 유의미한 결과를 명확히 전달한다.
```
## 2026-05-08 현재 진행 작업: 불균형 진단과 균형형 추천

상태: **진행 중**

진행할 작업:

- 원본 데이터 브랜드/카테고리 분포 시각화
- 기존 Top100 브랜드/카테고리 분포 시각화
- 보정 Top100 브랜드/카테고리 분포 시각화
- 보정 전후 편중 완화 수치 계산
- 카테고리별 균형형 추천 리스트 생성
- 브랜드별 균형형 추천 리스트 생성
- 발표용 방어 논리 문서 작성
- 관련 MD 파일 전체 업데이트

이번 작업이 끝나면 다음 단계는 최종 발표용 결과 정리와 발표자료 초안 작성이다.
## 2026-05-08 불균형 진단과 균형형 추천 완료

상태: **완료**

완료된 작업:

- 원본 데이터 브랜드/카테고리 분포 시각화: **완료**
- 기존 Top100 브랜드/카테고리 분포 시각화: **완료**
- 보정 Top100 브랜드/카테고리 분포 시각화: **완료**
- 보정 전후 편중 완화 수치 계산: **완료**
- 카테고리별 균형형 추천 리스트 생성: **완료**
- 브랜드별 균형형 추천 리스트 생성: **완료**
- 발표용 방어 논리 문서 작성: **완료**
- 관련 MD 파일 전체 업데이트: **완료**

생성된 주요 파일:

- `analysis_outputs/imbalance/imbalance_summary.csv`
- `analysis_outputs/imbalance/imbalance_metrics.csv`
- `analysis_outputs/imbalance/balanced_recommendations.csv`
- `analysis_outputs/imbalance/imbalance_defense_report.md`
- `analysis_outputs/imbalance/imbalance_visualization_guide.md`
- `analysis_outputs/imbalance/charts/`

다음 우선 작업:

1. 최종 발표용 결과 정리 문서 작성
2. 발표에 넣을 핵심 그래프 10~12개 선별
3. 그래프별 발표 멘트 작성
4. 교수님 예상 질문과 방어 답변 작성
5. 최종 보고서/발표자료 초안 작성
