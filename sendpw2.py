import streamlit as st
import cv2
import requests

def trigger_action():
    response = requests.get("http://localhost:5000/trigger")
    if response.status_code == 200:
        st.success("メールに送信しました")
    else:
        st.error("失敗しました")

def blur_frame(frame):
    blurred_frame = cv2.GaussianBlur(frame, (111, 111), 50)
    return blurred_frame

def authenticate(username, password):
    predefined_username = "admin"
    predefined_password = "password"
    
    if username == predefined_username and password == predefined_password:
        return True
    else:
        return False

def send_password_to_guardian(username, password):
    line_token = "fKVwPel+bcZBbDaC5ckPhJBaRey5BJztfCu0wVYynLtppmworF1u6SHaDPmnFOqs0HChrr6V8x4Wy43rFbN+rVybD020IeFERvzbdwuO1Jq/XuUujdJEWsyE7JgmLBE0pot1u46LiIo8nXe+QImhZQdB04t89/1O/w1cDnyilFU="
    guardian_user_id = "U7bbb043aed5832647e554557979a6110"

    message = f"Username: {username}\nPassword: {password}"
    
    payload = {
        "to": guardian_user_id,
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {line_token}"
    }
    
    response = requests.post("https://api.line.me/v2/bot/message/push", json=payload, headers=headers)
    
    if response.status_code == 200:
        return True
    else:
        return False

def show_guardian_page():
    st.subheader("見守り映像")
    is_blurred = True   
        
    if st.button("映像切り替え用パスワード要求（LINE通知）"):
        if send_password_to_guardian("admin", "password"):
            st.success("送信成功しました")
        else:
            st.error("送信失敗しました")
    
    cap = cv2.VideoCapture(0)
    video_container = st.empty()
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            st.warning("カメラがない")
            break
        
        if is_blurred:
            frame = blur_frame(frame)
        
        video_container.image(frame, channels="BGR")

def show_protected_page():
    st.subheader("被見守り者ページ")
    is_blurred = st.checkbox("ぼかし/クリア", key="blurred_checkbox")
    
    cap = cv2.VideoCapture(0)
    video_container = st.empty()

    if st.button("異常がある"):
        trigger_action() 
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            st.warning("カメラがない")
            break
        
        if is_blurred:
            frame = blur_frame(frame)
        
        video_container.image(frame, channels="BGR")

def main():
    st.title("見守りシステム")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("映像切り替えlogin"):
        if authenticate(username, password):
            st.session_state.role = "被見守り者"
    
    if "role" not in st.session_state:
        st.session_state.role = "見守り者"
    
    if st.session_state.role == "被見守り者":
        show_protected_page()
    else:
        show_guardian_page()

if __name__ == "__main__":
    main()
