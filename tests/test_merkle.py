import hashlib
import json
import os

import pytest

from backend.services.evidence import build_evidence, build_merkle_root
from backend.services.report_builder import generate_json, generate_pdf


def make_hop(**overrides):
    hop_number = overrides.get("hop_number", 1)
    hop = {
        "wallet": "bc1qwallet1",
        "hop_number": hop_number,
        "from_wallet": "bc1qsender1",
        "to_wallet": "bc1qreceiver1",
        "txid": "{:064d}".format(hop_number),
        "amount": 0.5,
        "time": 1709000000,
        "risk_score": 40,
        "vasp_match": "Binance",
    }
    hop.update(overrides)
    return hop


@pytest.fixture
def trace_result():
    path = [
        make_hop(hop_number=1),
        make_hop(hop_number=2),
        make_hop(hop_number=3),
    ]
    evidence = build_evidence(path)
    return {
        "wallet_address": "bc1qwallet1",
        "traced_at": 1709000000,
        "path": path,
        "risk_score": 70,
        "vasp_match": "Binance",
        "risk_breakdown": [
            {
                "wallet": "bc1qwallet1",
                "risk_score": 40,
                "reasons": ["High-value transaction: +40"],
            }
        ],
        "merkle_root": build_merkle_root([e["leaf_hash"] for e in evidence]),
    }


def test_four_leaves_produce_deterministic_root():
    traced_path = [
        make_hop(hop_number=i) for i in range(1, 5)
    ]
    hashes = [e["leaf_hash"] for e in build_evidence(traced_path)]
    root1 = build_merkle_root(hashes)
    root2 = build_merkle_root(hashes)
    assert root1 == root2
    assert len(root1) == 64
    pair1 = hashlib.sha256((hashes[0] + hashes[1]).encode()).hexdigest()
    pair2 = hashlib.sha256((hashes[2] + hashes[3]).encode()).hexdigest()
    assert root1 == hashlib.sha256((pair1 + pair2).encode()).hexdigest()


def test_changing_one_leaf_changes_root():
    path_a = [
        make_hop(hop_number=1, amount=0.5),
        make_hop(hop_number=2, amount=0.5),
    ]
    path_b = [
        make_hop(hop_number=1, amount=0.5),
        make_hop(hop_number=2, amount=0.51),
    ]
    root_a = build_merkle_root(
        [e["leaf_hash"] for e in build_evidence(path_a)]
    )
    root_b = build_merkle_root(
        [e["leaf_hash"] for e in build_evidence(path_b)]
    )
    assert root_a != root_b


def test_single_leaf_produces_correct_hash():
    leaf_hash = build_evidence([make_hop(hop_number=1)])[0]["leaf_hash"]
    assert build_merkle_root([leaf_hash]) == leaf_hash


def test_odd_number_of_leaves_handled():
    traced_path = [make_hop(hop_number=i) for i in range(1, 4)]
    hashes = [e["leaf_hash"] for e in build_evidence(traced_path)]
    root = build_merkle_root(hashes)
    assert len(root) == 64
    pair1 = hashlib.sha256((hashes[0] + hashes[1]).encode()).hexdigest()
    pair2 = hashlib.sha256((hashes[2] + hashes[2]).encode()).hexdigest()
    assert root == hashlib.sha256((pair1 + pair2).encode()).hexdigest()


def test_pdf_file_created_and_non_empty(tmp_path):
    path = generate_pdf(trace_result(), out_dir=tmp_path)
    assert os.path.isfile(path)
    assert os.path.getsize(path) > 0


def test_json_output_has_required_keys(tmp_path):
    path = generate_json(trace_result(), out_dir=tmp_path)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for key in (
        "wallet_address",
        "traced_at",
        "path",
        "risk_score",
        "vasp_match",
        "merkle_root",
        "risk_breakdown",
    ):
        assert key in data
    assert data["merkle_root"] == trace_result()["merkle_root"]