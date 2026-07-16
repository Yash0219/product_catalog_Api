import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="E-commerce Dashboard", layout="wide")

st.title("🛍️ E-commerce Product Management Dashboard")
st.write("Welcome! This frontend interacts with our FastAPI relational database backend.")

# ==========================================
# SIDEBAR: LIVE RESOURCE DIRECTORY
# ==========================================
st.sidebar.header("📁 Product Categories")

categories_list = []
category_mapping = {}

try:
    cat_response = requests.get(f"{BACKEND_URL}/categories/")
    if cat_response.status_code == 200:
        raw_categories = cat_response.json()
        if not raw_categories:
            st.sidebar.info("No categories found.")
        for category in raw_categories:
            st.sidebar.write(f"📁 {category['name']} (ID: {category['id']})")
            categories_list.append(category["name"])
            category_mapping[category["name"]] = category["id"]
    else:
        st.sidebar.error("Failed to load categories.")
except requests.exceptions.ConnectionError:
    st.sidebar.error("🔌 Cannot connect to FastAPI backend. Is your Uvicorn server running?")

st.sidebar.markdown("---")
st.sidebar.header("👤 Registered Users")

users_list = []
user_mapping = {}

try:
    user_response = requests.get(f"{BACKEND_URL}/users/")
    if user_response.status_code == 200:
        raw_users = user_response.json()
        if not raw_users:
            st.sidebar.info("No users registered.")
        for user in raw_users:
            st.sidebar.write(f"👤 {user['username']} (ID: {user['id']})")
            users_list.append(user["username"])
            user_mapping[user["username"]] = user["id"]
    else:
        st.sidebar.error("Failed to load users.")
except requests.exceptions.ConnectionError:
    pass


