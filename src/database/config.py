import os

import streamlit as st
from supabase import create_client, Client


def _get_secret(name: str) -> str:
    # Render: environment variables. Local / Streamlit Cloud: st.secrets
    value = os.environ.get(name)
    if value:
        return value
    try:
        return st.secrets[name]
    except Exception:
        raise RuntimeError(
            f"Missing {name}. Add it as an environment variable in Render."
        )


supabase: Client = create_client(
    _get_secret("SUPABASE_URL"),
    _get_secret("SUPABASE_KEY"),
)
