# Demo Validation

## 1. 검증 대상

파일:

- `app.py`

데이터:

- `analysis_outputs/scoring/store_score_explanations.csv`

## 2. 검증 방식

표준 라이브러리 `ThreadingHTTPServer`를 테스트 스레드로 실행한 뒤 다음 엔드포인트를 확인했다.

검증 엔드포인트:

- `/`
- `/api/store?id=ba_13248384`
- `/api/store?id=missing_shop`

## 3. 검증 결과

### 3.1 메인 화면

요청:

```text
GET /
```

결과:

```text
HTTP 200
```

해석:

- 데모 HTML 화면이 정상 응답한다.

### 3.2 존재하는 매장 ID

요청:

```text
GET /api/store?id=ba_13248384
```

결과:

```text
HTTP 200
```

응답 주요 내용:

- 매장명: 본죽&비빔밥 구리인창점
- 브랜드: 본그룹
- 카테고리: 백반·죽·국수
- 기준 월: 2025-09
- GroMong Score: 98.18
- 등급: A

해석:

- 실제 존재하는 `platform_shop_id`에 대해 점수, 등급, 구성요소, 주요 근거가 정상 반환된다.

### 3.3 존재하지 않는 매장 ID

요청:

```text
GET /api/store?id=missing_shop
```

결과:

```json
{"store": null}
```

해석:

- 존재하지 않는 매장 ID에 대해 오류가 아니라 빈 결과를 반환한다.
- 화면에서는 “매장을 찾을 수 없습니다” 메시지를 표시하도록 구현했다.

## 4. 실행 방법

프로젝트 루트에서 다음 명령을 실행한다.

```powershell
& 'C:\Users\tobes\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' app.py
```

브라우저 접속:

```text
http://127.0.0.1:8765
```

## 5. 검증 상태

상태:

- 앱 로직 검증 완료
- API 응답 검증 완료
- 존재하지 않는 ID 예외 처리 확인 완료

주의:

- Codex 셸의 백그라운드 프로세스 유지 방식에서는 별도 서버 지속 실행이 불안정할 수 있다.
- 일반 터미널에서 위 실행 명령을 사용하면 데모 서버를 실행할 수 있다.
