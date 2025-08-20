import pandas as pd
def export_trial_balance(tb_df: pd.DataFrame, csv_path: str, xlsx_path: str):
    tb_df.to_csv(csv_path, index=False)
    with pd.ExcelWriter(xlsx_path) as w:
        tb_df.to_excel(w, index=False, sheet_name="Trial Balance")
    return csv_path, xlsx_path
def export_journals(j_df: pd.DataFrame, csv_path: str, xlsx_path: str):
    j_df.to_csv(csv_path, index=False)
    with pd.ExcelWriter(xlsx_path) as w:
        j_df.to_excel(w, index=False, sheet_name="Journals")
    return csv_path, xlsx_path
