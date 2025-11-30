import streamlit as st
from vnstock import Finance
import pandas as pd

# === TIÊU ĐỀ ===
st.set_page_config(page_title="StockGuru Việt Nam", layout="centered")
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
                # Khởi tạo đối tượng Finance với nguồn VCI
                finance = Finance(symbol=symbol, source='VCI')
                
                # Lấy chỉ số tài chính với tiếng Việt
                ratios = finance.ratio(period='year', lang='vi')
                
                if ratios.empty:
                    st.error(f"❌ Không tìm thấy dữ liệu cho **{symbol}**. Vui lòng thử mã HOSE như FPT, VNM, VIC.")
                else:
                    # === LẤY DỮ LIỆU P/E VÀ EPS THEO ĐÚNG CẤU TRÚC TÀI LIỆU ===
                    # Theo tài liệu: https://vnstocks.com/docs/vnstock/bao-cao-tai-chinh#chi-so-tai-chinh
                    # Cấu trúc cột là MultiIndex: ('Chỉ tiêu định giá', 'P/E'), ('Chỉ tiêu định giá', 'EPS (VND)')
                    
                    # Lấy năm mới nhất (dòng đầu tiên)
                    latest_row = ratios.iloc[0]
                    
                    # Truy xuất P/E và EPS theo đúng tên cột trong tài liệu
                    try:
                        # Cột P/E: ('Chỉ tiêu định giá', 'P/E')
                        pe_col = ('Chỉ tiêu định giá', 'P/E')
                        pe = latest_row[pe_col] if pe_col in latest_row.index else None
                        
                        # Cột EPS: ('Chỉ tiêu định giá', 'EPS (VND)')
                        eps_col = ('Chỉ tiêu định giá', 'EPS (VND)')
                        eps = latest_row[eps_col] if eps_col in latest_row.index else None
                    except Exception as e:
                        st.error(f"Lỗi truy xuất dữ liệu: {str(e)}")
                        st.stop()
                    
                    # === KIỂM TRA DỮ LIỆU HỢP LỆ ===
                    if pe is None or eps is None:
                        st.error("❌ Dữ liệu P/E hoặc EPS không có. Cổ phiếu này có thể không đủ thông tin định giá trên VCI.")
                    elif pe <= 0 or eps <= 0:
                        st.error("❌ Dữ liệu P/E hoặc EPS không hợp lệ (≤ 0).")
                    else:
                        # === TÍNH TOÁN GIÁ TRỊ HỢP LÝ ===
                        current_price = pe * eps
                        industry_pe = 15  # P/E ngành trung bình (có thể điều chỉnh)
                        fair_value = eps * industry_pe
                        premium = (fair_value - current_price) / current_price * 100
                        
                        # === HIỂN THỊ KẾT QUẢ ===
                        st.success(f"✅ Phân tích thành công {symbol}!")
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Giá hiện tại", f"{current_price:,.0f} VND")
                        col2.metric("Giá trị hợp lý", f"{fair_value:,.0f} VND")
                        col3.metric("Chênh lệch", f"{premium:+.1f}%")
                        
                        # === KHUYẾN NGHỊ ===
                        if premium > 15:
                            st.markdown("### 🟢 **KHUYẾN NGHỊ: MUA** — Cổ phiếu đang định giá thấp!")
                        elif premium > -5:
                            st.markdown("### 🟡 **KHUYẾN NGHỊ: GIỮ** — Định giá hợp lý.")
                        else:
                            st.markdown("### 🔴 **KHUYẾN NGHỊ: BÁN** — Cổ phiếu đang định giá cao.")
                        
                        # === HIỂN THỊ THÊM THÔNG TIN ===
                        st.subheader("📊 Thông tin chi tiết")
                        st.write(f"- **P/E hiện tại**: {pe:.2f}x")
                        st.write(f"- **EPS**: {eps:,.0f} VND")
                        st.write(f"- **P/E ngành tham chiếu**: {industry_pe}x")
            
            except Exception as e:
                st.error(f"❌ Lỗi khi phân tích {symbol}: {str(e)}")
                st.caption("Gợi ý: Dùng mã HOSE chuẩn như FPT, VNM, VIC, VCB, HPG...")

# === Footer ===
st.markdown("---")
st.caption("Dữ liệu từ VCI qua thư viện vnstock. Miễn phí – không quảng cáo.")
