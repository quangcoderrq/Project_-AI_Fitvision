import React, { useState, useEffect } from 'react';
import { Moon, Sun, LogIn, LogOut, Sparkles, User } from 'lucide-react';
import { fetchBrands, predictSize, login, register, fetchProfile, regenerateToken, subscribe } from './api';
import FormControls from './components/FormControls';
import DynamicGuide from './components/DynamicGuide';
import ImageUploader from './components/ImageUploader';
import ResultsDisplay from './components/ResultsDisplay';
import BaggyWarningModal from './components/BaggyWarningModal';
import Body3DViewer from './components/Body3DViewer';

// SaaS Pages
import LandingPage from './components/LandingPage';
import PricingSection from './components/PricingSection';
import CheckoutModal from './components/CheckoutModal';
import DeveloperDashboard from './components/DeveloperDashboard';
import AuthPage from './components/AuthPage';

const REMEMBER_KEYS = ['fv_remember_me', 'fv_saved_email', 'fv_saved_password'];

function loadRememberedLogin() {
    if (localStorage.getItem('fv_remember_me') !== 'true') {
        return { rememberMe: false, email: '', password: '' };
    }
    return {
        rememberMe: true,
        email: localStorage.getItem('fv_saved_email') || '',
        password: localStorage.getItem('fv_saved_password') || '',
    };
}

function saveRememberedLogin(email, password) {
    localStorage.setItem('fv_remember_me', 'true');
    localStorage.setItem('fv_saved_email', email);
    localStorage.setItem('fv_saved_password', password);
}

function clearRememberedLogin() {
    REMEMBER_KEYS.forEach((key) => localStorage.removeItem(key));
}

