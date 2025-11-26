from src.jhinter import Application
from src.pages import StartPage, LoginPage, SignupPage, BookPage


# Create the main application window
app = Application("Online Bookstore", "800x600")

app.add_page(app, StartPage.start_page, "Start Page")
app.add_page(app, LoginPage.login_page, "Login Page")
app.add_page(app, SignupPage.signup_page, "Sign Up Page")
app.add_page(app, BookPage.book_page, "Book Page")

app.start_app()
