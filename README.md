# Universal Unity Korean Font Patcher (범용 유니티 한글 폰트 패처)

스팀(Steam) 등의 유니티(Unity) 64-bit Mono 기반 게임에서 게임 원본 파일을 훼손하지 않고, 원하는 한글 폰트(메이플스토리체, 나눔바른고딕 등)를 게임 전체에 런타임으로 자동 주입해 주는 **범용 원클릭 한글 폰트 패치 도구**입니다.

---

## ✨ 주요 특징

1. **원클릭 GUI & CLI 지원**:
   - `run_patcher.bat` 더블 클릭만으로 직관적인 GUI 창 실행.
   - 드래그 앤 드롭 또는 폴더 선택으로 1초 만에 설치 및 삭제.
   - 파이썬 CLI 명령어(`install`, `uninstall`, `analyze`)로 스크립트 자동화 지원.
2. **비파괴적 런타임 Fallback 훅 (No-Modding Risk)**:
   - 게임의 원본 대용량 애셋(`*.assets`, `*.bundle`)을 1바이트도 수정하지 않습니다.
   - 스팀 무결성 검사나 게임 패치가 진행되어도 파일 충돌이 발생하지 않습니다.
3. **게임 내 실시간 폰트 핫리로드 (F10 키)**:
   - 게임을 끄지 않고 `BepInEx/plugins/Fonts/` 폴더에 폰트 파일을 바꾼 뒤 게임 내에서 `F10`을 누르면 실시간으로 폰트가 변경됩니다.
4. **지능형 굵기(Bold/Regular) 자동 매칭**:
   - `Bold`, `Black`, `Title` 계열의 UI에는 굵은 폰트를, 본문/설명에는 라이트/레귤러 폰트를 자동 매핑하여 가독성을 보장합니다.
5. **1초 만에 100% 순정 바닐라 복원**:
   - 패처 프로그램의 [패치 제거] 버튼 하나로 설치된 파일만 안전하게 청소하여 원상 복구됩니다.

---

## 🖥️ 호환 환경

- **엔진**: Unity 2018 ~ 2022+ 기반 PC 게임
- **런타임**: Windows 64-bit Mono 런타임 (`MonoBleedingEdge` 또는 `*_Data/Mono` 보유 게임)
- **UI 텍스트**: TextMeshPro (`Unity.TextMeshPro.dll` 사용 게임)
- **실제 검증 완료 게임 (E:\SteamLibrary)**:
  - 🟢 **House Flipper** (하우스 플리퍼)
  - 🟢 **Valheim** (발하임 - 메인 로직 분할 어셈블리 지원)
  - 🟢 **Nine Sols** (나인 솔)
  - 🟢 **Dinkum** (딩컴)
  - 🟢 **The Planet Crafter** (더 플래닛 크래프터)
  - 🟢 **My Time at Sandrock** (마이 타임 앳 샌드로크)
  - 🟢 **Another Crab's Treasure** (어나더 크랩스 트레저)
  - 🟢 **Shogun Showdown** (쇼군 쇼다운)
- **미지원 게임 유형**:
  - 🔴 **IL2CPP 게임** (Last Epoch, V Rising 등 - C++ 바이너리 컴파일 방식)
  - 🔴 **독자 비트맵/스프라이트 폰트 게임** (Core Keeper 등 - 픽셀 스프라이트 아틀라스 방식)
  - 🔴 **구형 유니티 레거시 텍스트 UI** (The Forest, Green Hell 등 - `UnityEngine.UI.Text` 사용)


---

## 🚀 사용 방법

### 1) GUI 창으로 사용하기 (가장 쉬움)
1. `run_patcher.bat` 파일을 더블 클릭하여 실행합니다.
2. **1. 게임 폴더 선택**에서 대상 게임 설치 폴더(`*_Data` 폴더가 있는 루트)를 선택합니다.
   - (예: `E:\SteamLibrary\steamapps\common\House Flipper`)
3. **2. 적용할 폰트 선택**:
   - `메이플스토리체` (권장: 제목 볼드 + 본문 라이트)
   - `나눔바른고딕`
   - `사용자 정의 폰트` (.ttf / .otf 파일 직접 선택)
4. **[🚀 패치 설치]** 버튼을 누르면 즉시 설치 완료!
5. 평소대로 스팀에서 게임을 플레이합니다.

