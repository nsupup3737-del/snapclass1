import streamlit as st


def header_home():
    st.markdown(
        """
        <div style="text-align:center; padding:20px 0;">
            <h1 style="margin:0; font-size:3rem;">📸 SnapClass</h1>
            <p style="margin:5px 0 0 0; color:#64748b; font-size:1.1rem;">
                Smart attendance using Face and Voice recognition
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def header_dashboard():
    st.markdown(
        """
        <div style="padding:10px 0;">
            <h1 style="margin:0;">📸 SnapClass</h1>
            <p style="margin:0; color:#64748b;">Attendance made simple</p>
        </div>
        """,
        unsafe_allow_html=True,
    )