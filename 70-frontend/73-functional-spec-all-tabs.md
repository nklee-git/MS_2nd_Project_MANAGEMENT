> 대상: 최민 (개발자 리드) · 형준 (데이터조회 탭)
> 작성일: 2026-09-17
> 참고: [[72-dashboard-spec]] · [[25-execution-design]] · [[71-readme]] · [[24-alert-rules]] · [[23-cost-plan]]

---

## 1. 개요

### 1-1. 프로젝트 개요
패션 브랜드(가상 브랜드 NQNQ)의 재고 재발주를 AI가 예측해서 추천하고, 사람이 Teams나 대시보드에서 승인/반려하면 그 결과가 Dataverse에 기록되는 시스템. 목적은 "재고 담당자가 감으로 발주하는 문제"를 데이터 기반 의사결정으로 바꾸는 것.

- **9/23**: ML 예측 + 승인 플로우 코어 완성 체크포인트
- **9/29**: 최종 발표

### 1-2. 타겟 사용자
| 사용자 | 역할 | Dataverse 권한 |
| --- | --- | --- |
| MD (나경) | 재발주 승인/반려 최종 결정 | `Reorder Approver` |
| 유관부서(SCM/CFO/디자이너 등) | 알림 수신, 조회만 | `Viewer` |

---

## 2. 기능 명세

### 2-1. 탭별 주요 기능

| 탭 | 사용자 동작 | 시스템 응답 |
| --- | --- | --- |
| 승인이력 | 목록 열람 | `GET /api/reorders?status=`로 Dataverse 재조회 후 테이블 표시 |
| 승인이력 | 승인 버튼 클릭 | `PATCH /api/reorders/{skuCode}` → `status=Approved` |
| 승인이력 | 반려 버튼 클릭 + 사유 선택 | `PATCH` → `status=Rejected` + `rejectionReason` 저장 → 협업허브에 알림 카드 생성 |
| 협업허브 | 게시물 탭 열람 | 반려/이슈 기반 자동 생성 카드 목록 표시 |
| 협업허브 | 채팅 버튼 클릭 | 실제 Teams를 새 창/새 탭으로 열기 (임베드 아님) |
| 예측대조 | 기간 선택 | `GET /api/forecast?range=` → 예측치·실측치 라인차트 갱신 |
| 데이터조회 | 질문 칩/자연어 입력(숫자) | SQL 집계 조회 → AI가 문장으로 요약 → 표/차트 |
| 데이터조회 | 자유 채팅(정책) | AI Search로 정책 문서 검색 → AI가 답변 + 원문 링크 |
| 홈 | 진입 | **미정** — 5-1절 참고 |
| 설정 | 진입 | **미정** — 5-2절 참고 |

### 2-2. 화면 설계

**승인이력**
- 요약카드 4개: 대기중 건수 / 오늘 승인 건수 / 반려율 / 평균 처리시간
- 필터: 상태·카테고리·인기도·SKU검색 / 정렬: risk_score·생성일시·추천수량
- 테이블(20건/페이지): SKU·스타일명·카테고리·인기도·risk_score·예측수요·추천수량·상태·생성일시
- 상세 드로어(행 클릭 시): risk_score 근거, 재고 스택바, 판매 스파크라인, 승인/반려 버튼

**협업허브**

| 하위탭 | 내용 | 이번 스코프 |
| --- | --- | --- |
| 게시물 | 반려사유 기반 자동 알림 카드 | 구현 |
| 공지사항 | 정기 리포트(주간매출 등) | 백로그 |
| 파일 | 첨부 문서 링크 | 백로그 |
| 채팅 | Teams 딥링크 버튼만 | 구현 |

**예측대조**
- 요약카드 3개: 검증기간 / 평균오차율(MAPE) / 목표달성률
- 기간선택기 → 예측-실측 라인차트 → 카테고리별 오차율 바차트 → SKU별 오차 테이블(클릭 시 차트 하이라이트)

**데이터조회**
- 질문 칩 4개(고정) + 자연어 입력창(숫자 질문용)
- 별도 채팅창(정책 질문용) — 답변에 원문 문서 링크 포함
- 결과 표/차트 + CSV 다운로드 버튼

### 2-3. 핵심 사용자 흐름

