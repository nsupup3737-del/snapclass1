import streamlit as st

from src.screens.home_screen import home_screen
from src.screens.student_screen import student_screen
from src.screens.teacher_screen import teacher_screen
from src.components.dialog_auto_enroll import auto_enroll_dialog


def main():
    # Must be the first Streamlit call
    st.set_page_config(
        page_title="SnapClass - Making Attendance faster using AI",
        page_icon="https://i.ibb.co/YTYGn5qV/logo.png",
    )

    if "login_type" not in st.session_state:
        st.session_state["login_type"] = None

    # Handle join links BEFORE rendering any screen
    join_code = st.query_params.get("join-code")
    if join_code and st.session_state.login_type != "student":
        st.session_state.login_type = "student"
        st.rerun()

    match st.session_state["login_type"]:
        case "teacher":
            teacher_screen()
        case "student":
            student_screen()
        case _:
            home_screen()

    # Auto-enroll once the student is logged in
    if (
        join_code
        and st.session_state.get("is_logged_in")
        and st.session_state.get("user_role") == "student"
    ):
        auto_enroll_dialog(join_code)


main()
