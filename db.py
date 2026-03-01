import sqlite3
import json
from contextlib import contextmanager

DATABASE = "gift_bot.db"

@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS filters (
                user_id INTEGER PRIMARY KEY,
                floor_price INTEGER DEFAULT 0,
                models TEXT DEFAULT '[]',
                backgrounds TEXT DEFAULT '[]',
                gift_names TEXT DEFAULT '[]',
                price_deviation INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sent_gifts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gift_id TEXT UNIQUE NOT NULL,
                platform TEXT NOT NULL,
                price INTEGER NOT NULL,
                model TEXT,
                background TEXT,
                title TEXT,
                url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    print("База данных создана/проверена")

def add_user(telegram_id):
    with get_db() as conn:
        try:
            cur = conn.execute(
                "INSERT INTO users (telegram_id) VALUES (?)",
                (telegram_id,)
            )
            user_id = cur.lastrowid
            conn.execute(
                "INSERT INTO filters (user_id, floor_price, models, backgrounds, gift_names, price_deviation) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, 0, '[]', '[]', '[]', 0)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def remove_user(telegram_id):
    with get_db() as conn:
        conn.execute("DELETE FROM users WHERE telegram_id = ?", (telegram_id,))
        conn.commit()
        return conn.total_changes > 0

def get_all_users(only_active=True):
    with get_db() as conn:
        if only_active:
            cur = conn.execute("SELECT telegram_id FROM users WHERE is_active=1")
        else:
            cur = conn.execute("SELECT telegram_id FROM users")
        return [row["telegram_id"] for row in cur.fetchall()]

def user_exists(telegram_id):
    with get_db() as conn:
        cur = conn.execute("SELECT 1 FROM users WHERE telegram_id=?", (telegram_id,))
        return cur.fetchone() is not None

def is_user_active(telegram_id):
    with get_db() as conn:
        cur = conn.execute("SELECT is_active FROM users WHERE telegram_id=?", (telegram_id,))
        row = cur.fetchone()
        return row and row["is_active"] == 1

def get_user_filters(telegram_id):
    with get_db() as conn:
        cur = conn.execute("""
            SELECT f.floor_price, f.models, f.backgrounds, f.gift_names, f.price_deviation
            FROM users u
            JOIN filters f ON u.id = f.user_id
            WHERE u.telegram_id = ?
        """, (telegram_id,))
        row = cur.fetchone()
        if row:
            return {
                "floor_price": row["floor_price"],
                "models": json.loads(row["models"]),
                "backgrounds": json.loads(row["backgrounds"]),
                "gift_names": json.loads(row["gift_names"]) if row["gift_names"] else [],
                "price_deviation": row["price_deviation"] or 0
            }
        return {"floor_price": 0, "models": [], "backgrounds": [], "gift_names": [], "price_deviation": 0}

def update_filters(telegram_id, floor_price=None, models=None, backgrounds=None):
    with get_db() as conn:
        cur = conn.execute("SELECT id FROM users WHERE telegram_id=?", (telegram_id,))
        row = cur.fetchone()
        if not row:
            return False
        user_id = row["id"]

        updates = []
        params = []
        if floor_price is not None:
            updates.append("floor_price = ?")
            params.append(floor_price)
        if models is not None:
            updates.append("models = ?")
            params.append(json.dumps(models))
        if backgrounds is not None:
            updates.append("backgrounds = ?")
            params.append(json.dumps(backgrounds))

        if updates:
            query = f"UPDATE filters SET {', '.join(updates)} WHERE user_id = ?"
            params.append(user_id)
            conn.execute(query, params)
            conn.commit()
        return True

def update_gift_names(telegram_id, gift_names=None):
    with get_db() as conn:
        cur = conn.execute("SELECT id FROM users WHERE telegram_id=?", (telegram_id,))
        row = cur.fetchone()
        if not row:
            return False
        user_id = row["id"]
        
        if gift_names is not None:
            conn.execute(
                "UPDATE filters SET gift_names = ? WHERE user_id = ?",
                (json.dumps(gift_names), user_id)
            )
            conn.commit()
        return True

def update_price_deviation(telegram_id, deviation):
    with get_db() as conn:
        cur = conn.execute("SELECT id FROM users WHERE telegram_id=?", (telegram_id,))
        row = cur.fetchone()
        if not row:
            return False
        user_id = row["id"]
        
        conn.execute(
            "UPDATE filters SET price_deviation = ? WHERE user_id = ?",
            (deviation, user_id)
        )
        conn.commit()
        return True

def gift_already_sent(gift_id):
    with get_db() as conn:
        cur = conn.execute("SELECT 1 FROM sent_gifts WHERE gift_id=?", (gift_id,))
        return cur.fetchone() is not None

def add_sent_gift(gift_id, platform, price, model, background, title, url):
    with get_db() as conn:
        try:
            conn.execute("""
                INSERT INTO sent_gifts (gift_id, platform, price, model, background, title, url)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (gift_id, platform, price, model, background, title, url))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def get_all_users_full():
    with get_db() as conn:
        cur = conn.execute("""
            SELECT u.telegram_id, u.is_active, f.floor_price
            FROM users u
            LEFT JOIN filters f ON u.id = f.user_id
            ORDER BY u.created_at DESC
        """)
        return [dict(row) for row in cur.fetchall()]
