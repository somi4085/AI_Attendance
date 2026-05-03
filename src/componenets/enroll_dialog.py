import streamlit as st

from src.database.db import create_subject
from src.database.config import supabase
from src.database.db import enroll_student_to_sub
import time
@st.dialog("Enroll in subject")
def enroll_dialog():

    st.write("Enter subject code provided by teacher to enroll")
    join_code = st.text_input('Subject code', placeholder='Eg. CS101')

    if st.button('Enroll Now', type='primary', use_container_width=True):

        if not join_code:
            st.warning("Please enter subject code")
            return

        res_data = supabase.table('subjects') \
            .select('subject_id, name, subject_code') \
            .eq('subject_code', join_code) \
            .execute()

        subjects = res_data.data

        if not subjects:
            st.error("Invalid subject code")
            return

        subject = subjects[0]
        student_id = st.session_state.student_data['student_id']

        check = supabase.table('subject_students') \
            .select("*") \
            .eq('subject_id', subject['subject_id']) \
            .eq('student_id', student_id) \
            .execute()

        if check.data:
            st.warning("Already enrolled")
        else:
            enroll_student_to_sub(student_id, subject['subject_id'])
            st.success("Successfully enrolled")
            time.sleep(1)
            st.rerun()