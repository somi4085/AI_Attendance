import dlib
import numpy as np
import face_recognition_models
from sklearn.svm import SVC
import streamlit as st

from src.database.db import get_all_students


# ---------------- LOAD MODELS ----------------
@st.cache_resource
def load_dlib_model():
    detector = dlib.get_frontal_face_detector()

    sp = dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()
    )

    facerec = dlib.face_recognition_model_v1(
        face_recognition_models.face_recognition_model_location()
    )

    return detector, sp, facerec


# ---------------- FACE EMBEDDINGS ----------------
def get_face_embedding(image_np):
    detector, sp, facerec = load_dlib_model()

    faces = detector(image_np, 1)

    encodings = []

    for face in faces:
        shape = sp(image_np, face)

        desc = facerec.compute_face_descriptor(
            image_np,
            shape,
            1
        )

        encodings.append(np.array(desc, dtype=float))

    return encodings


# ---------------- TRAIN MODEL ----------------
@st.cache_resource
def get_trained_model():
    X = []
    y = []

    student_db = get_all_students()

    # FIXED ERROR HERE
    if not student_db:
        return None

    for student in student_db:

        # use correct column name
        embeddings = student.get("face_embedding")

        if embeddings:
            X.append(np.array(embeddings, dtype=float))
            y.append(student.get("student_id"))

    if len(X) == 0:
        return None

    clf = SVC(
        kernel="linear",
        probability=True,
        class_weight="balanced"
    )

    try:
        clf.fit(X, y)
    except ValueError:
        return None

    return {
        "clf": clf,
        "X": X,
        "y": y
    }


# ---------------- RETRAIN ----------------
def train_classifier():
    st.cache_resource.clear()
    model_data = get_trained_model()
    return bool(model_data)


# ---------------- PREDICT ----------------
def predict_attendance(class_image_np):
    encodings = get_face_embedding(class_image_np)

    detected_student = {}

    model_data = get_trained_model()

    if not model_data:
        return detected_student, [], len(encodings)

    clf = model_data["clf"]
    X_train = model_data["X"]
    y_train = model_data["y"]

    all_students = sorted(list(set(y_train)))

    for encoding in encodings:

        # if multiple students in DB
        if len(all_students) >= 2:
            predicted_id = int(
                clf.predict([encoding])[0]
            )
        else:
            predicted_id = int(all_students[0])

        student_embedding = X_train[
            y_train.index(predicted_id)
        ]

        score = np.linalg.norm(
            student_embedding - encoding
        )

        # threshold
        if score <= 0.6:
            detected_student[predicted_id] = True

    return detected_student, all_students, len(encodings)