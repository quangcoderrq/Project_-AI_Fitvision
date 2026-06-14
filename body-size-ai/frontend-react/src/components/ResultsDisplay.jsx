import React from 'react';
import { CheckCircle, AlertCircle, ShoppingBag, Eye } from 'lucide-react';

export default function ResultsDisplay({ result, garmentType, onView3D }) {
    if (!result) return null;

    const renderSizeCard = (title, sizeData, defaultSize, icon) => {
        const size = sizeData?.recommended_size || defaultSize;
        const confidence = sizeData ? Math.round(sizeData.confidence * 100) : Math.round(result.confidence * 100);
        const reason = sizeData?.reason;
        const altSizes = sizeData?.alternative_sizes || [];

        return (
            <div className="glass-panel" style={{ flex: 1, textAlign: 'center', background: 'rgba(255,255,255,0.02)' }}>
                <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>{icon}</div>
                <h4 style={{ color: 'var(--text-secondary)' }}>{title}</h4>
                <div style={{ fontSize: '3rem', fontWeight: 700, color: 'var(--primary-color)', margin: '0.5rem 0' }}>{size || '-'}</div>
                <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Độ tin cậy: {confidence}%</div>
                {reason && <div style={{ fontSize: '0.85rem', color: 'var(--warning-color)', marginTop: '0.5rem' }}>{reason}</div>}
                
                {altSizes.length > 0 && (
                    <div style={{ marginTop: '1rem' }}>
                        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Size thay thế: </span>
                        {altSizes.map(s => (
                            <span key={s} style={{ 
                                display: 'inline-block', padding: '2px 8px', margin: '0 2px', 
                                background: 'rgba(255,255,255,0.1)', borderRadius: '10px', fontSize: '0.8rem' 
                            }}>{s}</span>
                        ))}
                    </div>
                )}
            </div>
        );
    };

    const showShirt = garmentType === 'both' || garmentType === 'shirt';
    const showPants = garmentType === 'both' || garmentType === 'pants';

    return (
        <div className="fade-in">
            <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
                {showShirt && renderSizeCard('Size Áo', result.shirt_size, result.predicted_size, '👕')}
                {showPants && renderSizeCard('Size Quần', result.pants_size, result.predicted_size, '👖')}
            </div>

            <button className="btn btn-primary" style={{ width: '100%', marginBottom: '1rem', background: 'var(--success-color)' }}>
                <ShoppingBag size={20} /> Áp dụng Size vào Giỏ hàng
            </button>

            <button className="btn btn-secondary" style={{ width: '100%', marginBottom: '2rem' }} onClick={onView3D}>
                <Eye size={20} /> Xem mô hình 3D
            </button>

            {result.measurements && (
                <div className="glass-panel">
                    <h4 style={{ marginBottom: '1rem', borderBottom: '1px solid var(--glass-border)', paddingBottom: '0.5rem' }}>📏 Số đo dự đoán</h4>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(100px, 1fr))', gap: '1rem' }}>
                        {Object.entries(result.measurements).map(([key, value]) => (
                            <div key={key} style={{ textAlign: 'center' }}>
                                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'capitalize' }}>
                                    {key.replace('_cm', '').replace('_circumference', '').replace('_width', '')}
                                </div>
                                <div style={{ fontWeight: 600 }}>{value > 0 ? `${value.toFixed(1)} cm` : '-'}</div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
