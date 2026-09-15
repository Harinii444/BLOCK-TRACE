import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "database" / "exchanges.db"


def match_vasp(wallet_address: str) -> dict:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT exchange_name FROM wallets WHERE address = ?", (wallet_address,)
    )
    row = cur.fetchone()
    conn.close()
    if row:
        return {"vasp_match": row[0], "is_exchange": True}
    return {"vasp_match": None, "is_exchange": False}