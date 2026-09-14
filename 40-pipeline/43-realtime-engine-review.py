# ============================================================================
# [리뷰 코멘트 — 2026-09-11, 코드는 한 줄도 고치지 않았습니다. 문제 되는 줄마다
# 바로 위/옆에 ⚠️ 주석만 달았고, 아래는 그 요약입니다. 원본 로직은 100% 그대로.]
#
# 배경 이해: 이 스크립트는 generate_v4.py(mock, ~2026-08-09까지 커버)가 못 만드는
# "9월 held-out 실측 데이터"를 실시간/이벤트 단위로 만드는 모듈로 이해했습니다.
# 이 9월 데이터는 나중에 ML 예측치와 대조하는 라이브 데모의 핵심 자료라서
# (21. Appservice Core model.md의 "9월 held-out 실측 대조"), mock 데이터와
# 통계적 생성 규칙이 어긋나면 "모델이 틀렸다"가 아니라 "애초에 두 기간 생성
# 규칙 자체가 다르다"가 원인이 되어버립니다. 아래 이슈는 전부 그 위험과 관련.
#
# ── 0. [최우선/치명적 — 이 상태로는 실행이 안 됨] ──────────────────────────
# generate_single_realtime_event() 안, 반품/QC 처리 블록 여러 줄에
# `[span_4](start_span)[span_4](end_span)` 같은 텍스트 조각이 실행 코드 사이에
# 그대로 섞여 있습니다(해당 줄마다 아래 ⚠️⚠️ 표시). 이 상태로는 그 줄이 실행되는
# 순간 NameError가 납니다 — 즉 반품 발생 시나리오·QC 처리 시나리오는 지금까지
# 한 번도 끝까지 실행된 적이 없을 가능성이 높습니다. 코드를 옮겨오는 과정(PDF
# 주석 도구·하이라이트 뷰어 등)에서 생긴 조각인지, 최민님 원본 .py 파일에도
# 실제로 있는 건지부터 확인 부탁드립니다. 요청하신 대로 여기서는 고치지 않고
# 표시만 해뒀습니다.
#
# ── 1. [치명적 — db_name을 nqnq.db로 바꾸는 순간 기존 카탈로그가 사라짐] ────
# _init_db()가 시작할 때마다 PRODUCT/SKU/FACTORY/CHANNEL/STORE를 전부 DROP하고
# 아래 2번 항목의 "자체 소형 카탈로그"(3개 카테고리, 75개 SKU)로 다시 채웁니다.
# 지금은 db_name 기본값이 "nqnq_korean_app.db"라는 별도 파일이라 당장 위험하진
# 않지만, 나중에 9월 데이터를 mock 데이터(nqnq.db)와 합치려고 이 엔진이
# "nqnq.db"를 가리키게 되는 순간 — generate_v4.py가 만든 진짜 520개 SKU
# 카탈로그·4개 매장·공장 데이터를 통째로 삭제하고 아래 축소판으로 덮어씁니다.
# 제안: 통합 시점엔 PRODUCT/SKU/FACTORY/CHANNEL/STORE는 건드리지 말고(이미
# nqnq.db에 있는 걸 그대로 SELECT해서 재사용), 이 엔진은 트랜잭션성 테이블
# (ORDERS/ORDER_ITEM/INVENTORY_LEDGER/RETURN_REQUEST/CUSTOMER, INVENTORY UPDATE)
# 만 다루는 구조로 바꾸는 게 안전합니다.
#
# ── 2. [SKU/카테고리 체계가 공식 카탈로그와 다름 — "SKU 번호 헷갈림"의 원인] ──
# 공식 카탈로그(generate_v4.py CATEGORIES, 22. SKU & Option Code System.md):
#   - 카테고리 6종: TOP/PNT/CLR/OUT/ACC/DRS (여기선 OUT/ACC/DRS가 아예 없음)
#   - SKU 코드 포맷: NQ-{카테고리}-{일련번호}-{사이즈}-{컬러} (예: NQ-TOP-001-M-BLK)
#   - 카테고리별 실제 사이즈(TOP/PNT는 XS~4XL 8단계 등)·컬러가 SKU 코드에 들어감
# 이 스크립트:
#   - 카테고리 3종만 존재: TOP / PANTS(공식 코드는 PNT) / COLOR_BASIC(공식 코드는 CLR)
#   - SKU 코드 포맷: SKU-NQNQ-{카테고리}-{일련번호} — 사이즈·컬러가 코드에 없고
#     모든 SKU가 size="STD_SIZE", color_code="BASIC_COLOR"라는 자리표시자 문자열
#     그대로 고정됨(실제 사이즈/컬러 값이 전혀 없음)
#   - product_id도 "PRD-S1-{카테고리}" 하나뿐이라 카테고리당 스타일이 1개뿐
#     (공식은 TOP 5종/PNT 4종 등 카테고리당 여러 디자인 + HERO/STEADY/NICHE 비중)
# 9월 데이터가 이 카탈로그를 쓰면, mock 기간에 있던 SKU들(NQ-TOP-001-M-BLK 등)이
# 9월엔 하나도 안 나오고 전혀 다른 SKU 코드(SKU-NQNQ-TOP-001 등)가 나오게 됩니다
# — "SKU 번호가 헷갈린다"는 게 아마 이 지점일 것 같습니다.
# 제안: 새 카탈로그를 만들지 말고, nqnq.db의 sku/product 테이블을 그대로 읽어서
# (예: SELECT sku_code, product_id, price, cost FROM sku) 쓰는 걸 권장합니다.
#
# ── 3. [원가율 불일치] ──────────────────────────────────────────────────
# cost = price * random(0.30~0.35) — 공식(generate_v4.py COST_RATIO)은 정가의
# 48% 고정. 9월 마진율이 8월까지와 갑자기 달라 보이는 원인이 될 수 있습니다.
#
# ── 4. [채널/매장 ID 불일치] ────────────────────────────────────────────
# CH-ZIGZAG/CH-SHOWROOM vs 공식 ZIGZAG/OFFLINE(+2026-09-11에 WHOLESALE 추가).
# STR-SHOWROOM-01(open 2026-08-01) vs 공식 STORE-04(강남 상설쇼룸, open
# 2026-04-01) — 같은 매장을 가리키는 것 같은데 store_id·open_date가 모두 달라서
# 합치면 강남 상설쇼룸이 두 개 있는 것처럼 보이게 됩니다.
#
# ── 5. [채널 배정 확률] ────────────────────────────────────────────────
# 온라인 80% : 오프라인 20% — 공식(generate_v4.py)은 "운영 중인 매장이 있을
# 때만 5% 확률로 오프라인, 나머지는 온라인"(매장 공백기엔 100% 온라인)입니다.
# 20%는 공식 5%의 4배라 9월 오프라인 매출 비중이 8월까지보다 훨씬 커 보이게 됨.
#
# ── 6. [반품 발생 확률·사유 분포] ──────────────────────────────────────
# 반품 발생 확률이 카테고리 구분 없이 flat 20% — 공식은 카테고리별 return_rate
# (TOP 15%/PNT 20%/CLR 10%)를 씁니다. 아래 CATEGORY_ALERT_THRESHOLDS(22/28/15%)
# 를 정의는 해뒀지만 실제로는 어디서도 참조 안 됨(죽은 코드) — 게다가 그 값
# 자체도 "정상 반품율"이 아니라 33번 문서의 "경고 알림 트리거"(비정상 감지선)
# 값입니다.
# 반품 사유(R01~R05)도 채널 구분 없이 한 분포(45/15/20/5/15)로 뽑는데, 공식은
# 온라인/오프라인을 완전히 다른 분포로 다룹니다(오프라인: R05 70%+R01/02/03=
# 50/20/30, R04 없음 / 온라인: R01~R04=50/15/25/10, R05 없음). 특히 R05는
# 33번 문서에서 "쇼룸 체험 후 *온라인* 재구매"로 정의되는데, 이 스크립트는
# reason_code=="R05"일 때 channel_type을 "오프라인"으로 태깅합니다 — 방향이
# 반대로 보입니다. SLA도 온라인 3일/오프라인 당일(0일)/R05 1일 세 갈래가
# 맞는데 여기는 R05=1일, 나머지 전부 3일 두 갈래뿐이라 "오프라인 당일 처리"가
# 반영되지 않습니다.
#
# ── 7. [스키마 누락/추가] ──────────────────────────────────────────────
# CUSTOMER에 persona_segment 컬럼 없음(공식엔 있음). RETURN_REQUEST엔 공식
# 필드 resolution(환불/교환)이 빠지고 대신 channel_type/sla_days/is_kpi_target
# 이 새로 생김. INVENTORY엔 공식에 없는 showroom_qty/par_level이 새로 생김 —
# 방향성 자체(쇼룸 전시재고 분리)는 33번 문서 백로그와 맞지만, 쓰기로 하면
# 71/72번 문서·models.py에도 같이 반영해야 다른 사람 코드와 안 어긋납니다.
# CATEGORY/PURCHASE_ORDER/PO_ITEM 테이블 자체가 없어서, 리오더 알림이 실제
# 발주 레코드로 안 이어지고 로그 메시지만 남습니다(Dataverse
# ReorderRecommendation 원천 데이터가 없다는 뜻).
#
# ── 8. [상태값 불일치] ─────────────────────────────────────────────────
# ORDERS.status="결제완료"는 공식 enum(주문완료/배송중/배송완료/구매확정/취소)
# 에 없는 값. RETURN_REQUEST.status로 쓰는 "불량판정(폐기/수선)"·"재입고완료"도
# 공식 enum(접수/검수중/완료)에 없는 새 상태값입니다.
#
# ── [제안하는 9월 생성 시나리오] ────────────────────────────────────────
# 1) 기간: generate_v4.py TODAY=2026-08-09 다음날부터 9월 말까지 공백 없이
#    이어서 생성. 단 00.WBS 쪽 문서엔 "cutoff 8/20"이라는 표현도 있어서 실제
#    학습 컷오프가 8/9인지 8/20인지 문서 간에 안 맞습니다 — 먼저 확인 필요.
# 2) 카탈로그: 새로 만들지 말고 nqnq.db의 category/product/sku/factory/channel/
#    store를 그대로 읽어서 재사용(1·2번 항목).
# 3) 트랜잭션 규칙: "실시간"은 배치가 아니라 이벤트 단위로 도는 실행 방식일
#    뿐, 통계적 규칙(채널 배정 확률, 카테고리별 반품율, 채널별 반품사유 분포,
#    COST_RATIO, 리오더포인트 공식 등)은 generate_v4.py와 동일해야 함 — 그래야
#    "9월에 예측이 틀렸다"가 생성 규칙 차이가 아니라 진짜 모델 문제로 해석됨.
# 4) 재발주는 로그가 아니라 실제 PURCHASE_ORDER/PO_ITEM 레코드로 남겨서
#    Dataverse ReorderRecommendation과 연결 가능하게.
# 5) 새로 필요해 보이는 개념(showroom_qty 전시재고 등)이 있으면 71/72번 문서·
#    models.py에도 같이 반영해서 mock 쪽 스키마와 갈라지지 않게.
#
# ⚠️ 추가 발견(2026-09-11): [[16. PPT plan]] "설계 원리" 절엔 컷오프를
# "2026-08-20을 오늘로 고정"이라고 명시돼 있는데, generate_v4.py 코드 상수는
# TODAY = date(2026, 8, 9)로 돼 있습니다. 11일 차이 — 16번 문서가 발표 시나리오의
# 공식 설계 근거라 8/20이 맞고 코드가 안 맞춰진 쪽으로 보입니다. 9월 시작점을
# "8/20 다음날부터"로 맞추실 때 이 상수도 같이 확인해주세요.
#
# ── [라이브 데모용 사전 시딩(pre-seeding) 시나리오 — 2026-09-11 추가] ────────
# [[16. PPT plan]]에 이미 있던 결론: "약 2.5주 동안 실제로 만들어야 할 건
# 4번(라이브 데모) 하나로 수렴한다" — 즉 이 엔진은 사이드 유틸리티가 아니라
# 발표 클라이맥스 그 자체를 실행하는 모듈입니다. 발표 무대에서 "운에 맡기는"
# 방식은 위험하니, 아래처럼 특정 SKU 하나를 주인공으로 삼아 타이밍을
# 보장하는 시딩 설계를 제안합니다. (상세 각본은 [[16. PPT plan]]에 정리함 —
# 여기서는 이 엔진 코드에 어디를 건드리면 되는지만 표시)
#
# 1) 주인공 SKU 고정: NQ-TOP-001-M-BLK(스퀘어라인 기본티, TOP, HERO 등급) —
#    여러 문서에 이미 대표 예시로 반복 등장해서 발표 중 설명하기도 쉬움.
#    (이 엔진의 자체 카탈로그가 아니라 nqnq.db 진짜 카탈로그 기준 — 1·2번
#    항목대로 카탈로그를 nqnq.db에서 읽어오게 고친 뒤를 전제로 함)
#
# 2) 시딩 절차(라이브 시작 직전, 1회):
#    - 그 SKU의 INVENTORY.available_qty를 reorder_point보다 살짝 위(예: +3~5장)
#      로 맞춰둠 — 너무 크면 발표 시간(20분) 안에 안 터지고, 너무 작으면
#      시작하자마자 터져서 "실시간으로 쌓이는 모습"을 못 보여줌.
#    - 예: reorder_point=60이면 available_qty=64 정도로 세팅(실시간 스트리밍
#      3초 간격 기준 몇 번 클릭 안에 리오더포인트 도달하도록 역산).
#
# 3) ⚠️ 지금 코드로는 타이밍 보장이 안 됨: generate_single_realtime_event()의
#    `selected_skus = random.sample(MASTER_SKUS, item_count)`는 완전 균등
#    랜덤 추출입니다(공식 generate_v4.py는 인기도 가중치를 반영한
#    `random.choices(active_skus, weights=sku_weights, ...)`를 씀). 균등
#    랜덤이면 카탈로그가 수백 개일 때 주인공 SKU가 라이브 중 정확한 타이밍에
#    안 뽑힐 위험이 큽니다 — 무대에서 "왜 안 터지지"가 되면 곤란함.
#
# 4) 제안하는 보강 방향(둘 중 하나, 코드로 옮기진 않았음 — 설계만):
#    (A) 데모 전용 강제 포함 파라미터 추가
#        예: generate_single_realtime_event(self, current_time=None,
#                                            force_sku=None):
#            if force_sku: selected_skus에 force_sku를 반드시 포함시키고
#            나머지만 random.sample로 채움 — 진행자가 라이브 중 원하는
#            타이밍에 "이번엔 주인공 SKU 포함"을 직접 트리거 가능
#    (B) 공식과 동일하게 인기도 가중치 샘플링으로 바꿔서 확률만 높여두기
#        (완전 보장은 아니고 "잘 뽑히게"만 — 무대 리스크는 (A)보다 큼)
#    라이브 무대라는 특성상 (A)(강제 트리거)를 권장합니다 — 리허설(9/28)에서
#    타이밍 맞춰보고 필요하면 여러 번 눌러서 보정할 수 있게.
#
# 5) 클로징 연결: 이 SKU가 리오더포인트를 찍는 순간(위 REORDER ALERT 로그가
#    뜨는 지점, 9번 항목이 실제 PURCHASE_ORDER 레코드로 고쳐진 뒤 기준)이
#    "4번 라이브 데모"(Dataverse 승인 카드 → MD 클릭 승인)로 바로 이어지고,
#    그 다음 "9월 held-out 실측 대조" 화면으로 전환해서 이 SKU 포함 9월 전체
#    예측 오차율을 공개하는 게 [[16. PPT plan]]에 새로 정리한 각본입니다.
# ============================================================================

