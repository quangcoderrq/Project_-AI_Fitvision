import React from 'react';
import { ArrowRight, Bot, Shirt, Layers, ShieldCheck, Zap } from 'lucide-react';

export default function LandingPage({ onNavigate }) {
    return (
        <div className="fade-in" style={{ paddingBottom: '3rem' }}>
            {/* Hero Banner */}
            <section className="hero-section">
                <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(59, 130, 246, 0.1)', color: 'var(--primary-color)', padding: '0.5rem 1rem', borderRadius: '30px', fontSize: '0.85rem', fontWeight: '600', marginBottom: '1.5rem' }}>
                    <Bot size={16} /> Công nghệ AI gợi ý size thông minh
                </div>

                <h2 className="hero-title">FitVision AI</h2>

                <h3 style={{ fontSize: '2rem', marginBottom: '1.5rem', fontWeight: '500', lineHeight: '1.3' }}>
                    Giải pháp AI tự động đo cơ thể và gợi ý size quần áo cho cửa hàng online
                </h3>

                <p className="hero-subtitle">
                    FitVision AI giúp khách hàng chọn đúng size chỉ bằng một ảnh toàn thân,
                    chiều cao và cân nặng. Hệ thống phân tích vóc dáng, đề xuất size phù hợp
                    và hỗ trợ shop giảm tỷ lệ đổi trả khi bán hàng trực tuyến.
                </p>

                <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                    <button className="btn btn-primary" onClick={() => onNavigate('demo')}>
                        Trải nghiệm demo <ArrowRight size={18} />
                    </button>
                    <button className="btn btn-secondary" onClick={() => onNavigate('pricing')}>
                        Xem bảng giá
                    </button>
                </div>
            </section>

            {/* Stats Metrics */}
            <section style={{ marginTop: '1rem', marginBottom: '4rem' }}>
                <div className="stats-grid">
                    <div className="glass-panel stat-card">
                        <div className="stat-val">+32%</div>
                        <div className="stat-label">Tăng tỷ lệ chuyển đổi</div>
                    </div>
                    <div className="glass-panel stat-card">
                        <div className="stat-val">-45%</div>
                        <div className="stat-label">Giảm tỷ lệ đổi trả</div>
                    </div>
                    <div className="glass-panel stat-card">
                        <div className="stat-val">95%</div>
                        <div className="stat-label">Khách hàng hài lòng với gợi ý size</div>
                    </div>
                </div>
            </section>

            {/* Core Features */}
            <section style={{ marginBottom: '4rem' }}>
                <h3 style={{ textAlign: 'center', fontSize: '2rem', marginBottom: '2.5rem' }}>
                    Tính năng nổi bật
                </h3>

                <div className="grid-3">
                    <div className="glass-panel flex-col" style={{ padding: '2rem' }}>
                        <div style={{ width: '50px', height: '50px', borderRadius: '12px', background: 'var(--gradient-1)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', marginBottom: '1rem' }}>
                            <Shirt size={24} />
                        </div>
                        <h4 style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>
                            Nhận diện vóc dáng bằng AI
                        </h4>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', lineHeight: '1.5' }}>
                            Phân tích ảnh toàn thân để nhận diện các điểm quan trọng trên cơ thể,
                            từ đó ước lượng số đo và đưa ra khuyến nghị size phù hợp.
                        </p>
                    </div>

                    <div className="glass-panel flex-col" style={{ padding: '2rem' }}>
                        <div style={{ width: '50px', height: '50px', borderRadius: '12px', background: 'var(--gradient-2)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', marginBottom: '1rem' }}>
                            <Layers size={24} />
                        </div>
                        <h4 style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>
                            Mô phỏng cơ thể 3D
                        </h4>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', lineHeight: '1.5' }}>
                            Hiển thị mô hình cơ thể trực quan dựa trên số đo ước lượng,
                            giúp khách hàng dễ hình dung vóc dáng và tự tin hơn khi chọn size.
                        </p>
                    </div>

                    <div className="glass-panel flex-col" style={{ padding: '2rem' }}>
                        <div style={{ width: '50px', height: '50px', borderRadius: '12px', background: 'var(--gradient-gold)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', marginBottom: '1rem' }}>
                            <Zap size={24} />
                        </div>
                        <h4 style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>
                            Dễ dàng tích hợp vào website
                        </h4>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', lineHeight: '1.5' }}>
                            Tích hợp FitVision AI vào website bán hàng thông qua Widget hoặc API,
                            phù hợp với các cửa hàng online và nền tảng thương mại điện tử.
                        </p>
                    </div>
                </div>
            </section>

            {/* How it works */}
            <section className="glass-panel" style={{ padding: '3rem 2rem', marginBottom: '4rem' }}>
                <h3 style={{ textAlign: 'center', fontSize: '1.8rem', marginBottom: '2.5rem' }}>
                    Quy trình sử dụng đơn giản
                </h3>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '2rem' }}>
                    <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '2.5rem', color: 'var(--primary-color)', fontWeight: '700', marginBottom: '1rem', fontFamily: 'Outfit' }}>01</div>
                        <h5 style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>
                            Tải ảnh toàn thân
                        </h5>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                            Khách hàng tải lên ảnh đứng thẳng, rõ dáng và đủ ánh sáng.
                        </p>
                    </div>

                    <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '2.5rem', color: 'var(--primary-color)', fontWeight: '700', marginBottom: '1rem', fontFamily: 'Outfit' }}>02</div>
                        <h5 style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>
                            Nhập thông tin cơ bản
                        </h5>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                            Người dùng nhập chiều cao, cân nặng, giới tính và thương hiệu cần chọn size.
                        </p>
                    </div>

                    <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '2.5rem', color: 'var(--primary-color)', fontWeight: '700', marginBottom: '1rem', fontFamily: 'Outfit' }}>03</div>
                        <h5 style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>
                            AI phân tích vóc dáng
                        </h5>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                            Hệ thống xử lý hình ảnh, ước lượng số đo và đối chiếu với bảng size.
                        </p>
                    </div>

                    <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '2.5rem', color: 'var(--primary-color)', fontWeight: '700', marginBottom: '1rem', fontFamily: 'Outfit' }}>04</div>
                        <h5 style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>
                            Nhận gợi ý size phù hợp
                        </h5>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                            Khách hàng nhận kết quả gợi ý size áo, quần hoặc cả bộ chỉ trong vài giây.
                        </p>
                    </div>
                </div>
            </section>

            {/* Integration Section */}
            <section style={{ marginBottom: '4rem' }}>
                <h3 style={{ textAlign: 'center', fontSize: '2rem', marginBottom: '2.5rem' }}>
                    Phù hợp cho cửa hàng online
                </h3>

                <div className="grid-3">
                    <div className="glass-panel flex-col" style={{ padding: '2rem' }}>
                        <div style={{ width: '50px', height: '50px', borderRadius: '12px', background: 'var(--gradient-1)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', marginBottom: '1rem' }}>
                            <ShieldCheck size={24} />
                        </div>
                        <h4 style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>
                            Giảm sai size khi mua hàng
                        </h4>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', lineHeight: '1.5' }}>
                            Hỗ trợ khách hàng chọn size chính xác hơn, hạn chế tình trạng mua nhầm size
                            và giảm chi phí đổi trả cho shop.
                        </p>
                    </div>

                    <div className="glass-panel flex-col" style={{ padding: '2rem' }}>
                        <div style={{ width: '50px', height: '50px', borderRadius: '12px', background: 'var(--gradient-2)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', marginBottom: '1rem' }}>
                            <Bot size={24} />
                        </div>
                        <h4 style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>
                            Tư vấn size tự động
                        </h4>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', lineHeight: '1.5' }}>
                            Thay vì tư vấn thủ công, shop có thể để FitVision AI hỗ trợ khách hàng
                            chọn size ngay trên website.
                        </p>
                    </div>

                    <div className="glass-panel flex-col" style={{ padding: '2rem' }}>
                        <div style={{ width: '50px', height: '50px', borderRadius: '12px', background: 'var(--gradient-gold)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', marginBottom: '1rem' }}>
                            <Zap size={24} />
                        </div>
                        <h4 style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>
                            Tích hợp qua mã API
                        </h4>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', lineHeight: '1.5' }}>
                            Doanh nghiệp có thể sử dụng mã API để kết nối FitVision AI với hệ thống
                            bán hàng, trang sản phẩm hoặc công cụ quản lý riêng.
                        </p>
                    </div>
                </div>
            </section>

            {/* Bottom Call-to-action */}
            <section style={{ textAlign: 'center', padding: '2rem 0' }}>
                <h3 style={{ fontSize: '1.8rem', marginBottom: '1rem' }}>
                    Sẵn sàng nâng cấp trải nghiệm chọn size?
                </h3>

                <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
                    Dùng thử FitVision AI ngay hôm nay để giúp khách hàng chọn đúng size nhanh hơn,
                    tự tin hơn và mua hàng dễ dàng hơn.
                </p>

                <button className="btn btn-primary" onClick={() => onNavigate('demo')}>
                    Trải nghiệm demo ngay
                </button>
            </section>
            {/* Footer */}
