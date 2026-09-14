> 관련 문서: [[62-erd]] · [[22-sku-code-system]] · [[27-size-expansion-plan]] · [[32-inventory-policy]] · [[33-returns-process]] · [[42-channel-settlement]] · [[48-offline-store-plan]]
> **2026-09-08 갱신**: 2026.09 SKU 체계 개편(체형태그·사이즈 확장) 반영 — PRODUCT.body_tone_code 의미 변경, SKU.sku_code 포맷 카테고리별 분화, 실제 카탈로그 값(카테고리·사이즈·컬러) 표 추가. **원본 데이터(`nqnq.db`) 재생성은 아직 안 함** — 이 문서는 `generate_v4.py`의 현재 코드 기준으로 작성됐고, 카탈로그(상품·SKU)만 미리 뽑아본 샘플이 있음(나경에게 요청).

## 📐 설계 원칙
- **PRODUCT(스타일)와 SKU(판매 최소단위)를 분리** — [[22-sku-code-system]]의 "체형전용 스타일 × 사이즈 × 컬러" 구조를 그대로 반영
- **INVENTORY(현재 스냅샷)와 INVENTORY_LEDGER(이동 이력)를 분리** — 현재 재고 수량 조회는 빠르게, 이동 히스토리는 별도 로그로 추적 (감사·트러블슈팅 대응)
- **CHANNEL(유통 채널)과 STORE(물리적 공간)를 분리** — 지그재그처럼 수수료가 걸리는 유통 채널과, 팝업/쇼룸처럼 물리적 공간 개념은 성격이 다름
- 이번 1차 모델링은 **판매 트랜잭션 핵심 흐름**에 집중. 운영/관리 성격 엔터티(STAFF, TASK, CAMPAIGN 등)는 하단 "다음 확장 대상"에 백로그로 정리

