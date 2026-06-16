import React from 'react';
import { ArrowRight, Bot, Shirt, Layers, ShieldCheck, Zap } from 'lucide-react';

export default function LandingPage({ onNavigate }) {
    return (
        <div className="landing-page fade-in">
            <section className="landing-hero">
                <div className="landing-badge">
                    <Bot size={16} />
                    Công nghệ AI gợi ý size thông minh
                </div>

                <h2 className="hero-title">FitVision AI</h2>

                <h3 className="landing-hero-heading">
                    Giải pháp AI tự động đo cơ thể và gợi ý size quần áo cho cửa hàng online
                </h3>

                <p className="hero-subtitle">
                    FitVision AI giúp khách hàng chọn đúng size chỉ bằng một ảnh toàn thân,
                    chiều cao và cân nặng. Hệ thống phân tích vóc dáng, đề xuất size phù hợp
                    và hỗ trợ shop giảm tỷ lệ đổi trả khi bán hàng trực tuyến.
                </p>

                <div className="landing-hero-actions">
                    <button className="btn btn-primary" onClick={() => onNavigate('demo')}>
                        Trải nghiệm demo <ArrowRight size={18} />
                    </button>

                    <button className="btn btn-secondary" onClick={() => onNavigate('pricing')}>
                        Xem bảng giá
                    </button>
                </div>
            </section>

            <section className="landing-section compact">
                <div className="stats-grid">
                    <StatCard value="+32%" label="Tăng tỷ lệ chuyển đổi" />
                    <StatCard value="-45%" label="Giảm tỷ lệ đổi trả" />
                    <StatCard value="95%" label="Khách hàng hài lòng với gợi ý size" />
                </div>
            </section>

            <section className="landing-section">
                <h3 className="landing-section-title">Tính năng nổi bật</h3>

                <div className="grid-3">
                    <FeatureCard
                        icon={<Shirt size={24} />}
                        gradient="var(--gradient-1)"
                        title="Nhận diện vóc dáng bằng AI"
                        text="Phân tích ảnh toàn thân để nhận diện các điểm quan trọng trên cơ thể, từ đó ước lượng số đo và đưa ra khuyến nghị size phù hợp."
                    />

                    <FeatureCard
                        icon={<Layers size={24} />}
                        gradient="var(--gradient-2)"
                        title="Mô phỏng cơ thể 3D"
                        text="Hiển thị mô hình cơ thể trực quan dựa trên số đo ước lượng, giúp khách hàng dễ hình dung vóc dáng và tự tin hơn khi chọn size."
                    />

                    <FeatureCard
                        icon={<Zap size={24} />}
                        gradient="var(--gradient-gold)"
                        title="Dễ dàng tích hợp vào website"
                        text="Tích hợp FitVision AI vào website bán hàng thông qua Widget hoặc API, phù hợp với các cửa hàng online và nền tảng thương mại điện tử."
                    />
                </div>
            </section>

            <section className="glass-panel landing-section how-it-works">
                <h3 className="landing-section-title">Quy trình sử dụng đơn giản</h3>

                <div className="how-grid">
                    <StepCard number="01" title="Tải ảnh toàn thân" text="Khách hàng tải lên ảnh đứng thẳng, rõ dáng và đủ ánh sáng." />
                    <StepCard number="02" title="Nhập thông tin cơ bản" text="Người dùng nhập chiều cao, cân nặng, giới tính và thương hiệu cần chọn size." />
                    <StepCard number="03" title="AI phân tích vóc dáng" text="Hệ thống xử lý hình ảnh, ước lượng số đo và đối chiếu với bảng size." />
                    <StepCard number="04" title="Nhận gợi ý size phù hợp" text="Khách hàng nhận kết quả gợi ý size áo, quần hoặc cả bộ chỉ trong vài giây." />
                </div>
            </section>

            <section className="landing-section">
                <h3 className="landing-section-title">Phù hợp cho cửa hàng online</h3>

                <div className="grid-3">
                    <FeatureCard
                        icon={<ShieldCheck size={24} />}
                        gradient="var(--gradient-1)"
                        title="Giảm sai size khi mua hàng"
                        text="Hỗ trợ khách hàng chọn size chính xác hơn, hạn chế tình trạng mua nhầm size và giảm chi phí đổi trả cho shop."
                    />

                    <FeatureCard
                        icon={<Bot size={24} />}
                        gradient="var(--gradient-2)"
                        title="Tư vấn size tự động"
                        text="Thay vì tư vấn thủ công, shop có thể để FitVision AI hỗ trợ khách hàng chọn size ngay trên website."
                    />

                    <FeatureCard
                        icon={<Zap size={24} />}
                        gradient="var(--gradient-gold)"
                        title="Tích hợp qua mã API"
                        text="Doanh nghiệp có thể sử dụng mã API để kết nối FitVision AI với hệ thống bán hàng, trang sản phẩm hoặc công cụ quản lý riêng."
                    />
                </div>
            </section>

            <section className="landing-cta">
                <h3>Sẵn sàng nâng cấp trải nghiệm chọn size?</h3>

                <p>
                    Dùng thử FitVision AI ngay hôm nay để giúp khách hàng chọn đúng size nhanh hơn,
                    tự tin hơn và mua hàng dễ dàng hơn.
                </p>

                <button className="btn btn-primary" onClick={() => onNavigate('demo')}>
                    Trải nghiệm demo ngay
                </button>
            </section>

            <footer className="glass-panel landing-footer">
                <div className="landing-footer-grid">
                    <div>
                        <h3 className="footer-brand">FitVision AI</h3>
                        <p>
                            Giải pháp AI hỗ trợ đo cơ thể và gợi ý size quần áo cho cửa hàng online.
                        </p>
                    </div>

                    <FooterColumn
                        title="Sản phẩm"
                        items={['Gợi ý size bằng AI', 'Mô phỏng cơ thể 3D', 'API tích hợp website']}
                    />

                    <FooterColumn
                        title="Dành cho shop"
                        items={['Giảm đổi trả', 'Tăng trải nghiệm mua hàng', 'Tư vấn size tự động']}
                    />

                    <FooterColumn
                        title="Liên hệ"
                        items={['Email: support@fitvision.ai', 'Website: fitvision.ai', 'Việt Nam']}
                    />
                </div>

                <div className="landing-footer-bottom">
                    <span>© 2025 FitVision AI. All rights reserved.</span>
                    <span>AI Size Recommendation Platform</span>
                </div>
            </footer>
        </div>
    );
}

function StatCard({ value, label }) {
    return (
        <div className="glass-panel stat-card">
            <div className="stat-val">{value}</div>
            <div className="stat-label">{label}</div>
        </div>
    );
}

function FeatureCard({ icon, gradient, title, text }) {
    return (
        <div className="glass-panel feature-card">
            <div className="feature-icon" style={{ background: gradient }}>
                {icon}
            </div>

            <h4>{title}</h4>
            <p>{text}</p>
        </div>
    );
}

function StepCard({ number, title, text }) {
    return (
        <div className="step-card">
            <div className="step-number">{number}</div>
            <h5>{title}</h5>
            <p>{text}</p>
        </div>
    );
}

function FooterColumn({ title, items }) {
    return (
        <div>
            <h4>{title}</h4>
            {items.map((item) => (
                <p key={item}>{item}</p>
            ))}
        </div>
    );
}