import streamlit as st
import requests

# 1. The network coordinates where our FastAPI backend is running
BACKEND_URL = "http://127.0.0.1:8000"

st.title("E-commerce Product Management Dashboard")
st.write("Welcome! This frontend interacts with our FastAPI relational database backend.")

# ==========================================
# SIDEBAR: VIEW CATEGORIES
# ==========================================
st.sidebar.header("Product Categories")

# Fire a live HTTP GET request down the machine line into your FastAPI endpoint
try:
    response = requests.get(f"{BACKEND_URL}/categories/")
    
    if response.status_code == 200:
        categories = response.json()  # Unpack the list of categories sent by the API
        
        if not categories:
            st.sidebar.info("No categories found in database.")
        for category in categories:
            # Render each category name as a visual point in the sidebar layout
            st.sidebar.write(f"📁 {category['name']} (ID: {category['id']})")
    else:
        st.sidebar.error("Failed to load categories from backend.")
        
except requests.exceptions.ConnectionError:
    st.sidebar.error("🔌 Cannot connect to FastAPI backend. Is your Uvicorn server running?")
    

# MAIN PAGE: MANAGE CATEGORIES

st.header("Add New Categories")

# Create an isolated UI containment box for input fields
with st.form("create_category_form", clear_on_submit=True):
    new_category_name = st.text_input("Category Name", placeholder="e.g., Home & Kitchen, Books")
    submit_button = st.form_submit_button("Save Category")
    
    # This block executes ONLY when the user clicks the submission button
    if submit_button:
        if not new_category_name.strip():
            st.error("⚠️ Category name cannot be empty!")
        else:
            try:
                # Match the exact JSON structure your Pydantic CategoryCreate schema gatekeeper expects
                payload = {"name": new_category_name}
                post_response = requests.post(f"{BACKEND_URL}/categories/", json=payload)
                
                if post_response.status_code == 200:
                    st.success(f"🎉 Success! '{new_category_name}' has been written to the catalog.")
                    st.rerun()  # Instantly triggers a script reload so the sidebar list refreshes!
                elif post_response.status_code == 400:
                    # Capture and display our custom backend HTTPException error message
                    st.error(f"🛑 Backend Refusal: {post_response.json()['detail']}")
                else:
                    st.error("❌ Something went wrong on the server.")
                    
            except requests.exceptions.ConnectionError:
                st.error("🔌 Lost connection to the backend server.")