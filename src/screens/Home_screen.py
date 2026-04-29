import streamlit as st
from src.componenets.header import home_header
from src.UI.base_layout import style_base_layout, style_background_home
from src.componenets.footer import footer_home
def home_screen():


    home_header()
    style_background_home()
    style_base_layout()
    col1,col2 = st.columns(2, gap="large")

    with col1:
        if st.button("Teacher portal", type="primary",icon=":material/arrow_outward:", icon_position="right"):
            st.session_state['login_type'] = 'teacher'
            st.rerun()
    with col2:
        if st.button("Student Portal", type="primary", icon=":material/arrow_outward:", icon_position="right"):
            st.session_state['login_type'] = 'student'
            st.rerun()
    footer_home()
    