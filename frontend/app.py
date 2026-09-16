import streamlit as st
import pandas as pd

from blockchain.tracer import trace_wallet
from database.vasp_data import identify_vasp
from detection.risk_engine import calculate_confidence


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="BLOCK TRACE",
    page_icon="🔗",
    layout="wide"
)


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("🔗 BLOCK TRACE")
st.subheader(
    "Blockchain Intelligence & VASP Proximity Analysis"
)

st.write(
    "Trace cryptocurrency wallet transactions, "
    "identify possible VASP destinations, and calculate "
    "a rule-based confidence score."
)

st.divider()


# --------------------------------------------------
# WALLET INPUT
# --------------------------------------------------

wallet = st.text_input(
    "Enter Unknown Crypto Wallet Address",
    placeholder="Example: 0xSuspect"
)


# --------------------------------------------------
# ANALYZE WALLET
# --------------------------------------------------

if st.button("🔍 Analyze Wallet", type="primary"):

    if wallet.strip() == "":
        st.warning("Please enter a wallet address.")

    else:

        wallet = wallet.strip()

        # ------------------------------------------
        # TRACE WALLET
        # ------------------------------------------

        trace = trace_wallet(wallet)

        if not trace:

            st.error(
                f"No transactions found for wallet: {wallet}"
            )

        else:

            # --------------------------------------
            # VASP IDENTIFICATION
            # --------------------------------------

            final_wallet = trace[-1]["to"]

            vasp = identify_vasp(final_wallet)

            # --------------------------------------
            # CONFIDENCE CALCULATION
            # --------------------------------------

            confidence = calculate_confidence(
                trace,
                vasp
            )

            # --------------------------------------
            # WALLET OVERVIEW
            # --------------------------------------

            st.success("Wallet analysis completed.")

            st.divider()

            st.subheader("📊 Wallet Overview")

            total_transactions = len(trace)

            incoming = sum(
                1
                for tx in trace
                if tx["to"] == wallet
            )

            outgoing = sum(
                1
                for tx in trace
                if tx["from"] == wallet
            )

            total_volume = sum(
                float(tx["amount"])
                for tx in trace
            )

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Transactions",
                total_transactions
            )

            col2.metric(
                "Incoming",
                incoming
            )

            col3.metric(
                "Outgoing",
                outgoing
            )

            col4.metric(
                "Transaction Volume",
                f"{total_volume:.2f} ETH"
            )


            # --------------------------------------
            # TRANSACTION HISTORY
            # --------------------------------------

            st.divider()

            st.subheader("💸 Transaction Trace")

            transaction_data = []

            for tx in trace:

                transaction_data.append({
                    "From": tx["from"],
                    "To": tx["to"],
                    "Amount": f'{tx["amount"]} ETH',
                    "Transaction Hash": tx["tx_hash"]
                })

            df = pd.DataFrame(transaction_data)

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )


            # --------------------------------------
            # TRANSACTION PATH
            # --------------------------------------

            st.divider()

            st.subheader("🔗 Transaction Path")

            path = [wallet]

            for tx in trace:
                path.append(tx["to"])

            st.code(
                "  ↓\n".join(path),
                language="text"
            )


            # --------------------------------------
            # VASP PROXIMITY ANALYSIS
            # --------------------------------------

            st.divider()

            st.subheader("🏢 VASP Proximity Analysis")

            if vasp:

                st.success(
                    f"VASP Identified: {vasp['name']}"
                )

                vasp_col1, vasp_col2, vasp_col3 = st.columns(3)

                with vasp_col1:
                    st.metric(
                        "VASP",
                        vasp["name"]
                    )

                with vasp_col2:
                    st.metric(
                        "VASP Type",
                        vasp["type"]
                    )

                with vasp_col3:
                    st.metric(
                        "Country",
                        vasp["country"]
                    )

            else:

                st.warning(
                    "No matching VASP was found for the "
                    "final destination wallet."
                )


            # --------------------------------------
            # CONFIDENCE SCORE
            # --------------------------------------

            st.divider()

            st.subheader("🎯 Analysis Result")

            st.metric(
                "Confidence Score",
                f"{confidence}%"
            )

            st.progress(
                min(confidence, 100) / 100
            )


            if vasp:

                st.info(
                    f"The traced transaction path ends at "
                    f"{final_wallet}, which is associated with "
                    f"{vasp['name']} in the prototype VASP database."
                )

            else:

                st.info(
                    f"The traced transaction path ends at "
                    f"{final_wallet}, but no VASP association "
                    f"was found in the prototype database."
                )


            # --------------------------------------
            # PROTOTYPE DISCLAIMER
            # --------------------------------------

            st.divider()

            st.warning(
                "⚠️ Prototype Notice: This analysis uses "
                "sample/mock blockchain transaction data and "
                "a rule-based confidence calculation. "
                "It does not establish the real-world identity "
                "or ownership of a cryptocurrency wallet."
            )