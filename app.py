
# (Route moved below app = Flask(__name__))


    # (Route moved below app = Flask(__name__))
import sqlite3
import mimetypes
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mail import Mail, Message
import re

mimetypes.add_type("image/webp", ".webp")

app = Flask(__name__)
app.secret_key = "supriya_secret"  # Needed for cart sessions

# Flask-Mail configuration (using Gmail - free)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'supriyashyam1998@gmail.com'  # Your Gmail
app.config['MAIL_PASSWORD'] = 'your_app_password'    # Replace with Gmail app password
app.config['MAIL_DEFAULT_SENDER'] = 'supriyashyam1998@gmail.com'

mail = Mail(app)

# Shop phone number for WhatsApp notifications
SHOP_PHONE = '+91-7890565431'  # Your phone number

SHOP_EMAIL = 'supriyashyam1998@gmail.com'  # Your email for notifications

def send_notification(to_email, subject, body):
    if app.config['MAIL_PASSWORD'] == 'your_app_password':
        # Demo mode - print WhatsApp-ready messages
        print(f"\n=== WHATSAPP NOTIFICATION (Demo Mode) ===")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"Body:\n{body}")
        
        # Show WhatsApp-ready message for manual sending
        if "New Order" in subject:
            # Shop notification - send to shop owner
            whatsapp_text = f"🚨 *NEW ORDER ALERT* 🚨\n\n{body.replace('New Order Details:', '').strip()}\n\n🍳 *Time to cook!* 🍳"
            print(f"\n=== WHATSAPP MESSAGE (Send to Yourself) ===")
            print(f"Send to: {SHOP_PHONE}")
            print(f"Message:\n{whatsapp_text}")
        elif "being prepared" in subject:
            whatsapp_text = "🍳 *Order Update*\nHi! Your order is now being prepared. We'll notify you when it's ready!\n\nEstimated time: 20-30 minutes\n\nThank you for choosing Supriya's Curry Point 🍛"
            print(f"\n=== WHATSAPP MESSAGE (Copy & Send to Customer) ===")
            print(f"Message:\n{whatsapp_text}")
        elif "is ready" in subject:
            whatsapp_text = "🚀 *Order Ready!*\nHi! Your order is ready for delivery!\n\nEstimated delivery: 10-15 minutes\n\nThank you for choosing Supriya's Curry Point 🍛"
            print(f"\n=== WHATSAPP MESSAGE (Copy & Send to Customer) ===")
            print(f"Message:\n{whatsapp_text}")
        elif "delivered" in subject:
            whatsapp_text = "✅ *Order Delivered!*\nHi! Your order has been delivered successfully. Enjoy your meal!\n\nPlease share your feedback: Visit our website and track your order to leave a review.\n\nThank you for choosing Supriya's Curry Point 🍛"
            print(f"\n=== WHATSAPP MESSAGE (Copy & Send to Customer) ===")
            print(f"Message:\n{whatsapp_text}")
        
        print("=" * 60)
        return
    
    try:
        msg = Message(subject, recipients=[to_email])
        msg.body = body
        mail.send(msg)
        print(f"Email sent to {to_email}: {subject}")
    except Exception as e:
        print(f"Failed to send email: {e}")
        # Fallback to console output
        print(f"\n=== EMAIL NOTIFICATION (Fallback) ===")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"Body:\n{body}")
        print("=" * 40)


# ------------------ Home Page ------------------
@app.route("/", methods=["GET", "POST"])
def home():
    conn = sqlite3.connect("curry.db")
    cur = conn.cursor()
    cur.execute("SELECT id, name, price, image_url FROM menu")
    curries = [dict(id=row[0], name=row[1], price=row[2], image_url=row[3]) for row in cur.fetchall()]
    conn.close()

    # Cart logic
    cart = session.get("cart", {})
    return render_template("home.html", curries=curries, cart=cart)

# ------------------ About Page ------------------
@app.route("/about")
def about():
    return render_template("about.html")

