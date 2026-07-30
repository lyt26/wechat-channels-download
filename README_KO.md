# 위챗 채널(视频号) 다운로더

<p align="center">
  <img src="docs/assets/logo.png" width="120" alt="SPH Logo" />
</p>

<p align="center">
  <b>공유 링크만 붙이면 MP4가 됩니다.</b><br/>
  복잡한 설정 없음. 초보도 30초면 충분.
</p>

<p align="center">
  <a href="README.md">简体中文</a> ·
  <a href="README_EN.md">English</a> ·
  <a href="README_JA.md">日本語</a> ·
  <a href="#-30초-빠른-시작">한국어</a>
</p>

<p align="center">
  <img src="docs/assets/hero-banner.png" width="900" alt="히어로 배너" />
</p>

<p align="center">
  <a href="https://github.com/lyt26/wechat-channels-download/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/lyt26/wechat-channels-download?style=for-the-badge&logo=github&color=07C160" /></a>
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img alt="License" src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" />
</p>

---

## 🟢 초보 추천: Windows 화면 버전

1. [Releases](https://github.com/lyt26/wechat-channels-download/releases/latest) 에서  
   **`WeChatChannelsDownloader-Windows.exe`** 다운로드
2. 더블클릭 → 링크 붙여넣기 → 초록 버튼

연락 QQ **3031635159**（커피 한 잔 환영·선택）. 무료, 라이선스 잠금 없음. [docs/SUPPORT.md](docs/SUPPORT.md)

소스 실행:

```bash
python gui/app.py
```

---

## 왜 Star 할까요?

| 문제 | 예전 | 지금 |
|------|------|------|
| PC에 저장하고 싶음 | 화면 녹화로 화질 저하 | **명령 한 줄 → 선명한 MP4** |
| `yt-dlp` 되나요? | **미지원** | `weixin.qq.com/sph/...` 전용 |
| 개발자여야 하나요? | 인증서·패킷 캡처 | **링크 복사 후 실행** |

도움이 되었다면 **Star** 한 번이 큰 힘이 됩니다. ⭐

---

## 🚀 30초 빠른 시작

<p align="center">
  <img src="docs/assets/steps-flow.png" width="900" alt="3단계 흐름" />
</p>

1. 위챗 채널에서 **공유 → 링크 복사**
2. Python 3.10+ 설치 (최초 1회)
3. 실행:

```bash
git clone https://github.com/lyt26/wechat-channels-download.git
cd wechat-channels-download

python scripts/download_sph.py "https://weixin.qq.com/sph/당신의ID" -o ./downloads
```

`downloads` 폴더의 MP4를 더블클릭하면 재생됩니다.

---

## ✨ 특징

- 추가 pip 패키지 없음 (표준 라이브러리만)
- 공유 문장 속 URL 자동 추출
- Windows / macOS / Linux 안전한 파일명
- `--h265` 로 고비트레이트 우선 가능
- Cursor Agent Skill 포함

---

## 📦 사용법

```bash
python scripts/download_sph.py "공유링크" -o ./downloads
python scripts/download_sph.py "이거 봐 https://weixin.qq.com/sph/xxxx" -o ./downloads
python scripts/download_sph.py "https://weixin.qq.com/sph/xxxx" -o ./downloads --h265
```

| 인자 | 의미 |
|------|------|
| `url` | 공유 링크 또는 링크가 포함된 텍스트 |
| `-o` | 저장 폴더 |
| `--h265` | H.265 우선 |
| `--json` | 파싱 JSON 출력 |

---

## 동작 원리 (쉽게)

```text
공유 링크 → 실제 영상 URL 해석 → Referer와 함께 다운로드 → MP4 저장
```

공식 미리보기는 종종 **표지만** 주고, `yt-dlp`도 미지원입니다. 이 도구가 그 빈틈을 채웁니다.

---

## FAQ

**실패 / videoUrl 없음**  
링크 만료가 흔합니다. 위챗에서 링크를 다시 복사하세요.

**상업적 대량 수집?**  
개인 백업·허가된 자료용입니다. 저작권과 플랫폼 규칙을 지켜 주세요.

---

## 라이선스

MIT. 도움이 되었다면 **Star** 부탁드려요. ⭐

<p align="center">
  <a href="https://github.com/lyt26/wechat-channels-download">https://github.com/lyt26/wechat-channels-download</a>
</p>
