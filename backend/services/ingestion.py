import json
import os
import time
import requests


# Configuration
CACHE_DIR = os.path.join(
    os.path.dirname(__file__),
    '..',
    '..',
    'data',
    'cache'
)

BLOCKSTREAM_BASE = 'https://blockstream.info/api'

os.makedirs(CACHE_DIR, exist_ok=True)
def _cache_path(wallet_address: str) -> str:
    """Return the file path for caching a wallet's transactions."""
    return os.path.join(CACHE_DIR, f'{wallet_address}.json')


def _load_from_cache(wallet_address: str):
    """Return cached tx list if file exists, else return None."""
    path = _cache_path(wallet_address)

    if os.path.exists(path):
        with open(path, 'r') as f:
            data = json.load(f)

        print(f'[Ingestion] Cache HIT for {wallet_address}')
        return data['transactions']

    print(f'[Ingestion] Cache MISS for {wallet_address}')
    return None

def _save_to_cache(wallet_address: str, transactions: list):
    """Save the fetched transactions to a JSON cache file."""
    path = _cache_path(wallet_address)

    payload = {
        'wallet': wallet_address,
        'fetched_at': int(time.time()),
        'transactions': transactions,
    }

    with open(path, 'w') as f:
        json.dump(payload, f, indent=2)

    print(f'[Ingestion] Cached {len(transactions)} txs for {wallet_address}')

def _fetch_from_api(wallet_address: str) -> list:
    """Call Blockstream API and return raw transaction list."""
    url = f'{BLOCKSTREAM_BASE}/address/{wallet_address}/txs'

    print(f'[Ingestion] Fetching from API: {url}')

    response = requests.get(url, timeout=15)
    response.raise_for_status()

    return response.json()

def _parse_transactions(raw_txs: list, wallet_address: str) -> list:
    """
    Convert raw Blockstream tx list into the standard format.
    Output: [{ from, to, amount, time, txid }]
    """
    result = []

    for tx in raw_txs:
        txid = tx.get('txid', '')
        block_time = tx.get('status', {}).get('block_time', 0)

        # Extract sender wallets from vin
        senders = []

        for vin in tx.get('vin', []):
            prev = vin.get('prevout', {})
            addr = prev.get('scriptpubkey_address')

            if addr:
                senders.append(addr)

        from_wallet = senders[0] if senders else 'unknown'

        # Extract receiver wallets from vout
        for vout in tx.get('vout', []):
            to_wallet = vout.get('scriptpubkey_address')
            value_sat = vout.get('value', 0)

            amount_btc = value_sat / 1e8

            if to_wallet and amount_btc > 0:
                result.append({
                    'from': from_wallet,
                    'to': to_wallet,
                    'amount': round(amount_btc, 8),
                    'time': block_time,
                    'txid': txid,
                })

    return result

def validate_address(wallet_address: str):
    """Raise ValueError if the address doesn't look like a Bitcoin address."""
    if not wallet_address:
        raise ValueError('Wallet address cannot be empty.')

    if not wallet_address.startswith(('1', '3', 'bc1')):
        raise ValueError(f'Not a valid Bitcoin address: {wallet_address}')

    if not (25 <= len(wallet_address) <= 62):
        raise ValueError(
            f'Bitcoin address has unexpected length: {wallet_address}'
        )

def get_transactions(wallet_address: str) -> list:
    """
    Main public function. Always call THIS from other modules.

    1. Validates address
    2. Checks local cache
    3. If cache miss → calls Blockstream API → saves to cache
    4. Returns list of tx dicts in standard format
    """
    validate_address(wallet_address)

    # Step 1: try cache
    cached = _load_from_cache(wallet_address)

    if cached is not None:
        return cached

    # Step 2: call live API
    try:
        raw = _fetch_from_api(wallet_address)
    except requests.RequestException as e:
        raise ConnectionError(
            f'[Ingestion] Blockstream API failed for {wallet_address}: {e}'
        )

    # Step 3: parse & cache
    transactions = _parse_transactions(raw, wallet_address)
    _save_to_cache(wallet_address, transactions)

    return transactions