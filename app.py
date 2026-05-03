import streamlit as st
from src.screens.Home_screen import home_screen
from src.screens.Teacher_screen import teacher_screen
from src.screens.Student_screen import student_screen
from src.componenets.auto_enroll_dialog import auto_enroll_dialog
def main():
    if 'login_type' not in st.session_state:
        st.session_state['login_type'] = None

    match st.session_state['login_type']:
        case 'teacher':
            teacher_screen()
        case 'student':
            student_screen()
        case None:
            home_screen()

     # -------------------------
    join_code = st.query_params.get("join-code")

    if join_code:
        join_code = join_code[0]
        st.session_state.pending_join_code = join_code
        st.query_params.clear()
        st.rerun()

    # -------------------------
    # Trigger dialog safely
    # -------------------------
    if (
        st.session_state.get("is_logged_in")
        and st.session_state.get("user_role") == "student"
        and st.session_state.get("pending_join_code")
    ):
        auto_enroll_dialog(st.session_state.pending_join_code)

main()