> 관련 문서: [[21-system-model]] 2절 · [[22-feature-spec]] · [[72-dashboard-spec]] · [[5-dataverse-guide]] · [[23-cost-plan]] · [[24-alert-rules]] · [[42-work-order-choimin]]
> **상태**: 팀장 확정안. 인프라 배치(원시데이터는 Blob, Dataverse는 결과 전용, 대시보드↔Dataverse는 C# API 서버 경유 — 최민님 C# 개발 경험 목적)는 위 문서들에 2026-09-14 반영 완료. 이 문서는 그 위에서 ML·RAG·프론트·백엔드 4개 영역의 요구사항분석→설계→구현→테스트를 확정한다. 각 영역 담당자는 이 문서 기준으로 진행하고, 다른 방향이 필요하면 구두가 아니라 이 문서 개정으로 처리한다.
> **작성 원칙**: 새 기술/새 라이브러리를 되도록 도입하지 않는다 — 이미 존재하는 산출물(`generate_v4.py` 공식, React 목업의 화면/컬러 결정, [[24-alert-rules]] risk_score 공식)을 그대로 재사용하는 쪽으로 설계한다. 2.5주 PoC 규모에 맞지 않는 과설계는 배제한다.

## 서론
ML(임현제)·RAG(나경)·프론트(나경)·백엔드(최민, 신규 C# API) 4개 영역 각각을 **요구사항분석→설계→구현→테스트** 순서로 정리했다. 코어(1절, 2-1~2-4절, 3절, 4절)가 먼저이고, 스트레치(2-5·2-6절)는 **9/23 체크포인트를 통과한 뒤에만** 착수 — 순서를 바꾸면 코어도 못 끝낸 채 부가기능에 시간을 쓰게 된다.

---

## 1. ML — Databricks (담당: 임현제)

### 1-1. 요구사항분석
| 항목 | 내용 |
| --- | --- |
| 입력 | Blob의 원시데이터(`nqnq.db` 기반 CSV, cutoff 8/20) — product/sku/inventory/orders/order_item/return_request/inventory_ledger |
| 출력 | SKU별 `predicted_demand`/`recommended_qty`/`risk_score` → Dataverse `ReorderRecommendation` upsert (원시데이터는 올리지 않음, [[21-system-model]] 2절) |
| 처리 주기 | 짧은 주기 micro-batch(5~10분) — 진짜 상시 스트리밍 아님([[23-cost-plan]]) |
| 정확도 검증 | 9월 held-out(8/21~9/20)과 대조, **9/23 체크포인트**에서 1차 확인 |
| risk_score 공식 | [[24-alert-rules]] 확정 공식(재고소진임박도 × 인기도가중치, **고정 가중치**)으로 통일 — 현재 대시보드 구현(랜덤 구간)은 폐기 |

### 1-2. 설계
- 노트북 파이프라인: `01_ingest`(Blob mount) → `02_feature_engineering`(velocity, 계절계수, 리드타임) → `03_forecast` → `04_risk_score` → `05_write_dataverse`
- 예측 모델: 베이스라인(이동평균/지수평활 등 단순 모델)부터 확정 — 정확도가 부족하면 그때 고도화. 처음부터 복잡한 모델 시도 금지(시간 리스크)
- 예측근거 자연어 설명(ReAct 축소판, [[21-system-model]] 부록 A)은 **코어 루프(위 5단계) 배포·검증 완료 후에만** 착수 — Tier1 스트레치, 순서 바뀌면 안 됨
- **(신규)** `04_risk_score` 단계에서 `auto_decidable`(Boolean) 플래그도 같이 계산 — risk_score·recommended_qty가 낮아 "잘못돼도 손실이 작은" 건만 true. 2절(RAG) "담당자 부재 시 자동 의사결정" 스트레치의 판정 근거로 재사용. 이것도 코어 루프 이후 착수

### 1-3. 구현
- 피처 공식은 새로 만들지 않고 `generate_v4.py`(reorder_point/par_level/safety_stock, SKU 가중치, 반품율) 그대로 포팅
- 클러스터: 소형(1~2 노드) + **autotermination 15~30분 필수**([[23-cost-plan]]), 작업 끝나면 종료 상태 직접 확인
- Dataverse 인증: Azure AD App Registration(Client Credentials) → Databricks secret scope에 client_id/secret 저장, `05_write_dataverse`에서 Web API POST/PATCH

### 1-4. 테스트
- 단위: risk_score 계산 함수를 SKU 3~5개 수기 계산값과 대조
- 통합: 노트북 실행 → Dataverse `ReorderRecommendation`에 실제 upsert됐는지 Power Apps 테이블 뷰에서 직접 확인
- 정확도: 9/23 체크포인트에서 held-out 대비 오차율(MAPE) 산출, 대시보드 예측대조 뷰에 표시할 수치 형태로 저장

---

## 2. RAG·자동화 — Power Automate + Teams (담당: 나경)

> **2026-09-16 갱신**: 형준에게 실행을 잠시 이관했다가(같은 날 1차 갱신), 형준이 같은 날 팀에서 이탈하면서 나경 단독 담당으로 복귀. 2-2~2-4절 코어(Adaptive Card + Power Automate Cloud Flow)는 나경이 직접 구현·테스트까지 완료함. 2-5·2-6절 스트레치는 9/23 체크포인트 통과 후 담당 재논의.

### 2-1. 요구사항분석
> 실제 "RAG 챗봇"은 이번 스코프가 아니다([[21-system-model]] 서론에 이미 확정) — "RAG·자동화" 롤의 실제 작업은 **Power Automate 승인 워크플로우**다. 이름에 낚이지 않는다.

| 항목 | 내용 |
| --- | --- |
| 트리거 | Dataverse `ReorderRecommendation` 신규 행 생성 |
| 액션 | Teams Adaptive Card 발송(SKU/예측수요/추천수량/risk_score + 승인/반려 버튼) |
| 응답 처리 | 승인 → status=Approved / 반려 → 사유 선택(드롭다운 4종 + 자유입력, 9-10 타운홀 확정) → status=Rejected, Dataverse 업데이트 |
| 스트레치(Tier1) | 카드에 예측근거 자연어 1~2문장 추가(ReAct 축소판, Structured Output `{"summary","key_factor","confidence"}`) — **1절 ML 코어 완료 후** 착수 |

### 2-2. 설계
- Power Automate Cloud Flow 1개: Dataverse 트리거(row created) → Adaptive Card 발송 → 응답 대기(Wait for a response) → Dataverse row 업데이트
- Adaptive Card는 JSON 템플릿(Adaptive Cards Designer로 작성) — 필드는 `ReorderRecommendation` 7필드에서 그대로 매핑, 새 필드 만들지 않음
- 스트레치 단계: 같은 플로우 안에 LLM 호출 액션 추가, 입력은 같은 트리거 레코드에서 조회한 근거 데이터
- **(2026-09-16 미확정 — 확인 필요)** 최민님 의견: 이 LLM 호출을 Power Automate 커넥터 대신 `FashionAI.Api`(C#)에 엔드포인트로 얹으면 바로 붙일 수 있을 것 같다는 제안. 두 방식 다 기술적으로 가능(REST API라 Power Automate 커넥터든 C#의 `HttpClient` 호출이든 결국 같은 엔드포인트를 부름) — 차이는 "어디서 부르냐"뿐이다. 다만 이 항목은 **9/23 코어 체크포인트 통과 후에만** 착수하는 스트레치이므로, 지금 아키텍처를 바꾸지 말고 그 시점에 팀 논의로 확정할 것(4-2절 엔드포인트 계약에 5번째 엔드포인트를 추가하는 결정이 되므로 4절 "엔드포인트 4개 제한" 원칙과 함께 검토 필요).
- **⚠️ (2026-09-17 밤 갱신) 실제로는 셋 중 어느 쪽도 아닌 제3의 방식이 이미 쓰이고 있음**: 임현제가 본인 RAG 프로토타입에서 **Azure AI Foundry 모델 배포 + API Key 직접 호출**로 이미 LLM을 붙였다고 보고 — Power Automate 커넥터도, `FashionAI.Api` 엔드포인트도 아니고, (아마 Databricks 노트북 등에서) 직접 REST 호출하는 구조로 보임. 이건 임현제 개인 작업 범위 기준이라 위 "호출 위치" 논의(카드에 붙는 나경/박형준 담당 스트레치용)와는 별개일 수 있지만, **같은 Foundry 배포·API Key를 재사용할 수 있는지는 팀이 확인 안 함** — 9/23 이후 호출 위치 확정할 때 이 옵션도 같이 검토할 것. 참고로 `FashionAI.Api`는 2026-09-17 기준 깃허브에 기본 템플릿(`WeatherForecastController` 샘플)만 있고 4개 엔드포인트 중 실제 구현된 것은 없음 — "엔드포인트 얹기" 옵션은 현재 코드베이스가 없는 상태에서 논의되고 있었던 것.

### 2-3. 구현
- Power Automate 메이커 포털에서 Dataverse 커넥터로 트리거 플로우 생성(로우코드 — 별도 배포 불필요)
- 반려 사유 UX는 대시보드에 이미 구현된 것과 동일하게 맞춤(9-10 타운홀 B절)

### 2-4. 테스트
- Dataverse에 테스트 레코드 수동 삽입 → Teams 카드 도착 확인 → 승인/반려 클릭 → status 반영 확인(End-to-end)
- 반려 자유입력 케이스 별도 확인
- 1절과 같은 시점(9/23)에 전체 루프(예측→Dataverse→Teams→발주확정)로 통합 검증

### 2-5. 담당자 부재 시 자동 의사결정 (신규, 임현제님 제안 — 스트레치)

> HITL 원칙([[21-system-model]] 서론, 과신 방지 근거 포함) 준수 위해 스코프를 좁힌다: **완전자동화 아님 — SLA 타임아웃 + 저위험 건만 안전 기본값 처리 + 전부 기록에 남겨 사람이 뒤집을 수 있게.** "담당자 없으면 AI가 다 결정한다"는 버전은 만들지 않는다.

**요구사항분석**
- 문제: MD가 Teams 카드에 응답하지 않으면 발주추천이 Pending으로 무한 대기 — "의사결정 지연을 줄인다"는 프로젝트 목적(0-1절)과 배치됨
- 자동판정 대상은 **잘못돼도 손실이 작은 건만**: risk_score·recommended_qty가 낮은 건만 자동승인 후보, 고위험/고금액 건은 절대 자동승인하지 않고 에스컬레이션만

**설계**
- Power Automate Flow의 "Wait for a response"에 SLA 타임아웃 추가(예: 근무시간 기준 4시간 — 정확한 값은 9/14 회의에서 확정)
- 타임아웃 발생 시 Condition 분기:
  - `auto_decidable = true`(임현제님 계산, 아래 참고) → 자동 승인 처리, `approved_by = "System(Auto)"`, `auto_decided = true` 기록
  - `auto_decidable = false` → 자동승인 안 함, Viewer(유관부서) 전체에 에스컬레이션 재알림, Pending 유지
- 대시보드: `auto_decided = true`인 건은 "자동승인" 뱃지로 별도 표시(3절 프론트에 반영) — 사람이 사후에 확인·뒤집을 수 있어야 함(XAI 과신 방지 원칙과 동일선상)

**구현**
- **임현제님 담당**: 자동승인 가능 여부(`auto_decidable`) 판정 로직 — risk_score 계산과 같은 근거 데이터를 쓰므로 1절 ML 노트북의 `04_risk_score` 단계에서 같이 계산해 Dataverse에 넣는다(Power Automate는 이 값을 Condition으로만 읽음, 복잡한 로직을 로우코드로 안 짜도 됨)
- **Dataverse 스키마 추가 2개**: `auto_decidable`(Boolean, ML이 계산) / `auto_decided`(Boolean, Power Automate가 기록) — 최민님 스키마 확장 목록에 추가 필요
- **나경 담당** (형준 2026-09-16 팀 이탈로 원복): Power Automate 타임아웃 분기 + 에스컬레이션 재알림 구현

**테스트**
- 테스트 레코드로 응답 없이 SLA 경과 시뮬레이션 — 저위험/고위험 각각 결과 확인
- 대시보드 "자동승인" 뱃지 노출 확인
- 에스컬레이션 알림이 실제 Viewer 그룹에 재발송되는지 확인

**일정 배치**: 1절 ML 코어 루프 + 2-1~2-4 코어 승인 플로우가 9/23 체크포인트를 통과한 **이후에만** 착수 — 7절 GenAI 스트레치와 같은 순서 원칙(코어 먼저, 스트레치는 그 다음). SLA 시간·임계값 구체적 수치는 9/14 회의에서 확정.

### 2-6. 위험 알람을 앱까지 도달시키기 — Teams 긴급(Urgent) 우선순위 (신규)

> "어플이랑 연동"을 **별도 커스텀 모바일 앱 신규 개발**로 해석하면 비추천이다: 팀 전원이 이미 Teams 모바일 앱을 쓰고 있어 Adaptive Card 알림이 원래 모바일에도 가고, 새 앱(네이티브/PWA)+푸시 인프라(디바이스 토큰 등록 등)를 지금 만드는 건 [[1-kickoff-brief]] "기술스택 고정 원칙"(확정 후 변경은 문서 개정으로만)과 충돌하며 무료 티어 범위도 벗어난다. 대신 **Teams 자체의 긴급 알림 기능**으로 같은 목적(놓치지 않고 폰까지 알림이 감)을 달성한다.

**요구사항분석**
- 목적: 고위험 건은 담당자가 알림을 놓쳐 승인이 늦어지는 일을 2-5절 자동승인(SLA 타임아웃)까지 가기 전에 먼저 방지 — "사람이 여전히 결정한다"는 원칙에 더 가까운, 자동승인보다 안전한 1차 조치
- 대상: risk_score가 임계값 이상인 고위험 건만(전부 긴급으로 보내면 알림 피로로 무시당함)

**설계**
- Power Automate Flow(2-2절)에 Condition 추가: `risk_score >= 긴급임계값` → 카드 발송 시 **Importance: Urgent**로 발송(수신자가 무음 설정해도 2분 간격 최대 20분 반복 알림, Teams 자체 기능) / 미만이면 일반 발송
- 순서: 레코드 생성 즉시 위험도별 일반/긴급 알림 발송 → 그래도 2-5절 SLA 시간 내 무응답이면 자동판정 로직으로 넘어감(2-5절과 2-6절은 같은 무응답 문제에 대한 1차/2차 방어선)
- 긴급임계값은 2-5절 `auto_decidable`(저위험=자동승인 후보)과 반대 개념 — 고위험 쪽 별도 임계값으로 정의(예: risk_score 상위 20%, 정확한 값은 9/14 회의에서 확정)

**구현**
- 나경 담당 (형준 2026-09-16 팀 이탈로 원복) — 기존 2절 Power Automate 플로우에 Condition 분기 하나 추가. 새 커넥터·새 서비스 불필요

**테스트**
- 고위험 테스트 레코드 → Urgent 알림이 실제로 모바일에 반복 도달하는지 확인
- 저위험 레코드는 일반 알림만 가는지 확인

---

## 3. 프론트 — ASP.NET Core MVC/Razor Pages (담당: 나경, 2026-09-11~09-16 박형준 공동 담당 기간 있었음)

### 3-1. 요구사항분석
- 화면은 **2개만**([[22-feature-spec]] 3절 확정): 승인이력 뷰, 예측대조 뷰 — 화면을 늘리지 않고 이 2개를 깊게 만든다
- **(2026-09-13 변경)** 데이터 출처는 Dataverse가 아니라 **최민님의 C# Web API 서버**([[42-work-order-choimin]] 1-2절, [[5-dataverse-guide]] 3-5절) — 프론트는 Dataverse 인증·OData를 전혀 모른다. API가 주는 JSON만 받아서 렌더링
- 기존 React 목업(v0.5.0)의 **화면 구조·컬러 팔레트·컴포넌트 분해는 그대로 재사용** — 디자인을 새로 정하지 않는다(6색 팔레트, Pretendard, risk_score 앰버 램프 등 [[04.MS-DataSchool/20.PROJECT/22.MS_2nd_Project/70-frontend/71-readme|70-frontend/readme.md]] "디자인 결정 사항" 그대로)

### 3-2. 설계
- Razor Pages 구조: `Pages/Approvals/Index.cshtml`, `Pages/Forecast/Index.cshtml` — React의 `ApprovalsView`/`ForecastView` 컴포넌트 분해를 Partial View 단위로 1:1 매핑(`FilterBar`→`_FilterBar.cshtml`, `DetailDrawer`→`_DetailDrawer.cshtml` 등)
- 서버측: `ReorderApiClient`(최민님 API를 호출하는 얇은 `HttpClient` 래퍼) → ViewModel 매핑, Controller/PageModel은 얇게 유지. Dataverse 클라이언트·MSAL 인증은 **여기 없음**(4절 백엔드 담당)
- 프론트↔백엔드 인증: 같은 앱 서비스 내부 통신이라 API Key 헤더 정도면 충분(사용자 로그인 인증 아님)

### 3-3. 구현
- **1차(병렬 가능, 최민님 API 완성 대기 불필요)**: 기존 `SampleDataService`(CSV 기반) 로직을 Razor Pages 뷰로 먼저 이식 — 화면·차트가 먼저 돌아가게 만듦
- **2차(최민님 API 완성 후)**: `SampleDataService`를 `ReorderApiClient`로 교체만 하면 되도록, 1차 단계에서 인터페이스를 분리해둘 것(`IReorderDataService` 등) — API의 JSON 응답 스키마는 4-2절 엔드포인트 계약 참고
- 차트는 기존 Recharts 대신 서버 렌더링 환경에 맞는 라이브러리로 교체 필요(예: Chart.js) — 시각적 스펙(라인차트/바차트 구성)은 [[72-dashboard-spec]] 그대로, 라이브러리만 교체

### 3-4. 테스트
- 화면 단위: 필터/정렬/드로어 동작, 차트 렌더링(1차 CSV 기준으로 먼저 검증 가능)
- 통합: 최민님 API 연동 후 재검증(9/23 체크포인트)
- 반응형/크로스브라우저는 우선순위 낮음(발표가 노트북 고정, 기존 결정 유지)

---

## 4. 백엔드 — C# Web API 서버 신규 프로젝트 (담당: 최민)

> **2026-09-13 확정**: 최민님이 C# 백엔드 개발을 직접 해보고 싶다고 확인되어, "임베디드 서비스"가 아니라 **독립된 ASP.NET Core Web API 프로젝트**로 분리한다([[42-work-order-choimin]] 1-2절 동일 반영). 대신 학습 목적과 일정 리스크를 같이 관리하기 위해 **엔드포인트를 아래 4개로 제한**한다 — 늘리고 싶으면 이 문서를 먼저 고치고 시작할 것.

### 4-1. 요구사항분석
| 항목 | 내용 |
| --- | --- |
| 역할 | MVC 프론트와 Dataverse 사이의 유일한 통로. 프론트는 Dataverse를 전혀 모름 |
| 기능 | (1) 발주추천 목록 조회 (2) 승인/반려 처리 (3) 예측대조 데이터 조회 (4) SKU 마스터 조회 |
| 실시간 데이터 생성 | 신규 주문/재고이동/반품/재발주추천 이벤트를 tick마다 생성해 Dataverse에 반영 ([[42-work-order-choimin]] 4-1절 우선순위 표 그대로) — 이 API 서버 안에서 처리(3-③) |
| 인증(대외) | Dataverse: Azure AD App Registration, MSAL Client Credentials |
| 인증(대내) | 프론트→이 API: 같은 앱 서비스 내부 통신용 API Key 정도로 충분 (사용자 로그인 체계 아님) |

### 4-2. 설계 — 엔드포인트 계약 (4개, 이 이상 늘리지 않음)
| 메서드/경로 | 용도 | 비고 |
| --- | --- | --- |
| `GET /api/reorders?status=` | 승인이력 뷰 목록 | `ReorderRecommendation` + SKU 마스터 조인해서 반환 |
| `PATCH /api/reorders/{skuCode}` | 승인/반려 처리 | body: `{status, rejectionReason?}` |
| `GET /api/forecast?range=` | 예측대조 뷰 데이터 | held-out 대조용 |
| `GET /api/skus` | SKU 마스터 목록 | 필터/검색용 |

- 레이어 구조: `Controllers/`(얇게, 요청/응답만) → `Services/`(비즈니스 로직 + Dataverse 매핑) → `DataverseClient`(OData HTTP 래퍼, 순수 통신만)
- `RealtimeGenerationService : BackgroundService`(PeriodicTimer): tick 5~10초(데모)/5분(실사용) 환경변수로 전환, `generate_v4.py`의 재고정책 공식(`reorder_point = velocity × tier_ratio × 52 × 1.3` 등)과 SKU 가중치(날씨×사이즈×인기도 티어)를 C#으로 그대로 포팅. 트렌드캡슐(`line_type = TREND`) SKU는 자동재발주 트리거 대상에서 제외 — 기존 원칙 그대로
- Swagger/OpenAPI 자동 노출 — 학습용으로도, 나경과의 계약 문서로도 겸용

### 4-3. 구현
- `dotnet new webapi -n FashionAI.Api`로 신규 프로젝트 생성(기존 MVC 프론트 프로젝트와 별개 솔루션 항목)
- NuGet: `Microsoft.Identity.Client`(MSAL), `HttpClientFactory` 패턴으로 `DataverseClient` DI 등록, `Swashbuckle`(Swagger)
- 로컬 개발: 프론트(MVC)와 API를 포트 분리해 동시 실행. 배포 시 Azure App Service 2개(또는 App Service Plan 하나에 앱 2개)
- 시크릿: 로컬 `dotnet user-secrets`, 배포 시 App Service Configuration

### 4-4. 테스트
- 단위: `Services`/`DataverseClient` — xUnit + Moq로 `HttpClient` 목킹, OData 응답 파싱 검증
- API 자체: Swagger UI 또는 Postman으로 4개 엔드포인트 수동 검증
- `RealtimeGenerationService` 통합 테스트: 짧은 tick 주기로 로컬 실행 → Dataverse 테스트 환경 반영 확인
- 프론트-백엔드 통합: 9/23 체크포인트에 포함
- 시뮬레이션 데이터임을 UI에 표시할지는 [[42-work-order-choimin]] 결론 결정에 따름

---

## 결론 — 통합 일정 & Definition of Done

| 시점                | 목표         | 통과 기준                                                                                                                       |
| ----------------- | ---------- | --------------------------------------------------------------------------------------------------------------------------- |
| Week1 (9/11~9/20) | 각 영역 병렬 준비 | 최민: Dataverse 스키마 확정 + `FashionAI.Api` 프로젝트 스캐폴딩(4개 엔드포인트 뼈대) / 임현제: 노트북 초안 / 나경: Power Automate 플로우 설계 + 프론트 1차(CSV 기반) 이식 |
| **9/23 체크포인트**    | 풀 루프 1회 통과 | 예측(ML) → Dataverse 적재 → Teams 승인 → 상태 업데이트 → **API 서버 경유** → 대시보드 반영까지 **끝까지 한 번 통과**. 여기서 막히면 추석 연휴 동안 만회 불가 — 최우선         |
| Week3 (9/26~9/28) | 검증·동결      | held-out 최종 대조, 스키마 freeze, 예외 케이스 점검, 스트레치(예측근거 자연어 설명) 착수 여부는 이 시점 이후에만 판단                                                |

인프라 배치(어디에 뭘 두는가)는 [[21-system-model]]·[[23-cost-plan]]·[[5-dataverse-guide]]·[[42-work-order-choimin]]가 우선하고, 이 문서(역할별 구현설계)는 그 위에서 실행 세부사항을 정한다. 서로 어긋나 보이면 저 문서들 쪽이 최신 인프라 결정이다.
