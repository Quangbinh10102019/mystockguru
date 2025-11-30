import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import time

# Config trang
st.set_page_config(
    page_title="StockGuru Việt Nam - VNIndex Pro",
    page_icon="🎯",
    layout="wide"
)

# CSS tuỳ chỉnh
st.markdown("""
<style>
    .stMetric {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .stMetric > div {
        text-align: center !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px;
        color: #4a4a4a;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0066cc;
        color: white;
    }
    div[data-testid="stForm"] {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .recommendation-box {
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #0066cc;
    }
    .strong-buy {
        background-color: rgba(0, 204, 102, 0.1);
        border-left-color: #00cc66;
    }
    .buy {
        background-color: rgba(51, 153, 102, 0.1);
        border-left-color: #339966;
    }
    .hold {
        background-color: rgba(255, 153, 0, 0.1);
        border-left-color: #ff9900;
    }
    .reduce {
        background-color: rgba(255, 51, 51, 0.1);
        border-left-color: #ff3333;
    }
    .sell {
        background-color: rgba(204, 0, 0, 0.1);
        border-left-color: #cc0000;
    }
</style>
""", unsafe_allow_html=True)

# Danh sách cổ phiếu VN30
VN30_STOCKS = [
    'VNM', 'VIC', 'FPT', 'VHM', 'HPG', 'TCB', 'MSN', 'VRE', 'MWG', 'BID', 
    'CTG', 'VCB', 'ACB', 'MBB', 'TPB', 'GAS', 'VJC', 'BVH', 'SSI', 'VIB',
    'POW', 'PLX', 'NVL', 'KDH', 'HDB', 'PNJ', 'SAB', 'REE', 'VCB', 'VHM'
]

# Phân loại ngành
STOCK_INDUSTRY_MAP = {
    # Ngân hàng
    'BID': 'Ngân hàng', 'CTG': 'Ngân hàng', 'VCB': 'Ngân hàng', 'ACB': 'Ngân hàng', 'MBB': 'Ngân hàng', 
    'TPB': 'Ngân hàng', 'VPB': 'Ngân hàng', 'TCB': 'Ngân hàng', 'HDB': 'Ngân hàng', 'STB': 'Ngân hàng', 
    'VIB': 'Ngân hàng', 'EIB': 'Ngân hàng', 'SHB': 'Ngân hàng', 'LPB': 'Ngân hàng', 'MSB': 'Ngân hàng',
    # Bất động sản
    'VIC': 'Bất động sản', 'VHM': 'Bất động sản', 'NVL': 'Bất động sản', 'PDR': 'Bất động sản', 
    'DXG': 'Bất động sản', 'KDH': 'Bất động sản', 'NLG': 'Bất động sản', 'VRE': 'Bất động sản',
    # Tiêu dùng
    'VNM': 'Tiêu dùng', 'MSN': 'Tiêu dùng', 'MWG': 'Tiêu dùng', 'PNJ': 'Tiêu dùng', 'SAB': 'Tiêu dùng', 
    'HAG': 'Tiêu dùng', 'DGC': 'Tiêu dùng', 'GAS': 'Tiêu dùng', 'REE': 'Tiêu dùng',
    # Chứng khoán
    'SSI': 'Chứng khoán', 'VND': 'Chứng khoán', 'HCM': 'Chứng khoán', 'TVS': 'Chứng khoán', 'AGR': 'Chứng khoán',
    # Công nghiệp
    'VJC': 'Công nghiệp', 'HVN': 'Công nghiệp', 'FPT': 'Công nghiệp', 'HPG': 'Công nghiệp', 'POW': 'Công nghiệp',
    # Năng lượng & Nguyên liệu
    'PLX': 'Năng lượng', 'DPM': 'Nguyên liệu', 'DRC': 'Nguyên liệu', 'BWE': 'Năng lượng', 'PC1': 'Công nghiệp'
}

# P/E trung bình ngành
INDUSTRY_PE = {
    'Ngân hàng': 8.5,
    'Bất động sản': 6.5,
    'Tiêu dùng': 20.0,
    'Chứng khoán': 16.0,
    'Công nghiệp': 12.0,
    'Năng lượng': 14.0,
    'Nguyên liệu': 10.0,
    'Khác': 15.0
}

