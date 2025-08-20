import streamlit as st
import pandas as pd
from datetime import date
from src import ocr, classifier
from src.ledger import LedgerState, post_double_entry, trial_balance, reset
from src.chart_of_accounts import CHART, CODE_TO_ACCOUNT
from src.models import JournalEntry
from src.reports import export_trial_balance, export_journals
from src.db import StorageAdapter

st.set_page_config(page_title="AI Bookkeeping MVP", layout="wide")

if "ledger" not in st.session_state:
    st.session_state.ledger = LedgerState(journals=[])
if "transactions" not in st.session_state:
    st.session_state.transactions = pd.DataFrame(columns=["date","description","amount","reference"])
if "suggestions" not in st.session_state:
    st.session_state.suggestions = pd.DataFrame(columns=["date","description","amount","suggested_account","vat_code","confidence","reason","link_ref"])

storage = StorageAdapter()

st.title("📚 AI SaaS Bookkeeping (MVP)")
st.caption("Upload → AI classify → Human approve → Post to GL → Trial Balance")

tab_upload, tab_review, tab_ledger, tab_reports = st.tabs(["1) Upload & AI","2) Review & Post","3) Ledger & TB","4) Export"])

with tab_upload:
    st.header("Upload bank statements or invoices")
    src_type = st.selectbox("Source type", ["Bank CSV","Bank Excel","Bank PDF (digital)","Invoice CSV"])

    f = st.file_uploader("Choose a file", type=["csv","xlsx","xls","pdf"])
    if f is not None:
        try:
            if src_type == "Bank CSV" and f.name.endswith(".csv"):
                df = ocr.load_bank_csv(f.read())
                df["source"] = "bank_csv"
            elif src_type == "Bank Excel" and (f.name.endswith(".xlsx") or f.name.endswith(".xls")):
                df = ocr.load_bank_excel(f.read())
                df["source"] = "bank_excel"
            elif src_type == "Bank PDF (digital)" and f.name.endswith(".pdf"):
                df = ocr.load_bank_pdf(f.read())
                df["source"] = "bank_pdf"
            elif src_type == "Invoice CSV" and f.name.endswith(".csv"):
                df = pd.read_csv(f)
                # expect: date, description, amount, reference, vat_code
                for col in ["date","description","amount"]:
                    if col not in df.columns:
                        st.error(f"Invoice CSV must include column: {col}")
                        st.stop()
                df["date"] = pd.to_datetime(df["date"]).dt.date
                df["reference"] = df.get("reference","")
                df["source"] = "invoice_csv"
            else:
                st.error("File type does not match selected source.")
                st.stop()

            st.session_state.transactions = pd.concat([st.session_state.transactions, df], ignore_index=True)
            st.success(f"Loaded {len(df)} rows from {f.name}")
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Error reading file: {e}")

    if not st.session_state.transactions.empty:
        st.subheader("Run AI classification on uploaded rows")
        to_classify = st.session_state.transactions.copy()
        if st.button("Run AI on all un-suggested rows"):
            suggestions = []
            for i, row in to_classify.iterrows():
                acc_code, vat_code, conf, reason = classifier.classify(str(row["description"]), float(row["amount"]))
                suggestions.append({
                    "date": row["date"],
                    "description": row["description"],
                    "amount": row["amount"],
                    "suggested_account": acc_code,
                    "vat_code": vat_code,
                    "confidence": conf,
                    "reason": reason,
                    "link_ref": row.get("reference",""),
                })
            sugg_df = pd.DataFrame(suggestions)
            st.session_state.suggestions = pd.concat([st.session_state.suggestions, sugg_df], ignore_index=True)
            st.success(f"AI created {len(suggestions)} suggestions.")
        st.dataframe(st.session_state.suggestions, use_container_width=True)

