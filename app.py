import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="E-commerce Catalog Dashboard", layout="wide")

st.title("🛍️ E-commerce Product Management Dashboard")
st.write("A full-stack relational database catalog designed with FastAPI & Streamlit.")

# ==========================================
# SIDEBAR: LIVE DESK CLERK
# ==========================================
st.sidebar.header("📁 Product Categories")

categories_list = []
category_mapping = {}

try:
    cat_response = requests.get(f"{BACKEND_URL}/categories/")
    if cat_response.status_code == 200:
        raw_categories = cat_response.json()
        for category in raw_categories:
            st.sidebar.write(f"📁 {category.get('name')} (ID: {category.get('id')})")
            categories_list.append(category.get('name'))
            category_mapping[category.get('name')] = category.get('id')
except Exception:
    st.sidebar.error("🔌 Cannot connect to backend categories route.")

st.sidebar.markdown("---")
st.sidebar.header("👤 Registered Users")

users_list = []
user_mapping = {}

try:
    user_response = requests.get(f"{BACKEND_URL}/users/")
    if user_response.status_code == 200:
        for user in user_response.json():
            st.sidebar.write(f"👤 {user.get('username')} (ID: {user.get('id')})")
            users_list.append(user.get('username'))
            user_mapping[user.get('username')] = user.get('id')
except Exception:
    pass

