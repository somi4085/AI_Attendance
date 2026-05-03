import streamlit as st
from src.database.db import create_subject

@st.dialog("Create New Subject")
def create_subject_dialog(teacher_id):

    st.write("Enter subject details")

    sub_id = st.text_input("Subject code", placeholder="CS101")
    sub_name = st.text_input("Subject name", placeholder="Intro to CS")
    sub_section = st.text_input("Section", placeholder="A")

    if st.button("Create Subject", type="primary"):

        if sub_id and sub_name and sub_section:
            try:
                create_subject(sub_id, sub_name, sub_section, teacher_id)
                st.success("Subject created successfully")
                st.rerun()

            except Exception as e:
                st.error(str(e))

        else:
            st.warning("Please fill all fields")
