import streamlit as st
import time
import pandas as pd
import numpy as np

from datetime import datetime

from src.UI.base_layout import (
    style_background_dashboard,
    style_base_layout
)

from src.componenets.dialog_subject import create_subject_dialog
from src.componenets.header import header_dashboard
from src.componenets.footer import footer_dashboard
from src.componenets.subject_card import subject_card
from src.componenets.dialog_share_subject import share_subject_code
from src.componenets.add_photos_dialog import add_photos_dialog
from src.componenets.attendance_result_dialog import attendance_result_dialog
from src.componenets.voice_attendance_dialog import voice_attendance_dialog

from src.pipeline.face_pipeline import predict_attendance

from src.database.config import supabase
from src.database.db import (
    check_teacher_exists,
    create_teacher,
    teacher_login,
    get_teacher_subjects,
    get_attendance_for_teacher
)


# ---------------- MAIN SCREEN ----------------
def teacher_screen():
    style_background_dashboard()
    style_base_layout()

    if st.session_state.get("is_logged_in") and \
       st.session_state.get("user_role") == "teacher":
        teacher_dashboard()
        return

    if "teacher_login_type" not in st.session_state:
        st.session_state.teacher_login_type = "login"

    if st.session_state.teacher_login_type == "register":
        teacher_screen_register()
    else:
        teacher_screen_login()


# ---------------- LOGIN PAGE ----------------
def teacher_screen_login():

    c1, c2 = st.columns(2, vertical_alignment="center")

    with c1:
        header_dashboard()

    with c2:
        if st.button("Go back to home", key="login_back_btn"):
            st.session_state.teacher_login_type = None
            st.rerun()

    st.header("Login using password")

    teacher_username = st.text_input("Enter username").strip()
    teacher_password = st.text_input("Enter password", type="password").strip()

    st.divider()

    btn1, btn2 = st.columns(2)

    with btn1:
        if st.button("Login", use_container_width=True):
            success, teacher = teacher_login(
                teacher_username,
                teacher_password
            )

            if success:
                st.session_state.teacher_data = teacher
                st.session_state.user_role = "teacher"
                st.session_state.is_logged_in = True
                st.session_state.teacher_login_type = None
                st.session_state.login_type = "teacher"
                st.rerun()
            else:
                st.error("Invalid username/password")

    with btn2:
        if st.button(
            "Register Instead",
            type="primary",
            use_container_width=True
        ):
            st.session_state.teacher_login_type = "register"
            st.rerun()

    footer_dashboard()


# ---------------- REGISTER LOGIC ----------------
def register_teacher(username, name, password, confirm_password):

    if not username or not name or not password:
        return False, "All fields required"

    if check_teacher_exists(username):
        return False, "Username already exists"

    if password != confirm_password:
        return False, "Passwords do not match"

    if len(password) < 6:
        return False, "Password too short"

    try:
        create_teacher(username, password, name)
        return True, "Account created successfully"

    except Exception as e:
        return False, str(e)


# ---------------- REGISTER PAGE ----------------
def teacher_screen_register():

    c1, c2 = st.columns(2, vertical_alignment="center")

    with c1:
        header_dashboard()

    with c2:
        if st.button("Go back to home", key="register_back_btn"):
            st.session_state.teacher_login_type = None
            st.rerun()

    st.header("Register your teacher profile")

    teacher_username = st.text_input("Enter username").strip()
    teacher_name = st.text_input("Enter name").strip()
    teacher_pass = st.text_input("Enter password", type="password")
    teacher_pass_confirm = st.text_input("Confirm password", type="password")

    st.divider()

    btn1, btn2 = st.columns(2)

    with btn1:
        if st.button("Login instead", use_container_width=True):
            st.session_state.teacher_login_type = "login"
            st.rerun()

    with btn2:
        if st.button("Register", type="primary", use_container_width=True):

            success, message = register_teacher(
                teacher_username,
                teacher_name,
                teacher_pass,
                teacher_pass_confirm
            )

            if success:
                st.success(message)
                time.sleep(1)
                st.session_state.teacher_login_type = "login"
                st.rerun()
            else:
                st.error(message)

    footer_dashboard()


