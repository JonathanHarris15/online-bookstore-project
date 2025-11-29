import customtkinter as ctk
import requests
import json
from src.jhinter import Page

user_info_page = Page()

API_BASE = "http://127.0.0.1:5000"


def get_user_info(token, username):
    headers = {"Authorization": f"Bearer {token}"}
    # Try endpoint that returns current user by username or token
    try:
        response = requests.get(f"{API_BASE}/auth/user/{username}", headers=headers)
    except Exception:
        return None

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch user info: {response.status_code} {response.text}")
        return None

def update_user_info(token, username, data):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    # Try a PATCH endpoint for user updates
    response = requests.patch(f"{API_BASE}/auth/user/{username}", headers=headers, data=json.dumps(data))
    return response

def create_user_order_widget(parent, order):
    oframe = ctk.CTkFrame(parent, border_width=1, height=120)
    oframe.pack(fill='x', padx=5, pady=5)
    oframe.grid_propagate(False)

    oframe.grid_columnconfigure(0, weight=1)
    oframe.grid_columnconfigure(1, weight=0)

    ctk.CTkLabel(oframe, text=f"Order ID: {order.get('id')}", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky='w', padx=10)
    ctk.CTkLabel(oframe, text=f"Date: {order.get('order_date')}").grid(row=1, column=0, sticky='w', padx=10)
    ctk.CTkLabel(oframe, text=f"Total: ${order.get('total_amount', 0):.2f}").grid(row=0, column=1, sticky='e', padx=10)
    ctk.CTkLabel(oframe, text=f"Status: {order.get('payment_status')}").grid(row=1, column=1, sticky='e', padx=10)

    # items
    items = order.get('items') or []
    for idx, itm in enumerate(items):
        title = itm.get('title') or f"Book ID {itm.get('book_id') }"
        ptype = itm.get('type', '')
        price = itm.get('item_price', 0.0)
        ctk.CTkLabel(oframe, text=f" - {title} ({ptype}): ${price:.2f}", anchor='w').grid(row=2+idx, column=0, columnspan=2, sticky='w', padx=20)

    return oframe

def user_info_frame(parent):
    frame = ctk.CTkFrame(parent)

    # Fetch current info
    user = None
    token = user_info_page.get_var("token")
    username = user_info_page.get_var("username")
    if token and username:
        user = get_user_info(token, username)

    ctk.CTkLabel(frame, text="Your Account", font=("Arial", 24)).pack(pady=2)

    form = ctk.CTkFrame(frame)
    # tighten spacing so buttons sit directly below the form
    form.pack(padx=20, pady=(0,0), fill='x')

    # Username (read-only)
    ctk.CTkLabel(form, text="Username:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
    username_var = ctk.StringVar(value=user.get('username') if user else (username or ""))
    username_entry = ctk.CTkEntry(form, textvariable=username_var, state='disabled')
    username_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=5)

    # Email
    ctk.CTkLabel(form, text="Email:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
    email_var = ctk.StringVar(value=user.get('email') if user else "")
    email_entry = ctk.CTkEntry(form, textvariable=email_var)
    email_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=5)

    # Current password (required to save changes)
    ctk.CTkLabel(form, text="Current Password (required to save):").grid(row=2, column=0, sticky='w', padx=5, pady=5)
    current_pw_var = ctk.StringVar()
    current_pw_entry = ctk.CTkEntry(form, textvariable=current_pw_var, show='*')
    current_pw_entry.grid(row=2, column=1, sticky='ew', padx=5, pady=5)

    # New password (optional)
    ctk.CTkLabel(form, text="New Password (optional):").grid(row=3, column=0, sticky='w', padx=5, pady=5)
    new_pw_var = ctk.StringVar()
    new_pw_entry = ctk.CTkEntry(form, textvariable=new_pw_var, show='*')
    new_pw_entry.grid(row=3, column=1, sticky='ew', padx=5, pady=5)

    form.grid_columnconfigure(1, weight=1)

    status_label = ctk.CTkLabel(frame, text="", text_color="red")
    # remove extra vertical gap
    status_label.pack(pady=(0,0))

    buttons = ctk.CTkFrame(frame)
    # pack buttons immediately under the form (no vertical gap)
    buttons.pack(padx=20, pady=(0,0), fill='x')

    def enable_save(*args):
        # Save enabled only if current password provided and email not empty
        cur = current_pw_var.get().strip()
        em = email_var.get().strip()
        save_btn.configure(state='normal' if cur and em else 'disabled')

    current_pw_var.trace_add('write', enable_save)
    email_var.trace_add('write', enable_save)

    def on_cancel():
        # reset fields to fetched values
        if user:
            email_var.set(user.get('email',''))
        current_pw_var.set("")
        new_pw_var.set("")
        status_label.configure(text="")

    def on_save():
        status_label.configure(text="")
        cur_pw = current_pw_var.get().strip()
        if not cur_pw:
            status_label.configure(text="Enter current password to save.")
            return

        payload = {
            'current_password': cur_pw,
            'email': email_var.get().strip()
        }
        if new_pw_var.get().strip():
            payload['new_password'] = new_pw_var.get().strip()

        try:
            resp = update_user_info(token, username_var.get(), payload)
        except Exception as e:
            status_label.configure(text=f"Network error: {e}")
            return

        if resp is None:
            status_label.configure(text="No response from server.")
            return

        if resp.status_code in (200, 204):
            status_label.configure(text="Saved successfully.", text_color="green")
            # clear sensitive fields
            current_pw_var.set("")
            new_pw_var.set("")
            # refresh user info from server
            updated = get_user_info(token, username_var.get())
            if updated:
                email_var.set(updated.get('email',''))
        else:
            try:
                msg = resp.json().get('message', resp.text)
            except Exception:
                msg = resp.text
            status_label.configure(text=f"Failed: {msg}")

    save_btn = ctk.CTkButton(buttons, text="Save", command=on_save, state='disabled')
    save_btn.pack(side='right', padx=5)

    cancel_btn = ctk.CTkButton(buttons, text="Cancel", command=on_cancel)
    cancel_btn.pack(side='right', padx=5)

    # helper to focus current password when opening
    def on_show():
        current_pw_entry.focus()

    frame.bind("<Visibility>", lambda e: on_show())

    orders = user.get('orders') if user else []
    order_widgets = []
    # put the section title inside the scrollable area so it appears at the top
    order_widgets.append(lambda sf: ctk.CTkLabel(sf, text="Order History", font=("Arial", 18, "bold")).pack(pady=(0,6)))
    if orders:
        for ord_item in orders:
            order_widgets.append(lambda sf, o=ord_item: create_user_order_widget(sf, o))
    else:
        order_widgets.append(lambda sf: ctk.CTkLabel(sf, text="No past orders.").pack(pady=6))

    # Orders Section: place the scrollable list directly below the buttons
    user_info_page.add_scrollable_list(frame, x=0.5, y=0.6, w=0.97, h=0.6, widget_generators=order_widgets)

    # Back Button
    user_info_page.add_button(parent, x=0.96, y=0.98, w=0.05, h=0.025, content="Back", command=lambda: user_info_page.to_Page("Book Page", ["token", "username"]))
    return frame


user_info_page.set_frame(user_info_frame)
