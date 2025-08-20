import pandas as pd
from typing import Tuple
def export_trial_balance(tb_df: pd.DataFrame, path_csv: str, path_xlsx: str) -> Tuple[str,str]:
    tb_df.to_csv(path_csv, index=False)
    with pd.ExcelWriter(path_xlsx) as w:
        tb_df.to_excel(w, index=False, sheet_name="Trial Balance")
    return path_csv, path_xlsx
def export_journals(j_df: pd.DataFrame, path_csv: str, path_xlsx: str) -> Tuple[str,str]:
    j_df.to_csv(path_csv, index=False)
    with pd.ExcelWriter(path_xlsx) as w:
        j_df.to_excel(w, index=False, sheet_name="Journals")
    return path_csv, path_xlsx
