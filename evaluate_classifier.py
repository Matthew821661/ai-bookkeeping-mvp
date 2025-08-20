import pandas as pd
from src.classifier import classify

def evaluate(path="sample_data/golden_dataset.csv"):
    df = pd.read_csv(path)
    total = len(df)
    acc_count = 0
    vat_count = 0
    rows = []
    for _, r in df.iterrows():
        code, vat, conf, reason = classify(str(r["description"]), float(r["amount"]))
        ok_acc = int(code) == int(r["expected_account_code"])
        ok_vat = str(vat).upper() == str(r["expected_vat_code"]).upper()
        acc_count += 1 if ok_acc else 0
        vat_count += 1 if ok_vat else 0
        rows.append({
            "description": r["description"],
            "amount": r["amount"],
            "pred_code": code,
            "exp_code": int(r["expected_account_code"]),
            "acc_match": ok_acc,
            "pred_vat": vat,
            "exp_vat": r["expected_vat_code"],
            "vat_match": ok_vat,
            "confidence": conf,
            "reason": reason
        })
    acc = round(acc_count / total * 100, 2)
    vat = round(vat_count / total * 100, 2)
    print(f"Accuracy (Account): {acc}%")
    print(f"Accuracy (VAT): {vat}%")
    out = pd.DataFrame(rows)
    out.to_csv("sample_data/golden_eval_output.csv", index=False)
    print("Saved details to sample_data/golden_eval_output.csv")

if __name__ == "__main__":
    evaluate()
