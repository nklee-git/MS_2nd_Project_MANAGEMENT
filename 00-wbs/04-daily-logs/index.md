> **용도**: PM(이나경) 일별 업무 상세 기록. [[1-todo-board]]가 "지금 뭘 해야 하는지"라면, 이 문서는 "이미 뭘 했는지"의 히스토리 — 회고·발표 준비·팀 공유 시 참고.
> **2026-09-12 구조 변경**: 하루하루 쌓여 파일 하나가 계속 길어지는 문제가 있어, 날짜별로 이 폴더(`00-wbs/daily-logs/`) 안 별도 노트로 분리했습니다. 새 날짜는 이 폴더 안에 `2026-MM-DD.md` 파일로 추가하면 아래 표에 자동으로 나타납니다.
> **기록 신뢰도 표시**: 🟢 그날 세션에서 직접 기록(상세) · 🟡 git 커밋 로그 기반 재구성(제목 단위, 세부 대화 기록 없음).

```dataview
TABLE WITHOUT ID
  link(file.link, dateformat(date, "yyyy-MM-dd")) AS "날짜",
  confidence AS "신뢰도"
FROM "04.MS-DataSchool/20.PROJECT/22.MS_2nd_Project/00-wbs/daily-logs"
SORT date DESC
```
