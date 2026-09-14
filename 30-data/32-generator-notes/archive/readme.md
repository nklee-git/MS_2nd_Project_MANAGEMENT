# 아카이브

현재 파이프라인(`generate_v5.py` + `generate_v4_miss.py` + `add_wholesale.py`)에서 더 이상 쓰이지 않는 이전 버전/중간 산출물 모음. 삭제하지 않고 보관만 함.

## generate_scripts/
- `generate_v3.py`, `generate_v3_miss.py` — v4 이전 버전 (243 SKU 카탈로그, 인기도 티어 도입 전)
- `generate_v4.py` — 베이스 시나리오 생성 스크립트. v5(`../generate_v5.py`, HUB/매장 재고 분리)로 대체됨.
  - 주의: `generate_v4_miss.py`(미달 시나리오)는 아직 v5로 포팅되지 않아 메인 폴더에 그대로 남아있음 — v4.py와 짝을 이루는 파일이라 필요 시 참고용으로 여기 함께 둘 수도 있으나, 현재는 활성 스크립트라 메인에 유지.

## export_scripts/
- `export_for_dataverse.py`, `export_full_for_dataverse.py` — v5 스키마 변경(inventory/inventory_ledger에 `location_id` 추가) 이전 버전. 지금 `nqnq.db`에 그대로 실행하면 컬럼이 어긋남. 전체 추출은 `../export_full_v5.py`로 대체됨.

## catalog_preview/
- 2026-09 체형태그·사이즈 개편을 `nqnq.db` 재생성 전에 미리 검증하기 위해 뽑았던 1회성 산출물(products/sku_master만). 재생성 완료 후 `../csv_preview/`가 같은 내용을 최신 기준으로 포함하므로 중복.
