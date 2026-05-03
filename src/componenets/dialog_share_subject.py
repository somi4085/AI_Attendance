import streamlit as st
import segno
import io
@st.dialog("Share Class Link")
def share_subject_code(subject_name, subject_code):

    app_domain = "snapclass-mains.streamlit.app"

    join_url = f"{app_domain}/?join-code={subject_code}"   # FIXED

    st.header("Scan to join")

    qr = segno.make(join_url)

    out = io.BytesIO()
    qr.save(out, kind="png", scale=10, border=1)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Copy link")
        st.code(join_url)
        st.code(subject_code)
        st.info("Share this link via WhatsApp or Email")

    with col2:
        st.image(out.getvalue(), caption="QR Code", use_container_width=True)