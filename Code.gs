/**
 * Google Sheets에 연결된 Apps Script 코드입니다.
 * 스프레드시트에서 확장 프로그램 > Apps Script를 열어 붙여 넣으세요.
 *
 * 최초 1회 아래 함수 setApiKey()를 실행하고 API_KEY를 설정하세요.
 */
const SHEET_NAME = "방문자";

function setApiKey() {
  // 아래 문자열을 Streamlit Secrets의 apps_script_token 값과 동일하게 변경하세요.
  PropertiesService.getScriptProperties().setProperty(
    "API_KEY",
    "여기에_충분히_길고_무작위인_비밀키를_입력하세요"
  );
}

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents || "{}");
    const savedKey = PropertiesService.getScriptProperties().getProperty("API_KEY");

    if (!savedKey || data.api_key !== savedKey) {
      return jsonResponse({ ok: false, message: "unauthorized" });
    }

    const required = ["token", "school", "student_id", "name", "phone", "purpose", "registered_at"];
    for (const key of required) {
      if (!data[key] || String(data[key]).trim() === "") {
        return jsonResponse({ ok: false, message: "missing field: " + key });
      }
    }

    const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
    let sheet = spreadsheet.getSheetByName(SHEET_NAME);

    if (!sheet) {
      sheet = spreadsheet.insertSheet(SHEET_NAME);
    }

    if (sheet.getLastRow() === 0) {
      sheet.appendRow([
        "등록번호", "학교", "학번", "이름", "연락처", "방문 목적", "등록 일시"
      ]);
    }

    // 수식 삽입 방지를 위해 사용자 입력이 =, +, -, @ 로 시작하면 문자로 저장합니다.
    const safe = value => {
      const text = String(value);
      return /^[=+\-@]/.test(text) ? "'" + text : text;
    };

    sheet.appendRow([
      safe(data.token),
      safe(data.school),
      safe(data.student_id),
      safe(data.name),
      safe(data.phone),
      safe(data.purpose),
      safe(data.registered_at)
    ]);

    return jsonResponse({ ok: true });
  } catch (err) {
    return jsonResponse({ ok: false, message: "server_error" });
  }
}

function jsonResponse(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
