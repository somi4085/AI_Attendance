import streamlit as st

from src.database.db import enroll_student_to_sub
from src.database.config import supabase

import time

@st.dialog("Quick enrollment")
def auto_enroll_dialog(subject_code):
    if "student_data" not in st.session_state:
        st.error("User not logged in")
        return

    student_id = st.session_state.student_data['student_id']

    res = supabase.table('subjects') \
        .select('subject_id, name') \
        .eq('subject_code', subject_code) \
        .execute()

    if not res.data:
        st.error("Subject code not found")
        if st.button("Close", key="close_not_found"):
            st.query_params = {}
            st.rerun()
        return

    subject = res.data[0]

    check = supabase.table('subject_students') \
        .select("*") \
        .eq('subject_id', subject['subject_id']) \
        .eq('student_id', student_id) \
        .execute()

    if check.data:
        st.info("You are already enrolled")
        if st.button("Got it", key="already_enrolled_ok"):
            st.query_params = {}
            st.rerun()
        return

    st.markdown(f"Would you like to enroll in **{subject['name']}**?")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("No thanks", key="cancel_enroll"):
            st.query_params = {}
            st.rerun()

    with col2:
        if st.button("Yes enroll now", type="primary", key="confirm_enroll"):
            enroll_student_to_sub(student_id, subject['subject_id'])
            st.toast("Successfully joined")
            st.query_params = {}
            st.rerun()