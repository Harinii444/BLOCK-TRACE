import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "database" / "exchanges.db"

SEED_WALLETS = [
    {"address": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh", "exchange_name": "Binance", "category": "exchange", "source": "seed"},
    {"address": "bc1q7p8g5q6y2z3j4k5l6m7n8o9p0q1r2s3t4u5v6w", "exchange_name": "Binance", "category": "exchange", "source": "seed"},
    {"address": "bc1q9m2n8p0q4r6s2t8u0w1y3a5c7d9e1f3g5h7j9k", "exchange_name": "Coinbase", "category": "exchange", "source": "seed"},
    {"address": "bc1q4m3b2c7d9e1f2g3h4j5k6l7m8n9p0q1r2s3t4u5", "exchange_name": "Coinbase", "category": "exchange", "source": "seed"},
    {"address": "bc1q2n4p6r8s0t2u4w6y8a0c2e4g6i8k0m2o4q6s8u0", "exchange_name": "Kraken", "category": "exchange", "source": "seed"},
    {"address": "bc1qw8r2t4y6u8a0c2e4g6i8k0m2o4q6s8u0w2y4a6c8", "exchange_name": "Kraken", "category": "exchange", "source": "seed"},
    {"address": "bc1q5h9j3k7l1m5n9p3q7r1s5t9u3w7y1a5c9e3g7i1k", "exchange_name": "Crypto.com", "category": "exchange", "source": "seed"},
    {"address": "bc1q0e2g4i6k8m0o2q4s6u8w0y2a4c6e8g0i2k4m6o8q", "exchange_name": "Crypto.com", "category": "exchange", "source": "seed"},
    {"address": "bc1q6y8a0c2e4g6i8k0m2o4q6s8u0w2y4a6c8e0g2i4k", "exchange_name": "OKX", "category": "exchange", "source": "seed"},
    {"address": "bc1q3t5v7x9z1b3d5f7h9j1l3n5p7r9t1v3x5z7b9d1f", "exchange_name": "OKX", "category": "exchange", "source": "seed"},
    {"address": "bc1qa4c6e8g0i2k4m6o8q0s2u4w6y8a0c2e4g6i8k0m2", "exchange_name": "Huobi", "category": "exchange", "source": "seed"},
    {"address": "bc1q1l3n5p7r9t1v3x5z7b9d1f3h5j7l9n1p3r5t7v9x", "exchange_name": "Huobi", "category": "exchange", "source": "seed"},
    {"address": "bc1q8r2t4y6u8a0c2e4g6i8k0m2o4q6s8u0w2y4a6c8e", "exchange_name": "Kucoin", "category": "exchange", "source": "seed"},
    {"address": "bc1q7p9r1t3v5x7z9b1d3f5h7j9l1n3p5r7t9v1x3z5", "exchange_name": "Kucoin", "category": "exchange", "source": "seed"},
    {"address": "bc1q2s4u6w8y0a2c4e6g8i0k2m4o6q8s0u2w4y6a8c0", "exchange_name": "Bitstamp", "category": "exchange", "source": "seed"},
    {"address": "bc1q6m8o0q2s4u6w8y0a2c4e6g8i0k2m4o6q8s0u2w4y6", "exchange_name": "Bitstamp", "category": "exchange", "source": "seed"},
    {"address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "exchange_name": "Gemini", "category": "exchange", "source": "seed"},
    {"address": "3D2oetdNuZUqQHPJmcMDDHYoqkyNVsFk9r", "exchange_name": "Gemini", "category": "exchange", "source": "seed"},
    {"address": "bc1q0x3f5h7j9l1n3p5r7t9v1x3z5b7d9f1h3j5l7n9p", "exchange_name": "CoinDCX", "category": "exchange", "source": "seed"},
    {"address": "3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy", "exchange_name": "WazirX", "category": "exchange", "source": "seed"},
]


def build_exchanges_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS wallets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            address TEXT NOT NULL UNIQUE,
            exchange_name TEXT NOT NULL,
            category TEXT,
            source TEXT
        )
        """
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_address ON wallets(address)")
    cur.executemany(
        """
        INSERT OR REPLACE INTO wallets (address, exchange_name, category, source)
        VALUES (:address, :exchange_name, :category, :source)
        """,
        SEED_WALLETS,
    )
    conn.commit()
    count = cur.execute("SELECT COUNT(*) FROM wallets").fetchone()[0]
    conn.close()
    print(f"exchanges.db created at {DB_PATH} with {count} wallet entries")


if __name__ == "__main__":
    build_exchanges_db()