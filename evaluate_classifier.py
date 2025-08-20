import pandas as pd
from src.classifier import classify
def evaluate(path='sample_data/golden_dataset.csv'):
    df = pd.read_csv(path); total=len(df); acc=vat=0; rows=[]
    from src.chart_of_accounts import NAME_TO_CODE
    for _, r in df.iterrows():
        code, vat_code, conf, reason = classify(str(r["description"]), float(r["amount"]))
        ok_acc = int(code) == int(r["expected_account_code"]); ok_vat = vat_code.upper()==str(r["expected_vat_code"]).upper()
        acc += 1 if ok_acc else 0; vat += 1 if ok_vat else 0
        rows.append({"description":r["description"],"pred_code":code,"exp_code":int(r["expected_account_code"]),"acc_match":ok_acc,"pred_vat":vat_code,"exp_vat":r["expected_vat_code"],"vat_match":ok_vat,"confidence":conf,"reason":reason})
    print(f"Accuracy (Account): {acc/total*100:.2f}%"); print(f"Accuracy (VAT): {vat/total*100:.2f}%")
    pd.DataFrame(rows).to_csv("sample_data/golden_eval_output.csv", index=False); print("Saved details to sample_data/golden_eval_output.csv")
if __name__=='__main__': evaluate()
