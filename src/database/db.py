from src.database.config import supabase
import bcrypt


# ---------------- PASSWORD HELPERS ----------------
def hash_pass(pwd):
    return bcrypt.hashpw(
        pwd.encode(),
        bcrypt.gensalt()
    ).decode()


def check_pass(pwd, hashed):
    return bcrypt.checkpw(
        pwd.encode(),
        hashed.encode()
    )


# ---------------- TEACHER ----------------
def check_teacher_exists(username):
    response = (
        supabase.table("teachers")
        .select("username")
        .eq("username", username)
        .execute()
    )

    return len(response.data) > 0


def create_teacher(username, password, name):
    try:
        data = {
            "username": username,
            "password": hash_pass(password),
            "name": name
        }

        response = (
            supabase.table("teachers")
            .insert(data)
            .execute()
        )

        return response.data

    except Exception as e:
        print("Teacher Create Error:", e)
        return None


def teacher_login(username, password):
    try:
        response = (
            supabase.table("teachers")
            .select("*")
            .eq("username", username)
            .execute()
        )

        if response.data:

            teacher = response.data[0]

            if check_pass(
                password,
                teacher["password"]
            ):
                return True, teacher

        return False, None

    except Exception as e:
        print("Teacher Login Error:", e)
        return False, None


# ---------------- STUDENTS ----------------
def get_all_students():
    try:
        response = (
            supabase.table("students")
            .select("*")
            .execute()
        )

        return response.data

    except Exception as e:
        print("Get Students Error:", e)
        return []


def create_student(
    new_name,
    face_embedding=None,
    voice_embedding=None
):
    try:
        data = {
            "name": new_name,
            "face_embedding": face_embedding,
            "voice_embedding": voice_embedding
        }

        response = (
            supabase.table("students")
            .insert(data)
            .execute()
        )

        return response.data

    except Exception as e:
        print("Create Student Error:", e)
        return None


def create_subject(subject_code, name, section, teacher_id):
    data = {
        "subject_code": subject_code,
        "name": name,
        "section": section,
        "teacher_id": teacher_id
    }

    response = supabase.table("subjects").insert(data).execute()
    return response.data


def get_teacher_subjects(teacher_id):

    subjects = supabase.table("subjects") \
        .select("*") \
        .eq("teacher_id", teacher_id) \
        .execute().data

    for sub in subjects:

        students = supabase.table("subject_students") \
            .select("student_id") \
            .eq("subject_id", sub["subject_id"]) \
            .execute().data

        sub["total_students"] = len(students)
        sub["total_classes"] = 0

    return subjects


def enroll_student_to_sub(student_id, subject_id):
    data = {'student_id': student_id, 'subject_id':subject_id}
    response = supabase.table('subject_students').insert(data).execute()

    return response.data


def unenroll_student_to_sub(student_id, subject_id):
    data = {'student_id': student_id, 'subject_id':subject_id}
    response = supabase.table('subject_students').delete().eq('student_id',student_id).eq('student_id', student_id).execute()
    return response.data

def get_student_subject(student_id):
    response = supabase.table('subject_students').select("*, subjects(*)").eq('student_id',student_id).execute()
    return response.data


def get_student_attendance(student_id):
    response = supabase.table('attendance_log').select("*, subjects(*)").eq('student_id',student_id).execute()
    return response.data

def create_attendance(logs):
    response = supabase.table('attendance_log').insert(logs).execute()
    return response.data


def get_attendance_for_teacher(teacher_id):
    response = supabase.table("attendance_log").select("*,subjects!inner(*)").eq('subjects.teacher_id',teacher_id).execute()
    return response.data