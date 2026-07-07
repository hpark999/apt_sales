# apt_sales — 서울 강남구 아파트 매매 실거래가 대시보드

국토교통부 [아파트 매매 실거래가 API](https://www.data.go.kr/data/15126469/openapi.do)를 이용해 강남구(`11680`) 최근 6개월 실거래 데이터를 보여주는 간단한 웹 대시보드입니다.

## 로컬 실행

```bash
cp .env.example .env
# .env 파일에 SERVICE_KEY 입력

python server.py
```

브라우저: http://127.0.0.1:8080

## API 참고

- **운영 엔드포인트** (사용): `RTMSDataSvcAptTrade/getRTMSDataSvcAptTrade`
- **개발 엔드포인트** (403 발생): `RTMSDataSvcAptTradeDev/...`

## GitHub 배포 (코드 업로드)

```bash
git init
git add index.html server.py README.md render.yaml .env.example .gitignore
git commit -m "Add Gangnam apartment trade dashboard"
git branch -M main
git remote add origin https://github.com/hpark999/apt_sales.git
git push -u origin main
```

## 웹 배포 (Render — GitHub 연동)

1. [Render](https://render.com) 가입 후 **New → Blueprint**
2. GitHub 저장소 `hpark999/apt_sales` 연결
3. `render.yaml` 적용 후 **Environment**에 `SERVICE_KEY` 추가
4. Deploy 완료 후 `https://apt-sales-gangnam.onrender.com` 형태 URL 확인

> GitHub Pages는 정적 파일만 호스팅하므로, API 프록시(`server.py`)가 필요한 이 프로젝트는 Render 같은 Python 호스팅을 사용합니다.

## 비활성화 방법 (실습용)

### Render 서비스 중지/삭제
1. Render Dashboard → `apt-sales-gangnam` 선택
2. **Suspend Service** (일시 중지) 또는 **Delete Web Service** (완전 삭제)

### GitHub 저장소 보관
1. GitHub → Settings → **Archive this repository** (읽기 전용 보관)
2. 또는 Settings → Danger Zone → **Delete this repository**

### 환경변수 키 폐기 (선택)
공공데이터포털에서 인증키 재발급 시 기존 키는 자동 무효화됩니다.
