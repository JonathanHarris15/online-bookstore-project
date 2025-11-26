import customtkinter as ctk
from tkinter import filedialog
from src.jhinter import Page

login_page = Page()

def login_page_frame(parent):
    frame = ctk.CTkFrame(parent)
    ctk.CTkLabel(frame, text="Login", font=("Arial", 24)).place(relx=0.5, rely=0.05, anchor="center")

    #Username and Password
    login_page.add_text_input(parent, x=0.5, y=0.45, w=0.35, h=0.05, id="username_entry", placeholder="Username")
    login_page.add_text_input(parent, x=0.5, y=0.51, w=0.35, h=0.05, id="password_entry", placeholder="Password", show="*")

    #Login Button
    login_page.add_button(parent, x=0.5, y=0.6, w=0.2, h=0.05, content="Login", command=lambda: login_page.print_vars())

    #Back to Main Menu
    login_page.add_button(parent, x=0.94, y=0.96, w=0.1, h=0.05, content="Back", command=lambda: login_page.to_Page("Start Page"))
    return frame

login_page.set_frame(login_page_frame)
