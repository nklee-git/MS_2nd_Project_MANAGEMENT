> 관련 문서: [[1-kickoff-brief]] · [[21-system-model]] · [[23-cost-plan]] · [[24-alert-rules]]

## 서론

이 문서는 **4개 롤이 서로 안 보고도 병렬 작업할 수 있게 해주는 유일한 접점**(크로스커팅 계약)이다 — 스키마·권한·데이터흐름 순서만 지키면 각자 담당 부분을 독립적으로 구현해도 나중에 맞물린다. 한 줄 시나리오: **품절위험 SKU를 AI가 예측 → Dataverse에 발주추천 생성 → Teams 카드로 승인요청 → 클릭 한 번으로 발주 확정**(2026-08-20을 "오늘"로 고정해 9월 held-out과 대조 검증).

---

## 본론

### 1. 크로스커팅 계약 (확정)

**1-1. Dataverse 테이블 `ReorderRecommendation`** — 핵심 7필드

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| sku_code | Text (PK) | 대상 SKU |
| predicted_demand | Number | 예측 수요량 |
| recommended_qty | Number | 추천 발주량 |
| risk_score | Number | 품절위험 스코어 |
| status | Choice | Pending / Approved / Rejected |
| created_at | DateTime | 생성 시각 |
| approved_by | Lookup(User) | 승인자 |

2026-09-14 확정된 확장 필드 5개(`resolved_at`/`rejection_reason`/`auto_decidable`/`auto_decided` 등)는 [[5-dataverse-guide]] 3-2절. risk_score 공식은 [[24-alert-rules]]. 트리거 조건(리오더포인트 도달)도 [[24-alert-rules]].

**1-2. Security Role** — `Reorder Approver`(승인/반려) · `Viewer`(읽기전용) 2종만 확정, 세분화는 롤 담당자 판단.

**1-3. 데이터 흐름 순서** (2026-09-14 갱신)
`Blob Storage` → `Data Factory(오케스트레이션)` → `Databricks(ML 처리, 결과를 Dataverse에 직접 적재)` → `Dataverse ReorderRecommendation` → `Power Automate` → `Teams Adaptive Card` → `승인 시 Dataverse 상태 업데이트` → `C# API 서버(FashionAI.Api)가 조회` → `대시보드가 이 API 호출`. 별도 서빙 레이어 없이 Dataverse 단일 저장소, 대시보드는 API 서버 경유만 허용 — 근거: [[21-system-model]] 2절 · [[23-cost-plan]] · [[5-dataverse-guide]].

**1-4. 9월 held-out 검증** — 학습 cutoff 2026-08-20, 검증 구간 08-21~09-20, `generate_v4.py` 확장으로 생성하되 모델 입력에서 제외.

### 2. 롤별 TBD (담당자가 채울 것)
| 롤 | 채워야 할 것 |
| --- | --- |
| 데이터 파이프라인 | Data Factory 상세 구성, 배치 주기, held-out 생성 스크립트 |
| ML·모델링 | 피처 엔지니어링(24절기 채택 여부는 [[4-differentiation-ideas]] 논의 6), 평가지표 |
| Azure 인프라 | Dataverse 필드 확장 |
| RAG·자동화 | Power Automate 상세, Teams 카드 레이아웃 |
| 대시보드·프론트 | 차트 라이브러리(Recharts→서버렌더링 대응), Power BI 연동 범위 |

### 3. 확정 제외 사항 (Out of Scope)
GenAI 콘텐츠 생성 · 부서별 다중 KPI 대시보드 · 실제 AppSource 등재 · 실제 Event Hub 스트리밍(배치 리플레이로 대체) · Cosmos DB 서빙 레이어 · 실시간 A/B테스트 인프라(마케터 산출물은 사후분석 차트로 대체).

---

## 결론

크로스커팅 계약(1절)은 확정, 롤별 TBD(2절)는 각 담당자가 계속 채워나가면 된다. 아래는 과거 열린 질문 중 이미 해결된 것 — 재논의 불필요.

- ~~Databricks 스트레치 vs AutoML~~ → **Databricks 기술 핵심 확정**(2026-09-03)
- ~~반려 사유 자유입력 vs 사전정의~~ → **드롭다운 4종 + 자유입력 병행**(2026-09-10, [[04.MS-DataSchool/20.PROJECT/22.MS_2nd_Project/00-wbs/03-meetings/2026-09-10-townhall]] B절)
- ~~대시보드 프레임워크~~ → **ASP.NET Core MVC/Razor Pages 신규 구현**, React(v0.5.0) 폐기(2026-09-10)
