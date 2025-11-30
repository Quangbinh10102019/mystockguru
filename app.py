import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from vnstock import Vnstock

# Config trang
st.set_page_config(
    page_title="StockGuru Việt Nam - Phiên bản Pro",
    page_icon="🎯",
    layout="wide"
)

# Tiêu đề
st.markdown("""
<h1 style='text-align: center; color: #0066cc;'>
    🎯 StockGuru Việt Nam <span style='font-size: 0.7em; color: #666;'>Phiên bản Pro</span>
</h1>
<h3 style='text-align: center; color: #666; margin-bottom: 2rem;'>
    Phân tích định giá chuyên nghiệp dựa trên báo cáo tài chính
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
</style>
""", unsafe_allow_html=True)

# Class phân tích cổ phiếu chuyên nghiệp - PHIÊN BẢN TCBS
class StockAnalyzer:
    def __init__(self, symbol):
        self.symbol = symbol.upper()
        try:
            # KHỞI TẠO ĐÚNG VỚI TCBS
            self.stock_obj = Vnstock().stock(symbol=self.symbol, source='TCBS')
            self.finance = self.stock_obj.finance
            self.load_financial_data()
        except Exception as e:
            st.error(f"❌ Lỗi khi kết nối TCBS: {str(e)}")
            self.ratios = None
    
    def load_financial_data(self):
        """Tải toàn bộ dữ liệu tài chính cần thiết từ TCBS"""
        try:
            # Lấy chỉ số tài chính - DÙNG NGUỒN TCBS
            self.ratios = self.finance.ratio(period='year')
            
            # Lấy báo cáo KQKD
            self.income = self.finance.income_statement(period='year')
            
            # Lấy báo cáo CĐKT
            self.balance = self.finance.balance_sheet(period='year')
            
        except Exception as e:
            st.error(f"❌ Lỗi khi tải dữ liệu: {str(e)}")
            self.ratios = None
    
    def get_latest_financial_metrics(self):
        """Lấy các chỉ số tài chính quan trọng nhất - PHIÊN BẢN TCBS"""
        if self.ratios is None or self.ratios.empty:
            return None
        
        try:
            # Lấy dòng dữ liệu mới nhất
            latest = self.ratios.iloc[0]
            year = self.ratios.index[0]
            
            # Trích xuất các chỉ số quan trọng từ TCBS
            # TCBS dùng tên cột tiếng Anh đơn giản
            
            # Chỉ số định giá
            pe_ratio = latest.get('priceToEarning', latest.get('pe', 0))
            pb_ratio = latest.get('priceToBook', latest.get('pb', 0))
            ps_ratio = latest.get('priceToSales', latest.get('ps', 0))
            
            # EPS và BVPS - TCBS trả về đơn vị nghìn đồng
            eps = latest.get('earningsPerShare', latest.get('eps', 0)) * 1000  # chuyển sang VND
            bvps = latest.get('bookValuePerShare', latest.get('bvps', 0)) * 1000  # chuyển sang VND
            
            # Chỉ số sinh lời
            roe = latest.get('returnOnEquity', latest.get('roe', 0)) * 100  # chuyển sang %
            roa = latest.get('returnOnAssets', latest.get('roa', 0)) * 100  # chuyển sang %
            
            # Biên lợi nhuận
            gross_margin = latest.get('grossProfitMargin', latest.get('biMargin', 0)) * 100
            net_margin = latest.get('netProfitMargin', latest.get('postTaxMargin', 0)) * 100
            
            # Chỉ số thanh khoản & đòn bẩy
            current_ratio = latest.get('currentRatio', 1.0)
            debt_to_equity = latest.get('debtToEquity', 0.5)
            
            # Tăng trưởng EPS 3 năm
            eps_cagr = latest.get('earningsPerShareGrowth', latest.get('epsGrowth', 0)) * 100
            
            # Vốn hóa (tỷ đồng) - TCBS có thể không cung cấp trực tiếp
            market_cap = None
            shares_outstanding = None
            if hasattr(self.stock_obj, 'overview'):
                try:
                    overview = self.stock_obj.overview()
                    if 'marketCap' in overview:
                        market_cap = overview['marketCap']  # tỷ đồng
                    if 'sharesOutstanding' in overview:
                        shares_outstanding = overview['sharesOutstanding'] / 1e6  # triệu cổ phiếu
                except:
                    pass
            
            if market_cap is None and shares_outstanding is not None and eps > 0:
                market_cap = (pe_ratio * eps * shares_outstanding * 1e6) / 1e9  # tỷ đồng
            
            return {
                'year': year,
                'pe_ratio': float(pe_ratio),
                'pb_ratio': float(pb_ratio),
                'ps_ratio': float(ps_ratio),
                'eps': float(eps),
                'bvps': float(bvps),
                'market_cap': float(market_cap) if market_cap else None,
                'shares_outstanding': float(shares_outstanding) if shares_outstanding else None,
                'roe': float(roe),
                'roa': float(roa),
                'gross_margin': float(gross_margin),
                'net_margin': float(net_margin),
                'current_ratio': float(current_ratio),
                'debt_to_equity': float(debt_to_equity),
                'eps_cagr': float(eps_cagr)
            }
        except Exception as e:
            st.error(f"❌ Lỗi khi trích xuất chỉ số: {str(e)}")
            return None
    
    def calculate_fair_value(self, metrics):
        """Tính giá trị hợp lý bằng nhiều phương pháp"""
        if metrics is None:
            return None
        
        current_price = metrics['pe_ratio'] * metrics['eps']
        results = {
            'current_price': current_price,
            'methods': {},
            'premiums': {}
        }
        
        # 1. P/E so sánh ngành - ngành chứng khoán thường có P/E từ 12-18
        industry_pe_avg = self.get_industry_pe()
        industry_pe_fair = metrics['eps'] * industry_pe_avg
        results['methods']['pe_industry'] = industry_pe_fair
        results['premiums']['pe_industry'] = (industry_pe_fair - current_price) / current_price * 100
        
        # 2. P/B so sánh ngành - ngành chứng khoán thường có P/B từ 1.5-2.5
        industry_pb_avg = self.get_industry_pb()
        pb_fair = metrics['bvps'] * industry_pb_avg
        results['methods']['pb_industry'] = pb_fair
        results['premiums']['pb_industry'] = (pb_fair - current_price) / current_price * 100
        
        # 3. Tăng trưởng EPS (PEG) - PEG hợp lý = 1
        eps_growth = metrics['eps_cagr']
        if eps_growth > 0 and eps_growth < 100:  # tránh giá trị bất thường
            peg_ratio = 1.0  # PEG hợp lý
            growth_pe = eps_growth * peg_ratio
            peg_fair = metrics['eps'] * growth_pe
            results['methods']['peg'] = peg_fair
            results['premiums']['peg'] = (peg_fair - current_price) / current_price * 100
        
        # 4. ROE-based valuation - Cổ phiếu chất lượng cao có ROE > 15%
        roe = metrics['roe']
        if roe > 5 and roe < 100:  # tránh giá trị bất thường
            # Công thức: P/E = 15 + (ROE - 15) * 0.5 cho ROE > 15%
            # P/E = ROE * 1.2 cho ROE <= 15%
            if roe > 15:
                roe_pe = 15 + (roe - 15) * 0.5
            else:
                roe_pe = roe * 1.2
            roe_fair = metrics['eps'] * roe_pe
            results['methods']['roe_based'] = roe_fair
            results['premiums']['roe_based'] = (roe_fair - current_price) / current_price * 100
        
        # 5. P/S so sánh ngành
        industry_ps_avg = self.get_industry_ps()
        ps_fair = current_price / metrics['ps_ratio'] * industry_ps_avg
        results['methods']['ps_industry'] = ps_fair
        results['premiums']['ps_industry'] = (ps_fair - current_price) / current_price * 100
        
        # 6. Tính fair value tổng hợp
        valid_methods = []
        weights = {}
        
        # Gán trọng số dựa trên độ tin cậy của từng phương pháp
        if 'pe_industry' in results['methods'] and results['premiums']['pe_industry'] is not None:
            valid_methods.append('pe_industry')
            weights['pe_industry'] = 0.3
        
        if 'pb_industry' in results['methods'] and results['premiums']['pb_industry'] is not None:
            valid_methods.append('pb_industry')
            weights['pb_industry'] = 0.25
        
        if 'peg' in results['methods'] and results['premiums']['peg'] is not None:
            valid_methods.append('peg')
            weights['peg'] = 0.2
        
        if 'roe_based' in results['methods'] and results['premiums']['roe_based'] is not None:
            valid_methods.append('roe_based')
            weights['roe_based'] = 0.15
        
        if 'ps_industry' in results['methods'] and results['premiums']['ps_industry'] is not None:
            valid_methods.append('ps_industry')
            weights['ps_industry'] = 0.1
        
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
    
    def get_industry_pe(self):
        """Lấy P/E trung bình ngành phù hợp với cổ phiếu"""
        # Phân loại ngành dựa trên mã cổ phiếu
        if self.symbol.startswith(('BVH', 'BMI', 'BIC', 'BID', 'CTG', 'EIB', 'HDB', 
                                  'LPB', 'MBB', 'MSB', 'OCB', 'SHB', 'STB', 'TCB', 'TPB', 'VCB', 'VIB', 'VPB')):
            return 8.5  # Ngân hàng
        
        elif self.symbol.startswith(('FPT', 'CMG', 'DXG', 'KDH', 'NVL', 'PDR', 'VHM', 
                                    'VIC', 'VRE', 'NLG', 'TTC', 'HAR')):
            return 6.5  # Bất động sản
        
        elif self.symbol.startswith(('SAB', 'MSN', 'MWG', 'PNJ', 'VNM', 'HAG', 'DGC',
                                    'GAS', 'REE', 'HCM', 'SSI', 'VND', 'TVS', 'AGR')):
            return 20.0  # Tiêu dùng & Dịch vụ
        
        elif self.symbol.startswith(('VJC', 'HVN', 'AAA', 'HCM', 'PLX', 'DPM', 'DRC',
                                    'BWE', 'PC1', 'SBT')):
            return 15.0  # Công nghiệp & Nguyên liệu
        
        else:
            return 15.0  # Mặc định
    
    def get_industry_pb(self):
        """Lấy P/B trung bình ngành"""
        if self.symbol.startswith(('BVH', 'BMI', 'BIC', 'BID', 'CTG', 'EIB', 'HDB', 
                                  'LPB', 'MBB', 'MSB', 'OCB', 'SHB', 'STB', 'TCB', 'TPB', 'VCB', 'VIB', 'VPB')):
            return 1.2  # Ngân hàng
        
        elif self.symbol.startswith(('FPT', 'CMG', 'DXG', 'KDH', 'NVL', 'PDR', 'VHM', 
                                    'VIC', 'VRE', 'NLG', 'TTC', 'HAR')):
            return 0.9  # Bất động sản
        
        elif self.symbol.startswith(('SAB', 'MSN', 'MWG', 'PNJ', 'VNM', 'HAG', 'DGC',
                                    'GAS', 'REE', 'HCM', 'SSI', 'VND', 'TVS', 'AGR')):
            return 3.5  # Tiêu dùng & Dịch vụ
        
        elif self.symbol.startswith(('VJC', 'HVN', 'AAA', 'HCM', 'PLX', 'DPM', 'DRC',
                                    'BWE', 'PC1', 'SBT')):
            return 1.8  # Công nghiệp & Nguyên liệu
        
        else:
            return 2.0  # Mặc định
    
    def get_industry_ps(self):
        """Lấy P/S trung bình ngành"""
        if self.symbol.startswith(('BVH', 'BMI', 'BIC', 'BID', 'CTG', 'EIB', 'HDB', 
                                  'LPB', 'MBB', 'MSB', 'OCB', 'SHB', 'STB', 'TCB', 'TPB', 'VCB', 'VIB', 'VPB')):
            return 3.0  # Ngân hàng
        
        elif self.symbol.startswith(('FPT', 'CMG', 'DXG', 'KDH', 'NVL', 'PDR', 'VHM', 
                                    'VIC', 'VRE', 'NLG', 'TTC', 'HAR')):
            return 1.5  # Bất động sản
        
        elif self.symbol.startswith(('SAB', 'MSN', 'MWG', 'PNJ', 'VNM', 'HAG', 'DGC',
                                    'GAS', 'REE', 'HCM', 'SSI', 'VND', 'TVS', 'AGR')):
            return 1.8  # Tiêu dùng & Dịch vụ
        
        elif self.symbol.startswith(('VJC', 'HVN', 'AAA', 'HCM', 'PLX', 'DPM', 'DRC',
                                    'BWE', 'PC1', 'SBT')):
            return 0.9  # Công nghiệp & Nguyên liệu
        
        else:
            return 1.5  # Mặc định
    
    def get_recommendation(self, premium):
        """Đưa ra khuyến nghị dựa trên chênh lệch định giá"""
        if premium > 30:
            return "STRONG BUY 🚀", "Cổ phiếu đang định giá RẤT THẤP so với giá trị thực, cơ hội sinh lời lớn.", "strong-buy"
        elif premium > 15:
            return "BUY 💰", "Cổ phiếu đang định giá THẤP so với giá trị thực, tiềm năng tăng trưởng tốt.", "buy"
        elif premium > -5:
            return "HOLD ⚖️", "Cổ phiếu đang định giá HỢP LÝ, có thể nắm giữ trong danh mục.", "hold"
        elif premium > -20:
            return "REDUCE 📉", "Cổ phiếu đang định giá CAO so với giá trị thực, cân nhắc giảm tỷ trọng.", "reduce"
        else:
            return "SELL 🔴", "Cổ phiếu đang định giá RẤT CAO so với giá trị thực, nên chốt lời.", "sell"
    
    def generate_pe_chart(self):
        """Tạo biểu đồ P/E lịch sử"""
        if self.ratios is None or self.ratios.empty:
            return None
        
        try:
            # Lấy dữ liệu P/E lịch sử
            years = self.ratios.index.tolist()[:5]
            pe_values = []
            
            for year in years:
                row = self.ratios.loc[year]
                pe_value = row.get('priceToEarning', row.get('pe', 0))
                pe_values.append(pe_value)
            
            df = pd.DataFrame({
                'Năm': years,
                'P/E': pe_values
            })
            
            if df['P/E'].sum() == 0:
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
                min(metrics['roe'] / 25 * 100, 100),  # Chuẩn hóa về 0-100
                min(metrics['net_margin'] * 3, 100),  # Chuẩn hóa về 0-100
                min(metrics['current_ratio'] * 33, 100),  # Chuẩn hóa về 0-100
                max(100 - metrics['debt_to_equity'] * 25, 0)  # Chuẩn hóa về 0-100
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
                showlegend=False,
                height=400
            )
            
            return fig
        except Exception as e:
            st.warning(f"⚠️ Không thể tạo biểu đồ sức khỏe tài chính: {str(e)}")
            return None

