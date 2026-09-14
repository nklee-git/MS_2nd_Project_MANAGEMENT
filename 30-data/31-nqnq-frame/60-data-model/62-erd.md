> 관련 문서: [[61-entity-dictionary]]
> Obsidian에서 이 코드블록은 자동으로 다이어그램으로 렌더링됩니다 (Mermaid 코어 플러그인 필요, 기본 활성화됨).
> **2026-09-14**: 발표/비개발자 공유용 한글 버전 ERD가 별도로 있음(Team 저장소 로컬, 아직 미커밋) — [[65-model-changelog]] "한글 테이블·컬럼명 CSV 사본 + ERD 다이어그램 신규" 참고. 아래는 여전히 코드/DB 작업용 영문 SSOT.

## 핵심 트랜잭션 ERD (1차 모델링)

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
  STORE ||--o{ INVENTORY : stocks
  STORE ||--o{ INVENTORY_LEDGER : logs

  CATEGORY {
    string category_code PK
    string name
  }
  PRODUCT {
    string product_id PK
    string category_code FK
    string style_name
    string body_tone_code
    string season
    string status
    string line_type
    string popularity_tier
    date launch_date
  }
  SKU {
    string sku_code PK
    string product_id FK
    string size
    string color_code
    int price
    int cost
  }
  FACTORY {
    string factory_id PK
    string name
    int moq
    int lead_time_days
    string payment_terms
  }
  PURCHASE_ORDER {
    string po_id PK
    string factory_id FK
    date order_date
    date expected_arrival_date
    string status
  }
  PO_ITEM {
    int id PK
    string po_id FK
    string sku_code FK
    int qty
    int unit_cost
  }
  INVENTORY {
    string sku_code PK
    string location_id PK
    int available_qty
    int reserved_qty
    int defective_qty
    int pending_return_qty
    int safety_stock
    int reorder_point
    datetime last_updated
  }
  INVENTORY_LEDGER {
    string ledger_id PK
    string sku_code FK
    string location_id
    string movement_type
    int qty_change
    string reference_id
    datetime movement_date
  }
  CHANNEL {
    string channel_id PK
    string name
    float commission_rate
    string settlement_cycle
  }
  CUSTOMER {
    string customer_id PK
    string persona_segment
    string signup_channel
    date signup_date
  }
  ORDERS {
    string order_id PK
    string customer_id FK
    string channel_id FK
    string store_id FK
    datetime order_date
    string status
    int total_amount
  }
  ORDER_ITEM {
    int id PK
    string order_id FK
    string sku_code FK
    int qty
    int unit_price
  }
  RETURN_REQUEST {
    string return_id PK
    string order_id FK
    string sku_code FK
    string reason_code
    string status
    date request_date
    string resolution
  }
  STORE {
    string store_id PK
    string type
    string location
    date open_date
    date close_date
  }
```

## 📝 변경 이력
- v1.0: 최초 13개 엔터티 설계
- v1.1: `INVENTORY_LEDGER` 추가 — 재고 스냅샷만으로는 이동 이력 추적이 안 되는 문제 보완 (트러블슈팅·감사 대응 목적)
- v1.2: `RETURN_REQUEST`에 `sku_code` FK 추가 — 가상데이터 생성 중 발견: order_id만으로는 다중 아이템 주문에서 "어떤 SKU가 반품됐는지" 구분 불가능했던 문제 보완
- v1.3: `INVENTORY.sku_code`의 키 타입을 `PK_FK`(잘못된 문법) → `PK`로 수정 — Mermaid ERD 문법에는 복합 키 타입 표기가 없어 파싱 에러 발생, mermaid.parse()로 직접 검증 후 수정
- v1.4: `PRODUCT`에 `line_type`(BASIC/TREND) 필드 추가 — 트렌드 캡슐 라인 도입([[21-core-categories]])에 따라 베이직/트렌드 라인 구분 필요
- v1.5: `PRODUCT`에 `popularity_tier`(HERO/STEADY/NICHE) 필드 추가 — SKU 수 부족 문제 해결 위해 디자인 라인업 확장하며 롱테일 판매 가중치 도입
- v1.6 (2026-09-11): 엔터티 구조 변경 없음 — [[61-entity-dictionary]]에 엔터티별 데이터 품질 체크리스트 추가(팀원 제안 데이터 딕셔너리 템플릿 참고, 데이터 생성 일관성 확보 목적)
- v1.7 (2026-09-11, generate_v5.py): `INVENTORY`에 `location_id` 추가해 `(sku_code, location_id)` 복합키로 변경(HUB 중앙창고 + 매장별 재고를 분리 추적), `INVENTORY_LEDGER`에도 `location_id` 추가하고 `movement_type='이관'`을 HUB↔매장 이동 기록에 실사용 — 매장 오픈 시 사전비축/상설쇼룸 정기보충/팝업 폐점 시 잔여재고 반납을 전부 `이관` 레저로 남김. `SKU ||--|| INVENTORY`(1:1)도 `SKU ||--o{ INVENTORY`(1:다)로 카디널리티 수정. 계기: 기존 단일 전역재고 모델에서 같은 날 동시에 열린 매장이 여러 곳이면 코드가 그중 하나만 선택하고 나머지는 판매실적이 영원히 0이 되는 버그 발견(매장별 재고 분리로 자연 해소).
- v1.8 (2026-09-14): 한글 발표용 ERD([[65-model-changelog]] 참고) 작업 중 멘토 코멘트로 "매장→재고 관계가 이어져 보이지 않는다"는 지적이 나와 `models.py`를 재대조한 결과, **관계는 원래부터 정상**(`Inventory.location_id`/`InventoryLedger.location_id` 모두 `ForeignKey("store.store_id")`로 이미 선언돼 있었음)이었으나 **이 다이어그램에 `STORE ||--o{ INVENTORY`·`STORE ||--o{ INVENTORY_LEDGER` 관계선 자체가 누락**돼 있던 게 원인으로 확인돼 추가. 같은 대조 중 `PO_ITEM`·`ORDER_ITEM`도 `models.py`엔 surrogate `int id PK`가 있는데 이 ERD 필드 목록엔 빠져있어 같이 추가(코드와 다이어그램 드리프트 보정, 스키마 자체 변경 아님).

세부 필드 정의는 [[61-entity-dictionary]] 참고.
