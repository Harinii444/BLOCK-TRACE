import hashlib
import json
import time

import networkx as nx
import streamlit as st


# ============================================================
# BLOCK TRACE - Divakar's Streamlit Dashboard
# Phase 1: Mock Data
# ============================================================

st.set_page_config(
    page_title="BLOCK TRACE — Blockchain Forensics",
    page_icon="🔎",
    layout="wide",
)


# ------------------------------------------------------------
# Mock blockchain trace data
# ------------------------------------------------------------

DEMO_WALLET = "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0w4"

MOCK_HOPS = [
    {
        "wallet": DEMO_WALLET,
        "hop_number": 0,
        "risk_score": 88,
        "vasp_match": None,
    },
    {
        "wallet": "bc1qdemo2wallet8trace7example9",
        "hop_number": 1,
        "risk_score": 76,
        "vasp_match": None,
    },
    {
        "wallet": "bc1qdemo3wallet8trace7example2",
        "hop_number": 2,
        "risk_score": 61,
        "vasp_match": "Example Exchange",
    },
    {
        "wallet": "bc1qdemo4wallet8trace7example5",
        "hop_number": 3,
        "risk_score": 42,
        "vasp_match": None,
    },
]


# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------

def validate_wallet(address: str) -> bool:
    """Basic Bitcoin wallet validation for the Phase 1 demo."""
    address = address.strip()

    if not address:
        return False

    if len(address) < 25 or len(address) > 62:
        return False

    return address.startswith(("1", "3", "bc1"))


def risk_label(score: int) -> str:
    if score >= 70:
        return "HIGH"
    elif score >= 40:
        return "MEDIUM"
    return "LOW"


def risk_emoji(score: int) -> str:
    if score >= 70:
        return "🔴"
    elif score >= 40:
        return "🟠"
    return "🟢"


def calculate_merkle_root(records: list) -> str:
    """Create a deterministic SHA-256 Merkle root for demo evidence."""
    hashes = [
        hashlib.sha256(
            json.dumps(record, sort_keys=True).encode("utf-8")
        ).hexdigest()
        for record in records
    ]

    if not hashes:
        return ""

    while len(hashes) > 1:
        if len(hashes) % 2 == 1:
            hashes.append(hashes[-1])

        hashes = [
            hashlib.sha256(
                (hashes[i] + hashes[i + 1]).encode("utf-8")
            ).hexdigest()
            for i in range(0, len(hashes), 2)
        ]

    return hashes[0]


def build_graph(hops: list) -> nx.DiGraph:
    graph = nx.DiGraph()

    for hop in hops:
        wallet = hop["wallet"]

        graph.add_node(
            wallet,
            risk_score=hop["risk_score"],
            vasp_match=hop["vasp_match"],
        )

    for index in range(len(hops) - 1):
        graph.add_edge(
            hops[index]["wallet"],
            hops[index + 1]["wallet"],
        )

    return graph


def graph_node_color(score: int) -> str:
    if score >= 70:
        return "red"
    elif score >= 40:
        return "orange"
    return "green"


# ------------------------------------------------------------
# Session state
# ------------------------------------------------------------

if "screen" not in st.session_state:
    st.session_state.screen = 1

if "wallet" not in st.session_state:
    st.session_state.wallet = ""

if "trace_data" not in st.session_state:
    st.session_state.trace_data = None


# ------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------

st.sidebar.title("🔎 BLOCK TRACE")

st.sidebar.markdown("### Investigation")

screen = st.sidebar.radio(
    "Navigate",
    [
        "1. Wallet Investigation",
        "2. Trace Results",
        "3. Evidence & Report",
    ],
)

if screen.startswith("1"):
    st.session_state.screen = 1
elif screen.startswith("2"):
    st.session_state.screen = 2
else:
    st.session_state.screen = 3

st.sidebar.markdown("---")

st.sidebar.info(
    "Phase 1 dashboard uses mock blockchain data. "
    "Real FastAPI integration will be added during Phase 2."
)


# ============================================================
# SCREEN 1 — WALLET INVESTIGATION
# ============================================================

