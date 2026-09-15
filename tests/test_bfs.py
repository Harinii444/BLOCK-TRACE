import networkx as nx

from backend.services.graph_builder import build_graph
from backend.services.bfs_engine import (
    bounded_bfs,
    MAX_HOP_DEPTH,
    MAX_WALLETS_VISITED,
    MAX_EDGES_FOLLOWED,
)


def test_graph_builder_creates_correct_graph():
    transactions = [
        {
            "from": "A",
            "to": "B",
            "amount": 5.0,
            "time": 100,
            "txid": "tx1",
        },
        {
            "from": "B",
            "to": "C",
            "amount": 3.0,
            "time": 200,
            "txid": "tx2",
        },
        {
            "from": "C",
            "to": "D",
            "amount": 1.0,
            "time": 300,
            "txid": "tx3",
        },
    ]

    graph = build_graph(transactions)

    assert isinstance(graph, nx.DiGraph)
    assert graph.number_of_nodes() == 4
    assert graph.number_of_edges() == 3

    assert graph["A"]["B"]["amount"] == 5.0
    assert graph["A"]["B"]["time"] == 100
    assert graph["A"]["B"]["txid"] == "tx1"


def test_graph_builder_handles_duplicate_transactions():
    transactions = [
        {
            "from": "A",
            "to": "B",
            "amount": 5.0,
            "time": 100,
            "txid": "tx1",
        },
        {
            "from": "A",
            "to": "B",
            "amount": 2.0,
            "time": 200,
            "txid": "tx2",
        },
    ]

    graph = build_graph(transactions)

    assert graph.number_of_edges() == 1
    assert len(graph["A"]["B"]["transactions"]) == 2


def test_bounded_bfs_returns_expected_path():
    transactions = [
        {
            "from": "A",
            "to": "B",
            "amount": 5.2,
            "time": 100,
            "txid": "tx1",
        },
        {
            "from": "B",
            "to": "C",
            "amount": 4.8,
            "time": 200,
            "txid": "tx2",
        },
        {
            "from": "C",
            "to": "D",
            "amount": 4.5,
            "time": 300,
            "txid": "tx3",
        },
        {
            "from": "D",
            "to": "E",
            "amount": 4.0,
            "time": 400,
            "txid": "tx4",
        },
    ]

    graph = build_graph(transactions)

    result = bounded_bfs(graph, "A", set())

    assert [item["wallet"] for item in result] == [
        "B",
        "C",
        "D",
        "E",
    ]

    assert [item["hop_number"] for item in result] == [
        1,
        2,
        3,
        4,
    ]


def test_bfs_stops_at_max_hop_depth():
    transactions = []

    wallets = ["A", "B", "C", "D", "E", "F"]

    for i in range(len(wallets) - 1):
        transactions.append(
            {
                "from": wallets[i],
                "to": wallets[i + 1],
                "amount": 1.0,
                "time": i,
                "txid": f"tx{i}",
            }
        )

    graph = build_graph(transactions)

    result = bounded_bfs(graph, "A", set())

    assert len(result) == MAX_HOP_DEPTH
    assert all(
        item["hop_number"] <= MAX_HOP_DEPTH
        for item in result
    )


def test_bfs_stops_at_wallet_limit():
    graph = nx.DiGraph()

    for i in range(1, MAX_WALLETS_VISITED + 100):
        graph.add_edge(
            "A",
            f"W{i}",
            amount=1.0,
            time=i,
            txid=f"tx{i}",
        )

    result = bounded_bfs(graph, "A", set())

    wallets = {"A"}
    wallets.update(item["wallet"] for item in result)

    assert len(wallets) <= MAX_WALLETS_VISITED


def test_bfs_stops_at_edge_limit():
    graph = nx.DiGraph()

    for i in range(MAX_EDGES_FOLLOWED + 100):
        graph.add_edge(
            "A",
            f"W{i}",
            amount=1.0,
            time=i,
            txid=f"tx{i}",
        )

    result = bounded_bfs(graph, "A", set())

    assert len(result) <= MAX_EDGES_FOLLOWED


def test_bfs_does_not_expand_beyond_vasp():
    transactions = [
        {
            "from": "A",
            "to": "B",
            "amount": 5.0,
            "time": 100,
            "txid": "tx1",
        },
        {
            "from": "B",
            "to": "VASP",
            "amount": 4.0,
            "time": 200,
            "txid": "tx2",
        },
        {
            "from": "VASP",
            "to": "C",
            "amount": 3.0,
            "time": 300,
            "txid": "tx3",
        },
        {
            "from": "C",
            "to": "D",
            "amount": 2.0,
            "time": 400,
            "txid": "tx4",
        },
    ]

    graph = build_graph(transactions)

    result = bounded_bfs(
        graph,
        "A",
        {"VASP"},
    )

    wallets = [item["wallet"] for item in result]

    assert "VASP" in wallets
    assert "C" not in wallets
    assert "D" not in wallets