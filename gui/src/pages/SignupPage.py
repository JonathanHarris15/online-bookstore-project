import customtkinter as ctk
from tkinter import filedialog
from src.jhinter import Page
import threading
import requests

signup_page = Page()

url = "http://127.0.0.1:5000/auth/register"

def signup_page_frame(parent):
    frame = ctk.CTkFrame(parent)
    ctk.CTkLabel(frame, text="Sign Up", font=("Arial", 24)).place(relx=0.5, rely=0.05, anchor="center")

    def register():
        email_val = signup_page.get_var("email_entry")
        username_val = signup_page.get_var("username_entry")
        password_val = signup_page.get_var("password_entry")
        password_c_val = signup_page.get_var("c_password_entry")

        #check to see if passwords match
        if password_val != password_c_val:
            signup_page.set_var("status", "Passwords do not match")
            signup_page.set_var("passord_entry", None)
            signup_page.set_var("c_password_entry", None)
            return
        
        #check to make sure they have filled out all the fields
        if email_val is None or username_val is None or password_val is None:
            signup_page.set_var("status", "Please fill out all fields")
            return
        
        #valid email
        if "@" not in email_val:
            signup_page.set_var("status", "Invalid email")
            return

        def send_request_task(email, username, password):
            try:
                response = requests.post(url, json={
                    "email": email,
                    "username": username,
                    "password": password
                })
                print("response:")
                print(response.json())
                
                signup_page.set_var("status", "Request Complete") 

            except Exception as e:
                print(f"Error: {e}")
                signup_page.set_var("status", "Something went wrong")

        # This creates a separate lane for the network traffic so the GUI doesn't freeze
        t = threading.Thread(target=send_request_task, args=(email_val, username_val, password_val))
        t.start()

    #Username, Password, and Email
    signup_page.add_text_input(parent, x=0.5, y=0.39, w=0.35, h=0.05, id="email_entry", placeholder="Email")
    signup_page.add_text_input(parent, x=0.5, y=0.45, w=0.35, h=0.05, id="username_entry", placeholder="Username")
    signup_page.add_text_input(parent, x=0.5, y=0.51, w=0.35, h=0.05, id="password_entry", placeholder="Password", show="*")
    signup_page.add_text_input(parent, x=0.5, y=0.57, w=0.35, h=0.05, id="c_password_entry", placeholder="Confirm Password", show="*")

    #Login Button
    signup_page.add_button(parent, x=0.5, y=0.65, w=0.2, h=0.05, content="Register", command=lambda: register())

    #Status Message
    status = signup_page.get_var("status")
    if status is None: status = ""
    ctk.CTkLabel(frame, text=status, font=("Arial", 12), text_color="yellow").place(relx=0.5, rely=0.7, anchor="center")

    #Back to Main Menu
    def back():
        signup_page.set_var("status", None)
        signup_page.set_var("email_entry", None)
        signup_page.set_var("username_entry", None)
        signup_page.set_var("password_entry", None)
        signup_page.to_Page("Start Page")
    signup_page.add_button(parent, x=0.94, y=0.96, w=0.1, h=0.05, content="Back", command=lambda: back())
    return frame

signup_page.set_frame(signup_page_frame)
