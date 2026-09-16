from blockchain.tracer import trace_wallet
from database.vasp_data import identify_vasp
from detection.risk_engine import calculate_confidence


def analyze_wallet(wallet):
    trace = trace_wallet(wallet)

    if not trace:
        print("No transactions found.")
        return

    final_wallet = trace[-1]["to"]
    vasp = identify_vasp(final_wallet)
    confidence = calculate_confidence(trace, vasp)

    print("\n========== BLOCK TRACE ==========")
    print(f"Starting Wallet: {wallet}")

    print("\nTransaction Path:")
    for tx in trace:
        print(f'{tx["from"]} → {tx["to"]} | {tx["amount"]} ETH')

    print("\nFinal Destination:", final_wallet)

    if vasp:
        print("VASP Identified:", vasp["name"])
        print("VASP Type:", vasp["type"])
        print("Country:", vasp["country"])
    else:
        print("VASP Identified: Not found")

    print(f"\nConfidence Score: {confidence}%")
    print("=================================")


if __name__ == "__main__":
    analyze_wallet("0xSuspect")
