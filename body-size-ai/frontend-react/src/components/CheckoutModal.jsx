import React, { useState } from 'react';
import { CreditCard, QrCode, X, CheckCircle2, ShieldCheck, Loader2 } from 'lucide-react';

export default function CheckoutModal({ isOpen, onClose, planName, planPrice, onPaymentSuccess }) {
    const [activeTab, setActiveTab] = useState('card');
    const [isProcessing, setIsProcessing] = useState(false);
    const [isSuccess, setIsSuccess] = useState(false);
    
    // Card inputs
    const [cardData, setCardData] = useState({
        number: '4111 2222 3333 4444',
        name: 'NGUYEN VAN A',
        expiry: '12/28',
        cvv: '123'
    });

    if (!isOpen) return null;

    const handlePayment = (e) => {
        e.preventDefault();
        setIsProcessing(true);
        
        // Simulate payment call delay
        setTimeout(() => {
            setIsProcessing(false);
            setIsSuccess(true);
        }, 1500);
    };

    const handleSuccessClose = () => {
        onPaymentSuccess(planName);
        setIsSuccess(false);
        onClose();
    };

    return (
        <div className="modal-overlay">
            <div className="glass-panel modal-content" style={{ position: 'relative', overflow: 'hidden' }}>
                
                {/* Close Button */}
                {!isProcessing && !isSuccess && (
                    <button 
                        onClick={onClose}
                        style={{ position: 'absolute', top: '1.25rem', right: '1.25rem', background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}
                    >
                        <X size={20} />
                    </button>
                )}

                {/* Processing State */}
                {isProcessing && (
                    <div style={{ textAlign: 'center', padding: '3rem 1rem' }} className="flex-col">
                        <div style={{ display: 'flex', justifyContent: 'center' }}>
                            <Loader2 size={48} className="spinner" style={{ color: 'var(--primary-color)' }} />
                        </div>
                        <h3 style={{ fontSize: '1.5rem', marginTop: '1rem' }}>Đang xác thực thanh toán...</h3>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                            Vui lòng không đóng trình duyệt hoặc tải lại trang.
                        </p>
                    </div>
                )}

                {/* Success State */}
                {isSuccess && (
                    <div style={{ textAlign: 'center', padding: '2.5rem 1rem' }} className="flex-col">
                        <div style={{ display: 'flex', justifyContent: 'center', color: 'var(--success-color)' }}>
                            <CheckCircle2 size={64} />
                        </div>
                        <h3 style={{ fontSize: '1.75rem', marginTop: '1rem', color: 'var(--text-primary)' }}>Thanh toán thành công!</h3>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
                            Gói <strong>{planName}</strong> ({planPrice}) của bạn đã được kích hoạt. API Token của bạn đã sẵn sàng sử dụng.
                        </p>
                        <button 
                            className="btn btn-primary" 
                            style={{ width: '100%', marginTop: '1.5rem' }}
                            onClick={handleSuccessClose}
                        >
                            Đến Dashboard lập trình viên
                        </button>
                    </div>
                )}

                {/* Main Payment Form */}
                {!isProcessing && !isSuccess && (
                    <div>
                        <h3 style={{ fontSize: '1.5rem', marginBottom: '0.25rem' }}>Thanh toán</h3>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
                            Đăng ký gói: <strong>{planName}</strong> — <strong>{planPrice}</strong>
                        </p>

                        {/* Tabs */}
                        <div className="payment-tab-buttons">
                            <button 
                                className={`payment-tab ${activeTab === 'card' ? 'active' : ''}`}
                                onClick={() => setActiveTab('card')}
                                type="button"
                            >
                                <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', justifyContent: 'center' }}>
                                    <CreditCard size={16} /> Thẻ tín dụng
                                </span>
                            </button>
                            <button 
                                className={`payment-tab ${activeTab === 'qr' ? 'active' : ''}`}
                                onClick={() => setActiveTab('qr')}
                                type="button"
                            >
                                <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', justifyContent: 'center' }}>
                                    <QrCode size={16} /> Chuyển khoản QR
                                </span>
                            </button>
                        </div>

                        <form onSubmit={handlePayment}>
                            {/* Card Form */}
                            {activeTab === 'card' && (
                                <div className="fade-in">
                                    {/* Virtual Card View */}
                                    <div className="credit-card-mockup">
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                            <span style={{ fontSize: '1.1rem', fontWeight: 'bold', fontFamily: 'Outfit', letterSpacing: '1px' }}>FITVISION</span>
                                            <span style={{ fontSize: '0.8rem', color: '#cbd5e1' }}>CREDIT CARD</span>
                                        </div>
                                        <div style={{ fontSize: '1.3rem', letterSpacing: '3px', fontFamily: 'monospace', margin: '1rem 0' }}>
                                            {cardData.number || '•••• •••• •••• ••••'}
                                        </div>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
                                            <div>
                                                <div style={{ color: '#94a3b8', fontSize: '0.6rem' }}>CARD HOLDER</div>
                                                <div style={{ fontWeight: '600' }}>{cardData.name || 'FULL NAME'}</div>
                                            </div>
                                            <div>
                                                <div style={{ color: '#94a3b8', fontSize: '0.6rem' }}>EXPIRES</div>
                                                <div style={{ fontWeight: '600' }}>{cardData.expiry || 'MM/YY'}</div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Input Fields */}
                                    <div className="input-group">
                                        <label className="input-label">Số thẻ</label>
                                        <input 
                                            type="text" 
                                            className="glass-input" 
                                            value={cardData.number}
                                            onChange={(e) => setCardData(prev => ({ ...prev, number: e.target.value }))}
                                            required
                                        />
                                    </div>
                                    <div className="input-group">
                                        <label className="input-label">Tên chủ thẻ</label>
                                        <input 
                                            type="text" 
                                            className="glass-input" 
                                            value={cardData.name}
                                            onChange={(e) => setCardData(prev => ({ ...prev, name: e.target.value.toUpperCase() }))}
                                            required
                                        />
                                    </div>
                                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                                        <div className="input-group">
                                            <label className="input-label">Hạn sử dụng</label>
                                            <input 
                                                type="text" 
                                                className="glass-input" 
                                                placeholder="MM/YY"
                                                value={cardData.expiry}
                                                onChange={(e) => setCardData(prev => ({ ...prev, expiry: e.target.value }))}
                                                required
                                            />
                                        </div>
                                        <div className="input-group">
                                            <label className="input-label">CVV/CVC</label>
                                            <input 
                                                type="password" 
                                                className="glass-input" 
                                                maxLength="3"
                                                value={cardData.cvv}
                                                onChange={(e) => setCardData(prev => ({ ...prev, cvv: e.target.value }))}
                                                required
                                            />
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* QR Transfer Form */}
                            {activeTab === 'qr' && (
                                <div className="qr-container fade-in">
                                    <div className="qr-box">
                                        {/* Standard mockup QR code using SVG or CSS to avoid broken links */}
                                        <svg width="150" height="150" viewBox="0 0 150 150" xmlns="http://www.w3.org/2000/svg">
                                            <rect width="150" height="150" fill="white"/>
                                            {/* Outer borders */}
                                            <rect x="10" y="10" width="30" height="30" fill="black"/>
                                            <rect x="15" y="15" width="20" height="20" fill="white"/>
                                            <rect x="20" y="20" width="10" height="10" fill="black"/>

                                            <rect x="110" y="10" width="30" height="30" fill="black"/>
                                            <rect x="115" y="15" width="20" height="20" fill="white"/>
                                            <rect x="120" y="120" width="10" height="10" fill="black"/>

                                            <rect x="10" y="110" width="30" height="30" fill="black"/>
                                            <rect x="15" y="115" width="20" height="20" fill="white"/>
                                            <rect x="20" y="120" width="10" height="10" fill="black"/>
                                            
                                            <rect x="110" y="110" width="30" height="30" fill="black"/>
                                            <rect x="115" y="115" width="20" height="20" fill="white"/>
                                            
                                            {/* Random QR code pixels */}
                                            <rect x="50" y="20" width="10" height="20" fill="black"/>
                                            <rect x="70" y="10" width="20" height="10" fill="black"/>
                                            <rect x="50" y="50" width="30" height="10" fill="black"/>
                                            <rect x="90" y="40" width="10" height="30" fill="black"/>
                                            <rect x="20" y="60" width="20" height="20" fill="black"/>
                                            <rect x="60" y="80" width="15" height="15" fill="black"/>
                                            <rect x="10" y="90" width="10" height="10" fill="black"/>
                                            <rect x="80" y="90" width="30" height="10" fill="black"/>
                                            <rect x="90" y="110" width="10" height="20" fill="black"/>
                                            <rect x="50" y="110" width="20" height="30" fill="black"/>
                                            <rect x="120" y="70" width="20" height="10" fill="black"/>
                                            <rect x="130" y="90" width="10" height="20" fill="black"/>
                                        </svg>
                                    </div>
                                    <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', textAlign: 'left', width: '100%', background: 'rgba(0,0,0,0.02)', padding: '0.75rem', borderRadius: '8px' }}>
                                        <div>🏦 Ngân hàng: <strong>Techcombank (TCB)</strong></div>
                                        <div>👤 Tên tài khoản: <strong>CONG TY FITVISION AI</strong></div>
                                        <div>🔢 Số tài khoản: <strong>1903 5688 9999</strong></div>
                                        <div>📝 Nội dung chuyển khoản: <strong>FITVISION {planName.toUpperCase()} 4281</strong></div>
                                    </div>
                                    <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                                        * Hệ thống sẽ tự động quét trạng thái giao dịch sau khi nhận được chuyển khoản.
                                    </p>
                                </div>
                            )}

                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', margin: '1rem 0', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                                <ShieldCheck size={16} style={{ color: 'var(--success-color)' }} />
                                Kết nối bảo mật chuẩn SSL 256-bit.
                            </div>

                            <button 
                                className="btn btn-primary" 
                                style={{ width: '100%' }}
                                type="submit"
                            >
                                Xác nhận thanh toán ({planPrice})
                            </button>
                        </form>
                    </div>
                )}

            </div>
        </div>
    );
}
