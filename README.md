# 학교축제 방문자 사전 등록 앱 — 일반 Google 계정 Sheets 방식

## 핵심 구조
Streamlit(Python) → Apps Script 웹앱 → 담당자 개인 Google Sheets

Google Cloud 서비스 계정, JSON 키, gspread 인증은 사용하지 않습니다.
Apps Script 웹앱이 소유자 권한으로 실행되어 소유자의 스프레드시트에 행을 추가합니다.

## A. Google Sheets 준비
1. 담당자 개인 Google 계정으로 새 Google 스프레드시트를 만듭니다.
2. 스프레드시트에서 `확장 프로그램` → `Apps Script`를 엽니다.
3. 이 프로젝트의 `Code.gs` 내용을 Apps Script 편집기에 붙여 넣습니다.
4. `setApiKey()` 안의 예시 문자열을 충분히 길고 무작위인 비밀키로 바꿉니다.
5. 저장한 다음 함수 선택 메뉴에서 `setApiKey`를 선택하고 실행합니다.
6. 첫 실행 시 Google 계정 권한 승인 화면이 나타나면 본인 계정으로 승인합니다.

## B. Apps Script 웹앱 배포
1. Apps Script 오른쪽 위 `배포` → `새 배포`
2. 유형 선택(톱니/유형 선택) → `웹 앱`
3. 다음 사용자 권한으로 실행: **나**
4. 액세스 권한: 공개 방문자 등록이 필요하면 **모든 사용자(Anyone)** 를 선택합니다.
   - 계정/학교 Workspace 관리자 정책에 따라 이 옵션이 없을 수 있습니다.
   - 학교 내부 사용자만 허용할 경우 조직 정책에 맞는 접근 옵션을 선택하세요.
5. 배포를 누르고 권한을 승인합니다.
6. 생성된 웹 앱 URL 중 `/exec`로 끝나는 URL을 복사합니다.

주의: Anyone으로 배포하면 웹 앱 URL을 아는 누구나 요청을 보낼 수 있는 공개 엔드포인트가 됩니다.
API_KEY를 강력하게 설정하고 외부에 노출하지 마세요. API_KEY는 GitHub 코드에 넣지 않습니다.

## C. GitHub에 올릴 파일
다음 파일을 GitHub 저장소에 업로드합니다.
- `app.py`
- `requirements.txt`
- `.gitignore`
- `Code.gs` (Apps Script 편집기에 복사할 원본 백업)

`.streamlit/secrets.toml`은 GitHub에 올리지 않습니다.
실제 Streamlit Secrets는 Streamlit Cloud의 앱 설정에서 등록합니다.

## D. Streamlit Community Cloud Secrets
1. https://share.streamlit.io 에서 GitHub 저장소를 연결합니다.
2. Main file path는 `app.py`로 지정합니다.
3. 앱의 Settings → Secrets에 아래 내용을 입력합니다.

```toml
apps_script_url = "https://script.google.com/macros/s/실제배포ID/exec"
apps_script_token = "Apps Script setApiKey에 입력한 동일한 비밀키"
```

4. 저장하고 앱을 배포/재시작합니다.

## E. 테스트
1. 배포된 Streamlit 앱에 테스트 데이터를 입력합니다.
2. 등록 버튼을 누릅니다.
3. QR코드가 화면에 뜨는지 확인합니다.
4. Google Sheets의 `방문자` 탭에 한 행이 추가되는지 확인합니다.

## 저장 열
등록번호 | 학교 | 학번 | 이름 | 연락처 | 방문 목적 | 등록 일시

QR코드에는 무작위 등록 토큰만 포함하며 개인정보는 포함하지 않습니다.
이 버전은 등록과 QR 발급까지 구현합니다. QR 스캔 체크인/중복 입장 차단은 다음 기능으로 별도 추가해야 합니다.

## 개인정보 및 보안
- 실제 학교 운영 전 개인정보 수집·이용의 법적 근거, 고지/동의, 보유기간 및 파기 방법을 학교 담당자와 확인하세요.
- 수집 항목을 최소화하고 Google Sheet 공유 권한을 필요한 담당자로 제한하세요.
- Streamlit Secrets와 Apps Script API_KEY를 GitHub에 올리지 마세요.
- Apps Script 실행자 계정의 소유자가 퇴직하거나 계정이 정지되면 서비스가 중단될 수 있으므로 학교가 관리하는 계정 사용을 권장합니다.
- 공개 웹앱의 악용을 줄이기 위해 QR 등록 URL을 외부에 무분별하게 공유하지 말고, 실제 행사 전 부하/중복 요청/네트워크 장애를 시험하세요.
