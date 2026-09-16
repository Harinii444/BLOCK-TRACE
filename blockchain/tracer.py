import json


def load_transactions():
    with open("mock_data/transactions.json", "r") as file:
        return json.load(file)


def trace_wallet(start_wallet):
    transactions = load_transactions()

    current_wallet = start_wallet
    path = []

    while True:
        found = False

        for tx in transactions:
            if tx["from"] == current_wallet:
                path.append(tx)
                current_wallet = tx["to"]
                found = True
                break

        if not found:
            break

    return path


if __name__ == "__main__":
    result = trace_wallet("0xSuspect")

    print("\nTransaction Trace:")
    print("------------------")

    for tx in result:
        print(
            f'{tx["from"]} → {tx["to"]} | '
            f'Amount: {tx["amount"]} ETH | '
            f'TX: {tx["tx_hash"]}'
        )
