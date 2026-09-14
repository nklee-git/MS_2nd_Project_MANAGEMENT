> **Goal**: MD 대시보드 내 `@태그`, `작업 할당`, `의사결정 승인(Approval)` 및 `내부 챗/메모` 테스트를 위해 카카오/NQNQ 조직 기반의 가상 인물 계정을 생성합니다.
> **2026-09-10 갱신**: 실제 개발팀(최민·임현제)을 NQNQ 내부 데이터·AI팀으로 신규 편입, 협업 허브 실무 시나리오(승인 문서·매출 데이터·의사결정 논의)를 Security Role 매핑과 함께 구체화. 이나경·최민·임현제(실제 팀원) 외 가상 인물 전원을 아이돌 멤버 이름(BTS·NewJeans·BLACKPINK·Red Velvet)으로 교체 — `@태그` 시연 시 팀원들이 외우기 쉽도록.

---

## 👤 1. NQNQ Brand Cell (핵심 내근 사용자)

| 이름 | 직책 | 역할 (R&R) | ID / 이메일 | 대시보드 주요 접근 메뉴 |
| :--- | :--- | :--- | :--- | :--- |
| **김남준** | NQNQ Brand Lead | 셀 총괄 / 최종 승인자 | `namjoon.k@kakaostyle.com` | 손익(P&L) 대시보드, 통합 KPI, 승인함 |
| **이나경** | NQNQ 메인 MD (나!) | 카테고리 기획, 원가/재고/소싱 총괄 | `nk.l@kakaostyle.com` | **MD 메인 종합 대시보드 (Admin)** |
| **박지민** | Technical Designer | 체형 패턴 설계, 샘플링 및 QC | `jimin.p@kakaostyle.com` | 샘플/스펙 관리, 체형 데이터베이스 |
| **김민지** | Content Marketer | 숏폼/릴스 기획, 인플루언서 협업 | `minji.k@kakaostyle.com` | 마케팅 ROI, 숏폼 성과, 프로모션 달력 |
| **김태형** | Visual Designer | 상세페이지 및 로고/패키징 디자인 | `taehyung.k@kakaostyle.com` | 디자인 자산(Asset), 상세페이지 승인 |

---

## 🤖 1-0. 데이터·AI팀 (신규, 2026-09-10 편입)

NQNQ 재고 리플레니시먼트 AI 시스템(Data Factory·Databricks·Dataverse)을 실제로 만들고 운영하는 팀. Brand Cell과 별도 팀이지만 같은 Year 1 핵심 인력으로 취급 — Brand Cell이 "무엇을 보여줄지"를 정한다면 데이터·AI팀은 "그 숫자가 어떻게 계산되는지"를 책임짐.

| 이름      | 직책                | 역할 (R&R)                                               | ID / 이메일                   | 대시보드 주요 접근 메뉴                 |
| :------ | :---------------- | :----------------------------------------------------- | :------------------------- | :---------------------------- |
| **최민**  | Data & Infra Lead | Data Factory 파이프라인, Dataverse 스키마·Security Role 관리, 배포 | `min.c@kakaostyle.com`     | Dataverse 관리 콘솔, 파이프라인 모니터링   |
| **임현제** | AI Forecast Lead  | Databricks 기반 수요예측 모델링, risk_score 산출, held-out 검증     | `hyunje.im@kakaostyle.com` | 예측대조 뷰(Admin), 모델 성능·오차율 모니터링 |

> **Security Role 참고**: 개발 중에는 두 분 다 System Administrator로 전체 접근하되, 데모 직전 `Reorder Approver`(승인 가능)가 아니라 `Viewer`로 낮춰서 "MD가 실제로 승인 버튼을 누르는" 시연 흐름을 방해하지 않도록 함 (3-0절 표 참고).

---

## 👥 1-1. Y2 신규 합류 (2025.03, 쇼룸 1호점 오픈 대응 — [[52-team-structure]] 참고)

