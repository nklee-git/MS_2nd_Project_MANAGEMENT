# 60-rag

RAG·자동화 롤 실행 폴더. Power Automate 트리거 플로우, Teams Adaptive Card 정의를 여기 담습니다.

> **담당**: 나경(플로우 설계·에스컬레이션 로직) · 박형준(2026-09-16부터 합류 — Adaptive Card 템플릿 제작부터 시작). 데이터 적재(customer·factory) 작업 마무리 후 워크플로우 재배정([[2026-09-15-mentoring-followup]] 5절)에 따라 새로 맡은 영역. 상세 작업 순서는 [[62-work-order-parkhyungjun]] 참고.

## 참고 문서
- [[62-work-order-parkhyungjun]] — 박형준 작업지시서(무엇부터 해야 하는지 순서·판단 기준 포함)
- [[22-feature-spec]] 1-3절 — 데이터 흐름 순서(Dataverse 레코드 생성 → Power Automate 트리거 → Teams Adaptive Card → 승인 시 상태 업데이트)
- [[21-system-model]] 부록 A — 예측근거 자연어 설명 기능(2026-09-10 채택 확정, Tier 1 스트레치 — 착수 순서만 코어 이후로 결정된 상태)
- [[72-dashboard-spec]] 7절 — Teams 연동 상세(필수: 승인 알림 / Should: 웹사이트 탭)

## 📌 2026-09-14 전달사항 — 나경 신규 작업 2건 (스트레치, 코어 이후 착수)

상세 설계는 [[25-execution-design]] 2-5·2-6절 참고. 둘 다 **9/23 코어 체크포인트 통과 이후에만** 착수.

1. **위험 알람 Teams 긴급(Urgent) 우선순위**(2-6절) — risk_score가 임계값 이상인 고위험 건만 Adaptive Card를 Importance: Urgent로 발송(무음 설정해도 2분 간격 최대 20분 반복 알림). 별도 모바일 앱 신규개발은 비용·일정 리스크로 기각.
2. **담당자 부재 시 자동 의사결정**(2-5절, 임현제 제안) — "Wait for a response"에 SLA 타임아웃 추가, 타임아웃 시 `auto_decidable=true`(임현제 계산)인 저위험 건만 자동승인, 아니면 Viewer 그룹 전체 에스컬레이션 재알림. SLA 시간·긴급임계값은 9/14 회의에서 확정.