with tab_review:
    st.header("Human-in-the-loop review & posting")
    if st.session_state.suggestions.empty:
        st.info("No AI suggestions yet. Go to the Upload tab and run AI.")
    else:
        editable = st.session_state.suggestions.copy()
        # Map account code → label
        code_to_label = {a.code: f"{a.code} - {a.name}" for a in CHART}
        editable["account_label"] = editable["suggested_account"].map(code_to_label)
        editable = editable[["date","description","amount","account_label","vat_code","confidence","reason","link_ref"]]
        edited = st.data_editor(
            editable,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "account_label": st.column_config.SelectboxColumn(
                    "Account (edit as needed)",
                    options=list(code_to_label.values()),
                    required=True,
                ),
                "vat_code": st.column_config.SelectboxColumn(
                    "VAT Code",
                    options=["STD","ZERO","EXEMPT","NONE"],
                    required=True,
                ),
                "confidence": st.column_config.NumberColumn(format="%.2f", min_value=0.0, max_value=1.0, step=0.01)
            }
        )

        st.markdown("When you click **Post Selected**, each row is posted as a double-entry with Bank (1000) as counterparty for cash-based rows. For invoice rows, you'll map to Debtors/Creditors control as needed in future iterations.")

        post_idx = st.multiselect("Select rows to post", options=list(edited.index))
        direction_hint = st.selectbox("Counterparty (for cash rows)", ["Bank (1000)", "Debtors Control (1010)", "Creditors Control (2000)"])
        counter_map = {"Bank (1000)":1000, "Debtors Control (1010)":1010, "Creditors Control (2000)":2000}
        counter_acc = counter_map[direction_hint]

        if st.button("Post Selected"):
            count = 0
            for idx in post_idx:
                row = edited.loc[idx]
                # parse account code back
                acc_code = int(str(row["account_label"]).split(" - ")[0])
                amt = float(row["amount"])
                memo = str(row["description"])
                vat_code = str(row["vat_code"]).upper()
                conf = float(row["confidence"] or 1.0)
                reason = str(row.get("reason","") or "")
                # Posting logic: if amount < 0 it's a payment (credit bank), else receipt (debit bank)
                if counter_acc == 1000:
                    if amt < 0:
                        # Expense: Debit expense, Credit bank
                        post_double_entry(st.session_state.ledger, row["date"], acc_code, 1000, abs(amt), memo=memo, link_ref=row.get("link_ref",""), created_by="Human", vat_code=vat_code, confidence=conf, reason=reason)
                    else:
                        # Income: Debit bank, Credit income
                        post_double_entry(st.session_state.ledger, row["date"], 1000, acc_code, abs(amt), memo=memo, link_ref=row.get("link_ref",""), created_by="Human", vat_code=vat_code, confidence=conf, reason=reason)
                else:
                    # Debtors/Creditors as counterparty (simplified example)
                    if amt < 0:
                        post_double_entry(st.session_state.ledger, row["date"], acc_code, counter_acc, abs(amt), memo=memo, link_ref=row.get("link_ref",""), created_by="Human", vat_code=vat_code, confidence=conf, reason=reason)
                    else:
                        post_double_entry(st.session_state.ledger, row["date"], counter_acc, acc_code, abs(amt), memo=memo, link_ref=row.get("link_ref",""), created_by="Human", vat_code=vat_code, confidence=conf, reason=reason)
                count += 1
            st.success(f"Posted {count} journal lines (double-entry).")

        st.divider()
        st.subheader("Current Journal Entries")
        jdf = st.session_state.ledger.to_dataframe()
        st.dataframe(jdf, use_container_width=True)

with tab_ledger:
    st.header("Trial Balance")
    tb = trial_balance(st.session_state.ledger)
    st.dataframe(tb, use_container_width=True)
    st.metric("TB Debit", f"{tb['TB_Debit'].sum():,.2f}")
    st.metric("TB Credit", f"{tb['TB_Credit'].sum():,.2f}")

    if st.button("Reset Ledger (clear all journals)"):
        reset(st.session_state.ledger)
        st.success("Ledger cleared.")

with tab_reports:
    st.header("Exports")
    jdf = st.session_state.ledger.to_dataframe()
    tb = trial_balance(st.session_state.ledger)
    if jdf.empty or tb.empty:
        st.info("Post some journals first.")
    else:
        tb_csv = "trial_balance.csv"
        tb_xlsx = "trial_balance.xlsx"
        j_csv = "journals.csv"
        j_xlsx = "journals.xlsx"
        export_trial_balance(tb, tb_csv, tb_xlsx)
        export_journals(jdf, j_csv, j_xlsx)

        with open(tb_csv, "rb") as f:
            st.download_button("Download Trial Balance (CSV)", f, file_name="trial_balance.csv")
        with open(tb_xlsx, "rb") as f:
            st.download_button("Download Trial Balance (Excel)", f, file_name="trial_balance.xlsx")
        with open(j_csv, "rb") as f:
            st.download_button("Download Journals (CSV)", f, file_name="journals.csv")
        with open(j_xlsx, "rb") as f:
            st.download_button("Download Journals (Excel)", f, file_name="journals.xlsx")
