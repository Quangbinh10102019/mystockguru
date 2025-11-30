import streamlit as st
from vnstock import Finance

# === TIÊU ĐỀ ===
st.title("🎯 StockGuru Việt Nam")
st.markdown("### Nhập mã cổ phiếu để xem định giá!")

# === Ô NHẬP VÀ NÚT ===
symbol = st.text_input("Mã cổ phiếu", placeholder="Ví dụ: FPT, VNM, VIC").strip().upper()

# === XỬ LÝ KHI NHẤN NÚT ===
if st.button("🔍 Phân tích ngay"):
    if not symbol:
        st.warning("Vui lòng nhập mã cổ phiếu!")
    else:
        with st.spinner(f"Đang lấy dữ liệu {symbol} từ VCI..."):
            try:
                finance = Finance(symbol=symbol, source='VCI')
                ratios = finance.ratio(period='year', lang='vi')

                if ratios.empty:
                    st.error(f"❌ Không tìm thấy dữ liệu cho **{symbol}**. Vui lòng thử mã HOSE như FPT, VNM, VIC.")
                else:
                    latest = ratios.iloc[0]

                    # ✅ SỬA LỖI: Truy xuất đúng MultiIndex
                    try:
                        pe = latest[('Chỉ tiêu định giá', 'P/E')]
                        eps = latest[('Chỉ tiêu định giá', 'EPS (VND)')]
                    except KeyError:
                        pe = None
                        eps = None

                    if pe is None or eps is None:
                        st.error("❌ Dữ liệu P/E hoặc EPS không có. Cổ phiếu này có thể không đủ thông tin định giá.")
                    elif pe <= 0 or eps <= 0:
                        st.error("❌ Dữ liệu P/E hoặc EPS không hợp lệ (≤ 0).")
                    else:
                        current_price = pe * eps
                        industry_pe = 15
                        fair_value = eps * industry_pe
                        premium = (fair_value - current_price) / current_price * 100

                        st.success(f"✅ Phân tích thành công {symbol}!")
                        st.metric("Giá hiện tại", f"{current_price:,.0f} VND")
                        st.metric("Giá trị hợp lý (P/E=15)", f"{fair_value:,.0f} VND")
                        st.metric("Chênh lệch", f"{premium:+.1f}%")

                        if premium > 15:
                            st.markdown("### 🟢 **KHUYẾN NGHỊ: MUA**")
                        elif premium > -5:
                            st.markdown("### 🟡 **KHUYẾN NGHỊ: GIỮ**")
                        else:
                            st.markdown("### 🔴 **KHUYẾN NGHỊ: BÁN**")

            except Exception as e:
                st.error(f"❌ Lỗi khi phân tích {symbol}.")
                st.caption("Gợi ý: Dùng mã HOSE chuẩn như FPT, VNM, VIC, VCB, HPG...")

# === Footer ===
st.markdown("---")
st.caption("Dữ liệu từ VCI qua thư viện vnstock. Miễn phí – không quảng cáo.")
