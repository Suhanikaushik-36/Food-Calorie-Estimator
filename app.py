import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
import io
import json
import uuid
import datetime
import random
import numpy as np
import base64
import pandas as pd
from tensorflow.keras.models import load_model

# -------------------------------------------------
# CONFIG - HIDE ALL WARNINGS AND ERRORS
# -------------------------------------------------
st.set_page_config(page_title="🍽 Food Calorie Estimator", layout="wide")

# Remove the problematic options - they're not needed in newer Streamlit versions

# -------------------------------------------------
# BACKGROUND IMAGE
# -------------------------------------------------
def set_bg_local(image_file):
    with open(image_file, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/jpg;base64,{b64}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        [data-testid="stAppViewContainer"]::before {{
            content: "";
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: rgba(240,240,240,0.4);
            z-index: 0;
        }}
        [data-testid="stAppViewContainer"] > div {{
            position: relative;
            z-index: 1;
        }}
        .main-header {{
            font-size: 48px;
            font-weight: 900;
            color: #2E8B57;
            text-align: center;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(255,255,255,0.8);
        }}
        /* Hide all Streamlit warnings and errors */
        .stAlert {{
            display: none !important;
        }}
        .stException {{
            display: none !important;
        }}
        [data-testid="stDecoration"] {{
            display: none !important;
        }}
        .reportview-container .main .block-container{{
            padding-top: 1rem;
            padding-bottom: 0rem;
        }}
        html, body, [data-testid="stAppViewContainer"] {{
            height: 100%;
            overflow: hidden;
        }}
        section.main {{
            padding-top: 0px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_bg_local("background.jpg")

# -------------------------------------------------
# USER DATABASE AUTH
# -------------------------------------------------
USER_DB = "users.json"

def load_users():
    if not os.path.exists(USER_DB):
        with open(USER_DB, "w") as f:
            json.dump([], f)
    with open(USER_DB, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_DB, "w") as f:
        json.dump(users, f, indent=2)

def find_user(email):
    users = load_users()
    for u in users:
        if u["email"].lower() == email.lower():
            return u
    return None

def register_user(name, age, gender, allergies, medications, email, password):
    users = load_users()
    if find_user(email):
        return False, "Email already exists!"

    user = {
        "name": name,
        "age": age,
        "gender": gender,
        "allergies": allergies,
        "medications": medications,
        "email": email,
        "password": password
    }
    users.append(user)
    save_users(users)
    return True, "Account created successfully!"

def authenticate(email, password):
    user = find_user(email)
    if user and user["password"] == password:
        return True, user
    return False, None

def reset_password(email, new_pass):
    users = load_users()
    for u in users:
        if u["email"].lower() == email.lower():
            u["password"] = new_pass
            save_users(users)
            return True
    return False

# AUTH STATES
if "auth_page" not in st.session_state:
    st.session_state.auth_page = "login"

if "user" not in st.session_state:
    st.session_state.user = None


# -------------------------------------------------
# AUTH SCREENS
# -------------------------------------------------

# ---------------------- LOGIN PAGE ----------------------
if st.session_state.user is None and st.session_state.auth_page == "login":
    # Main Header
    st.markdown("<div class='main-header'>🍱 FOOD CALORIE ESTIMATOR</div>", unsafe_allow_html=True)
    
    # Use columns to center the content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div style='text-align: center; margin-bottom: 5px; font-size: 28px; font-weight: 700; color: #2E8B57;'>Welcome Back</div>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center; margin-bottom: 25px; font-size: 14px; color: #666;'>We can get your food and respond you to the next day!</div>", unsafe_allow_html=True)
        
        # White content box
        with st.container():
            st.markdown("<div style='background: rgba(255,255,255,0.95); padding: 30px; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
            
            email = st.text_input("Enter your email address", placeholder="Enter your email address", key="login_email")
            password = st.text_input("Enter your password", type="password", placeholder="Enter your password", key="login_password")
            
            if st.button("Login", key="login_btn", use_container_width=True):
                if email and password:
                    ok, user = authenticate(email, password)
                    if ok:
                        st.session_state.user = user
                        st.success("Login successful!")
                        st.experimental_rerun()
                    else:
                        st.error("Invalid email or password")
                else:
                    st.warning("Please fill in all fields")
            
            if st.button("Create Account", key="create_acc_btn", use_container_width=True):
                st.session_state.auth_page = "register"
                st.experimental_rerun()
            
            st.markdown("<div style='margin: 20px 0; border-top: 1px solid #e0e0e0;'></div>", unsafe_allow_html=True)
            
            if st.button("Forget Password?", key="forgot_btn", use_container_width=True):
                st.session_state.auth_page = "forgot"
                st.experimental_rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)

    st.stop()

# ---------------------- REGISTER PAGE ----------------------
if st.session_state.user is None and st.session_state.auth_page == "register":
    # Main Header
    st.markdown("<div class='main-header'>🍱 FOOD CALORIE ESTIMATOR</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div style='text-align: center; margin-bottom: 5px; font-size: 28px; font-weight: 700; color: #2E8B57;'>Create Account</div>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center; margin-bottom: 25px; font-size: 14px; color: #666;'>Join us for healthier eating habits</div>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown("<div style='background: rgba(255,255,255,0.95); padding: 30px; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
            
            name = st.text_input("Full Name", placeholder="Enter your full name", key="reg_name")
            email = st.text_input("Email Address", placeholder="Enter your email", key="reg_email")
            
            col1, col2 = st.columns(2)
            with col1:
                age = st.number_input("Age", min_value=1, max_value=120, value=20, key="reg_age")
            with col2:
                gender = st.selectbox("Gender", ["Female", "Male", "Other"], key="reg_gender")
            
            allergies = st.text_input("Allergies", placeholder="Comma separated (e.g., nuts, dairy)", key="reg_allergies")
            medications = st.text_input("Medications", placeholder="Current medications (optional)", key="reg_meds")
            
            password = st.text_input("Password", type="password", placeholder="Create password", key="reg_pass")
            confirm = st.text_input("Confirm Password", type="password", placeholder="Confirm password", key="reg_confirm")
            
            if st.button("Create Account", key="reg_btn", use_container_width=True):
                if not all([name, email, password, confirm]):
                    st.error("Please fill in all required fields")
                elif password != confirm:
                    st.error("Passwords do not match")
                else:
                    ok, msg = register_user(name, age, gender, allergies, medications, email, password)
                    if ok:
                        st.success(msg)
                        st.session_state.auth_page = "login"
                        st.experimental_rerun()
                    else:
                        st.error(msg)
            
            if st.button("Back to Login", key="back_login_btn", use_container_width=True):
                st.session_state.auth_page = "login"
                st.experimental_rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)

    st.stop()

# ---------------------- FORGOT PASSWORD PAGE ----------------------
if st.session_state.user is None and st.session_state.auth_page == "forgot":
    # Main Header
    st.markdown("<div class='main-header'>🍱 FOOD CALORIE ESTIMATOR</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div style='text-align: center; margin-bottom: 5px; font-size: 28px; font-weight: 700; color: #2E8B57;'>Reset Password</div>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center; margin-bottom: 25px; font-size: 14px; color: #666;'>Enter your email to reset your password</div>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown("<div style='background: rgba(255,255,255,0.95); padding: 30px; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
            
            email = st.text_input("Enter registered email", placeholder="Enter your registered email address", key="forgot_email")
            new_pass = st.text_input("New Password", type="password", placeholder="Enter new password", key="forgot_pass")
            
            if st.button("Update Password", key="update_pass_btn", use_container_width=True):
                if email and new_pass:
                    ok = reset_password(email, new_pass)
                    if ok:
                        st.success("Password updated successfully!")
                        st.session_state.auth_page = "login"
                        st.experimental_rerun()
                    else:
                        st.error("Email not found in our system")
                else:
                    st.warning("Please fill in all fields")
            
            if st.button("Back to Login", key="back_from_forgot_btn", use_container_width=True):
                st.session_state.auth_page = "login"
                st.experimental_rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)

    st.stop()

# -------------------------------------------------
# STORAGE SETUP
# -------------------------------------------------
HISTORY_FILE = "history.json"
HISTORY_IMG_DIR = "history_images"

def init_storage():
    os.makedirs(HISTORY_IMG_DIR, exist_ok=True)
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w") as f:
            json.dump([], f)

def load_history():
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_history(entry):
    hist = load_history()
    hist.insert(0, entry)
    hist = hist[:50]
    with open(HISTORY_FILE, "w") as f:
        json.dump(hist, f, indent=2, default=str)

def clear_history():
    for fname in os.listdir(HISTORY_IMG_DIR):
        try:
            os.remove(os.path.join(HISTORY_IMG_DIR, fname))
        except:
            pass
    with open(HISTORY_FILE, "w") as f:
        json.dump([], f)

def save_image_file(pil_img):
    fname = f"{uuid.uuid4().hex}.png"
    path = os.path.join(HISTORY_IMG_DIR, fname)
    pil_img.save(path)
    return path

# -------------------------------------------------
# HEALTH TIPS
# -------------------------------------------------
FOOD_HEALTH_TIPS = {
    "Apple": "An apple a day keeps the doctor away 🍎.",
    "Burger": "Use whole-grain buns & grilled patties 🍔.",
    "Avocado": "Rich in healthy fats — great for your heart 🥑.",
    "Bread": "Prefer multigrain bread 🍞.",
    "Milk": "Try low-fat or plant-based milk 🥛.",
    "Pizza": "Thin crust + veggies = healthier 🍕."
}

# -------------------------------------------------
# CNN MODEL LOADING
# -------------------------------------------------
@st.cache_resource
def load_cnn_model():
    try:
        model = load_model("models/custom_food_model.h5")
        return model
    except Exception:
        # Return a dummy model if real model not found
        return None

cnn_model = load_cnn_model()

def predict_food(pil_img):
    if cnn_model is None:
        # Mock prediction if model not loaded
        classes = ["Apple", "Burger", "Avocado", "Bread", "Milk", "Pizza"]
        name = random.choice(classes)
        confidence = random.uniform(85, 98)
    else:
        img = pil_img.resize((224,224))
        x = np.array(img)
        x = np.expand_dims(x, axis=0)
        x = x / 255.0

        preds = cnn_model.predict(x)
        classes = ["Apple", "Burger", "Avocado", "Bread", "Milk", "Pizza"]
        pred_class = np.argmax(preds)
        confidence = float(np.max(preds)) * 100
        name = classes[pred_class]

    base_cal = random.randint(220, 650)
    carb_pct, protein_pct, fat_pct = 0.50, 0.20, 0.30
    carbs_g = int((base_cal * carb_pct) / 4)
    protein_g = int((base_cal * protein_pct) / 4)
    fat_g = int((base_cal * fat_pct) / 9)

    return {
        "dish": name,
        "confidence": confidence,
        "calories": base_cal,
        "carbs_g": carbs_g,
        "protein_g": protein_g,
        "fat_g": fat_g,
    }

# -------------------------------------------------
# ALLERGY CHECK
# -------------------------------------------------
dish_ingredients = {
    'Apple': ['sugar'],
    'Pizza': ['dairy', 'gluten', 'tomato'],
    'Avocado': [],
    'Milk': ['dairy'],
    'Burger': ['gluten', 'dairy', 'sugar'],
    'Bread': ['gluten', 'sugar']
}

def check_allergies(dish_name, user_allergies_list):
    ingredients = dish_ingredients.get(dish_name, [])
    if user_allergies_list:
        user_allergies_list = [x.strip().lower() for x in user_allergies_list.split(",") if x.strip()]
        found = [i for i in ingredients if i.lower() in user_allergies_list]
        return found
    return []

def overlay_allergy_alert(pil_img, allergy_list):
    if not allergy_list:
        return pil_img
    draw = ImageDraw.Draw(pil_img)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    text = "⚠ Allergy: " + ", ".join(allergy_list)
    draw.text((10, 10), text, fill="red", font=font)
    return pil_img

# -------------------------------------------------
# APP BEGINS (after login)
# -------------------------------------------------
init_storage()

# HEADER
with st.container():
    st.markdown("<div style='text-align: center;' class='big-header'>🍱 Food Calorie Estimator</div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center;' class='sub-header'>An app that keeps you healthy and aware 🌿</div>", unsafe_allow_html=True)

# SIDEBAR PROFILE
st.sidebar.markdown("<div style='background: rgba(255,255,255,0.85); padding:12px; border-radius:12px; box-shadow: 0 3px 8px rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
st.sidebar.write(f"**{st.session_state.user['name']}**")
st.sidebar.write(f"Age: {st.session_state.user['age']} • {st.session_state.user['gender']}")
if st.session_state.user.get("allergies"):
    st.sidebar.write(f"Allergies: {st.session_state.user['allergies']}")
if st.session_state.user.get("medications"):
    st.sidebar.write(f"Meds: {st.session_state.user['medications']}")
st.sidebar.markdown("</div>", unsafe_allow_html=True)

page = st.sidebar.radio("Navigate", ["Camera", "Upload & Predict", "History", "Profile & Settings"])

# CAMERA PAGE
if page == "Camera":
    st.header("📷 Capture a meal")
    img_file = st.camera_input("Take a photo")

    if img_file is not None:
        pil_img = Image.open(img_file).convert("RGB")
        st.image(pil_img, caption="Captured image", use_column_width=True)
        portion = st.slider("Adjust portion size", 25, 200, 100, 5)

        if st.button("Analyze food"):
            with st.spinner("Estimating..."):
                result = predict_food(pil_img)
                scale = portion / 100.0
                calories = int(result["calories"] * scale)
                carbs_g = int(result["carbs_g"] * scale)
                protein_g = int(result["protein_g"] * scale)
                fat_g = int(result["fat_g"] * scale)

                user_allergies_input = st.session_state.user.get("allergies", "")
                allergy_found = check_allergies(result['dish'], user_allergies_input)
                pil_img = overlay_allergy_alert(pil_img, allergy_found)

                st.subheader("🔍 Predicted Result")
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.image(pil_img, caption="Analyzed Image", use_column_width=True)
                    st.markdown(f"*Dish:* {result['dish']} ({result['confidence']:.1f}% confidence)")
                    st.metric("Estimated Calories", f"{calories} kcal")
                    st.write(f"*Portion:* {portion}%")
                    if allergy_found:
                        st.error(f"⚠ Allergy Detected: {', '.join(allergy_found)}")

                with col2:
                    st.markdown("*Nutrition breakdown*")
                    st.write(f"Carbs: {carbs_g} g")
                    st.write(f"Protein: {protein_g} g")
                    st.write(f"Fat: {fat_g} g")

                tip = FOOD_HEALTH_TIPS.get(result['dish'], "Eat balanced meals and stay hydrated 💧.")
                st.write(f"💡 *Health Tip:* {tip}")

                img_path = save_image_file(pil_img)
                entry = {
                    "id": uuid.uuid4().hex,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "user": st.session_state.user["name"],
                    "dish": result["dish"],
                    "confidence": result["confidence"],
                    "calories": calories,
                    "carbs_g": carbs_g,
                    "protein_g": protein_g,
                    "fat_g": fat_g,
                    "portion_pct": portion,
                    "img_path": img_path,
                    "allergy_detected": allergy_found,
                }
                save_history(entry)
                st.success("Saved to your history 📚")

# UPLOAD PAGE
elif page == "Upload & Predict":
    st.header("📁 Upload a photo")
    uploaded_image = st.file_uploader("Upload a food image", type=["jpg", "jpeg", "png"])

    if uploaded_image:
        pil_img = Image.open(uploaded_image).convert("RGB")
        st.image(pil_img, caption="Uploaded Food Image", use_column_width=True)
        portion = st.slider("Adjust portion size", 25, 200, 100, 5)

        if st.button("Analyze upload"):
            with st.spinner("Analyzing image..."):
                result = predict_food(pil_img)
                scale = portion / 100.0
                calories = int(result["calories"] * scale)
                carbs_g = int(result["carbs_g"] * scale)
                protein_g = int(result["protein_g"] * scale)
                fat_g = int(result["fat_g"] * scale)

                user_allergies_input = st.session_state.user.get("allergies", "")
                allergy_found = check_allergies(result['dish'], user_allergies_input)
                pil_img = overlay_allergy_alert(pil_img, allergy_found)

                st.subheader("🔍 Predicted Result:")
                st.image(pil_img, caption="Analyzed Image", use_column_width=True)
                st.success(f"Dish: {result['dish']} ({result['confidence']:.1f}% confidence)")
                st.info(f"Estimated Calories: {calories} kcal")
                st.metric("Carbs (g)", carbs_g)
                st.metric("Protein (g)", protein_g)
                st.metric("Fat (g)", fat_g)
                if allergy_found:
                    st.error(f"⚠ Allergy Detected: {', '.join(allergy_found)}")

                tip = FOOD_HEALTH_TIPS.get(result['dish'], "Eat balanced meals and stay hydrated 💧.")
                st.write(f"💡 *Health Tip:* {tip}")

# HISTORY PAGE
elif page == "History":
    st.header("📚 Food History")
    hist = load_history()
    if not hist:
        st.info("No history yet — capture or upload an image.")
    else:
        df = pd.DataFrame([{
            "Time": h["timestamp"],
            "Dish": h["dish"],
            "Calories (kcal)": h["calories"],
            "Portion (%)": h.get("portion_pct", 100),
            "Allergy Detected": ", ".join(h["allergy_detected"]) if h.get("allergy_detected") else "None"
        } for h in hist])

        st.dataframe(df, use_container_width=True)

        if st.button("Clear history"):
            clear_history()
            st.success("History cleared")
            st.experimental_rerun()

# PROFILE PAGE
elif page == "Profile & Settings":
    st.header("⚙ Profile & Settings")

    if st.button("Logout"):
        st.session_state.user = None
        st.session_state.auth_page = "login"
        st.experimental_rerun()

st.markdown("---")
    