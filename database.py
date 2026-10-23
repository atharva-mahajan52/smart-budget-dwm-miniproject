import sqlite3

def init_db():
    conn = sqlite3.connect('budget_dwm.db')
    cursor = conn.cursor()
    
    # 1. Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            monthly_income REAL NOT NULL
        )
    ''')
    
    # 2. Expense Categories Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            is_discretionary INTEGER DEFAULT 0
        )
    ''')
    
    # 3. Transactions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            tx_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            is_weekend INTEGER DEFAULT 0,
            risk_label TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    
    # Seed Data (Small, realistic training dataset for DWM calculations)
    cursor.execute("SELECT COUNT(*) FROM transactions")
    if cursor.fetchone()[0] == 0:
        seed_data = [
            (1, 'Groceries', 450.0, 0, 'Safe'),
            (1, 'Dining', 1800.0, 1, 'High_Risk'),
            (1, 'Books/Stationery', 600.0, 0, 'Safe'),
            (1, 'Clubbing/Party', 2800.0, 1, 'High_Risk'),
            (1, 'Transit/Bus', 250.0, 0, 'Safe'),
            (1, 'Electronics Gadget', 4200.0, 1, 'High_Risk'),
            (1, 'Cafeteria Snack', 150.0, 0, 'Safe'),
            (1, 'Concert Ticket', 2200.0, 1, 'High_Risk'),
            (1, 'Pharmacy/Meds', 350.0, 0, 'Safe'),
            (1, 'Gaming Subscription', 1200.0, 1, 'Moderate_Risk'),
            (1, 'Printouts/Academic', 180.0, 0, 'Safe'),
            (1, 'Weekend Outing', 1600.0, 1, 'Moderate_Risk')
        ]
        cursor.executemany(
            "INSERT INTO transactions (user_id, category, amount, is_weekend, risk_label) VALUES (?, ?, ?, ?, ?)",
            seed_data
        )
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database budget_dwm.db initialized successfully.")
