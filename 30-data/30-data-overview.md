> **용도**: "지금 데이터가 정확히 뭐고, 어떤 버전이 있는지" 한눈에 보는 개요. 세부 필드는 [[61-entity-dictionary]], 세부 변경이력은 [[65-model-changelog]]/[[26-sku-change-history]]/[[62-erd]] 변경이력 절이 각각 SSOT — 여기는 그것들을 압축한 현재 상태 스냅샷이다.

## 1. 지금 데이터는 정확히 뭔가

**하나의 가상 패션 브랜드(NQNQ) 시뮬레이션 데이터**. 실제 개인정보 없음(전부 합성 데이터), `generate_v5.py`(볼트 밖 Team 저장소)로 생성.

| 항목 | 현재 값 (2026-09-11 v5 재생성판 기준) | 이전(구) 값 |
| --- | --- | --- |
| 전체 주문 | ~124만 건(1,243,079) | 108만 건 (v3) / ~120만 건 (v4) |
| SKU | 520개 (베이직 418 + 트렌드캡슐 102) | 530개 (v4, 2026.08) |
| 상품(디자인) | 41개 (베이직 20 + 트렌드캡슐 21) | — |
| 시즌1 표준 규모 | 75 SKU (론칭 기준) | — |
| 학습 cutoff | 2026-08-20 | 2026-08-09 (구) |
| held-out 검증 구간 | 2026-08-21 ~ 09-20 | — |
| 카테고리 수 | 6종(TOP/PNT/CLR/OUT/ACC/DRS) | Y1 론칭 시점엔 3종(TOP/PNT/CLR) |

> ⚠️ 위 "현재 값"은 **카탈로그 설계·생성 스크립트 규칙** 기준(2026-09-08 리밸런싱 반영)이다. 실제 `nqnq.db` 파일이 이 최신 규칙으로 재생성됐는지는 [[25-sku-master-catalog]]·[[22-sku-code-system]] 갱신 여부를 확인할 것 — 문서상 목표치와 실제 DB 상태가 다를 수 있다는 게 이 프로젝트에서 반복적으로 발견된 문제였다.

## 2. 엔터티 구성 (14개, [[62-erd]] 참고)
`CATEGORY · PRODUCT · SKU · FACTORY · PURCHASE_ORDER · PO_ITEM · INVENTORY · INVENTORY_LEDGER · CHANNEL · CUSTOMER · ORDERS · ORDER_ITEM · RETURN_REQUEST · STORE`

세부 필드·데이터 품질 체크리스트는 [[61-entity-dictionary]]. 앱(Dataverse) 레이어의 `ReorderRecommendation`(+SKU마스터)은 이 14개와 별개 — 그건 AI 처리 결과물이지 원천 데이터가 아니므로 [[5-dataverse-guide]]/[[22-feature-spec]] 쪽에 정의돼 있다.

## 3. 버전 히스토리 요약

**생성 스크립트**: v3 → v4(SKU 확장, 롱테일) → v5(2026-09-11, `location_id` 매장별 재고 분리 + cutoff 8/20) — 상세는 [[04.MS-DataSchool/20.PROJECT/22.MS_2nd_Project/30-data/32-generator-notes/1-readme|generator-notes readme]] · [[04.MS-DataSchool/20.PROJECT/22.MS_2nd_Project/30-data/32-generator-notes/2-scenario-readme|scenario-readme]]

**ERD/스키마**: v1.0(13개 엔터티) → v1.1(INVENTORY_LEDGER 추가) → ... → v1.7(2026-09-11, location_id 복합키) — 전체 변경 이력은 [[62-erd]] "변경 이력" 절

**SKU 카탈로그 규모**: 75(S1 론칭) → 93 → 147 → 192 → 243 → 530(2026.08 리밸런싱) → 520(2026-09-08 체형태그 개편) — 전체 변경 이력은 [[26-sku-change-history]]

**채널 모델 — 미해결**: 개념(3채널, 자사몰 포함) vs 실제 코드(3채널, ZIGZAG/OFFLINE/WHOLESALE) vs 최민님 별도안(5채널, %) — 3중 불일치 상태, [[42-channel-settlement]] 참고. 9/14 회의 안건.

## 4. 데이터가 실제로 어디 있는가
- **원본 생성 스크립트·DB·CSV**: 이 옵시디언 볼트 밖, `MS-DataSchool-Code/22.MS_2nd_Project_Team/30.DATA/`(git 저장소)
- **이 볼트(`30-data/`)에 있는 것**: 기획/설계 문서만(브랜드·카탈로그·공급망·조직·세일즈·데이터모델 스펙) + 생성 스크립트에 대한 설명 노트(`generator-notes/`)
- **Dataverse에 실제로 올라가는 것**: 원시데이터 아님 — `ReorderRecommendation`+SKU마스터 결과만([[21-system-model]] 2절)

## 5. 더 자세히 보려면
| 궁금한 것 | 문서 |
| --- | --- |
| 전체 필드 정의·데이터 품질 규칙 | [[61-entity-dictionary]] |
| 엔터티 관계도(ERD) | [[62-erd]] |
| SKU 코드 체계·현재 규모 | [[22-sku-code-system]] |
| 카테고리·디자인 라인업 | [[21-core-categories]] |
| 재고 정책 공식(동적 계산) | [[32-inventory-policy]]("2026-09-14 발견" 배너 참고, 고정수치는 폐기됨) |
| 채널·정산 조건 | [[42-channel-settlement]] |
| 조직/가상 인물 프로필 | [[53-virtual-team-profiles]] |
| 생성 스크립트 버전별 이슈 | [[04.MS-DataSchool/20.PROJECT/22.MS_2nd_Project/30-data/32-generator-notes/1-readme|generator-notes]] |
