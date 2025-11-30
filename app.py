with st.spinner(f"Đang lấy dữ liệu {symbol} từ VCI..."):
    try:
        from vnstock import Finance
        finance = Finance(symbol=symbol, source='VCI')
        ratios = finance.ratio(period='year', lang='vi')  # DÙNG TIẾNG VIỆT — đúng như tài liệu

        if ratios.empty:
            st.error(f"❌ Không tìm thấy dữ liệu cho **{symbol}**. Vui lòng kiểm tra lại mã (chỉ hỗ trợ mã HOSE).")
        else:
            # === LẤY DỮ LIỆU MỚI NHẤT (dòng đầu tiên) ===
            latest_row = ratios.iloc[0]

            # === AN TOÀN: DÙNG TUPLE ĐÚNG NHƯ TRONG TÀI LIỆU ===
            pe_val = latest_row.get(('Chỉ tiêu định giá', 'P/E'), None)
            eps_val = latest_row.get(('Chỉ tiêu định giá', 'EPS (VND)'), None)

            # === KIỂM TRA DỮ LIỆU HỢP LỆ ===
            if pe_val is None or eps_val is None:
                st.error("❌ Thiếu dữ liệu P/E hoặc EPS. Cổ phiếu này có thể không có đủ thông tin định giá trên VCI.")
            elif pe_val <= 0 or eps_val <= 0:
                st.error("❌ Dữ liệu P/E hoặc EPS không hợp lệ (≤ 0). Không thể định giá.")
            else:
                # === TÍNH TOÁN GIÁ TRỊ HỢP LÝ ===
                current_price = pe_val * eps_val
                industry_pe = 15  # Bạn có thể thay bằng P/E ngành thực tế sau này
                fair_value = eps_val * industry_pe
                premium = (fair_value - current_price) / current_price * 100

                # === HIỂN THỊ KẾT QUẢ ===
                st.success(f"✅ Phân tích thành công {symbol}!")
                st.metric("Giá hiện tại", f"{current_price:,.0f} VND")
                st.metric("Giá trị hợp lý (P/E=15)", f"{fair_value:,.0f} VND")
                st.metric("Chênh lệch", f"{premium:+.1f}%")

                # === KHUYẾN NGHỊ ===
                if premium > 15:
                    st.markdown("### 🟢 **KHUYẾN NGHỊ: MUA** — Cổ phiếu đang định giá thấp!")
                elif premium > -5:
                    st.markdown("### 🟡 **KHUYẾN NGHỊ: GIỮ** — Định giá hợp lý.")
                else:
                    st.markdown("### 🔴 **KHUYẾN NGHỊ: BÁN** — Cổ phiếu đang định giá cao.")

    except Exception as e:
        st.error(f"❌ Lỗi khi truy xuất dữ liệu {symbol}: {str(e)}")
        st.caption("Gợi ý: Thử lại với mã HOSE phổ biến như FPT, VNM, VIC, VCB, HPG...")