# P/B trung bình ngành
INDUSTRY_PB = {
    'Ngân hàng': 1.2,
    'Bất động sản': 0.9,
    'Tiêu dùng': 3.5,
    'Chứng khoán': 2.5,
    'Công nghiệp': 1.8,
    'Năng lượng': 1.5,
    'Nguyên liệu': 1.3,
    'Khác': 2.0
}

class StockAnalyzer:
    def __init__(self, symbol, source='TCBS'):
        self.symbol = symbol.upper()
        self.source = source
        self.ratios = None
        self.income = None
        self.balance = None
        self.cashflow = None
        self.load_financial_data()
    
    def load_financial_data(self):
        """Tải dữ liệu tài chính từ nguồn đã chọn (VCI/TCBS)"""
        try:
            from vnstock import Vnstock
            # Khởi tạo đúng cách cho TCBS
            self.stock_obj = Vnstock().stock(symbol=self.symbol, source=self.source)
            self.finance = self.stock_obj.finance
            
            # Lấy chỉ số tài chính
            try:
                self.ratios = self.finance.ratio(period='year')
                if self.ratios is not None and not self.ratios.empty:
                    # Kiểm tra cột P/E để xác định nguồn dữ liệu
                    if self.source == 'TCBS' and 'pe' not in self.ratios.columns:
                        st.warning(f"⚠️ Dữ liệu {self.symbol} có thể không đầy đủ. Thử dùng VCI nếu cần.")
            except Exception as e:
                st.warning(f"⚠️ Không tải được chỉ số tài chính cho {self.symbol}: {str(e)}")
            
            # Lấy báo cáo KQKD
            try:
                self.income = self.finance.income_statement(period='year')
            except Exception as e:
                st.warning(f"⚠️ Không tải được báo cáo KQKD cho {self.symbol}: {str(e)}")
            
            # Lấy báo cáo CĐKT
            try:
                self.balance = self.finance.balance_sheet(period='year')
            except Exception as e:
                st.warning(f"⚠️ Không tải được báo cáo CĐKT cho {self.symbol}: {str(e)}")
            
            # Lấy báo cáo LCTT
            try:
                self.cashflow = self.finance.cash_flow(period='year')
            except Exception as e:
                st.warning(f"⚠️ Không tải được báo cáo LCTT cho {self.symbol}: {str(e)}")
                
        except Exception as e:
            st.error(f"❌ Lỗi khi kết nối dữ liệu {self.source}: {str(e)}")
    
    def get_latest_financial_metrics(self):
        """Lấy các chỉ số tài chính quan trọng nhất với xử lý đa nguồn dữ liệu"""
        if self.ratios is None or self.ratios.empty:
            st.error("❌ Không tải được dữ liệu tài chính")
            return None
        
        try:
            # Lấy năm mới nhất
            latest_year = self.ratios.index[0]
            latest = self.ratios.loc[latest_year]
            
            # Xác định nguồn dữ liệu (VCI vs TCBS)
            is_vci = isinstance(self.ratios.columns, pd.MultiIndex)
            
            # Hàm trợ giúp lấy giá trị an toàn
            def safe_get_value(keys):
                """Lấy giá trị an toàn với nhiều tên cột có thể"""
                for key in keys:
                    if key in latest.index:
                        value = latest[key]
                        if pd.notna(value) and isinstance(value, (int, float)) and value > 0:
                            return float(value)
                return None
            
            # Trích xuất các chỉ số quan trọng
            if is_vci:
                # Dữ liệu VCI (MultiIndex)
                pe_ratio = safe_get_value([
                    ('Chỉ tiêu định giá', 'P/E'),
                    ('Valuation Ratios', 'P/E')
                ])
                pb_ratio = safe_get_value([
                    ('Chỉ tiêu định giá', 'P/B'),
                    ('Valuation Ratios', 'P/B')
                ])
                eps = safe_get_value([
                    ('Chỉ tiêu định giá', 'EPS (VND)'),
                    ('Valuation Ratios', 'EPS (VND)')
                ])
                bvps = safe_get_value([
                    ('Chỉ tiêu định giá', 'BVPS (VND)'),
                    ('Valuation Ratios', 'BVPS (VND)')
                ])
                market_cap = safe_get_value([
                    ('Chỉ tiêu định giá', 'Vốn hóa (Tỷ đồng)'),
                    ('Valuation Ratios', 'Market Cap (Bn VND)')
                ])
                shares_outstanding = safe_get_value([
                    ('Chỉ tiêu định giá', 'Số CP lưu hành (Triệu CP)'),
                    ('Valuation Ratios', 'Shares Outstanding (Million)')
                ])
                
                roe = safe_get_value([
                    ('Chỉ tiêu khả năng sinh lợi', 'ROE (%)'),
                    ('Profitability Ratios', 'ROE (%)')
                ])
                roa = safe_get_value([
                    ('Chỉ tiêu khả năng sinh lợi', 'ROA (%)'),
                    ('Profitability Ratios', 'ROA (%)')
                ])
                gross_margin = safe_get_value([
                    ('Chỉ tiêu khả năng sinh lợi', 'Biên lợi nhuận gộp (%)'),
                    ('Profitability Ratios', 'Gross Margin (%)')
                ])
                net_margin = safe_get_value([
                    ('Chỉ tiêu khả năng sinh lợi', 'Biên lợi nhuận ròng (%)'),
                    ('Profitability Ratios', 'Net Profit Margin (%)')
                ])
                current_ratio = safe_get_value([
                    ('Chỉ tiêu thanh khoản', 'Chỉ số thanh toán hiện thời'),
                    ('Liquidity Ratios', 'Current Ratio')
                ])
                debt_to_equity = safe_get_value([
                    ('Chỉ tiêu cơ cấu nguồn vốn', 'Nợ/VCSH'),
                    ('Financial Structure Ratios', 'Debt to Equity')
                ])
            else:
                # Dữ liệu TCBS (cột đơn giản)
                pe_ratio = safe_get_value(['pe', 'priceToEarning', 'P/E'])
                pb_ratio = safe_get_value(['pb', 'priceToBook', 'P/B'])
                eps = safe_get_value(['eps', 'earningsPerShare', 'EPS'])
                bvps = safe_get_value(['bvps', 'bookValuePerShare', 'BVPS'])
                market_cap = safe_get_value(['marketCap', 'Vốn hóa (Tỷ đồng)'])
                shares_outstanding = safe_get_value(['sharesOutstanding', 'Số CP lưu hành (Triệu CP)'])
                
                roe = safe_get_value(['roe', 'returnOnEquity', 'ROE'])
                roa = safe_get_value(['roa', 'returnOnAssets', 'ROA'])
                gross_margin = safe_get_value(['grossMargin', 'Biên lợi nhuận gộp'])
                net_margin = safe_get_value(['netMargin', 'Biên lợi nhuận ròng'])
                current_ratio = safe_get_value(['currentRatio', 'Hệ số thanh toán hiện thời'])
                debt_to_equity = safe_get_value(['debtToEquity', 'Nợ/VCSH'])
            
            # Chuyển đổi đơn vị (nếu cần)
            if eps is not None and is_vci:
                eps = eps * 1000  # Chuyển từ nghìn đồng → VND
            if bvps is not None and is_vci:
                bvps = bvps * 1000  # Chuyển từ nghìn đồng → VND
            
            # Tính toán EPS CAGR (nếu có dữ liệu)
            eps_cagr = 0
            if eps is not None:
                if is_vci:
                    eps_col = ('Chỉ tiêu định giá', 'EPS (VND)')
                else:
                    eps_col = 'eps'
                
                if eps_col in self.ratios.columns:
                    eps_values = self.ratios[eps_col].values[:3]
                    if len(eps_values) >= 3 and eps_values[2] > 0:
                        eps_cagr = (eps_values[0] / eps_values[2]) ** (1/2) - 1
            
            # Validate dữ liệu
            if eps is None or bvps is None or pe_ratio is None or pb_ratio is None:
                st.error("❌ Dữ liệu không đầy đủ để tính toán")
                return None
            
            return {
                'year': latest_year,
                'pe_ratio': pe_ratio,
                'pb_ratio': pb_ratio,
                'eps': eps,
                'bvps': bvps,
                'market_cap': market_cap,
                'shares_outstanding': shares_outstanding,
                'roe': roe,
                'roa': roa,
                'gross_margin': gross_margin,
                'net_margin': net_margin,
                'current_ratio': current_ratio,
                'debt_to_equity': debt_to_equity,
                'eps_cagr': eps_cagr * 100
            }
            
        except Exception as e:
            st.error(f"❌ Lỗi khi xử lý dữ liệu tài chính: {str(e)}")
            return None
    
    def get_industry_pe(self):
        """Lấy P/E trung bình ngành phù hợp với cổ phiếu"""
        industry = STOCK_INDUSTRY_MAP.get(self.symbol, 'Khác')
        return INDUSTRY_PE.get(industry, 15.0)
    
    def get_industry_pb(self):
        """Lấy P/B trung bình ngành"""
        industry = STOCK_INDUSTRY_MAP.get(self.symbol, 'Khác')
        return INDUSTRY_PB.get(industry, 2.0)
    
    def calculate_fair_value(self, metrics):
        """Tính giá trị hợp lý bằng nhiều phương pháp"""
        if metrics is None:
            return None
        
        try:
            current_price = metrics['pe_ratio'] * metrics['eps']
            results = {
                'current_price': current_price,
                'methods': {},
                'premiums': {}
            }
            
            # 1. P/E so sánh ngành
            industry_pe_avg = self.get_industry_pe()
            pe_fair = metrics['eps'] * industry_pe_avg
            results['methods']['pe_industry'] = pe_fair
            results['premiums']['pe_industry'] = (pe_fair - current_price) / current_price * 100
            
            # 2. P/B so sánh ngành
            industry_pb_avg = self.get_industry_pb()
            pb_fair = metrics['bvps'] * industry_pb_avg
            results['methods']['pb_industry'] = pb_fair
            results['premiums']['pb_industry'] = (pb_fair - current_price) / current_price * 100
            
            # 3. PEG Ratio
            eps_growth = metrics['eps_cagr']
            if eps_growth > 0:
                peg_ratio = 1.0  # PEG hợp lý
                growth_pe = eps_growth * peg_ratio
                peg_fair = metrics['eps'] * growth_pe
                results['methods']['peg'] = peg_fair
                results['premiums']['peg'] = (peg_fair - current_price) / current_price * 100
            
            # 4. ROE-based valuation
            roe = metrics['roe']
            if roe is not None and roe > 0:
                if roe > 15:
                    roe_pe = 15 + (roe - 15) * 0.5
                else:
                    roe_pe = roe * 1.2
                roe_fair = metrics['eps'] * roe_pe
                results['methods']['roe_based'] = roe_fair
                results['premiums']['roe_based'] = (roe_fair - current_price) / current_price * 100
            
            # 5. Tính fair value tổng hợp
            valid_methods = []
            weights = {
                'pe_industry': 0.4,
                'pb_industry': 0.3,
                'peg': 0.2,
                'roe_based': 0.1
            }
            
            for method, weight in weights.items():
                if method in results['methods'] and results['methods'][method] > 0:
                    valid_methods.append(method)
            
            if valid_methods:
                weighted_sum = 0
                total_weight = 0
                
                for method in valid_methods:
                    value = results['methods'][method]
                    weight = weights[method]
                    weighted_sum += value * weight
                    total_weight += weight
                
                if total_weight > 0:
                    fair_value = weighted_sum / total_weight
                    premium = (fair_value - current_price) / current_price * 100
                    results['consensus'] = {
                        'fair_value': fair_value,
                        'premium': premium
                    }
            
            return results
            
        except Exception as e:
            st.error(f"❌ Lỗi trong quá trình tính toán định giá: {str(e)}")
            return None
    
    def get_recommendation(self, premium):
        """Đưa ra khuyến nghị dựa trên chênh lệch định giá"""
        if premium > 30:
            return "STRONG BUY 🚀", "Cổ phiếu đang định giá RẤT THẤP so với giá trị thực", "strong-buy"
        elif premium > 15:
            return "BUY 💰", "Cổ phiếu đang định giá THẤP so với giá trị thực", "buy"
        elif premium > -5:
            return "HOLD ⚖️", "Cổ phiếu đang định giá HỢP LÝ", "hold"
        elif premium > -20:
            return "REDUCE 📉", "Cổ phiếu đang định giá CAO so với giá trị thực", "reduce"
        else:
            return "SELL 🔴", "Cổ phiếu đang định giá RẤT CAO so với giá trị thực", "sell"
    
    def generate_pe_chart(self):
        """Tạo biểu đồ P/E lịch sử"""
        if self.ratios is None or self.ratios.empty:
            return None
        
        try:
            # Xác định tên cột P/E
            pe_col = None
            if isinstance(self.ratios.columns, pd.MultiIndex):
                possible_cols = [
                    ('Chỉ tiêu định giá', 'P/E'),
                    ('Valuation Ratios', 'P/E')
                ]
                for col in possible_cols:
                    if col in self.ratios.columns:
                        pe_col = col
                        break
            else:
                possible_cols = ['pe', 'priceToEarning', 'P/E']
                for col in possible_cols:
                    if col in self.ratios.columns:
                        pe_col = col
                        break
            
            if pe_col is None:
                return None
            
            # Lấy 5 năm gần nhất
            years = self.ratios.index.tolist()[:5]
            pe_values = []
            
            for year in years:
                try:
                    pe_value = self.ratios.loc[year, pe_col]
                    if pd.isna(pe_value) or pe_value <= 0:
                        pe_value = None
                    pe_values.append(pe_value)
                except:
                    pe_values.append(None)
            
            # Tạo DataFrame cho biểu đồ
            df = pd.DataFrame({
                'Năm': years,
                'P/E': pe_values
            }).dropna()
            
            if df.empty:
                return None
            
            fig = px.line(df, x='Năm', y='P/E', markers=True,
                          title=f'P/E lịch sử {self.symbol}',
                          line_shape='spline')
            fig.update_traces(line=dict(width=3, color='#0066cc'),
                              marker=dict(size=10, color='#ff6600'))
            fig.update_layout(
                plot_bgcolor='white',
                xaxis_title='Năm',
                yaxis_title='P/E Ratio',
                hovermode='x unified'
            )
            return fig
            
        except Exception as e:
            st.warning(f"⚠️ Không thể tạo biểu đồ P/E: {str(e)}")
            return None
    
    def generate_financial_health_chart(self, metrics):
        """Tạo biểu đồ sức khỏe tài chính"""
        if metrics is None:
            return None
        
        try:
            categories = ['ROE (%)', 'Margin (%)', 'Thanh khoản', 'Đòn bẩy']
            values = [
                min(metrics['roe'] / 25 * 100, 100) if metrics['roe'] is not None else 0,
                min(metrics['net_margin'] * 3, 100) if metrics['net_margin'] is not None else 0,
                min(metrics['current_ratio'] * 33, 100) if metrics['current_ratio'] is not None else 0,
                max(100 - metrics['debt_to_equity'] * 25, 0) if metrics['debt_to_equity'] is not None else 0
            ]
            
            colors = ['#00cc66' if v > 70 else '#ff9900' if v > 40 else '#ff3333' for v in values]
            
            fig = px.bar(
                x=categories,
                y=values,
                title="Sức khỏe tài chính tổng thể",
                labels={'x': 'Chỉ số', 'y': 'Điểm (0-100)'}
            )
            
            fig.update_traces(
                marker_color=colors,
                text=[f"{v:.0f}" for v in values],
                textposition='outside'
            )
            
            fig.update_layout(
                plot_bgcolor='white',
                yaxis_range=[0, 110],
                showlegend=False
            )
            
            return fig
        except Exception as e:
            st.warning(f"⚠️ Không thể tạo biểu đồ sức khỏe tài chính: {str(e)}")
            return None

