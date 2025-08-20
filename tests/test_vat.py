from src.vat import compute_vat
def test_vat_std_inclusive():
    vat, net = compute_vat(115.0, "STD"); assert round(vat,2)==15.00 and round(net,2)==100.00
def test_vat_zero():
    vat, net = compute_vat(100.0, "ZERO"); assert vat==0.0 and net==100.0
def test_vat_exempt():
    vat, net = compute_vat(100.0, "EXEMPT"); assert vat==0.0 and net==100.0
