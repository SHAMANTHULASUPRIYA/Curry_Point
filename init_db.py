import sqlite3

conn = sqlite3.connect("curry.db")
cur = conn.cursor()

# Reset table
cur.execute("DROP TABLE IF EXISTS menu")
cur.execute("""
CREATE TABLE menu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    price REAL,
    image_url TEXT
)
""")

# Create orders table
cur.execute("DROP TABLE IF EXISTS orders")
cur.execute("""
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT,
    email TEXT,
    address TEXT,
    items TEXT,
    total REAL,
    status TEXT DEFAULT 'Pending',
    payment_method TEXT,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Create reviews table
cur.execute("DROP TABLE IF EXISTS reviews")
cur.execute("""
CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    customer_name TEXT,
    rating INTEGER,
    comment TEXT,
    review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders (id)
)
""")

# Insert dishes with only filenames
cur.execute("INSERT INTO menu (name, price, image_url) VALUES (?, ?, ?)",
            ("Paneer Butter Masala", 120, "paneer_curry.jpg"))
cur.execute("INSERT INTO menu (name, price, image_url) VALUES (?, ?, ?)",
            ("Chicken Curry", 150, "chicken_curry.jpg"))
cur.execute("INSERT INTO menu (name, price, image_url) VALUES (?, ?, ?)",
            ("Dal Fry", 80, "daal_curry.jpeg"))
cur.execute("INSERT INTO menu (name, price, image_url) VALUES (?, ?, ?)",
            ("Potato Curry", 70, "potato_curry.jpg"))
cur.execute("INSERT INTO menu (name, price, image_url) VALUES (?, ?, ?)",
            ("Brinjal Curry", 75, "brinjal_curry.jpg"))
cur.execute("INSERT INTO menu (name, price, image_url) VALUES (?, ?, ?)",
            ("Egg Curry", 90, "egg_curry.jpg"))
cur.execute("INSERT INTO menu (name, price, image_url) VALUES (?, ?, ?)",
            ("Tomato Curry", 150, "tomato_curry.webp"))

conn.commit()
conn.close()

print("Database fixed with correct image filenames!")
