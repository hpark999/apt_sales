# apt_sales — 서울 강남구 아파트 매매 실거래가 대시보드

국토교통부 [아파트 매매 실거래가 API](https://www.data.go.kr/data/15126469/openapi.do)를 이용해 강남구(`11680`) 최근 6개월 실거래 데이터를 보여주는 웹 대시보드입니다.

## 현재 상태

| 구분 | URL | 설명 |
|------|-----|------|
| **코드 저장소** | https://github.com/hpark999/apt_sales | GitHub (소스코드) |
| **로컬 대시보드** | http://127.0.0.1:8080 | `python server.py` 실행 시 **내 PC에서만** |
| **공개 대시보드** | Render 배포 후 URL 발급 | **인터넷 어디서나** 접속 가능 |

> GitHub에 push만 하면 **코드 배포**는 끝납니다. **웹사이트 공개**는 Render 등 클라우드 배포가 추가로 필요합니다.  
> 자세한 단계: **[DEPLOY.md](./DEPLOY.md)**

---

## 로컬 실행

```bash
cp .env.example .env
# .env 파일에 SERVICE_KEY 입력

python server.py
```

브라우저: http://127.0.0.1:8080

---

## 공개 배포 (Render, GitHub 연동)

1. [Render](https://render.com) 가입
2. **New → Blueprint** → GitHub `hpark999/apt_sales` 연결
3. `SERVICE_KEY` 환경변수 입력
4. **Apply** → `https://apt-sales-gangnam.onrender.com` 형태 URL 확인

상세: [DEPLOY.md](./DEPLOY.md)

---

## API 참고

- **운영 엔드포인트** (사용): `RTMSDataSvcAptTrade/getRTMSDataSvcAptTrade`
- **개발 엔드포인트** (403 발생): `RTMSDataSvcAptTradeDev/...`

---

## 비활성화 (실습용)

- **Render**: Dashboard → Suspend / Delete
- **GitHub**: Settings → Archive this repository
