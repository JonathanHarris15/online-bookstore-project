import customtkinter as ctk
from tkinter import filedialog
from src.jhinter import Page

cart_page = Page()

def remove_from_cart(book):
    cart = cart_page.get_var("cart")
    cart = [item for item in cart if item[0] != book]
    cart_page.set_var("cart", cart)

def create_cart_widget(parent, book, purchase_type):
    cart_frame = ctk.CTkFrame(parent, border_width=1, height=70)
    cart_frame.pack(fill="x", padx=5, pady=5)
    cart_frame.grid_propagate(False)

    cart_frame.grid_columnconfigure(0, weight=1)
    cart_frame.grid_rowconfigure(0, weight=1)
    cart_frame.grid_rowconfigure(1, weight=1)

    title_font = ctk.CTkFont(size=16, weight="bold")
    ctk.CTkLabel(cart_frame, text=book.get("title", "No Title"), anchor="sw", font=title_font).grid(row=0, column=0, sticky="ew", padx=10)

    author_font = ctk.CTkFont(size=10)
    ctk.CTkLabel(cart_frame, text=f"by {book.get('author', 'N/A')}", anchor="nw", font=author_font).grid(row=1, column=0, sticky="ew", padx=10)

    price = book.get('rent_price', 0) if purchase_type == "rent" else book.get('buy_price', 0)
    status = f"Rent: ${price:.2f}" if purchase_type == "rent" else f"Purchase: ${price:.2f}"
    ctk.CTkLabel(cart_frame, text=status).grid(row=0, column=1, rowspan=2, padx=10)
    
    ctk.CTkButton(cart_frame, text="Remove", width=100, fg_color='red2', hover_color='red3', command=lambda: remove_from_cart(book)).grid(row=0, column=2, rowspan=2, padx=5, pady=5)


def cart_page_frame(parent):
    frame = ctk.CTkFrame(parent)
    cart = cart_page.get_var("cart")

    #Title
    ctk.CTkLabel(frame, text="Cart", font=("Arial", 24)).place(relx=0.03, rely=0.05, anchor="nw")

    #Create the scrollable shopping Cart
    cart_widgets = []
    total_cost = 0
    if cart:
        for book, purchase_type in cart:
            if purchase_type == "rent":
                total_cost += book.get('rent_price', 0)
            else:
                total_cost += book.get('buy_price', 0)
            cart_widgets.append(
                lambda sf, b=book, p_type=purchase_type: create_cart_widget(sf, b, p_type)
            )
    else:
        cart_widgets.append(
            lambda sf: ctk.CTkLabel(sf, text="Your cart is empty.").pack(pady=10)
        )

    cart_page.add_scrollable_list(frame, x=0.325, y=0.55, w=0.6, h=0.8, widget_generators=cart_widgets)

    # Mock Payment Screen
    payment_frame = ctk.CTkFrame(frame, border_width=1)
    payment_frame.place(relx=0.8, rely=0.2, relwidth=0.3, relheight=0.6, anchor="n")

    ctk.CTkLabel(payment_frame, text="Payment", font=("Arial", 18, "bold")).pack(pady=10)
    ctk.CTkEntry(payment_frame, placeholder_text="Card Number").pack(fill="x", padx=10, pady=5)
    ctk.CTkEntry(payment_frame, placeholder_text="MM/YY").pack(fill="x", padx=10, pady=5)
    ctk.CTkEntry(payment_frame, placeholder_text="CVC").pack(fill="x", padx=10, pady=5)

    # Total Cost
    ctk.CTkLabel(payment_frame, text=f"Total: ${total_cost:.2f}", font=("Arial", 16, "bold")).pack(pady=20)

    ctk.CTkButton(payment_frame, text="Confirm Purchase", command=lambda: print("Purchase Confirmed")).pack(fill="x", padx=10, pady=10)


    cart_page.add_button(parent, x=0.94, y=0.96, w=0.1, h=0.05, content="Back", command=lambda: cart_page.to_Page("Book Page","cart"))
    return frame

cart_page.set_frame(cart_page_frame)
