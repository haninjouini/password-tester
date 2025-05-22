import streamlit as st
import math
import pandas as pd
import hashlib
import logging
import os
import random

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load top 1000 passwords from file
def load_common_passwords():
    with open("top-1000.txt", "r", encoding="utf-8") as file:
        return set(p.strip().lower() for p in file.readlines())

common_passwords = load_common_passwords()

# Entropy estimator
def calculate_entropy(password):
    pool = 0
    if any(c.islower() for c in password): pool += 26
    if any(c.isupper() for c in password): pool += 26
    if any(c.isdigit() for c in password): pool += 10
    if any(c in "!@#$%^&*()_+~`|}{[]:;?><,./-=" for c in password): pool += 32
    entropy = len(password) * math.log2(pool) if pool else 0
    return round(entropy, 2)

# Strength label
def strength_label(entropy):
    if entropy < 28:
        return "Very Weak", "red", 0.2
    elif entropy < 36:
        return "Weak", "orange", 0.4
    elif entropy < 60:
        return "Moderate", "yellow", 0.6
    elif entropy < 80:
        return "Strong", "lightgreen", 0.8
    else:
        return "Very Strong", "green", 1.0

# Password suggestion
def generate_strong_password(length=12):
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+~`|}{[]:;?><,./-="
    return ''.join(random.SystemRandom().choice(chars) for _ in range(length))

# Save to Excel
def save_hashed_password(password):
    hashed = hashlib.sha256(password.encode()).hexdigest()
    file = "hashed_passwords.xlsx"
    try:
        if os.path.exists(file):
            df = pd.read_excel(file)
            df.loc[len(df)] = [hashed]
        else:
            df = pd.DataFrame([[hashed]], columns=["Hashed Password"])
        df.to_excel(file, index=False)
        logging.info("Password saved.")
    except Exception as e:
        logging.error(f"Error saving password: {e}")
        st.error("❌ Failed to save password.")

# Streamlit UI
st.title("🔐 Password Strength Tester")

show = st.checkbox("👁️ Show Password")
password = st.text_input("Enter Password", type="default" if show else "password")

if password:
    entropy = calculate_entropy(password)
    label, color, strength = strength_label(entropy)

    st.markdown(f"📋 **Entropy:** `{entropy}` bits")
    st.markdown(f"<span style='color:{color}; font-weight:bold;'>❓ Strength: {label}</span>", unsafe_allow_html=True)
    st.progress(strength)

    is_common = password.lower() in common_passwords

    if is_common:
        st.warning("⚠️ This password is too common!")

    if not is_common and label in ["Strong", "Very Strong"]:
        if st.button("✅ Validate & Save"):
            save_hashed_password(password)
            st.success("✅ Password validated and saved successfully.")
    elif not is_common:
        st.info("ℹ️ Please use a stronger password before saving.")