# Tiêu đề
st.markdown("""
<h1 style='text-align: center; color: #0066cc;'>
    🎯 StockGuru Việt Nam <span style='font-size: 0.7em; color: #666;'>VNIndex Pro</span>
</h1>
<h3 style='text-align: center; color: #666; margin-bottom: 2rem;'>
    Phân tích & định giá cổ phiếu từ dữ liệu VCI/TCBS
</h3>
""", unsafe_allow_html=True)

# Form nhập mã cổ phiếu
with st.form("analysis_form"):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        symbol = st.text_input("🔍 Nhập mã cổ phiếu", value="FPT", placeholder="Ví dụ: FPT, VNM, VIC...").strip().upper()
        source = st.selectbox("Nguồn dữ liệu", ["TCBS", "VCI"], index=0)
        submitted = st.form_submit_button("🚀 Phân tích ngay", use_container_width=True)

if submitted:
    if not symbol:
        st.warning("⚠️ Vui lòng nhập mã cổ phiếu!")
    else:
        with st.spinner(f"Đang phân tích {symbol} từ dữ liệu {source}..."):
            try:
                analyzer = StockAnalyzer(symbol, source=source)
                metrics = analyzer.get_latest_financial_metrics()
                
                if metrics is None:
                    st.error(f"❌ Không tìm thấy dữ liệu cho **{symbol}**. Vui lòng thử mã khác.")
                    st.info("💡 Gợi ý: Dùng mã cổ phiếu HOSE phổ biến như FPT, VNM, VIC, VCB, HPG...")
                else:
                    # Tính giá trị hợp lý
                    valuation = analyzer.calculate_fair_value(metrics)
                    
                    if valuation is None:
                        st.error(f"❌ Không thể tính giá trị hợp lý cho {symbol}.")
                    else:
                        # Hiển thị kết quả
                        st.success(f"✅ Phân tích thành công {symbol}!")
                        
                        # Thông tin cơ bản
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Giá hiện tại", f"{valuation['current_price']:,.0f} VND")
                        col2.metric("EPS (VND)", f"{metrics['eps']:,.0f}")
                        col3.metric("P/E hiện tại", f"{metrics['pe_ratio']:.1f}x")
                        
                        # Khuyến nghị
                        if 'consensus' in valuation:
                            fair_value = valuation['consensus']['fair_value']
                            premium = valuation['consensus']['premium']
                            
                            col1, col2 = st.columns(2)
                            col1.metric("Giá trị hợp lý", f"{fair_value:,.0f} VND")
                            col2.metric("Chênh lệch", f"{premium:+.1f}%")
                            
                            recommendation, desc, css_class = analyzer.get_recommendation(premium)
                            st.markdown(f"### {recommendation}")
                            st.caption(desc)
                            
                            # Hiển thị thông tin chi tiết
                            st.subheader("📊 Thông tin chi tiết")
                            st.write(f"- **P/E ngành**: {analyzer.get_industry_pe()}x")
                            st.write(f"- **P/B ngành**: {analyzer.get_industry_pb()}x")
                            st.write(f"- **ROE**: {metrics['roe']:.1f}%")
                            st.write(f"- **Biên lợi nhuận ròng**: {metrics['net_margin']:.1f}%")
                            st.write(f"- **Tăng trưởng EPS 3 năm**: {metrics['eps_cagr']:.1f}%")
                        
                        # Biểu đồ P/E
                        st.subheader("📈 P/E Lịch sử")
                        pe_chart = analyzer.generate_pe_chart()
                        if pe_chart:
                            st.plotly_chart(pe_chart, use_container_width=True)
                        else:
                            st.info("Không có đủ dữ liệu để hiển thị biểu đồ P/E lịch sử")
                        
                        # Sức khỏe tài chính
                        st.subheader("💪 Sức khỏe tài chính")
                        health_chart = analyzer.generate_financial_health_chart(metrics)
                        if health_chart:
                            st.plotly_chart(health_chart, use_container_width=True)
                        else:
                            st.info("Không có đủ dữ liệu để phân tích sức khỏe tài chính")
            
            except Exception as e:
                st.error(f"❌ Lỗi khi phân tích {symbol}: {str(e)}")
                st.info("💡 Gợi ý: Dùng mã cổ phiếu HOSE chuẩn như FPT, VNM, VIC, VCB, HPG...")

# Footer
st.markdown("---")
st.caption("Dữ liệu từ VCI/TCBS qua thư viện vnstock. Miễn phí - không quảng cáo.")
