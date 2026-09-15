import pytest

from scripts.seed_exchanges import SEED_WALLETS, build_exchanges_db


@pytest.fixture(scope="module", autouse=True)
def seeded_db():
    build_exchanges_db()


def test_known_exchange_wallet_returns_exchange_name(seeded_db):
    from backend.services.vasp_matcher import match_vasp

    known = SEED_WALLETS[0]
    result = match_vasp(known["address"])
    assert result["vasp_match"] == known["exchange_name"]
    assert result["is_exchange"] is True


def test_unknown_wallet_returns_none(seeded_db):
    from backend.services.vasp_matcher import match_vasp

    result = match_vasp("bc1qunknown53f9dz2g9k3j2q3j2q3j2q3j2q3j2q")
    assert result["vasp_match"] is None
    assert result["is_exchange"] is False