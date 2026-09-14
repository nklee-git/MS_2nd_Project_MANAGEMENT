> 상위 문서: [[22-sku-code-system]]
> 관련 문서: [[21-core-categories]] (전체 디자인×인기도 티어 목록) · [[26-sku-change-history]] · [[61-entity-dictionary]]
> 2026.08 개정: 530 SKU로 확장되면서 전체 목록을 마크다운 표로 유지하는 게 비효율적이라 판단 — **정식 목록(Source of Truth)은 DB/CSV**로 관리하고, 이 문서는 카테고리 요약 + 조회 방법만 안내합니다.
> **⚠️ 2026-09-14 발견 — 아래 숫자는 v4(2026.08) 기준으로 stale**: 2026-09-08 체형태그·사이즈 개편([[27-size-expansion-plan]])으로 베이직 SKU가 428→418로 줄어 **전체 520 SKU**(418+102)가 현재 기준입니다 — [[61-entity-dictionary]]/[[22-sku-code-system]]/[[26-sku-change-history]]와 일치. 아래 표는 아직 갱신 전이니 숫자는 [[61-entity-dictionary]]를 기준으로 볼 것.

## 📊 전체 규모 요약 (v4, 2026.08 — stale, 현재는 520 SKU)
| 구분 | 스타일(디자인×체형/톤) | SKU |
| --- | --- | --- |
| 베이직 | 63 | 428 → **418**(2026-09-08 개편 후) |
| 트렌드캡슐 | 16 | 102 |
| **합계** | **79** | ~~530~~ → **520** |

카테고리별 분해와 디자인명·인기도 티어는 [[21-core-categories]]의 "디자인 라인업 확장" 표 참고.

## 🔎 전체 목록 조회 방법
정확한 제품명·SKU코드·가격·상태까지 포함한 전체 로스터는 아래에서 확인할 수 있습니다.

- **CSV**: 데이터 산출물의 `csv_preview/products.csv` (스타일 단위), `csv_preview/sku_master.csv` (SKU 단위)
- **DB 직접 조회**:
  ```sql
  SELECT p.style_name, p.category_code, p.body_tone_code, p.popularity_tier,
         p.line_type, p.status, COUNT(s.sku_code) as sku_count
  FROM product p JOIN sku s ON s.product_id = p.product_id
  GROUP BY p.product_id
  ORDER BY p.category_code, p.popularity_tier;
  ```

## 🏷️ 네이밍 규칙
- 베이직: `[체형/톤 라벨] 디자인명` — 예: `STR 브이넥 니트`
- 트렌드캡슐: `디자인명(체형코드)` — 예: `액티브 반집업 아우터(STR)`
- SKU 코드는 [[22-sku-code-system]] 체계를 그대로 따름: `NQ-{카테고리}-{체형/톤}-{순번}-{사이즈}-{컬러}`

세부 변경 흐름은 [[26-sku-change-history]] 참고.