# Form nhập mã cổ phiếu
with st.form("analysis_form"):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        symbol = st.text_input("🔍 Nhập mã cổ phiếu", 
                              value="FPT",
                              placeholder="Ví dụ: FPT, VNM, VIC, VCB...",
                              label_visibility="collapsed")
        submitted = st.form_submit_button("🚀 Phân tích chuyên sâu", use_container_width=True)

# Xử lý khi nhấn nút phân tích
if submitted and symbol:
    # Kiểm tra tính hợp lệ của mã cổ phiếu
    if len(symbol.strip()) < 2 or len(symbol.strip()) > 4:
        st.error("❌ Mã cổ phiếu không hợp lệ. Vui lòng nhập mã HOSE chuẩn (2-4 ký tự).")
    else:
        with st.spinner(f"Đang phân tích {symbol.upper()} từ dữ liệu TCBS..."):
            try:
                analyzer = StockAnalyzer(symbol)
                metrics = analyzer.get_latest_financial_metrics()
                
                if metrics is None or metrics['eps'] <= 0:
                    st.error(f"❌ Không tìm thấy dữ liệu hợp lệ cho mã **{symbol.upper()}**. Vui lòng thử mã khác.")
                    st.info("💡 Gợi ý: Sử dụng mã cổ phiếu HOSE phổ biến như FPT, VNM, VIC, VCB, HPG, MWG...")
                else:
                    # Tính fair value
                    valuation = analyzer.calculate_fair_value(metrics)
                    
                    if valuation is None:
                        st.error(f"❌ Không thể tính giá trị hợp lý cho {symbol.upper()}.")
                    else:
                        # Hiển thị kết quả
                        st.subheader(f"📊 KẾT QUẢ PHÂN TÍCH CHUYÊN SÂU {symbol.upper()} - NĂM {metrics['year']}")
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
                            if metrics['market_cap']:
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
                        
                        if 'ps_industry' in valuation['methods']:
                            methods_data.append({
                                'Phương pháp': 'P/S ngành',
                                'P/S tham chiếu': f"{analyzer.get_industry_ps():.1f}x",
                                'Giá trị hợp lý (VND)': valuation['methods']['ps_industry'],
                                'Chênh lệch (%)': valuation['premiums']['ps_industry']
                            })
                        
                        if methods_data:
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
                        
                        tab1, tab2, tab3 = st.tabs(["📈 P/E Lịch sử", "💪 Sức khỏe tài chính", "📊 Tổng quan"])
                        
                        with tab1:
                            pe_chart = analyzer.generate_pe_chart()
                            if pe_chart:
                                st.plotly_chart(pe_chart, use_container_width=True)
                                
                                # Phân tích P/E
                                current_pe = metrics['pe_ratio']
                                if len(analyzer.ratios) >= 3:
                                    avg_pe_3y = np.mean([
                                        analyzer.ratios.iloc[i].get('priceToEarning', 
                                                                   analyzer.ratios.iloc[i].get('pe', 0))
                                        for i in range(3)
                                    ])
                                    pe_analysis = ""
                                    
                                    if current_pe < avg_pe_3y * 0.8:
                                        pe_analysis = f"P/E hiện tại ({current_pe:.1f}) thấp hơn 20% so với trung bình 3 năm ({avg_pe_3y:.1f}), cho thấy cổ phiếu đang được định giá hấp dẫn."
                                    elif current_pe > avg_pe_3y * 1.2:
                                        pe_analysis = f"P/E hiện tại ({current_pe:.1f}) cao hơn 20% so với trung bình 3 năm ({avg_pe_3y:.1f}), có thể đang bị định giá cao."
                                    else:
                                        pe_analysis = f"P/E hiện tại ({current_pe:.1f}) ở mức tương đương với trung bình 3 năm ({avg_pe_3y:.1f}), phản ánh định giá hợp lý."
                                    
                                    st.info(pe_analysis)
                            else:
                                st.info("Không có đủ dữ liệu để hiển thị biểu đồ P/E lịch sử.")
                        
                        with tab2:
                            health_chart = analyzer.generate_financial_health_chart(metrics)
                            if health_chart:
                                st.plotly_chart(health_chart, use_container_width=True)
                                
                                # Phân tích sức khỏe tài chính
                                health_analysis = ""
                                
                                if metrics['roe'] > 15 and metrics['net_margin'] > 15 and metrics['current_ratio'] > 1.5 and metrics['debt_to_equity'] < 1:
                                    health_analysis = "✅ **Sức khỏe tài chính TỐT**: Công ty có khả năng sinh lời cao, biên lợi nhuận tốt, thanh khoản ổn định và đòn bẩy tài chính an toàn, đủ điều kiện tăng trưởng bền vững."
                                elif metrics['roe'] > 10 and metrics['net_margin'] > 10 and metrics['current_ratio'] > 1 and metrics['debt_to_equity'] < 2:
                                    health_analysis = "🟡 **Sức khỏe tài chính TRUNG BÌNH**: Công ty có nền tảng tài chính chấp nhận được nhưng cần theo dõi một số chỉ số quan trọng để đảm bảo tăng trưởng ổn định."
                                else:
                                    health_analysis = "⚠️ **Sức khỏe tài chính YẾU**: Công ty có một số vấn đề về khả năng sinh lời, biên lợi nhuận thấp, hoặc rủi ro tài chính cao, cần thận trọng khi đầu tư."
                                
                                st.info(health_analysis)
                            else:
                                st.info("Không có đủ dữ liệu để phân tích sức khỏe tài chính.")
                        
                        with tab3:
                            # Hiển thị các chỉ số tài chính quan trọng
                            st.markdown("#### 📋 Chỉ số sinh lời")
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("ROE (%)", f"{metrics['roe']:.1f}")
                            with col2:
                                st.metric("ROA (%)", f"{metrics['roa']:.1f}")
                            with col3:
                                st.metric("Biên lợi nhuận gộp (%)", f"{metrics['gross_margin']:.1f}")
                            with col4:
                                st.metric("Biên lợi nhuận ròng (%)", f"{metrics['net_margin']:.1f}")
                            
                            st.markdown("#### 💰 Thanh khoản & Đòn bẩy")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Hệ số thanh toán hiện tại", f"{metrics['current_ratio']:.2f}")
                            with col2:
                                st.metric("Nợ/Vốn CSH", f"{metrics['debt_to_equity']:.2f}")
                            with col3:
                                st.metric("Tăng trưởng EPS (%)", f"{metrics['eps_cagr']:.1f}")
                            
                            # Phân tích tổng quan
                            st.markdown("#### 📝 Nhận xét tổng quan")
                            overview = f"""
                            <div style='background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin-top: 15px;'>
                                <p><strong>{symbol.upper()}</strong> là một công ty thuộc <strong>ngành {analyzer.get_industry_pe().__class__.__name__}</strong> 
                                với mức P/E tham chiếu ngành là <strong>{analyzer.get_industry_pe():.1f}x</strong> và P/B tham chiếu là <strong>{analyzer.get_industry_pb():.1f}x</strong>.</p>
                                
                                <p>Công ty có hệ số <strong>ROE {metrics['roe']:.1f}%</strong>, cho thấy khả năng sinh lời trên vốn chủ sở hữu ở mức 
                                <strong>{'rất tốt' if metrics['roe'] > 15 else 'khá tốt' if metrics['roe'] > 10 else 'trung bình' if metrics['roe'] > 5 else 'thấp'}</strong>. 
                                Biên lợi nhuận ròng đạt <strong>{metrics['net_margin']:.1f}%</strong>, phản ánh hiệu quả hoạt động kinh doanh 
                                <strong>{'cao' if metrics['net_margin'] > 15 else 'trung bình' if metrics['net_margin'] > 8 else 'cần cải thiện'}</strong>.</p>
                                
                                <p>Khả năng thanh khoản được đánh giá ở mức 
                                <strong>{'tốt' if metrics['current_ratio'] > 1.5 else 'chấp nhận được' if metrics['current_ratio'] > 1 else 'yếu'}</strong> 
                                với hệ số thanh toán hiện tại là <strong>{metrics['current_ratio']:.2f}</strong>. 
                                Đòn bẩy tài chính ở mức <strong>{'an toàn' if metrics['debt_to_equity'] < 1 else 'trung bình' if metrics['debt_to_equity'] < 2 else 'rủi ro cao'}</strong> 
                                với tỷ lệ nợ/vốn chủ sở hữu là <strong>{metrics['debt_to_equity']:.2f}</strong>.</p>
                            </div>
                            """
                            st.markdown(overview, unsafe_allow_html=True)
                        
                        st.markdown("---")
                        
                        # Kết luận chuyên gia
                        st.subheader("🎯 KẾT LUẬN CHUYÊN GIA")
                        
                        conclusion = f"""
                        <div class="recommendation-box {css_class}">
                            <p style='font-size: 1.1em; line-height: 1.6; margin-bottom: 10px;'>
                                <strong>{symbol.upper()}</strong> hiện đang được định giá ở mức <strong>{premium:+.1f}%</strong> so với giá trị hợp lý được tính toán từ nhiều phương pháp định giá khác nhau.
                            </p>
                            
                            <p style='font-size: 1.1em; line-height: 1.6; margin-bottom: 10px;'>
                                Dựa trên phân tích các chỉ số tài chính quan trọng, đặc biệt là <strong>ROE {metrics['roe']:.1f}%</strong>, 
                                <strong>biên lợi nhuận ròng {metrics['net_margin']:.1f}%</strong> và 
                                <strong>tăng trưởng EPS {metrics['eps_cagr']:.1f}%</strong>, 
                                công ty thể hiện <strong>{'tiềm năng tăng trưởng tốt' if metrics['roe'] > 12 and metrics['eps_cagr'] > 10 else 'năng lực kinh doanh ổn định' if metrics['roe'] > 8 else 'một số thách thức trong hoạt động kinh doanh'}</strong>.
                            </p>
                            
                            <p style='font-size: 1.1em; line-height: 1.6; margin-bottom: 0;'>
                                <strong>Khuyến nghị đầu tư:</strong> {recommendation} - {desc}
                            </p>
                        </div>
                        """
                        
                        st.markdown(conclusion, unsafe_allow_html=True)
                        
            except Exception as e:
                error_msg = str(e)
                if "403" in error_msg or "Forbidden" in error_msg:
                    st.error("❌ Lỗi kết nối với nguồn dữ liệu TCBS. Vui lòng thử lại sau.")
                    st.info("💡 Gợi ý: Hệ thống có thể đang bảo trì hoặc bị giới hạn truy cập. Thử lại sau vài phút.")
                elif "No data" in error_msg or "empty" in error_msg or "None" in error_msg:
                    st.error(f"❌ Không có dữ liệu cho mã **{symbol.upper()}**. Vui lòng thử mã khác.")
                    st.info("💡 Gợi ý: Dùng mã cổ phiếu HOSE phổ biến như FPT, VNM, VIC, VCB, HPG, MWG, SAB...")
                elif "symbol" in error_msg.lower():
                    st.error("❌ Mã cổ phiếu không hợp lệ hoặc không tồn tại trên sàn HOSE.")
                    st.info("💡 Gợi ý: Dùng mã cổ phiếu HOSE chuẩn (2-4 chữ cái), ví dụ: FPT, VNM, VIC, VCB...")
                else:
                    st.error(f"❌ Lỗi không xác định: {error_msg}")
                    st.info("💡 Gợi ý: Thử lại với mã khác hoặc liên hệ hỗ trợ.")