| 이름 | 직책 | 역할 (R&R) | ID / 이메일 | 대시보드 주요 접근 메뉴 |
| :--- | :--- | :--- | :--- | :--- |
| **강해린** | MD 2 (카테고리 분담) | OUTER 카테고리 기획, 원가/재고 관리 | `haerin.k@kakaostyle.com` | 카테고리별 재고·매출 대시보드 |
| **박수영** | 쇼룸 매니저 (홍대 1호점) | 오프라인 쇼룸 운영, 재고 현장관리, R05 반품 처리 | `suyoung.p@kakaostyle.com` | 오프라인 매출·방문객 대시보드, [[33-returns-process]] R05 처리 |
| **김혜인** | CS 전담 연동 담당 | 고객 문의·반품 이슈 1차 대응, MD 에스컬레이션 | `hyein.k@kakaostyle.com` | CS 티켓 큐, 반품 사유코드 통계 |

## 👥 1-2. Y3 신규 합류 (2026.03, 매장 확장·홀세일 진입 대응)

| 이름 | 직책 | 역할 (R&R) | ID / 이메일 | 대시보드 주요 접근 메뉴 |
| :--- | :--- | :--- | :--- | :--- |
| **전정국** | MD 3 (카테고리 분담) | ACC·DRS 신규 카테고리 기획 | `jungkook.j@kakaostyle.com` | 카테고리별 재고·매출 대시보드 |
| **김지수** | MD 4 (홀세일 연계) | 홀세일 파트너向 SKU 구성, 도매공급가 관리 | `jisoo.k@kakaostyle.com` | [[42-channel-settlement]] 홀세일 정산 뷰 |
| **정호석** | 쇼룸 매니저 (강남 2호점) | 오프라인 쇼룸 운영, 매장 KPI 관리 | `hoseok.j@kakaostyle.com` | 오프라인 매출·방문객 대시보드 |
| **민윤기** | 홀세일 영업 담당 | 편집숍/백화점 입점 영업, 계약 관리 | `yoongi.m@kakaostyle.com` | 홀세일 파트너 리스트, 계약 현황 |
| **김석진** | 데이터/AI 운영 담당 | [[21-system-model]] 알림 로직 튜닝, 대시보드 지표 관리 | `seokjin.k@kakaostyle.com` | 전체 KPI 대시보드, [[24-alert-rules]] 설정 |

> 팀 규모 추이: Y1 7명(Brand Cell 5 + 데이터·AI팀 2) → Y2 10명 → Y3 15명. 데이터·AI팀은 Y1부터 존재하되 [[52-team-structure]]의 "5인 정예 팀" 서사는 Brand Cell 기준 — 실제 시스템 빌더인 데이터·AI팀은 별도 트랙으로 취급.

---

## 🔗 2. 유관부서 네트워크

> MD 대시보드 내에서 `@이름`으로 호출하여 실시간 요청 및 승인을 주고받는 유관부서 가상 인물입니다.

#### 📊 CFO / 재무 부문
* **강슬기 팀장 (경영기획팀)** | `seulgi.k@kakaostyle.com`
  * *대시보드 활용*: NQNQ 월별 예산(OPEX) 집행률 승인 및 BEP 달성도 모니터링. 고액 발주 2차 승인권자(3-1절 시나리오 B).
* **박채영 파트장 (회계팀)** | `chaeyoung.p@kakaostyle.com`
  * *대시보드 활용*: OEM 공장 기성금/원단 대금 정산 확인 및 세금계산서 승인 요청 수신.

#### 💻 CTO / 개발 부문 (카카오스타일 본사, 데이터·AI팀과 별개)
* **손승완 수석 (광고커머스개발팀)** | `seungwan.s@kakaostyle.com`
  * *대시보드 활용*: "앱 내 체형 필터(스트레이트/웨이브) UX 개발 티켓" 수신 및 기능 업데이트 공유. NQNQ 전용 시스템(데이터·AI팀 담당)이 아니라 카카오스타일 공통 앱 인프라 담당이라는 점에서 최민/임현제와 역할 구분.

#### 🚚 SCM / 물류 부문
* **배주현 팀장 (직진배송 풀필먼트팀)** | `juhyun.b@kakaostyle.com`
  * *대시보드 활용*: NQNQ 신상품 5,000벌 입고 예정일 수신, 재고 부족/반품률 알림 수신. 생산 지연 승인 체인의 1차 판단자(3-1절 시나리오 C).

