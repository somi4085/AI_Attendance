import streamlit as st
from src.UI.base_layout import style_background_dashboard, style_base_layout
from src.componenets.header import header_dashboard
from src.componenets.footer import footer_dashboard
from PIL import Image
from src.pipeline.face_pipeline import (
    predict_attendance,
    train_classifier,
    get_face_embedding
)
from src.pipeline.voice_pipeline import get_voice_embeddings
from src.database.db import get_all_students, create_student, get_student_subject, get_student_attendance,unenroll_student_to_sub
from src.componenets.enroll_dialog import enroll_dialog
from src.componenets.subject_card import subject_card
import numpy as np
import time



# ---------------- DASHBOARD ----------------
def student_dashboard():

    student_data = st.session_state.student_data
    student_id = student_data['student_id']

    c1, c2 = st.columns(2, vertical_alignment="center")

    with c1:
        header_dashboard()

    with c2:
        st.subheader(f"Welcome {student_data    ['name']}")
        
        if st.button("Logout", use_container_width=True):
            st.session_state.is_logged_in = False
            st.session_state.student_data = None
            st.rerun()

    st.divider()

    c1,c2 = st.columns(2)
    with c1:
        st.header("Your Enroll Subjects")
    
    with c2:
        if st.button("Enroll in subjects", type="primary", width='stretch'):
            enroll_dialog()
    
    st.divider()

    with st.spinner("Loading your Subjects..."):
        subjects = get_student_subject(student_id)
        logs = get_student_attendance(student_id)

        stats_map = {}

        for log in logs:
            sid = log['student_id']

            if sid not in stats_map:
                stats_map[sid] = {"total":0, "attended":0}

            stats_map[sid]['total'] +=1
            if logs.get('is_present'):
                stats_map[sid]['attended'] +=1

        cols = st.columns(2)
        for i, sub_node in enumerate(subjects):
            sub = sub_node['subjects']
            sid = sub['subject_id']


            stats = stats_map.get(sid,{"total":0, "attended":0})
            def unenroll_btn():
                if st.button(
                    "unenroll from this course",
                    type="tertiary",
                    use_container_width=True,
                    key=f"unenroll_{sid}"
                    ):
                    unenroll_student_to_sub(student_id, sid)
                    st.rerun()
            with cols[i % 2]:
                subject_card(
                    name=sub['name'],
                    code=sub['subject_code'],
                    section=sub['section'],
                    stats=[
                        {"icon": "📅", "label": "Total", "value": stats['total']},
                        {"icon": "✅", "label": "Attended", "value": stats['attended']},
                        ],
                        footer_callback=unenroll_btn
                        )
                
    footer_dashboard()


# ---------------- MAIN SCREEN ----------------
def student_screen():
    style_background_dashboard()
    style_base_layout()

    # if already logged in
    if "student_data" in st.session_state and st.session_state.student_data:
        student_dashboard()
        return

    c1, c2 = st.columns(2, vertical_alignment="center")

    with c1:
        header_dashboard()

    with c2:
        if st.button("Go back to home", key="student_back_btn"):
            st.session_state.student_data = None
            st.session_state.is_logged_in = False
            st.rerun()

    st.header("Student Face Login", text_alignment="center")
    st.write("")
    st.write("")

    show_registration = True

    photo_source = st.camera_input("📷 Position your face in the center")

    # ---------------- FACE LOGIN ----------------
    if photo_source:
        img = np.array(Image.open(photo_source))

        with st.spinner("AI is scanning your face..."):
            detected, all_ids, num_faces = predict_attendance(img)

        if num_faces == 0:
            st.warning("No face detected")

        elif num_faces > 1:
            st.warning("Multiple faces found")

        else:
            if detected:
                student_id = list(detected.keys())[0]

                all_students = get_all_students()

                student = next(
                    (s for s in all_students if s["student_id"] == student_id),
                    None
                )

                if student:
                    st.session_state.student_data = student
                    st.session_state.user_role = "student"
                    st.session_state.is_logged_in = True

                    st.toast(f"Welcome back {student['name']} 🎉")
                    time.sleep(1)
                    st.rerun()

            else:
                st.info("Face not recognized. Register as new student.")
                show_registration = True

    # ---------------- REGISTER NEW STUDENT ----------------
    if show_registration:
        with st.container(border=True):
            st.header("📝 Register New Student")

            new_name = st.text_input(
                "Enter your name",
                placeholder="Eg: Somi Singh"
            )

            st.subheader("🎤 Optional Voice Enrollment")
            st.info("Record your voice for voice-based attendance")

            audio_data = None

            try:
                audio_data = st.audio_input(
                    "Say: I am present, My name is ____"
                )
            except Exception:
                st.warning("Audio input not supported")

            if st.button("Create Account", type="primary"):

                if not new_name:
                    st.warning("Please enter your name")
                    footer_dashboard()
                    return

                with st.spinner("Creating profile..."):

                    img = np.array(Image.open(photo_source))
                    encodings = get_face_embedding(img)

                    if not encodings:
                        st.error("Could not capture face properly")
                        footer_dashboard()
                        return

                    face_embd = encodings[0].tolist()

                    voice_embd = None

                    if audio_data:
                        voice_embd = get_voice_embeddings(
                            audio_data.read()
                        )
                        if voice_embd is not None:
                            voice_embd = list(voice_embd)

                    response_data = create_student(
                        new_name,
                        face_embd,
                        voice_embd
                    )

                    if response_data:
                        train_classifier()

                        st.session_state.student_data = response_data[0]
                        st.session_state.user_role = "student"
                        st.session_state.is_logged_in = True

                        st.toast(f"Profile created! Hi {new_name} 🎉")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Failed to create profile")

    footer_dashboard()