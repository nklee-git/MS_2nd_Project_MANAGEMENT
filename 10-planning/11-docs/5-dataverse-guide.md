> 관련 문서: [[21-system-model]] 2절 · [[22-feature-spec]] 1절 · [[23-cost-plan]] · [[2-onboarding-checklist]] · [[61-entity-dictionary]]
> **용도**: 팀 전원이 Dataverse를 처음 다뤄봐서, "이게 대체 뭐고 우리 프로젝트에서 왜 필요한지"를 한 문서에 정리. 작업지시서·기능명세서는 "뭘 만들지"를 다루고, 이 문서는 "왜/어떻게 이 도구를 쓰는지"를 다룸.

## 1. Dataverse가 뭔가 (한 줄 요약)

**Dataverse = Microsoft가 만든 클라우드 데이터베이스 + 그 위에서 화면·자동화·권한을 바로 붙일 수 있는 플랫폼.**

SQL 데이터베이스(MySQL, PostgreSQL 같은 것)랑 근본적으로 비슷한 일(테이블에 행·컬럼으로 데이터 저장)을 하지만, 차이가 있음:

|          | 일반 DB(SQL)          | Dataverse                                         |
| -------- | ------------------- | ------------------------------------------------- |
| 데이터 저장   | 테이블                 | 테이블(Dataverse에서는 "엔터티"라고도 부름) — 개념은 동일            |
| 화면 붙이기   | 직접 프론트엔드 코딩 필요      | Power Apps로 화면을 거의 자동 생성 가능                       |
| 자동화      | 별도 스케줄러/코드 필요       | Power Automate가 "레코드 생성되면 → 알림 보내기" 같은 걸 코드 없이 처리 |
| 권한 관리    | 직접 구현(로그인·역할 테이블 등) | Security Role로 "누가 뭘 볼 수 있는지" 화면에서 클릭만으로 설정       |
| Teams 연동 | 직접 API 붙여야 함        | Power Automate가 Teams Adaptive Card를 기본 지원        |

즉 "DB + 화면툴 + 자동화툴 + 권한관리 + Teams연동"이 한 세트로 묶여있는 게 Dataverse. Microsoft Dynamics 365(D365, 실제 기업들이 쓰는 유료 ERP)도 내부적으로 전부 Dataverse 위에서 돌아감.

## 2. 우리가 왜 이걸 쓰는가

이 프로젝트는 공식적으로 **"Azure Databricks 프로젝트"**로 명명돼 있고, 기술 핵심은 Databricks+Data Factory의 ML/데이터처리다. Dataverse는 그 결과물이 "실제 회사 시스템처럼 보이게" 만들어주는 **차별화 레이어**다 — 실제 기업이 D365를 어떻게 쓰는지, 왜 애드온 구조여야 하는지, 비용이 왜 0원인지는 [[23-cost-plan]] "🏢 실제 기업은 D365를 어떻게 쓰는가" 절 참고(중복 설명 안 함).

## 3. 우리 프로젝트에서 실제로 어떻게 쓰이는지

### 3-1. 전체 흐름 속 위치
> **2026-09-14 갱신**: 원시데이터는 Dataverse가 아니라 **Blob Storage**로 간다(9/13 최민님이 원시 14개 테이블을 Dataverse에 적재하려다 발견된 아키텍처 어긋남 — [[23-cost-plan]] "Dataverse에 원시데이터를 통째로 올리면 안 되는 이유" 참고). 대시보드도 Dataverse를 직접 부르지 않고 **최민님이 만드는 C# Web API 서버**를 거친다.

