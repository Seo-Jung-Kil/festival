import uuid
import re
from datetime import datetime
from io import BytesIO

import requests
import qrcode
import streamlit as st

st.set_page_config(page_title="학교축제 방문자 사전 등록", page_icon="🎪", layout="centered")

def create_qr_image(token: str):
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(token)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white")
    output = BytesIO()
    image.save(output, format="PNG")
    output.seek(0)
    return output

def valid_phone(phone: str) -> bool:
    digits = re.sub(r"\D", "", phone)
    return 9 <= len(digits) <= 11

st.title("🎪 학교축제 방문자 사전 등록")
st.write("학교, 학번, 이름, 연락처와 방문 목적을 입력해 주세요.")
st.info("QR코드에는 개인정보가 아닌 무작위 등록 토큰만 포함됩니다.")

with st.form("visitor_form"):
    school = st.text_input("학교", max_chars=80)
    student_id = st.text_input("학번", max_chars=20)
    name = st.text_input("이름", max_chars=40)
    phone = st.text_input("연락처", placeholder="010-1234-5678", max_chars=20)
    purpose = st.selectbox(
        "방문 목적",
        ["축제 관람", "학생·교직원 가족", "학교 관계자", "초청 및 업무", "기타"]
    )
    consent = st.checkbox("방문 등록 및 입장 확인을 위한 개인정보 수집·이용에 동의합니다.")
    submitted = st.form_submit_button("방문 등록 및 QR코드 발급", use_container_width=True)

if submitted:
    if not all([school.strip(), student_id.strip(), name.strip(), phone.strip()]):
        st.error("학교, 학번, 이름, 연락처를 모두 입력해 주세요.")
    elif not valid_phone(phone):
        st.error("연락처를 확인해 주세요. 숫자 기준 9~11자리로 입력해 주세요.")
    elif not consent:
        st.error("개인정보 수집·이용 동의가 필요합니다.")
    else:
        token = uuid.uuid4().hex
        payload = {
            "token": token,
            "school": school.strip(),
            "student_id": student_id.strip(),
            "name": name.strip(),
            "phone": phone.strip(),
            "purpose": purpose,
            "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "api_key": st.secrets["apps_script_token"],
        }
        try:
            response = requests.post(
                st.secrets["apps_script_url"],
                json=payload,
                timeout=30,
                allow_redirects=True,
            )
            response.raise_for_status()
            result = response.json()
            if result.get("ok") is True:
                st.session_state["registration_result"] = {
                    "token": token,
                    "school": school.strip(),
                    "name": name.strip(),
                    "registered_at": payload["registered_at"],
                }
                st.success("등록이 완료되었습니다. QR코드를 저장해 주세요.")
            else:
                st.error("등록이 처리되지 않았습니다. 관리자에게 문의해 주세요.")
        except Exception as exc:
            st.error("Google Sheets 저장에 실패했습니다. 잠시 후 다시 시도해 주세요.")
            st.caption(f"오류 유형: {type(exc).__name__}")

result = st.session_state.get("registration_result")
if result:
    st.divider()
    st.subheader("발급된 방문자 QR코드")
    st.write(f"**학교:** {result['school']}")
    st.write(f"**이름:** {result['name']}")
    st.write(f"**등록 일시:** {result['registered_at']}")
    qr = create_qr_image(result["token"])
    st.image(qr, width=280, caption="학교축제 방문 확인용 QR코드")
    st.download_button(
        "QR코드 이미지 다운로드",
        data=qr.getvalue(),
        file_name=f"festival_QR_{result['token'][:8]}.png",
        mime="image/png",
        use_container_width=True,
    )
    st.caption("QR코드는 방문자 본인만 보관하고 다른 사람에게 공유하지 마세요.")

st.divider()
st.caption("방문자 정보는 담당자의 일반 Google 계정으로 만든 Google 스프레드시트에 저장됩니다.")
