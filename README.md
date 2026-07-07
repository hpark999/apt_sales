# apt_sales — 서울 강남구 아파트 매매 실거래가 대시보드

국토교통부 [아파트 매매 실거래가 API](https://www.data.go.kr/data/15126469/openapi.do)를 이용한 강남구 실거래 대시보드입니다.

## 배포 URL

| 구분 | URL |
|------|-----|
| **GitHub Pages (공개)** | https://hpark999.github.io/apt_sales/ |
| **로컬 개발** | http://127.0.0.1:8080 (`python server.py`) |
| **코드 저장소** | https://github.com/hpark999/apt_sales |

---

## GitHub Pages 최초 설정 (1회만)

### 1. API 키 Secret 등록

1. GitHub → `apt_sales` 저장소 → **Settings**
2. **Secrets and variables** → **Actions** → **New repository secret**
3. Name: `SERVICE_KEY` / Value: 공공데이터포털 일반 인증키

### 2. Pages 활성화

1. **Settings** → **Pages**
2. **Build and deployment** → Source: **GitHub Actions**

### 3. 배포 실행

`main` 브랜치에 push하면 자동 배포됩니다.  
또는 **Actions** 탭 → **Deploy GitHub Pages** → **Run workflow**

1~2분 후 https://hpark999.github.io/apt_sales/ 에서 확인하세요.

---

## 로컬 실행

```bash
cp .env.example .env
# .env에 SERVICE_KEY 입력

python server.py          # 실시간 API (http://127.0.0.1:8080)
python build_pages.py     # docs/ 생성 (Pages와 동일 구조)
```

---

## GitHub Pages 비활성화 (실습용)

1. **Settings** → **Pages**
2. Source를 **None**으로 변경 → 사이트 비공개

또는 **Settings** → **Actions** → **General** → Workflow permissions에서 Actions 비활성화

---

## 구조

```
GitHub Actions (push 시)
  → API에서 데이터 수집 (SERVICE_KEY)
  → docs/data.json + docs/index.html 생성
  → GitHub Pages 배포
```

> GitHub Pages는 정적 파일만 호스팅합니다. API 호출은 Actions에서 수행하고, 결과 JSON을 페이지에 표시합니다.
