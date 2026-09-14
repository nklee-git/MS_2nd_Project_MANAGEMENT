> **이 문서는 Dataview로 vault의 원본 문서를 실시간 쿼리합니다.** 여기서 체크박스를 클릭하면 원본 파일의 체크박스도 함께 바뀝니다(Dataview 기본 동작). 내용을 직접 수정하려면 아래 링크된 원본 문서를 여세요.

## 📊 진행 현황 요약 (문서별)

```dataview
TABLE
  length(filter(file.tasks, (t) => !t.completed)) AS "남음",
  length(filter(file.tasks, (t) => t.completed)) AS "완료"
FROM ("04.MS-DataSchool/20.PROJECT/22.MS_2nd_Project/00-wbs" OR "04.MS-DataSchool/20.PROJECT/22.MS_2nd_Project/10-planning" OR "04.MS-DataSchool/20.PROJECT/22.MS_2nd_Project/20-architecture") AND -"04.MS-DataSchool/20.PROJECT/22.MS_2nd_Project/00-wbs/daily-logs"
WHERE length(file.tasks) > 0
SORT file.name ASC
```

## 🔥 지금 당장 (PM 개인 액션)
```dataview
TASK
FROM ("04.MS-DataSchool/20.PROJECT/22.MS_2nd_Project/00-wbs" OR "04.MS-DataSchool/20.PROJECT/22.MS_2nd_Project/10-planning" OR "04.MS-DataSchool/20.PROJECT/22.MS_2nd_Project/20-architecture") AND -"04.MS-DataSchool/20.PROJECT/22.MS_2nd_Project/00-wbs/daily-logs"
WHERE contains(tags, "#todo/now")
SORT completed ASC
```

## 🧰 팀 온보딩 (합류 직후, 전원)
```dataview
TASK
FROM ("04.MS-DataSchool/20.PROJECT/22.MS_2nd_Project/00-wbs" OR "04.MS-DataSchool/20.PROJECT/22.MS_2nd_Project/10-planning" OR "04.MS-DataSchool/20.PROJECT/22.MS_2nd_Project/20-architecture") AND -"04.MS-DataSchool/20.PROJECT/22.MS_2nd_Project/00-wbs/daily-logs"
WHERE contains(tags, "#todo/onboarding")
SORT completed ASC
```

## 📚 팀 합류 전 자료 보강
```dataview
TASK
FROM ("04.MS-DataSchool/20.PROJECT/22.MS_2nd_Project/00-wbs" OR "04.MS-DataSchool/20.PROJECT/22.MS_2nd_Project/10-planning" OR "04.MS-DataSchool/20.PROJECT/22.MS_2nd_Project/20-architecture") AND -"04.MS-DataSchool/20.PROJECT/22.MS_2nd_Project/00-wbs/daily-logs"
WHERE contains(tags, "#todo/pre-team")
SORT completed ASC
```

## 🤝 Week 0 — 팀 첫 회의 안건
```dataview
TASK
FROM ("04.MS-DataSchool/20.PROJECT/22.MS_2nd_Project/00-wbs" OR "04.MS-DataSchool/20.PROJECT/22.MS_2nd_Project/10-planning" OR "04.MS-DataSchool/20.PROJECT/22.MS_2nd_Project/20-architecture") AND -"04.MS-DataSchool/20.PROJECT/22.MS_2nd_Project/00-wbs/daily-logs"
WHERE contains(tags, "#todo/week0")
SORT completed ASC
```

## ⚙️ Week 1~3 — 기술 실행
```dataview
TASK
FROM ("04.MS-DataSchool/20.PROJECT/22.MS_2nd_Project/00-wbs" OR "04.MS-DataSchool/20.PROJECT/22.MS_2nd_Project/10-planning" OR "04.MS-DataSchool/20.PROJECT/22.MS_2nd_Project/20-architecture") AND -"04.MS-DataSchool/20.PROJECT/22.MS_2nd_Project/00-wbs/daily-logs"
WHERE contains(tags, "#todo/week1-3")
SORT completed ASC
```

## 🎤 발표 준비 (PM 담당)
```dataview
TASK
FROM ("04.MS-DataSchool/20.PROJECT/22.MS_2nd_Project/00-wbs" OR "04.MS-DataSchool/20.PROJECT/22.MS_2nd_Project/10-planning" OR "04.MS-DataSchool/20.PROJECT/22.MS_2nd_Project/20-architecture") AND -"04.MS-DataSchool/20.PROJECT/22.MS_2nd_Project/00-wbs/daily-logs"
WHERE contains(tags, "#todo/presentation")
SORT completed ASC
```