#### 🏭 외부 파트너 (제조 공장)
* **장성호 사장 (성진어패럴 - 메인 봉제 공장)** | `sh.jang@sungjin-apparel.co.kr`
  * *대시보드 활용*: [공장 전용 뷰] 생산 스케줄 입력, 샘플 수정 요청 건 확인 및 출고 확정.

---

## 💬 3. 협업 허브 실무 시나리오 (Collaboration Feature Spec)

> [[21-system-model]] 크로스커팅 계약(Data Factory→Databricks→Dataverse→Power Automate→Teams→대시보드)을 실제 인물·부서 단위로 구체화한 버전. Security Role·Power Automate 트리거·Teams Adaptive Card 설계 시 이 절을 그대로 참고.

### 3-0. Security Role 매핑

| 인물/팀                 | Dataverse Security Role                      | 비고                                                                 |
| -------------------- | -------------------------------------------- | ------------------------------------------------------------------ |
| 이나경                  | `Reorder Approver`                           | 표준 발주 승인권자 (1차)                                                    |
| 김남준                  | `Reorder Approver` (상위)                      | 5,000만원 이상 최종 승인                                                   |
| 강슬기 (CFO)            | `Budget Approver` *(신규 제안)*                  | 500만원 이상 발주 2차 예산 승인 — 기존 `Reorder Approver`/`Viewer` 2종에 추가 검토 필요 |
| 최민·임현제 (데이터·AI팀)     | `System Administrator` (개발용) → 데모 시 `Viewer` | 시스템은 관리하지만 승인 액션의 주인공은 아님                                          |
| 배주현 (SCM)            | `Viewer` + Power Automate 알림 수신              | 승인 권한 없이 알림만 수신, 필요시 코멘트                                           |
| 박지민·김민지·김태형 등 나머지 인원 | `Viewer`                                     | 조회 전용                                                              |

### 3-1. 자동 승인 문서 발송 시나리오

**시나리오 A — 표준 재고 리오더 승인 (기존 확정 플로우)**
- 트리거: `risk_score ≥ 0.7` AND `available_qty ≤ reorder_point`
- Databricks 예측 결과 → Dataverse `ReorderRecommendation` 레코드 생성 → Power Automate 트리거 → Teams Adaptive Card 발송 (수신: 이나경)
- 카드 필드: SKU·스타일명·risk_score·추천발주량·현재 재고·[승인]/[반려] 버튼
- 반려 시: 반려 사유 선택 → 데이터 이상 가능성이 사유(예: "예측 신뢰도 낮음")면 @최민에게 자동 알림 — "이 SKU 예측 로직 확인 요청"

**시나리오 B — 고액 발주 2단계 승인 (신규, [[72-dashboard-spec]] "승인 워크플로우 스텝퍼" 백로그를 구체화)**
- 트리거: `recommended_qty × unit_cost ≥ 5,000,000원`
- 1차(이나경) 승인 → 자동으로 2차 카드가 **강슬기(CFO)**에게 발송 ("예산 재승인 요청" — OPEX 집행률과 함께 표시)
- `recommended_qty × unit_cost ≥ 50,000,000원`이면 3차로 **김남준(Brand Lead)** 최종 승인까지 자동 라우팅
- 어느 단계에서든 반려되면 체인 중단 + 이나경에게 반려 사유 통보

**시나리오 C — 생산 지연 승인 (SCM 연계)**
- 트리거: `PurchaseOrder.expected_arrival_date` 경과 AND `status != 입고완료`
- **장성호(공장)** → **배주현(SCM)**에게 지연 사유 보고 카드 자동 발송
- 배주현이 "메인 노출 일정 조정 필요" 체크박스 선택 시 → **이나경**에게 `@배주현: [스타일명] 입고 지연, 메인 노출 일정 조정 필요` 멘션 자동 생성 (지금 대시보드 협업허브 멘션 예시가 이 시나리오의 실제 사례)

### 3-2. 매출 데이터 전송 시나리오

**시나리오 D — 주간 매출 리포트**
- 매주 월요일 09:00, Power Automate 스케줄 트리거
- `monthly_revenue_summary` 기반 주간 매출·전주 대비 증감률·AOV 요약 카드를 Teams "NQNQ 전체" 채널에 자동 게시
- 수신: 이나경, 김남준, 김민지 (마케팅이 프로모션 효과 바로 확인 가능하도록)

