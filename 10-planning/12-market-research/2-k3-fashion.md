# K3 Fashion 기능 정리

## 1. 개요

**K3 Fashion**(정식으로는 K3|fashion, 현재 운영사명 K3 Fashion Solutions)은 영국의 K3 Business Technology Group이 개발한 패션·의류 업계 전용 ERP 솔루션이다. 2023년 Infosys가 K3를 인수하면서 현재는 Infosys 산하 브랜드로 운영되고 있다. Microsoft Dynamics 365 Finance, Supply Chain Management(SCM), Commerce 위에서 동작하며, "컨셉부터 소비자까지(concept to consumer)"라는 슬로건대로 디자인 단계부터 소싱·생산·물류·매장 판매까지 패션 브랜드의 전 과정을 하나의 시스템 안에서 관리하도록 설계되었다.

주요 타깃은 직원 1,000명 이상의 대형 패션·의류 브랜드/리테일러이며, 클라우드 기반으로 제공되고 가격은 별도 견적을 통해서만 공개된다.

## 2. 전체 아키텍처: Microsoft Dynamics 365와의 관계

K3 Fashion은 D365 위에 별도로 얹혀 데이터를 주고받는 "연동(integration)" 방식이 아니라, K3 스스로 "Dynamics 365 기술 구조 안에 완전히 내장된 코드(fully embedded code in the Dynamics 365 technical landscape)"라고 설명하는 **임베디드(embedded) 확장 구조**를 취한다.

- K3가 만든 기능들은 D365 Finance & Operations의 애플리케이션 코드 안에 확장 모듈로 직접 들어가 있으며, 같은 데이터베이스, 같은 보안/권한 체계, 같은 화면 프레임워크를 그대로 사용한다.
- 회계·재무 등 범용 ERP 기능은 D365 표준 기능을 그대로 쓰고, K3는 사이즈·컬러 변형, 시즌 관리, 소싱 등 **패션 특화 기능**에만 집중해 개발했다.
- 이 구조 덕분에 Microsoft는 K3를 자사의 "패션 전문 글로벌 ISV(Independent Software Vendor)"로 공식 파트너 취급하고 있다.
- 임베디드 구조로 인해 K3 기능들은 Microsoft 생태계의 연결 서비스들과 자연스럽게 이어진다: **Teams, Office 365, Power BI, Dataverse, Copilot(AI 어시스턴트)**.
  - 예: 창고 직원과 매장 직원이 Teams로 재고를 확인, CRM 데이터로 고객 맞춤 영업, Copilot이 시즌별 실적 리포트를 자동 생성.

> 참고: 여기까지가 K3·Microsoft가 공개적으로 밝힌 "구조와 흐름" 수준의 정보이며, 실제 테이블 스키마나 API 상세 스펙 등 개발자용 문서는 공개되어 있지 않다(파트너사 전용 문서로 추정).

## 3. 핵심 기능 상세

### 3.1 Product Wizard (상품 등록 마법사)

새 상품(스타일)을 등록할 때 컬러, 사이즈, 소재, 가격 등 필요한 정보를 단계별로 안내받으며 빠르게 입력할 수 있는 도구.

- 복잡한 화면을 처음부터 다 채우는 대신 마법사가 순서대로 질문하듯 안내 → 상품 등록 속도 대폭 단축.
- **동작 방식**: D365 표준 "상품 정보 관리(Released Product / Product Variant)" 모듈을 확장한 화면. 마법사에서 입력을 마치면 그 결과가 D365의 표준 "출시 상품(Released Product)"과 "상품 변형" 테이블에 그대로 저장되어, 이후 가격 책정·재고·판매주문 등 D365의 다른 기능들이 이 데이터를 문제없이 인식·활용한다.

### 3.2 Matrix (컬러-사이즈 매트릭스)

컬러를 세로축, 사이즈를 가로축(또는 반대)으로 하는 격자표 형태로 상품 변형(variant)을 한눈에 보여주고 입력하는 화면.

- 패션 상품은 한 스타일에 컬러 10종 × 사이즈 8종처럼 변형 조합(SKU)이 매우 많은데, 이를 매트릭스 표 안에서 각 칸에 수량·가격을 바로 채워 넣어 대량의 SKU를 빠르게 등록·관리할 수 있다.
- **동작 방식**: D365가 원래 갖고 있는 "속성(dimension) 조합으로 변형 상품을 만드는" 표준 기능을 패션 업계 규모에 맞게 격자표 UI로 확장한 것. 입력 결과는 D365의 상품 변형/재고 차원 조합 테이블에 직접 반영된다.

### 3.3 Ratio Curves (사이즈 배분 비율 곡선)

사이즈별로 미리 정해둔 배분 비율 템플릿.

- 예: S:M:L:XL = 10%:30%:40%:20%로 항상 배분한다고 설정해두면, 총수량이 정해질 때마다 이 비율을 자동 적용해 사이즈별 수량을 자동 계산.
- 매번 사이즈별 수량을 수작업으로 입력할 필요 없이, 과거 판매 데이터 기반의 비율 곡선을 여러 상품·매장에 반복 적용 가능.
- **동작 방식**: 한 번 정의하면 마스터 데이터로 저장되고, 이후 구매주문(PO) 생성이나 매장 간 재고 이동(stock transfer) 시 D365 SCM 모듈이 이 비율을 자동 참조해 총수량을 사이즈별로 자동 분할한다. 즉 발주·배분 단계에서 사람 개입 없이 자동 적용되는 규칙.

### 3.4 Season Management (시즌 관리)

S/S(봄여름), F/W(가을겨울) 등 시즌 단위로 컬렉션을 기획·관리하는 기능.

