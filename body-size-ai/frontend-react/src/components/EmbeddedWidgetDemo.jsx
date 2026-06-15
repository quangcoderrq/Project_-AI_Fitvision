import React, { useState } from 'react';
import { Sparkles, Sliders, UserCheck, RefreshCw, Loader2 } from 'lucide-react';
import ImageUploader from './ImageUploader';
import FormControls from './FormControls';
import ResultsDisplay from './ResultsDisplay';
import Body3DViewer from './Body3DViewer';
import { predictSize } from '../api';

export default function EmbeddedWidgetDemo({ apiToken, brandsData }) {
    // Customizer State
    const [btnText, setBtnText] = useState('Gợi ý size bằng AI');
    const [btnColor, setBtnColor] = useState('#3b82f6');
    const [borderRadius, setBorderRadius] = useState('12');
    const [showSparkles, setShowSparkles] = useState(true);

    // Widget Sandbox State
    const [isWidgetOpen, setIsWidgetOpen] = useState(false);
    const [selectedSize, setSelectedSize] = useState(null);
    
    // AI widget runner state
    const [image, setImage] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [result, setResult] = useState(null);
    const [is3DOpen, setIs3DOpen] = useState(false);
    const [formData, setFormData] = useState({
        height: 170,
        weight: 65,
        gender: 'male',
        brand: 'uniqlo',
        region: 'asia',
        garmentType: 'shirt' // product is a shirt
    });

    const handlePredict = async () => {
        if (!image) {
            setError('Vui lòng chọn ảnh.');
            return;
        }
        setIsLoading(true);
        setError(null);
        setResult(null);

        const payload = {
            ...formData,
            image_type: 'upper', // product is a shirt
            ignore_baggy_warning: true,
            image: image.split(',')[1] // remove data URL prefix
        };

        const res = await predictSize(payload);
        setIsLoading(false);

        if (res.success) {
            setResult(res);
            // Apply recommended size to the product option
            if (res.shirt_size && res.shirt_size.recommended_size) {
                setSelectedSize(res.shirt_size.recommended_size);
            } else if (res.predicted_size) {
                setSelectedSize(res.predicted_size);
            }
        } else {
            setError(res.error || 'Có lỗi xảy ra khi gọi API');
        }
    };

    return (
        <div className="grid-2 fade-in" style={{ gap: '2rem', marginTop: '1rem' }}>
            
            {/* Left Column: Customizer */}
            <div className="glass-panel flex-col">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', borderBottom: '1px solid var(--glass-border)', paddingBottom: '1rem' }}>
                    <Sliders size={20} style={{ color: 'var(--primary-color)' }} />
                    <h3 style={{ fontSize: '1.25rem' }}>Trình Tùy Biến Widget</h3>
                </div>

                {/* Customizer controls */}
                <div className="input-group">
                    <label className="input-label">Nội dung văn bản trên nút</label>
                    <input 
                        type="text" 
                        className="glass-input" 
                        value={btnText}
                        onChange={(e) => setBtnText(e.target.value)}
                    />
                </div>

                <div className="input-group">
                    <label className="input-label">Màu sắc chủ đạo (Brand Color)</label>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                        {['#3b82f6', '#10b981', '#ec4899', '#0f172a', '#f59e0b'].map((color) => (
                            <button
                                key={color}
                                type="button"
                                style={{ width: '32px', height: '32px', borderRadius: '50%', background: color, border: btnColor === color ? '2px solid var(--text-primary)' : 'none', cursor: 'pointer', outline: 'none' }}
                                onClick={() => setBtnColor(color)}
                            />
                        ))}
                        <input 
                            type="color" 
                            style={{ width: '32px', height: '32px', border: 'none', background: 'transparent', cursor: 'pointer' }}
                            value={btnColor}
                            onChange={(e) => setBtnColor(e.target.value)}
                        />
                    </div>
                </div>

                <div className="input-group">
                    <label className="input-label">Độ bo góc nút (Border Radius: {borderRadius}px)</label>
                    <input 
                        type="range" 
                        min="0" 
                        max="24" 
                        className="glass-input"
                        style={{ padding: '0' }}
                        value={borderRadius}
                        onChange={(e) => setBorderRadius(e.target.value)}
                    />
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.5rem' }}>
                    <input 
                        type="checkbox" 
                        id="showSparkles"
                        checked={showSparkles}
                        onChange={(e) => setShowSparkles(e.target.checked)}
                        style={{ width: '18px', height: '18px', cursor: 'pointer' }}
                    />
                    <label htmlFor="showSparkles" className="input-label" style={{ margin: '0', cursor: 'pointer', userSelect: 'none' }}>
                        Hiển thị Icon AI lấp lánh (Sparkles)
                    </label>
                </div>

                <div style={{ background: 'rgba(59, 130, 246, 0.06)', border: '1px solid rgba(59, 130, 246, 0.15)', padding: '1rem', borderRadius: '12px', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                    💡 <strong>Mẹo:</strong> Thiết lập token của bạn để kết nối widget trực tiếp với mô hình AI học máy của FitVision. Mã nhúng HTML ở tab tích hợp sẽ tự động đồng bộ các tùy chỉnh này!
                </div>
            </div>

            {/* Right Column: E-commerce Product Page Preview */}
            <div className="flex-col">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <h4 style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>Cửa hàng giả lập (E-Commerce Sandbox)</h4>
                    <span style={{ fontSize: '0.75rem', color: 'var(--success-color)', background: 'rgba(16, 185, 129, 0.1)', padding: '0.2rem 0.5rem', borderRadius: '4px', fontFamily: 'monospace' }}>
                        Token: {apiToken.slice(0, 10)}...
                    </span>
                </div>

                <div className="sandbox-product">
                    {/* Product Gallery Mockup */}
                    <div className="sandbox-gallery">
                        👕
                    </div>

                    {/* Product Details Mockup */}
                    <div className="sandbox-details">
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 'bold' }}>Uniqlo Collection</div>
                        <h3 style={{ fontSize: '1.4rem' }}>Áo Thun Cotton Oversized Unisex</h3>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <span style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'var(--primary-color)' }}>$39.00</span>
                            <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)', textDecoration: 'line-through' }}>$49.00</span>
                        </div>
                        
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', lineHeight: '1.4' }}>
                            Chất liệu vải Supima cotton cao cấp cực mát, bền đẹp và giữ form sau nhiều lần giặt. Kiểu dáng thời thượng phù hợp cho cả nam và nữ.
                        </p>

                        <hr style={{ border: 'none', borderTop: '1px solid var(--glass-border)', margin: '0.5rem 0' }} />

                        {/* Sizing selection */}
                        <div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                <span style={{ fontSize: '0.85rem', fontWeight: '600' }}>Kích cỡ:</span>
                                {selectedSize && (
                                    <span style={{ fontSize: '0.85rem', color: 'var(--success-color)', fontWeight: 'bold' }}>
                                        Đã chọn size gợi ý: {selectedSize}
                                    </span>
                                )}
                            </div>
                            <div style={{ display: 'flex', gap: '0.5rem' }}>
                                {['XS', 'S', 'M', 'L', 'XL'].map((size) => (
                                    <button
                                        key={size}
                                        type="button"
                                        style={{ width: '40px', height: '40px', borderRadius: '8px', border: selectedSize === size ? '2px solid var(--primary-color)' : '1px solid var(--glass-border)', background: selectedSize === size ? 'var(--primary-glow)' : 'transparent', color: selectedSize === size ? 'var(--primary-color)' : 'var(--text-primary)', fontWeight: 'bold', cursor: 'pointer' }}
                                        onClick={() => setSelectedSize(size)}
                                    >
                                        {size}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* FITVISION AI WIDGET BUTTON */}
                        <div style={{ margin: '0.75rem 0' }}>
                            <button
                                className="sandbox-btn-fit"
                                style={{
                                    backgroundColor: btnColor,
                                    color: 'white',
                                    borderRadius: `${borderRadius}px`,
                                    width: '100%'
                                }}
                                onClick={() => setIsWidgetOpen(true)}
                            >
                                {showSparkles && <Sparkles size={16} fill="white" />}
                                {btnText}
                            </button>
                        </div>

                        <button 
                            className="btn btn-secondary" 
                            style={{ width: '100%', borderStyle: 'dashed' }}
                            disabled
                        >
                            Thêm vào giỏ hàng
                        </button>
                    </div>
                </div>
            </div>

            {/* AI Recommendation Widget Modal (Simulated Embed) */}
            {isWidgetOpen && (
                <div className="modal-overlay" style={{ zIndex: 200, padding: '1rem' }}>
                    <style>{`
                        .fit-widget-modal {
                            width: min(760px, calc(100vw - 2rem));
                            border-radius: 22px;
                        }
                        .fit-widget-body-grid {
                            display: grid;
                            grid-template-columns: minmax(300px, 1.15fr) minmax(260px, 0.85fr);
                            gap: 1.25rem;
                            align-items: stretch;
                        }
                        .fit-widget-upload-panel,
                        .fit-widget-form-panel {
                            min-width: 0;
                        }
                        .fit-widget-form-panel {
                            background: rgba(15, 23, 42, 0.18);
                            border: 1px solid var(--glass-border);
                            border-radius: 20px;
                            padding: 1.25rem;
                        }
                        .fit-widget-form-panel .input-group {
                            margin-bottom: 1rem;
                        }
                        .fit-widget-form-panel input,
                        .fit-widget-form-panel select,
                        .fit-widget-form-panel button {
                            max-width: 100%;
                        }
                        .fit-widget-submit {
                            min-height: 52px;
                            border-radius: 14px;
                            font-weight: 800;
                            box-shadow: 0 14px 32px rgba(245, 158, 11, 0.22);
                        }
                        @media (max-width: 760px) {
                            .fit-widget-body-grid {
                                grid-template-columns: 1fr;
                            }
                            .fit-widget-modal {
                                padding: 1rem !important;
                            }
                        }
                    `}</style>
                    <div className="glass-panel modal-content fit-widget-modal" style={{ maxWidth: '760px', padding: '1.75rem', maxHeight: '90vh', overflowY: 'auto' }}>
                        
                        {/* Header */}
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', borderBottom: '1px solid var(--glass-border)', paddingBottom: '0.9rem' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                <Sparkles size={18} style={{ color: btnColor }} />
                                <h3 style={{ fontSize: '1.25rem', lineHeight: 1.25, margin: 0 }}>Gợi ý Size bằng Trí tuệ Nhân tạo</h3>
                            </div>
                            <button 
                                onClick={() => setIsWidgetOpen(false)}
                                style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', padding: '0.35rem', borderRadius: '10px' }}
                            >
                                <X size={20} />
                            </button>
                        </div>

                        {/* Content */}
                        {!result ? (
                            <div className="flex-col" style={{ gap: '1.25rem' }}>
                                <div className="fit-widget-body-grid">
                                    <div className="fit-widget-upload-panel flex-col">
                                        <ImageUploader image={image} setImage={setImage} />
                                    </div>
                                    <div className="fit-widget-form-panel flex-col">
                                        <FormControls formData={formData} setFormData={setFormData} brandsData={brandsData} hideGarmentType={true} />
                                    </div>
                                </div>

                                {error && (
                                    <div style={{ color: 'var(--error-color)', padding: '0.5rem', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '8px', fontSize: '0.9rem' }}>
                                        {error}
                                    </div>
                                )}

                                <button
                                    className="btn btn-primary fit-widget-submit"
                                    style={{ backgroundColor: btnColor, width: '100%', marginTop: '0.25rem' }}
                                    onClick={handlePredict}
                                    disabled={isLoading}
                                >
                                    {isLoading ? (
                                        <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                            <Loader2 size={16} className="spinner" /> AI Đang Tính Toán...
                                        </span>
                                    ) : (
                                        'Phân Tích & Tính Toán Size'
                                    )}
                                </button>
                            </div>
                        ) : (
                            <div className="flex-col fade-in">
                                <ResultsDisplay 
                                    result={result} 
                                    garmentType="shirt" 
                                    onView3D={() => setIs3DOpen(true)}
                                />
                                
                                <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                                    <button 
                                        className="btn btn-primary"
                                        style={{ backgroundColor: btnColor, flex: 1 }}
                                        onClick={() => {
                                            setIsWidgetOpen(false);
                                            setResult(null);
                                            setImage(null);
                                        }}
                                    >
                                        <UserCheck size={18} /> Áp dụng Size gợi ý
                                    </button>
                                    <button 
                                        className="btn btn-secondary"
                                        onClick={() => {
                                            setResult(null);
                                            setImage(null);
                                        }}
                                    >
                                        <RefreshCw size={16} /> Đo lại
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* 3D Body Viewer */}
            <Body3DViewer 
                isOpen={is3DOpen}
                onClose={() => setIs3DOpen(false)}
                gender={formData.gender}
                measurements={result ? { ...result.measurements, height_cm: formData.height, weight_kg: formData.weight } : null}
            />

        </div>
    );
}

// Simple local SVG Close button
function X({ size, ...props }) {
    return (
        <svg xmlns="http://www.w3.org/2000/svg" width={size || 24} height={size || 24} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
    );
}