export default function App() {
    const [theme, setTheme] = useState('dark');
    const [activeTab, setActiveTab] = useState('home');
    const [brandsData, setBrandsData] = useState([]);
    
    // Auth & Subscription States (Persisted in localStorage)
    const [isLoggedIn, setIsLoggedIn] = useState(() => {
        return localStorage.getItem('fv_is_logged_in') === 'true';
    });
    const [userEmail, setUserEmail] = useState(() => {
        return localStorage.getItem('fv_user_email') || '';
    });
    const [userFullName, setUserFullName] = useState(() => {
        return localStorage.getItem('fv_user_full_name') || '';
    });
    const [isSubscribed, setIsSubscribed] = useState(() => {
        return localStorage.getItem('fv_is_subscribed') === 'true';
    });
    const [activePlan, setActivePlan] = useState(() => {
        return localStorage.getItem('fv_active_plan') || '';
    });
    const [apiToken, setApiToken] = useState(() => {
        return localStorage.getItem('fv_api_token') || '';
    });

    // Auth page mode
    const [authMode, setAuthMode] = useState('login');
    const [isAuthSubmitting, setIsAuthSubmitting] = useState(false);
    const [isCheckoutOpen, setIsCheckoutOpen] = useState(false);
    const [selectedPlan, setSelectedPlan] = useState({ name: '', price: '' });
    
    const [authError, setAuthError] = useState(null);
    const [rememberMe, setRememberMe] = useState(() => loadRememberedLogin().rememberMe);
    
    // Login / Register form fields
    const [loginForm, setLoginForm] = useState({ fullName: '', email: '', password: '' });

    // AI Prediction Demo States
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [result, setResult] = useState(null);
    const [image, setImage] = useState(null);
    const [is3DOpen, setIs3DOpen] = useState(false);
    const [baggyModalState, setBaggyModalState] = useState({ isOpen: false, message: '' });

    const [formData, setFormData] = useState({
        height: 170,
        weight: 65,
        gender: 'male',
        brand: 'generic',
        region: 'asia',
        garmentType: 'both'
    });

    // Sync theme
    useEffect(() => {
        document.documentElement.setAttribute('data-theme', theme);
    }, [theme]);

    // Check existing session on load
    useEffect(() => {
        const checkSession = async () => {
            const jwtToken = localStorage.getItem('fv_jwt_token');
            if (jwtToken) {
                const profile = await fetchProfile();
                if (profile) {
                    setIsLoggedIn(true);
                    setUserEmail(profile.email);
                    setUserFullName(profile.full_name || '');
                    setApiToken(profile.api_token);
                    setActivePlan(profile.active_plan);
                    setIsSubscribed(profile.active_plan !== 'Free');
                    
                    localStorage.setItem('fv_is_logged_in', 'true');
                    localStorage.setItem('fv_user_email', profile.email);
                    localStorage.setItem('fv_user_full_name', profile.full_name || '');
                    localStorage.setItem('fv_api_token', profile.api_token);
                    localStorage.setItem('fv_active_plan', profile.active_plan);
                    localStorage.setItem('fv_is_subscribed', (profile.active_plan !== 'Free').toString());
                } else {
                    handleLogout();
                }
            }
        };
        checkSession();
    }, []);

    // Fetch Brands configuration on mount
    useEffect(() => {
        const init = async () => {
            const data = await fetchBrands();
            if (data.brands) {
                setBrandsData(data.brands);
                if (data.default_brand) {
                    setFormData(prev => ({ ...prev, brand: data.default_brand }));
                }
            }
        };
        init();
    }, []);

    const toggleTheme = () => {
        setTheme(t => t === 'dark' ? 'light' : 'dark');
    };

    const goToAuth = (mode = 'login') => {
        setAuthMode(mode);
        setAuthError(null);

        if (mode === 'login') {
            const saved = loadRememberedLogin();
            setRememberMe(saved.rememberMe);
            setLoginForm({
                fullName: '',
                email: saved.rememberMe ? saved.email : '',
                password: saved.rememberMe ? saved.password : '',
            });
        } else {
            setLoginForm({ fullName: '', email: '', password: '' });
        }

        setActiveTab('auth');
    };

    const handleAuthModeSwitch = (mode) => {
        setAuthMode(mode);
        setAuthError(null);

        if (mode === 'login') {
            const saved = loadRememberedLogin();
            setRememberMe(saved.rememberMe);
            setLoginForm({
                fullName: '',
                email: saved.rememberMe ? saved.email : '',
                password: saved.rememberMe ? saved.password : '',
            });
        } else {
            setLoginForm({ fullName: '', email: '', password: '' });
        }
    };

    const handleRememberMeChange = (checked) => {
        setRememberMe(checked);
        if (!checked) {
            clearRememberedLogin();
        }
    };

    const leaveAuth = () => {
        setAuthError(null);
        setLoginForm({ fullName: '', email: '', password: '' });
        setSelectedPlan({ name: '', price: '' });
        setActiveTab('home');
    };

    // Handle Auth Login & Registration
    const handleAuthSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setAuthError(null);

        const isRegister = authMode === 'register';

        if (isRegister) {
            if (!loginForm.fullName.trim()) {
                setAuthError('Vui lòng nhập họ và tên.');
                return;
            }
            if (loginForm.password.length < 6) {
                setAuthError('Mật khẩu phải có ít nhất 6 ký tự.');
                return;
            }
        }

        setIsAuthSubmitting(true);
        let res;
        
        if (isRegister) {
            res = await register(loginForm.fullName.trim(), loginForm.email.trim(), loginForm.password);
        } else {
            res = await login(loginForm.email.trim(), loginForm.password);
        }
        setIsAuthSubmitting(false);

        if (res && res.access_token) {
            if (!isRegister) {
                if (rememberMe) {
                    saveRememberedLogin(
                        loginForm.email.trim(),
                        loginForm.password
                    );
                } else {
                    clearRememberedLogin();
                }
            }

            setIsLoggedIn(true);
            setUserEmail(res.email);
            setUserFullName(res.full_name || '');
            setApiToken(res.api_token);
            setActivePlan(res.active_plan);
            setIsSubscribed(res.active_plan !== 'Free');
            
            localStorage.setItem('fv_jwt_token', res.access_token);
            localStorage.setItem('fv_is_logged_in', 'true');
            localStorage.setItem('fv_user_email', res.email);
            localStorage.setItem('fv_user_full_name', res.full_name || '');
            localStorage.setItem('fv_api_token', res.api_token);
            localStorage.setItem('fv_active_plan', res.active_plan);
            localStorage.setItem('fv_is_subscribed', (res.active_plan !== 'Free').toString());
            
            setLoginForm({ fullName: '', email: '', password: '' });
            setAuthError(null);
            
            if (selectedPlan.name) {
                setActiveTab('pricing');
                setIsCheckoutOpen(true);
            } else {
                setActiveTab('dashboard');
            }
        } else {
            setAuthError(res?.error || 'Xác thực thất bại.');
        }
    };

    // Handle Auth Logout
    const handleLogout = () => {
        const saved = loadRememberedLogin();

        setIsLoggedIn(false);
        setUserEmail('');
        setUserFullName('');
        setIsSubscribed(false);
        setActivePlan('');
        setApiToken('');
        localStorage.clear();

        if (saved.rememberMe) {
            saveRememberedLogin(saved.email, saved.password);
        }

        setActiveTab('home');
    };

    // Select subscription plan
    const handleSelectPlan = (planName, planPrice) => {
        setSelectedPlan({ name: planName, price: planPrice });
        if (!isLoggedIn) {
            goToAuth('login');
        } else {
            setIsCheckoutOpen(true);
        }
    };

    // Handle checkout success
    const handlePaymentSuccess = async (planName) => {
        const res = await subscribe(planName);
        if (res) {
            setIsSubscribed(res.active_plan !== 'Free');
            setActivePlan(res.active_plan);
            setApiToken(res.api_token);
            
            localStorage.setItem('fv_is_subscribed', (res.active_plan !== 'Free').toString());
            localStorage.setItem('fv_active_plan', res.active_plan);
            localStorage.setItem('fv_api_token', res.api_token);
            
            setIsCheckoutOpen(false);
            setActiveTab('dashboard');
        } else {
            alert('Lỗi cập nhật gói dịch vụ.');
        }
    };

    // Handle token regeneration
    const handleRegenerateToken = async () => {
        if (window.confirm('Bạn có chắc chắn muốn tạo lại Token? Token cũ của bạn sẽ ngừng hoạt động ngay lập tức.')) {
            const res = await regenerateToken();
            if (res) {
                setApiToken(res.api_token);
                localStorage.setItem('fv_api_token', res.api_token);
                alert('Tạo Token mới thành công!');
            } else {
                alert('Tạo Token mới thất bại.');
            }
        }
    };

    // Run AI Prediction
    const handlePredict = async (ignoreBaggyWarning = false) => {
        if (!image) {
            setError('Vui lòng chọn ảnh.');
            return;
        }
        
        setIsLoading(true);
        setError(null);
        setResult(null);

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
            }
        } else {
            setError(res.error || 'Có lỗi xảy ra khi gọi dịch vụ AI');
        }
    };

    return (
        <>
            {/* Full-screen Auth Page */}
            {activeTab === 'auth' && (
                <AuthPage
                    mode={authMode}
                    onSwitchMode={handleAuthModeSwitch}
                    onSubmit={handleAuthSubmit}
                    onNavigateHome={leaveAuth}
                    form={loginForm}
                    setForm={setLoginForm}
                    authError={authError}
                    isSubmitting={isAuthSubmitting}
                    theme={theme}
                    toggleTheme={toggleTheme}
                    rememberMe={rememberMe}
                    setRememberMe={handleRememberMeChange}
                />
            )}

        <div className="app-container" style={{ display: activeTab === 'auth' ? 'none' : undefined }}>
            {/* Background Shape */}
            <div className="bg-animation">
                <div className="bg-shape bg-shape-1"></div>
                <div className="bg-shape bg-shape-2"></div>
            </div>

            {/* Navigation Bar */}
            <nav className="navbar">
                  <div className="nav-brand" onClick={() => setActiveTab('home')}>

                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '32px', height: '32px', borderRadius: '8px', background: 'var(--gradient-1)', color: 'white' }}>
                        <Sparkles size={18} fill="white" />
                    </div>
                    <span style={{ fontSize: '1.25rem', fontWeight: 'bold', fontFamily: 'Outfit', background: 'var(--gradient-1)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                        FitVision AI
                    </span>
                </div>

                <div className="nav-links">
                    <button className={`nav-item ${activeTab === 'home' ? 'active' : ''}`} onClick={() => setActiveTab('home')}>Trang chủ</button>
                    <button className={`nav-item ${activeTab === 'demo' ? 'active' : ''}`} onClick={() => setActiveTab('demo')}>Xem Demo AI</button>
                    <button className={`nav-item ${activeTab === 'pricing' ? 'active' : ''}`} onClick={() => setActiveTab('pricing')}>Bảng giá</button>
                    <button className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`} onClick={() => setActiveTab('dashboard')}>Developer Dashboard</button>
                </div>

                <div className="nav-actions">
                    <button className="theme-toggle" onClick={toggleTheme}>
                        {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
                    </button>
                    
                    {isLoggedIn ? (
                        <div className="nav-user-actions">
                            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                                <User size={16} /> {userFullName || userEmail.split('@')[0]}
                            </div>
                            <button className="btn btn-secondary" style={{ padding: '0.5rem 1rem', fontSize: '0.85rem' }} onClick={handleLogout}>
                                <LogOut size={16} /> Đăng xuất
                            </button>
                        </div>
                    ) : (
                        <div className="nav-user-actions">
                            <button className="btn btn-secondary" style={{ padding: '0.5rem 1rem', fontSize: '0.85rem' }} onClick={() => goToAuth('register')}>
                                Đăng ký
                            </button>
                            <button className="btn btn-primary" style={{ padding: '0.5rem 1rem', fontSize: '0.85rem' }} onClick={() => goToAuth('login')}>
                                <LogIn size={16} /> Đăng nhập
                            </button>
                        </div>
                    )}
                </div>
            </nav>

            {/* Pages Content Router */}
            <main style={{ marginTop: '1rem' }}>
                {activeTab === 'home' && <LandingPage onNavigate={setActiveTab} />}
                
                {activeTab === 'pricing' && <PricingSection onSelectPlan={handleSelectPlan} />}
                
                {activeTab === 'dashboard' && (
                    <DeveloperDashboard 
                        isSubscribed={isSubscribed}
                        activePlan={activePlan}
                        apiToken={apiToken}
                        onRegenerateToken={handleRegenerateToken}
                        onNavigate={setActiveTab}
                        brandsData={brandsData}
                    />
                )}
                
                {activeTab === 'demo' && (
                    <div className="grid-2 fade-in">
                        {/* Left Panel */}
                        <div className="flex-col">
                            <DynamicGuide garmentType={formData.garmentType} />
                            
                            <ImageUploader image={image} setImage={setImage} />
                            
                            <div className="glass-panel" style={{ marginTop: '1rem' }}>
                                <FormControls formData={formData} setFormData={setFormData} brandsData={brandsData} />
                                
                                {error && (
                                    <div style={{ color: 'var(--error-color)', marginTop: '1rem', padding: '0.5rem', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '8px' }}>
                                        {error}
                                    </div>
                                )}
                                
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
                                    Kết quả đo lường và gợi ý size của AI sẽ hiển thị ở đây.
                                </div>
                            )}
                            
                            {isLoading && (
                                <div style={{ textAlign: 'center', padding: '3rem 0', color: 'var(--primary-color)' }}>
                                    <div style={{ animation: 'float 2s infinite', fontSize: '2rem' }}>⏳</div>
                                    AI đang xử lý tư thế và trích xuất đặc trưng...
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
                    </div>
                )}
            </main>

            {/* Modals & Dialogs */}
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

            <CheckoutModal 
                isOpen={isCheckoutOpen}
                onClose={() => setIsCheckoutOpen(false)}
                planName={selectedPlan.name}
                planPrice={selectedPlan.price}
                onPaymentSuccess={handlePaymentSuccess}
            />
        </div>
        </>
    );
}