import sqlite3
import random
import uuid
from datetime import datetime, timedelta
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox

# ==========================================
# 1. 컬럼 및 테이블 한글 매핑 딕셔너리
# ==========================================
TABLE_DISPLAY_NAMES = {
    "INVENTORY": "재고 마스터",
    "ORDERS": "주문 트랜잭션",
    "RETURN_REQUEST": "반품/RMA 요청",
    "ORDER_ITEM": "주문 상세 품목",
    "INVENTORY_LEDGER": "재고 수불부",
    "CUSTOMER": "고객 정보",
    "SKU": "단품 SKU",
    "PRODUCT": "상품 스타일",
    "CHANNEL": "판매 채널",
    "STORE": "매장 정보",
    "FACTORY": "제조 공장"
}

COLUMN_DISPLAY_NAMES = {
    # INVENTORY
    "sku_code": "SKU코드",
    "available_qty": "가용재고수량",
    "reserved_qty": "예약재고수량",
    "defective_qty": "불량재고수량",
    "pending_return_qty": "반품대기수량",
    "showroom_qty": "전시재고수량",
    "reorder_point": "리오더포인트",
    "safety_stock": "안전재고",
    "par_level": "목표재발주량",
    "last_updated": "최종갱신일시",

    # ORDERS & ORDER_ITEM
    "order_id": "주문ID",
    "customer_id": "고객ID",
    "channel_id": "채널ID",
    "store_id": "매장ID",
    "order_date": "주문일시",
    "total_amount": "총결제금액",
    "unit_price": "판매단가",
    "qty": "주문수량",

    # RETURN_REQUEST
    "return_id": "반품ID",
    "reason_code": "사유코드",
    "channel_type": "채널구분",
    "sla_days": "SLA일수",
    "is_kpi_target": "KPI반영여부",
    "request_date": "요청일자",
    "status": "상태",

    # INVENTORY_LEDGER
    "ledger_id": "수불ID",
    "movement_type": "이동유형",
    "qty_change": "수량변동폭",
    "reference_id": "참조ID",
    "movement_date": "이동일시",

    # PRODUCT & SKU & FACTORY & OTHERS
    "product_id": "상품ID",
    "category_code": "카테고리코드",
    "style_name": "스타일명",
    "body_tone_code": "체형/톤코드",
    "season": "시즌",
    "line_type": "라인유형",
    "popularity_tier": "인기도등급",
    "launch_date": "출시일자",
    "size": "사이즈",
    "color_code": "컬러코드",
    "price": "판매가",
    "cost": "원가",
    "factory_id": "공장ID",
    "name": "공장/채널명",
    "moq": "최소주문수량_MOQ",
    "lead_time_days": "리드타임_일",
    "signup_channel": "가입채널",
    "signup_date": "가입일자",
    "type": "매장유형",
    "location": "위치",
    "open_date": "오픈일자",
    "close_date": "폐점일자"
}

