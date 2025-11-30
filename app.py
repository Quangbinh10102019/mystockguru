import streamlit as st
from vnstock import Finance

st.set_page_config(
    page_title="StockGuru Việt Nam",
    page_icon="🎯",
    layout="centered"
)

st.markdown("<h1 style='text-align: center; color: #007BFF;'>🎯 StockGuru Việt Nam</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #666;'>Phân tích & định giá cổ phiếu chỉ trong 1 click</h3>", unsafe_allow_html=True)

with st.form("stock_analysis_form"):
    symbol = st.text_input("Nhập mã cổ phiếu", value="", placeholder="Ví dụ: FPT, VNM, VIC...").strip().upper()
    submitted = st.form_submit_button("🔍 Phân tích ngay", use_container_width=True)

if submitted:
    if not symbol:
        st.warning("⚠️ Vui lòng nhập mã cổ phiếu!")
    else:
        with st.spinner(f"Đang phân tích {symbol} từ dữ liệu TCBS..."):
            try:
                # ✅ SỬA CHÍNH: DÙNG TCBS THAY VÌ VCI (tránh 403 Forbidden)
                finance = Finance(symbol=symbol, source='TCBS')
                ratios = finance.ratio(period='year', lang='vi')

                if ratios.empty:
                    st.error(f"❌ Không tìm thấy dữ liệu cho mã **{symbol}**. Vui lòng thử lại sau.")
                else:
                    # ✅ SỬA CHÍNH: XÁC ĐỊNH CỘT ĐÚNG THEO TÀI LIỆU
                    pe_col = ('Chỉ tiêu định giá', 'P/E')
                    eps_col = ('Chỉ tiêu định giá', 'EPS (VND)')
                    
                    # Kiểm tra cột tồn tại
                    if pe_col not in ratios.columns or eps_col not in ratios.columns:
                        st.error("❌ Không tìm thấy dữ liệu P/E hoặc EPS. Mã cổ phiếu này có thể không hỗ trợ trên TCBS.")
                        st.info("💡 Gợi ý: Thử các mã phổ biến như FPT, VNM, VIC, VCB, HPG...")
                    else:
                        latest = ratios.iloc[0]
                        pe = latest[pe_col]
                        eps = latest[eps_col]
                        
                        if pe <= 0 or eps <= 0:
                            st.error("❌ Dữ liệu P/E hoặc EPS không hợp lệ (≤ 0).")
                        else:
                            # Tính toán giá trị hợp lý
                            current_price = pe * eps
                            industry_pe = 15  # P/E trung bình ngành
                            fair_value = eps * industry_pe
                            premium = (fair_value - current_price) / current_price * 100
                            
                            # Hiển thị kết quả
                            st.success(f"✅ Phân tích thành công **{symbol}**")
                            
                            col1, col2, col3 = st.columns(3)
                            col1.metric("Giá hiện tại", f"{current_price:,.0f} VND")
                            col2.metric("Giá trị hợp lý", f"{fair_value:,.0f} VND")
                            col3.metric("Chênh lệch", f"{premium:+.1f}%")
                            
                            # Khuyến nghị
                            if premium > 25:
                                st.markdown("### 🟢 **KHUYẾN NGHỊ: STRONG BUY**\nCổ phiếu đang định giá rất thấp so với giá trị thực.")
                            elif premium > 15:
                                st.markdown("### 🟢 **KHUYẾN NGHỊ: BUY**\nCổ phiếu đang định giá thấp.")
                            elif premium > -5:
                                st.markdown("### 🟡 **KHUYẾN NGHỊ: HOLD**\nĐịnh giá hợp lý.")
                            else:
                                st.markdown("### 🔴 **KHUYẾN NGHỊ: SELL**\nCổ phiếu đang định giá cao.")
                            
                            # Thông tin chi tiết
                            st.subheader("📊 Thông tin chi tiết")
                            st.write(f"- **P/E hiện tại**: {pe:.2f}x")
                            st.write(f"- **EPS**: {eps:,.0f} VND")
                            st.write(f"- **P/E ngành tham chiếu**: {industry_pe}x")
            
            except Exception as e:
                st.error(f"❌ Lỗi khi phân tích {symbol}: {str(e)}")
                st.info("💡 Gợi ý: Sử dụng mã cổ phiếu HOSE phổ biến như FPT, VNM, VIC, VCB, HPG...")

st.markdown("---")
st.caption("Dữ liệu từ TCBS qua thư viện vnstock. Miễn phí - không quảng cáo.")
