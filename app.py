import streamlit as st
from vnstock import Finance

# Cấu hình trang
st.set_page_config(
    page_title="StockGuru Việt Nam",
    page_icon="🎯",
    layout="centered"
)

# Tiêu đề
st.markdown("<h1 style='text-align: center; color: #007BFF;'>🎯 StockGuru Việt Nam</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #666;'>Phân tích & định giá cổ phiếu chỉ trong 1 click</h3>", unsafe_allow_html=True)

# Form nhập mã cổ phiếu
with st.form("stock_analysis_form"):
    symbol = st.text_input("Nhập mã cổ phiếu", value="", placeholder="Ví dụ: FPT, VNM, VIC...").strip().upper()
    submitted = st.form_submit_button("🔍 Phân tích ngay", use_container_width=True)

if submitted:
    if not symbol:
        st.warning("⚠️ Vui lòng nhập mã cổ phiếu!")
    else:
        with st.spinner(f"Đang phân tích {symbol} từ dữ liệu VCI..."):
            try:
                # Khởi tạo đối tượng Finance từ vnstock
                finance = Finance(symbol=symbol, source='VCI')
                
                # Lấy chỉ số tài chính với tiếng Việt
                ratios = finance.ratio(period='year', lang='vi')
                
                if ratios.empty:
                    st.error(f"❌ Không tìm thấy dữ liệu cho mã **{symbol}**. Vui lòng kiểm tra lại mã cổ phiếu.")
                else:
                    # Lấy năm mới nhất
                    latest_year = ratios[('Meta', 'Năm')].iloc[0]
                    
                    # Lấy P/E và EPS theo đúng cấu trúc MultiIndex
                    pe_col = ('Chỉ tiêu định giá', 'P/E')
                    eps_col = ('Chỉ tiêu định giá', 'EPS (VND)')
                    
                    if pe_col in ratios.columns and eps_col in ratios.columns:
                        pe = ratios[pe_col].iloc[0]
                        eps = ratios[eps_col].iloc[0]
                        
                        if pe <= 0 or eps <= 0:
                            st.error("❌ Dữ liệu P/E hoặc EPS không hợp lệ (≤ 0).")
                        else:
                            # Tính toán giá trị hợp lý
                            current_price = pe * eps
                            industry_pe = 15  # P/E trung bình ngành
                            fair_value = eps * industry_pe
                            premium = (fair_value - current_price) / current_price * 100
                            
                            # Hiển thị kết quả
                            st.success(f"✅ Phân tích thành công **{symbol}** ({latest_year})")
                            
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
                            
                            # Hiển thị thông tin chi tiết
                            st.subheader("📊 Thông tin chi tiết")
                            st.write(f"- **P/E hiện tại**: {pe:.2f}x")
                            st.write(f"- **EPS**: {eps:,.0f} VND")
                            st.write(f"- **P/E ngành tham chiếu**: {industry_pe}x")
                            
                    else:
                        st.error("❌ Không tìm thấy dữ liệu P/E hoặc EPS trong báo cáo tài chính.")
            
            except Exception as e:
                st.error(f"❌ Lỗi khi phân tích {symbol}: {str(e)}")
                st.info("💡 Gợi ý: Sử dụng mã cổ phiếu HOSE phổ biến như FPT, VNM, VIC, VCB, HPG...")

# Footer
st.markdown("---")
st.caption("Dữ liệu từ VCI qua thư viện vnstock. Miễn phí - không quảng cáo.")