## 🏷️ 네이밍 컨벤션 (신규 — 토스플레이스 PANDA 사례 참고, 2026-08-26 추가)
지금까지 테이블/컬럼명은 암묵적으로 일관되게 지어왔지만(예: `sku_code`, `order_id`), 팀 합류 예정 인원이 늘어나는 시점에 대비해 규칙을 명문화. 토스플레이스 [PANDA(데이터봇)](https://toss.tech/article/da-assistant-panda) 사례의 "테이블/컬럼명만 보고 역할을 알 수 있게" SSOT 컨벤션 원칙을 참고.

| 대상 | 규칙 | 예시 |
| --- | --- | --- |
| 테이블(엔터티)명 | 대문자 단수 명사 | `PRODUCT`, `INVENTORY_LEDGER` |
| PK 컬럼 | `{entity_snake}_id` 또는 도메인 코드(`sku_code`, `po_id`) | `product_id`, `sku_code` |
| FK 컬럼 | 참조 대상 PK와 동일한 이름 유지(별칭 금지) | `SKU.product_id` → `PRODUCT.product_id` |
| 상태/분류 컬럼 | `status`, `{domain}_tier`, `{domain}_code` 형태로 통일 | `popularity_tier`, `body_tone_code` |
| 이력/로그 테이블 | `{원본엔터티}_LEDGER` 또는 `{원본엔터티}_LOG` | `INVENTORY_LEDGER`, (백로그) `ALERT_LOG` |

> 이 컨벤션은 신규 엔터티(백로그의 `ALERT_LOG`, `TASK`, `CAMPAIGN` 등) 설계 시부터 적용.

## 🗂️ 엔터티별 데이터 딕셔너리

### CATEGORY (카테고리)
| 필드 | 한글명 | 타입 | 제약 | 설명 |
| --- | --- | --- | --- | --- |
| category_code | 카테고리코드 | string | PK | TOP / PNT / CLR / OUT / ACC / DRS ([[22-sku-code-system]]) |
| name | 카테고리명 | string | | 카테고리명(상의/팬츠/컬러베이직/아우터/액세서리/원피스) |

### PRODUCT (상품 · 스타일 마스터)
| 필드 | 한글명 | 타입 | 제약 | 설명 |
| --- | --- | --- | --- | --- |
| product_id | 상품아이디 | string | PK | 스타일 고유 ID — 카테고리별 포맷이 다름(아래 "SKU 코드 포맷" 참고) |
| category_code | 카테고리코드 | string | FK → CATEGORY | |
| style_name | 스타일명 | string | | 예: "스퀘어라인 기본티" |
| body_tone_code | 바디톤코드 | string | | **2026.09 개편으로 카테고리마다 의미가 다름**(아래 참고) |
| season | 시즌 | string | | Y1SS, Y1FW... ([[45-season-calendar]]) |
| status | 판매상태 | string | | 기획중/샘플링중/생산중/판매중/품절/단종 ([[23-product-lifecycle]]) |
| line_type | 라인유형 | string | | BASIC(베이직, 상시판매) / TREND(트렌드캡슐, 한정판매) — [[22-sku-code-system]] 참고 |
| popularity_tier | 인기도등급 | string | | HERO(3.0x)/STEADY(1.0x)/NICHE(0.3x) — 롱테일 판매 가중치 ([[21-core-categories]] 참고) |
| launch_date | 출시일자 | date | | 판매 오픈일 |

> **body_tone_code의 카테고리별 의미 (2026.09 개편, [[27-size-expansion-plan]])**
> | 카테고리 | 값 | 의미 |
> | --- | --- | --- |
> | TOP / OUT / DRS | `"STR,WAV,NAT"` 형태의 콤마join 문자열 | **실제 상품을 구분 짓는 값이 아니라 스타일링 추천 태그** — 체형별로 다른 물리적 상품을 만드는 게 아니라, 하나의 상품에 "이 체형에 잘 어울림" 태그만 붙임 |
> | PNT | `"-"` | 체형 개념 없음(태그도 안 씀) — 기존 5LT/PLT 바디코드는 디자인명과 중복 곱해지던 버그였어서 제거됨 |
> | CLR | `WRM` / `COOL` / `MUT` 단일값 | **실제 상품 차원(진짜 다른 색으로 염색)** — 유일하게 body_tone_code가 SKU 배수 축으로 남아있는 카테고리 |
> | ACC | 아이템 종류 코드(BAG/BLT/SCF/CAP/PCH) | 카테고리 자체가 아이템 종류 축이라 예외 |

### SKU (재고관리단위)
| 필드         | 한글명 | 타입     | 제약           | 설명                                                  |
| ---------- | --- | ------ | ------------ | --------------------------------------------------- |
| sku_code   | 재고관리단위코드 | string | PK           | 카테고리별로 포맷이 다름 — 아래 표 참고                             |
| product_id | 상품아이디 | string | FK → PRODUCT |                                                     |
| size       | 사이즈 | string |              | 카테고리별로 사이즈 depth가 다름 — 아래 "실제 카탈로그 값" 참고            |
| color_code | 색상코드 | string |              | BLK/WHT/CRM 등 — 카테고리별 코어/포인트 컬러는 아래 참고              |
| price      | 판매가격 | int    |              | 정가 (원, [[43-revenue-cost]] 원가구조 기반 산출) |
| cost       | 원가 | int    |              | 원가 = 정가 × 0.48(COST_RATIO, `generate_v4.py`)        |

> **sku_code / product_id 포맷 (카테고리별, 2026.09 개편)**
> | 카테고리 | product_id 예시 | sku_code 예시 |
> | --- | --- | --- |
> | TOP / PNT / OUT / DRS | `NQ-TOP-001` (체형코드 없음) | `NQ-TOP-001-M-BLK` |
> | CLR | `NQ-CLR-WRM-001` (톤코드 유지) | `NQ-CLR-WRM-001-M-CRM` |
> | ACC | `NQ-ACC-BAG-001` (아이템종류 유지) | `NQ-ACC-BAG-001-FREE-BLK` |
> | 트렌드캡슐 | `TRD-{카테고리}-{캡슐번호}-{체형/톤}-{일련번호}` | `TRD-OUT-02-STR-001-M-BRN` — 트렌드캡슐은 이번 개편 대상 아니라 기존 포맷 그대로 |

### 실제 카탈로그 값 (2026.09 개편 기준, `generate_v4.py` CATEGORIES 딕셔너리)
| 카테고리 | 디자인 수 | 사이즈 | 코어 컬러 | 포인트 컬러(HERO 디자인 한정) |
| --- | --- | --- | --- | --- |
| TOP | 5 | XS/S/M/L/XL/2XL/3XL/4XL (8단계) | BLK·WHT·GRY·NVY | ORC(오키드)·SKB(하늘색)·LYL(연노랑) |
| PNT | 4 | XS/S/M/L/XL/2XL/3XL/4XL (8단계) | BLK·GRY·BEG | KHK(카키)·NVY |
| OUT | 3 | S/M/L (3단계, 변경 없음) | BLK·BEG·GRY·NVY | (이번 개편 대상 아님) |
| DRS | 2 | S/M/L (3단계, 변경 없음) | BLK·IVR | (이번 개편 대상 아님) |
| CLR | 2 (×톤 3종 = 상품 6개) | S/M/L (3단계, 변경 없음) | CRM(웜)·ASH(뮤트)·IVR(쿨) | (톤 자체가 색상 축이라 별도 포인트컬러 없음) |
| ACC | 5종(가방/벨트/스카프/캡/파우치) | FREE | BLK·BEG·WHT·BRN | (사이즈 축 없음) |

> XS~4XL 8단계 사이즈의 실제 배분 비율은 실측 데이터가 아직 없는 잠정 가정치(4/14/24/24/16/10/5/3%) — [[27-size-expansion-plan]] 2-4절 참고.

### 카탈로그 규모 (2026.09 개편 후, 실행 전 코드 기준 계산값)
| 구분            | 값                                                                        |
| ------------- | ------------------------------------------------------------------------ |
| 베이직 상품(스타일) 수 | 20 (TOP 5 + PNT 4 + OUT 3 + DRS 2 + CLR 6 + ACC 5 — CLR은 톤 3종이라 상품 수는 6) |
| 베이직 SKU 수     | 418                                                                      |
| 트렌드캡슐 상품 수    | 21                                                                       |
| 트렌드캡슐 SKU 수   | 102                                                                      |
| **전체 상품 수**   | **41**                                                                   |
| **전체 SKU 수**  | **520**                                                                  |

> 개편 전(428 베이직 SKU)과 거의 같은 총량 — SKU를 늘린 게 아니라 체형배수를 걷어내고 그만큼을 TOP/PNT 사이즈·컬러 뎁스에 재배분한 결과. 상세 계산은 [[27-size-expansion-plan]] 3절.

### FACTORY (공장)
| 필드 | 한글명 | 타입 | 제약 | 설명 |
| --- | --- | --- | --- | --- |
| factory_id | 공장아이디 | string | PK | |
| name | 공장명 | string | | 예: 성진어패럴 |
| moq | 최소발주수량 | int | | 컬러당 최소발주수량 ([[31-factory-master]]) |
| lead_time_days | 리드타임일수 | int | | 생산 리드타임(45일) |
| payment_terms | 결제조건 | string | | 선급30%/잔금70% |

### PURCHASE_ORDER (발주)
| 필드                    | 한글명 | 타입     | 제약           | 설명                                                          |
| --------------------- | --- | ------ | ------------ | ----------------------------------------------------------- |
| po_id                 | 발주아이디 | string | PK           |                                                             |
| factory_id            | 공장아이디 | string | FK → FACTORY |                                                             |
| order_date            | 발주일자 | date   |              |                                                             |
| expected_arrival_date | 입고예정일자 | date   |              | order_date + 52일 ([[31-factory-master]] 전체 리드타임) |
| status                | 발주상태 | string |              | 발주/생산중/검수중/입고완료                                             |
|                       |     |        |              |                                                             |

### PO_ITEM (발주품목)
| 필드 | 한글명 | 타입 | 제약 | 설명 |
| --- | --- | --- | --- | --- |
| po_id | 발주아이디 | string | PK, FK → PURCHASE_ORDER | **2026-09-14 확인**: 현재 데이터는 1발주=1SKU라 po_id가 사실상 PK(DB 유니크 제약은 미설정, 품질 체크리스트 참고) |
| sku_code | 재고관리단위코드 | string | FK → SKU | |
| qty | 수량 | int | | 발주 수량 (동적 재고정책 기반 — INVENTORY 섹션의 재고정책 공식 참고) |
| unit_cost | 매입단가 | int | | |

### INVENTORY (재고 · 현재 스냅샷) — 2026-09-11 v5: (sku_code, location_id) 복합키로 변경
| 필드 | 한글명 | 타입 | 제약 | 설명 |
| --- | --- | --- | --- | --- |
| sku_code | 재고관리단위코드 | string | PK(복합), FK → SKU | |
| location_id | 위치아이디 | string | PK(복합), FK → STORE.store_id | **2026-09-12 정규화**: HUB도 STORE에 실제 행으로 추가되어 정식 FK로 선언됨(이전엔 가상 위치라 FK 미적용) |
| available_qty | 가용수량 | int | | 가용재고(해당 location 기준) |
| reserved_qty | 예약수량 | int | | 예약재고(현재 생성 로직에서 항상 0, 미사용) |
| defective_qty | 불량수량 | int | | 불량재고(현재 생성 로직에서 항상 0, 미사용) |
| pending_return_qty | 반품대기수량 | int | | 반품대기재고 — v5에선 HUB 행에만 반영(매장 반품은 전부 HUB 귀속으로 단순화) ([[33-returns-process]]) |
| safety_stock | 안전재고 | int | | **동적 계산**(고정값 아님, 아래 참고) — 모든 location 행에 SKU 기준 동일 공식값 저장(단순화) |
| reorder_point | 재발주시점 | int | | **동적 계산**(고정값 아님, 아래 참고) — 팩토리 재발주 트리거는 **HUB 행만** 사용, 매장 재고 부족은 HUB→매장 보충(이관)으로 해결 |
| last_updated | 최종수정일시 | datetime | | |

> **재고정책 공식 (2026.08 개정, `generate_v4.py`)** — SKU당 판매속도(velocity, 분기별 매출목표 역산) × 인기도 티어 비율(tier_ratio) × 리드타임(52일) × 버퍼 계수로 매일 재계산:
> - `reorder_point = velocity × tier_ratio × 52일 × 1.3`(REORDER_BUFFER)
> - `par_level(파레벨) = velocity × tier_ratio × 52일 × 3.0`(PAR_BUFFER)
> - `safety_stock = reorder_point × 0.5`(SAFETY_STOCK_RATIO)
> - 트렌드캡슐 초도물량은 베이직(3.0배)보다 훨씬 적은 1.0배 버퍼 — "소량 정예" 운영 원칙
> 고정 수치(SKU당 200장 등)로는 매출 목표 성장 구간에서 병목이 생겨서, 실판매 속도 기반으로 바뀐 것 — [[32-inventory-policy]] 참고.

### INVENTORY_LEDGER (재고원장 · 이동 이력)
| 필드 | 한글명 | 타입 | 제약 | 설명 |
| --- | --- | --- | --- | --- |
| ledger_id | 원장아이디 | string | PK | |
| sku_code | 재고관리단위코드 | string | FK → SKU | |
| location_id | 위치아이디 | string | FK → STORE.store_id | **2026-09-12 정규화**: 어느 위치의 재고가 움직였는지(`HUB` 또는 매장) — STORE FK로 정식 선언 |
| movement_type | 이동유형 | string | | 입고(팩토리→HUB)/판매출고/반품입고/불량처리/이관(v5부터 실사용 — HUB↔매장 이동) |
| qty_change | 변동수량 | int | | +/- 수량 |
| reference_id | 참조아이디 | string | | 관련 order_id, po_id, 또는 v5 이관 이벤트 ID(`PREP-*`=사전비축, `TOPUP-*`=상설쇼룸 보충, `CLOSE-*`=팝업 폐점 반납) |
| movement_date | 이동일자 | datetime | | |

### CHANNEL (채널)
| 필드 | 한글명 | 타입 | 제약 | 설명 |
| --- | --- | --- | --- | --- |
| channel_id | 채널아이디 | string | PK | |
| name | 채널명 | string | | 아래 코드 집합 참고 |
| commission_rate | 수수료율 | float | | 채널별 상이 — 아래 코드 집합 참고 |
| settlement_cycle | 정산주기 | string | | 채널별 상이 — 아래 코드 집합 참고 |

> **코드 집합 — `channel_id` (2026-09-11 코드 대조 후 갱신)**
> | channel_id | name | commission_rate | settlement_cycle | 비고 |
> | --- | --- | --- | --- | --- |
> | `ZIGZAG` | 지그재그(직진배송) | 0.15 | 월 2회 | `generate_v4.py` 실제 생성 |
> | `OFFLINE` | 오프라인 쇼룸/팝업 | 0.0 | - | `generate_v4.py` 실제 생성, 물리 매장은 STORE 참고 |
> | `WHOLESALE` | 홀세일/입점 | 0.0 | 월 1회 | `add_wholesale.py`가 별도 삽입(파일럿 8개 파트너) — 2026-09-11까지는 `channel` 테이블에 이 행 자체가 없어 FK 위반 상태였음(FK 체크를 꺼서 삽입), 두 스크립트 모두 이번에 수정 |
>
> [[42-channel-settlement]]가 개념상 설명하는 "지그재그 Z결제 15% vs 자사몰 경유 0%" 구분은 **코드에는 없음** — `channel.commission_rate`는 채널당 고정값 하나뿐이고, "자사몰"이라는 별도 channel_id/데이터도 존재하지 않음. 실제로 채널을 늘리려면 이 표에 행을 추가하고 위 두 생성 스크립트도 같이 고쳐야 함(품질 체크 참고).

### CUSTOMER (고객)
| 필드 | 한글명 | 타입 | 제약 | 설명 |
| --- | --- | --- | --- | --- |
| customer_id | 고객아이디 | string | PK | |
| persona_segment | 고객유형 | string | | Primary(18-24)/Secondary(25-28), [[2-target-persona]] |
| signup_channel | 가입채널 | string | | |
| signup_date | 가입일자 | date | | |

### ORDERS (주문)
| 필드 | 한글명 | 타입 | 제약 | 설명 |
| --- | --- | --- | --- | --- |
| order_id | 주문아이디 | string | PK | |
| customer_id | 고객아이디 | string | FK → CUSTOMER | |
| channel_id | 채널아이디 | string | FK → CHANNEL | |
| store_id | 매장아이디 | string | FK → STORE, nullable | 오프라인 매장 경유 주문인 경우만 — HUB는 오지 않으므로 '매장아이디'로 명명(INVENTORY 계열의 '위치아이디'와 역할명이 다름) |
| order_date | 주문일시 | datetime | | |
| status | 주문상태 | string | | 주문완료/배송중/배송완료/구매확정/취소 |
| total_amount | 총주문금액 | int | | |

### ORDER_ITEM (주문품목)
| 필드 | 한글명 | 타입 | 제약 | 설명 |
| --- | --- | --- | --- | --- |
| order_id | 주문아이디 | string | PK(복합), FK → ORDERS | **2026-09-14 확인**: order_id 단독은 주문당 최대 15건까지 중복(PK 불가) — (order_id, sku_code) 조합은 실측 전량 유니크 |
| sku_code | 재고관리단위코드 | string | PK(복합), FK → SKU | |
| qty | 수량 | int | | |
| unit_price | 판매단가 | int | | |

### RETURN_REQUEST (반품요청)
| 필드 | 한글명 | 타입 | 제약 | 설명 |
| --- | --- | --- | --- | --- |
| return_id | 반품아이디 | string | PK | |
| order_id | 주문아이디 | string | FK → ORDERS | |
| sku_code | 재고관리단위코드 | string | FK → SKU | 주문 내 반품 대상 SKU (라인아이템 단위 추적용, v1.2에서 추가) |
| reason_code | 사유코드 | string | | R01~R05 ([[33-returns-process]]) |
| status | 처리상태 | string | | 접수/검수중/완료 |
| request_date | 요청일자 | date | | |
| resolution | 처리결과 | string | | 환불/교환 |

### STORE (매장)
| 필드 | 한글명 | 타입 | 제약 | 설명 |
| --- | --- | --- | --- | --- |
| store_id | 매장아이디 | string | PK | **2026-09-12 정규화**: HUB(중앙창고)도 실제 행으로 추가되어 5개 행(팝업2+상설쇼룸2+HUB1) — INVENTORY/INVENTORY_LEDGER는 이 컬럼을 '위치아이디'로 참조(ERD 표시명 통일), ORDERS는 오프라인 매장 전용 의미로 '매장아이디' 그대로 사용 |
| type | 매장유형 | string | | 팝업/상설쇼룸 ([[48-offline-store-plan]]) |
| location | 위치 | string | | |
| open_date | 개점일자 | date | | |
| close_date | 폐점일자 | date | nullable | 팝업의 경우만 |

## 🧪 데이터 품질 체크리스트 (2026-09-11 추가 — 데이터 생성 일관성용)
> 팀원이 제안한 데이터 딕셔너리 템플릿(Staging/Dim/Fact 테이블마다 품질 체크 항목을 명시하는 방식, `stg_erp_products`/`dim_product` 등)의 취지를 이 프로젝트의 실제 엔터티에 맞게 반영. `generate_v4.py`로 데이터를 새로 만들거나 스키마를 바꿀 때마다 아래 항목을 확인하면, 이번 데이터모델 검토에서 드러난 것 같은 문서-코드 드리프트(예: `body_tone_code`·`safety_stock`/`reorder_point`가 `models.py`엔 있는데 다른 ERD 초안엔 빠지는 문제)를 미리 잡을 수 있음.

- **CATEGORY**: `category_code` unique/not null · `name`이 6개 카테고리(TOP/PNT/CLR/OUT/ACC/DRS)와 1:1 매핑되는지
- **PRODUCT**: `product_id` unique/not null · `category_code` → CATEGORY 참조 무결성 · `body_tone_code`가 카테고리별 규칙(TOP/OUT/DRS=콤마join 태그, PNT/ACC="-", CLR=WRM/COOL/MUT 단일값) 준수 · `popularity_tier` ∈ {HERO,STEADY,NICHE} · `line_type` ∈ {BASIC,TREND}
- **SKU**: `sku_code` unique/not null · `product_id` → PRODUCT 참조 무결성 · `sku_code` 포맷이 카테고리별 규칙(위 "sku_code 포맷" 표) 준수 · `cost` ≈ `price` × 0.48(COST_RATIO)
- **FACTORY**: `factory_id` unique/not null
- **PURCHASE_ORDER**: `po_id` unique/not null · `factory_id` → FACTORY 참조 무결성 · `expected_arrival_date` = `order_date` + 52일
- **PO_ITEM**: `po_id` unique/not null(사실상 PK, **2026-09-14 확인**: 현재 데이터 1발주=1SKU) — **DB 레벨 유니크 제약은 여전히 미설정**이라 향후 1발주-다SKU로 바뀌면 깨질 수 있음, 추가 검토 대상 · `po_id`/`sku_code` 참조 무결성
- **INVENTORY**: (`sku_code`,`location_id`) unique/not null(복합PK) · `location_id` ∈ {HUB, STORE.store_id} · `available_qty`/`reserved_qty`/`defective_qty`/`pending_return_qty` ≥ 0 · HUB 행이 SKU당 정확히 1개 존재하는지(리오더포인트 알림의 전제조건)
- **INVENTORY_LEDGER**: `ledger_id` unique/not null · `sku_code` 참조 무결성 · `location_id` ∈ {HUB, STORE.store_id} · `movement_type` ∈ {입고,판매출고,반품입고,불량처리,이관} · 이관은 항상 같은 reference_id로 두 행(from -location, to +location)이 쌍으로 존재하는지
- **CHANNEL**: `channel_id` unique/not null · `channel_id` ∈ {ZIGZAG,OFFLINE,WHOLESALE}(위 코드 집합) · `ORDERS.channel_id`가 전부 이 3개 안에서만 나오는지(과거엔 WHOLESALE이 여기 없어 FK 위반이었음, 2026-09-11 수정)
- **CUSTOMER**: `customer_id` unique/not null
- **ORDERS**: `order_id` unique/not null · `customer_id`/`channel_id` 참조 무결성 · `store_id`는 오프라인 경유 주문만 not null · `status` ∈ {주문완료,배송중,배송완료,구매확정,취소}
- **ORDER_ITEM**: (`order_id`,`sku_code`) unique/not null(사실상 복합PK, **2026-09-14 확인**: 실측 전량 유니크) — DB 레벨 유니크 제약은 미설정, `order_id` 단독은 주문당 최대 15건 중복되어 PK 불가 · `order_id`/`sku_code` 참조 무결성
- **RETURN_REQUEST**: `return_id` unique/not null · `order_id`/`sku_code` 참조 무결성 · `reason_code` ∈ {R01~R05}
- **STORE**: `store_id` unique/not null · `close_date`는 팝업(`type`)만 not null 허용

## 🔜 다음 확장 대상 (2차 모델링 백로그)
- `STAFF` / `USER` — [[53-virtual-team-profiles]] 기반 내부 사용자
- `TASK` / `APPROVAL` — [[54-approval-workflow]] 기반 업무/승인 흐름
- `CAMPAIGN` / `PROMOTION` — [[47-marketing-plan]] 기반 마케팅 캠페인 성과 추적 → [[44-kpi-definitions]]의 "마케팅 ROAS" 미수집 상태 해소용
- `ALERT_LOG` — [[24-alert-rules]] 기반 알림 발생 이력
- `SITE_VISIT` / `CART_EVENT` (신규, 2026-09-09 추가) — 방문 세션·장바구니 이벤트 로그. [[44-kpi-definitions]]의 "CVR(전환율)" 미수집 상태 해소용. 대시보드 홈 탭 핵심 판매 KPI 위젯에서 지금은 목표치(2~3%)만 표시 중.

이 5개는 "판매 트랜잭션"이 아니라 "운영 관리" 성격이라 별도 ERD로 분리하는 것을 권장.

> **재구매율은 스키마 문제가 아님** — CUSTOMER·ORDER FK로 고객별 주문 건수를 이미 셀 수 있는 구조라, 신규 엔터티가 필요한 게 아니라 **표본이 아닌 전체 Order 데이터(2026-09-11 v5 재생성판 기준 ~1,243,079건)를 조회**하면 바로 계산 가능. 지금 대시보드가 "가정치(30%)"로 남아있는 건 order_items_sample.csv가 500건짜리 미리보기라서 — 카탈로그 재생성 시 고객별 재구매 집계 쿼리를 csv_preview에 추가하면 해소됨.
