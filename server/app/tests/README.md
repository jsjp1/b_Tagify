# Overview

이 디렉토리는 FastAPI 기반 프로젝트의 **기능별 단위 테스트**를 포함
각 테스트 파일은 하나의 도메인(예: 사용자, 인증, 콘텐츠 등)을 담당하며, 아래와 같은 API들을 검증

## Test Environment

- 비동기 테스트 지원: `pytest-asyncio`
- FastAPI 디펜던시 오버라이드 및 비동기 DB 세션 사용
- 외부 인증 API (Google/Apple OAuth)는 `unittest.mock.AsyncMock` 으로 패치 처리
- 인증이 필요한 요청은 `auth_client` fixture 사용

---

## Test Detail

### [`test_user.py`](./unit/test_user.py)

#### `/health/db`

| 테스트명             | 설명                                      |
| -------------------- | ----------------------------------------- |
| `test_db_connection` | DB 연결 정상 여부 확인 (`GET /health/db`) |

---

#### `/api/users/`

| 테스트명             | 설명                                                                |
| -------------------- | ------------------------------------------------------------------- |
| `test_get_all_users` | 전체 유저 조회 응답 구조 및 필드 포함 여부 확인 (`GET /api/users/`) |

---

#### `/api/users/login` (OAuth)

| 테스트명                          | 설명                                                       |
| --------------------------------- | ---------------------------------------------------------- |
| `test_login_google_new_user`      | 신규 Google 유저 로그인 → 유저 생성 및 토큰 발급           |
| `test_login_google_existing_user` | 기존 Google 유저 로그인 → 새 유저 생성 없이 기존 유저 반환 |
| `test_login_google_invalid_token` | Google OAuth 토큰에서 `sub` 누락 → 400 에러 확인           |
| `test_login_apple_new_user`       | 신규 Apple 유저 로그인 → 유저 생성 및 토큰 발급            |
| `test_login_apple_existing_user`  | 기존 Apple 유저 로그인 → 기존 유저 반환                    |
| `test_login_apple_invalid_token`  | Apple OAuth 토큰에서 `sub` 누락 → 400 에러 확인            |

---

#### `/api/users/token/refresh`

| 테스트명                     | 설명                                                    |
| ---------------------------- | ------------------------------------------------------- |
| `test_refresh_token_success` | 유효한 refresh_token으로 새로운 access_token 발급       |
| `test_refresh_token_missing` | refresh_token 누락 시 422 Validation Error 발생         |
| `test_refresh_token_invalid` | 잘못된 refresh_token 사용 시 401 Unauthorized 에러 발생 |

---

#### `/api/users/name/{user_id}`

| 테스트명                                 | 설명                                              |
| ---------------------------------------- | ------------------------------------------------- |
| `test_update_user_name_success`          | 유저 이름 변경 성공 케이스                        |
| `test_update_user_name_validation_error` | `username` 누락 시 422 Validation Error           |
| `test_update_user_name_invalid_user`     | 존재하지 않는 유저 ID에 대해 처리 확인 (400 예상) |

---

#### `/api/users/profile_image/{user_id}`

| 테스트명                                     | 설명                                               |
| -------------------------------------------- | -------------------------------------------------- |
| `test_update_profile_image_success`          | 유저의 프로필 이미지 URL 변경 성공                 |
| `test_update_profile_image_validation_error` | `profile_image` 누락 시 422 Validation Error       |
| `test_update_profile_image_invalid_user`     | 잘못된 유저 ID로 요청 시 예외 처리 확인 (400 예상) |

---

## 공통 설정

- 인증 필요 테스트는 `auth_client` fixture를 사용
- Google / Apple OAuth는 `verify_google_token`, `verify_apple_token`을 `AsyncMock`으로 패치하여 외부 호출 제거
- `test_user_persist`, `test_google_user_persist`, `test_apple_user_persist` 등의 fixture로 사용자 미리 생성