**시나리오 E — 카테고리 매출 이상치 알림**
- 트리거: 특정 `category_code` 매출이 전주 대비 **-20% 이상** 하락
- 수신: 이나경 + 해당 카테고리 담당 MD(강해린/전정국/김지수 — 카테고리별 자동 라우팅) + 김민지(마케팅 원인 파악용)
- 카드에 "재고 문제인지 수요 둔화인지" 1차 진단 체크리스트 포함 (재고 있음/부족 자동 표시)

**시나리오 F — 분기 마감 리포트 → CFO**
- 분기 마감일, `SALES_TARGETS`(Y1/Y2/Y3 목표) 기준 달성률 자동 계산 → **강슬기**에게 카드 전송
- BEP 달성도, 카테고리별 기여도 포함 — 다음 분기 예산 편성 회의 자료로 바로 사용 가능한 형태

### 3-3. 의사결정 협업 논의 시나리오

**시나리오 G — 신규 SKU 기획 리뷰**
- 트리거: 베스트셀러 위젯에서 특정 스타일이 3주 연속 판매량 상위 10%
- **이나경**이 "라인 확장 검토" 스레드 자동 생성 → `@박지민`(패턴 확장 가능성) + `@김민지`(마케팅 앵글) 자동 태그
- 스레드에 해당 스타일의 최근 판매 추이 스파크라인 자동 첨부

**시나리오 H — 재고 위험 대응 회의**
- 트리거: risk_score 상위 5개 SKU 중 3개 이상이 동일 카테고리에 몰림 (구조적 신호 가능성)
- **이나경 + 최민(데이터·AI팀, 데이터 검증) + 배주현(SCM)** 3자 스레드 자동 생성
- 논의 주제 템플릿: "일시적 트렌드 vs 구조적 수요 증가 — 재발주점(reorder_point) 임시 상향 필요 여부"

**시나리오 I — 트렌드캡슐 런칭 일정 조율**
- 트리거: 신규 TREND 캡슐 `launch_date`가 해당 SKU `PurchaseOrder` 입고 예정일보다 빠름(공급 리스크)
- **이나경 + 배주현 + 김민지** 3자 협업 스레드 자동 생성 — 런칭일 연기 또는 초도물량 축소 중 선택하는 의사결정 카드 첨부

### 3-4. Teams ↔ 협업허브 연동 프로세스 (2026-09-10 신규)

> 지금까지 시나리오 A~I는 "대시보드 → Teams" 단방향(승인 카드 발송)만 다뤘음. 여기서는 **양방향**(Teams에서 온 메시지가 대시보드 협업허브에 자동으로 뜨고, 대시보드에서 답장하면 다시 Teams로 나가는) 흐름을 구체화. [[61-entity-dictionary]] 5절 백로그의 `MENTION` 엔티티를 실제 필드까지 확정하는 절.

#### (1) 인바운드 — Teams 메시지가 협업허브에 자동으로 뜨는 흐름
1. Teams 채널/DM에 메시지 도착 (예: NQNQ 협업 채널에 `@이나경 [스타일명] 재입고 지연` 게시)
2. Power Automate 트리거: **"새 채널 메시지가 게시되는 경우"**(Teams 커넥터)
3. Power Automate가 메시지 파싱:
   - 발신자·본문·타임스탬프·`@멘션` 대상 추출
   - 본문에서 SKU 코드 패턴(`NQ-[A-Z]+-\d+...`)이나 발주추천 ID(`RR-\d+`)를 정규식으로 감지 → 관련 레코드 자동 연결
   - Teams 메시지에 파일(사진·엑셀 등)이 첨부돼 있으면 SharePoint 링크 그대로 보존
4. Dataverse `MENTION` 테이블에 레코드 생성
5. 대시보드 협업허브가 최민님의 C# API 서버(`FashionAI.Api`) 경유로 최신 `MENTION`을 조회해 카드로 표시(2026-09-14부로 Dataverse 직접 호출 아님) — 발신자, 본문, **관련 문서 미리보기**, 관련 SKU/발주 요약이 한 카드 안에 같이 뜸

