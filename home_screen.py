import streamlit as st
from PIL import Image

from src.components.header import header_home
from src.ui.base_layout import style_base_layout, style_background_home


def home_screen():

    style_background_home()
    style_base_layout()
    header_home()

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.header("I am a Teacher")

        teacher_img = Image.open("src/components/teacher.png")
        teacher_img = teacher_img.resize((200, 150))
        st.image(teacher_img)

        if st.button('Teacher Portal'):
            st.session_state['login_type'] = 'teacher'
            st.rerun()

    with col2:
        st.header("I am a Student")

        student_img = Image.open("src/components/student.png")
        student_img = student_img.resize((200, 150))
        st.image(student_img)

        if st.button('Student Portal'):
            st.session_state['login_type'] = 'student'
            st.rerun()