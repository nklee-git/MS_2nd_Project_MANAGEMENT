> 관련 문서: [[91-application-prep]] · [[93-year2-detail]]
> 원본: [[21-system-model]] 부록 B (2026-08-31 작성, 여기서 더 상세화)
> **용도**: 모두의창업 지원서 "성장 로드맵"(Q4-1) 섹션에 쓰기 위한 것. "지금 만든 것"이 아니라 "앞으로 이렇게 확장할 계획"으로만 서술.

## 포지셔닝
재고 리플레니시먼트 MVP(학교 2차 프로젝트, Year 1)를 발판으로, 아래 순서로 확장하는 3개년 로드맵.

| 연차 | 확장 내용 |
| --- | --- |
| Year 1 (지금, 2026) | AI 수요예측 + Dataverse 발주추천 + Teams 승인 워크플로우 — 재고 리플레니시먼트 코어 |
| Year 2 (2027) | **체형 수요 예측 심화** — 동적 사이즈 커브·반품 피드백 루프·신규 체형 세그먼트 시뮬레이션·체형 기반 상품기획 지원 툴. 상세: [[93-year2-detail]] |
| Year 3 (2028) | **ESG/디지털 제품 패스포트(DPP) 대응 확장** — 아래 상세 |

## 📅 규제 근거 — 왜 하필 Year 3(2028)인가 (2026-09-04 확인)
EU ESPR(Ecodesign for Sustainable Products Regulation) Working Plan 2025-2030 기준, **섬유·의류 전용 위임법안(Delegated Act)이 2027년 3~4분기 채택 예정**이고, 채택 후 통상 18개월 유예를 거쳐 **실질 의무화는 2027~2029년 사이**로 전망됨. 즉 Year 3(2028)는 임의로 잡은 숫자가 아니라 **실제 규제 시점과 겹치는 시점**이라는 게 이번에 확인됨 — "미리 준비해두는 로드맵"이라는 근거가 더 탄탄해짐.

예상 요구 데이터 항목(확정 전이지만 업계 컨센서스): 소재 구성(material composition), 생산공정, 환경지표(탄소 등), 화학물질 규제 준수, **공급망 추적성(최소 티어2까지)**, 내구성·재활용성. 적용 대상엔 의류뿐 아니라 가방·스카프 등 패션 액세서리, 홈텍스타일도 포함될 전망.

## 🔧 Year 3 세부 기능 (구체화, 2026-09-04)
학교 2차 프로젝트에서 이미 만드는 자산 위에 얹는 구조라는 걸 기능 단위로 쪼개면:

| 기능                 | Year 1 자산과의 연결점                                                                                                                                                                                                                                                                                                                                            |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ① 원단 인증서 자동 수집     | 이미 있는 공급업체 데이터(`31. Partner & Factory Master`)에 인증서 필드 추가 — OCR/구조화 파싱으로 소재 혼용률 자동 입력                                                                                                                                                                                                                                                                      |
| ② 소재 구성 데이터        | [[4-differentiation-ideas]] 논의 7(소재·컬러 데이터 SKU 피처화)에서 이미 설계해둔 `material_composition` 필드가 그대로 DPP의 "소재 구성" 요구사항과 일치 — Year 1에서 코어 완성 후 스트레치로 시도하려던 게 Year 3의 선행 작업이 됨                                                                                                                                                                                       |
| ③ 탄소발자국(LCA) 계산    | **직접 측정이 아니라 업계 표준 배출계수 참조** — 패션 업계 표준인 Higg MSI(Materials Sustainability Index, Cascale/구 Sustainable Apparel Coalition 운영, 연 2회 갱신)가 소재별 "1kg당 배출량"을 이미 계산해둔 참조표를 제공. `탄소발자국 = ②의 소재구성 × Higg MSI 배출계수 합산` — LCA 과학을 새로 만드는 게 아니라, **이 외부 참조표와 우리 SKU 데이터를 Databricks로 자동 조인하는 파이프라인**을 만드는 것. Year 1의 "체형·날씨 조건화 예측"과 똑같은 패턴(외부 데이터 + SKU 데이터 조인)을 재사용 |
| ④ 공급망 추적성(Tier 2)  | 지금은 1차 공급업체(원단 소싱)까지만 모델링 — Year 3엔 그 위 원사 공급업체(Tier 2)까지 확장                                                                                                                                                                                                                                                                                               |
| ⑤ QR 기반 소비자 조회 페이지 | Year 1에서 이미 만드는 ASP.NET Core MVC 대시보드 스킬을 그대로 재사용 — 내부용 대시보드 → 외부 소비자용 조회 페이지로 확장                                                                                                                                                                                                                                                                          |

**핵심 메시지**: 완전히 새로운 트랙이 아니라, **Year 1에서 이미 설계해둔 데이터 모델·기술 스택을 그대로 재사용**해서 Year 3 규제 대응까지 자연스럽게 확장한다는 것 — 지원서에서 "이미 실행 가능성이 검증된 확장 경로"로 어필 가능.

## 지원서에서 강조 포인트
- 정부 창업지원사업은 ESG/사회적가치 정렬을 긍정적으로 평가하는 경향 — 다만 모두의창업 공식 평가기준(bizinfo.go.kr·modoo.or.kr)에서 실제 배점 여부는 별도 확인 필요
- **"트렌드 편승"이 아니라 "규제 캘린더 기반 준비"**라는 톤으로 — 실제 EU 위임법안 채택 시점(2027)과 로드맵 Year 3(2028)가 겹친다는 근거 제시

## 출처
- [What Is the EU Digital Product Passport? ESPR Requirements — COSH!](https://cosh.eco/en/articles/eu-digital-product-passport-espr-explained-fashion-textiles)
- [ESPR Working Plan 2025–2030: Timeline & Delegated Acts — PassportCraft](https://passportcraft.com/insights/espr-timeline-what-brands-need-to-know)
- [Digital Product Passport for Textiles: What Fashion Brands Need to Know — Carbonfact](https://www.carbonfact.com/blog/policy/digital-product-passport-fashion)
- [Digital Product Passport — European Commission](https://single-market-economy.ec.europa.eu/single-market/digital-product-passport_en)
- [Higg MSI: Materials Sustainability Index — Worldly](https://worldly.io/solutions/materials-lifecycle-assessment-data/)
- [Higg MSI Methodology (PDF) — Cascale](https://marketing-cdn.production.worldly.io/guides/reslib/Higg%20MSI%20Methodology%20JUNE%202024.pdf)
