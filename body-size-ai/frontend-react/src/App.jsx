import React, { useState, useEffect } from 'react';
import { Moon, Sun } from 'lucide-react';
import { fetchBrands, predictSize } from './api';
import FormControls from './components/FormControls';
import DynamicGuide from './components/DynamicGuide';
import ImageUploader from './components/ImageUploader';
import ResultsDisplay from './components/ResultsDisplay';
import BaggyWarningModal from './components/BaggyWarningModal';
import Body3DViewer from './components/Body3DViewer';

export default function App() {
    const [theme, setTheme] = useState('dark');
    const [brandsData, setBrandsData] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [result, setResult] = useState(null);
    const [image, setImage] = useState(null);
    const [is3DOpen, setIs3DOpen] = useState(false);
    
    // Modal state
    const [baggyModalState, setBaggyModalState] = useState({ isOpen: false, message: '' });

    const [formData, setFormData] = useState({
        height: 170,
        weight: 65,
        gender: 'male',
        brand: 'generic',
        region: 'asia',
        garmentType: 'both'
    });

    useEffect(() => {
        document.documentElement.setAttribute('data-theme', theme);
    }, [theme]);

    useEffect(() => {
        // Pre-configure options from URL parameters if available (useful for merchant customized buttons)
        const queryParams = new URLSearchParams(window.location.search);
        const urlGarment = queryParams.get('garment');
        const urlBrand = queryParams.get('brand');
        const urlRegion = queryParams.get('region');
        
        if (urlGarment) setFormData(prev => ({ ...prev, garmentType: urlGarment }));
        if (urlBrand) setFormData(prev => ({ ...prev, brand: urlBrand }));
        if (urlRegion) setFormData(prev => ({ ...prev, region: urlRegion }));
    }, []);

    useEffect(() => {
        const init = async () => {
            const data = await fetchBrands();
            if (data.brands) {
                setBrandsData(data.brands);
                
                // Only set brand from API if URL query param didn't specify one
                const queryParams = new URLSearchParams(window.location.search);
                if (!queryParams.get('brand') && data.default_brand) {
                    setFormData(prev => ({ ...prev, brand: data.default_brand }));
                }
            }
        };
        init();
    }, []);

    const toggleTheme = () => {
        setTheme(t => t === 'dark' ? 'light' : 'dark');
    };

    const handlePredict = async (ignoreBaggyWarning = false) => {
        if (!image) {
            setError('Vui lòng chọn ảnh.');
            return;
        }
        
        setIsLoading(true);
        setError(null);
        setResult(null);

        // Derive image type from garment type
        let imageType = 'full';
        if (formData.garmentType === 'shirt') imageType = 'upper';
        if (formData.garmentType === 'pants') imageType = 'lower';

        const payload = {
            ...formData,
            image_type: imageType,
            ignore_baggy_warning: ignoreBaggyWarning,
            image: image.split(',')[1] // remove data URL prefix
        };

        const res = await predictSize(payload);
        setIsLoading(false);

        if (res.success) {
            if (res.require_user_confirmation && res.baggy_clothes_detected) {
                setBaggyModalState({ isOpen: true, message: res.warning_message });
            } else {
                setResult(res);

                // Broadcast size result to the parent window if embedded in a merchant iframe
                if (typeof window !== 'undefined' && window.parent && window.parent !== window) {
                    window.parent.postMessage({
                        type: 'BODY_SIZE_AI_RESULT',
                        result: res,
                        garmentType: formData.garmentType
                    }, '*');
                }
            }
        } else {
            setError(res.error || 'Có lỗi xảy ra');
        }
    };

    return (
        <div className="app-container">
            {/* Background */}
            <div className="bg-animation">
                <div className="bg-shape bg-shape-1"></div>
                <div className="bg-shape bg-shape-2"></div>
            </div>

            {/* Header */}
            <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <h1 style={{ background: 'var(--gradient-1)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', fontSize: '2rem' }}>
                        Body Size AI
                    </h1>
                    <p style={{ color: 'var(--text-secondary)' }}>Gợi ý size áo & quần bằng AI</p>
                </div>
                <button className="theme-toggle" onClick={toggleTheme}>
                    {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
                </button>
            </header>

            <main className="grid-2">
                {/* Left Panel */}
                <div className="flex-col">
                    <DynamicGuide garmentType={formData.garmentType} />
                    
                    <ImageUploader image={image} setImage={setImage} />
                    
                    <div className="glass-panel" style={{ marginTop: '1rem' }}>
                        <FormControls formData={formData} setFormData={setFormData} brandsData={brandsData} />
                        
                        {error && <div style={{ color: 'var(--error-color)', marginTop: '1rem', padding: '0.5rem', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '8px' }}>{error}</div>}
                        
                        <button 
                            className="btn btn-primary" 
                            style={{ width: '100%', marginTop: '1.5rem' }}
                            onClick={() => handlePredict(false)}
                            disabled={isLoading}
                        >
                            {isLoading ? 'Đang phân tích...' : 'Phân tích & Gợi ý size'}
                        </button>
                    </div>
                </div>

                {/* Right Panel */}
                <div className="glass-panel">
                    <h3 style={{ marginBottom: '1.5rem' }}>Kết quả</h3>
                    
                    {!result && !isLoading && (
                        <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '3rem 0' }}>
                            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🎯</div>
                            Kết quả sẽ hiển thị ở đây
                        </div>
                    )}
                    
                    {isLoading && (
                        <div style={{ textAlign: 'center', padding: '3rem 0', color: 'var(--primary-color)' }}>
                            <div style={{ animation: 'float 2s infinite', fontSize: '2rem' }}>⏳</div>
                            AI đang tính toán...
                        </div>
                    )}
                    
                    {result && (
                        <ResultsDisplay 
                            result={result} 
                            garmentType={formData.garmentType} 
                            onView3D={() => setIs3DOpen(true)}
                        />
                    )}
                </div>
            </main>

            <Body3DViewer 
                isOpen={is3DOpen}
                onClose={() => setIs3DOpen(false)}
                gender={formData.gender}
                measurements={result ? { ...result.measurements, height_cm: formData.height, weight_kg: formData.weight } : null}
            />

            <BaggyWarningModal 
                isOpen={baggyModalState.isOpen}
                message={baggyModalState.message}
                onCancel={() => {
                    setBaggyModalState({ isOpen: false, message: '' });
                    setImage(null);
                }}
                onConfirm={() => {
                    setBaggyModalState({ isOpen: false, message: '' });
                    handlePredict(true);
                }}
            />
        </div>
    );
}

