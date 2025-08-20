import streamlit as st
import pandas as pd
from src import ocr, classifier
from src.ledger import LedgerState, post_double_entry, trial_balance, reset
from src.chart_of_accounts import CHART

st.set_page_config(page_title="AI Bookkeeping v1.4 (OCR)", layout="wide")

if "ledger" not in st.session_state:
    st.session_state.ledger = LedgerState(journals=[])
if "bank_df" not in st.session_state:
    st.session_state.bank_df = pd.DataFrame(columns=["date","description","amount","reference"]).astype({"date":"object","description":"object","amount":"float","reference":"object"})
if "inv_df" not in st.session_state:
    st.session_state.inv_df = pd.DataFrame(columns=["date","description","amount","reference","vat_code"]).astype({"date":"object","description":"object","amount":"float","reference":"object","vat_code":"object"})
if "sugg_df" not in st.session_state:
    st.session_state.sugg_df = pd.DataFrame(columns=["date","description","amount","suggested_account","vat_code","confidence","reason","link_ref"])

st.title("📚 AI SaaS Bookkeeping (v1.4 — OCR)")
st.caption("Upload (CSV/Excel/PDF digital or scanned) → AI classify → Human review → Post to GL → Trial Balance → Export")

st.sidebar.header("Settings")
enable_ocr = st.sidebar.toggle("🔎 Enable OCR fallback for scanned PDFs", value=False)
st.sidebar.caption("If a PDF has no readable text, we'll OCR it. Requires Tesseract on host.")

tab_upload, tab_review, tab_ledger, tab_export = st.tabs(["1) Upload","2) Review & Post","3) Ledger & TB","4) Export"])

with tab_upload:
    st.subheader("Bank statements")
    col1, col2 = st.columns(2)
    with col1:
        bank_type = st.selectbox("Bank file type", ["CSV","Excel","PDF"])
    with col2:
        bank_file = st.file_uploader("Upload bank file", type=["csv","xlsx","xls","pdf"], key="bank_up")
    if bank_file:
        try:
            if bank_type=="CSV" and bank_file.name.endswith(".csv"): df = ocr.load_bank_csv(bank_file.read())
            elif bank_type=="Excel" and (bank_file.name.endswith(".xlsx") or bank_file.name.endswith(".xls")): df = ocr.load_bank_excel(bank_file.read())
            elif bank_type=="PDF" and bank_file.name.endswith(".pdf"): df = ocr.load_bank_pdf(bank_file.read(), enable_ocr=enable_ocr)
            else: st.error("File type does not match selection."); st.stop()
            st.session_state.bank_df = pd.concat([st.session_state.bank_df, df], ignore_index=True)
            st.success(f"Loaded {len(df)} bank rows.")
        except Exception as e:
            st.error(f"Bank import error: {e}")
    st.dataframe(st.session_state.bank_df, use_container_width=True)

    st.divider()
    st.subheader("Invoices")
    col3, col4 = st.columns(2)
    with col3:
        inv_type = st.selectbox("Invoice file type", ["CSV","Excel","PDF"])
    with col4:
        inv_file = st.file_uploader("Upload invoice file", type=["csv","xlsx","xls","pdf"], key="inv_up")
    if inv_file:
        try:
            if inv_type=="CSV" and inv_file.name.endswith(".csv"): df2 = ocr.load_invoice_csv(inv_file.read())
            elif inv_type=="Excel" and (inv_file.name.endswith(".xlsx") or inv_file.name.endswith(".xls")): df2 = ocr.load_invoice_excel(inv_file.read())
            elif inv_type=="PDF" and inv_file.name.endswith(".pdf"): df2 = ocr.load_invoice_pdf(inv_file.read(), enable_ocr=enable_ocr)
            else: st.error("File type does not match selection."); st.stop()
            st.session_state.inv_df = pd.concat([st.session_state.inv_df, df2], ignore_index=True)
            st.success(f"Loaded {len(df2)} invoice rows.")
        except Exception as e:
            st.error(f"Invoice import error: {e}")
    st.dataframe(st.session_state.inv_df, use_container_width=True)

    st.divider()
    st.subheader("Run AI suggestions")
    if st.button("Suggest accounts for BANK rows"):
        suggestions = []
        for _, r in st.session_state.bank_df.iterrows():
            code, vat_code, conf, reason = classifier.classify(str(r["description"]), float(r["amount"]))
            suggestions.append({
                "date": r["date"],
                "description": r["description"],
                "amount": r["amount"],
                "suggested_account": code,
                "vat_code": vat_code,
                "confidence": conf,
                "reason": reason,
                "link_ref": r.get("reference",""),
            })
        st.session_state.sugg_df = pd.DataFrame(suggestions)
        st.success(f"AI suggested {len(suggestions)} bank rows.")
    if st.button("Suggest accounts for INVOICE rows"):
        suggestions = []
        for _, r in st.session_state.inv_df.iterrows():
            code, vat_code, conf, reason = classifier.classify(str(r["description"]), float(r["amount"]))
            suggestions.append({
                "date": r["date"],
                "description": r["description"],
                "amount": r["amount"],
                "suggested_account": code,
                "vat_code": r.get("vat_code", vat_code),
                "confidence": conf,
                "reason": reason + " (invoice) ",
                "link_ref": r.get("reference",""),
            })
        st.session_state.sugg_df = pd.concat([st.session_state.sugg_df, pd.DataFrame(suggestions)], ignore_index=True)
        st.success(f"AI suggested {len(suggestions)} invoice rows.")
    st.subheader("AI Suggestions (editable)")
    if not st.session_state.sugg_df.empty:
        st.dataframe(st.session_state.sugg_df, use_container_width=True)

