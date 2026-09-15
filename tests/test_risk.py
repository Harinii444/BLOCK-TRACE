import pytest

from backend.services.risk_engine import calculate_risk


def make_hop(**overrides):
    hop = {
        "wallet": "bc1qwallet",
        "hop_number": 1,
        "from_wallet": "bc1qsender",
        "to_wallet": "bc1qreceiver",
        "txid": "txid123",
        "amount": 0.5,
        "time": 1709000000,
    }
    hop.update(overrides)
    return hop


def test_high_value_amount_adds_40_points():
    hop = make_hop(amount=2.0)
    result = calculate_risk(hop)
    assert result["risk_score"] == 40
    assert "High-value transaction: +40" in result["reasons"]


def test_rapid_movement_adds_30_points():
    hop = make_hop(to_wallet="bc1qwallet", time=1709000000)
    traced_path = [
        make_hop(wallet="bc1qwallet", to_wallet="bc1qwallet", time=1709000000),
        make_hop(from_wallet="bc1qwallet", time=1709000300),
    ]
    result = calculate_risk(hop, traced_path)
    assert result["risk_score"] == 30
    assert "Rapid onward movement: +30" in result["reasons"]


def test_peel_chain_adds_30_points():
    hop = make_hop(wallet="bc1qsplitter", to_wallet="bc1qsplitter")
    traced_path = [
        make_hop(wallet="bc1qsplitter", to_wallet="bc1qsplitter", amount=0.1),
        make_hop(from_wallet="bc1qsplitter", amount=0.2),
        make_hop(from_wallet="bc1qsplitter", amount=0.3),
    ]
    result = calculate_risk(hop, traced_path)
    assert result["risk_score"] == 30
    assert "Peel-chain pattern: +30" in result["reasons"]


def test_no_patterns_scores_zero():
    hop = make_hop(amount=0.1)
    traced_path = [
        make_hop(wallet="bc1qwallet", to_wallet="bc1qwallet", amount=0.1),
        make_hop(from_wallet="someotherwallet", amount=0.5),
    ]
    result = calculate_risk(hop, traced_path)
    assert result["risk_score"] == 0
    assert result["reasons"] == []


def test_all_three_patterns_scores_capped_at_100():
    hop = make_hop(amount=50.0, wallet="bc1qbad", to_wallet="bc1qbad", time=1709000000)
    traced_path = [
        make_hop(wallet="bc1qbad", to_wallet="bc1qbad", amount=50.0, time=1709000000),
        make_hop(from_wallet="bc1qbad", amount=0.2, time=1709000300),
        make_hop(from_wallet="bc1qbad", amount=0.3, time=1709000600),
    ]
    result = calculate_risk(hop, traced_path)
    assert result["risk_score"] == 100
    assert len(result["reasons"]) == 3