# ---------------- DASHBOARD ----------------
def teacher_dashboard():

    teacher = st.session_state.teacher_data

    c1, c2 = st.columns(2, vertical_alignment="center")

    with c1:
        header_dashboard()

    with c2:
        st.subheader(f"Welcome {teacher['name']}")

        if st.button("Logout", use_container_width=True):
            st.session_state.teacher_data = None
            st.session_state.user_role = None
            st.session_state.is_logged_in = False
            st.rerun()

    st.divider()
    st.header("Teacher Dashboard")

    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = "take_attendance"

    tab1, tab2, tab3 = st.columns(3)

    with tab1:
        btn_type = (
            "primary"
            if st.session_state.current_teacher_tab == "take_attendance"
            else "secondary"
        )

        if st.button(
            "Take Attendance",
            type=btn_type,
            use_container_width=True
        ):
            st.session_state.current_teacher_tab = "take_attendance"
            st.rerun()

    with tab2:
        btn_type = (
            "primary"
            if st.session_state.current_teacher_tab == "manage_subjects"
            else "secondary"
        )

        if st.button(
            "Manage Subjects",
            type=btn_type,
            use_container_width=True
        ):
            st.session_state.current_teacher_tab = "manage_subjects"
            st.rerun()

    with tab3:
        btn_type = (
            "primary"
            if st.session_state.current_teacher_tab == "attendance_records"
            else "secondary"
        )

        if st.button(
            "Attendance Records",
            type=btn_type,
            use_container_width=True
        ):
            st.session_state.current_teacher_tab = "attendance_records"
            st.rerun()

    st.divider()

    if st.session_state.current_teacher_tab == "take_attendance":
        teacher_tab_take_attendance()

    elif st.session_state.current_teacher_tab == "manage_subjects":
        teacher_tab_manage_subjects()

    elif st.session_state.current_teacher_tab == "attendance_records":
        teacher_tab_attendance_records()

    footer_dashboard()


# ---------------- TAKE ATTENDANCE ----------------
def teacher_tab_take_attendance():

    teacher_id = st.session_state.teacher_data["teacher_id"]
    st.header("Take AI Attendance")

    if "attendance_images" not in st.session_state:
        st.session_state.attendance_images = []

    subjects = get_teacher_subjects(teacher_id)

    if not subjects:
        st.warning("You haven't created any subjects.")
        return

    subject_options = {
        f"{s['name']} - {s['subject_id']}": s["subject_id"]
        for s in subjects
    }

    col1, col2 = st.columns([3, 1], vertical_alignment="bottom")

    with col1:
        selected_subject_label = st.selectbox(
            "Select Subject",
            options=list(subject_options.keys())
        )

    with col2:
        if st.button(
            "Add Photos",
            type="primary",
            icon=":material/photo_prints:",
            use_container_width=True
        ):
            add_photos_dialog()

    selected_subject_id = subject_options[selected_subject_label]

    st.divider()

    if st.session_state.attendance_images:
        st.subheader("Added Photos")

        cols = st.columns(4)

        for idx, img in enumerate(st.session_state.attendance_images):
            with cols[idx % 4]:
                st.image(
                    img,
                    use_container_width=True,
                    caption=f"Photo {idx + 1}"
                )

    has_photo = bool(st.session_state.attendance_images)

    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button(
            "Clear All Photos",
            type="primary",
            icon=":material/delete:",
            disabled=not has_photo,
            use_container_width=True
        ):
            st.session_state.attendance_images = []
            st.rerun()

    with c2:
        if st.button(
            "Run Face Analysis",
            type="secondary",
            icon=":material/analytics:",
            disabled=not has_photo,
            use_container_width=True
        ):
            with st.spinner("Deep scanning classroom photos..."):

                all_detected_id = {}

                for idx, img in enumerate(
                    st.session_state.attendance_images
                ):
                    img_np = np.array(img.convert("RGB"))

                    detected, _, _ = predict_attendance(img_np)

                    if detected:
                        for sid in detected.keys():
                            student_id = int(sid)

                            all_detected_id.setdefault(
                                student_id, []
                            ).append(f"Photo {idx + 1}")

                enrolled_res = (
                    supabase.table("subject_students")
                    .select("*, students(*)")
                    .eq("subject_id", selected_subject_id)
                    .execute()
                )

                enrolled_students = enrolled_res.data

                results = []
                attendance_to_log = []

                if not enrolled_students:
                    st.warning("No students enrolled.")

                else:
                    current_timestamp = datetime.now().strftime(
                        "%Y-%m-%dT%H:%M:%S"
                    )

                    for node in enrolled_students:

                        student = node["students"]

                        sources = all_detected_id.get(
                            int(student["student_id"]),
                            []
                        )

                        is_present = len(sources) > 0

                        results.append({
                            "Name": student["name"],
                            "ID": student["student_id"],
                            "Source": (
                                ", ".join(sources)
                                if is_present else "-"
                            ),
                            "Status": (
                                "✅ Present"
                                if is_present else "❌ Absent"
                            )
                        })

                        attendance_to_log.append({
                            "student_id": student["student_id"],
                            "subject_id": selected_subject_id,
                            "timestamp": current_timestamp,
                            "is_present": is_present
                        })

                    attendance_result_dialog(
                        pd.DataFrame(results),
                        attendance_to_log
                    )

    with c3:
        if st.button(
            "Use Voice Attendance",
            type="primary",
            icon=":material/mic:",
            use_container_width=True
        ):
            voice_attendance_dialog(selected_subject_id)