- 시즌 시작 전 어떤 상품을 낼지 미리 계획(선시즌 기획).
- 시즌 진행 중에도 판매 추이를 보며 추가 발주·물량 조정 가능(오픈투바이, open-to-buy 가시성).
- **동작 방식**: D365의 상품 카테고리 계층 구조에 "시즌" 속성을 추가하는 방식으로 동작. D365의 수요예측(demand planning) 기능이 시즌 정보를 반영해 계산하고, Power BI로 시즌별 리포트를 뽑을 때도 이 데이터가 그대로 활용된다.

### 3.5 Retail Inventory Management (소매 재고 관리)

매장 단위, 지역 단위로 재고를 실시간 파악·관리하는 기능.

- 매장별/온라인몰 재고 현황을 한눈에 파악, 매장 간 재고 이동이나 보충(replenishment) 처리.
- 품절과 과잉재고를 동시에 방지하는 것이 목적.
- 옴니채널 계획 기능을 통해 도매와 소매를 함께 지원하며, 부서별(디자인·구매·생산·리테일) 역할 기반 데이터 접근으로 협업을 강화.
- **동작 방식**: D365 Commerce(매장/POS)와 Supply Chain Management(창고)를 잇는 영역. 매장 POS(D365 Commerce 클라우드 POS)에서 판매가 발생하는 즉시 중앙 재고 데이터가 실시간 갱신되고, K3가 여기에 패션 업계 특유의 보충·배분 로직을 추가한 구조.

### 3.6 Product Lifecycle Management, PLM (제품 수명주기 관리)

상품이 "디자인 아이디어 → 샘플 제작 → 승인 → 생산 → 판매"까지 거치는 전체 과정을 하나의 시스템에서 관리.

- 내장 PLM·PDM 기능으로 샘플링 과정을 단축 → 출시까지 걸리는 시간(time-to-market) 단축, 디자인 일관성 유지.
- 종합 BOM(Bill of Materials, 자재명세서)으로 제조 사양 관리.
- 크리티컬 패스 플래닝, 생산 단계별 품질 관리, 생산 자원 배치 최적화 → K3는 이를 통해 생산 물량을 최대 15%까지 늘릴 수 있다고 설명.
- 디자인팀·소싱팀·생산팀이 같은 데이터를 보며 협업 가능.
- **동작 방식**: 상품이 태어나기 전 단계(디자인, 샘플, BOM/텍판)의 데이터를 관리하다가 승인이 나면 그 데이터가 그대로 D365의 소싱·구매 모듈로 넘어가 실제 발주로 이어지는 흐름.

### 3.7 Product Data Management, PDM (제품 정보 관리)

상품 관련 모든 마스터 데이터(사양, 소재, BOM, 사이즈 정보 등)를 한 곳에서 정확하게 관리.

- PLM이 "과정 전체의 흐름"을 관리한다면, PDM은 그 안에서 쓰이는 "정확한 상품 데이터 자체"를 관리.
- 부서마다 데이터가 다르게 흩어지는 것을 방지하고, 하나의 신뢰할 수 있는 정보원(single source of truth) 확보.

## 4. 그 외 모듈 (참고)

K3 Fashion 공식 페이지에서 확인한 추가 기능 영역:

- **머천다이징 & 어소트먼트**: 색상-사이즈-핏 그리드 관리, 실시간 재고 데이터 기반 구성 결정, AI 기반 자동 상품 설명 생성.
- **재고 & 배분**: 재고 분할·배분 관리(품절/과잉재고 방지), 핵심 고객군 재고 보호 규칙, 다중 매장·지역 중앙 재고 관리.
- **물류 & 유통**: 프리팩(prepack) 생성·관리, 자동 주문 배분, 우선순위 기반 공급 일정 관리.
- **소싱 & 공급업체 관리**: 공급업체 성과·컴플라이언스 추적, CSR(사회적 책임) 인증 모니터링, 실시간 공급업체 데이터 기반 구매 결정.
- **품질 & 생산**: 생산 단계별 품질 관리, 크리티컬 패스 플래닝.
- **다중 통화 지원** 및 폭넓은 커스터마이징 옵션.

## 5. 기능 분류 요약

| 목적 | 관련 기능 |
|---|---|
| 상품을 빠르고 정확하게 등록 | Product Wizard, Matrix, PDM |
| 시즌·재고·사이즈 단위 계획·관리 | Season Management, Retail Inventory Management, Ratio Curves |
| 상품이 태어나서 팔리기까지 전체 프로세스 관리 | PLM |

## 6. 출처

- [K3 Fashion | ERP Software for Fashion Brands](https://k3fashionsolutions.com/solutions/enterprise/k3-fashion/)
- [K3|fashion ERP - ERP Pricing, Demo & Comparison Tool](https://www.erpfocus.com/k3-fashion-erp-software-profile.html)
- [Revolutionising the Fashion ERP Industry with Dynamics 365 and K3 - Fibre2Fashion](https://www.fibre2fashion.com/industry-article/10003/revolutionising-the-fashion-erp-industry-with-dynamics-365-and-k3)
- [Made-to-measure, ready-to-wear software by K3 (Infosys)](https://www.infosys.com/about/alliances/k3.html)
- [Ratio Curves - K3 Fashion (YouTube)](https://www.youtube.com/watch?v=qZD-t-SRplI)
- [Product Wizard - K3|fashion (YouTube)](https://www.youtube.com/watch?v=hCiQKfXL6vI)

---
*참고: 이 문서는 공개된 마케팅 자료·제품 소개 페이지·영상 제목을 바탕으로 정리한 내용이며, K3의 비공개 기술 문서(API/DB 스키마 수준)는 포함되어 있지 않습니다. 정확한 최신 정보나 견적은 K3 Fashion Solutions 공식 채널을 통해 확인하는 것을 권장합니다.*