if st.session_state.screen == 1:

    st.title("BLOCK TRACE — Blockchain Forensics")

    st.subheader("Investigate a Bitcoin Wallet")

    st.write(
        "Enter a Bitcoin wallet address to begin a blockchain "
        "forensic trace."
    )

    wallet_input = st.text_input(
        "Bitcoin Wallet Address",
        value=st.session_state.wallet,
        placeholder="Example: bc1q...",
    )

    col1, col2 = st.columns(2)

    with col1:
        trace_button = st.button(
            "🚀 Trace Wallet",
            use_container_width=True,
        )

    with col2:
        demo_button = st.button(
            "🎯 Load Demo Wallet",
            use_container_width=True,
        )

    if demo_button:
        wallet_input = DEMO_WALLET
        st.session_state.wallet = DEMO_WALLET
        st.session_state.trace_data = MOCK_HOPS
        st.session_state.screen = 2
        st.rerun()

    if trace_button:

        if not validate_wallet(wallet_input):
            st.error(
                "❌ Invalid Bitcoin address. "
                "Address must begin with 1, 3, or bc1 and "
                "contain 25–62 characters."
            )
        else:
            st.session_state.wallet = wallet_input.strip()

            with st.spinner("Tracing blockchain transactions..."):
                time.sleep(1)

            st.session_state.trace_data = [
                {
                    **hop,
                    "wallet": (
                        st.session_state.wallet
                        if hop["hop_number"] == 0
                        else hop["wallet"]
                    ),
                }
                for hop in MOCK_HOPS
            ]

            st.success("✅ Trace completed successfully.")

            st.session_state.screen = 2
            st.rerun()

    with st.expander("ℹ️ How does BLOCK TRACE work?"):

        st.write(
            """
            BLOCK TRACE is a blockchain intelligence and forensic
            analysis prototype.

            The investigator provides a Bitcoin wallet address.
            The system traces connected wallets, calculates
            heuristic risk scores, checks possible VASP matches,
            and prepares evidence for reporting.

            Phase 1 uses mock data for the dashboard.
            Phase 2 will connect this interface to the FastAPI
            `/trace` endpoint.
            """
        )

    st.markdown("---")

    st.caption(
        "For authorized blockchain investigation and educational use."
    )


# ============================================================
# SCREEN 2 — TRACE RESULTS
# ============================================================

elif st.session_state.screen == 2:

    st.title("🔍 Trace Results")

    hops = st.session_state.trace_data or MOCK_HOPS

    # Metrics
    total_wallets = len(hops)
    total_hops = max(len(hops) - 1, 0)
    final_risk = hops[-1]["risk_score"]
    average_risk = round(
        sum(item["risk_score"] for item in hops) / len(hops)
    )

    high_risk = sum(
        1 for item in hops if item["risk_score"] >= 70
    )

    medium_risk = sum(
        1
        for item in hops
        if 40 <= item["risk_score"] < 70
    )

    low_risk = sum(
        1 for item in hops if item["risk_score"] < 40
    )

    progress = min(100, total_hops * 25)

    st.progress(
        progress,
        text=f"Trace progress: {progress}%",
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Hops Traced",
        total_hops,
    )

    col2.metric(
        "Wallets Found",
        total_wallets,
    )

    col3.metric(
        "Risk Score",
        f"{final_risk}/100",
    )

    col4.metric(
        "Average Score",
        f"{average_risk}/100",
    )

    st.markdown("---")

    # Risk summary
    st.subheader("Risk Distribution")

    r1, r2, r3 = st.columns(3)

    r1.metric("🔴 High Risk", high_risk)
    r2.metric("🟠 Medium Risk", medium_risk)
    r3.metric("🟢 Low Risk", low_risk)

    # Wallet table
    st.subheader("Wallet Trace")

    table_data = []

    for hop in hops:
        table_data.append(
            {
                "Hop": hop["hop_number"],
                "Wallet": hop["wallet"],
                "Risk Score": hop["risk_score"],
                "Risk Level": (
                    f"{risk_emoji(hop['risk_score'])} "
                    f"{risk_label(hop['risk_score'])}"
                ),
                "VASP Match": (
                    hop["vasp_match"]
                    if hop["vasp_match"]
                    else "No match"
                ),
            }
        )

    st.dataframe(
        table_data,
        use_container_width=True,
        hide_index=True,
    )

    # Graph
    st.subheader("Transaction Graph")

    graph = build_graph(hops)

    positions = nx.spring_layout(
        graph,
        seed=42,
    )

    import matplotlib.pyplot as plt

    figure = plt.figure(figsize=(12, 6))

    node_colors = [
        graph_node_color(
            graph.nodes[node].get("risk_score", 0)
        )
        for node in graph.nodes
    ]

    nx.draw(
        graph,
        positions,
        with_labels=False,
        node_color=node_colors,
        node_size=1800,
        arrows=True,
        arrowsize=20,
    )

    # Add shortened wallet labels
    labels = {
        node: f"{node[:8]}...\n"
        f"Risk {graph.nodes[node].get('risk_score', 0)}"
        for node in graph.nodes
    }

    nx.draw_networkx_labels(
        graph,
        positions,
        labels=labels,
        font_size=8,
    )

    st.pyplot(
        figure,
        use_container_width=True,
    )

    st.info(
        "🔴 High risk ≥ 70 | "
        "🟠 Medium risk 40–69 | "
        "🟢 Low risk < 40"
    )

    if st.button("➡️ View Evidence & Report"):
        st.session_state.screen = 3
        st.rerun()


