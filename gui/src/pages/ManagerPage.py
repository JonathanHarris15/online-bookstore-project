import customtkinter as ctk
import requests
import json
from src.jhinter import Page

manager_page = Page()

def get_all_orders(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get("http://127.0.0.1:5000/manager/orders", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch orders: {response.json().get('message')}")
        return []

def get_all_books():
    response = requests.get("http://127.0.0.1:5000/books")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch books: {response.json().get('message')}")
        return []

def update_order_status(order_id, new_status, token, status_label, button):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {"payment_status": new_status}
    response = requests.patch(f"http://127.0.0.1:5000/manager/orders/{order_id}", headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        print(f"Order {order_id} updated successfully")
        status_label.configure(text=f"Status: {new_status}")
        button.destroy()
    else:
        print(f"Failed to update order: {response.json().get('message')}")

def add_book(title_entry, author_entry, buy_price_entry, rent_price_entry, token, book_list_frame):
    title = title_entry.get()
    author = author_entry.get()
    
    try:
        buy_price = float(buy_price_entry.get())
        rent_price = float(rent_price_entry.get())
    except ValueError:
        print("Invalid price format. Please enter a number.")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "title": title,
        "author": author,
        "buy_price": buy_price,
        "rent_price": rent_price
    }
    response = requests.post("http://127.0.0.1:5000/books", headers=headers, data=json.dumps(data))
    if response.status_code == 201:
        print(f"Book '{title}' added successfully")
        title_entry.delete(0, 'end')
        author_entry.delete(0, 'end')
        buy_price_entry.delete(0, 'end')
        rent_price_entry.delete(0, 'end')
        
        for widget in book_list_frame.winfo_children():
            widget.destroy()
        
        books = get_all_books()
        for book in books:
            create_book_widget(book_list_frame, book, token)
    else:
        print(f"Failed to add book: {response.json().get('message')}")

def delete_book(book_id, token, book_frame):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"http://127.0.0.1:5000/books/{book_id}", headers=headers)
    if response.status_code == 200:
        print(f"Book {book_id} deleted successfully")
        book_frame.destroy()
    else:
        print(f"Failed to delete book: {response.json().get('message')}")

def update_book(book_id, data, token, book_frame):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    response = requests.patch(f"http://127.0.0.1:5000/books/{book_id}", headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        print(f"Book {book_id} updated successfully")
        updated_book = response.json()
        populate_book_frame(book_frame, updated_book, token)
    else:
        print(f"Failed to update book: {response.json().get('message')}")

def open_update_book_window(book, token, book_frame):
    update_window = ctk.CTkToplevel(book_frame)
    update_window.title("Update Book")
    update_window.geometry("400x400")

    ctk.CTkLabel(update_window, text="Title").pack(pady=(10, 0))
    title_entry = ctk.CTkEntry(update_window, width=300)
    title_entry.insert(0, book['title'])
    title_entry.pack(pady=5)

    ctk.CTkLabel(update_window, text="Author").pack(pady=5)
    author_entry = ctk.CTkEntry(update_window, width=300)
    author_entry.insert(0, book['author'])
    author_entry.pack(pady=5)

    ctk.CTkLabel(update_window, text="Buy Price").pack(pady=5)
    buy_price_entry = ctk.CTkEntry(update_window, width=300)
    buy_price_entry.insert(0, str(book['buy_price']))
    buy_price_entry.pack(pady=5)

    ctk.CTkLabel(update_window, text="Rent Price").pack(pady=5)
    rent_price_entry = ctk.CTkEntry(update_window, width=300)
    rent_price_entry.insert(0, str(book['rent_price']))
    rent_price_entry.pack(pady=5)
    
    is_available_var = ctk.BooleanVar(value=book['is_available'])
    ctk.CTkCheckBox(update_window, text="Is Available", variable=is_available_var).pack(pady=10)

    def save_update():
        updated_data = {
            "title": title_entry.get(),
            "author": author_entry.get(),
            "buy_price": float(buy_price_entry.get()),
            "rent_price": float(rent_price_entry.get()),
            "is_available": is_available_var.get()
        }
        update_book(book['id'], updated_data, token, book_frame)
        update_window.destroy()

    save_button = ctk.CTkButton(update_window, text="Save", command=save_update)
    save_button.pack(pady=10)

    cancel_button = ctk.CTkButton(update_window, text="Cancel", command=update_window.destroy)
    cancel_button.pack(pady=5)

    update_window.grab_set()
    update_window.focus()

def populate_book_frame(book_frame, book, token):
    for widget in book_frame.winfo_children():
        widget.destroy()

    book_frame.grid_columnconfigure(0, weight=1)
    book_frame.grid_columnconfigure(1, weight=0)
    book_frame.grid_columnconfigure(2, weight=0)

    availability = "Available" if book['is_available'] else "Rented"
    
    ctk.CTkLabel(book_frame, text=book['title'], font=("Arial", 16, "bold")).grid(row=0, column=0, sticky="w", padx=10)
    ctk.CTkLabel(book_frame, text=f"by {book['author']}").grid(row=1, column=0, sticky="w", padx=10)
    ctk.CTkLabel(book_frame, text=f"Buy: ${book['buy_price']:.2f}").grid(row=0, column=1, sticky="e", padx=10)
    ctk.CTkLabel(book_frame, text=f"Rent: ${book['rent_price']:.2f}").grid(row=1, column=1, sticky="e", padx=10)
    ctk.CTkLabel(book_frame, text=f"Status: {availability}").grid(row=2, column=0, columnspan=2, sticky="w", padx=10)


    if book['is_available']:
        ctk.CTkButton(book_frame, text="Update", command=lambda: open_update_book_window(book, token, book_frame)).grid(row=0, column=2, padx=5, pady=4)
        ctk.CTkButton(book_frame, text="Delete", command=lambda: delete_book(book['id'], token, book_frame)).grid(row=1, column=2, padx=5, pady=4)
    else:
        ctk.CTkButton(book_frame, text="Mark as Returned", command=lambda: update_book(book['id'], {'is_available': True}, token, book_frame)).grid(row=0, column=2, rowspan=2, padx=5, pady=4)

def create_order_widget(parent, order, token):
    order_frame = ctk.CTkFrame(parent, border_width=1, height=70)
    order_frame.pack(fill="x", padx=5, pady=5)
    order_frame.grid_propagate(False)

    order_frame.grid_columnconfigure(0, weight=1)
    order_frame.grid_columnconfigure(1, weight=1)
    order_frame.grid_columnconfigure(2, weight=1)

    ctk.CTkLabel(order_frame, text=f"Order ID: {order['id']}").grid(row=0, column=0, sticky="w", padx=10)
    ctk.CTkLabel(order_frame, text=f"User ID: {order['user_id']}").grid(row=1, column=0, sticky="w", padx=10)
    ctk.CTkLabel(order_frame, text=f"Total: ${order['total_amount']:.2f}").grid(row=0, column=1, sticky="w", padx=10)
    status_label = ctk.CTkLabel(order_frame, text=f"Status: {order['payment_status']}")
    status_label.grid(row=1, column=1, sticky="w", padx=10)

    def open_order_detail_window(order):
        detail_win = ctk.CTkToplevel(order_frame)
        detail_win.title(f"Order {order['id']} Details")
        detail_win.geometry("500x400")
        detail_win.grab_set()
        detail_win.focus()

        ctk.CTkLabel(detail_win, text=f"Order ID: {order['id']}", font=("Arial", 16, "bold")).pack(pady=(10,0))
        ctk.CTkLabel(detail_win, text=f"User ID: {order['user_id']}").pack(pady=(0,5))
        ctk.CTkLabel(detail_win, text=f"Order Date: {order.get('order_date','')}").pack(pady=(0,5))
        ctk.CTkLabel(detail_win, text=f"Total: ${order.get('total_amount',0):.2f}").pack(pady=(0,5))
        ctk.CTkLabel(detail_win, text=f"Status: {order.get('payment_status','')}").pack(pady=(0,10))

        items_frame = ctk.CTkFrame(detail_win)
        items_frame.pack(fill='both', expand=True, padx=10, pady=5)

        if order.get('items'):
            for itm in order['items']:
                title = itm.get('title') or f"Book ID {itm.get('book_id') }"
                author = itm.get('author', 'N/A')
                ptype = itm.get('type', '')
                price = itm.get('item_price', 0.0)
                item_txt = f"{title} by {author} — {ptype.capitalize()}: ${price:.2f}"
                ctk.CTkLabel(items_frame, text=item_txt, anchor='w').pack(fill='x', pady=2)
        else:
            ctk.CTkLabel(items_frame, text="No items available.").pack(pady=10)

    # View button always available
    view_btn = ctk.CTkButton(order_frame, text="View", command=lambda: open_order_detail_window(order))
    view_btn.grid(row=0, column=2, padx=5, pady=4)

    if order['payment_status'] == 'Pending':
        button = ctk.CTkButton(order_frame, text="Mark as Paid", command=lambda: update_order_status(order['id'], 'Paid', token, status_label, button))
        button.grid(row=1, column=2, padx=5)

def create_book_widget(parent, book, token):
    book_frame = ctk.CTkFrame(parent, border_width=1, height=100)
    book_frame.pack(fill="x", padx=5, pady=5)
    book_frame.grid_propagate(False)

    populate_book_frame(book_frame, book, token)

def manager_page_frame(parent):
    frame = ctk.CTkFrame(parent)
    token = manager_page.get_var("token")

    # Orders Section
    orders_frame = ctk.CTkFrame(frame)
    orders_frame.place(relx=0.01, rely=0.05, relwidth=0.48, relheight=0.9)

    ctk.CTkLabel(orders_frame, text="All Orders", font=("Arial", 24)).pack(pady=10)

    orders = get_all_orders(token)
    order_widgets = [lambda sf, o=order: create_order_widget(sf, o, token) for order in orders]
    manager_page.add_scrollable_list(orders_frame, x=0.5, y=0.5, w=0.95, h=0.8, widget_generators=order_widgets)

    # Books Section
    books_frame = ctk.CTkFrame(frame)
    books_frame.place(relx=0.51, rely=0.05, relwidth=0.48, relheight=0.9)

    ctk.CTkLabel(books_frame, text="All Books", font=("Arial", 24)).pack(pady=10)

    # Book View
    books = get_all_books()
    book_widgets = [lambda sf, b=book: create_book_widget(sf, b, token) for book in books]
    book_list_frame = manager_page.add_scrollable_list(books_frame, x=0.5, y=0.32, w=0.95, h=0.55, widget_generators=book_widgets)

    # Add Book Form
    add_book_frame = ctk.CTkFrame(books_frame)
    add_book_frame.place(relx=0.5, rely=0.62, relwidth=0.95, relheight=0.35, anchor="n")

    ctk.CTkLabel(add_book_frame, text="Add New Book", font=("Arial", 18)).pack(pady=10)

    title_entry = ctk.CTkEntry(add_book_frame, placeholder_text="Title")
    title_entry.pack(fill="x", padx=10, pady=5)
    author_entry = ctk.CTkEntry(add_book_frame, placeholder_text="Author")
    author_entry.pack(fill="x", padx=10, pady=5)
    buy_price_entry = ctk.CTkEntry(add_book_frame, placeholder_text="Buy Price")
    buy_price_entry.pack(fill="x", padx=10, pady=5)
    rent_price_entry = ctk.CTkEntry(add_book_frame, placeholder_text="Rent Price")
    rent_price_entry.pack(fill="x", padx=10, pady=5)

    ctk.CTkButton(add_book_frame, text="Add Book", command=lambda: add_book(
        title_entry,
        author_entry,
        buy_price_entry,
        rent_price_entry,
        token,
        book_list_frame
    )).pack(fill="x", padx=10, pady=10)


    manager_page.add_button(parent, x=0.96, y=0.98, w=0.05, h=0.025, content="Back", command=lambda: manager_page.to_Page("Start Page"))
    return frame

manager_page.set_frame(manager_page_frame)

