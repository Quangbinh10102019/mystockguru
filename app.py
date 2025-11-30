import re
import math
import traceback
import streamlit as st
import pandas as pd
from vnstock import Finance

# === TIÊU ĐỀ ===
st.title("🎯 StockGuru Việt Nam")
st.markdown("### Nhập mã cổ phiếu để xem định giá!")

# === HỖ TRỢ CACHE CHO VIỆC LẤY DỮ LIỆU ===
@st.cache_data(ttl=3600)
def fetch_ratios_raw(symbol: str):
    """Trả về dữ liệu thô từ vnstock, không cố gắng ép kiểu."""
    finance = Finance(symbol=symbol, source='VCI')
    return finance.ratio(period='year', lang='vi')

# === HÀM HỖ TRỢ ===
def col_name_to_str(col):
    if isinstance(col, (tuple, list)):
        return " ".join([str(x) for x in col if x is not None])
    return str(col)

def find_column(df: pd.DataFrame, keywords):
    for col in df.columns:
        try:
            name = col_name_to_str(col).lower()
        except Exception:
            # bảo vệ nếu col không thể stringify
            name = str(col).lower()
        for kw in keywords:
            if kw.lower() in name:
                return col
    return None

def parse_number(x):
    if x is None:
        return None
    if isinstance(x, (int, float)) and not isinstance(x, bool):
        if isinstance(x, float) and math.isnan(x):
            return None
        return float(x)
    s = str(x).strip()
    if s in ("", "-", "—", "–", "NaN", "nan"):
        return None
    s = re.sub(r"[^\d\.,\-]", "", s)
    if s.count(",") > 0 and s.count(".") == 0:
        parts = s.split(",")
        if len(parts[-1]) <= 2:
            s = s.replace(",", ".")
        else:
            s = s.replace(",", "")
    else:
        s = s.replace(",", "")
    try:
        return float(s)
    except Exception:
        return None

# === Ô NHẬP VÀ NÚT ===
symbol = st.text_input("Mã cổ phiếu", placeholder="Ví dụ: FPT, VNM, VIC").strip().upper()

# === XỬ LÝ KHI NHẤN NÚT ===
if st.button("🔍 Phân tích ngay"):
    if not symbol:
        st.warning("Vui lòng nhập mã cổ phiếu!")
    else:
        with st.spinner(f"Đang lấy dữ liệu {symbol} từ VCI..."):
            try:
                raw = None
                try:
                    raw = fetch_ratios_raw(symbol)
                except Exception as e_fetch:
                    st.error("❌ Lỗi khi gọi vnstock.Finance.ratio().")
                    st.exception(e_fetch)
                    st.markdown("Traceback:")
                    st.text(traceback.format_exc())
                    # vẫn tiếp tục để in raw nếu có
                # Hiện debug về raw
                st.markdown("**DEBUG: kiểu dữ liệu trả về từ vnstock:**")
                st.write(type(raw))
                st.markdown("**DEBUG: repr(raw) (1000 ký tự đầu):**")
                st.write(repr(raw)[:1000])

                # Cố gắng chuẩn hóa sang DataFrame
                ratios = None
                if isinstance(raw, pd.DataFrame):
                    ratios = raw.copy()
                elif isinstance(raw, pd.Series):
                    ratios = raw.to_frame().T
                elif isinstance(raw, dict):
                    try:
                        ratios = pd.DataFrame.from_dict(raw)
                        # Nếu dict trả về là nested (keys là cột), transpose nếu cần
                        if ratios.shape[0] == 0 and ratios.shape[1] > 0:
                            ratios = ratios.T
                    except Exception:
                        try:
                            ratios = pd.DataFrame([raw])
                        except Exception:
                            ratios = None
                elif isinstance(raw, list):
                    try:
                        ratios = pd.DataFrame(raw)
                    except Exception:
                        ratios = None
                else:
                    # thử convert bằng DataFrame trực tiếp (thử mọi cách)
                    try:
                        ratios = pd.DataFrame(raw)
                    except Exception:
                        ratios = None

                if ratios is None:
                    st.error(f"❌ Không thể chuyển đổi dữ liệu trả về thành DataFrame cho **{symbol}**.")
                    st.markdown("Bạn có thể dán ở đây phần output `repr(raw)` để tôi xem cấu trúc.")
                    raise RuntimeError("Cannot convert vnstock result to DataFrame")

                # Hiện thông tin cột/ràng buộc để debug
                st.markdown("**DEBUG: Thông tin DataFrame sau khi chuẩn hoá:**")
                st.write("Type:", type(ratios))
                st.write("Shape:", getattr(ratios, "shape", None))
                st.markdown("Các cột (repr):")
                st.write([repr(c) for c in ratios.columns])
                st.dataframe(ratios.head(8))

                if ratios.empty:
                    st.error(f"❌ Không tìm thấy dữ liệu cho **{symbol}** (DataFrame rỗng).")
                else:
                    latest = ratios.iloc[0]

                    # mở rộng danh sách keyword để nhận dạng nhiều biến thể
                    pe_col = find_column(ratios, ["p/e", "pe", "p/e (x)", "pe (x)", "giá trên lợi nhuận", "pe x"])
                    eps_col = find_column(ratios, ["eps", "eps (vnd)", "eps (vnđ)", "eps (đ)", "lợi nhuận trên cổ phiếu", "eps vnd"])

                    st.write("DEBUG: pe_col, eps_col =", pe_col, eps_col)

                    pe_val = None
                    eps_val = None
                    try:
                        if pe_col is not None:
                            pe_val = latest[pe_col]
                    except Exception as e:
                        st.write("Không thể lấy giá trị P/E từ latest bằng pe_col:", repr(e))
                    try:
                        if eps_col is not None:
                            eps_val = latest[eps_col]
                    except Exception as e:
                        st.write("Không thể lấy giá trị EPS từ latest bằng eps_col:", repr(e))

                    pe = parse_number(pe_val)
                    eps = parse_number(eps_val)

                    if pe is None or eps is None:
                        st.error("❌ Dữ liệu P/E hoặc EPS không có hoặc không thể chuyển sang số.")
                        st.markdown("**Chi tiết dữ liệu thu được (dùng để debug):**")
                        st.dataframe(ratios.head(10))
                        st.markdown("**Các tên cột nhận dạng được:**")
                        col_names = [col_name_to_str(c) for c in ratios.columns]
                        st.write(col_names)
                        st.markdown("**Giá trị thô của ô P/E và EPS (trong latest):**")
                        st.write({"pe_raw": pe_val, "eps_raw": eps_val})
                    else:
                        if pe <= 0 or eps <= 0:
                            st.error("❌ Dữ liệu P/E hoặc EPS không hợp lệ (≤ 0).")
                        else:
                            current_price = pe * eps
                            industry_pe = 15
                            fair_value = eps * industry_pe
                            premium = float("inf") if current_price == 0 else (fair_value - current_price) / current_price * 100

                            st.success(f"✅ Phân tích thành công {symbol}!")
                            st.metric("Giá hiện tại (ước tính từ P/E * EPS)", f"{current_price:,.0f} VND")
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
                st.caption("Nếu lỗi vẫn xảy ra, vui lòng copy toàn bộ phần báo lỗi (traceback) và dán vào chat để tôi phân tích chi tiết.")
                st.exception(e)
                st.text(traceback.format_exc())
