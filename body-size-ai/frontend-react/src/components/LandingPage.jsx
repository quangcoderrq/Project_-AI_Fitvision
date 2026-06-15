import React from 'react';
import { ArrowRight, Bot, Shirt, Layers, ShieldCheck, Zap } from 'lucide-react';

export default function LandingPage({ onNavigate }) {
    return (
        <div className="fade-in" style={{ paddingBottom: '3rem' }}>
            {/* Hero Banner */}
            <section className="hero-section">
                <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(59, 130, 246, 0.1)', color: 'var(--primary-color)', padding: '0.5rem 1rem', borderRadius: '30px', fontSize: '0.85rem', fontWeight: '600', marginBottom: '1.5rem' }}>
                    <Bot size={16} /> Công nghệ AI Chọn Size Hàng Đầu
                </div>
                <h2 className="hero-title">FitVision AI</h2>
                <h3 style={{ fontSize: '2rem', marginBottom: '1.5rem', fontWeight: '500', lineHeight: '1.3' }}>
                    Giải pháp đo kích thước & gợi ý size áo quần tự động cho e-Commerce
                </h3>
                <p className="hero-subtitle">
                    Tích hợp widget chọn size thông minh vào website bán lẻ của bạn. Khách hàng chỉ cần tải lên 1 ảnh đứng thẳng và nhập chiều cao/cân nặng để nhận ngay khuyến nghị size chuẩn xác và mô phỏng 3D trực quan sinh động.
                </p>
                <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                    <button className="btn btn-primary" onClick={() => onNavigate('demo')}>
                        Trải nghiệm Demo <ArrowRight size={18} />
                    </button>
                    <button className="btn btn-secondary" onClick={() => onNavigate('pricing')}>
                        Xem bảng giá tích hợp
                    </button>
                </div>
            </section>

            {/* Stats Metrics */}
            <section style={{ marginTop: '1rem', marginBottom: '4rem' }}>
                <div className="stats-grid">
                    <div className="glass-panel stat-card">
                        <div className="stat-val">+32%</div>
                        <div className="stat-label">Tăng Tỷ Lệ Chuyển Đổi (CVR)</div>
                    </div>
                    <div className="glass-panel stat-card">
                        <div className="stat-val">-45%</div>
                        <div className="stat-label">Giảm Tỷ Lệ Đổi Trả Quần Áo</div>
                    </div>
                    <div className="glass-panel stat-card">
                        <div className="stat-val">95%</div>
                        <div className="stat-label">Khách Hàng Hài Lòng Về Gợi Ý</div>
                    </div>
                </div>
            </section>

            {/* Core Features */}
            <section style={{ marginBottom: '4rem' }}>
                <h3 style={{ textAlign: 'center', fontSize: '2rem', marginBottom: '2.5rem' }}>Tính Năng Nổi Bật</h3>
                <div className="grid-3">
                    <div className="glass-panel flex-col" style={{ padding: '2rem' }}>
                        <div style={{ width: '50px', height: '50px', borderRadius: '12px', background: 'var(--gradient-1)', display: 'flex', alignItems: 'center', justifyCenter: 'center', justifyContent: 'center', color: 'white', marginBottom: '1rem' }}>
                            <Shirt size={24} />
                        </div>
                        <h4 style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>Pose Estimation Nhạy Bén</h4>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', lineHeight: '1.5' }}>
                            Sử dụng thư viện MediaPipe để phát hiện các keypoints quan trọng trên cơ thể người dùng từ ảnh 2D thông thường, tự động cảnh báo quần áo quá rộng.
                        </p>
                    </div>

                    <div className="glass-panel flex-col" style={{ padding: '2rem' }}>
                        <div style={{ width: '50px', height: '50px', borderRadius: '12px', background: 'var(--gradient-2)', display: 'flex', alignItems: 'center', justifyCenter: 'center', justifyContent: 'center', color: 'white', marginBottom: '1rem' }}>
                            <Layers size={24} />
                        </div>
                        <h4 style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>Mô Phỏng Cơ Thể 3D</h4>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', lineHeight: '1.5' }}>
                            Xây dựng mô hình 3D trực quan từ số đo (vòng ngực, eo, hông) giúp khách hàng dễ dàng hình dung dáng vóc của mình và tự tin hơn khi chọn size.
                        </p>
                    </div>

                    <div className="glass-panel flex-col" style={{ padding: '2rem' }}>
                        <div style={{ width: '50px', height: '50px', borderRadius: '12px', background: 'var(--gradient-gold)', display: 'flex', alignItems: 'center', justifyCenter: 'center', justifyContent: 'center', color: 'white', marginBottom: '1rem' }}>
                            <Zap size={24} />
                        </div>
                        <h4 style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>Tích Hợp Dễ Dàng</h4>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', lineHeight: '1.5' }}>
                            Nhúng trực tiếp vào Shopify, WooCommerce hoặc bất kỳ website HTML tùy biến nào chỉ bằng API Token được kích hoạt sau vài bước thanh toán.
                        </p>
                    </div>
                </div>
            </section>

            {/* How it works */}
            <section className="glass-panel" style={{ padding: '3rem 2rem', marginBottom: '4rem' }}>
                <h3 style={{ textAlign: 'center', fontSize: '1.8rem', marginBottom: '2.5rem' }}>Quy Trình Tích Hợp Đơn Giản</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '2rem' }}>
                    <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '2.5rem', color: 'var(--primary-color)', fontWeight: '700', marginBottom: '1rem', fontFamily: 'Outfit' }}>01</div>
                        <h5 style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>Chọn gói cước</h5>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Tham khảo bảng giá các gói và đăng ký tài khoản doanh nghiệp.</p>
                    </div>
                    <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '2.5rem', color: 'var(--primary-color)', fontWeight: '700', marginBottom: '1rem', fontFamily: 'Outfit' }}>02</div>
                        <h5 style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>Nhận API Token</h5>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Thanh toán và lấy mã API Token độc quyền trên trang Dashboard lập trình viên.</p>
                    </div>
                    <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '2.5rem', color: 'var(--primary-color)', fontWeight: '700', marginBottom: '1rem', fontFamily: 'Outfit' }}>03</div>
                        <h5 style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>Nhúng Widget</h5>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Sao chép mã HTML/JS của FitVision AI dán vào trang chi tiết sản phẩm của bạn.</p>
                    </div>
                    <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '2.5rem', color: 'var(--primary-color)', fontWeight: '700', marginBottom: '1rem', fontFamily: 'Outfit' }}>04</div>
                        <h5 style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>Bùng nổ doanh số</h5>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Theo dõi các số liệu phân tích cuộc gọi API và phản hồi tích cực từ khách hàng.</p>
                    </div>
                </div>
            </section>

            {/* Bottom Call-to-action */}
            <section style={{ textAlign: 'center', padding: '2rem 0' }}>
                <h3 style={{ fontSize: '1.8rem', marginBottom: '1rem' }}>Bắt đầu nâng tầm sàn thương mại điện tử của bạn</h3>
                <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>Hãy đăng ký dùng thử miễn phí hoặc mua gói kích hoạt đầy đủ API Token ngay.</p>
                <button className="btn btn-primary" onClick={() => onNavigate('pricing')}>
                    Bắt đầu tích hợp ngay
                </button>
            </section>
        </div>
    );
}
