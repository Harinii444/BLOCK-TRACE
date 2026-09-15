from collections import deque


# BFS safety limits
MAX_HOP_DEPTH = 4
MAX_WALLETS_VISITED = 500
MAX_EDGES_FOLLOWED = 1500


def bounded_bfs(graph, start_wallet, vasp_set):
    """
    Perform bounded Breadth-First Search from a starting wallet.

    The search stops when:
    - maximum hop depth is reached
    - maximum wallet count is reached
    - maximum edge count is reached
    - a VASP wallet is found
    """

    # If starting wallet doesn't exist
    if start_wallet not in graph:
        return []

    vasp_set = set(vasp_set)

    # Queue stores:
    # (wallet, current hop number)
    queue = deque([(start_wallet, 0)])

    # Keep track of wallets already visited
    visited = {start_wallet}

    # Store the final BFS path
    result = []

    # Count edges followed
    edges_followed = 0

    while queue:

        current_wallet, current_hop = queue.popleft()

        # Do not go beyond maximum hop depth
        if current_hop >= MAX_HOP_DEPTH:
            continue

        # Visit all outgoing transactions
        for neighbor in graph.successors(current_wallet):

            # Stop when edge limit is reached
            if edges_followed >= MAX_EDGES_FOLLOWED:
                return sorted(
                    result,
                    key=lambda item: item["hop_number"]
                )

            # Ignore already visited wallets
            if neighbor in visited:
                continue

            edges_followed += 1

            # Get transaction information
            edge_data = graph[current_wallet][neighbor]

            hop_number = current_hop + 1

            # Create hop information
            hop = {
                "wallet": neighbor,
                "hop_number": hop_number,
                "from_wallet": current_wallet,
                "txid": edge_data["txid"],
                "amount": edge_data["amount"],
                "time": edge_data["time"],
            }

            result.append(hop)

            # Mark wallet as visited
            visited.add(neighbor)

            # If this wallet is a VASP:
            # record it but DON'T continue searching from it.
            if neighbor in vasp_set:
                continue

            # Stop when wallet limit is reached
            if len(visited) >= MAX_WALLETS_VISITED:
                return sorted(
                    result,
                    key=lambda item: item["hop_number"]
                )

            # Add wallet to BFS queue
            queue.append((neighbor, hop_number))

    # Return results sorted by hop number
    return sorted(
        result,
        key=lambda item: item["hop_number"]
    )