# ==========================================
# MAIN INTERACTIVE SURFACE
# ==========================================
tab1, tab2, tab3 = st.tabs(["🏗️ Data Orchestration", "🛒 Live Catalog & Reviews", "❌ Safe Deletion Manager"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Add New Category")
        with st.form("create_category_form", clear_on_submit=True):
            new_cat_name = st.text_input("Category Name")
            submit_cat = st.form_submit_button("Save Category")
            if submit_cat and new_cat_name.strip():
                try:
                    res = requests.post(f"{BACKEND_URL}/categories/", json={"name": new_cat_name.strip()})
                    if res.status_code == 200:
                        st.success(f"Added '{new_cat_name}'")
                        st.rerun()
                    else:
                        st.error(res.json().get('detail', 'Error saving category'))
                except Exception:
                    st.error("Backend offline.")

        st.subheader("Register New User")
        with st.form("create_user_form", clear_on_submit=True):
            uname = st.text_input("Username")
            uemail = st.text_input("Email")
            submit_user = st.form_submit_button("Register User")
            if submit_user and uname.strip() and uemail.strip():
                try:
                    # Defensive fallback: try plural '/users/', fallback to singular '/User/' if needed
                    res = requests.post(f"{BACKEND_URL}/users/", json={"username": uname.strip(), "email": uemail.strip()})
                    if res.status_code == 404:
                        res = requests.post(f"{BACKEND_URL}/User/", json={"username": uname.strip(), "email": uemail.strip()})
                    
                    if res.status_code == 200:
                        st.success(f"Registered '{uname}'")
                        st.rerun()
                    else:
                        st.error(res.json().get('detail', 'Error registering user'))
                except Exception:
                    st.error("Backend offline.")

    with col2:
        st.subheader("Add New Product")
        if not categories_list:
            st.info("Create a category first.")
        else:
            with st.form("create_product_form", clear_on_submit=True):
                pname = st.text_input("Product Name")
                pprice = st.number_input("Price ($)", min_value=0.01, step=0.01)
                pdesc = st.text_area("Description")
                pcat = st.selectbox("Select Category", options=categories_list)
                submit_prod = st.form_submit_button("Save Product")
                if submit_prod and pname.strip():
                    payload = {"name": pname.strip(), "price": pprice, "description": pdesc.strip(), "category_id": category_mapping[pcat]}
                    try:
                        res = requests.post(f"{BACKEND_URL}/products/", json=payload)
                        if res.status_code == 200:
                            st.success(f"Saved product '{pname}'")
                        else:
                            st.error(res.json().get('detail', 'Error saving product'))
                    except Exception:
                        st.error("Backend offline.")

        st.subheader("Submit Product Review")
        products_list = []
        product_mapping = {}
        try:
            p_fetch = requests.get(f"{BACKEND_URL}/products/")
            if p_fetch.status_code == 200:
                for p in p_fetch.json():
                    products_list.append(p.get('name'))
                    product_mapping[p.get('name')] = p.get('id')
        except Exception:
            pass

        if not products_list or not users_list:
            st.info("Ensure you have at least one product and one user to leave reviews.")
        else:
            with st.form("create_review_form", clear_on_submit=True):
                r_prod = st.selectbox("Select Product", options=products_list)
                r_user = st.selectbox("Select User", options=users_list)
                r_rating = st.slider("Rating", 1, 5, 5)
                r_comment = st.text_area("Comment")
                submit_rev = st.form_submit_button("Submit Review")
                if submit_rev:
                    payload = {"rating": r_rating, "comment": r_comment.strip(), "product_id": product_mapping[r_prod], "user_id": user_mapping[r_user]}
                    try:
                        res = requests.post(f"{BACKEND_URL}/reviews/", json=payload)
                        if res.status_code == 200:
                            st.success("Review recorded!")
                        else:
                            st.error(res.json().get('detail', 'Error saving review'))
                    except Exception:
                        st.error("Backend offline.")

with tab2:
    st.header("🛒 Live Product Catalog")
    try:
        prod_response = requests.get(f"{BACKEND_URL}/products/")
        if prod_response.status_code == 200:
            products_data = prod_response.json()
            if not products_data:
                st.info("No products currently in inventory.")
            else:
                product_options = {f"{p.get('name')} (${p.get('price'):.2f})": p.get('id') for p in products_data}
                selected_label = st.selectbox("Select a product to view details:", options=list(product_options.keys()))
                p_id = product_options[selected_label]
                
                detail_response = requests.get(f"{BACKEND_URL}/products/{p_id}/")
                if detail_response.status_code == 404 or detail_response.status_code == 405:
                    detail_response = requests.get(f"{BACKEND_URL}/products/{p_id}")
                
                if detail_response.status_code == 200:
                    p_data = detail_response.json()
                    c1, c2 = st.columns(2)
                    with c1:
                        st.metric(label="Product Name", value=p_data.get("name", "N/A"))
                        st.write(f"**Description:** {p_data.get('description', 'None')}")
                    with c2:
                        st.metric(label="Price", value=f"${p_data.get('price', 0.0):.2f}")
                        
                        # CRITICAL DEFENSIVE CHECK: Prevents KeyError if backend isn't nesting
                        category_obj = p_data.get("category")
                        if isinstance(category_obj, dict):
                            st.success(f"📁 **Category:** {category_obj.get('name', 'N/A')}")
                        else:
                            st.warning(f"📁 **Category ID:** {p_data.get('category_id', 'N/A')} (Fix backend to view name)")
                    
                    st.subheader("💬 Customer Reviews")
                    reviews = p_data.get("reviews", [])
                    if not reviews:
                        st.info("No reviews for this product yet.")
                    else:
                        for r in reviews:
                            with st.chat_message("user"):
                                st.write(f"⭐ **Rating:** {r.get('rating')}/5")
                                st.write(r.get('comment', '*No text comment*'))
                else:
                    st.error(f"Backend returned code {detail_response.status_code} on detail view.")
        else:
            st.error("Failed to load catalog inventory.")
    except Exception:
        st.error("Backend server unreachable.")

with tab3:
    st.header("❌ Safe Deletion Manager")
    st.write("Secure parent-node restriction panel.")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Delete Category")
        if categories_list:
            del_cat = st.selectbox("Select Category", options=categories_list, key="dc")
            if st.button("Delete Category", type="primary"):
                try:
                    res = requests.delete(f"{BACKEND_URL}/categories/{category_mapping[del_cat]}/")
                    if res.status_code == 200:
                        st.success("Deleted!"); st.rerun()
                    else:
                        st.error(res.json().get('detail', 'Could not delete.'))
                except Exception: st.error("Offline.")
                
    with col2:
        st.subheader("Delete User")
        if users_list:
            del_usr = st.selectbox("Select User", options=users_list, key="du")
            if st.button("Delete User", type="primary"):
                try:
                    res = requests.delete(f"{BACKEND_URL}/users/{user_mapping[del_usr]}/")
                    if res.status_code == 200:
                        st.success("Deleted!"); st.rerun()
                    else:
                        st.error(res.json().get('detail', 'Could not delete.'))
                except Exception: st.error("Offline.")
                
    with col3:
        st.subheader("Delete Product")
        if 'products_data' in locals() and products_data:
            del_p_opts = {p.get('name'): p.get('id') for p in products_data}
            del_prod = st.selectbox("Select Product", options=list(del_p_opts.keys()), key="dp")
            if st.button("Delete Product", type="primary"):
                try:
                    res = requests.delete(f"{BACKEND_URL}/products/{del_p_opts[del_prod]}/")
                    if res.status_code == 200:
                        st.success("Deleted!"); st.rerun()
                    else:
                        st.error(res.json().get('detail', 'Could not delete.'))
                except Exception: st.error("Offline.")
        else:
            st.info("No products present.")