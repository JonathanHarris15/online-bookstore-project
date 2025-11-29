import customtkinter as ctk
from tkinter import filedialog
from src.jhinter import Page
import threading
import requests

url = "http://127.0.0.1:5000/auth/login"

login_page = Page()

def try_login():
    username_val = login_page.get_var("username_entry")
    password_val = login_page.get_var("password_entry")
    if username_val is None or password_val is None:
        login_page.set_var("status", "Please fill out all fields")
        return
    
    def send_request_task(username, password):
        try:
            response = requests.post(url, json={
                "username": username,
                "password": password
            })
            if response.status_code == 200:
                login_page.set_var("status", "Login Successful")
                login_page.set_var("username", username)
                token = response.json()["access_token"]
                login_page.set_var("token", token)

                #Check the manager database
                headers = {"Authorization": f"Bearer {token}"}
                manager_check_response = requests.get("http://127.0.0.1:5000/manager/orders", headers=headers)
                
                if manager_check_response.status_code == 200:
                    # Is a manager
                    login_page.to_Page("Manager Page", ["username", "token"])
                else:
                    # Is not a manager
                    login_page.to_Page("Book Page",["username","token"])
            if response.status_code == 401:
                login_page.set_var("status", "Invalid Credentials")
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            login_page.set_var("status", "Something went wrong. Could not connect to server.")
    
    t = threading.Thread(target=send_request_task, args=(username_val, password_val))
    t.start()

def login_page_frame(parent):
    frame = ctk.CTkFrame(parent)
    ctk.CTkLabel(frame, text="Login", font=("Arial", 24)).place(relx=0.5, rely=0.05, anchor="center")

    #Username and Password
    login_page.add_text_input(parent, x=0.5, y=0.45, w=0.35, h=0.05, id="username_entry", placeholder="Username")
    login_page.add_text_input(parent, x=0.5, y=0.51, w=0.35, h=0.05, id="password_entry", placeholder="Password", show="*")

    #Login Button
    login_page.add_button(parent, x=0.5, y=0.6, w=0.2, h=0.05, content="Login", command=lambda: try_login())

    #Status Message
    status = login_page.get_var("status")
    if status is None: status = ""
    ctk.CTkLabel(frame, text=status, font=("Arial", 12), text_color="yellow").place(relx=0.5, rely=0.7, anchor="center")

    #Back to Main Menu
    login_page.add_button(parent, x=0.94, y=0.96, w=0.1, h=0.05, content="Back", command=lambda: login_page.to_Page("Start Page"))
    return frame

login_page.set_frame(login_page_frame)
