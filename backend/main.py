from fastapi import FastAPI, HTTPException
import pymysql
from pydantic import BaseModel
from typing import Optional
from datetime import date, timedelta
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs
import os

load_dotenv()

app = FastAPI()


# ------------------------
# Helper Function
# ------------------------
def get_connection():
    url = os.getenv("TIDB_URL")
    parsed = urlparse(url)
    params = parse_qs(parsed.query)

    return pymysql.connect(
        host=parsed.hostname,
        port=parsed.port or 4000,
        user=parsed.username,
        password=parsed.password,
        database=parsed.path.lstrip("/"),
        ssl={
            "ca": params.get("ssl_ca", [None])[0]
        },
        cursorclass=pymysql.cursors.DictCursor
    )


# ------------------------
# Models
# ------------------------
class Friend(BaseModel):
    name: str


class Category(BaseModel):
    name: str
    type: str
    has_friend: int


class Transaction(BaseModel):
    date: str
    category_id: int
    amount: float
    note: Optional[str] = None
    friend_id: Optional[int] = None


# ------------------------
# Categories APIs
# ------------------------
@app.get("/categories")
def get_categories():
    conn = get_connection()
    print(f"conn da {conn}")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories where id <> 1")
    data = cursor.fetchall()
    conn.close()
    return data


@app.post("/categories")
def add_category(category: Category):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO categories (name, type, has_friend) VALUES (%s, %s, %s)",
            (category.name, category.type, category.has_friend)
        )
        conn.commit()
    except:
        raise HTTPException(status_code=400, detail="Category already exists")
    finally:
        conn.close()
    return {"message": "Category added"}


@app.delete("/categories/{category_id}")
def delete_category(category_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM transactions WHERE category_id = %s",
        (category_id,)
    )
    row = cursor.fetchone()
    count = list(row.values())[0]

    if count > 0:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="You have recorded the transaction(s) in this category. You cannot delete this"
        )

    cursor.execute(
        "DELETE FROM categories WHERE id = %s",
        (category_id,)
    )
    conn.commit()
    conn.close()

    return {"message": "Category deleted"}


# ------------------------
# Friends APIs
# ------------------------
@app.get("/friends")
def get_friends():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM friends")
    data = cursor.fetchall()
    conn.close()
    return data


@app.post("/friends")
def add_friend(friend: Friend):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO friends (name) VALUES (%s)", (friend.name,))
        conn.commit()
    except:
        raise HTTPException(status_code=400, detail="Friend already exists")
    finally:
        conn.close()
    return {"message": "Friend added"}


@app.delete("/friends/{friend_id}")
def delete_friend(friend_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM transaction_friends WHERE friend_id = %s",
        (friend_id,)
    )
    row = cursor.fetchone()
    count = list(row.values())[0]

    if count > 0:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="You have recorded the transaction(s) with this friend. You cannot delete this"
        )
    cursor.execute("DELETE FROM friends WHERE id=%s", (friend_id,))
    conn.commit()
    conn.close()
    return {"message": "Friend deleted"}


# ------------------------
# Transactions APIs
# ------------------------

@app.get("/balance")
def get_balance():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            COALESCE((SELECT amount FROM transactions WHERE id = 1), -1) AS opening_balance,
            COALESCE(SUM(CASE WHEN c.type = 'income' THEN t.amount ELSE 0 END), 0) AS income,
            COALESCE(SUM(CASE WHEN c.type = 'expense' THEN t.amount ELSE 0 END), 0) AS expense,
            COUNT(t.id) as total_count
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
    """)

    result = cursor.fetchone()

    opening_balance = result["opening_balance"] or 0
    income = result["income"] or 0
    expense = result["expense"] or 0
    total_count = result["total_count"]

    if total_count == 0:
        conn.close()
        return {
            "Opening_balance": -1,
            "current_balance": -1,
            "total_income": -1,
            "total_expense": -1
        }

    balance = income - expense

    conn.close()

    return {
        "Opening_balance": opening_balance,
        "current_balance": balance,
        "total_income": income,
        "total_expense": expense
    }


@app.get("/transactions")
def get_transactions(
    start_date: date = None,
    end_date: date = None
):
    if end_date is None:
        end_date = date.today()
    if start_date is None:
        start_date = end_date - timedelta(days=30)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id, t.date, c.name, c.type, t.amount, t.note
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.id <> 1
          AND t.date >= %s
          AND t.date <= %s
        ORDER BY t.date DESC;
    """, (str(start_date), str(end_date)))
    data = cursor.fetchall()
    conn.close()
    return data