**흐름 A — 승인**
MD 로그인 → 승인이력 탭 → 대기중 건 확인 → 상세 드로어 열람(근거 확인) → 승인 클릭 → Dataverse 업데이트 → (Teams로 알림 갔던 건이면) Teams 카드도 자동으로 처리됨 표시

**흐름 B — 반려 → 협업 알림**
승인이력에서 반려 클릭 → 사유 태그 선택(예: 체형스펙수정) → 저장 → 협업허브 게시물에 박지민(디자이너) 대상 카드 자동 생성

**흐름 C — 데이터 셀프서비스**
MD가 데이터조회 탭에서 "이번 주 반품 많은 카테고리는?" 클릭 → SQL 집계 → 표시. 별도로 "체형스펙수정 반려 기준이 뭐였지?" 채팅 입력 → 정책 문서 검색 → 답변

**흐름 D — 예측 신뢰성 확인**
예측대조 탭에서 9월 기간 선택 → 예측치 vs held-out 실측치 비교 → 오차율 확인

---

## 3. 기술 명세

### 3-1. 기술 스택

| 레이어 | 기술 | 비고 |
| --- | --- | --- |
| 프론트엔드 | ASP.NET Core MVC/Razor Pages | 2026-09-10 React에서 전환 확정. **확인 필요**: 실제 프로젝트명이 `FashionAiDashboard.Client`인데 이 네이밍은 보통 Blazor WebAssembly 프로젝트에 붙는 패턴이라 실제로 Razor Pages가 맞는지 최민님 확인 필요 |
| 차트 | Chart.js (권장, 미확정) | 기존 React 목업은 Recharts 사용 — 서버 렌더링 환경에 안 맞아 교체 필요, 시각 스펙은 동일 |
| 백엔드 API | ASP.NET Core Web API (`FashionAI.Api`), C# | 4개 엔드포인트로 제한(3-2절) |
| 데이터 저장 | Microsoft Dataverse | `ReorderRecommendation` 테이블(7필드+확장 5필드) |
| 자동화 | Power Automate + Teams Adaptive Cards | 승인 카드 발송/응답 처리 |
| ML | Azure Databricks | 수요예측, risk_score 산출 |
| RAG/AI | Azure OpenAI + Azure AI Search | 데이터조회 탭 전용 |
| BI | Power BI | **미확정** — 5-1절 참고 |
| 인증 | Azure AD App Registration + MSAL | Dataverse Web API 호출용(Client Credentials) |
| 폰트 | Pretendard (로컬 서빙) | |

### 3-2. API 계약 (4개, 늘리지 않음)
| 메서드/경로 | 용도 |
| --- | --- |
| `GET /api/reorders?status=` | 승인이력 목록 조회 |
| `PATCH /api/reorders/{skuCode}` | 승인/반려 처리 |
| `GET /api/forecast?range=` | 예측대조 데이터 조회 |
| `GET /api/skus` | SKU 마스터 조회 |

레이어 구조: `Controllers/`(요청/응답만) → `Services/`(비즈니스 로직) → `DataverseClient`(OData HTTP 래퍼)

### 3-3. 인증 방식
- **프론트 ↔ 백엔드**: 내부 통신용 API Key (사용자 로그인 인증 아님)
- **백엔드 ↔ Dataverse**: Azure AD App Registration(Client ID/Secret) + MSAL Client Credentials Flow → Dataverse에 Application User로 등록 + Security Role 부여 필요

### 3-4. 코딩 스타일 가이드
**확정된 것만 적음, 나머지는 미정**:
- 레이어 분리: Controller는 얇게, 비즈니스 로직은 Service, Dataverse 통신은 별도 클라이언트 클래스로 분리
- Swagger/OpenAPI 자동 노출 — 팀 간 계약 문서로도 사용
- ESLint/네이밍 컨벤션 등 세부 규칙은 아직 팀 차원에서 정한 적 없음 — 필요하면 최민님이 정해서 공유

---

## 4. 디자인 명세

### 4-1. 디자인 시스템
**컬러 팔레트** (2026-09-09 확정, 6색만 사용):
| 이름 | 값 | 용도 |
| --- | --- | --- |
| Poppy Pink | `#F33283` | accent, 버튼, 배지, 사이드바 active |
| Punchy Pink | `#FF80B4` | hover |
| Pastel Pink | `#FFADD7` | secondary 강조 |
| Regular White | `#FFFFFF` | 카드 배경 |
| Off-White | `#F9F9F9` | 페이지 배경 |
| Regular Black | `#000000` | 사이드바, 회색이 필요하면 이 색의 투명도만 사용(새 회색 안 만듦) |