# ============================================================
# SCREEN 3 — EVIDENCE & REPORT
# ============================================================

else:

    st.title("📋 Evidence & Report")

    hops = st.session_state.trace_data or MOCK_HOPS

    suspect_wallet = hops[0]["wallet"]
    final_risk = hops[-1]["risk_score"]

    vasp_matches = [
        hop["vasp_match"]
        for hop in hops
        if hop["vasp_match"]
    ]

    vasp_match = (
        vasp_matches[0]
        if vasp_matches
        else "No VASP match"
    )

    merkle_root = calculate_merkle_root(hops)

    # Summary card
    st.subheader("Investigation Summary")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Suspect Wallet",
        f"{suspect_wallet[:12]}...",
    )

    c2.metric(
        "Trace Time",
        "1.02 sec",
    )

    c3.metric(
        "Final Risk",
        f"{final_risk}/100",
    )

    c4.metric(
        "VASP Match",
        vasp_match,
    )

    st.markdown("---")

    # Hop details
    with st.expander("🔎 Full Hop Details", expanded=True):

        for hop in hops:

            st.write(
                f"**Hop {hop['hop_number']}** — "
                f"`{hop['wallet']}`"
            )

            st.write(
                f"Risk Score: **{hop['risk_score']}/100**  \n"
                f"Risk Level: **"
                f"{risk_emoji(hop['risk_score'])} "
                f"{risk_label(hop['risk_score'])}**  \n"
                f"VASP Match: **"
                f"{hop['vasp_match'] or 'None'}**"
            )

            st.divider()

    # Merkle root
    st.subheader("🔐 Evidence Integrity")

    st.write(
        "Merkle Root"
    )

    st.code(
        merkle_root,
        language="text",
    )

    st.caption(
        "The Merkle root provides a deterministic integrity "
        "identifier for the evidence records in this demo."
    )

    # Prepare JSON
    report_data = {
        "project": "BLOCK TRACE",
        "wallet": suspect_wallet,
        "hops": hops,
        "final_risk_score": final_risk,
        "vasp_match": vasp_match,
        "merkle_root": merkle_root,
        "analysis_type": "Heuristic analysis",
    }

    json_data = json.dumps(
        report_data,
        indent=4,
    )

    # Simple PDF-like text download for Phase 1
    pdf_text = f"""
BLOCK TRACE — Blockchain Forensics
==================================

Suspect Wallet:
{suspect_wallet}

Final Risk Score:
{final_risk}/100

VASP Match:
{vasp_match}

Merkle Root:
{merkle_root}

Hop Details:
"""

    for hop in hops:
        pdf_text += (
            f"\nHop {hop['hop_number']}: "
            f"{hop['wallet']}\n"
            f"Risk: {hop['risk_score']}/100\n"
            f"VASP: {hop['vasp_match'] or 'None'}\n"
        )

    st.subheader("📥 Download Evidence")

    d1, d2 = st.columns(2)

    with d1:
        st.download_button(
            "⬇️ Download JSON Report",
            data=json_data,
            file_name="block_trace_report.json",
            mime="application/json",
            use_container_width=True,
        )

    with d2:
        st.download_button(
            "⬇️ Download Evidence Report",
            data=pdf_text,
            file_name="block_trace_evidence.txt",
            mime="text/plain",
            use_container_width=True,
        )

    st.warning(
        "⚠️ Ethical Disclaimer: Heuristic analysis only. "
        "Not legal evidence."
    )

    st.caption(
        "BLOCK TRACE — Phase 1 Streamlit Dashboard"
    )