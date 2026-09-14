> **용도**: 이 프로젝트에서 시각화 가능한 것 전부를 한 곳에 모은 허브 문서. 이 파일 하나만 열어도 시스템 구조·데이터 모델·조직·일정·우선순위의 전체 뼈대가 보이는 게 목표. 각 다이어그램의 원본(자세한 텍스트 설명·변경이력)은 아래에 링크된 문서이며, 그 문서가 SSOT — 이 허브는 "요약 시각화 모음"이지 별도 결정 기록이 아니다. 아키텍처가 바뀌면 원본 문서 먼저 고치고 여기 동기화할 것.

---

## 1. 전체 시스템 아키텍처 (원본: [[21-system-model]] 2절)
실선이 핵심 데모 경로, 점선은 Should-have/검증용 보조 경로.

```mermaid
flowchart LR
    src[("로컬 데이터<br/>nqnq.db · 124만 건")]
    blob[("Blob Storage<br/>원시데이터 업로드")]
    df["Azure Data Factory<br/>오케스트레이션(트리거만)<br/>cutoff 8/20"]
    ml["Azure Databricks<br/>ML 처리(기술 핵심)<br/>짧은 주기 micro-batch"]

    subgraph tenant["M365 Developer 테넌트 (무료 샌드박스)"]
        dv[("Dataverse<br/>ReorderRecommendation<br/>+ SKU 마스터 + Security Role(승인자+다중조회자)")]
        pa["Power Automate<br/>트리거 플로우"]
        teams["Teams<br/>Adaptive Card 승인"]
        bi["Power BI<br/>(Should-have)"]
    end

    api["C# Web API 서버<br/>(신규, 최민 담당)"]
    dash["ASP.NET Core MVC 대시보드<br/>승인이력 · 예측대조"]
    holdout[("9월 held-out 실측<br/>(모델엔 비공개)")]

    src --> blob --> df --> ml -->|예측 결과 적재| dv
    dv -->|신규 행 감지| pa
    pa -->|승인요청 카드| teams
    teams -->|승인/반려 응답| pa
    pa -->|상태 업데이트| dv
    dv -.조회.-> bi
    dv -->|Dataverse Web API| api -->|내부 API| dash
    holdout -.Week3 예측·실측 대조.-> dash

    classDef data fill:#e3edf5,stroke:#2f6690,color:#1b1c2b;
    classDef mlcls fill:#eeedfc,stroke:#4338ca,color:#1b1c2b;
    classDef infra fill:#f6ecfd,stroke:#9333ea,color:#1b1c2b;
    classDef auto fill:#fbeedd,stroke:#b4690a,color:#1b1c2b;
    classDef dashcls fill:#e4f3ec,stroke:#2f7d5e,color:#1b1c2b;
    classDef neutral fill:#f0eff8,stroke:#6b6c85,color:#1b1c2b;

    class df,blob data
    class ml mlcls
    class dv,api infra
    class pa,teams auto
    class dash dashcls
    class src,holdout,bi neutral
```

## 2. 데이터 흐름 4단계 요약
```mermaid
flowchart LR
    A["1. 원시데이터 생성<br/>generate_v4/v5.py"] --> B["2. Blob 업로드<br/>+ Data Factory 트리거"]
    B --> C["3. Databricks 처리<br/>예측·risk_score 산출"]
    C --> D["4. Dataverse 적재<br/>ReorderRecommendation만"]
    D --> E["Power Automate<br/>→ Teams 승인"]
    E --> F["C# API 서버<br/>→ 대시보드 표시"]
```

## 3. ERD — 핵심 트랜잭션 엔티티 (원본: [[62-erd]], 전체 필드는 [[61-entity-dictionary]])
```mermaid
erDiagram
  CATEGORY ||--o{ PRODUCT : has
  PRODUCT ||--o{ SKU : has
  FACTORY ||--o{ PURCHASE_ORDER : fulfills
  PURCHASE_ORDER ||--o{ PO_ITEM : contains
  SKU ||--o{ PO_ITEM : ordered_as
  SKU ||--o{ INVENTORY : tracked_in
  SKU ||--o{ INVENTORY_LEDGER : moves
  CHANNEL ||--o{ ORDERS : receives
  CUSTOMER ||--o{ ORDERS : places
  ORDERS ||--o{ ORDER_ITEM : contains
  SKU ||--o{ ORDER_ITEM : sold_as
  ORDERS ||--o{ RETURN_REQUEST : may_have
  SKU ||--o{ RETURN_REQUEST : returned_as
  STORE ||--o{ ORDERS : optional_source
```

