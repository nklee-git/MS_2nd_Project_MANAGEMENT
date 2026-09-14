> 관련 문서: [[61-entity-dictionary]] · [[62-erd]]
> 대상 파일: `NQNQ_데이터_모델.html` / `nqnq_data_model.html` (바탕화면\짬통 폴더, 완전 동일 중복본 2개) — [[61-entity-dictionary]]·[[62-erd]](구 71·72번 문서)를 한 페이지로 묶어 시각화한 정적 HTML 요약본.

## 배경

OneDrive에서 받은 zip(`OneDrive_2026-09-11 (1).zip`) 안의 `데이터 모델 정리 .html`을 로컬 사본과 비교한 결과, 둘 다 **2026-09-08~10 스냅샷(v1.5)**으로 동일했음. 반면 원본 소스인 [[61-entity-dictionary]] · [[62-erd]]은 이미 **2026-09-11에 v1.7까지 갱신**되어 있어서, HTML 요약본만 그 사이 변경을 못 따라간 상태였음(문서-코드가 아니라 "문서-문서" 간 드리프트).

## HTML 요약본에 반영한 변경 (v1.5 → v1.7)

| 위치 | 이전 | 이후 |
| --- | --- | --- |
| masthead | 최종 갱신 2026-09-08 · 버전 v1.5 | 최종 갱신 2026-09-11 · 버전 v1.7 |
| ERD (`INVENTORY`) | `sku_code` 단일 PK | `(sku_code, location_id)` 복합 PK — `location_id` 필드 추가 |
| ERD (`INVENTORY_LEDGER`) | `location_id` 필드 없음 | `location_id` 필드 추가 |
| ERD 관계선 | `SKU \|\|--\|\| INVENTORY`(1:1) | `SKU \|\|--o{ INVENTORY`(1:다) |
| 핵심 규칙 섹션 | ①~③ (body_tone_code, SKU 코드 포맷, 동적 재고정책) | ④ `INVENTORY`의 SKU×location 분리(HUB/매장, 어느 채널이 어느 location을 차감하는지) · ⑤ `WHOLESALE` 채널이 한동안 `CHANNEL` 테이블에 없어 FK가 깨져있던 이력 + 현재 3개 채널 코드 집합 추가 |
| FIG.3 캡션 | `generate_v4.py, 2026.08 개정` | `2026.08 개정 로직, generate_v5.py에서도 유지` |
| 변경 이력 섹션 | v1.5까지만 | v1.6(품질 체크리스트 추가), v1.7(INVENTORY location_id 분리) 항목 추가 |
| 백로그 콜아웃 | 전체 Order 1,098,763건(구 수치) | 1,243,079건(v5 재생성판) + `full_export/order_item.csv` 전체 추출본 존재 언급 |

## 데이터가 실제로 어떻게 바뀌었는지 (요약)

- **재고 구조**: SKU당 재고 1행 → SKU × location(HUB 또는 STORE-01~04)별로 재고 분리. HUB는 온라인(ZIGZAG)·홀세일(WHOLESALE) 판매를 차감하고, 매장은 오프라인(OFFLINE) 판매만 차감. 매장 로컬재고가 7일치 이하로 떨어지면 HUB에서 14일치를 보충(이관).
- **재고 이동 이력**: `INVENTORY_LEDGER`에 `location_id`가 생기면서 `movement_type="이관"`이 처음으로 실사용됨 — 매장 오픈 시 사전비축, 상설쇼룸 정기보충, 팝업 폐점 시 잔여재고 HUB 반납을 전부 이 레저로 추적.
- **버그 수정 계기**: 개편 전엔 같은 날 여러 매장이 동시에 열려있으면 코드가 그중 하나만 선택해 나머지 매장 판매실적이 0으로 남는 문제가 있었음 — 매장별 재고 분리로 자연히 해소됨.
- **채널**: `WHOLESALE`이 `CHANNEL` 테이블에 행 자체가 없는 채로 주문만 꽂히던 FK 위반 상태가 수정되어, `ZIGZAG`/`OFFLINE`/`WHOLESALE` 3개 채널이 정상적으로 참조 무결성을 갖춤.

## 반영 안 한 것

- zip 안의 원본 `데이터 모델 정리 .html`(다운로드 폴더 스냅샷)은 수정하지 않음 — 다운로드 시점 기록이라 그대로 둠.
- `71. Entity Definitions & Data Dictionary` · `72. Entity Relationship Diagram` 자체는 이미 v1.7이라 추가 수정 없음.

---

## 2026-09-14 — 한글 테이블·컬럼명 CSV 사본 + ERD 다이어그램 신규 (발표/비개발자 공유용)

