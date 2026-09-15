HIGH_VALUE_THRESHOLD_BTC = 1.0
HIGH_VALUE_POINTS = 40
HIGH_VALUE_REASON = "High-value transaction: +40"

RAPID_MOVEMENT_WINDOW_SECONDS = 600
RAPID_MOVEMENT_POINTS = 30
RAPID_MOVEMENT_REASON = "Rapid onward movement: +30"

PEEL_CHAIN_MIN_SPLITS = 2
PEEL_CHAIN_MAX_AMOUNT_BTC = 1.0
PEEL_CHAIN_POINTS = 30
PEEL_CHAIN_REASON = "Peel-chain pattern: +30"

MAX_RISK_SCORE = 100


def _detect_rapid_movement(hop_record: dict, traced_path: list) -> bool:
    wallet = hop_record.get("to_wallet") or hop_record.get("wallet")
    arrival_time = hop_record.get("time", 0)
    for tx in traced_path:
        if tx.get("from_wallet") == wallet or tx.get("from") == wallet:
            gap = tx.get("time", 0) - arrival_time
            if 0 < gap <= RAPID_MOVEMENT_WINDOW_SECONDS:
                return True
    return False


def _detect_peel_chain(hop_record: dict, traced_path: list) -> bool:
    wallet = hop_record.get("wallet")
    sends = [
        tx
        for tx in traced_path
        if tx.get("from_wallet") == wallet or tx.get("from") == wallet
    ]
    small_outputs = [
        tx for tx in sends if tx.get("amount", 0) <= PEEL_CHAIN_MAX_AMOUNT_BTC
    ]
    return len(small_outputs) >= PEEL_CHAIN_MIN_SPLITS


def _detect_peel_chain_standalone(hop_record: dict) -> bool:
    small_outputs = 0
    for key in ("outputs", "outgoing", "splits"):
        outputs = hop_record.get(key)
        if not isinstance(outputs, list):
            continue
        for out in outputs:
            amount = out.get("amount", 0) if isinstance(out, dict) else out
            if amount <= PEEL_CHAIN_MAX_AMOUNT_BTC:
                small_outputs += 1
    return small_outputs >= PEEL_CHAIN_MIN_SPLITS


def calculate_risk(hop_record: dict, traced_path: list | None = None) -> dict:
    traced_path = traced_path or []
    score = 0
    reasons = []

    amount = hop_record.get("amount", 0) or 0
    if amount > HIGH_VALUE_THRESHOLD_BTC:
        score += HIGH_VALUE_POINTS
        reasons.append(HIGH_VALUE_REASON)

    if traced_path:
        if _detect_rapid_movement(hop_record, traced_path):
            score += RAPID_MOVEMENT_POINTS
            reasons.append(RAPID_MOVEMENT_REASON)
        if _detect_peel_chain(hop_record, traced_path):
            score += PEEL_CHAIN_POINTS
            reasons.append(PEEL_CHAIN_REASON)
    else:
        if _detect_peel_chain_standalone(hop_record):
            score += PEEL_CHAIN_POINTS
            reasons.append(PEEL_CHAIN_REASON)

    return {
        "risk_score": min(score, MAX_RISK_SCORE),
        "reasons": reasons,
    }