## 4. 팀 조직 & 역할 (2026-09-14 확정, 원본: [[21-system-model]] 롤별 담당표)
```mermaid
flowchart TB
    lead["최민<br/>🏆 테크리드(2026-09-14 확정)<br/>이견조율 최종결정권만, 책임은 팀 전체 분담"]
    lead --> pipeline["데이터·인프라<br/>Blob·Data Factory<br/>Dataverse 스키마"]
    lead --> api["백엔드 API(신규)<br/>FashionAI.Api<br/>C# Web API 서버"]

    ml["임현제<br/>ML·모델링"] --> mlwork["Databricks<br/>수요예측·risk_score<br/>auto_decidable 판정"]

    pm["나경<br/>PM/TPM"] --> rag["RAG·자동화<br/>Power Automate<br/>Teams Adaptive Card"]
    pm --> coord["전체 조율<br/>크로스커팅 계약 관리<br/>체크포인트 운영"]

    fe["박형준(9/11 합류)<br/>프론트"] --> front["대시보드<br/>Razor Pages 2뷰"]
    pm -.공동.- front

    classDef leadcls fill:#fbeedd,stroke:#b4690a,color:#1b1c2b;
    classDef personcls fill:#e3edf5,stroke:#2f6690,color:#1b1c2b;
    classDef workcls fill:#f0eff8,stroke:#6b6c85,color:#1b1c2b;
    class lead leadcls
    class ml,pm,fe personcls
    class pipeline,api,mlwork,rag,coord,front workcls
```

## 3-1. 데이터 프레임(기획 문서) 구조 — DB 엔티티와 다른 레이어 (원본: `30-data/31-nqnq-frame` 폴더)
> 위 3번은 **데이터베이스 엔티티** 관계도이고, 이건 그 엔티티들이 어떤 **기획 논리**로 도출됐는지 담은 문서 묶음 자체의 구조다. 브랜드 결정 → 카탈로그 설계 → 공급망/세일즈 조건 → 조직/워크플로우 → (마지막에) 기술 데이터 모델, 순서로 위에서 아래로 논리가 이어진다.

```mermaid
flowchart TB
    frame["31-nqnq-frame<br/>가상 브랜드 기획 문서 전체"]
    frame --> home["00-home<br/>NQNQ가 뭔지, 3개년 로드맵"]
    frame --> brand["10-brand<br/>브랜드스토리·타겟퍼소나·톤앤매너"]
    frame --> catalog["20-catalog<br/>카테고리·SKU체계·성장로드맵(7개 문서)"]
    frame --> supply["30-supply-chain<br/>공장·재고정책·반품프로세스"]
    frame --> sales["40-sales-finance<br/>채널·매출·KPI·시즌캘린더(8개 문서)"]
    frame --> org["50-org-workflow<br/>조직구조·가상인물·승인워크플로우"]
    frame --> dm["60-data-model<br/>ERD·엔터티딕셔너리·변경이력(가장 기술적)"]

    home --> brand --> catalog --> supply --> sales --> org --> dm

    classDef framecls fill:#f6ecfd,stroke:#9333ea,color:#1b1c2b;
    classDef leafcls fill:#e3edf5,stroke:#2f6690,color:#1b1c2b;
    class frame framecls
    class home,brand,catalog,supply,sales,org,dm leafcls
```

## 5. 승인 워크플로우 (원본: [[54-approval-workflow]])
```mermaid
flowchart LR
    req["요청 발생<br/>(재고리오더/초도발주/가격변경 등)"] --> chk{"금액 규모?"}
    chk -->|"500만원 이하"| md["MD 단독 승인"]
    chk -->|"500만원~5천만원"| mgmt["MD → 경영기획 승인"]
    chk -->|"5천만원 초과"| brand["MD → 경영기획 → Brand Lead 공동승인"]
    md --> done["진행 → 완료"]
    mgmt --> done
    brand --> done
```

### 5-1. (신규 스트레치) 담당자 부재 시 자동 의사결정 — 원본: [[25-execution-design]] 2-5절
```mermaid
flowchart LR
    card["Teams 승인카드 발송"] --> wait{"SLA 시간 내<br/>응답?"}
    wait -->|Yes| human["사람이 승인/반려"]
    wait -->|No, 타임아웃| risk{"auto_decidable<br/>= true?(저위험)"}
    risk -->|Yes| auto["자동승인<br/>approved_by=System(Auto)<br/>대시보드에 뱃지 표시"]
    risk -->|No, 고위험| escalate["Viewer 그룹 전체<br/>에스컬레이션 재알림<br/>(Pending 유지)"]
```