# ==========================================
# 2. 문서 기반 정밀 마스터 데이터 정의
# ==========================================
MASTER_VENDOR_NAME = "성진어패럴"

# ⚠️ 6번 항목: 아래 각 튜플의 4번째 값(0.22/0.28/0.15)은 변수명은
# "return_threshold"지만 실제 값은 33. Returns & RMA Process.md의 "경고 알림
# 트리거"(TOP 22%/PANTS 28%/COLOR 15%)와 일치합니다. "정상 반품율 기준"은
# TOP 15%/PANTS 20%/COLOR 10%(generate_v4.py CATEGORIES[..]["return_rate"])라
# 이것과 다릅니다. 그리고 이 값은 CATEGORY_ALERT_THRESHOLDS에 저장만 되고
# 실제 반품 발생 판정(아래 `if random.random() < 0.20:`)에는 안 쓰입니다.
#
# ⚠️ 2번 항목: 카테고리가 TOP/PANTS/COLOR_BASIC 3종뿐 — 공식 6종(TOP/PNT/CLR/
# OUT/ACC/DRS) 중 OUT/ACC/DRS가 없고, PANTS·COLOR_BASIC은 공식 코드(PNT/CLR)
# 와 이름 자체가 다릅니다.
CATEGORIES_CONFIG = [
    ("TOP", 18, 3600, 0.22, "NQNQ SS 시즌1 상의 라인", [39000, 89000]),
    ("PANTS", 30, 6000, 0.28, "NQNQ SS 시즌1 팬츠 라인", [49000, 99000]),
    ("COLOR_BASIC", 27, 5400, 0.15, "NQNQ SS 시즌1 베이직 라인", [19000, 39000])
]

MASTER_PRODUCTS = []
MASTER_SKUS = []
CATEGORY_ALERT_THRESHOLDS = {}