```
로컬 데이터(nqnq.db) → Blob Storage → Data Factory(트리거만) → Databricks(ML 처리, 예측)
    ↓ 예측 결과 적재 (ReorderRecommendation만, 원시데이터 아님)
Dataverse: ReorderRecommendation 테이블에 새 행 생성
    ↓ 신규 행 감지
Power Automate → Teams Adaptive Card로 승인 요청
    ↓ 승인/반려 클릭
Power Automate → Dataverse 상태 업데이트(status 컬럼)
    ↓
C# Web API 서버(FashionAI.Api, 최민 담당)가 Dataverse Web API로 조회
    ↓
ASP.NET Core MVC 대시보드가 이 API를 호출해서 화면에 표시
```
전체 다이어그램은 [[21-system-model]] 2절 참고. **Dataverse는 이 흐름의 "중간 저장소"** — ML이 계산한 결과가 여기 쌓이고, Teams 승인도 여기 상태를 바꾸고, C# API 서버도 여기서 읽어온다(대시보드는 Dataverse를 모름). 세 롤(데이터·인프라 / RAG·자동화 / 대시보드)이 전부 이 하나의 테이블을 보고 일하는 구조라 **스키마가 제일 먼저 확정돼야** 나머지가 안 막힌다.

### 3-2. 지금 우리가 쓰는 테이블 — `ReorderRecommendation`
원본 7개 필드(`sku_code`/`predicted_demand`/`recommended_qty`/`risk_score`/`status`/`created_at`/`approved_by`)는 [[22-feature-spec]] 1-1절 참고.

**2026-09-14 확정 — 추가 필드 5개** ([[42-work-order-choimin]] 2절 결정 완료):
| 필드 | 타입 | 설명 |
| --- | --- | --- |
| resolved_at | DateTime | 승인/반려 처리 시각 |
| rejection_reason | Text | 반려 사유(드롭다운 4종+자유입력 병행) |
| auto_decidable | Boolean | ML이 계산 — 저위험이라 자동승인 후보인지 |
| auto_decided | Boolean | Power Automate가 기록 — 실제로 자동승인됐는지 ([[25-execution-design]] 2-5절, 담당자 부재 시 자동 의사결정 스트레치) |

risk_score 산출 근거(`stockout_urgency`/`popularity_weight`)는 필드로 저장하지 않고 그때그때 계산하는 쪽으로 확정(스키마 최소화). SKU 마스터는 별도 소형 Dataverse 테이블로 분리(Lookup) — 대시보드 조인용, 원본은 Factory/Blob에 두지 않고 Dataverse 안에 작게 복제.

**이 테이블을 실제로 Dataverse에 만드는 것 자체가 최민님 Week 1 첫 작업**이다.

