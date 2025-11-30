import vnstock as vs
import pandas as pd

def analyze_stock_valuation(ticker: str, growth_2026: float, pe_target: float):
    """
    Phân tích định giá đơn giản cho 1 cổ phiếu.
    
    Args:
        ticker: Mã cổ phiếu (ví dụ: 'MSN')
        growth_2026: Tăng trưởng LN ròng năm 2026 so với TTM (dạng thập phân, ví dụ 0.138 = +13.8%)
        pe_target: P/E hợp lý năm 2026 (ví dụ 22.5)
    """
    
    # === 1. Lấy dữ liệu hiện tại ===
    price = vs.quote_price(ticker).iloc[0]['close']
    income_q = vs.financial_report(ticker, report_type="income", period="quarterly", last_n_quarters=4)
    
    net_profit_ttm = income_q['netIncome'].sum()  # Lợi nhuận TTM (tỷ VND)
    
    # Lấy số CP lưu hành
    overview = vs.company_overview(ticker)
    shares = overview['sharesOutstanding']  # đơn vị: cổ phiếu
    
    # EPS hiện tại
    eps_ttm = (net_profit_ttm * 1e9) / shares  # VND
    
    # === 2. Dự báo EPS 2026 ===
    net_profit_2026 = net_profit_ttm * (1 + growth_2026)
    eps_2026 = eps_ttm * (1 + growth_2026)
    
    # === 3. Định giá bằng P/E ===
    target_price = eps_2026 * pe_target
    
    # === 4. Output kết quả ===
    upside = (target_price - price) / price * 100
    
    print(f"📊 Phân tích định giá: {ticker}")
    print(f"Giá hiện tại: {price:,.0f} VND")
    print(f"Lợi nhuận TTM: {net_profit_ttm:,.0f} tỷ VND")
    print(f"EPS TTM: {eps_ttm:,.0f} VND")
    print(f"Dự báo LN 2026: {net_profit_2026:,.0f} tỷ (+{growth_2026:.1%})")
    print(f"EPS 2026: {eps_2026:,.0f} VND")
    print(f"P/E mục tiêu: {pe_target}x")
    print(f"🔹 Giá mục tiêu 2026: {target_price:,.0f} VND")
    print(f"📈 Upside: {upside:+.1f}%")
    
    if upside > 15:
        print("✅ Khuyến nghị: BUY")
    elif upside > 0:
        print("🔶 Khuyến nghị: HOLD/BUY")
    else:
        print("⚠️ Khuyến nghị: HOLD")

# === VÍ DỤ ÁP DỤNG CHO MSN ===
analyze_stock_valuation(
    ticker="MSN",
    growth_2026=0.138,   # +13.8% nhờ WCM lãi
    pe_target=22.5       # P/E hợp lý năm 2026
)
