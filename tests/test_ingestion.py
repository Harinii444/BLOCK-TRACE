import pytest

from backend.services.ingestion import (
    get_transactions,
    validate_address,
    _load_from_cache,
    _save_to_cache,
)


SAMPLE_WALLET = 'bc1q_sample_test_wallet'

VALID_TEST_WALLET = 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh'

SAMPLE_TX = [{
    'from': 'bc1q_A',
    'to': 'bc1q_B',
    'amount': 1.5,
    'time': 1709000000,
    'txid': 'txid_001'
}]


def test_cache_save_and_load(tmp_path, monkeypatch):
    """Saving then loading returns the same transaction list."""
    import backend.services.ingestion as ing

    monkeypatch.setattr(ing, 'CACHE_DIR', str(tmp_path))

    _save_to_cache(SAMPLE_WALLET, SAMPLE_TX)
    loaded = _load_from_cache(SAMPLE_WALLET)

    assert loaded == SAMPLE_TX


def test_cache_miss_returns_none(tmp_path, monkeypatch):
    """Loading from an empty cache dir returns None."""
    import backend.services.ingestion as ing

    monkeypatch.setattr(ing, 'CACHE_DIR', str(tmp_path))

    result = _load_from_cache('bc1q_not_cached_ever')

    assert result is None


def test_validate_address_empty():
    """Empty string raises ValueError."""
    with pytest.raises(ValueError):
        validate_address('')


def test_validate_address_invalid_prefix():
    """Non-Bitcoin address prefix raises ValueError."""
    with pytest.raises(ValueError):
        validate_address('ETH_not_bitcoin_address')


def test_validate_address_valid():
    """Known-valid Bitcoin address passes without exception."""
    validate_address(VALID_TEST_WALLET)


def test_get_transactions_uses_cache(tmp_path, monkeypatch):
    """get_transactions returns cached data without hitting API."""
    import backend.services.ingestion as ing

    monkeypatch.setattr(ing, 'CACHE_DIR', str(tmp_path))

    _save_to_cache(VALID_TEST_WALLET, SAMPLE_TX)

    result = get_transactions(VALID_TEST_WALLET)

    assert result == SAMPLE_TX


def test_get_transactions_output_structure(tmp_path, monkeypatch):
    """Each tx dict has all required keys."""
    import backend.services.ingestion as ing

    monkeypatch.setattr(ing, 'CACHE_DIR', str(tmp_path))

    _save_to_cache(VALID_TEST_WALLET, SAMPLE_TX)

    txs = get_transactions(VALID_TEST_WALLET)

    for tx in txs:
        assert set(tx.keys()) >= {'from', 'to', 'amount', 'time', 'txid'}