### 3-3. 지금 우리가 쓰는 환경 — "2nd_5team"
회사가 아니라 개인 학교 계정이라 계정마다 기본으로 주어지는 "공유 환경"은 테이블 생성 권한이 없다. 그래서 나경 개인 명의로 만든 **Dataverse Developer 환경**("2nd_5team")을 팀 전체가 같이 쓰는 방식으로 우회했다([[2-onboarding-checklist]] 참고). 각자 본인 학교 M365 계정으로 [make.powerapps.com](https://make.powerapps.com)에 로그인 → 우측 상단에서 이 환경을 선택하면 접속된다. 지금은 전원 System Administrator 권한이고, 데모 직전에 `Reorder Approver`/`Viewer` 2종으로 좁힐 예정.

### 3-4. Security Role — 승인자 + 다중 조회자 (2026-09-11 확정, [[4-differentiation-ideas]] 논의 2)
- **Reorder Approver**: `ReorderRecommendation` 테이블 승인/반려 가능 — MD(나경) 1인
- **Viewer**: 읽기 전용 — 유관부서 다중 배정. 대상 부서는 [[24-alert-rules]] 알림 표의 수신자 컬럼 기준(예: 재무=마진 영향 확인, 생산/SCM=발주 이행 확인)

확정 배경(왜 MD 단독에서 승인자+다중조회자로 바뀌었는지)은 [[4-differentiation-ideas]] 논의 2 참고 — 화면은 MD 중심 1개 그대로, Viewer 다중화는 최민님 Week 1 Security Role 세팅 범위 안에서 처리 가능.

### 3-5. 대시보드가 Dataverse를 읽는 방법
> **2026-09-14 확정**: 대시보드는 Dataverse를 **직접** 부르지 않는다. 최민님이 만드는 별도 **C# Web API 서버**(`FashionAI.Api`)가 Dataverse Web API(OData)를 전담 호출하고, 대시보드는 이 API가 주는 JSON만 받는다 — 최민님이 C# 백엔드 개발을 해보고 싶다고 해서 이렇게 분리함. 상세 엔드포인트·설계는 [[25-execution-design]] 4절 참고.

지금 대시보드(`SampleDataService`)는 아직 CSV 파일을 읽고 있고, Dataverse 연동은 안 된 상태다. 연동되면 최민님의 API 서버가 **Dataverse Web API**(REST API 형태)로 Dataverse에 HTTP 요청을 보내서 데이터를 가져오는 방식이 된다 — 일반 SQL의 `SELECT * FROM ReorderRecommendation WHERE status='Pending'` 같은 조회를, Dataverse에서는 특정 URL로 HTTP GET 요청을 보내는 형태로 한다고 생각하면 된다. 인증은 Azure AD 앱 등록으로 발급받은 Client ID/Secret을 쓴다(최민 담당).

## 4. 용어 정리 (SQL 아는 사람 기준 비유)

| Dataverse 용어 | SQL로 치면 | 비고 |
| --- | --- | --- |
| 환경(Environment) | 하나의 DB 서버/인스턴스 | 우리는 "2nd_5team" 하나만 씀 |
| 테이블/엔터티 | 테이블 | `ReorderRecommendation`이 우리 테이블 |
| 컬럼 | 컬럼 | 위 3-2절 7개 필드 |
| 레코드 | 행(row) | SKU 하나당 재발주 추천 1건 = 레코드 1개 |
| Lookup | Foreign Key | `approved_by`가 User 테이블을 참조하는 Lookup |
| Choice | Enum | `status`가 Pending/Approved/Rejected 중 하나 |
| Security Role | 권한/역할 테이블 + 접근제어 로직 | 화면에서 클릭만으로 설정, 직접 구현 안 해도 됨 |
| Power Apps | (해당 없음, DB엔 없는 기능) | Dataverse 데이터로 화면을 자동 생성하는 노코드 툴 — 우리는 Power Apps 화면 자체는 안 쓰고 테이블·Security Role 관리용으로만 사용 |
| Power Automate | (해당 없음) | "레코드 생성되면 X 하기" 같은 트리거 자동화 — 우리 프로젝트에선 Teams 카드 발송을 담당 |
| Dataverse Web API | REST API | SQL 쿼리 대신 HTTP 요청으로 데이터를 읽고 쓴다 |

## 5. 지금 당장 누가 뭘 해야 하는가

- **최민**: `ReorderRecommendation`+SKU마스터 테이블 실제 생성 + Security Role 2종 세팅(Week 1 최우선, [[42-work-order-choimin]] 참고) + **C# Web API 서버(`FashionAI.Api`) 신규 구축**(2026-09-14 확정, Azure AD 앱 등록·MSAL 인증 포함)
- **나경·박형준**: API 서버가 주는 JSON만 받아 대시보드 렌더링(Dataverse 직접 연동 없음)
- **임현제**: ML 예측 결과가 위 필드 형태로 나오도록 산출물 정리 — Databricks가 직접 Dataverse에 적재(API 서버를 거치지 않는 별도 경로). `auto_decidable` 플래그 계산도 포함(스트레치, [[25-execution-design]] 2-5절)

## 6. 더 알아보고 싶으면

- [Microsoft Learn — Dataverse란?](https://learn.microsoft.com/ko-kr/power-apps/maker/data-platform/data-platform-intro) (공식 문서, 한국어)
- 이 프로젝트 안에서는 [[23-cost-plan]] "🏢 실제 기업은 D365를 어떻게 쓰는가" 절이 배경지식으로 제일 도움 됨
- 막히는 부분은 [[2-onboarding-checklist]] "🤖 문서가 너무 많아서 부담되면" 절처럼 Claude Code한테 이 볼트 열어두고 바로 물어봐도 됨