<footer className="glass-panel" style={{ padding: '2.5rem 2rem', marginTop: '4rem' }}>
    <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: '2rem',
        marginBottom: '2rem'
    }}>
        <div>
            <h3 style={{ color: 'var(--primary-color)', fontSize: '1.5rem', marginBottom: '0.75rem' }}>
                FitVision AI
            </h3>
            <p style={{ color: 'var(--text-secondary)', lineHeight: '1.6', fontSize: '0.95rem' }}>
                Giải pháp AI hỗ trợ đo cơ thể và gợi ý size quần áo cho cửa hàng online.
            </p>
        </div>

        <div>
            <h4 style={{ marginBottom: '0.75rem' }}>Sản phẩm</h4>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Gợi ý size bằng AI</p>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Mô phỏng cơ thể 3D</p>
            <p style={{ color: 'var(--text-secondary)' }}>API tích hợp website</p>
        </div>

        <div>
            <h4 style={{ marginBottom: '0.75rem' }}>Dành cho shop</h4>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Giảm đổi trả</p>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Tăng trải nghiệm mua hàng</p>
            <p style={{ color: 'var(--text-secondary)' }}>Tư vấn size tự động</p>
        </div>

        <div>
            <h4 style={{ marginBottom: '0.75rem' }}>Liên hệ</h4>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                Email: support@fitvision.ai
            </p>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                Website: fitvision.ai
            </p>
            <p style={{ color: 'var(--text-secondary)' }}>
                Việt Nam
            </p>
        </div>
    </div>

    <div style={{
        borderTop: '1px solid rgba(255,255,255,0.1)',
        paddingTop: '1.25rem',
        display: 'flex',
        justifyContent: 'space-between',
        gap: '1rem',
        flexWrap: 'wrap',
        color: 'var(--text-secondary)',
        fontSize: '0.9rem'
    }}>
        <span>© 2025 FitVision AI. All rights reserved.</span>
        <span>AI Size Recommendation Platform</span>
    </div>
</footer>
        </div>
    );
}