**`MENTION` 테이블 필드 (신규 확정 제안)**
| 필드 | 타입 | 설명 |
| --- | --- | --- |
| mention_id | string (PK) | |
| teams_message_id | string | Teams 원본 메시지 ID (답장 매칭용) |
| from_user | string | 발신자 (Dataverse User 참조) |
| to_user | string | `@멘션` 대상 |
| message_text | string | 본문 |
| related_entity_type | string | `ReorderRecommendation` / `PurchaseOrder` / 없음 |
| related_entity_id | string | 위 타입의 실제 레코드 ID (본문 정규식 파싱 결과) |
| attachment_url | string, nullable | Teams 첨부파일의 SharePoint 링크 |
| status | string | 안읽음 / 읽음 / 답변완료 |
| created_at | datetime | |

#### (2) 관련 문서 자동 첨부 로직
- 메시지 본문에 발주추천 ID나 SKU 코드가 감지되면 → 해당 `ReorderRecommendation`의 risk_score·재고현황 요약을 "관련 문서" 카드로 자동 첨부 (별도 파일이 아니라 대시보드 내부 데이터 스냅샷)
- Teams 메시지에 실제 파일이 첨부된 경우 → 원본 SharePoint 링크를 그대로 노출(다운로드/미리보기 버튼), 별도 저장은 하지 않음(중복 방지)

#### (3) 아웃바운드 — 대시보드에서 답장하면 Teams로 나가는 흐름
1. 협업허브에서 사용자가 답장 입력 후 [전송]
2. 대시보드가 Dataverse에 답장 레코드 저장(같은 `teams_message_id` 스레드로 연결) → Power Automate 트리거 호출(Dataverse 레코드 생성 트리거 또는 HTTP 트리거)
3. Power Automate가 **"채널에 메시지 게시"**(Teams 커넥터, `replyToId`에 원본 `teams_message_id` 지정)로 원 스레드에 답글 게시 — "[대시보드에서 응답]" 접두어 또는 전용 봇 계정으로 발송해 출처 구분
4. 원 발신자는 Teams 앱 밖으로 안 나가도 실시간으로 답장을 받음 — 대화가 대시보드-Teams 양쪽 어디서든 이어짐

#### (4) 구현 전 필요한 것
- Dataverse `MENTION` 테이블 신설(위 필드 기준, [[61-entity-dictionary]] 반영)
- Power Automate 플로우 2개: (a) Teams→Dataverse 인바운드, (b) 대시보드→Dataverse→Teams 아웃바운드
- M365 Developer 테넌트에 Teams 봇 계정 또는 웹훅 등록
- ✅ 2026-09-14 확정: [[42-work-order-choimin]] 1-2절 — 별도 C# API 서버(`FashionAI.Api`)로 결정됨. (3)번 트리거는 대시보드→API 서버→Dataverse 경로로 진행

---

## 🌐 4. 향후 아이디어 (스트레치, 미착수)

- **메타버스 오피스형 협업허브** (2026-09-10 아이디어 제안) — Gather.town류 2D 아바타 가상오피스로 협업허브를 시각화하는 안. 현재 확정 스코프(Data Factory·Databricks·Dataverse·Power Automate·Teams)엔 없는 별도 플랫폼 연동이라 2.5주 일정 안에서는 보류. [[82-ppt-plan]] 발표 연출용 비주얼로는 검토 가능 — 실제 기능이 아니라 발표 자료 톤앤매너 참고용으로만 남겨둠.

---

### 참고
- `@Mention` 스레드 태그: `#긴급승인` `#생산지연` `#원가절감` `#체형스펙수정` `#직진배송입고` `#매출이상치` `#라인확장검토` (2026-09-10, 시나리오 D~I 추가로 태그 3종 확장)
- 지금 ASP.NET Core 대시보드(70.FRONT/dashboard)의 협업허브 화면은 위 시나리오 중 A(멘션 예시)·C(태스크 예시)만 샘플 데이터로 먼저 반영돼 있음 — 나머지는 `MENTION`/`TASK`/`ALERT_LOG` 엔티티 확장 후 순차 반영 예정.
