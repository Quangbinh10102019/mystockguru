import streamlit as st
from vnstock import Finance

st.set_page_config(page_title="StockGuru Việt Nam", layout="centered")
st.title("🎯 StockGuru Việt Nam")
st.markdown("### Phân tích & định giá cổ phiếu — chỉ cần nhập mã!")

import re

symbol_input = st.text_input("Nhập mã cổ phiếu", placeholder="Ví dụ: FPT, VNM, VIC")
symbol = (symbol_input or "").strip().upper()
# optional: keep only letters, digits and dot (adjust regex as needed)
symbol = re.sub(r'[^A-Z0-9.]', '', symbol)
if st.button("🔍 Phân tích ngay"):
    if not symbol:
        st.warning("Vui lòng nhập mã cổ phiếu!")
    else:
        try:
            with st.spinner(f"Đang lấy dữ liệu {symbol} từ VCI..."):
                # Lấy dữ liệu từ VCI (nguồn uy tín)
                finance = Finance(symbol=symbol, source='VCI')
                ratios = finance.ratio(period='year', lang='vi')  # ← DÙNG TIẾNG VIỆT
                
                if ratios.empty:
                    st.error(f"❌ Không tìm thấy dữ liệu cho **{symbol}**. Vui lòng kiểm tra lại mã.")
                else:
                    # Lấy dữ liệu mới nhất
                    latest = ratios.iloc[0]
                    
                    # Tìm P/E
                    if ('Chỉ tiêu định giá', 'P/E') in ratios.columns:
                        pe_val = ratios[('Chỉ tiêu định giá', 'P/E')].iloc[0]
                    else:
                        pe_val = None
                    
                    # Tìm EPS
                    if ('Chỉ tiêu định giá', 'EPS (VND)') in ratios.columns:
                        eps_val = ratios[('Chỉ tiêu định giá', 'EPS (VND)')].iloc[0]
                    else:
                        eps_val = None
                    
                    pe = pe_val
                    eps = eps_val
                    
                    if pe and eps:
                        current_price = pe * eps
                        # Giả định P/E ngành = 15 (có thể điều chỉnh sau)
                        industry_pe = 15
                        fair_value = eps * industry_pe
                        premium = (fair_value - current_price) / current_price * 100
                        
                        st.success(f"✅ Phân tích thành công {symbol}!")
                        st.metric("Giá hiện tại", f"{current_price:,.0f} VND")
                        st.metric("Giá trị hợp lý (P/E=15)", f"{fair_value:,.0f} VND")
                        st.metric("Chênh lệch", f"{premium:+.1f}%")
                        
                        if premium > 15:
                            st.markdown("### 🟢 **KHUYẾN NGHỊ: MUA** — Cổ phiếu đang định giá thấp!")
                        elif premium > -5:
                            st.markdown("### 🟡 **KHUYẾN NGHỊ: GIỮ** — Định giá hợp lý.")
                        else:
                            st.markdown("### 🔴 **KHUYẾN NGHỊ: BÁN** — Cổ phiếu đang định giá cao.")
                    else:
                        st.error("❌ Thiếu dữ liệu P/E hoặc EPS. Thử lại sau.")
        except Exception as e:
            st.error(f"❌ Không phân tích được {symbol}. Mã có thể không tồn tại hoặc không có dữ liệu.")
            st.caption("Gợi ý: Dùng mã chuẩn HOSE như FPT, VNM, VIC, VCB...")

st.markdown("---")
st.caption("Dữ liệu từ VCI qua thư viện vnstock. Miễn phí – không quảng cáo.")
