import streamlit as st

from src.database.db import supabase


@st.dialog("Enroll in Subject")
def enroll_dialog():
    st.write("Enter the subject code provided by your teacher to enroll")

    student_id = st.session_state.student_data["student_id"]
    code = st.text_input("Subject Code", placeholder="e.g. CS100")

    if st.button("Enroll now", type="primary", width="stretch"):
        code = code.strip()

        if not code:
            st.warning("Please enter a subject code.")
            return

        try:
            # 1. find the subject (case-insensitive match on the code)
            found = (
                supabase.table("subjects")
                .select("*")
                .ilike("subject_code", code)
                .execute()
            )
            if not found.data:
                st.error(f"No subject found with code '{code}'.")
                return

            subject = found.data[0]
            subject_id = subject["subject_id"]

            # 2. already enrolled?
            existing = (
                supabase.table("subjects_students")
                .select("*")
                .eq("student_id", student_id)
                .eq("subject_id", subject_id)
                .execute()
            )
            if existing.data:
                st.warning("You are already enrolled in this subject.")
                return

            # 3. enroll
            result = (
                supabase.table("subjects_students")
                .insert({"student_id": student_id, "subject_id": subject_id})
                .execute()
            )
            if not result.data:
                st.error("Enrollment did not save. Check Supabase RLS policies.")
                return

            st.toast(f"Enrolled in {subject['name']}!")
            st.rerun()

        except Exception as e:
            print("ENROLL ERROR:", e)
            st.error(f"Enrollment failed: {e}")