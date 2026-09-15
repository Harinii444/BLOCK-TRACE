import networkx as nx


def build_graph(transactions):
    """
    Build a directed transaction graph.

    Each wallet is represented as a node.
    Each transaction is represented as a directed edge.
    """

    graph = nx.DiGraph()

    for tx in transactions:
        from_wallet = tx["from"]
        to_wallet = tx["to"]

        # Add wallets as nodes
        graph.add_node(from_wallet)
        graph.add_node(to_wallet)

        # Handle duplicate transactions
        if graph.has_edge(from_wallet, to_wallet):
            graph[from_wallet][to_wallet]["transactions"].append(tx)

            # Keep latest transaction information
            graph[from_wallet][to_wallet]["amount"] = tx["amount"]
            graph[from_wallet][to_wallet]["time"] = tx["time"]
            graph[from_wallet][to_wallet]["txid"] = tx["txid"]

        else:
            graph.add_edge(
                from_wallet,
                to_wallet,
                amount=tx["amount"],
                time=tx["time"],
                txid=tx["txid"],
                transactions=[tx],
            )

    return graph