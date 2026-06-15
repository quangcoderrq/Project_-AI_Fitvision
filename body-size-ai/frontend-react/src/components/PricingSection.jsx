import React from 'react';
import { Check, Flame } from 'lucide-react';

const PLANS = [
    {
        name: 'Starter',
        price: '$29',
        period: '/tháng',
        desc: 'Phù hợp cho các shop thời trang nhỏ mới bắt đầu tối ưu hóa việc chọn size.',
        features: [
            'Tối đa 2,000 lượt gọi API / tháng',
            'Tích hợp widget tiêu chuẩn',
            'Xem mô hình 3D cơ bản',
            'Báo cáo thống kê cơ bản',
            'Hỗ trợ qua email (phản hồi trong 48h)'
        ],
        isPopular: false,
        buttonText: 'Chọn gói Starter'
    },
    {
        name: 'Professional',
        price: '$79',
        period: '/tháng',
        desc: 'Lựa chọn tốt nhất cho các thương hiệu thời trang đang phát triển mạnh mẽ.',
        features: [
            'Tối đa 10,000 lượt gọi API / tháng',
            'Trình tùy biến Widget (đổi màu, text)',
            'Xem mô hình 3D nâng cao sắc nét',
            'Báo cáo Analytics chi tiết (tỷ lệ đổi trả)',
            'Hỗ trợ kỹ thuật 24/7 qua chat & email'
        ],
        isPopular: true,
        buttonText: 'Đăng ký gói Pro'
    },
    {
        name: 'Enterprise',
        price: '$249',
        period: '/tháng',
        desc: 'Dành cho các sàn thương mại điện tử lớn cần hiệu năng cao và tùy biến sâu.',
        features: [
            'Không giới hạn lượt gọi API',
            'White-label (tùy biến giao diện & xóa logo)',
            'Tích hợp sâu API vào hệ thống ERP/Kho hàng',
            'Máy chủ AI riêng biệt (Phản hồi < 0.5s)',
            'Kỹ sư hỗ trợ tích hợp trực tiếp tận nơi'
        ],
        isPopular: false,
        buttonText: 'Liên hệ Enterprise'
    }
];

export default function PricingSection({ onSelectPlan }) {
    return (
        <div className="fade-in" style={{ padding: '2rem 0 4rem 0' }}>
            <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
                <h2 style={{ fontSize: '2.5rem', marginBottom: '1rem', background: 'var(--gradient-1)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                    Bảng Giá Dịch Vụ
                </h2>
                <p style={{ color: 'var(--text-secondary)', maxWidth: '600px', margin: '0 auto', fontSize: '1.05rem', lineHeight: '1.5' }}>
                    Chọn gói cước phù hợp với quy mô kinh doanh của bạn. Nâng cấp hoặc hủy gói bất cứ lúc nào một cách nhanh chóng.
                </p>
            </div>

            <div className="grid-3">
                {PLANS.map((plan) => (
                    <div 
                        key={plan.name} 
                        className={`glass-panel pricing-card ${plan.isPopular ? 'popular' : ''}`}
                        style={{ display: 'flex', flexDirection: 'column', height: '100%', justifyContent: 'space-between' }}
                    >
                        {plan.isPopular && (
                            <div className="popular-badge flex-row" style={{ alignItems: 'center', gap: '0.2rem' }}>
                                <Flame size={12} fill="white" /> Phổ biến nhất
                            </div>
                        )}
                        
                        <div>
                            <h3 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>{plan.name}</h3>
                            <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', minHeight: '45px', marginBottom: '1rem' }}>
                                {plan.desc}
                            </p>
                            
                            <div className="price-box">
                                <span className="price-amount">{plan.price}</span>
                                <span className="price-period">{plan.period}</span>
                            </div>
                            
                            <hr style={{ border: 'none', borderTop: '1px solid var(--glass-border)', margin: '1.5rem 0' }} />
                            
                            <ul className="features-list">
                                {plan.features.map((feat, i) => (
                                    <li key={i} className="feature-item">
                                        <div style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', width: '20px', height: '20px', borderRadius: '50%', background: plan.isPopular ? 'rgba(59, 130, 246, 0.15)' : 'var(--glass-border)', color: 'var(--primary-color)', flexShrink: 0 }}>
                                            <Check size={12} strokeWidth={3} />
                                        </div>
                                        <span>{feat}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                        
                        <button 
                            className={`btn ${plan.isPopular ? 'btn-primary' : 'btn-secondary'}`} 
                            style={{ width: '100%' }}
                            onClick={() => onSelectPlan(plan.name, plan.price)}
                        >
                            {plan.buttonText}
                        </button>
                    </div>
                ))}
            </div>
            
            <div className="glass-panel" style={{ marginTop: '3rem', textAlign: 'center', padding: '2rem' }}>
                <h4 style={{ fontSize: '1.25rem', marginBottom: '0.5rem' }}>💡 Bạn cần một giải pháp thiết kế riêng biệt?</h4>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', marginBottom: '1rem' }}>
                    Chúng tôi cung cấp các tùy chọn nhúng, hỗ trợ setup từ xa cho các nền tảng thương mại điện tử đặc thù.
                </p>
                <button className="btn btn-secondary" onClick={() => onSelectPlan('Custom Enterprise', 'Custom Price')}>
                    Gửi yêu cầu tư vấn
                </button>
            </div>
        </div>
    );
}
