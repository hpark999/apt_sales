# 공개 배포 실습 가이드 (Render)

GitHub에는 **코드만** 올라가 있습니다. 인터넷에서 대시보드를 보려면 Python 서버를 클라우드에 배포해야 합니다.

## 왜 GitHub Pages로는 안 되나요?

| 방식 | 가능 여부 | 이유 |
|------|-----------|------|
| GitHub Pages | ❌ | HTML만 호스팅, `server.py` 실행 불가 |
| Render / Railway | ✅ | Python 서버 + API 프록시 실행 가능 |
| 로컬 `127.0.0.1:8080` | ✅ | 내 PC에서만 접속 가능 |

공공데이터 API는 브라우저에서 직접 호출하면 CORS 오류가 나므로, `server.py`가 중간에서 대신 호출해 줍니다.

---

## Render 배포 (약 5분, 무료)

### 1단계 — Render 가입 및 GitHub 연결

1. https://render.com 접속 → **Get Started** (GitHub 계정으로 가입 가능)
2. 우측 상단 **New +** → **Blueprint** 선택
3. **Connect account** → GitHub `hpark999` 계정 연결
4. 저장소 **`apt_sales`** 선택 → **Connect**

### 2단계 — 환경변수 설정

Blueprint 적용 화면에서 `SERVICE_KEY` 입력란이 나옵니다.

| Key | Value |
|-----|-------|
| `SERVICE_KEY` | 공공데이터포털 일반 인증키 |

> 키는 GitHub에 올리지 않고 Render 환경변수에만 넣습니다.

### 3단계 — 배포

1. **Apply** 클릭
2. 2~3분 대기 (Logs 탭에서 `대시보드: http://0.0.0.0:10000` 비슷한 메시지 확인)
3. 상단 **URL** 클릭 → `https://apt-sales-gangnam.onrender.com` 형태

이 URL을 **어디서든** (폰, 다른 PC) 열 수 있습니다.

### 4단계 — 동작 확인

- 대시보드: `https://(본인-URL)/`
- 헬스체크: `https://(본인-URL)/api/health` → `{"status":"ok"}`

> 무료 플랜은 15분 미사용 시 슬립 모드 → 첫 접속 시 30초~1분 걸릴 수 있습니다.

---

## 코드 수정 후 재배포

```bash
git add .
git commit -m "update dashboard"
git push origin main
```

Render가 GitHub push를 감지하면 **자동 재배포**됩니다.

---

## 비활성화 실습

### 일시 중지 (URL 접속 불가, 설정 유지)

Render Dashboard → `apt-sales-gangnam` → **Suspend**

### 완전 삭제

Render Dashboard → **Delete Web Service**

### GitHub 저장소 보관

GitHub → `apt_sales` → Settings → **Archive this repository**

---

## 문제 해결

| 증상 | 해결 |
|------|------|
| Application failed to respond | Render Logs 확인, `SERVICE_KEY` 설정 여부 |
| API 403 | 운영 URL 사용 중인지 확인 (`AptTrade`, not `Dev`) |
| 첫 로딩 매우 느림 | 무료 플랜 슬립 모드 — 정상 |
