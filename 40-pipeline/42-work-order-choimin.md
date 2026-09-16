> 대상: 최민님 (데이터 파이프라인 + Azure 인프라 + 백엔드 API 담당, 테크리드)
> 참고 문서: [[22-feature-spec]] 1·2절 · [[04.MS-DataSchool/20.PROJECT/22.MS_2nd_Project/00-wbs/01-docs/2-schedule]] · [[21-system-model]] · [[61-entity-dictionary]] · [[24-alert-rules]] · [[53-virtual-team-profiles]] · [[5-dataverse-guide]]

## 서론

이 문서는 최민님 담당 영역(Dataverse 인프라, 데이터 파이프라인, 신규 C# API 서버)의 **작업지시서 겸 결정 기록**이다. 원래 2026-09-10에 "질문 목록"으로 시작했으나, 9/13~14 아키텍처 재정렬을 거치며 대부분 답이 나왔다 — 아래는 그 최종 상태다. 남은 열린 질문은 [결론](#결론--아직-열린-질문)만 확인하면 된다.

---

## 본론

### 1. 확정된 결정 (2026-09-14)

| 항목              | 결정                                                                                                                      |
| --------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Dataverse 초대    | 임현제·최민 완료, 박형준 9/14 초대(우선순위 아님)                                                                                         |
| 백엔드 아키텍처        | 별도 **C# Web API 서버**(`FashionAI.Api`) — 최민님이 C# 개발 경험을 원해서 "직접 호출" 대신 이 방향. 엔드포인트 4개 제한. 상세: [[25-execution-design]] 4절 |
| 테크리드            | 최민 — 이견 조율 최종 결정권만, 책임은 팀 전체 분담([[1-kickoff-brief]] 8절)                                                                 |
| `risk_score` 공식 | [[24-alert-rules]] 공식(고정 가중치)으로 통일 — 대시보드의 랜덤 구간 구현은 폐기                                                                 |
| 실시간 생성 실행 위치    | `FashionAI.Api` 안의 `BackgroundService` (MVC 앱 아님)                                                                       |

### 2. `ReorderRecommendation` 스키마 확장
기존 7필드(`sku_code`/`predicted_demand`/`recommended_qty`/`risk_score`/`status`/`created_at`/`approved_by`)에 추가:

| 필드                             | 결정                                                            |
| ------------------------------ | ------------------------------------------------------------- |
| `resolved_at` (DateTime)       | ✅ 추가 — 승인/반려 처리 시각                                            |
| `rejection_reason` (Text)      | ✅ 추가                                                          |
| SKU 마스터                        | ✅ 별도 Dataverse 테이블(Lookup) — Factory/Blob 직접 조회 없이 대시보드 조인 해결 |
| risk_score 근거값                 | ✅ 계산만 하고 미저장(스키마 최소화)                                         |
| `auto_decidable` (Boolean, 신규) | ✅ 추가 — ML이 계산, 저위험 자동승인 후보 여부. [[25-execution-design]] 2-5절   |
| `auto_decided` (Boolean, 신규)   | ✅ 추가 — Power Automate가 기록                                     |

### 3. Week 1~3 작업 목록
**Week 1 (9/11~9/20)**
- [ ] Mock 데이터셋 + held-out 생성 스크립트 확장
- [ ] Dataverse `ReorderRecommendation` + SKU마스터 테이블 생성 (2절 반영)
- [ ] Security Role 2종(`Reorder Approver`/`Viewer`) 세팅
- [ ] 원시데이터 14개 CSV(`dataverse_import/`)를 Dataverse 아닌 **Blob Storage**에 업로드(목적지만 변경, 작업은 재사용)
- [ ] Dataverse에 이미 만든 원시 테이블 14개 삭제, 데이터마트 7개 작업 중단([[21-system-model]] 부록 B, Year2/3 백로그)
- [ ] `FashionAI.Api` 프로젝트 스캐폴딩(엔드포인트 4개 뼈대)

**Week 2 (9/21~9/23, 추석 직전 — 가장 중요)**
- [ ] nqnq.db 실데이터 배치 전환(cutoff 8/20), ML 결과 Dataverse 적재 테스트, 승인자 권한 매핑
- [ ] **9/23 체크포인트**: 예측→Dataverse→Teams 승인→발주확정 풀 루프 1회 통과 (여기서 막히면 추석 연휴 동안 만회 불가)

**Week 3 (9/26~9/28)**
- [ ] held-out 정답 데이터 최종 고정, 스키마 동결 + 예외 케이스 점검

### 4. 실시간 데이터 생성 기술명세

**4-1. 무엇을 실시간으로 흔드나** (우선순위 순 — 카탈로그/예측모델은 정적으로 두고 트랜잭션성 데이터만)
| # | 데이터 | 발생 조건 | 다운스트림 |
| --- | --- | --- | --- |
| 1 | 신규 주문(`orders`/`order_item`) | tick마다 N건(SKU 가중치 랜덤) | 재고 차감 |
| 2 | 재고이동(`inventory_ledger`) | 주문 발생 시 1:1 | 재고 감사 |
| 3 | 반품(`return_request`) | 카테고리별 `return_rate` 확률 | 재고 복원 |
| 4 | 재발주 추천(`ReorderRecommendation`) | `available_qty ≤ reorder_point` | 승인함에 새 행 |
| 5 | 협업허브 알림(`ALERT_LOG`, 백로그 엔티티) | 4번과 동시 | [[53-virtual-team-profiles]] 3-4절 참고 |

**4-2. 재사용할 계산 공식** (새로 만들지 않음, `generate_v4.py`/[[61-entity-dictionary]] 그대로)
- `reorder_point = velocity × tier_ratio × 52 × 1.3`, `par_level = ×3.0`, `safety_stock = reorder_point × 0.5`
- SKU 선택 가중치: 날씨×사이즈×인기도 티어(`TIER_WEIGHT` HERO 3.0/STEADY 1.0/NICHE 0.3)
- 카테고리별 반품율: TOP 15%/PNT 20%/CLR 10%/OUT 18%/ACC 8%/DRS 15%
- 트렌드캡슐(`line_type=TREND`)은 자동재발주 트리거 제외([[24-sku-growth-roadmap]])

**4-3. 실행 위치**: `FashionAI.Api`의 `BackgroundService`(`IHostedService`/`PeriodicTimer`) — 1절 결정에 따라 확정. tick 5~10초(데모)/5분(실사용), 고정 시드(`Mulberry32`) 유지로 데모 재현성 확보.

### 5. 참고 — 지금 데이터 규모
2026-09-10 `generate_v4.py` 재실행 결과: 상품 41개·SKU 520개·주문 120만 건·반품 25.6만 건. `csv_preview/*.csv`도 이 기준(`30.DATA/32. nqnq_data/csv_preview/`, Team 저장소).

### 6. 2026-09-16 확정 — 백엔드/인프라 범위 확장

개발서버 구축 과정에서 원래 4절(엔드포인트 4개 제한) 범위보다 넓게 진행 중인 걸 이 문서에 공식 반영한다. 아래 7개는 최민님이 실제 진행 중인 작업으로 확정 기록:

1. `FashionAI.Api` 백엔드 본구현(스캐폴딩 이후 단계)
2. Azure DB 매핑
3. Power BI 매핑
4. API 설계 — **4-2절 "엔드포인트 4개 제한" 원칙과의 관계 확인 필요**: 늘어난 게 있으면 여기(4-2절)에 반영하고 시작할 것(원문 원칙: "늘리고 싶으면 이 문서를 먼저 고치고 시작")
5. app 테이블 설계 및 구축
6. 배포 아키텍처 설계
7. 8/20 이후 데이터 모듈 설계 및 구축(3절 Week2 "실데이터 배치 전환" 항목과 동일 계열 — 여기로 통합)

> **⚠️ 확인 필요 — 8번째 항목 "iOS 연동 테스트"는 지금 확정하지 않는다.** [[25-execution-design]] 2-6절에 "별도 모바일 앱 신규 개발은 기술스택 고정 원칙([[1-kickoff-brief]]) 충돌 + 무료 티어 이탈로 기각, Teams 자체 긴급알림으로 대체"가 2026-09-14에 이미 확정돼 있다. 지금 나온 iOS 연동이 이 결정을 뒤집는 새 범위인지, 아니면 다른 걸 가리키는 오해인지 최민님과 먼저 확인하고 나서 이 절에 추가할 것.

---

## 결론 — 아직 열린 질문
9/14 회의에서 확정할 것:
- [ ] `ALERT_LOG` 발생 시 협업허브에 즉시 반영할지 ([[53-virtual-team-profiles]] 3-4절 그대로 vs 재발주 추천까지만)
- [ ] 시뮬레이션 데이터임을 UI에 "실시간 시뮬레이션" 뱃지로 표시할지

결정되는 대로 [[22-feature-spec]] 1-1절과 [[61-entity-dictionary]]에 반영한다.