**상태 색**: 대기=amber / 승인=green / 반려=red
**risk_score**: 초록→빨강 아님 — 연한 amber→진한 오렌지 단일 색조 (색맹 접근성 고려)
**폰트**: Pretendard, 로컬 파일로 서빙(시스템에 폰트 없어도 동일하게 보이게)

### 4-2. 와이어프레임/목업
- 실제 화면 스크린샷: `70-frontend/screenshots/`
- 협업허브 재설계 목업: https://claude.ai/artifact/XrMVzPFPHtABJZ6h9sr5fa (이번에 만든 것, 게시물/공지사항/파일/채팅 구조 반영)

---

## 5. 비기능 명세

### 5-1. 성능 요구사항
확정된 수치가 많지 않음 — 있는 것만 적음:
- Databricks 클러스터: 15~30분 자동종료 필수(비용 관리, [[23-cost-plan]])
- 실시간 데이터 생성 주기: 데모 중 5~10초, 실사용 가정 시 5분 (환경변수로 전환)
- **페이지 로드 시간·API 응답시간 목표는 별도로 정해진 게 없음** — 필요하면 지금 정해야 함

### 5-2. 접근성
- risk_score 색상표현에 색맹 고려 반영(위 4-1절)
- **그 외 WCAG 등 공식 기준 준수는 목표로 잡은 적 없음** — 발표용 PoC라 우선순위 낮게 봐도 되는지 팀 확인 필요

### 5-3. 보안 요구사항
- Dataverse 접근: Azure AD App Registration + Application User + Security Role(2종: `Reorder Approver`/`Viewer`)
- 데모 직전 전원 System Administrator 권한을 실제 역할로 낮출 예정([[5-dataverse-guide]] §3-3)
- 프론트-백엔드 내부 통신: API Key
- 개인정보: 전부 합성 데이터라 실제 PII 없음

---

## 6. 테스트 계획

### 6-1. 테스트 케이스 (역할별)

| 영역 | 테스트 항목 |
| --- | --- |
| 백엔드 API | 4개 엔드포인트 각각 Swagger/Postman으로 수동 검증 |
| 백엔드 로직 | `Services`/`DataverseClient` 단위 테스트(HttpClient 목킹, OData 응답 파싱) |
| 자동화(Power Automate) | 테스트 레코드 삽입 → Teams 카드 도착 확인 → 승인/반려 클릭 → 상태 반영 확인 → 반려 자유입력 케이스 별도 확인 |
| 프론트 화면 | 필터/정렬/드로어 동작, 차트 렌더링(1차는 CSV 목데이터 기준) |
| 통합 | 예측→Dataverse→Teams 승인→API→대시보드 전체 흐름 1회 통과 (9/23 체크포인트) |

### 6-2. 테스트 도구
| 영역 | 도구 |
| --- | --- |
| 백엔드 단위테스트 | xUnit + Moq |
| API 수동 검증 | Swagger UI, Postman |
| 프론트 자동화 테스트 | **없음 — 수동 브라우저 확인만 계획됨.** Cypress 등 도입 여부는 시간 여유에 따라 결정 |

---

## 7. 확인 필요한 것 모음 (열린 질문)

| 항목 | 내용 | 확인 대상 |
| --- | --- | --- |
| 프론트 프레임워크 | `.Client` 네이밍이 Blazor를 뜻하는 건지, Razor Pages가 맞는지 | 최민 |
| 홈 탭 | Power BI를 이번에 실제로 붙이는지, 붙인다면 홈 탭 안에 임베드인지 링크인지 | 최민 |
| 설정 탭 | 이 탭에 원래 뭘 넣으려 했는지 | 최민 |
| 예측대조 데이터 저장 | held-out 실측치를 Dataverse에 넣을지 파일로 둘지 | 임현제 |
| 데이터조회 정책 문서 | AI Search 인덱싱 대상 문서 확정 (재고정책 문서는 구버전이 archive로 이동, 대체 문서 없음) | 형준 |
| 협업허브 알림 카드 | 상대방에게 보낼 메시지를 자동 생성할지, 기존 대화를 찾아 보여줄지 | 나경(팀 회의) |
| 코딩 컨벤션 | 네이밍/폴더 구조 세부 규칙 | 최민 (필요시) |