for cat_code, sku_count, total_qty, return_threshold, cat_name, price_range in CATEGORIES_CONFIG:
    prod_id = f"PRD-S1-{cat_code}"
    # ⚠️ product_id가 "PRD-S1-{카테고리}" 하나뿐이라 카테고리당 스타일이 1개.
    # 공식은 TOP 5종/PNT 4종처럼 카테고리당 여러 디자인 + HERO/STEADY/NICHE
    # 인기도 비중으로 롱테일을 만드는 구조입니다(22. SKU & Option Code System).
    MASTER_PRODUCTS.append((prod_id, cat_code, cat_name, "FREE", "2026 SS", "판매중", "BASIC", "HERO", "2026-08-01"))
    # ⚠️ body_tone_code 자리에 "FREE" — 공식 규칙(71. Entity Definitions & Data
    # Dictionary.md)상 body_tone_code는 TOP/OUT/DRS="STR,WAV,NAT"류 콤마join 태그,
    # PNT/ACC="-", CLR=WRM/COOL/MUT 중 하나만 가능한데 "FREE"는 이 중 어디에도
    # 없습니다(ACC의 사이즈값 "FREE"와 컬럼이 혼동됐을 가능성). season="2026 SS"
    # 도 공식 표기(예: "Y1SS"/"2026SS", 공백 없음)와 다릅니다. popularity_tier가
    # 3개 product 전부 "HERO"인 것도, product가 카테고리당 1개뿐이라 원래
    # HERO/STEADY/NICHE로 만들려던 롱테일 가중치 구조 자체가 성립하지 않습니다.
    CATEGORY_ALERT_THRESHOLDS[cat_code] = return_threshold

    for i in range(1, sku_count + 1):
        sku_code = f"SKU-NQNQ-{cat_code}-{i:03d}"
        # ⚠️ SKU 코드 포맷이 공식(NQ-{카테고리}-{일련번호}-{사이즈}-{컬러})과 다름
        # — 사이즈·컬러가 코드에 없습니다. 9월 데이터가 이 카탈로그를 쓰면
        # mock 기간 SKU(NQ-TOP-001-M-BLK 등)와 9월 SKU가 서로 하나도 안 겹치게
        # 됩니다 — "SKU 번호 헷갈림"의 원인이 아마 이 지점일 것 같습니다.
        selling_price = random.randrange(price_range[0], price_range[1] + 1, 1000)
        cost_price = int(selling_price * random.uniform(0.30, 0.35))
        # ⚠️ 원가율 30~35% — 공식(generate_v4.py COST_RATIO)은 정가의 48% 고정.
        # 9월 마진율이 8월까지와 갑자기 달라 보이는 원인이 될 수 있습니다.
        MASTER_SKUS.append((sku_code, prod_id, "STD_SIZE", "BASIC_COLOR", selling_price, cost_price))
        # ⚠️ size="STD_SIZE", color_code="BASIC_COLOR" — 실제 값이 아니라
        # 자리표시자 문자열이 그대로 저장됩니다. 공식은 카테고리별 실제 사이즈
        # (TOP/PNT는 XS~4XL 8단계 등)·컬러 코드(BLK/WHT/CRM 등)를 씁니다.

MASTER_FACTORIES = [
    ("FACT-SJ-JAMSIL", f"{MASTER_VENDOR_NAME} 잠실 공장", 300, 45)
]
# ⚠️ factory_id "FACT-SJ-JAMSIL" — 공식(generate_v4.py, 31. Partner & Factory
# Master)은 "FAC-001" 하나뿐입니다. PURCHASE_ORDER/PO_ITEM을 나중에 만들면
# (지금은 아예 없음, 7번 항목 참고) factory_id가 안 맞아 FK가 깨집니다.

MASTER_CHANNELS = [
    ("CH-ZIGZAG", "지그재그 (온라인)"),
    ("CH-SHOWROOM", "NQNQ 오프라인 쇼룸")
]
# ⚠️ channel_id "CH-ZIGZAG"/"CH-SHOWROOM" — 공식(generate_v4.py, 42. Channel &
# Settlement Terms)은 "ZIGZAG"/"OFFLINE"(+2026-09-11에 "WHOLESALE" 추가됨).
# ID 문자열 자체가 달라서 그대로 합치면 channel 테이블에 사실상 채널이 중복
# 됩니다.

MASTER_STORES = [
    ("STR-SHOWROOM-01", "상설쇼룸", "NQNQ 강남 쇼룸", "2026-08-01", None)
]
# ⚠️ store_id "STR-SHOWROOM-01", open_date "2026-08-01" — 공식(generate_v4.py
# STORES 딕셔너리)엔 이미 "STORE-04"가 상설쇼룸/강남/open 2026-04-01로
# 존재합니다. 같은 매장을 가리키는 것 같은데 store_id·open_date가 둘 다 달라서
# 합치면 강남 상설쇼룸이 두 개 있는 것처럼 보입니다. STORE-01~04(성수 팝업/
# 홍대 상설쇼룸/강남 팝업/강남 상설쇼룸) 재사용을 권장합니다.