**⚠️ 아직 Team GitHub 저장소에 커밋 안 함 — 로컬에만 존재.** 아래 경로는 전부 로컬 Team 저장소 클론 기준(`C:\Users\nklee\Desktop\MS-DataSchool-Code\22.MS_2nd_Project_Team\`).

- **한글 컬럼명 CSV 14개** — `30.DATA/32. nqnq_data/전체csv파일_v5_한글변경(테이블,컬럼)/` 폴더 신설. `full_export/`의 14개 원본 CSV(영문 스키마, [[61-entity-dictionary]] 기준)와 1:1 대응하되 테이블명·컬럼명만 한글로 변경 — 데이터 값 자체는 원본과 동일.

| 한글 파일명 | 원본(영문) 테이블 |
| --- | --- |
| `고객.csv` | `CUSTOMER` |
| `공장.csv` | `FACTORY` |
| `매장.csv` | `STORE` |
| `반품요청.csv` | `RETURN_REQUEST` |
| `발주.csv` | `PURCHASE_ORDER` |
| `발주품목.csv` | `PO_ITEM` |
| `상품.csv` | `PRODUCT` |
| `재고.csv` | `INVENTORY` |
| `재고관리단위.csv` | `SKU` |
| `재고원장.csv` | `INVENTORY_LEDGER` |
| `주문.csv` | `ORDERS` |
| `주문품목.csv` | `ORDER_ITEM` |
| `채널.csv` | `CHANNEL` |
| `카테고리.csv` | `CATEGORY` |

- **ERD 다이어그램 신규** — `30.DATA/32. nqnq_data/ERD_다이어그램.html`(독립 실행 HTML, 폰트 임베드된 단일 파일, 약 3.5MB). 제목 "NQNQ 데이터베이스 ERD (v5)" — 위 한글 테이블/컬럼명 기준으로 그려짐. [[62-erd]]의 Mermaid ERD(영문 스키마, 코드/DB 작업용 SSOT)를 대체하는 게 아니라, 발표나 비개발자 공유용으로 별도 병행 생성한 것.
- **용도**: 코드·스키마 작업은 계속 영문 기준([[61-entity-dictionary]] · [[62-erd]])으로 진행 — 이 한글 사본과 다이어그램은 발표자료·비개발자 설명용 보조 산출물.

---

## 2026-09-14 (계속) — 멘토링 피드백 반영: PK 표기 정정 + `62-erd` SSOT 갭 발견/수정

주제 멘토링에서 "발주품목/주문품목 PK 지정", "매장→재고 관계가 안 이어져 보인다" 코멘트를 받고 대조한 결과.

**한글 발표용 산출물 3곳에 반영** (`ERD_다이어그램.html`, `NQNQ_데이터명세서_v5.xlsx`의 `7.컬럼명세`, [[61-entity-dictionary]]):
- `PO_ITEM.po_id` → PK 표기 추가 — **2026-09-14 실측**: 현재 `po_item.csv` 4,306행 전부 `po_id` 유니크(1발주=1SKU)
- `ORDER_ITEM`의 `order_id`+`sku_code` → 복합PK 표기 추가 — **실측**: `order_id` 단독은 주문당 최대 15건 중복돼 불가하지만 (order_id, sku_code) 조합은 1,857,132행 전부 유니크
- `STORE`의 PK 표시명을 "매장아이디"→"위치아이디"로 통일 — `INVENTORY`/`INVENTORY_LEDGER`의 FK 컬럼명(`location_id`=위치아이디)과 이름이 달라서 "관계가 안 이어져 보인다"는 오해의 실제 원인이었음. `ORDERS.store_id`(매장아이디)는 오프라인 매장 전용 의미라 그대로 유지.
- ⚠️ 위 3건은 전부 **문서 표기 정정**이지 실제 스키마 변경이 아님 — 아래 참고.

**중요 확인 사항 — `models.py`/`nqnq.db`는 원래부터 정상이었음**:
- `PoItem`·`OrderItem`은 애초에 `id = Column(Integer, primary_key=True, autoincrement=True)`로 surrogate PK가 정의돼 있음. 다만 **CSV export가 이 `id` 컬럼을 안 내보내서**(`po_item.csv`/`order_item.csv`엔 없음) 한글 산출물(CSV 기준)만 보면 PK가 안 보였던 것 — 그래서 "실측 결과 po_id/composite가 사실상 PK"라고 문서화한 것이지 `models.py`를 고치라는 뜻은 아니었음.
- `Inventory.location_id`/`InventoryLedger.location_id`도 원래부터 `ForeignKey("store.store_id")`로 정상 선언돼 있었음 — "매장→재고 관계"는 데이터도 실측으로 1:N 확인됨(예: STORE-02 재고 418행·재고원장 7만행). 진짜 문제는 관계가 아니라 **[[62-erd]]의 Mermaid 다이어그램에 `STORE ||--o{ INVENTORY`·`STORE ||--o{ INVENTORY_LEDGER` 관계선 자체가 빠져있던 것** — 이번에 발견해서 [[62-erd]] v1.8로 추가함(같은 김에 `PO_ITEM`/`ORDER_ITEM`의 `id` PK 필드도 SSOT에 누락돼 있어 같이 보정).

**남은 것 (급하지 않음)**:
- `전체csv파일_v5_한글변경(테이블,컬럼)/매장.csv`는 여전히 컬럼명이 "매장아이디"라, 위에서 통일한 "위치아이디"와 표기가 다름 — 요청 시 맞출 예정, 아직 미반영.