@app.get("/all_transactions")
def get_all_transactions():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id, t.date, c.name, c.type, t.amount, t.note
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.id <> 1 ORDER BY t.date DESC;
    """)
    data = cursor.fetchall()
    conn.close()
    return data


@app.post("/transactions")
def add_transaction(tx: Transaction):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO transactions (date, category_id, amount, note) VALUES (%s, %s, %s, %s)",
        (tx.date, tx.category_id, tx.amount, tx.note)
    )

    tx_id = cursor.lastrowid

    if tx.friend_id:
        cursor.execute(
            "INSERT INTO transaction_friends (transaction_id, friend_id) VALUES (%s, %s)",
            (tx_id, tx.friend_id)
        )

    conn.commit()
    conn.close()
    return {"message": "Transaction added"}

@app.put("/transactions/{tx_id}")
def update_transaction(tx_id: int, tx: Transaction):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE transactions
        SET date=%s, category_id=%s, amount=%s, note=%s
        WHERE id=%s
    """, (tx.date, tx.category_id, tx.amount, tx.note, tx_id))

    cursor.execute("DELETE FROM transaction_friends WHERE transaction_id=%s", (tx_id,))

    if tx.friend_id:
        cursor.execute(
            "INSERT INTO transaction_friends (transaction_id, friend_id) VALUES (%s, %s)",
            (tx_id, tx.friend_id)
        )

    conn.commit()
    conn.close()

    return {"message": "Transaction updated"}

@app.delete("/transactions/{tx_id}")
def delete_transaction(tx_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM transaction_friends WHERE transaction_id=%s", (tx_id,))
    cursor.execute("DELETE FROM transactions WHERE id=%s", (tx_id,))

    conn.commit()
    conn.close()

    return {"message": "Transaction deleted"}

@app.put("/friends/{f_id}")
def update_friend(f_id: int, f: Friend):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE friends
        SET name=%s
        WHERE id=%s
    """, (f.name, f_id))

    conn.commit()
    conn.close()

    return {"message": "Friend updated"}

@app.put("/Categories/{cat_id}")
def update_category(cat_id: int, cat: Category):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE categories
        SET name=%s
        WHERE id=%s
    """, (cat.name, cat_id))

    conn.commit()
    conn.close()

    return {"message": "Category updated"}

@app.get("/friends/transactions/{tx_id}")
def get_friend_for_transaction(tx_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT f.name
        FROM transaction_friends tf
        JOIN friends f ON f.id = tf.friend_id
        WHERE tf.transaction_id = %s
    """, (tx_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(
            status_code=404,
            detail="No friend found for this transaction"
        )

    return {"friend": row["name"]}

@app.get("/transactions/friends")
def get_friends_transaction_details():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            f.name AS name,

            COALESCE(SUM(CASE 
                WHEN c.type = 'income' THEN t.amount 
                ELSE 0 
            END), 0) AS Income,

            COALESCE(SUM(CASE 
                WHEN c.type = 'expense' THEN t.amount 
                ELSE 0 
            END), 0) AS Expense

        FROM friends f

        LEFT JOIN transaction_friends tf 
            ON f.id = tf.friend_id

        LEFT JOIN transactions t 
            ON tf.transaction_id = t.id

        LEFT JOIN categories c 
            ON t.category_id = c.id

        GROUP BY f.id, f.name
        ORDER BY f.name;
    """)

    data = cursor.fetchall()

    conn.close()
    return data