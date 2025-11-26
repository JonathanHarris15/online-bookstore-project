import customtkinter as ctk
from tkinter import filedialog
from src.jhinter import Page

start_page = Page()

def start_page_frame(parent):
    frame = ctk.CTkFrame(parent)
    ctk.CTkLabel(frame, text="Online Bookstore", font=("Arial", 24)).place(relx=0.5, rely=0.05, anchor="center")    

    #Go to Login Page
    start_page.add_button(parent, x=0.5, y=0.44, w=0.2, h=0.1, content="Log In", command=lambda:start_page.to_Page("Login Page"))

    #Go to Sign Up Page
    start_page.add_button(parent, x=0.5, y=0.56, w=0.2, h=0.1, content="Sign Up", command=lambda: start_page.to_Page("Sign Up Page"))

    return frame

start_page.set_frame(start_page_frame)
