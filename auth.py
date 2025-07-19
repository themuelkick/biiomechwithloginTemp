import streamlit as st
from supabase import create_client, Client
import os

@st.cache_resource
def get_supabase_client():
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets.get("SUPABASE_SERVICE_ROLE_KEY")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase_client()

# Add this at the top of the file
# Always get ADMIN_EMAILS as a list, even if provided as a comma-separated string in secrets
def get_admin_emails():
    emails = st.secrets.get("ADMIN_EMAILS", ["mmueller4@rogers.com"])
    if isinstance(emails, str):
        # Support comma-separated string
        emails = [e.strip() for e in emails.split(",") if e.strip()]
    return emails
ADMIN_EMAILS = get_admin_emails()

def is_admin(email):
    return email in ADMIN_EMAILS

if 'user' not in st.session_state:
    st.session_state.user = None
if 'profile' not in st.session_state:
    st.session_state.profile = {}

def login():
    st.subheader("Login")
    email = st.text_input("Email", key="login_email")
    pwd = st.text_input("Password", type="password", key="login_pwd")
    if st.button("Login"):
        try:
            # Query the profiles table for a matching email and password
            result = supabase.table("profiles").select("id, email, is_admin").eq("email", email).eq("password", pwd).execute()
            if result.data and len(result.data) > 0:
                user_profile = result.data[0]
                # If email is in ADMIN_EMAILS but is_admin is not True, update the profile
                if is_admin(email) and not user_profile.get("is_admin", False):
                    supabase.table("profiles").update({"is_admin": True}).eq("id", user_profile["id"]).execute()
                    user_profile["is_admin"] = True
                st.session_state.user = user_profile["id"]
                st.session_state.user_email = user_profile["email"]
                st.session_state.profile = {"is_admin": user_profile.get("is_admin", False)}
                st.success("✅ Logged in")
                st.rerun()
            else:
                st.error("❌ Login failed. Please check your credentials.")
        except Exception as e:
            st.error(f"❌ Login error: {e}")

def signup():
    st.subheader("Create Account")
    email = st.text_input("Email", key="su_email")
    pwd = st.text_input("Password", type="password", key="su_pwd")
    if st.button("Sign Up"):
        try:
            # Check if email already exists
            existing = supabase.table("profiles").select("id").eq("email", email).execute()
            if existing.data and len(existing.data) > 0:
                st.error("❌ Email already registered. Please log in or use another email.")
                return
            # Insert new profile with email and password
            import uuid
            user_id = str(uuid.uuid4())
            is_admin_value = is_admin(email)
            profile_data = {"id": user_id, "email": email, "password": pwd, "is_admin": is_admin_value}
            supabase.table("profiles").insert(profile_data).execute()
            st.success("✅ Account created successfully! You can now log in.")
        except Exception as e:
            st.error(f"❌ Sign-up error: {e}")

def auth_screen():
    st.title("Login Page")
    option = st.selectbox("Choose an Action:", ["Login", "Sign Up"])
    if option == "Login":
        login()
    else:
        signup()

def sign_out():
    supabase.auth.sign_out()
    st.session_state.user = None
    st.session_state.session = None
    st.session_state.user_email = None
    st.session_state.profile = {}
    st.rerun()

def main():
    auth_screen()

if __name__ == "__main__":
    main()









