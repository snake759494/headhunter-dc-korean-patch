# 재빌드

## 준비물

- Python 3.11 이상
- `numpy`, `Pillow` (`pip install numpy pillow`)
- 원본 유럽판 디스크 1·2의 Redump cue/bin
  - 저장소 최상위에 두 디스크의 `.cue`와 `(Track 3).bin`을 둡니다. 파일 이름은 Redump 이름 그대로여야 합니다.
  - Track 3의 MD5는 디스크 1이 `208145da634104c4c05c185e71550fad`, 디스크 2가 `2fe16b28a2915900b3a3187b5eedd379`이어야 합니다.
- 글꼴(`docs/FONT_CREDITS.md`). 저장소 최상위나 `fonts/` 폴더에 둡니다.
  - `NanumSquareNeo-cBd.ttf`, `NanumSquareNeo-eHv.ttf`
- (배포 파일을 만들 때) xdelta3

## 순서

```powershell
python tools/prepare.py
```

이 명령이 하는 일은 다음과 같습니다.
1. 두 디스크의 Track 3 MD5를 확인합니다.
2. 실행 파일 `1ST_READ.BIN`을 `orig/`에 꺼냅니다.
3. `tools/extract_text.py`로 영어 원문 텍스트를 `text_en/`과 `text_index.json`에 꺼냅니다.

```powershell
python tools/check_tr.py
python tools/build.py
```

- `check_tr.py`: 번역문에 게임 글꼴이 표시할 수 없는 문자나 CSV 구분자(`;`)가 없는지 검사합니다. `errors 0`이 나와야 합니다.
- `build.py`: 원본 Track 3를 복사해 `... (Track 3) [KR].bin`과 이를 가리키는 `... [KR].cue`를 디스크마다 만듭니다.
  - 중간에 `texts 893 glyphs 919`가 나오면 번역을 모두 찾은 것입니다.
  - 번역이 없는 문장이 있으면 `missing.txt`에 파일 이름과 원문 해시를 적고 멈춥니다.
  - 디스크 하나만 만들려면 `python tools/build.py 1`처럼 번호를 줍니다.

## 배포 파일 만들기

```powershell
xdelta3 -e -0 -S none -A -s '.\Headhunter (Europe) (En,Fr,De,Es) (Disc 1) (Track 3).bin' '.\Headhunter (Europe) (En,Fr,De,Es) (Disc 1) (Track 3) [KR].bin' Headhunter_DC_KO_v1.0_Disc1.xdelta
xdelta3 -e -0 -S none -A -s '.\Headhunter (Europe) (En,Fr,De,Es) (Disc 2) (Track 3).bin' '.\Headhunter (Europe) (En,Fr,De,Es) (Disc 2) (Track 3) [KR].bin' Headhunter_DC_KO_v1.0_Disc2.xdelta
```

결과 bin의 SHA-256이 README 표의 값과 같으면 배포판과 같은 결과입니다.

## 생성·무시되는 파일

다음 파일은 `.gitignore`에 들어 있어 커밋되지 않습니다.
- 원본·결과 cue/bin, xdelta
- `orig/`, `text_en/`, `text_index.json`, `missing.txt`
- 글꼴
