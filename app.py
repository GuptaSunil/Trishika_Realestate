import os
from datetime import datetime

from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_mail import Mail, Message

from database import (
    get_listings,
    get_listings_by_type,
    init_db,
    save_inquiry,
    get_inquiries,
    get_inquiries_count,
)

app = Flask(__name__)
app.config["DATABASE"] = os.path.join(os.path.dirname(__file__), "realestate.db")
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")

# Email Configuration
app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME", "")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD", "")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER", "noreply@trishikaproperties.com")

mail = Mail(app)

# Admin email to receive enquiries
ADMIN_EMAIL = "guPta.sunil561@gmail.com"

# Simple admin credentials (in-memory). For production, use a proper user store.
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")


def setup_database():
    init_db(app.config["DATABASE"])


def admin_required(func):
    def wrapper(*args, **kwargs):
        if not session.get("admin_logged_in"):
            # Inform the user they must login first
            flash("Please sign in to access the admin area.", "error")
            return redirect(url_for("admin_login"))
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


def send_enquiry_email(name: str, email: str, phone: str, property_name: str, message: str) -> bool:
    """Send enquiry email to admin and confirmation to user."""
    try:
        # Email to admin
        admin_msg = Message(
            subject=f"New Enquiry: {property_name}",
            recipients=[ADMIN_EMAIL],
            html=f"""
            <h2>New Property Enquiry</h2>
            <p><strong>Name:</strong> {name}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Phone:</strong> {phone or 'Not provided'}</p>
            <p><strong>Property:</strong> {property_name}</p>
            <p><strong>Message:</strong></p>
            <p>{message}</p>
            """
        )
        mail.send(admin_msg)
        
        # Confirmation email to user
        confirm_msg = Message(
            subject="We received your enquiry - Trishika Properties",
            recipients=[email],
            html=f"""
            <h2>Thank you for your enquiry!</h2>
            <p>Dear {name},</p>
            <p>We have received your enquiry for <strong>{property_name}</strong> and will get back to you shortly.</p>
            <p>Your Message: {message}</p>
            <p>Best regards,<br>Trishika Properties Team</p>
            """
        )
        mail.send(confirm_msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


@app.before_request
def ensure_database():
    setup_database()


@app.route("/")
def home():
    all_listings = get_listings(app.config["DATABASE"])
    outright_listings = get_listings_by_type(app.config["DATABASE"], "Outright")
    rental_listings = get_listings_by_type(app.config["DATABASE"], "Rental")
    pg_listings = get_listings_by_type(app.config["DATABASE"], "PG")
    return render_template(
        "index.html",
        listings=all_listings,
        outright_count=len(outright_listings),
        rental_count=len(rental_listings),
        pg_count=len(pg_listings),
        active_page="home",
    )


@app.route("/outright")
def outright():
    listings = get_listings_by_type(app.config["DATABASE"], "Outright")
    return render_template(
        "listings.html",
        listings=listings,
        page_title="Outright Listings",
        page_description="Buy your ideal home with trusted outright property options.",
        active_page="outright",
    )


@app.route("/rentals")
def rentals():
    listings = get_listings_by_type(app.config["DATABASE"], "Rental")
    return render_template(
        "listings.html",
        listings=listings,
        page_title="Rental Listings",
        page_description="Explore premium rental homes available across top neighborhoods.",
        active_page="rentals",
    )


@app.route("/pg")
def pg():
    listings = get_listings_by_type(app.config["DATABASE"], "PG")
    return render_template(
        "listings.html",
        listings=listings,
        page_title="PG Listings for Boys & Girls",
        page_description="Browse clean and secure PG homes for boys and girls across top Indian cities.",
        active_page="pg",
    )


@app.route("/enquiry", methods=["GET", "POST"])
def enquiry():
    sent = False
    property_names = [listing["title"] for listing in get_listings(app.config["DATABASE"])]

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        property_name = request.form.get("property_name", "General enquiry").strip()
        message = request.form.get("message", "").strip()

        if name and email and message:
            save_inquiry(
                app.config["DATABASE"],
                name,
                email,
                phone,
                property_name,
                message,
            )
            # Send email notification
            send_enquiry_email(name, email, phone, property_name, message)
            sent = True

    return render_template(
        "enquiry.html",
        sent=sent,
        property_names=property_names,
        active_page="enquiry",
    )


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("admin_inquiries"))
        flash("Invalid credentials", "error")

    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin_login"))


@app.route("/admin/inquiries")
@admin_required
def admin_inquiries():
    # Pagination and date filter
    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        page = 1
    per_page = 10
    date_from = request.args.get("date_from") or None
    date_to = request.args.get("date_to") or None
    today_date = datetime.now().strftime("%Y-%m-%d")

    offset = (max(page, 1) - 1) * per_page
    inquiries = get_inquiries(app.config["DATABASE"], limit=per_page, offset=offset, date_from=date_from, date_to=date_to)
    total = get_inquiries_count(app.config["DATABASE"], date_from=date_from, date_to=date_to)
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1

    return render_template(
        "admin_inquiries.html",
        inquiries=inquiries,
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        date_from=date_from,
        date_to=date_to,
        today_date=today_date,
    )


if __name__ == "__main__":
    setup_database()
    app.run(debug=True)