# ==========================================
# 3. ERD 기반 실시간 데이터 스트리밍 제어 엔진
# ==========================================
class PureRealtimeEcomEngine:
    def __init__(self, db_name="nqnq_korean_app.db"):
        # ⚠️ 1번 항목 — 이 db_name을 나중에 "nqnq.db"로 바꾸면 아래 _init_db()의
        # DROP TABLE + 자체 카탈로그 재생성 로직이 그대로 실행되어 mock 데이터의
        # 진짜 카탈로그(520개 SKU 등)를 지우고 위 축소판으로 덮어씁니다.
        self.db_name = db_name
        self._init_db()
        # ⚠️ 라이브 데모 사전 시딩 관련(파일 맨 위 참고) — 여기가 "시딩 절차"
        # 훅을 넣기 좋은 자리로 보입니다. 예시(설계만, 코드로 옮기진 않음):
        #   DEMO_SEED_SKU = "NQ-TOP-001-M-BLK"
        #   self.seed_demo_scenario(DEMO_SEED_SKU, target_gap=4)  # available_qty
        #   를 reorder_point + target_gap으로 맞추는 메서드를 새로 추가하는 방향

    def _get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()

            tables_to_drop = ["RETURN_REQUEST", "ORDER_ITEM", "ORDERS", "INVENTORY_LEDGER",
                              "INVENTORY", "SKU", "PRODUCT", "FACTORY", "CHANNEL", "STORE", "CUSTOMER"]
            for tbl in tables_to_drop:
                cursor.execute(f"DROP TABLE IF EXISTS {tbl}")
            # ⚠️ 1번 항목 — 이 DROP이 PRODUCT/SKU/FACTORY/CHANNEL/STORE까지
            # 포함합니다. nqnq.db를 가리키게 되면 여기서 mock 카탈로그가 전부
            # 사라집니다. CATEGORY/PURCHASE_ORDER/PO_ITEM은 애초에 이 목록에도,
            # 아래 CREATE TABLE에도 없습니다(9번 항목).

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS PRODUCT (
                    product_id TEXT PRIMARY KEY,
                    category_code TEXT,
                    style_name TEXT,
                    body_tone_code TEXT,
                    season TEXT,
                    status TEXT,
                    line_type TEXT,
                    popularity_tier TEXT,
                    launch_date DATE
                )
            """)
            # ⚠️ category_code가 CATEGORY 테이블을 FK로 참조하지 않습니다
            # (CATEGORY 테이블 자체가 없음) — 문자열로만 존재.

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS SKU (
                    sku_code TEXT PRIMARY KEY,
                    product_id TEXT,
                    size TEXT,
                    color_code TEXT,
                    price INTEGER,
                    cost INTEGER,
                    FOREIGN KEY(product_id) REFERENCES PRODUCT(product_id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS FACTORY (
                    factory_id TEXT PRIMARY KEY,
                    name TEXT,
                    moq INTEGER,
                    lead_time_days INTEGER
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS INVENTORY (
                    sku_code TEXT PRIMARY KEY,
                    available_qty INTEGER,
                    reserved_qty INTEGER,
                    defective_qty INTEGER,
                    pending_return_qty INTEGER,
                    showroom_qty INTEGER,
                    reorder_point INTEGER,
                    safety_stock INTEGER,
                    par_level INTEGER,
                    last_updated DATETIME,
                    FOREIGN KEY(sku_code) REFERENCES SKU(sku_code)
                )
            """)
            # ⚠️ 7번 항목 — 공식 INVENTORY(models.py)는 (sku_code, available_qty,
            # reserved_qty, defective_qty, pending_return_qty, safety_stock,
            # reorder_point, last_updated) 7개 컬럼. showroom_qty·par_level은
            # 공식엔 없는 새 컬럼입니다. 방향(쇼룸 전시재고 분리, 33번 문서
            # 백로그)은 맞아 보이지만, 쓰기로 하면 71/72번 문서·models.py에도
            # 같이 반영해야 다른 사람 코드와 안 어긋납니다.

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS INVENTORY_LEDGER (
                    ledger_id TEXT PRIMARY KEY,
                    sku_code TEXT,
                    movement_type TEXT,
                    qty_change INTEGER,
                    reference_id TEXT,
                    movement_date DATETIME,
                    FOREIGN KEY(sku_code) REFERENCES SKU(sku_code)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS CHANNEL (
                    channel_id TEXT PRIMARY KEY,
                    name TEXT
                )
            """)
            # ⚠️ 공식 CHANNEL(71번 문서)엔 commission_rate·settlement_cycle도
            # 있는데 여기는 channel_id/name 2개뿐입니다.

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS STORE (
                    store_id TEXT PRIMARY KEY,
                    type TEXT,
                    location TEXT,
                    open_date DATE,
                    close_date DATE
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS CUSTOMER (
                    customer_id TEXT PRIMARY KEY,
                    signup_channel TEXT,
                    signup_date DATE
                )
            """)
            # ⚠️ 7번 항목 — 공식 CUSTOMER(71번 문서)는 (customer_id,
            # persona_segment, signup_channel, signup_date) 4개 컬럼인데
            # persona_segment가 빠져 있습니다. 나중에 9월 CUSTOMER 데이터를
            # mock 기간 데이터와 합치면(UNION) 컬럼 수가 안 맞습니다.

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ORDERS (
                    order_id TEXT PRIMARY KEY,
                    customer_id TEXT,
                    channel_id TEXT,
                    store_id TEXT,
                    order_date DATETIME,
                    status TEXT,
                    total_amount INTEGER,
                    FOREIGN KEY(customer_id) REFERENCES CUSTOMER(customer_id),
                    FOREIGN KEY(channel_id) REFERENCES CHANNEL(channel_id),
                    FOREIGN KEY(store_id) REFERENCES STORE(store_id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ORDER_ITEM (
                    order_id TEXT,
                    sku_code TEXT,
                    qty INTEGER,
                    unit_price INTEGER,
                    FOREIGN KEY(order_id) REFERENCES ORDERS(order_id),
                    FOREIGN KEY(sku_code) REFERENCES SKU(sku_code)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS RETURN_REQUEST (
                    return_id TEXT PRIMARY KEY,
                    order_id TEXT,
                    sku_code TEXT,
                    reason_code TEXT,
                    channel_type TEXT,
                    sla_days INTEGER,
                    is_kpi_target INTEGER,
                    status TEXT,
                    request_date DATE,
                    FOREIGN KEY(order_id) REFERENCES ORDERS(order_id),
                    FOREIGN KEY(sku_code) REFERENCES SKU(sku_code)
                )
            """)
            # ⚠️ 7번 항목 — 공식 RETURN_REQUEST(71번 문서)는 (return_id, order_id,
            # sku_code, reason_code, status, request_date, resolution). 여기는
            # resolution(환불/교환)이 빠지고 channel_type/sla_days/is_kpi_target
            # 이 새로 생겼습니다 — 두 스키마를 합치려면 조정이 필요합니다.

            for item in MASTER_PRODUCTS: cursor.execute("INSERT OR REPLACE INTO PRODUCT VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", item)
            for item in MASTER_SKUS: cursor.execute("INSERT OR REPLACE INTO SKU VALUES (?, ?, ?, ?, ?, ?)", item)
            for item in MASTER_FACTORIES: cursor.execute("INSERT OR REPLACE INTO FACTORY VALUES (?, ?, ?, ?)", item)
            for item in MASTER_CHANNELS: cursor.execute("INSERT OR REPLACE INTO CHANNEL VALUES (?, ?)", item)
            for item in MASTER_STORES: cursor.execute("INSERT OR REPLACE INTO STORE VALUES (?, ?, ?, ?, ?)", item)

            for sku in MASTER_SKUS:
                cursor.execute("""
                    INSERT OR REPLACE INTO INVENTORY VALUES (?, 200, 0, 0, 0, 5, 60, 40, 150, ?)
                """, (sku[0], "2026-08-01 09:00:00"))
                # ⚠️ 모든 SKU가 available_qty=200/reorder_point=60/safety_stock=40/
                # par_level=150 고정값으로 시작 — 공식(23. Alert & Trigger Rules,
                # 32. Inventory Policy)은 이 값들을 SKU당 판매속도×인기도가중치×
                # 리드타임으로 동적 계산합니다. 초기값이라 당장은 무난하지만,
                # reorder_point=60은 우연히 공식 문서의 예시값(리오더포인트 60장)
                # 과 같아서 의도한 건지 우연인지 확인해보시면 좋을 것 같습니다.

            conn.commit()

    def clear_realtime_events(self):
        realtime_tables = ["RETURN_REQUEST", "ORDER_ITEM", "ORDERS", "INVENTORY_LEDGER", "CUSTOMER"]
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for tbl in realtime_tables:
                cursor.execute(f"DELETE FROM {tbl}")

            for sku in MASTER_SKUS:
                cursor.execute("""
                    UPDATE INVENTORY
                    SET available_qty=200, reserved_qty=0, defective_qty=0, pending_return_qty=0, last_updated=?
                    WHERE sku_code=?
                """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), sku[0]))
            conn.commit()

    def generate_single_realtime_event(self, current_time=None):
        if current_time is None:
            current_time = datetime.now()

        time_str = current_time.replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S")
        date_str = current_time.strftime("%Y-%m-%d")
        unique_suffix = f"{current_time.strftime('%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"

        order_id = f"ORD-{current_time.strftime('%Y%m%d')}-{unique_suffix}"
        cust_id = f"CUST-2026-{random.randint(1000, 9999)}"

        channel_info = random.choices(MASTER_CHANNELS, weights=[80, 20], k=1)[0]
        channel_id = channel_info[0]
        store_id = MASTER_STORES[0][0] if channel_id == "CH-SHOWROOM" else None
        # ⚠️ 5번 항목 — 온라인:오프라인 = 80:20 고정. 공식(generate_v4.py)은
        # "운영 중인 매장이 있을 때만 5% 확률로 오프라인, 나머지는 온라인"이라
        # 20%는 공식(5%)의 4배입니다. 9월 오프라인 매출 비중이 8월까지보다
        # 훨씬 커 보이게 되는 원인이 될 수 있습니다.

        event_type = random.choices(['ORDER', 'QC_PROCESS'], weights=[70, 30], k=1)[0]
        alert_logs = []

        with self._get_connection() as conn:
            cursor = conn.cursor()

            if event_type == 'ORDER':
                item_count = random.choices([1, 2, 3], weights=[60, 30, 10], k=1)[0]
                selected_skus = random.sample(MASTER_SKUS, item_count)
                # ⚠️ 라이브 데모 사전 시딩 관련(파일 맨 위 "라이브 데모용 사전 시딩
                # 시나리오" 참고) — 완전 균등 랜덤이라 주인공 SKU(NQ-TOP-001-M-BLK
                # 후보)가 라이브 중 원하는 타이밍에 안 뽑힐 수 있습니다. 데모용
                # force_sku 파라미터를 추가해서 강제 포함시키는 방향을 제안합니다
                # (설계만 위에 적어뒀고, 여기 코드는 그대로 뒀습니다).

                order_total_amount = 0
                order_items_payload = []

                for sku_info in selected_skus:
                    sku_code, prod_id, size, color, price, cost = sku_info
                    item_qty = random.choices([1, 2], weights=[80, 20], k=1)[0]
                    item_total = price * item_qty
                    order_total_amount += item_total
                    order_items_payload.append({"sku_code": sku_code, "qty": item_qty, "price": price})

                cursor.execute("INSERT OR REPLACE INTO CUSTOMER VALUES (?, ?, ?)", (cust_id, channel_info[1], date_str))
                cursor.execute("INSERT INTO ORDERS VALUES (?, ?, ?, ?, ?, ?, ?)", (order_id, cust_id, channel_id, store_id, time_str, "결제완료", order_total_amount))
                # ⚠️ 8번 항목 — status="결제완료"는 공식 enum(주문완료/배송중/
                # 배송완료/구매확정/취소)에 없는 값입니다. "주문완료" 등으로
                # 맞추거나, 새 상태값으로 쓰기로 하면 문서에도 추가가 필요합니다.

                for idx, item in enumerate(order_items_payload):
                    sku_code = item["sku_code"]
                    qty = item["qty"]
                    price = item["price"]
                    ledger_id = f"LED-{unique_suffix}-{idx+1}"

                    cursor.execute("INSERT INTO ORDER_ITEM VALUES (?, ?, ?, ?)", (order_id, sku_code, qty, price))
                    cursor.execute("INSERT INTO INVENTORY_LEDGER VALUES (?, ?, ?, ?, ?, ?)", (ledger_id, sku_code, "판매출고", -qty, order_id, time_str))

                    cursor.execute("""
                        UPDATE INVENTORY
                        SET available_qty = MAX(0, available_qty - ?),
                            last_updated = ?
                        WHERE sku_code = ?
                    """, (qty, time_str, sku_code))

                    cursor.execute("SELECT available_qty, reorder_point FROM INVENTORY WHERE sku_code = ?", (sku_code,))
                    row = cursor.fetchone()
                    if row and row[0] <= row[1]:
                        alert_logs.append(f"🚨 [REORDER ALERT] {sku_code} 가용재고({row[0]}장) <= 리오더포인트({row[1]}장) 도달! 성진어패럴 잠실 공장 발주 필요 (리드타임 52일)")[span_4](start_span)[span_4](end_span)
                        # ⚠️⚠️ 0번 항목 — 이 줄 끝의 [span_4](start_span)[span_4](end_span)
                        # 는 유효한 파이썬이 아닙니다(append()의 반환값 None을
                        # span_4로 인덱싱하려는 모양인데 span_4가 정의돼 있지도
                        # 않음) — 실행되면 NameError. 원본 파일 확인 필요합니다.
                        #
                        # ⚠️ 별개로 로직도: 리오더포인트 도달 시 로그 메시지만
                        # 남기고 실제 PURCHASE_ORDER/PO_ITEM 레코드를 만들지
                        # 않습니다(9번 항목) — 공식(generate_v4.py)은 실제
                        # po_rows/po_item_rows를 만들어 재발주가 실제 발주
                        # 데이터로 이어집니다. 이 알림이 Dataverse
                        # ReorderRecommendation의 원천이 되어야 한다면, 로그
                        # 문자열이 아니라 실제 발주 레코드가 필요합니다.

                if random.random() < 0.20:
                    # ⚠️ 6번 항목 — 카테고리 구분 없이 flat 20% — 공식은 카테고리별
                    # return_rate(TOP 15%/PNT 20%/CLR 10%, generate_v4.py
                    # CATEGORIES[..]["return_rate"])를 씁니다. 위에서 정의한
                    # CATEGORY_ALERT_THRESHOLDS(22/28/15%)조차 여기서 안 쓰입니다
                    # (죽은 코드) — 그리고 그 값 자체도 "정상"이 아니라 "경고선"
                    # 값이라 어느 쪽으로도 지금 맞지 않습니다.
                    return_id = f"RET-{unique_suffix}"
                    target_sku = order_items_payload[0]["sku_code"]

                    reasons = ["R01", "R02", "R03", "R04", "R05"]
                    weights = [0.45, 0.15, 0.20, 0.05, 0.15]
                    reason_code = random.choices(reasons, weights=weights)[0]
                    # ⚠️ 6번 항목 — 채널 구분 없이 R01~R05를 한 분포로 뽑습니다.
                    # 공식(generate_v4.py)은 채널별로 완전히 다른 분포를 씁니다:
                    #   오프라인: R05 70%, 나머지 30%를 R01/R02/R03=50/20/30로 배분
                    #             (R04는 오프라인에서 아예 안 나옴)
                    #   온라인:   R01/R02/R03/R04 = 50/15/25/10 (R05는 온라인에서 안 나옴)
                    # 지금처럼 5개를 채널 구분 없이 섞으면 33. Returns & RMA
                    # Process.md의 채널별 구분 자체가 무의미해집니다.

                    channel_type = "오프라인(쇼룸)" if channel_id == "CH-SHOWROOM" or reason_code == "R05" else "온라인(지그재그)[span_5](start_span)"[span_5](end_span)
                    # ⚠️⚠️ 0번 항목 — 이 줄도 [span_5] 조각이 문자열 안팎에 섞여
                    # 있어서(문자열 리터럴 안에 "[span_5](start_span)" 글자가
                    # 그대로 들어가고, 그 뒤에 유효하지 않은 인덱싱까지 붙음)
                    # 실행하면 에러납니다.
                    #
                    # ⚠️ 로직: 33. Returns & RMA Process.md는 R05를 "쇼룸 체험
                    # 후 *온라인* 재구매 사이즈 변경"이라고 정의합니다 — 즉 R05는
                    # 원래 온라인 채널 이벤트인데, 이 코드는 reason_code=="R05"
                    # 이면 channel_type을 "오프라인"으로 태깅합니다. 방향이
                    # 반대로 보입니다.

                    sla_days = 1 if reason_code == "R05" else 3[span_6](start_span)[span_6](end_span)
                    # ⚠️⚠️ 0번 항목 — 여기도 [span_6] 조각.
                    # ⚠️ 로직: 공식은 온라인=3일 / 오프라인=당일(0일) / R05=1일
                    # (최우선) 세 갈래인데, 여기는 R05=1일 / 그 외 전부 3일 두
                    # 갈래뿐이라 "오프라인 당일 처리"가 반영 안 됩니다.

                    is_kpi = 0 if reason_code == "R05" else 1[span_7](start_span)[span_7](end_span)
                    # ⚠️⚠️ 0번 항목 — 여기도 [span_7] 조각.
                    # ⚠️ 로직 자체(R05는 KPI 반영 안 함)는 33번 문서 3-1절과
                    # 일치해서 맞습니다.

                    cursor.execute("""
                        INSERT INTO RETURN_REQUEST VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (return_id, order_id, target_sku, reason_code, channel_type, sla_days, is_kpi, "검수대기", date_str))
                    # ⚠️ 7번 항목 — resolution(환불/교환) 컬럼이 테이블에도
                    # INSERT에도 없습니다 — 공식 스키마엔 있는 필드라 나중에
                    # 합칠 때 컬럼이 하나 빕니다.

                    cursor.execute("UPDATE INVENTORY SET pending_return_qty = pending_return_qty + 1 WHERE sku_code = ?", (target_sku,))[span_8](start_span)[span_8](end_span)[span_9](start_span)[span_9](end_span)
                    alert_logs.append(f"↩️ [RMA 접수] {target_sku} 사유:{reason_code} (채널:{channel_type}, SLA:{sla_days}일, KPI반영:{bool(is_kpi)})")[span_10](start_span)[span_10](end_span)
                    # ⚠️⚠️ 0번 항목 — 두 줄 다 [span_N] 조각 있음.

            elif event_type == 'QC_PROCESS':
                cursor.execute("SELECT return_id, sku_code, reason_code FROM RETURN_REQUEST WHERE status = '검수대기' LIMIT 1")
                row = cursor.fetchone()
                if row:
                    rma_id, rma_sku, rma_reason = row
                    if rma_reason == 'R04': # R04(불량/하자) -> 불량재고 이동[span_11](start_span)[span_11](end_span)
                        # (이 줄의 [span_11]은 주석 뒤라 실행엔 지장 없음 — 그냥 주석 글자로 붙음)
                        cursor.execute("UPDATE INVENTORY SET pending_return_qty = MAX(0, pending_return_qty - 1), defective_qty = defective_qty + 1 WHERE sku_code = ?", (rma_sku,))[span_12](start_span)[span_12](end_span)[span_13](start_span)[span_13](end_span)
                        cursor.execute("UPDATE RETURN_REQUEST SET status = '불량판정(폐기/수선)' WHERE return_id = ?", (rma_id,))[span_14](start_span)
                        alert_logs.append(f"🛠️ [QC 완료] {rma_sku} 불량(R04) -> 불량재고 이동")[span_15](start_span)[span_15](end_span)[span_16](start_span)[span_16](end_span)
                        # ⚠️⚠️ 0번 항목 — 이 블록 3줄 다 [span_N] 조각 있음(실행
                        # 코드 부분). status 값 "불량판정(폐기/수선)"은 공식
                        # enum(접수/검수중/완료)에 없는 새 상태값이라, 쓰기로
                        # 하면 71번 문서에 반영이 필요합니다(8번 항목).
                    else: # 그 외 사유 -> 가용재고 재입고 복구[span_17](start_span)[span_17](end_span)
                        # (이 줄도 주석 뒤라 실행엔 지장 없음)
                        cursor.execute("UPDATE INVENTORY SET pending_return_qty = MAX(0, pending_return_qty - 1), available_qty = available_qty + 1 WHERE sku_code = ?", (rma_sku,))[span_18](start_span)[span_18](end_span)[span_19](start_span)[span_19](end_span)
                        cursor.execute("UPDATE RETURN_REQUEST SET status = '재입고완료' WHERE return_id = ?", (rma_id,))[span_20](start_span)
                        alert_logs.append(f"✅ [QC 완료] {rma_sku} 검수 통과 -> 가용재고 복구")[span_21](start_span)[span_21](end_span)[span_22](start_span)[span_22](end_span)
                        # ⚠️⚠️ 0번 항목 — 이 블록도 3줄 다 [span_N] 조각 있음.
                        # ⚠️ status "재입고완료"도 공식 enum(접수/검수중/완료)에
                        # 없는 값입니다(8번 항목).

            realtime_tables = ["RETURN_REQUEST", "ORDER_ITEM", "ORDERS", "INVENTORY_LEDGER", "CUSTOMER"]
            for tbl in realtime_tables:
                cursor.execute(f"DELETE FROM {tbl} WHERE rowid NOT IN (SELECT rowid FROM {tbl} ORDER BY rowid DESC LIMIT 30)")
            # ⚠️ 참고용 코멘트(문제는 아님): 이 GUI 데모용 엔진은 트랜잭션 테이블을
            # 최근 30건만 남기고 지웁니다. 9월 데이터를 실제로 nqnq.db에 누적
            # 저장하려는 목적이라면, 이 정리 로직은 데모(GUI 화면 표시용)에만
            # 남기고 실제 데이터 축적 파이프라인에는 가져가면 안 됩니다.

            conn.commit()
            return alert_logs

    def get_table_data(self, table_name):
        with self._get_connection() as conn:
            df = pd.read_sql_query(f"SELECT * FROM {table_name} ORDER BY rowid DESC", conn)
            # GUI용 한글 컬럼명 변환
            df.columns = [COLUMN_DISPLAY_NAMES.get(col, col) for col in df.columns]
            return df


# ==========================================
# 4. GUI 대시보드 모듈 (한글 레이블 표출)
# ==========================================
class NqnqNeonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NQNQ [성진어패럴] 실시간 재고 & RMA 모니터링 모듈")
        self.root.geometry("1200x800")
        self.root.configure(bg="#050505")

        self.engine = PureRealtimeEcomEngine()
        self.is_running = False
        self.virtual_time = datetime.now()
        self.timer_id = None

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TNotebook", background="#050505", borderwidth=1)
        self.style.configure("TNotebook.Tab", background="#111111", foreground="#00FF66", padding=[12, 6], borderwidth=1, lightcolor="#00FF66")
        self.style.map("TNotebook.Tab", background=[("selected", "#00FF66")], foreground=[("selected", "#050505")])

        self.style.configure("Treeview", background="#050505", fieldbackground="#050505", foreground="#00FF66", rowheight=26, borderwidth=1, relief="solid")
        self.style.configure("Treeview.Heading", background="#151515", foreground="#00FF66", font=("Courier", 10, "bold"), borderwidth=1, relief="solid")

        self._build_gui()

    def _build_gui(self):
        ctrl_frame = tk.Frame(self.root, bg="#111111", pady=10, padx=10, highlightbackground="#00FF66", highlightthickness=1)
        ctrl_frame.pack(fill="x", padx=10, pady=10)

        self.btn_reset = tk.Button(ctrl_frame, text="실시간 데이터 초기화", bg="#222222", fg="#00FF66", font=("Courier", 11, "bold"), command=self.reset_data)
        self.btn_reset.pack(side="left", padx=5)

        self.btn_single = tk.Button(ctrl_frame, text="+ 1건 트랜잭션 발생", bg="#00FF66", fg="#000000", font=("Courier", 11, "bold"), command=self.add_single_event)
        self.btn_single.pack(side="left", padx=5)

        self.btn_toggle = tk.Button(ctrl_frame, text="▶ 실시간 스트리밍 (3초 간격)", bg="#222222", fg="#00FF66", font=("Courier", 11, "bold"), command=self.toggle_streaming)
        self.btn_toggle.pack(side="left", padx=5)

        self.status_label = tk.Label(ctrl_frame, text="상태: 대기 중", bg="#111111", fg="#00FF66", font=("Courier", 11))
        self.status_label.pack(side="right", padx=10)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)

        self.tables = [
            "INVENTORY", "ORDERS", "RETURN_REQUEST", "ORDER_ITEM", "INVENTORY_LEDGER", "CUSTOMER",
            "SKU", "PRODUCT", "CHANNEL", "STORE", "FACTORY"
        ]

        self.tree_views = {}
        for tbl in self.tables:
            frame = tk.Frame(self.notebook, bg="#050505")
            # 탭 이름을 한글로 표시
            display_name = TABLE_DISPLAY_NAMES.get(tbl, tbl)
            self.notebook.add(frame, text=display_name)

            scroll_y = ttk.Scrollbar(frame, orient="vertical")
            scroll_x = ttk.Scrollbar(frame, orient="horizontal")

            tree = ttk.Treeview(frame, show="headings", selectmode="browse", yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
            scroll_y.config(command=tree.yview)
            scroll_x.config(command=tree.xview)

            scroll_y.pack(side="right", fill="y")
            scroll_x.pack(side="bottom", fill="x")
            tree.pack(fill="both", expand=True)

            self.tree_views[tbl] = tree

        log_frame = tk.LabelFrame(self.root, text=" 🚨 실시간 Alert & RMA 이벤트 로그 ", bg="#050505", fg="#00FF66", font=("Courier", 10, "bold"))
        log_frame.pack(fill="x", padx=10, pady=10)

        self.log_text = tk.Text(log_frame, height=4, bg="#0A0A0A", fg="#00FF66", font=("Consolas", 9), insertbackground="#00FF66")
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)

        self.refresh_tables()

    def reset_data(self):
        if self.is_running:
            self.toggle_streaming()
        self.engine.clear_realtime_events()
        self.log_text.delete("1.0", tk.END)
        self.refresh_tables()
        self.status_label.config(text="상태: 실시간 데이터 초기화 완료")

    def add_single_event(self):
        self.virtual_time += timedelta(minutes=random.randint(1, 5))
        alerts = self.engine.generate_single_realtime_event(self.virtual_time)
        if alerts:
            for log in alerts:
                self.log_text.insert(tk.END, f"[{self.virtual_time.strftime('%H:%M:%S')}] {log}\n")
                self.log_text.see(tk.END)
        self.refresh_tables()
        self.status_label.config(text="상태: 신규 트랜잭션/QC 처리 실행됨")

    def refresh_tables(self):
        for tbl in self.tables:
            tree = self.tree_views[tbl]
            tree.delete(*tree.get_children())

            df = self.engine.get_table_data(tbl)
            tree["columns"] = list(df.columns)

            for col in df.columns:
                tree.heading(col, text=col)
                tree.column(col, width=130, anchor="center")

            for idx, row in df.iterrows():
                tree.insert("", "end", values=list(row))

    def toggle_streaming(self):
        if not self.is_running:
            self.is_running = True
            self.btn_toggle.config(text="⏹ 스트리밍 중지", bg="#00FF66", fg="#000000")
            self.status_label.config(text="상태: 실시간 트랜잭션 스트리밍 중")
            self.stream_step()
        else:
            self.is_running = False
            if self.timer_id:
                self.root.after_cancel(self.timer_id)
                self.timer_id = None
            self.btn_toggle.config(text="▶ 실시간 스트리밍 (3초 간격)", bg="#222222", fg="#00FF66")
            self.status_label.config(text="상태: 중지됨")

    def stream_step(self):
        if self.is_running:
            self.virtual_time += timedelta(minutes=random.randint(1, 3))
            alerts = self.engine.generate_single_realtime_event(self.virtual_time)
            if alerts:
                for log in alerts:
                    self.log_text.insert(tk.END, f"[{self.virtual_time.strftime('%H:%M:%S')}] {log}\n")
                    self.log_text.see(tk.END)
            self.refresh_tables()
            self.timer_id = self.root.after(3000, self.stream_step)


if __name__ == "__main__":
    root = tk.Tk()
    app = NqnqNeonApp(root)
    root.mainloop()
