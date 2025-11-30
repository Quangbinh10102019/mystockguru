import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from vnstock import Finance

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

# Class phân tích cổ phiếu chuyên nghiệp
class StockAnalyzer:
    def __init__(self, symbol):
        self.symbol = symbol.upper()
        self.finance = Finance(symbol=self.symbol, source='TCBS')
        self.ratios = None
        self.income = None
        self.balance = None
        self.cashflow = None
        self.load_financial_data()
        
    def load_financial_data(self):
        """Tải toàn bộ dữ liệu tài chính cần thiết"""
        try:
            # Lấy chỉ số tài chính
            self.ratios = self.finance.ratio(period='year', lang='vi')
            
            # Lấy báo cáo KQKD
            self.income = self.finance.income_statement(period='year', lang='vi')
            
            # Lấy báo cáo CĐKT
            self.balance = self.finance.balance_sheet(period='year', lang='vi')
            
            # Lấy báo cáo LCTT
            self.cashflow = self.finance.cash_flow(period='year', lang='vi')
        except Exception as e:
            st.error(f"❌ Lỗi khi tải dữ liệu: {str(e)}")
    
    def get_latest_financial_metrics(self):
        """Lấy các chỉ số tài chính quan trọng nhất"""
        if self.ratios is None or self.ratios.empty:
            return None
        
        latest = self.ratios.iloc[0]
        
        # Trích xuất các chỉ số quan trọng
        try:
            # Chỉ số định giá
            pe_ratio = latest[('Chỉ tiêu định giá', 'P/E')]
            pb_ratio = latest[('Chỉ tiêu định giá', 'P/B')]
            eps = latest[('Chỉ tiêu định giá', 'EPS (VND)')]
            bvps = latest[('Chỉ tiêu định giá', 'BVPS (VND)')]
            market_cap = latest[('Chỉ tiêu định giá', 'Vốn hóa (Tỷ đồng)')]
            shares_outstanding = latest[('Chỉ tiêu định giá', 'Số CP lưu hành (Triệu CP)')]
            
            # Chỉ số sinh lời
            roe = latest[('Chỉ tiêu khả năng sinh lợi', 'ROE (%)')]
            roa = latest[('Chỉ tiêu khả năng sinh lợi', 'ROA (%)')]
            gross_margin = latest[('Chỉ tiêu khả năng sinh lợi', 'Biên lợi nhuận gộp (%)')]
            net_margin = latest[('Chỉ tiêu khả năng sinh lợi', 'Biên lợi nhuận ròng (%)')]
            
            # Chỉ số thanh khoản & đòn bẩy
            current_ratio = latest[('Chỉ tiêu thanh khoản', 'Chỉ số thanh toán hiện thời')]
            debt_to_equity = latest[('Chỉ tiêu cơ cấu nguồn vốn', 'Nợ/VCSH')]
            
            # Tăng trưởng EPS 3 năm
            eps_values = self.ratios[('Chỉ tiêu định giá', 'EPS (VND)')].values[:3]
            if len(eps_values) >= 3 and eps_values[2] > 0:
                eps_cagr = (eps_values[0] / eps_values[2]) ** (1/2) - 1
            else:
                eps_cagr = 0
                
            return {
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
        industry_pe_avg = 15  # P/E trung bình ngành chứng khoán
        industry_pe_fair = metrics['eps'] * industry_pe_avg
        results['methods']['pe_industry'] = industry_pe_fair
        results['premiums']['pe_industry'] = (industry_pe_fair - current_price) / current_price * 100
        
        # 2. P/B so sánh ngành - ngành chứng khoán thường có P/B từ 1.5-2.5
        industry_pb_avg = 2.0  # P/B trung bình ngành chứng khoán
        pb_fair = metrics['bvps'] * industry_pb_avg
        results['methods']['pb_industry'] = pb_fair
        results['premiums']['pb_industry'] = (pb_fair - current_price) / current_price * 100
        
        # 3. Tăng trưởng EPS (PEG) - PEG hợp lý = 1
        if metrics['eps_cagr'] > 0:
            peg_ratio = 1.0  # PEG hợp lý
            growth_pe = metrics['eps_cagr'] * peg_ratio
            peg_fair = metrics['eps'] * growth_pe
            results['methods']['peg'] = peg_fair
            results['premiums']['peg'] = (peg_fair - current_price) / current_price * 100
        
        # 4. ROE-based valuation - Cổ phiếu chất lượng cao có ROE > 15%
        if metrics['roe'] > 15:
            roe_pe = 15 + (metrics['roe'] - 15) * 0.5  # Công thức đơn giản
            roe_fair = metrics['eps'] * roe_pe
            results['methods']['roe_based'] = roe_fair
            results['premiums']['roe_based'] = (roe_fair - current_price) / current_price * 100
        
        # 5. Tính fair value tổng hợp
        valid_methods = [v for k, v in results['methods'].items() if 'premiums' in results and results['premiums'].get(k, 0) is not None]
        if valid_methods:
            # Trọng số hóa các phương pháp
            weights = {
                'pe_industry': 0.3,
                'pb_industry': 0.2,
                'peg': 0.3,
                'roe_based': 0.2
            }
            
            weighted_sum = 0
            total_weight = 0
            
            for method, value in results['methods'].items():
                if method in weights and value > 0:
                    weighted_sum += value * weights[method]
                    total_weight += weights[method]
            
            if total_weight > 0:
                fair_value = weighted_sum / total_weight
                premium = (fair_value - current_price) / current_price * 100
                results['consensus'] = {
                    'fair_value': fair_value,
                    'premium': premium
                }
        
        return results
    
    def get_recommendation(self, premium):
        """Đưa ra khuyến nghị dựa trên chênh lệch định giá"""
        if premium > 30:
            return "STRONG BUY 🚀", "Cổ phiếu đang định giá RẤT THẤP so với giá trị thực, cơ hội sinh lời lớn."
        elif premium > 15:
            return "BUY 💰", "Cổ phiếu đang định giá THẤP so với giá trị thực, tiềm năng tăng trưởng tốt."
        elif premium > -5:
            return "HOLD ⚖️", "Cổ phiếu đang định giá HỢP LÝ, có thể nắm giữ trong danh mục."
        elif premium > -20:
            return "REDUCE 📉", "Cổ phiếu đang định giá CAO so với giá trị thực, cân nhắc giảm tỷ trọng."
        else:
            return "SELL 🔴", "Cổ phiếu đang định giá RẤT CAO so với giá trị thực, nên chốt lời."
    
    def generate_pe_chart(self):
        """Tạo biểu đồ P/E lịch sử"""
        if self.ratios is None or self.ratios.empty:
            return None
        
        years = self.ratios[('Meta', 'Năm')].values[:5]
        pe_values = self.ratios[('Chỉ tiêu định giá', 'P/E')].values[:5]
        
        df = pd.DataFrame({
            'Năm': years,
            'P/E': pe_values
        })
        
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
    
    def generate_financial_health_chart(self, metrics):
        """Tạo biểu đồ sức khỏe tài chính"""
        if metrics is None:
            return None
        
        categories = ['ROE (%)', 'Margin (%)', 'Thanh khoản', 'Đòn bẩy']
        values = [
            min(metrics['roe'] / 20 * 100, 100),  # Chuẩn hóa về 0-100
            min(metrics['net_margin'] * 2, 100),  # Chuẩn hóa về 0-100
            min(metrics['current_ratio'] * 25, 100),  # Chuẩn hóa về 0-100
            max(100 - metrics['debt_to_equity'] * 20, 0)  # Chuẩn hóa về 0-100
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
            text=values,
            textposition='outside'
        )
        
        fig.update_layout(
            plot_bgcolor='white',
            yaxis_range=[0, 110],
            showlegend=False
        )
        
        return fig

# Form nhập mã cổ phiếu
with st.form("analysis_form"):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        symbol = st.text_input("🔍 Nhập mã cổ phiếu", placeholder="Ví dụ: FPT, VNM, VIC, VCB...", 
                              label_visibility="collapsed")
        submitted = st.form_submit_button("🚀 Phân tích chuyên sâu", use_container_width=True)

if submitted and symbol:
    with st.spinner(f"Đang phân tích {symbol.upper()} từ dữ liệu TCBS..."):
        try:
                            try:
                    # SỬA CHÍNH: Xử lý trường hợp symbol rỗng hoặc không hợp lệ
                    if not symbol or len(symbol) < 2 or len(symbol) > 5:
                        st.error("❌ Mã cổ phiếu không hợp lệ. Vui lòng nhập mã HOSE chuẩn (2-5 ký tự).")
                        st.stop()
                    
                    # SỬA CHÍNH: Thêm kiểm tra nguồn dữ liệu
                    analyzer = StockAnalyzer(symbol)
                    
                    # SỬA CHÍNH: Thêm kiểm tra xem đã tải được dữ liệu chưa
                    if analyzer.ratios is None or analyzer.ratios.empty:
                        st.error(f"❌ Không tải được dữ liệu cho mã **{symbol}**. Vui lòng thử lại sau hoặc dùng mã khác.")
                        st.info("💡 Gợi ý: Dùng mã cổ phiếu HOSE phổ biến như FPT, VNM, VIC, VCB, HPG...")
                        st.stop()
                    
                    # Lấy chỉ số tài chính
                    metrics = analyzer.get_latest_financial_metrics()
                    
                    # SỬA CHÍNH: Thêm kiểm tra metrics
                    if metrics is None:
                        st.error(f"❌ Không trích xuất được chỉ số tài chính cho mã **{symbol}**.")
                        st.info("💡 Gợi ý: Thử các mã phổ biến như FPT, VNM, VIC, VCB, HPG...")
                        st.stop()
                    
                    # Tính giá trị hợp lý
                    valuation = analyzer.calculate_fair_value(metrics)
                    
                    if valuation is None:
                        st.error(f"❌ Không thể tính giá trị hợp lý cho mã **{symbol}**.")
                        st.info("💡 Gợi ý: Thử các mã phổ biến như FPT, VNM, VIC, VCB, HPG...")
                        st.stop()
                    
                    # Hiển thị kết quả
                    st.success(f"✅ Phân tích thành công {symbol}!")
                    
                    # Hiển thị giá hiện tại và giá trị hợp lý
                    current_price = valuation['current_price']
                    fair_value = valuation['consensus']['fair_value']
                    premium = valuation['consensus']['premium']
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Giá hiện tại", f"{current_price:,.0f} VND")
                    with col2:
                        st.metric("Giá trị hợp lý", f"{fair_value:,.0f} VND")
                    with col3:
                        st.metric("Chênh lệch", f"{premium:+.1f}%")
                    
                    # SỬA CHÍNH: Thêm kiểm tra premium trước khi đưa ra khuyến nghị
                    if premium is not None:
                        recommendation, desc = analyzer.get_recommendation(premium)
                        st.markdown(f"### {recommendation}")
                        st.caption(desc)
                    else:
                        st.warning("⚠️ Không thể xác định khuyến nghị do thiếu dữ liệu.")
                    
                    # Hiển thị biểu đồ P/E
                    pe_chart = analyzer.generate_pe_chart()
                    if pe_chart:
                        st.plotly_chart(pe_chart, use_container_width=True)
                    
                    # Hiển thị thông tin chi tiết
                    st.subheader("📊 Thông tin chi tiết")
                    st.write(f"- **P/E hiện tại**: {metrics['pe_ratio']:.2f}x")
                    st.write(f"- **EPS**: {metrics['eps']:,.0f} VND")
                    st.write(f"- **P/E ngành tham chiếu**: {15:.1f}x")
                    st.write(f"- **ROE**: {metrics['roe']:.1f}%")
                    st.write(f"- **Biên lợi nhuận ròng**: {metrics['net_margin']:.1f}%")
                    st.write(f"- **Hệ số thanh khoản**: {metrics['current_ratio']:.2f}")
                    st.write(f"- **Nợ/Vốn CSH**: {metrics['debt_to_equity']:.2f}")
                    st.write(f"- **Tăng trưởng EPS 3 năm**: {metrics['eps_cagr']:.1f}%")
                    
                except Exception as e:
                    # SỬA CHÍNH: Hiển thị lỗi chi tiết hơn
                    error_msg = str(e)
                    if "403" in error_msg or "Forbidden" in error_msg:
                        st.error("❌ Lỗi kết nối với nguồn dữ liệu. Vui lòng thử lại sau.")
                        st.info("💡 Gợi ý: Hệ thống có thể đang bảo trì hoặc bị chặn truy cập.")
                    elif "No data" in error_msg or "empty" in error_msg:
                        st.error(f"❌ Không có dữ liệu cho mã **{symbol}**. Vui lòng thử mã khác.")
                        st.info("💡 Gợi ý: Dùng mã cổ phiếu HOSE phổ biến như FPT, VNM, VIC, VCB, HPG...")
                    else:
                        st.error(f"❌ Lỗi không xác định: {error_msg}")
                        st.info("💡 Gợi ý: Thử lại với mã khác hoặc liên hệ hỗ trợ.")
            metrics = analyzer.get_latest_financial_metrics()
            
            if metrics is None:
                st.error(f"❌ Không tìm thấy dữ liệu cho mã **{symbol.upper()}**. Vui lòng thử mã khác.")
            else:
                # Tính fair value
                valuation = analyzer.calculate_fair_value(metrics)
                
                # Hiển thị kết quả
                st.subheader(f"📊 KẾT QUẢ PHÂN TÍCH CHUYÊN SÂU {symbol.upper()}")
                st.markdown("---")
                
                # Thông tin cơ bản
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Giá hiện tại", f"{valuation['current_price']:,.0f} VND")
                with col2:
                    st.metric("EPS (VND)", f"{metrics['eps']:,.0f}")
                with col3:
                    st.metric("BVPS (VND)", f"{metrics['bvps']:,.0f}")
                
                st.markdown("---")
                
                # Kết quả định giá
                if 'consensus' in valuation:
                    fair_value = valuation['consensus']['fair_value']
                    premium = valuation['consensus']['premium']
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Giá trị hợp lý", f"{fair_value:,.0f} VND", 
                                 delta=f"{premium:+.1f}%", delta_color="normal")
                    with col2:
                        recommendation, desc = analyzer.get_recommendation(premium)
                        st.markdown(f"### {recommendation}")
                        st.caption(desc)
                
                st.markdown("---")
                
                # Chi tiết các phương pháp định giá
                st.subheader("📈 CHI TIẾT PHƯƠNG PHÁP ĐỊNH GIÁ")
                
                methods_df = pd.DataFrame({
                    'Phương pháp': ['P/E ngành', 'P/B ngành', 'PEG Ratio', 'ROE-based'],
                    'Giá trị hợp lý (VND)': [
                        valuation['methods'].get('pe_industry', 0),
                        valuation['methods'].get('pb_industry', 0),
                        valuation['methods'].get('peg', 0),
                        valuation['methods'].get('roe_based', 0)
                    ],
                    'Chênh lệch (%)': [
                        valuation['premiums'].get('pe_industry', 0),
                        valuation['premiums'].get('pb_industry', 0),
                        valuation['premiums'].get('peg', 0),
                        valuation['premiums'].get('roe_based', 0)
                    ]
                })
                
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
                
                tab1, tab2, tab3 = st.tabs(["📈 P/E Lịch sử", "💪 Sức khỏe tài chính", "📊 Báo cáo chi tiết"])
                
                with tab1:
                    pe_chart = analyzer.generate_pe_chart()
                    if pe_chart:
                        st.plotly_chart(pe_chart, use_container_width=True)
                        
                        # Phân tích P/E
                        current_pe = metrics['pe_ratio']
                        avg_pe_5y = np.mean(analyzer.ratios[('Chỉ tiêu định giá', 'P/E')].values[:5])
                        pe_analysis = ""
                        
                        if current_pe < avg_pe_5y * 0.8:
                            pe_analysis = f"P/E hiện tại ({current_pe:.1f}) thấp hơn 20% so với trung bình 5 năm ({avg_pe_5y:.1f}), cho thấy cổ phiếu đang được định giá hấp dẫn."
                        elif current_pe > avg_pe_5y * 1.2:
                            pe_analysis = f"P/E hiện tại ({current_pe:.1f}) cao hơn 20% so với trung bình 5 năm ({avg_pe_5y:.1f}), có thể đang bị định giá cao."
                        else:
                            pe_analysis = f"P/E hiện tại ({current_pe:.1f}) ở mức tương đương với trung bình 5 năm ({avg_pe_5y:.1f}), phản ánh định giá hợp lý."
                        
                        st.info(pe_analysis)
                
                with tab2:
                    health_chart = analyzer.generate_financial_health_chart(metrics)
                    if health_chart:
                        st.plotly_chart(health_chart, use_container_width=True)
                        
                        # Phân tích sức khỏe tài chính
                        health_analysis = ""
                        
                        if metrics['roe'] > 15 and metrics['net_margin'] > 15 and metrics['current_ratio'] > 1.5 and metrics['debt_to_equity'] < 1:
                            health_analysis = "✅ **Sức khỏe tài chính TỐT**: Công ty có khả năng sinh lời cao, biên lợi nhuận tốt, thanh khoản ổn định và đòn bẩy tài chính an toàn."
                        elif metrics['roe'] > 10 and metrics['net_margin'] > 10 and metrics['current_ratio'] > 1 and metrics['debt_to_equity'] < 2:
                            health_analysis = "🟡 **Sức khỏe tài chính TRUNG BÌNH**: Công ty có nền tảng tài chính chấp nhận được nhưng cần theo dõi một số chỉ số quan trọng."
                        else:
                            health_analysis = "⚠️ **Sức khỏe tài chính YẾU**: Công ty có một số vấn đề về khả năng sinh lời, biên lợi nhuận thấp, hoặc rủi ro tài chính cao."
                        
                        st.info(health_analysis)
                
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
                        st.metric("Tăng trưởng EPS 3 năm (%)", f"{metrics['eps_cagr']:.1f}")
                
                st.markdown("---")
                
                # Kết luận chuyên gia
                st.subheader("🎯 KẾT LUẬN CHUYÊN GIA")
                
                conclusion = f"""
                <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 4px solid #0066cc;'>
                    <p style='font-size: 1.1em; line-height: 1.6;'>
                        <strong>{symbol.upper()}</strong> hiện đang được định giá ở mức <strong>{premium:+.1f}%</strong> so với giá trị hợp lý được tính toán từ 4 phương pháp định giá khác nhau.
                    </p>
                    
                    <p style='font-size: 1.1em; line-height: 1.6;'>
                        Với <strong>ROE {metrics['roe']:.1f}%</strong> và <strong>tăng trưởng EPS {metrics['eps_cagr']:.1f}%</strong> trong 3 năm qua, công ty thể hiện khả năng sinh lời tốt. Sức khỏe tài chính được đánh giá là 
                        <strong>{'TỐT' if metrics['roe'] > 15 and metrics['current_ratio'] > 1.5 else 'TRUNG BÌNH'}</strong> với hệ số thanh khoản hiện tại {metrics['current_ratio']:.2f} và tỷ lệ nợ/vốn chủ sở hữu {metrics['debt_to_equity']:.2f}.
                    </p>
                    
                    <p style='font-size: 1.1em; line-height: 1.6;'>
                        <strong>Khuyến nghị đầu tư:</strong> {recommendation} - {desc}
                    </p>
                </div>
                """
                
                st.markdown(conclusion, unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"❌ Lỗi khi phân tích {symbol}: {str(e)}")
            st.info("💡 Gợi ý: Sử dụng mã cổ phiếu HOSE phổ biến như FPT, VNM, VIC, VCB, HPG...")

# Footer
st.markdown("---")
st.caption("""
📊 Dữ liệu từ TCBS qua thư viện vnstock | 📈 Phương pháp định giá: P/E, P/B, PEG, ROE-based | 
💡 Kết quả chỉ mang tính tham khảo - Không phải lời khuyên đầu tư
""")

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
</style>
""", unsafe_allow_html=True)
