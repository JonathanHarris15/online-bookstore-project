import customtkinter as ctk
from PIL import Image

class Application:
    def __init__(self, title, dimensions):
        self._current_page = 0
        self._pages = []
        self._pages_names = []
        
        # Initialize CustomTkinter
        ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
        ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
        
        self.root = ctk.CTk()
        self.root.title(title)
        self.root.geometry(dimensions)
        
        self.width = int(dimensions.split('x')[0])
        self.height = int(dimensions.split('x')[1])
    
    def add_page(self, app, page, pageName):
        page._app = app
        self._pages.append(page)
        self._pages_names.append(pageName)

    def clear_pages(self):
        for frame in self.root.winfo_children():
            frame.pack_forget()

    def start_app(self):
        if len(self._pages) < 1:
            print("WARNING: NO PAGES ADDED TO APPLICATION\nCANNOT START")
        else:
            page = self._pages[0]
            page.enter("*PROGRAM OPEN*")
            page._frame = page._promised_frame(self.root)
            page._frame.pack(fill="both", expand=True)
            self.root.mainloop()

    def set_Page(self, window, data_pass):
        self.clear_pages()
        if type(window) == int:
            index = window
        elif window in self._pages_names:
            index = self._pages_names.index(window)
        else:
            print(f"Page {window} not found.")
            return

        page = self._pages[index]
        page._vars.update(data_pass)
        page.enter(self._pages_names[self._current_page])
        page._frame = page._promised_frame(self.root)
        page._frame.master = self.root
        self._current_page = index
        c_frame = page._frame
        c_frame.pack(fill="both", expand=True)

class Page:
    def __init__(self):
        self.onEnter = lambda: print("")
        self._frame = None
        self._vars = {}
        self._reloading = False
        self._entering = True
        self._app = None
        # Default to CTkFrame
        self._promised_frame = lambda parent: ctk.CTkFrame(parent)
        self.entered_from = "Start"

    # Routine automatically called when page is entered to set flags correctly
    def enter(self, start_page):
        self.entered_from = start_page
        self._entering = True
        self.onEnter()
        self._entering = False

    # Made to refresh the information on the page
    def reload(self):
        if not self._reloading:
            self._reloading = True
            # Pass the root as the parent when reloading
            self._frame = self._promised_frame(self._app.root)
            self._reloading = False
            self._app.clear_pages()
            c_frame = self._frame
            c_frame.master = self._app.root
            c_frame.pack(fill="both", expand=True)

    # The method to migrate to another page
    def to_Page(self, page, info=[]):
        self._entering = True
        push_info = {}
        for key, value in self._vars.items():
            if key in info:
                push_info[key] = value
        self._app.set_Page(page, push_info)

    # Sets a page variable in a way that will refresh the screen
    def set_var(self, name, value):
        self._vars[name] = value
        if not self._entering:
            self.reload()

    # Helpers for array manipulation
    def change_index(self, name, index, value):
        x = self.get_var(name)
        if x:
            x[index] = value
            self.set_var(name, x)
    
    def push(self, name, value):
        x = self.get_var(name)
        if x is None: x = []
        x.append(value)
        self.set_var(name, x)

    def get_var(self, name):
        return self._vars.get(name, None)
        
    def set_frame(self, frm):
        if callable(frm):
            self._promised_frame = frm
        else:
            print("set_frame() must take a function")

    def print_vars(self):
        for key, value in self._vars.items():
            print(f"-----> {key} <-----")
            print(value)

    # ==========================================
    # WIDGET HELPER METHODS
    # ==========================================

    def add_button(self, parent, x, y, w, h, content, command=None, id=None, **kwargs):
        """
        Adds a CTkButton using relative positioning.
        x, y: Center position (0.0 to 1.0)
        w, h: Relative size (0.0 to 1.0)
        """
        btn = ctk.CTkButton(parent, text=content, command=command, **kwargs)
        btn.place(relx=x, rely=y, relwidth=w, relheight=h, anchor="center")
        if id: self._vars[id] = btn
        return btn

    def add_searchbar(self, parent, x, y, w, h, id, placeholder="", **kwargs):
        """
        Adds a CTkEntry. 
        Automatically updates self._vars[id] when text changes.
        """
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder, **kwargs)
        
        # Pre-fill if var exists
        if id in self._vars and self._vars[id] is not None:
            entry.insert(0, str(self._vars[id]))

        # Callback to update variable on key release
        def on_change(event):
            # We don't call set_var here to avoid full page reload on every keystroke
            # We just update the internal dictionary.
            self._vars[id] = entry.get()
            
        entry.bind("<KeyRelease>", on_change)
        entry.place(relx=x, rely=y, relwidth=w, relheight=h, anchor="center")
        return entry

    def add_text_input(self, parent, x, y, w, h, id, **kwargs):
        """Alias for add_searchbar used for general text input"""
        return self.add_searchbar(parent, x, y, w, h, id, **kwargs)

    def add_scrollable_list(self, parent, x, y, w, h, widget_generators, **kwargs):
        """
        Adds a CTkScrollableFrame.
        widget_generators: A list of FUNCTIONS (lambdas). 
                           Each function must accept 'scroll_frame' as an argument.
                           Example: [lambda f: ctk.CTkLabel(f, text="Hi").pack()]
        """
        scroll_frame = ctk.CTkScrollableFrame(parent, **kwargs)
        scroll_frame.place(relx=x, rely=y, relwidth=w, relheight=h, anchor="center")
        
        for gen in widget_generators:
            gen(scroll_frame)
            
        return scroll_frame

    def add_image(self, parent, x, y, w, h, image_path, **kwargs):
        """
        Adds a CTkImage inside a label.
        Requires 'image_path'.
        """
        try:
            # Need to keep a reference to avoid garbage collection
            pil_img = Image.open(image_path)
            # CTkImage requires a size tuple, default to something reasonable or use w/h * parent size if possible. 
            # Since relative sizing is hard for images without knowing parent pixel size, we default to arbitrary.
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(100, 100)) 
            
            lbl = ctk.CTkLabel(parent, text="", image=ctk_img, **kwargs)
            lbl.place(relx=x, rely=y, relwidth=w, relheight=h, anchor="center")
            return lbl
        except Exception as e:
            print(f"Error loading image: {e}")
            lbl = ctk.CTkLabel(parent, text=f"Img Error: {image_path}")
            lbl.place(relx=x, rely=y, relwidth=w, relheight=h, anchor="center")
            return lbl