# ------------------ Menu Page ------------------
@app.route("/menu")
def menu():
    conn = sqlite3.connect("curry.db")
    cur = conn.cursor()
    cur.execute("SELECT id, name, price, image_url FROM menu")
    items = cur.fetchall()
    
    # Get average ratings for each item
    menu_with_ratings = []
    for item in items:
        item_id, name, price, image_url = item
        # Find reviews for this item (by name in order items)
        cur.execute("""
            SELECT AVG(r.rating) as avg_rating, COUNT(r.rating) as review_count 
            FROM reviews r 
            JOIN orders o ON r.order_id = o.id 
            WHERE o.items LIKE ?
        """, (f"%{name}%",))
        rating_data = cur.fetchone()
        avg_rating = rating_data[0] if rating_data[0] else 0
        review_count = rating_data[1] if rating_data[1] else 0
        menu_with_ratings.append((item_id, name, price, image_url, avg_rating, review_count))
    
    conn.close()
    return render_template("menu.html", items=menu_with_ratings)


# ------------------ Add to Cart (with quantity) ------------------
@app.route("/add_to_cart/<int:curry_id>", methods=["POST"])
def add_to_cart(curry_id):
    # Get curry name by id
    conn = sqlite3.connect("curry.db")
    cur = conn.cursor()
    cur.execute("SELECT name FROM menu WHERE id = ?", (curry_id,))
    result = cur.fetchone()
    conn.close()
    if not result:
        return redirect(url_for("home"))
    curry_name = result[0]

    cart = session.get("cart", {})
    if curry_name in cart:
        cart[curry_name] += 1
    else:
        cart[curry_name] = 1
    session["cart"] = cart
    return redirect(url_for("menu"))


# ------------------ Cart Page ------------------
@app.route("/cart")
def cart():
    cart_items = []
    cart = session.get("cart", {})
    if cart:
        conn = sqlite3.connect("curry.db")
        cur = conn.cursor()
        names = list(cart.keys())
        if names:
            placeholders = ",".join(["?"] * len(names))
            cur.execute(f"SELECT id, name, price, image_url FROM menu WHERE name IN ({placeholders})", names)
            menu_items = cur.fetchall()
            for item_id, name, price, image_url in menu_items:
                quantity = cart.get(name, 0)
                cart_items.append((item_id, name, price, image_url, quantity))
        conn.close()
    return render_template("cart.html", cart_items=cart_items)

