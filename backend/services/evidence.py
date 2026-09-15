import hashlib
import json


def serialize_leaf(leaf: dict) -> str:
    return json.dumps(leaf, sort_keys=True, separators=(",", ":"))


def hash_leaf(leaf: dict) -> str:
    return hashlib.sha256(serialize_leaf(leaf).encode()).hexdigest()


def build_evidence(traced_path: list) -> list:
    evidence = []
    for hop in traced_path:
        leaf_data = {
            "from": hop.get("from_wallet"),
            "to": hop.get("to_wallet"),
            "txid": hop.get("txid"),
            "amount": hop.get("amount"),
            "time": hop.get("time"),
            "risk_score": hop.get("risk_score", 0),
            "vasp_match": hop.get("vasp_match"),
        }
        evidence.append(
            {"leaf_data": leaf_data, "leaf_hash": hash_leaf(leaf_data)}
        )
    return evidence


def build_merkle_root(leaf_hashes: list) -> str:
    if not leaf_hashes:
        raise ValueError("No leaf hashes provided")
    level = list(leaf_hashes)
    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1])
        next_level = []
        for i in range(0, len(level), 2):
            combined = level[i] + level[i + 1]
            next_level.append(
                hashlib.sha256(combined.encode()).hexdigest()
            )
        level = next_level
    return level[0]