## 🗄️ 백로그 — 착수 보류 (이유 명시, 2026-09-09 추가)
> [[72-dashboard-spec]] 부록(이해관계자 협업 대시보드 확장) Should/Could 항목. Must 티어는 이미
> 구현완료라 여기 없음 — 아래는 "왜 지금 안 하는지"까지 적어둔 것만 남김.
- [ ] 승인 워크플로우 스텝퍼 — *데이터 필요*: `ReorderRecommendation.status`가 3종뿐이라 다단계 결재 상태 저장 불가, 스키마 확장 먼저 #todo/backlog
- [ ] 코멘트 스레드(승인 드로어) — *데이터 필요*: `MENTION` 엔티티 없이는 새로고침 시 사라지는 로컬 목업 수준 #todo/backlog
- [ ] 디자이너 화면 — 리뷰 워드클라우드/SNS 무드보드 — *데이터 자체가 없음*: 리뷰 원문·SNS 크롤링 데이터 미보유, 외부 연동 논의 필요 #todo/backlog
- [ ] 마케터 화면 — CAC/ROAS, RFM 매트릭스 — *논의 필요*: RFM은 집계 쿼리 설계 필요, CAC/ROAS는 `CAMPAIGN` 엔티티 자체가 없어 마케터 롤 착수 여부부터 4인 회의 안건 #todo/backlog
- [ ] SCM 화면 — 공급망 현황/재고 이관 요청 — *데이터+논의 필요*: `STORE`별 재고 분할 스키마 없음, SCM 역할 실제 담당자도 미정 #todo/backlog
- [ ] 경영진 화면 — 통합 KPI 드릴다운/대규모 투자 승인함 — *데이터 필요*: 부서별 화면 자체가 없어 드릴다운 타겟 없음, 승인함은 스텝퍼와 동일한 다단계 결재 상태 갭 #todo/backlog
- [ ] TASK/MENTION/ALERT_LOG 3개 엔티티 실제 Dataverse 스키마화 — *논의 필요*: 데이터 모델링 담당자 협의 필요 #todo/backlog

## 🗑️ 미분류 (태그 없는 체크박스 — 확인 필요)
```dataview
TASK
FROM ("04.MS-DataSchool/20.PROJECT/22.MS_2nd_Project/00-wbs" OR "04.MS-DataSchool/20.PROJECT/22.MS_2nd_Project/10-planning" OR "04.MS-DataSchool/20.PROJECT/22.MS_2nd_Project/20-architecture") AND -"04.MS-DataSchool/20.PROJECT/22.MS_2nd_Project/00-wbs/daily-logs"
WHERE !contains(tags, "#todo/now") AND !contains(tags, "#todo/pre-team") AND !contains(tags, "#todo/week0") AND !contains(tags, "#todo/week1-3") AND !contains(tags, "#todo/presentation") AND !contains(tags, "#todo/onboarding") AND !contains(tags, "#todo/backlog")
SORT completed ASC
```

---

## 🗂️ 참고 문서 전체 맵
- [[21-system-model]] — 전체 비전 + 2차 스코프 노트
- [[3-roadmap]] — Phase 16 전체 진행상황
- [[2-schedule]] — 기술 레이어별 일자별 WBS (xlsx 버전 동일 폴더에 있음)
- [[4-changelog]] — 버전별 변경이력
- [[index]] — PM 일별 업무 상세 기록(무엇을 했는지)
- [[82-ppt-plan]] — 최종발표 컨셉·예측검증 시나리오
- [[23-cost-plan]] — 비용안전 아키텍처·D365 연동 기술옵션
- [[1-kickoff-brief]] — 팀 첫 회의용 방향성 브리핑
- [[2-tech-research]] — 경쟁사 분석·과금모델
- [[22-feature-spec]] — 크로스커팅 계약 + 롤별 TBD
- [[72-dashboard-spec]] — 대시보드 v1(MVP)+v2(협업 확장) 통합 스펙, 실제 코드는 `MS-DataSchool-Code/22.MS_2nd_Project_Team/70.FRONT`(볼트 밖)
- [[2-onboarding-checklist]] — 합류 직후 준비사항
- [[1-execution-plan]] — 롤별 주차 초안 + 병렬 작업 체크 방법
- [[3-ai-ethics-checklist]] — 심사기준 AI 윤리(15점) 대응
- [[2-tech-research]] — 경쟁사·기술스택 통합 조사

> 새 TODO를 추가할 땐 원본 문서에 `- [ ] 내용 #todo/카테고리` 형식으로 쓰기만 하면 이 대시보드에 자동으로 나타납니다. 카테고리: `now` · `pre-team` · `week0` · `week1-3` · `presentation` · `onboarding` · `backlog`(착수 보류, 이유 필수)