with tab_review:
    st.subheader("Human review and posting to GL")
    if st.session_state.sugg_df.empty:
        st.info("Run AI suggestions first on the Upload tab.")
    else:
        code_to_label = {a.code: f"{a.code} - {a.name}" for a in CHART}
        editable = st.session_state.sugg_df.copy()
        editable["account_label"] = editable["suggested_account"].map(code_to_label)
        show = editable[["date","description","amount","account_label","vat_code","confidence","reason","link_ref"]]
        edited = st.data_editor(
            show, use_container_width=True, num_rows="dynamic",
            column_config={
                "account_label": st.column_config.SelectboxColumn("Account", options=list(code_to_label.values()), required=True),
                "vat_code": st.column_config.SelectboxColumn("VAT", options=["STD","ZERO","EXEMPT","NONE"], required=True),
                "confidence": st.column_config.NumberColumn(format="%.2f", min_value=0.0, max_value=1.0, step=0.01),
            }
        )
        st.markdown("Select rows and choose a counterparty for double-entry posting.")
        post_idx = st.multiselect("Rows to post", options=list(edited.index))
        counterparty = st.selectbox("Counterparty", ["Bank (1000)", "Debtors Control (1010)", "Creditors Control (2000)"])
        counter_map = {"Bank (1000)":1000, "Debtors Control (1010)":1010, "Creditors Control (2000)":2000}
        c_acc = counter_map[counterparty]
        if st.button("Post Selected"):
            posted = 0
            for idx in post_idx:
                row = edited.loc[idx]
                try:
                    acc_code = int(str(row["account_label"]).split(" - ")[0])
                except:
                    st.error(f"Invalid account on row {idx}"); continue
                amt = float(row["amount"]); memo = str(row["description"])
                vat_code = str(row["vat_code"]).upper()
                conf = float(row.get("confidence",1.0)); reason = str(row.get("reason","") or "")
                if c_acc == 1000:
                    if amt < 0:
                        post_double_entry(st.session_state.ledger, row["date"], acc_code, 1000, abs(amt), memo=memo, link_ref=row.get("link_ref",""), created_by="Human", vat_code=vat_code, confidence=conf, reason=reason)
                    else:
                        post_double_entry(st.session_state.ledger, row["date"], 1000, acc_code, abs(amt), memo=memo, link_ref=row.get("link_ref",""), created_by="Human", vat_code=vat_code, confidence=conf, reason=reason)
                else:
                    if amt < 0:
                        post_double_entry(st.session_state.ledger, row["date"], acc_code, c_acc, abs(amt), memo=memo, link_ref=row.get("link_ref",""), created_by="Human", vat_code=vat_code, confidence=conf, reason=reason)
                    else:
                        post_double_entry(st.session_state.ledger, row["date"], c_acc, acc_code, abs(amt), memo=memo, link_ref=row.get("link_ref",""), created_by="Human", vat_code=vat_code, confidence=conf, reason=reason)
                posted += 1
            st.success(f"Posted {posted} journal lines (double-entry).")
        st.subheader("Current Journal Entries")
        st.dataframe(st.session_state.ledger.to_dataframe(), use_container_width=True)

with tab_ledger:
    st.subheader("Trial Balance")
    tb = trial_balance(st.session_state.ledger)
    st.dataframe(tb, use_container_width=True)
    st.metric("TB Debit", f"{tb['TB_Debit'].sum():,.2f}")
    st.metric("TB Credit", f"{tb['TB_Credit'].sum():,.2f}")
    confirm_reset = st.checkbox("I understand this will clear all journals.", value=False)
    if st.button("Reset Ledger (clear all journals)", disabled=not confirm_reset):
        reset(st.session_state.ledger)
        st.success("Ledger cleared.")

with tab_export:
    st.subheader("Export (CSV/Excel)")
    from src.reports import export_trial_balance, export_journals
    jdf = st.session_state.ledger.to_dataframe()
    tb = trial_balance(st.session_state.ledger)
    if jdf.empty or tb.empty:
        st.info("Post some journals first.")
    else:
        tb_csv, tb_xlsx = "trial_balance.csv", "trial_balance.xlsx"
        j_csv, j_xlsx = "journals.csv", "journals.xlsx"
        export_trial_balance(tb, tb_csv, tb_xlsx)
        export_journals(jdf, j_csv, j_xlsx)
        with open(tb_csv, "rb") as f: st.download_button("Download Trial Balance (CSV)", f, file_name="trial_balance.csv")
        with open(tb_xlsx, "rb") as f: st.download_button("Download Trial Balance (Excel)", f, file_name="trial_balance.xlsx")
        with open(j_csv, "rb") as f: st.download_button("Download Journals (CSV)", f, file_name="journals.csv")
        with open(j_xlsx, "rb") as f: st.download_button("Download Journals (Excel)", f, file_name="journals.xlsx")