# ==========================================
# MAIN INTERACTIVE TABBED INTERFACE
# ==========================================
tab1, tab2, tab3 = st.tabs(["🏗️ Create Content", "🛒 Live Catalog & Reviews", "❌ Deletion Manager"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Add New Categories")
        with st.form("create_category_form", clear_on_submit=True):
            new_category_name = st.text_input("Category Name", placeholder="e.g., Electronics, Books")
            submit_cat = st.form_submit_button("Save Category")
            
            if submit_cat:
                if not new_category_name.strip():
                    st.error("⚠️ Category name cannot be empty!")
                else:
                    # Clean lowercase URL handshake match
                    payload = {"name": new_category_name.strip()}
                    try:
                        post_response = requests.post(f"{BACKEND_URL}/categories/", json=payload)
                        if post_response.status_code == 200:
                            st.success(f"🎉 Success! Category '{new_category_name}' added.")
                            st.rerun()
                        elif post_response.status_code == 400:
                            st.error(f"🛑 Backend Refusal: {post_response.json()['detail']}")
                        else:
                            st.error(f"❌ Failed. Server code: {post_response.status_code}")
                    except requests.exceptions.ConnectionError:
                        st.error("🔌 Connection to backend server lost.")

        st.subheader("Register New User")
        with st.form("create_user_form", clear_on_submit=True):
            new_username = st.text_input("Username", placeholder="e.g., alex_gold")
            new_email = st.text_input("Email", placeholder="e.g., alex@email.com")
            submit_user = st.form_submit_button("Register User")
            
            if submit_user:
                if not new_username.strip() or not new_email.strip():
                    st.error("⚠️ Username and Email cannot be empty!")
                else:
                    payload = {"username": new_username.strip(), "email": new_email.strip()}
                    try:
                        post_response = requests.post(f"{BACKEND_URL}/users/", json=payload)
                        if post_response.status_code == 200:
                            st.success(f"🎉 Success! User '{new_username}' registered.")
                            st.rerun()
                        elif post_response.status_code == 400:
                            st.error(f"🛑 Backend Refusal: {post_response.json()['detail']}")
                        else:
                            st.error(f"❌ Error. Server code: {post_response.status_code}")
                    except requests.exceptions.ConnectionError:
                        st.error("🔌 Connection to backend server lost.")

    with col2:
        st.subheader("Add New Product")
        if not categories_list:
            st.info("⚠️ Please create at least one category before adding products.")
        else:
            with st.form("create_product_form", clear_on_submit=True):
                product_name = st.text_input("Product Name", placeholder="e.g., Gaming Mouse")
                # Prevents "$" symbol typing automatically by enforcing numeric float constraints
                product_price = st.number_input("Price ($)", min_value=0.01, step=0.01, format="%.2f")
                product_description = st.text_area("Product Description", placeholder="Optional details...")
                selected_category_name = st.selectbox("Select Category", options=categories_list)
                submit_product = st.form_submit_button("Save Product")
                
                if submit_product:
                    if not product_name.strip():
                        st.error("⚠️ Product name cannot be empty!")
                    else:
                        target_category_id = category_mapping[selected_category_name]
                        product_payload = {
                            "name": product_name.strip(),
                            "price": product_price,
                            "description": product_description.strip() if product_description.strip() else None,
                            "category_id": target_category_id
                        }
                        try:
                            product_response = requests.post(f"{BACKEND_URL}/products/", json=product_payload)
                            if product_response.status_code == 200:
                                st.success(f"📦 Success! Product '{product_name}' added.")
                            elif product_response.status_code == 400:
                                st.error(f"🛑 Backend Refusal: {product_response.json()['detail']}")
                            else:
                                st.error(f"❌ Failed. Server code: {product_response.status_code}")
                        except requests.exceptions.ConnectionError:
                            st.error("🔌 Connection to backend server lost.")

        st.subheader("Submit Product Review")
        products_list = []
        product_mapping = {}
        try:
            prod_fetch = requests.get(f"{BACKEND_URL}/products/")
            if prod_fetch.status_code == 200:
                for p in prod_fetch.json():
                    products_list.append(p["name"])
                    product_mapping[p["name"]] = p["id"]
        except requests.exceptions.ConnectionError:
            pass

        if not products_list:
            st.info("⚠️ Add a product before you can leave reviews.")
        elif not users_list:
            st.info("⚠️ Register a user before you can leave reviews.")
        else:
            with st.form("create_review_form", clear_on_submit=True):
                selected_prod = st.selectbox("Select Product to Review", options=products_list)
                selected_usr = st.selectbox("Reviewed By (Select User)", options=users_list)
                rating = st.slider("Rating Score (1-5)", min_value=1, max_value=5, value=5)
                comment = st.text_area("Review Comment", placeholder="What did you think of the item?")
                submit_review = st.form_submit_button("Submit Review")
                
                if submit_review:
                    review_payload = {
                        "rating": rating,
                        "comment": comment.strip() if comment.strip() else None,
                        "product_id": product_mapping[selected_prod],
                        "user_id": user_mapping[selected_usr]
                    }
                    try:
                        review_response = requests.post(f"{BACKEND_URL}/reviews/", json=review_payload)
                        if review_response.status_code == 200:
                            st.success("💬 Review added successfully!")
                        elif review_response.status_code == 400:
                            st.error(f"🛑 Backend Refusal: {review_response.json()['detail']}")
                        else:
                            st.error(f"❌ Failed to submit review. Server code: {review_response.status_code}")
                    except requests.exceptions.ConnectionError:
                        st.error("🔌 Connection to backend server lost.")


with tab2:
    st.header("🛒 Live Product Catalog")
    try:
        prod_response = requests.get(f"{BACKEND_URL}/products/")
        if prod_response.status_code == 200:
            products = prod_response.json()
            
            if not products:
                st.info("No products currently in inventory. Add a product above to get started!")
            else:
                product_options = {f"{p['name']} (${p['price']:.2f})": p["id"] for p in products}
                selected_product_label = st.selectbox("Select a product to view details & reviews:", options=list(product_options.keys()))
                product_id = product_options[selected_product_label]
                
                # Fetch detailed nested products with a synchronized trailing slash
                detail_response = requests.get(f"{BACKEND_URL}/products/{product_id}/")
                
                if detail_response.status_code == 200:
                    product_data = detail_response.json()
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(label="Product Name", value=product_data["name"])
                        st.write(f"**Description:** {product_data['description'] if product_data['description'] else 'No description provided.'}")
                    with col2:
                        st.metric(label="Price", value=f"${product_data['price']:.2f}")
                        st.success(f"📁 **Category:** {product_data['category']['name']} (ID: {product_data['category']['id']})")
                    
                    st.subheader("💬 Customer Reviews")
                    reviews = product_data.get("reviews", [])
                    
                    if not reviews:
                        st.info("No reviews for this product yet.")
                    else:
                        for review in reviews:
                            with st.chat_message("user"):
                                st.write(f"⭐ **Rating:** {review['rating']}/5")
                                st.write(f"📝 {review['comment'] if review['comment'] else '*No text comment left.*'}")
                                st.caption(f"Submitted by User ID: {review['user_id']}")
                else:
                    try:
                        error_detail = detail_response.json().get("detail", "Unknown Error")
                    except:
                        error_detail = detail_response.text
                        
                    st.error(f"❌ Backend Error Code: {detail_response.status_code}")
                    st.error(f"💬 Reason: {error_detail}")
        else:
            st.error("❌ Failed to pull product inventory.")
    except requests.exceptions.ConnectionError:
        st.error("🔌 Disconnected from backend server.")


with tab3:
    st.header("❌ Deletion Safe Manager")
    st.write("Remove records securely. Relational guards explicitly protect against deleting parent nodes that have children attached.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Delete Category")
        if not categories_list:
            st.info("No categories to delete.")
        else:
            selected_del_cat = st.selectbox("Select Category to Delete", options=categories_list, key="del_cat")
            if st.button("Delete Selected Category", type="primary"):
                cat_id = category_mapping[selected_del_cat]
                try:
                    del_response = requests.delete(f"{BACKEND_URL}/categories/{cat_id}/")
                    if del_response.status_code == 200:
                        st.success(f"Deleted Category ID: {cat_id} successfully!")
                        st.rerun()
                    else:
                        st.error(f"Error: {del_response.json().get('detail', 'Failed to delete')}")
                except requests.exceptions.ConnectionError:
                    st.error("🔌 Backend offline.")
                    
    with col2:
        st.subheader("Delete User")
        if not users_list:
            st.info("No users to delete.")
        else:
            selected_del_user = st.selectbox("Select User to Delete", options=users_list, key="del_user")
            if st.button("Delete Selected User", type="primary"):
                usr_id = user_mapping[selected_del_user]
                try:
                    del_response = requests.delete(f"{BACKEND_URL}/users/{usr_id}/")
                    if del_response.status_code == 200:
                        st.success(f"Deleted User ID: {usr_id} successfully!")
                        st.rerun()
                    else:
                        st.error(f"Error: {del_response.json().get('detail', 'Failed to delete')}")
                except requests.exceptions.ConnectionError:
                    st.error("🔌 Backend offline.")
                    
    with col3:
        st.subheader("Delete Product")
        del_products_options = {}
        try:
            prod_fetch = requests.get(f"{BACKEND_URL}/products/")
            if prod_fetch.status_code == 200:
                del_products_options = {p["name"]: p["id"] for p in prod_fetch.json()}
        except:
            pass
            
        if not del_products_options:
            st.info("No products to delete.")
        else:
            selected_del_prod = st.selectbox("Select Product to Delete", options=list(del_products_options.keys()), key="del_prod")
            if st.button("Delete Selected Product", type="primary"):
                p_id = del_products_options[selected_del_prod]
                try:
                    del_response = requests.delete(f"{BACKEND_URL}/products/{p_id}/")
                    if del_response.status_code == 200:
                        st.success(f"Deleted Product ID: {p_id} successfully!")
                        st.rerun()
                    else:
                        st.error(f"Error: {del_response.json().get('detail', 'Failed to delete')}")
                except requests.exceptions.ConnectionError:
                    st.error("🔌 Backend offline.")
                
    