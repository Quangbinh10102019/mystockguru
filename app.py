"""
Entry point - Hệ thống phân tích cổ phiếu tự động
Có thể chạy như CLI hoặc import như module
"""
import json
import sys
from analysis import analyze_stock


def format_output(result: dict) -> str:
    """Định dạng kết quả để hiển thị"""
    if result is None:
        return "❌ Không thể phân tích cổ phiếu này."
    
    output = []
    output.append(f"\n{'='*60}")
    output.append(f"📊 PHÂN TÍCH CỔ PHIẾU: {result['symbol']}")
    output.append(f"{'='*60}\n")
    
    # Thông tin cơ bản
    output.append("📈 THÔNG TIN CƠ BẢN:")
    output.append(f"  • Giá hiện tại: {result['current_price']:,.0f} VND")
    output.append(f"  • P/E hiện tại: {result['current_pe']:.2f}x")
    output.append(f"  • EPS: {result['current_eps']:,.0f} VND")
    output.append(f"  • Số năm phân tích: {result['years_analyzed']} năm\n")
    
    # Thống kê P/E
    output.append("📊 THỐNG KÊ P/E (5 năm):")
    output.append(f"  • Trung bình: {result['pe_stats']['avg_5y']:.2f}x")
    output.append(f"  • Thấp nhất: {result['pe_stats']['min_5y']:.2f}x")
    output.append(f"  • Cao nhất: {result['pe_stats']['max_5y']:.2f}x\n")
    
    # Xu hướng
    output.append("📈 XU HƯỚNG:")
    output.append(f"  • P/E: {result['trends']['pe']['status']} ({result['trends']['pe']['growth_rate']:+.1f}%/năm)")
    output.append(f"  • EPS: {result['trends']['eps']['status']} ({result['trends']['eps']['growth_rate']:+.1f}%/năm)\n")
    
    # Giá trị hợp lý
    output.append("💰 GIÁ TRỊ HỢP LÝ:")
    output.append(f"  • Theo P/E ngành: {result['fair_values']['pe_industry']:,.0f} VND")
    output.append(f"  • Theo P/E lịch sử: {result['fair_values']['pe_historical']:,.0f} VND")
    output.append(f"  • Theo tăng trưởng: {result['fair_values']['pe_growth']:,.0f} VND")
    output.append(f"  • Giá trị hợp lý (TB): {result['fair_values']['consensus']:,.0f} VND\n")
    
    # Đánh giá định giá
    output.append("🎯 ĐÁNH GIÁ ĐỊNH GIÁ:")
    status = result['valuation_status']
    output.append(f"  • Trạng thái: {status['status']} - {status['description']}")
    output.append(f"  • Chênh lệch: {result['premium']:+.1f}%\n")
    
    # Khuyến nghị
    rec = result['recommendation']
    output.append(f"💡 KHUYẾN NGHỊ: {rec['action']}")
    output.append(f"  {rec['action_detail']}\n")
    
    output.append("📋 LÝ DO:")
    for i, reason in enumerate(rec['reasons'], 1):
        output.append(f"  {i}. {reason}")
    
    output.append(f"\n{'='*60}\n")
    
    return "\n".join(output)


def main():
    """Hàm main - CLI mode"""
    if len(sys.argv) < 2:
        print("""
🎯 HỆ THỐNG PHÂN TÍCH CỔ PHIẾU TỰ ĐỘNG

Cách sử dụng:
  python main.py <MÃ_CỔ_PHIẾU> [--json]

Ví dụ:
  python main.py FPT
  python main.py VNM --json
  python main.py VIC

Tính năng:
  • Tự động phân tích 5 năm gần nhất
  • Tính toán giá trị hợp lý bằng nhiều phương pháp
  • Đánh giá over/under/fair value
  • Đưa ra khuyến nghị hành động cụ thể
        """)
        sys.exit(1)
    
    symbol = sys.argv[1].upper()
    output_json = '--json' in sys.argv
    
    print(f"Đang phân tích {symbol}...")
    result = analyze_stock(symbol)
    
    if output_json:
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    else:
        print(format_output(result))


if __name__ == "__main__":
    main()