else:
    # Hiển thị hướng dẫn khi chưa nhập mã
    st.markdown("""
    <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 20px;'>
        <h3 style='color: #0066cc; margin-top: 0;'>📖 Hướng dẫn sử dụng</h3>
        <p>1. <strong>Nhập mã cổ phiếu</strong> vào ô tìm kiếm phía trên (ví dụ: FPT, VNM, VIC...)</p>
        <p>2. Nhấn nút <strong>"🚀 Phân tích chuyên sâu"</strong></p>
        <p>3. Xem <strong>kết quả phân tích chi tiết</strong> với các thông tin:</p>
        <ul>
            <li>Giá trị hợp lý và chênh lệch so với giá hiện tại</li>
            <li>Biểu đồ P/E lịch sử</li>
            <li>Sức khỏe tài chính tổng thể</li>
            <li>Các chỉ số tài chính quan trọng (ROE, biên lợi nhuận, thanh khoản...)</li>
            <li>Khuyến nghị đầu tư chuyên nghiệp</li>
        </ul>
        <p style='background-color: #e3f2fd; padding: 10px; border-radius: 5px; margin-top: 15px;'>
            💡 <strong>Mẹo:</strong> Sử dụng các mã cổ phiếu phổ biến trên HOSE như FPT, VNM, VIC, VCB, HPG để có kết quả tốt nhất.
        </p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("""
📊 Dữ liệu từ TCBS qua thư viện vnstock | 📈 Phương pháp định giá: P/E, P/B, PEG, ROE-based | 
💡 Kết quả chỉ mang tính tham khảo - Không phải lời khuyên đầu tư
""")

# CSS bổ sung cho mobile
st.markdown("""
<style>
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