### 2) 순정 상태로 되돌리기
- 패처 창에서 **[🗑️ 패치 제거 (순정 복원)]** 버튼을 누르면 설치되었던 모드 파일이 말끔히 삭제되어 순정 상태로 돌아옵니다.

### 3) CLI 명령어로 사용하기 (파워 유저용)
```bash
# 게임 호환성 분석
python patcher.py analyze "E:\SteamLibrary\steamapps\common\House Flipper"

# 메이플스토리체 설치
python patcher.py install "E:\SteamLibrary\steamapps\common\House Flipper" --font maple

# 나눔바른고딕 설치
python patcher.py install "E:\SteamLibrary\steamapps\common\House Flipper" --font nanum

# 커스텀 폰트 파일 직접 지정 설치
python patcher.py install "E:\SteamLibrary\steamapps\common\House Flipper" --custom "C:\Fonts\MyFont.ttf"

# 패치 제거
python patcher.py uninstall "E:\SteamLibrary\steamapps\common\House Flipper"
```

---

## ⚙️ 상세 설정 커스터마이징

패치 설치 후 게임을 1회 실행하면 `BepInEx/config/UniversalKoreanFont.cfg` 파일이 생성됩니다:

```ini
[General]
## 굵은 폰트로 인식할 파일명/폰트명 키워드 (쉼표 구분)
BoldKeywords = bold,semibold,black,heavy,norse,title,header,heading

## 일반/가벼운 폰트로 인식할 키워드
LightKeywords = light,thin,regular,normal,book

## Fallback 대신 UI 요소의 font 필드를 무조건 강제로 덮어쓸지 여부 (기본: false)
OverrideDirectFont = false

## 씬 로드 후 폰트 자동 재점검 주기 (초)
CheckIntervalSeconds = 2.0

## 최대 재점검 횟수
MaxPeriodicChecks = 30

## 인게임 폰트 실시간 핫리로드 단축키 (기본: F10)
ReloadKey = F10
```

---

## 📄 기본 포함 폰트 라이선스 안내 (Font Licenses)

본 패처는 **배포 및 상업적/비상업적 이용에 법적 제약이 전혀 없는 100% 완전 오픈소스 글꼴(SIL Open Font License v1.1)**만을 기본 번들로 포함하고 있습니다.
(※ 메이플스토리체 등 제3자 재배포가 제한된 서체는 저작권 보호를 위해 기본 패키지에서 제외되었으며, 이용자가 직접 다운로드하여 [사용자 정의 폰트] 메뉴로 자유롭게 지정할 수 있습니다.)

### 1. 나눔바른고딕 (`NanumBarunGothic.ttf`, `NanumBarunGothicBold.ttf`)
- **저작권자**: 네이버 (NAVER Corp.) & 산돌커뮤니케이션 (Sandoll Communications)
- **라이선스**: **SIL Open Font License (OFL) v1.1**
- **특징**: 깔끔하고 반듯한 고딕 서체로 게임 내 UI 및 긴 대화창, 아이템 설명에 뛰어난 가독성을 제공합니다. (굵은 글씨 / 일반 글씨 자동 매핑)
- **이용 조건**: 오픈소스 라이선스로 개인 및 기업 사용자 모두에게 무료로 제공되며 자유롭게 사용, 번들링 및 재배포가 가능합니다.
- **공식 안내**: [네이버 글꼴 라이선스](https://hangeul.naver.com)

### 2. 나눔고딕 (`NanumGothic.ttf`, `NanumGothicBold.ttf`)
- **저작권자**: 네이버 (NAVER Corp.) & 폰트릭스 (Fontrix)
- **라이선스**: **SIL Open Font License (OFL) v1.1**
- **특징**: 부드럽고 친근한 둥근 획 끝 디자인이 적용된 대중적인 유니버설 한글 서체입니다.
- **이용 조건**: 오픈소스 라이선스로 개인 및 기업 사용자 모두에게 무료로 제공되며 자유롭게 사용, 번들링 및 재배포가 가능합니다.


---

## 🛠️ 개발자용 컴파일 방법

핵심 주입 플러그인(`UniversalFontPlugin.dll`)을 직접 수정하고 빌드하려면:
- Bash: `./build_plugin.sh`
- PowerShell: `.\build_plugin.ps1`
- 소스 코드: `src/UniversalFontPlugin.cs`

