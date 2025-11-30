import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# Config trang
st.set_page_config(
    page_title="StockGuru Việt Nam - VNIndex Pro",
    page_icon="🎯",
    layout="wide"
)

# Tiêu đề
st.markdown("""
<h1 style='text-align: center; color: #0066cc;'>
    🎯 StockGuru Việt Nam <span style='font-size: 0.7em; color: #666;'>VNIndex Pro Edition</span>
</h1>
<h3 style='text-align: center; color: #666; margin-bottom: 2rem;'>
    Phân tích & định giá toàn bộ cổ phiếu VN-Index từ dữ liệu VCI/TCBS
</h3>
""", unsafe_allow_html=True)

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
    .industry-table {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    @media (max-width: 768px) {
        .stColumn {
            width: 100% !important;
        }
        .stTabs [data-baseweb="tab"] {
            height: auto !important;
            white-space: normal !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Danh sách các cổ phiếu trong VN30 (đại diện cho VN-Index)
VN30_STOCKS = [
    'VNM', 'VIC', 'FPT', 'VHM', 'HPG', 'TCB', 'MSN', 'VRE', 'MWG', 'BID', 
    'CTG', 'VCB', 'ACB', 'MBB', 'TPB', 'GAS', 'VJC', 'BVH', 'SSI', 'VIB',
    'POW', 'PLX', 'NVL', 'KDH', 'HDB', 'PNJ', 'SAB', 'REE', 'VCB', 'VHM'
]

# Danh sách ngành và P/E tham chiếu
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

# Phân loại cổ phiếu theo ngành
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

class StockAnalyzer:
    def __init__(self, symbol, source='TCBS'):
        self.symbol = symbol.upper()
        self.source = source
        self.ratios = None
        self.income = None
        self.balance = None
        self.cashflow = None
        self.stock_obj = None
        self.load_financial_data()
        
    def load_financial_data(self):
        """Tải toàn bộ dữ liệu tài chính cần thiết từ nguồn đã chọn"""
        try:
            from vnstock import Vnstock
            if self.source == 'TCBS':
                self.stock_obj = Vnstock().stock(symbol=self.symbol, source='TCBS')
                self.finance = self.stock_obj.finance
            else:  # VCI
                # Sử dụng Finance trực tiếp từ vnstock cho VCI
                from vnstock import Finance
                self.finance = Finance(symbol=self.symbol, source='VCI')
            
            # Lấy chỉ số tài chính
            self.ratios = self.finance.ratio(period='year')
            
            # Lấy các báo cáo tài chính
            try:
                self.income = self.finance.income_statement(period='year')
            except:
                self.income = None
                
            try:
                self.balance = self.finance.balance_sheet(period='year')
            except:
                self.balance = None
                
            try:
                self.cashflow = self.finance.cash_flow(period='year')
            except:
                self.cashflow = None
                
        except Exception as e:
            st.error(f"❌ Lỗi khi kết nối dữ liệu {self.source}: {str(e)}")
    
    def get_latest_financial_metrics(self):
        """Lấy các chỉ số tài chính quan trọng nhất"""
        if self.ratios is None or self.ratios.empty:
            return None
        
        try:
            # Xử lý khác nhau tùy theo nguồn dữ liệu
            if self.source == 'TCBS':
                return self._get_metrics_tcbs()
            else:
                return self._get_metrics_vci()
        except Exception as e:
            st.warning(f"⚠️ Lỗi khi trích xuất chỉ số cho {self.symbol}: {str(e)}")
            return None
    
    def _get_metrics_tcbs(self):
        """Lấy chỉ số từ TCBS (đơn giản hơn)"""
        latest_year = self.ratios.index[0]
        latest = self.ratios.loc[latest_year]
        
        pe_ratio = latest.get('pe', latest.get('priceToEarning', 0))
        pb_ratio = latest.get('pb', latest.get('priceToBook', 0))
        eps = latest.get('eps', latest.get('earningsPerShare', 0)) * 1000  # chuyển sang VND
        bvps = latest.get('bvps', latest.get('bookValuePerShare', 0)) * 1000  # chuyển sang VND
        roe = latest.get('roe', latest.get('returnOnEquity', 0)) * 100
        net_margin = latest.get('netMargin', latest.get('postTaxMargin', 0)) * 100
        current_ratio = latest.get('currentRatio', 1.0)
        debt_to_equity = latest.get('debtToEquity', 0.5)
        eps_growth = latest.get('epsGrowth', 0) * 100
        
        # Lấy thông tin thị trường
        market_cap = None
        shares_outstanding = None
        
        try:
            if hasattr(self.stock_obj, 'overview'):
                overview = self.stock_obj.overview()
                market_cap = overview.get('marketCap')  # tỷ đồng
                shares_outstanding = overview.get('shareOutstanding', 0) / 1e6  # triệu CP
        except:
            pass
        
        return {
            'year': int(latest_year),
            'pe_ratio': float(pe_ratio),
            'pb_ratio': float(pb_ratio),
            'eps': float(eps),
            'bvps': float(bvps),
            'roe': float(roe),
            'net_margin': float(net_margin),
            'current_ratio': float(current_ratio),
            'debt_to_equity': float(debt_to_equity),
            'eps_cagr': float(eps_growth),
            'market_cap': float(market_cap) if market_cap else None,
            'shares_outstanding': float(shares_outstanding) if shares_outstanding else None
        }
    
    def _get_metrics_vci(self):
        """Lấy chỉ số từ VCI (MultiIndex)"""
        latest_year = self.ratios.index[0]
        latest = self.ratios.loc[latest_year]
        
        def get_vci_value(keys):
            """Truy xuất giá trị từ MultiIndex của VCI"""
            for key in keys:
                if isinstance(key, tuple) and key in latest.index:
                    return float(latest[key])
                # Thử tìm theo tên đơn giản
                matches = [col for col in latest.index if isinstance(col, tuple) and key.lower() in col[1].lower()]
                if matches:
                    return float(latest[matches[0]])
            return 0
        
        # Các tên cột có thể có cho từng chỉ số
        pe_keys = [('Chỉ tiêu định giá', 'P/E'), ('Valuation Ratios', 'P/E')]
        pb_keys = [('Chỉ tiêu định giá', 'P/B'), ('Valuation Ratios', 'P/B')]
        eps_keys = [('Chỉ tiêu định giá', 'EPS (VND)'), ('Valuation Ratios', 'EPS (VND)')]
        bvps_keys = [('Chỉ tiêu định giá', 'BVPS (VND)'), ('Valuation Ratios', 'BVPS (VND)')]
        roe_keys = [('Chỉ tiêu khả năng sinh lợi', 'ROE (%)'), ('Profitability Ratios', 'ROE (%)')]
        net_margin_keys = [('Chỉ tiêu khả năng sinh lợi', 'Biên lợi nhuận ròng (%)'), ('Profitability Ratios', 'Net Profit Margin (%)')]
        current_ratio_keys = [('Chỉ tiêu thanh khoản', 'Chỉ số thanh toán hiện thời'), ('Liquidity Ratios', 'Current Ratio')]
        debt_to_equity_keys = [('Chỉ tiêu cơ cấu nguồn vốn', 'Nợ/VCSH'), ('Financial Structure Ratios', 'Debt to Equity')]
        eps_growth_keys = [('Chỉ tiêu định giá', 'Tăng trưởng EPS (%)'), ('Growth Ratios', 'EPS Growth (%)')]
        
        pe_ratio = get_vci_value(pe_keys)
        pb_ratio = get_vci_value(pb_keys)
        eps = get_vci_value(eps_keys)
        bvps = get_vci_value(bvps_keys)
        roe = get_vci_value(roe_keys)
        net_margin = get_vci_value(net_margin_keys)
        current_ratio = get_vci_value(current_ratio_keys)
        debt_to_equity = get_vci_value(debt_to_equity_keys)
        eps_growth = get_vci_value(eps_growth_keys)
        
        # Ước lượng vốn hóa và số CP lưu hành
        market_cap = None
        shares_outstanding = None
        
        # Thử lấy số CP lưu hành từ VCI
        shares_keys = [('Chỉ tiêu định giá', 'Số CP lưu hành (Triệu CP)'), ('Valuation Ratios', 'Shares Outstanding (Million)')]
        shares_value = get_vci_value(shares_keys)
        if shares_value > 0:
            shares_outstanding = shares_value
        
        return {
            'year': int(latest_year),
            'pe_ratio': float(pe_ratio),
            'pb_ratio': float(pb_ratio),
            'eps': float(eps),
            'bvps': float(bvps),
            'roe': float(roe),
            'net_margin': float(net_margin),
            'current_ratio': float(current_ratio),
            'debt_to_equity': float(debt_to_equity),
            'eps_cagr': float(eps_growth),
            'market_cap': market_cap,
            'shares_outstanding': shares_outstanding
        }
    
    def get_industry_pe(self):
        """Lấy P/E trung bình ngành phù hợp với cổ phiếu"""
        industry = STOCK_INDUSTRY_MAP.get(self.symbol, 'Khác')
        return INDUSTRY_PE.get(industry, 15.0)
    
    def get_industry_pb(self):
        """Lấy P/B trung bình ngành phù hợp với cổ phiếu"""
        industry = STOCK_INDUSTRY_MAP.get(self.symbol, 'Khác')
        return INDUSTRY_PB.get(industry, 2.0)
    
    def calculate_fair_value(self, metrics, risk_free_rate=0.03):
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
            if 1 <= eps_growth <= 100:  # Chỉ tính nếu tăng trưởng hợp lý
                peg_ratio = 1.0
                growth_pe = eps_growth * peg_ratio
                peg_fair = metrics['eps'] * growth_pe
                results['methods']['peg'] = peg_fair
                results['premiums']['peg'] = (peg_fair - current_price) / current_price * 100
            
            # 4. ROE-based valuation
            roe = metrics['roe']
            if 5 <= roe <= 50:  # Chỉ tính nếu ROE hợp lý
                if roe > 15:
                    roe_pe = 15 + (roe - 15) * 0.5
                else:
                    roe_pe = roe * 1.2
                roe_fair = metrics['eps'] * roe_pe
                results['methods']['roe_based'] = roe_fair
                results['premiums']['roe_based'] = (roe_fair - current_price) / current_price * 100
            
            # 5. Tính fair value tổng hợp
            valid_methods = []
            weights = {}
            
            # Gán trọng số dựa trên độ tin cậy của từng phương pháp
            if 'pe_industry' in results['methods'] and pe_fair > 0:
                valid_methods.append('pe_industry')
                weights['pe_industry'] = 0.4
            
            if 'pb_industry' in results['methods'] and pb_fair > 0:
                valid_methods.append('pb_industry')
                weights['pb_industry'] = 0.3
            
            if 'peg' in results['methods'] and eps_growth > 0:
                valid_methods.append('peg')
                weights['peg'] = 0.2
            
            if 'roe_based' in results['methods'] and roe > 0:
                valid_methods.append('roe_based')
                weights['roe_based'] = 0.1
            
            if valid_methods:
                weighted_sum = 0
                total_weight = 0
                
                for method in valid_methods:
                    value = results['methods'][method]
                    weight = weights.get(method, 0)
                    if weight > 0:
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
            st.warning(f"Lỗi tính toán định giá cho {self.symbol}: {str(e)}")
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
            years = self.ratios.index.tolist()[:5]
            pe_values = []
            
            # Xác định tên cột P/E phù hợp
            pe_col = None
            if self.source == 'TCBS':
                possible_cols = ['pe', 'priceToEarning', 'P/E']
                for col in possible_cols:
                    if col in self.ratios.columns:
                        pe_col = col
                        break
            else:  # VCI
                possible_cols = [('Chỉ tiêu định giá', 'P/E'), ('Valuation Ratios', 'P/E')]
                for col in possible_cols:
                    if col in self.ratios.columns:
                        pe_col = col
                        break
            
            if pe_col is None:
                return None
            
            for year in years:
                try:
                    if self.source == 'TCBS':
                        pe_value = self.ratios.loc[year, pe_col]
                    else:
                        pe_value = self.ratios.loc[year][pe_col]
                    
                    if pd.isna(pe_value) or pe_value <= 0:
                        pe_value = 0
                    pe_values.append(pe_value)
                except:
                    pe_values.append(0)
            
            # Tạo DataFrame cho biểu đồ
            df = pd.DataFrame({
                'Năm': years,
                'P/E': pe_values
            })
            
            if sum(pe_values) > 0:
                fig = px.bar(df, x='Năm', y='P/E', 
                             title=f'P/E lịch sử {self.symbol}',
                             color='P/E',
                             color_continuous_scale='Blues')
                fig.update_layout(
                    plot_bgcolor='white',
                    xaxis_title='Năm',
                    yaxis_title='P/E Ratio',
                    hovermode='x unified'
                )
                return fig
            return None
            
        except Exception as e:
            st.warning(f"Không thể tạo biểu đồ P/E cho {self.symbol}: {str(e)}")
            return None
    
    def generate_radar_chart(self, metrics):
        """Tạo biểu đồ radar so sánh sức khỏe tài chính"""
        if metrics is None:
            return None
        
        try:
            categories = ['ROE', 'Lợi nhuận', 'Thanh khoản', 'Đòn bẩy']
            values = [
                min(metrics['roe'] / 20, 1.0),  # Chuẩn hóa về 0-1
                min(metrics['net_margin'] / 20, 1.0),  # Chuẩn hóa về 0-1
                min(metrics['current_ratio'] / 2, 1.0),  # Chuẩn hóa về 0-1
                max(1.0 - metrics['debt_to_equity'] / 2, 0)  # Chuẩn hóa về 0-1
            ]
            
            fig = go.Figure(data=go.Scatterpolar(
                r=values + [values[0]],  # Đóng vòng
                theta=categories + [categories[0]],
                fill='toself',
                name=self.symbol,
                line=dict(color='#0066cc')
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1]
                    )),
                showlegend=False,
                title=f"Sức khỏe tài chính {self.symbol}",
                plot_bgcolor='white'
            )
            
            return fig
        except Exception as e:
            st.warning(f"Không thể tạo biểu đồ radar cho {self.symbol}: {str(e)}")
            return None

def get_vnindex_stocks():
    """Lấy danh sách cổ phiếu VN30 (đại diện cho VN-Index)"""
    return VN30_STOCKS

def load_cached_analysis(source='TCBS'):
    """Tải phân tích đã cache để tăng tốc độ"""
    if f'vnindex_analysis_{source}' not in st.session_state:
        st.session_state[f'vnindex_analysis_{source}'] = {}
    return st.session_state[f'vnindex_analysis_{source}']

def save_cached_analysis(data, source='TCBS'):
    """Lưu cache phân tích"""
    st.session_state[f'vnindex_analysis_{source}'] = data

# Sidebar cho lựa chọn
with st.sidebar:
    st.header("⚙️ Cài đặt phân tích")
    
    # Chọn nguồn dữ liệu
    data_source = st.selectbox(
        "Chọn nguồn dữ liệu",
        ["TCBS", "VCI"],
        index=0,
        help="TCBS: tốc độ nhanh hơn, VCI: dữ liệu chi tiết hơn"
    )
    
    # Chọn cổ phiếu để phân tích
    st.subheader("📈 Chọn cổ phiếu")
    analysis_mode = st.radio(
        "Chế độ phân tích",
        ["Cổ phiếu đơn lẻ", "Danh mục VN30"],
        index=1
    )
    
    if analysis_mode == "Cổ phiếu đơn lẻ":
        symbol_input = st.text_input("Nhập mã cổ phiếu", value="FPT", placeholder="Ví dụ: FPT, VNM, VIC...")
    else:
        # Chọn nhóm ngành
        industry_filter = st.multiselect(
            "Lọc theo ngành",
            options=list(set(STOCK_INDUSTRY_MAP.values())),
            default=list(set(STOCK_INDUSTRY_MAP.values()))[:3]
        )
        
        # Chọn số lượng cổ phiếu muốn phân tích
        num_stocks = st.slider("Số lượng cổ phiếu", min_value=5, max_value=30, value=15)
    
    # Nút phân tích
    analyze_btn = st.button("🚀 Bắt đầu phân tích", use_container_width=True)

# Tab chính
tab1, tab2, tab3 = st.tabs(["📊 Tổng quan", "🔍 Chi tiết ngành", "📈 Biểu đồ"])

with tab1:
    if analyze_btn:
        with st.spinner("Đang phân tích dữ liệu..."):
            if analysis_mode == "Cổ phiếu đơn lẻ" and symbol_input:
                # Phân tích cổ phiếu đơn lẻ
                symbol = symbol_input.strip().upper()
                if len(symbol) < 2 or len(symbol) > 4:
                    st.error("❌ Mã cổ phiếu không hợp lệ. Vui lòng nhập mã HOSE chuẩn (2-4 ký tự).")
                else:
                    analyzer = StockAnalyzer(symbol, source=data_source)
                    metrics = analyzer.get_latest_financial_metrics()
                    
                    if metrics is None or metrics.get('eps', 0) <= 0:
                        st.error(f"❌ Không tìm thấy dữ liệu hợp lệ cho mã **{symbol}**. Vui lòng thử mã khác.")
                        st.info("💡 Gợi ý: Dùng mã cổ phiếu HOSE phổ biến như FPT, VNM, VIC, VCB, HPG...")
                    else:
                        valuation = analyzer.calculate_fair_value(metrics)
                        
                        if valuation is None:
                            st.error(f"❌ Không thể tính giá trị hợp lý cho {symbol}.")
                        else:
                            # Hiển thị kết quả phân tích
                            st.subheader(f"📊 KẾT QUẢ PHÂN TÍCH {symbol} - NĂM {metrics['year']}")
                            st.markdown("---")
                            
                            # Thông tin cơ bản
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Giá hiện tại", f"{valuation['current_price']:,.0f} VND")
                            with col2:
                                st.metric("EPS", f"{metrics['eps']:,.0f} VND")
                            with col3:
                                st.metric("BVPS", f"{metrics['bvps']:,.0f} VND")
                            with col4:
                                if metrics.get('market_cap'):
                                    st.metric("Vốn hóa", f"{metrics['market_cap']:,.0f} tỷ VND")
                                else:
                                    st.metric("P/E hiện tại", f"{metrics['pe_ratio']:.1f}x")
                            
                            st.markdown("---")
                            
                            # Kết quả định giá
                            if 'consensus' in valuation:
                                fair_value = valuation['consensus']['fair_value']
                                premium = valuation['consensus']['premium']
                                
                                col1, col2 = st.columns([2, 1])
                                with col1:
                                    st.metric("Giá trị hợp lý", f"{fair_value:,.0f} VND", 
                                             delta=f"{premium:+.1f}%", delta_color="normal")
                                with col2:
                                    recommendation, desc, css_class = analyzer.get_recommendation(premium)
                                    st.markdown(f"""
                                    <div class="recommendation-box {css_class}">
                                        <h3 style='margin: 0;'>{recommendation}</h3>
                                        <p style='margin: 5px 0 0 0; font-size: 0.9em; color: #666;'>{desc}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            st.markdown("---")
                            
                            # Chi tiết các phương pháp định giá
                            st.subheader("📈 CHI TIẾT PHƯƠNG PHÁP ĐỊNH GIÁ")
                            
                            methods_data = []
                            if 'pe_industry' in valuation['methods']:
                                methods_data.append({
                                    'Phương pháp': 'P/E ngành',
                                    'P/E tham chiếu': f"{analyzer.get_industry_pe():.1f}x",
                                    'Giá trị hợp lý (VND)': valuation['methods']['pe_industry'],
                                    'Chênh lệch (%)': valuation['premiums']['pe_industry']
                                })
                            
                            if 'pb_industry' in valuation['methods']:
                                methods_data.append({
                                    'Phương pháp': 'P/B ngành',
                                    'P/B tham chiếu': f"{analyzer.get_industry_pb():.1f}x",
                                    'Giá trị hợp lý (VND)': valuation['methods']['pb_industry'],
                                    'Chênh lệch (%)': valuation['premiums']['pb_industry']
                                })
                            
                            if 'peg' in valuation['methods']:
                                methods_data.append({
                                    'Phương pháp': 'PEG Ratio',
                                    'Tăng trưởng EPS': f"{metrics['eps_cagr']:.1f}%",
                                    'Giá trị hợp lý (VND)': valuation['methods']['peg'],
                                    'Chênh lệch (%)': valuation['premiums']['peg']
                                })
                            
                            if 'roe_based' in valuation['methods']:
                                methods_data.append({
                                    'Phương pháp': 'ROE-based',
                                    'ROE': f"{metrics['roe']:.1f}%",
                                    'Giá trị hợp lý (VND)': valuation['methods']['roe_based'],
                                    'Chênh lệch (%)': valuation['premiums']['roe_based']
                                })
                            
                            if methods_
                                methods_df = pd.DataFrame(methods_data)
                                
                                # Định dạng bảng đẹp
                                styled_df = methods_df.style.format({
                                    'Giá trị hợp lý (VND)': '{:,.0f}',
                                    'Chênh lệch (%)': '{:+.1f}%'
                                }).applymap(
                                    lambda x: 'color: #00cc66' if isinstance(x, (int, float)) and x > 15 else (
                                        'color: #ff9900' if isinstance(x, (int, float)) and x > -5 else 'color: #ff3333'),
                                    subset=['Chênh lệch (%)']
                                ).set_properties(**{
                                    'text-align': 'center',
                                    'padding': '10px'
                                })
                                
                                st.dataframe(styled_df, use_container_width=True)
                            
                            st.markdown("---")
                            
                            # Biểu đồ và phân tích chi tiết
                            st.subheader("🔍 PHÂN TÍCH CHI TIẾT")
                            
                            # Biểu đồ P/E lịch sử
                            pe_chart = analyzer.generate_pe_chart()
                            if pe_chart:
                                st.plotly_chart(pe_chart, use_container_width=True)
                            
                            # Radar chart sức khỏe tài chính
                            radar_chart = analyzer.generate_radar_chart(metrics)
                            if radar_chart:
                                st.plotly_chart(radar_chart, use_container_width=True)
                            
                            # Các chỉ số tài chính chi tiết
                            st.markdown("#### 📋 Chỉ số tài chính quan trọng")
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("ROE (%)", f"{metrics['roe']:.1f}")
                            with col2:
                                st.metric("Biên lợi nhuận ròng (%)", f"{metrics['net_margin']:.1f}")
                            with col3:
                                st.metric("Hệ số thanh toán hiện tại", f"{metrics['current_ratio']:.2f}")
                            with col4:
                                st.metric("Nợ/Vốn CSH", f"{metrics['debt_to_equity']:.2f}")
                            
                            st.markdown("---")
                            
                            # Kết luận chuyên gia
                            st.subheader("🎯 KẾT LUẬN CHUYÊN GIA")
                            
                            if 'consensus' in valuation:
                                conclusion = f"""
                                <div class="recommendation-box {css_class}">
                                    <p style='font-size: 1.1em; line-height: 1.6; margin-bottom: 10px;'>
                                        <strong>{symbol}</strong> hiện đang được định giá ở mức <strong>{premium:+.1f}%</strong> so với giá trị hợp lý được tính toán từ nhiều phương pháp định giá khác nhau.
                                    </p>
                                    
                                    <p style='font-size: 1.1em; line-height: 1.6; margin-bottom: 10px;'>
                                        Dựa trên phân tích các chỉ số tài chính quan trọng, đặc biệt là <strong>ROE {metrics['roe']:.1f}%</strong> và 
                                        <strong>biên lợi nhuận ròng {metrics['net_margin']:.1f}%</strong>, 
                                        công ty thể hiện <strong>{'tiềm năng tăng trưởng tốt' if metrics['roe'] > 12 and metrics['eps_cagr'] > 10 else 'năng lực kinh doanh ổn định'}</strong>.
                                    </p>
                                    
                                    <p style='font-size: 1.1em; line-height: 1.6; margin-bottom: 0;'>
                                        <strong>Khuyến nghị đầu tư:</strong> {recommendation} - {desc}
                                    </p>
                                </div>
                                """
                                st.markdown(conclusion, unsafe_allow_html=True)
            
            else:  # Phân tích danh mục VN30
                # Lấy danh sách cổ phiếu theo ngành đã chọn
                if industry_filter:
                    stocks_to_analyze = [stock for stock, industry in STOCK_INDUSTRY_MAP.items() 
                                       if industry in industry_filter and stock in VN30_STOCKS]
                else:
                    stocks_to_analyze = VN30_STOCKS
                
                # Giới hạn số lượng
                stocks_to_analyze = stocks_to_analyze[:num_stocks]
                
                if not stocks_to_analyze:
                    st.error("❌ Không có cổ phiếu nào phù hợp với tiêu chí đã chọn.")
                else:
                    # Tạo cache để tránh tải lại nhiều lần
                    cached_analysis = load_cached_analysis(data_source)
                    stocks_analyzed = []
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i, symbol in enumerate(stocks_to_analyze):
                        status_text.text(f"Đang phân tích {symbol} ({i+1}/{len(stocks_to_analyze)})...")
                        progress_bar.progress((i + 1) / len(stocks_to_analyze))
                        
                        # Sử dụng cache nếu có
                        if symbol in cached_analysis and cached_analysis[symbol].get('source') == data_source:
                            stocks_analyzed.append(cached_analysis[symbol])
                        else:
                            try:
                                analyzer = StockAnalyzer(symbol, source=data_source)
                                metrics = analyzer.get_latest_financial_metrics()
                                
                                if metrics and metrics.get('eps', 0) > 0:
                                    valuation = analyzer.calculate_fair_value(metrics)
                                    if valuation and 'consensus' in valuation:
                                        industry = STOCK_INDUSTRY_MAP.get(symbol, 'Khác')
                                        fair_value = valuation['consensus']['fair_value']
                                        premium = valuation['consensus']['premium']
                                        recommendation, _, css_class = analyzer.get_recommendation(premium)
                                        
                                        stock_data = {
                                            'symbol': symbol,
                                            'industry': industry,
                                            'current_price': valuation['current_price'],
                                            'fair_value': fair_value,
                                            'premium': premium,
                                            'recommendation': recommendation,
                                            'css_class': css_class,
                                            'eps': metrics['eps'],
                                            'roe': metrics['roe'],
                                            'pe_ratio': metrics['pe_ratio'],
                                            'pb_ratio': metrics['pb_ratio'],
                                            'year': metrics['year'],
                                            'source': data_source
                                        }
                                        stocks_analyzed.append(stock_data)
                                        cached_analysis[symbol] = stock_data
                            except Exception as e:
                                st.warning(f"Không thể phân tích {symbol}: {str(e)}")
                        
                        # Thêm delay để tránh bị chặn
                        time.sleep(0.5)
                    
                    # Lưu cache
                    save_cached_analysis(cached_analysis, data_source)
                    status_text.empty()
                    
                    if not stocks_analyzed:
                        st.error("❌ Không phân tích được cổ phiếu nào. Vui lòng thử lại sau.")
                    else:
                        st.subheader(f"📊 BẢNG PHÂN TÍCH {len(stocks_analyzed)} CỔ PHIẾU VN30")
                        st.markdown(f"*Nguồn dữ liệu: {data_source} | Cập nhật ngày: {datetime.now().strftime('%d/%m/%Y')}*")
                        
                        # Hiển thị kết quả theo ngành
                        industries = sorted(set([stock['industry'] for stock in stocks_analyzed]))
                        
                        for industry in industries:
                            industry_stocks = [stock for stock in stocks_analyzed if stock['industry'] == industry]
                            if industry_stocks:
                                st.markdown(f"### 📌 Ngành {industry}")
                                st.markdown(f"*P/E tham chiếu ngành: {INDUSTRY_PE.get(industry, 15.0):.1f}x | P/B tham chiếu: {INDUSTRY_PB.get(industry, 2.0):.1f}x*")
                                
                                # Tạo DataFrame cho ngành
                                industry_df = pd.DataFrame(industry_stocks)
                                industry_df = industry_df.sort_values('premium', ascending=False)
                                
                                # Định dạng bảng
                                def color_recommendation(val):
                                    colors = {
                                        'STRONG BUY': '#e6ffe6',
                                        'BUY': '#e6f7ff',
                                        'HOLD': '#fff8e6',
                                        'REDUCE': '#ffe6e6',
                                        'SELL': '#ffcccc'
                                    }
                                    return f'background-color: {colors.get(val, "white")}'
                                
                                styled_df = industry_df[['symbol', 'current_price', 'fair_value', 'premium', 'recommendation']].style\
                                    .format({
                                        'current_price': '{:,.0f}',
                                        'fair_value': '{:,.0f}',
                                        'premium': '{:+.1f}%'
                                    })\
                                    .applymap(lambda x: 'color: #00cc66' if isinstance(x, float) and x > 15 else (
                                             'color: #ff9900' if isinstance(x, float) and x > -5 else 'color: #ff3333'), 
                                             subset=['premium'])\
                                    .applymap(color_recommendation, subset=['recommendation'])
                                
                                st.dataframe(styled_df, use_container_width=True)
                        
                        st.markdown("---")
                        
                        # Tạo biểu đồ phân tích
                        st.subheader("📈 BIỂU ĐỒ PHÂN TÍCH")
                        
                        # Biểu đồ phân tán P/E vs Premium
                        fig = px.scatter(
                            stocks_analyzed,
                            x='pe_ratio',
                            y='premium',
                            color='industry',
                            size='roe',
                            hover_name='symbol',
                            title='P/E Ratio vs Chênh lệch định giá',
                            labels={
                                'pe_ratio': 'P/E Ratio',
                                'premium': 'Chênh lệch định giá (%)',
                                'roe': 'ROE (%)'
                            },
                            width=800,
                            height=500
                        )
                        
                        # Thêm đường tham chiếu
                        fig.add_hline(y=0, line_dash="dash", line_color="gray")
                        fig.add_vline(x=15, line_dash="dash", line_color="gray")
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Tải về kết quả
                        st.markdown("---")
                        st.subheader("💾 TẢI VỀ KẾT QUẢ")
                        
                        results_df = pd.DataFrame(stocks_analyzed)
                        csv = results_df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Tải về CSV",
                            data=csv,
                            file_name=f"vnindex_analysis_{data_source}_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
    else:
        # Hiển thị hướng dẫn khi chưa phân tích
        st.markdown("""
        <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 20px;'>
            <h3 style='color: #0066cc; margin-top: 0;'>📖 Hướng dẫn sử dụng</h3>
            <p><strong>StockGuru Việt Nam - Phiên bản VNIndex Pro</strong> cho phép bạn:</p>
            <ul>
                <li>🔹 Phân tích từng cổ phiếu đơn lẻ trong VN-Index</li>
                <li>🔹 So sánh hàng loạt cổ phiếu theo ngành</li>
                <li>🔹 Định giá cổ phiếu bằng nhiều phương pháp (P/E, P/B, PEG, ROE-based)</li>
                <li>🔹 Đánh giá sức khỏe tài chính qua các chỉ số ROE, biên lợi nhuận, thanh khoản</li>
                <li>🔹 So sánh với P/E, P/B trung bình ngành</li>
            </ul>
            <p style='background-color: #e3f2fd; padding: 10px; border-radius: 5px; margin-top: 15px;'>
                💡 <strong>Mẹo sử dụng:</strong> Chọn "Danh mục VN30" để xem báo cáo tổng quan toàn thị trường, hoặc chọn "Cổ phiếu đơn lẻ" để phân tích chi tiết một mã cụ thể.
            </p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("""
📊 Dữ liệu từ VCI/TCBS qua thư viện vnstock | 📈 Phương pháp định giá: P/E, P/B, PEG, ROE-based | 
💡 Kết quả chỉ mang tính tham khảo - Không phải lời khuyên đầu tư
""")
