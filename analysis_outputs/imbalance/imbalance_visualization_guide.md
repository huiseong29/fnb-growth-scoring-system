# Imbalance Visualization Guide

## 목적

데이터 불균형을 숨기지 않고, 원본-기존 Top100-보정 Top100-균형형 추천의 분포 변화를 시각적으로 설명한다.

## 생성된 시각화

- `original_brand_distribution.svg`: 원본 데이터 브랜드 분포
- `original_category_distribution.svg`: 원본 데이터 카테고리 분포
- `current_top100_category_distribution.svg`: 기존 Top100 카테고리 분포
- `calibrated_top100_category_distribution.svg`: 보정 Top100 카테고리 분포
- `balanced_category_distribution.svg`: 균형형 추천 카테고리 분포
- `category_distribution_comparison.svg`: 네 단계 카테고리 분포 비교
- `imbalance_key_metrics.svg`: 불균형 핵심 지표 카드

## 핵심 해석

```text
원본 데이터부터 백반·죽·국수와 본그룹 비중이 높고, 기존 Top100에서는 이 편중이 더 심해졌습니다. 보정 Top100은 기존 후보의 안정성을 유지하면서 일부 치킨/피자 후보를 더 드러냈고, 균형형 추천은 발표용 보조 후보군으로 카테고리 다양성을 확보합니다.
```

## 발표 문장

```text
저희는 데이터 불균형을 약점으로 숨기지 않고, 분석 대상 자체의 특성으로 먼저 진단했습니다. 그 다음 전체 Top 후보, 보정 Top 후보, 균형형 후보를 분리해 제시했습니다.
```

## 주의점

- 균형형 추천은 전체 점수보다 정확하다는 뜻이 아니다.
- 균형형 추천은 제한된 데이터 안에서 후보 다양성을 확보하기 위한 보조 결과다.
- 불균형이 완전히 해결됐다고 말하지 않는다.