## 6. 프로젝트 타임라인 (원본: [[1-execution-plan]])
```mermaid
gantt
    dateFormat  YYYY-MM-DD
    axisFormat  %m/%d
    section 버퍼
    팀 확정~타운홀        :done, 2026-09-02, 2026-09-10
    section Week 1
    스키마·API 확정 + 뼈대 구현 :active, 2026-09-11, 2026-09-20
    9/14 아키텍처·테크리드 확정 :milestone, 2026-09-14, 0d
    section Week 2 (짧음, 7일→3일)
    실데이터 전환 + 통합       :2026-09-21, 2026-09-23
    9/23 풀루프 체크포인트     :crit, milestone, 2026-09-23, 0d
    section 추석
    연휴(작업없음)            :2026-09-24, 2026-09-25
    section Week 3
    검증·동결·리허설          :2026-09-26, 2026-09-28
    section 발표
    최종 발표(9/29)          :milestone, 2026-09-29, 0d
```

## 7. 기능 우선순위 티어 (원본: [[3-feature-backlog]])
```mermaid
flowchart TB
    T0["Tier 0 — 확정 Must<br/>ML수요예측(Databricks)→Dataverse→Teams승인→발주확정<br/>대시보드 2뷰, Security Role 2종, held-out 검증"]
    T1["Tier 1 — 2주 스트레치(시간 남으면)<br/>GenAI 예측근거 설명, 24절기 알림<br/>Security Role 확장, 라인구분 필터"]
    T2["Tier 2 — 3차 프로젝트 백로그(이번엔 안 함)<br/>대시보드 모듈화, RAG Q&A, Power BI 연동"]
    T3["Tier 3 — 장기 비전(마켓플레이스 등재 수준)<br/>소비자 스토어프론트, AppSource 정식 등재"]
    T0 --> T1 --> T2 --> T3
    style T0 fill:#e4f3ec,stroke:#2f7d5e
    style T1 fill:#fbeedd,stroke:#b4690a
    style T2 fill:#f0eff8,stroke:#6b6c85
    style T3 fill:#f0eff8,stroke:#6b6c85,stroke-dasharray: 5 5
```

## 8. 카테고리 · SKU 분류체계 (원본: [[21-core-categories]], [[22-sku-code-system]])
```mermaid
flowchart TB
    root["NQNQ 카탈로그<br/>520 SKU(418 베이직+102 트렌드캡슐) · 41 상품"]
    root --> TOP["TOP<br/>스트레이트/웨이브/내추럴 체형 태그"]
    root --> PNT["PANTS<br/>5-Length 슬랙스 등"]
    root --> CLR["COLOR<br/>웜/쿨/뮤트 퍼스널컬러"]
    root --> OUT["OUTER"]
    root --> ACC["ACC"]
    root --> DRS["DRESS"]
    root --> TREND["트렌드캡슐(102)<br/>시즌 한정, 1~2시즌 후 단종"]

    TOP --> HERO1["HERO 3.0x"]
    TOP --> STEADY1["STEADY 1.0x"]
    TOP --> NICHE1["NICHE 0.3x"]
```

## 9. 비용/인프라 레이어 (원본: [[23-cost-plan]])
```mermaid
flowchart TB
    subgraph free["무료 티어 (M365 Dev Program)"]
        dv2["Dataverse"]
        pa2["Power Automate"]
        tm2["Teams"]
        bi2["Power BI"]
    end
    subgraph paid["학생크레딧/팀예산 — 사용량 과금, 자동종료 필수"]
        adf["Data Factory<br/>(저비용)"]
        dbx["Databricks<br/>소형클러스터+15~30분 자동종료"]
        apisrv["C# API 서버<br/>(App Service, 추가비용 없음)"]
    end
    adf --> dbx --> dv2
    dv2 --> pa2 --> tm2
    dv2 --> apisrv

    style dbx fill:#fbeedd,stroke:#b4690a
```

---

## 다이어그램 목록 (텍스트 인덱스)
| # | 다이어그램 | 원본 문서 |
| --- | --- | --- |
| 1 | 전체 시스템 아키텍처 | [[21-system-model]] |
| 2 | 데이터 흐름 4단계 | [[21-system-model]] |
| 3 | ERD | [[62-erd]] / [[61-entity-dictionary]] |
| 3-1 | 데이터 프레임(기획 문서) 구조 | `31-nqnq-frame` 폴더 |
| 4 | 팀 조직·역할 | [[21-system-model]] |
| 5 | 승인 워크플로우 (+자동의사결정) | [[54-approval-workflow]] / [[25-execution-design]] |
| 6 | 프로젝트 타임라인 | [[1-execution-plan]] |
| 7 | 기능 우선순위 티어 | [[3-feature-backlog]] |
| 8 | 카테고리·SKU 분류체계 | [[21-core-categories]] / [[22-sku-code-system]] |
| 9 | 비용/인프라 레이어 | [[23-cost-plan]] |
