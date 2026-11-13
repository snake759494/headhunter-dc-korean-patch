# 헤드헌터 드림캐스트 한글패치

드림캐스트 유럽판 **헤드헌터(Headhunter)**용 비공식 한국어 패치입니다. 다음 항목을 한국어로 바꿨습니다.

- **텍스트:** 컷신 자막, 대사·안내 메시지, 메뉴, 아이템·인벤토리, 임무 목표, 데이터베이스 항목, 문서(파일) 본문, LEILA 도움말, 라이선스 시험 브리핑, 엔딩 크레디트. 텍스트 파일 274개, 서로 다른 문장 2,213개입니다.
- **게임 글꼴:** 번역문에 쓰인 한글 919자를 나눔스퀘어네오로 새로 그렸습니다. 실행 파일의 글자 처리 루틴을 고쳐 2바이트 한글을 표시합니다.
- **그림 글자:** 타이틀 화면의 "START 버튼을 누르세요", 50/60Hz 선택 안내, 예/아니오·시작·취소 버튼, 게임 메뉴 탭(지도·VM·아이템·상태), 레이더 경고(위험·경고)

현재 배포판은 **v1.0 (2026-11-13)**입니다.

[패치 다운로드](https://github.com/snake759494/headhunter-dc-korean-patch/releases/latest) · [기술 설명](docs/TECHNICAL.md) · [재빌드](docs/BUILD.md) · [변경 기록](CHANGELOG.md) · [권리 안내](RIGHTS.md)

릴리즈에 첨부한 파일은 디스크별 한글패치 두 개입니다.
- **Headhunter_DC_KO_v1.0_Disc1.xdelta**
- **Headhunter_DC_KO_v1.0_Disc2.xdelta**

저장소에는 제작 소스와 한국어 번역만 공개합니다. 다음 파일은 넣지 않았습니다.
- 원본 디스크 이미지와 패치를 적용한 디스크 이미지
- 게임에서 추출한 파일
- 영어 원문
- 글꼴 파일과 외부 실행 파일

GitHub가 자동으로 만드는 Source code ZIP/TAR는 저장소 소스를 압축한 것이며, 게임 파일이 아닙니다.

## 게임 소개 및 대상 버전

『헤드헌터』는 아뮤즈(Amuze)가 개발하고 세가가 2001년 드림캐스트로 발매한 3인칭 액션 어드벤처 게임입니다. 치안이 민영화된 근미래 미국이 배경입니다. 기억을 잃은 전직 최고의 헤드헌터 잭 웨이드가 ACN 창립자 살해 사건의 배후를 쫓습니다. 잠입과 총격전, 오토바이 주행, VR 라이선스 시험을 오가며 진행합니다.

이 패치는 **유럽판 (En,Fr,De,Es) 2장짜리 GD-ROM (Redump cue/bin)**에만 적용됩니다. 패치하는 파일은 디스크마다 **Track 3** 하나이며, Track 1·2는 그대로 씁니다. 파일 이름보다 아래 표의 크기와 해시가 맞는지가 중요합니다.

## 적용할 원본

| 항목 | 디스크 1 | 디스크 2 |
| --- | --- | --- |
| 대상 파일 | `Headhunter (Europe) (En,Fr,De,Es) (Disc 1) (Track 3).bin` | `Headhunter (Europe) (En,Fr,De,Es) (Disc 2) (Track 3).bin` |
| 크기 | 1,185,760,800 바이트 | 1,185,760,800 바이트 |
| **원본 MD5** | `208145da634104c4c05c185e71550fad` | `2fe16b28a2915900b3a3187b5eedd379` |
| 원본 SHA-1 | `8c1667c210486bb50821d9cb2f7f83cf18da8608` | `6446ca0bd9c43b66c4623111b3e26677003518b4` |
| 원본 SHA-256 | `386138a1ef5677f57b51f435bbe16456841865796fd08b2057f344ba84ef6c52` | `09f1996f2dc291c76bbcafca6bfa33a26dfc812019e3314b834e7f5342971c70` |
| xdelta 파일 | `Headhunter_DC_KO_v1.0_Disc1.xdelta` (28,128,148 바이트) | `Headhunter_DC_KO_v1.0_Disc2.xdelta` (21,808,708 바이트) |
| xdelta SHA-256 | `8dd48b60bc9e5bc3c3f03f3b6c7da9a6ec2b05fba89d532cee0bac27760d09e4` | `77cefbe40e3794ad137baeac9af96d128f62a19ee97bfadb1fa36028b8f95013` |
| 결과 크기 | 1,185,760,800 바이트 | 1,185,760,800 바이트 |
| 결과 SHA-1 | `39baff017596248cd823c125f1252e3697834bc4` | `4aaf4e7ea84ea3fb58268a19340b0e5981bd8aef` |
| 결과 SHA-256 | `37f161fd50ae8baf2e21708fbb2a6a800e8d172ebffebe95141fea3b04d62de1` | `cd98a0859bb7f062e2ebb33a11006997e1ca340933d636b5bd90123db8fd2c96` |

원본 게임 파일은 사용자가 직접 준비해야 합니다.

## 패치 적용 방법

### 1. 해시 확인

```powershell
Get-FileHash -Algorithm MD5 -LiteralPath '.\Headhunter (Europe) (En,Fr,De,Es) (Disc 1) (Track 3).bin'
Get-FileHash -Algorithm MD5 -LiteralPath '.\Headhunter (Europe) (En,Fr,De,Es) (Disc 2) (Track 3).bin'
```

위 표와 다르면 적용을 중단하세요.

### 2. 한글판 폴더 만들기

원본을 덮어쓰지 않도록 새 폴더(예: `Headhunter (Korean)`)를 만들고, 디스크마다 다음 파일을 복사해 둡니다.
- `.cue` 파일
- `(Track 1).bin`, `(Track 2).bin`

Track 3는 다음 단계에서 패치 결과로 만듭니다.

### 3. xdelta UI로 적용

1. 릴리즈에서 xdelta 파일 두 개를 받습니다.
2. xdelta3 패치를 지원하는 도구에서 **Apply Patch** 기능을 엽니다.
3. **Patch**에는 디스크 번호가 맞는 xdelta 파일을, **Source File**에는 해시가 일치하는 원본 `(Track 3).bin`을 선택합니다.
4. **Output File**은 새 폴더 안에 **원래 Track 3와 같은 이름**으로 지정합니다. 그래야 복사해 둔 `.cue`가 그대로 결과 파일을 가리킵니다.
5. 디스크 2도 같은 방법으로 적용합니다.

xdelta는 호환성을 위해 압축·2차 압축·파일 경로 헤더 없이 만들었습니다. xdelta 자체는 [공식 프로젝트](https://github.com/jmacd/xdelta)를 참고하세요.

### 명령줄로 적용

```powershell
.\xdelta3.exe -d -s '.\Headhunter (Europe) (En,Fr,De,Es) (Disc 1) (Track 3).bin' '.\Headhunter_DC_KO_v1.0_Disc1.xdelta' '.\Headhunter (Korean)\Headhunter (Europe) (En,Fr,De,Es) (Disc 1) (Track 3).bin'
.\xdelta3.exe -d -s '.\Headhunter (Europe) (En,Fr,De,Es) (Disc 2) (Track 3).bin' '.\Headhunter_DC_KO_v1.0_Disc2.xdelta' '.\Headhunter (Korean)\Headhunter (Europe) (En,Fr,De,Es) (Disc 2) (Track 3).bin'
```

결과는 새 폴더의 `.cue`를 Redream·Flycast 등 에뮬레이터에서 여는 방식으로 실행합니다. GDEMU 등 광학 드라이브 에뮬레이터에서도 같은 cue/bin을 쓸 수 있습니다.

**언어와 세이브**
- 패치판은 게임 언어 설정과 관계없이 한국어로 나옵니다.
- 세이브 데이터 형식은 원본과 같아 원본판 VMU 세이브를 그대로 이어서 쓸 수 있습니다. 원본판에서 만든 에뮬레이터 세이브 스테이트는 쓰지 마세요.

## 한글화 범위

- **컷신 자막:** 모든 컷신의 자막
- **게임 텍스트:** 스테이지별 대사·안내, 메인 메뉴, 일시 정지 메뉴, 인벤토리·아이템 이름, 임무 목표, 데이터베이스 항목과 설명, 문서(파일) 본문, LEILA 도움말, VR 라이선스 시험 안내·브리핑, 엔딩 크레디트
- **그림 글자:**
  - 타이틀 화면의 "START 버튼을 누르세요"
  - 50/60Hz 선택 안내문과 예/아니오
  - 선택 창의 예/아니오/시작 버튼, 퍼즐 화면의 취소 버튼
  - 게임 메뉴 탭(지도·VM·아이템·상태), 레이더 경고(위험·경고)
- **글꼴:**
  - 게임 글꼴의 한글은 나눔스퀘어네오 Bd로 그렸습니다.
  - 그림 글자는 나눔스퀘어네오 Bd·Hv로 그렸습니다.
- **원문 유지:** 음성(영어), 타이틀 로고, "GAME OVER" 로고, 저작권 표기, 게임 화면 속 광고판·간판 그림

## 알려진 한계

**표기**
- 메뉴·버튼처럼 칸 크기가 정해진 곳은 원래 칸에 맞추느라 일부를 줄여 적었습니다(예: 노스·사우스 지구).
- 영어 음성에 맞춘 자막이라 한 줄 길이가 원문보다 길면 줄을 다시 나눴습니다.

**확인 범위**
- Redream에서 직접 플레이하며 다음을 확인했습니다.
  - 디스크 1: 타이틀, 메인 메뉴, 오프닝 컷신, 첫 스테이지(연구소 탈출), 게임 메뉴, 인벤토리, 데이터베이스와 문서 본문, 레이더 경고
  - 디스크 2: 타이틀, 디스크 1 세이브를 이어받은 본편 진행
- 예/아니오·시작 버튼은 게임 안에서 텍스처가 제대로 그려지는 것까지만 확인했고, 버튼이 실제로 나오는 장면까지 진행하지는 못했습니다.
- 50/60Hz 선택 화면은 PAL 기기에서만 나와 에뮬레이터에서 확인하지 못했습니다.
- 후반 스테이지의 대사는 데이터가 한국어로 바뀐 것만 확인했습니다. 실기 드림캐스트에서의 동작도 확인하지 못했습니다.

문제가 있으면 이슈로 알려 주세요.

## 재빌드

[docs/BUILD.md](docs/BUILD.md)를 참고하세요.
