import customtkinter as ctk
from tkinter import filedialog
from src.jhinter import Page
import threading
import requests

book_page = Page()

url = "http://127.0.0.1:5000/books"

def fetch_books(query=None):
    try:
        params = {}
        if query:
            params['q'] = query
        response = requests.get(url, params=params)
        response.raise_for_status()
        books_data = response.json()
        book_page.set_var("books", books_data)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching books: {e}")
        book_page.set_var("books", [])

def search_command():
    query = book_page.get_var("search_bar")
    threading.Thread(target=fetch_books, args=(query,)).start()

def on_enter():
    book_page.set_var("books", [])
    threading.Thread(target=fetch_books).start()

book_page.onEnter = on_enter

def create_book_widget(parent, book):
    book_frame = ctk.CTkFrame(parent, border_width=1, height=70)
    book_frame.pack(fill="x", padx=5, pady=5)
    book_frame.grid_propagate(False)

    # Grid layout: 2 rows, 3 columns
    # Let the first column expand to fill space, pinning the others to the right.
    book_frame.grid_columnconfigure(0, weight=1) 
    book_frame.grid_rowconfigure(0, weight=1)
    book_frame.grid_rowconfigure(1, weight=1)

    # --- Column 0: Title and Author ---
    title_font = ctk.CTkFont(size=16, weight="bold")
    ctk.CTkLabel(book_frame, text=book.get("title", "No Title"), anchor="sw", font=title_font).grid(row=0, column=0, sticky="ew", padx=10)
    
    author_font = ctk.CTkFont(size=10)
    ctk.CTkLabel(book_frame, text=f"by {book.get('author', 'N/A')}", anchor="nw", font=author_font).grid(row=1, column=0, sticky="ew", padx=10)
    
    # --- Columns 1 & 2: Pricing and Buttons ---
    if book.get("is_available", False):
        # Buy Info
        ctk.CTkLabel(book_frame, text=f"Buy: ${book.get('buy_price', 0):.2f}").grid(row=0, column=1, sticky="s")
        ctk.CTkButton(book_frame, text="Buy", width=100).grid(row=1, column=1, padx=5, pady=(0, 5))
        
        # Rent Info
        ctk.CTkLabel(book_frame, text=f"Rent: ${book.get('rent_price', 0):.2f}").grid(row=0, column=2, sticky="s")
        ctk.CTkButton(book_frame, text="Rent", width=100).grid(row=1, column=2, padx=5, pady=(0, 5))
    else:
        ctk.CTkLabel(book_frame, text="Not Available").grid(row=0, column=1, columnspan=2, rowspan=2)

    return book_frame

def book_page_frame(parent):
    frame = ctk.CTkFrame(parent)

    #Search Bar
    book_page.add_searchbar(frame, x=0.5, y=0.05, w=0.7, h=0.05, id="search_bar", placeholder="Search")
    book_page.add_button(frame, x=0.88, y=0.05, w=0.05, h=0.05, content="🔎", command=search_command)

    #Book View
    books = book_page.get_var("books")
    
    book_widgets = []
    if books:
        for book_data in books:
            book_widgets.append(
                lambda sf, data=book_data: create_book_widget(sf, data)
            )
    else:
        book_widgets.append(
            lambda sf: ctk.CTkLabel(sf, text="No books found...").pack(pady=10)
        )

    book_page.add_scrollable_list(frame, x=0.5, y=0.5, w=0.9, h=0.8, widget_generators=book_widgets)
    
    return frame

book_page.set_frame(book_page_frame)