# ------------------ Order Page ------------------
@app.route("/order", methods=["GET", "POST"])
def order():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form.get("email", "")
        address = request.form["address"]
        payment_method = request.form["payment_method"]

        cart = session.get("cart", {})
        if cart:
            conn = sqlite3.connect("curry.db")
            cur = conn.cursor()
            names = list(cart.keys())
            if names:
                placeholders = ",".join(["?"] * len(names))
                cur.execute(f"SELECT name, price FROM menu WHERE name IN ({placeholders})", names)
                menu_items = cur.fetchall()
                # items_str: "Paneer Butter Masala x2, Dal Fry x1"
                items_str = ", ".join([f"{name} x{cart[name]}" for name, price in menu_items])
                total = sum(price * cart[name] for name, price in menu_items)
            else:
                items_str = ""
                total = 0
            cur.execute("INSERT INTO orders (name, phone, email, address, items, total, status, payment_method) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (name, phone, email, address, items_str, total, 'Pending', payment_method))
            order_id = cur.lastrowid
            conn.commit()
            conn.close()
            # Send email to shop owner
            shop_subject = f"New Order #{order_id} - Supriya's Curry Point"
            shop_body = f"New Order Details:\n\nOrder ID: {order_id}\nCustomer: {name}\nPhone: {phone}\nEmail: {email}\nAddress: {address}\nItems: {items_str}\nTotal: ₹{total}\nPayment: {payment_method}"
            send_notification(SHOP_EMAIL, shop_subject, shop_body)
            session.pop("cart", None)  # Clear cart after ordering
            return f"""
            <h2>Thank you {name}, your order has been placed!</h2>
            <p><strong>Order ID: {order_id}</strong></p>
            <p>Estimated delivery time: 30-45 minutes</p>
            <p>You can track your order status at: <a href="{url_for('track_order', _external=True)}">Track Order</a></p>
            <p>Or use Order ID: {order_id} on the Track Order page.</p>
            """
        else:
            return "No items in cart"
    return render_template("order.html")

# ------------------ Orders Page ------------------
@app.route("/orders", methods=["GET", "POST"])
def orders():
    if request.method == "POST":
        password = request.form.get("password")
        if password == "admin123":  # Change this password
            session['admin'] = True
            conn = sqlite3.connect("curry.db")
            cur = conn.cursor()
            cur.execute("SELECT id, name, phone, email, address, items, total, status, payment_method, order_date FROM orders")
            orders_data = cur.fetchall()
            conn.close()
            return render_template("orders.html", orders=orders_data)
        else:
            return render_template("orders.html", error="Incorrect password")
    
    # GET request - check session
    if session.get('admin'):
        conn = sqlite3.connect("curry.db")
        cur = conn.cursor()
        cur.execute("SELECT id, name, phone, email, address, items, total, status, payment_method, order_date FROM orders")
        orders_data = cur.fetchall()
        conn.close()
        return render_template("orders.html", orders=orders_data)
    else:
        return render_template("orders.html")

# ------------------ Update Order Status ------------------
@app.route("/update_status/<int:order_id>/<status>")
def update_status(order_id, status):
    if not session.get('admin'):
        return redirect(url_for('orders'))
    valid_statuses = ['Pending', 'Preparing', 'Ready', 'Delivered']
    if status not in valid_statuses:
        return "Invalid status"
    conn = sqlite3.connect("curry.db")
    cur = conn.cursor()
    cur.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
    # Send status update email to customer if email provided
    cur.execute("SELECT email, name FROM orders WHERE id = ?", (order_id,))
    result = cur.fetchone()
    customer_email = result[0]
    customer_name = result[1]
    if customer_email and status in ['Preparing', 'Ready', 'Delivered']:
        if status == 'Preparing':
            subject = f"Your order #{order_id} is being prepared"
            body = f"Hi {customer_name},\n\nYour order #{order_id} is now being prepared. We'll notify you when it's ready!\n\nEstimated time: 20-30 minutes\n\nThank you for choosing Supriya's Curry Point."
        elif status == 'Ready':
            subject = f"Your order #{order_id} is ready"
            body = f"Hi {customer_name},\n\nYour order #{order_id} is ready and will be delivered soon!\n\nEstimated delivery: 10-15 minutes\n\nThank you for choosing Supriya's Curry Point."
        elif status == 'Delivered':
            subject = f"Your order #{order_id} has been delivered"
            body = f"Hi {customer_name},\n\nYour order #{order_id} has been delivered successfully! We hope you enjoy your meal.\n\nThank you for choosing Supriya's Curry Point."
        send_notification(customer_email, subject, body)
    conn.commit()
    conn.close()
    return redirect(url_for('orders'))

# ------------------ Logout ------------------
@app.route("/logout")
def logout():
    session.pop('admin', None)
    return redirect(url_for('orders'))

# ------------------ Track Order ------------------
@app.route("/track_order", methods=["GET", "POST"])
def track_order():
    if request.method == "POST":
        order_id = request.form.get("order_id")
        if order_id:
            conn = sqlite3.connect("curry.db")
            cur = conn.cursor()
            cur.execute("SELECT id, name, phone, address, items, total, status, payment_method, order_date FROM orders WHERE id = ?", (order_id,))
            order = cur.fetchone()
            conn.close()
            if order:
                return render_template("track_order.html", order=order)
            else:
                return render_template("track_order.html", error="Order not found")
    return render_template("track_order.html")

# ------------------ Submit Review ------------------
@app.route("/submit_review", methods=["POST"])
def submit_review():
    order_id = request.form.get("order_id")
    customer_name = request.form.get("customer_name")
    rating = request.form.get("rating")
    comment = request.form.get("comment", "")
    
    if order_id and rating:
        conn = sqlite3.connect("curry.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO reviews (order_id, customer_name, rating, comment) VALUES (?, ?, ?, ?)",
                    (order_id, customer_name, rating, comment))
        conn.commit()
        conn.close()
        return f"Thank you for your review! <a href='{url_for('menu')}'>Back to Menu</a>"
    
    return "Review submission failed"


# ------------------ Remove from Cart (by id) ------------------
@app.route("/remove_from_cart/<int:item_id>", methods=["POST"])
def remove_from_cart(item_id):
    cart = session.get("cart", {})
    # Find the name for this id
    conn = sqlite3.connect("curry.db")
    cur = conn.cursor()
    cur.execute("SELECT name FROM menu WHERE id = ?", (item_id,))
    result = cur.fetchone()
    conn.close()
    if result:
        item_name = result[0]
        if item_name in cart:
            cart.pop(item_name)
            session["cart"] = cart
    return redirect(url_for("cart"))

# ------------------ Run App ------------------
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