# ---------------- MANAGE SUBJECTS ----------------
def teacher_tab_manage_subjects():

    teacher_id = st.session_state.teacher_data["teacher_id"]

    st.header("Manage Subjects")

    if st.button("Create New Subject"):
        create_subject_dialog(teacher_id)

    subjects = get_teacher_subjects(teacher_id)

    if not subjects:
        st.info("No subjects found.")
        return

    for sub in subjects:

        stats = [
            {"icon": "👨‍🎓", "label": "Students", "value": 10},
            {"icon": "📘", "label": "Subjects", "value": 5},
        ]

        def share_btn(sub=sub):
            if st.button(
                f"Share Code: {sub['name']}",
                key=f"share_{sub['subject_code']}"
            ):
                share_subject_code(
                    sub["name"],
                    sub["subject_code"]
                )

        subject_card(
            name=sub["name"],
            code=sub["subject_code"],
            section=sub["section"],
            stats=stats,
            footer_callback=share_btn
        )


# ---------------- RECORDS ----------------
def teacher_tab_attendance_records():

    st.header("Attendance Records")

    teacher_id = st.session_state.teacher_data["teacher_id"]

    records = get_attendance_for_teacher(teacher_id)

    if not records:
        st.info("No records found.")
        return

    data = []

    for r in records:

        ts = r.get("timestamp")

        data.append({
            "ts_group": ts.split(".")[0] if ts else None,
            "Time": (
                datetime.fromisoformat(ts).strftime(
                    "%Y-%m-%d %I:%M %p"
                ) if ts else "N/A"
            ),
            "Subject": r["subjects"]["name"],
            "Subject Code": r["subjects"]["subject_code"],
            "is_present": bool(
                r.get("is_present", False)
            )
        })

    df = pd.DataFrame(data)

    summary = (
        df.groupby(
            [
                "ts_group",
                "Time",
                "Subject",
                "Subject Code"
            ]
        )
        .agg(
            Present_Count=("is_present", "sum"),
            Total_Count=("is_present", "count")
        )
        .reset_index()
    )

    summary["Attendance Stats"] = (
        "✅ "
        + summary["Present_Count"].astype(str)
        + " / "
        + summary["Total_Count"].astype(str)
        + " Students"
    )

    display_df = (
        summary.sort_values(
            by="ts_group",
            ascending=False
        )[
            [
                "Time",
                "Subject",
                "Subject Code",
                "Attendance Stats"
            ]
        ]
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

