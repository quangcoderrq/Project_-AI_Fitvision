import React, { useState, useEffect } from 'react';
import { Key, Copy, Check, Eye, EyeOff, RefreshCw, Code, LayoutGrid, Terminal, BarChart3, HelpCircle, Lock } from 'lucide-react';
import EmbeddedWidgetDemo from './EmbeddedWidgetDemo';
import { fetchLogs, fetchStats, predictSize } from '../api';

export default function DeveloperDashboard({ isSubscribed, activePlan, apiToken, onRegenerateToken, onNavigate, brandsData }) {
    const [activeSubTab, setActiveSubTab] = useState('integration');
    const [showToken, setShowToken] = useState(false);
    const [copiedToken, setCopiedToken] = useState(false);
    const [copiedCode, setCopiedCode] = useState(false);
    
    // API logs and statistics
    const [logs, setLogs] = useState([]);
    const [stats, setStats] = useState(null);
    const [isLoadingStats, setIsLoadingStats] = useState(false);
    
    // API Console state
    const [apiConsoleData, setApiConsoleData] = useState({
        height: 172,
        weight: 68,
        gender: 'male',
        brand: 'uniqlo'
    });
    const [isApiLoading, setIsApiLoading] = useState(false);
    const [apiResponse, setApiResponse] = useState(null);

    // Fetch logs & stats
    const loadLogsAndStats = async () => {
        setIsLoadingStats(true);
        try {
            const [logsData, statsData] = await Promise.all([
                fetchLogs(),
                fetchStats()
            ]);
            setLogs(logsData || []);
            setStats(statsData);
        } catch (e) {
            console.error("Error loading stats/logs:", e);
        } finally {
            setIsLoadingStats(false);
        }
    };

    useEffect(() => {
        loadLogsAndStats();
    }, [apiToken, isSubscribed]);

    // Copy token helper
    const handleCopyToken = () => {
        navigator.clipboard.writeText(apiToken);
        setCopiedToken(true);
        setTimeout(() => setCopiedToken(false), 2000);
    };

    // Copy integration code helper
    const handleCopyCode = (codeText) => {
        navigator.clipboard.writeText(codeText);
        setCopiedCode(true);
        setTimeout(() => setCopiedCode(false), 2000);
    };

    // Run API simulation
    const runApiTest = async () => {
        setIsApiLoading(true);
        setApiResponse(null);
        
        // Solid black 1x1 png image in base64
        const mockBase64Image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=";
        
        const payload = {
            height: apiConsoleData.height,
            weight: apiConsoleData.weight,
            gender: apiConsoleData.gender,
            brand: apiConsoleData.brand,
            region: 'asia',
            image_type: 'full',
            ignore_baggy_warning: true,
            image: mockBase64Image
        };
        
        try {
            const res = await predictSize(payload, apiToken);
            setApiResponse(res);
        } catch (error) {
            setApiResponse({ success: false, error: error.message });
        } finally {
            setIsApiLoading(false);
            // Reload logs and stats
            loadLogsAndStats();
        }
    };

    // Simulated integration code
    const getIntegrationCode = (platform) => {
        const tokenDisplay = isSubscribed ? apiToken : 'YOUR_API_TOKEN';
        if (platform === 'html') {
            return `<!-- 1. Đặt thẻ này ở nơi bạn muốn nút hiển thị -->
<div id="fitvision-ai-widget" 
     data-token="${tokenDisplay}"
     data-theme="dark" 
     data-brand="uniqlo" 
     data-garment="both">
</div>

<!-- 2. Nhúng file script ở cuối thẻ body -->
<script src="https://cdn.fitvision.ai/widget.v1.js" async></script>`;
        }
        if (platform === 'react') {
            return `import { FitVisionWidget } from '@fitvision/react-widget';

function ProductPage() {
  return (
    <div className="product-details">
      <h3>Áo Thun Unisex</h3>
      <FitVisionWidget 
        apiToken="${tokenDisplay}"
        brand="uniqlo"
        garmentType="shirt"
        theme="dark"
        onSelectSize={(size) => setSelectedSize(size)}
      />
    </div>
  );
}`;
        }
        return `// Hướng dẫn nhúng Shopify Liquid
// Chèn đoạn code sau vào file 'sections/main-product.liquid' của theme:

<div class="product-form__buttons">
  <div id="fitvision-ai-widget" 
       data-token="${tokenDisplay}" 
       data-brand="{{ product.vendor | downcase }}" 
       data-garment="shirt">
  </div>
</div>

<script src="https://cdn.fitvision.ai/shopify-widget.js" defer></script>`;
    };

    const [platformTab, setPlatformTab] = useState('html');

    return (
        <div className="developer-dashboard fade-in">
            
            {/* Page Header */}
            <div style={{ marginBottom: '2rem' }}>
                <h2 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>Dashboard Lập Trình Viên</h2>
                <p style={{ color: 'var(--text-secondary)' }}>Quản lý khóa API, cấu hình Widget và theo dõi dữ liệu đo lường.</p>
            </div>

            {/* Subscription Alert & Token section */}
            {!isSubscribed ? (
                <div className="glass-panel" style={{ borderLeft: '4px solid var(--warning-color)', marginBottom: '2rem', background: 'rgba(245, 158, 11, 0.05)' }}>
                    <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
                        <Lock size={24} style={{ color: 'var(--warning-color)', flexShrink: 0 }} />
                        <div>
                            <h4 style={{ fontSize: '1.1rem', marginBottom: '0.25rem' }}>Chưa kích hoạt gói API Token</h4>
                            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1rem' }}>
                                Bạn đang ở chế độ chạy thử nghiệm giới hạn. Vui lòng mua gói cước dịch vụ để kích hoạt API Token thương mại dùng nhúng vào cửa hàng bán hàng thật.
                            </p>
                            <button className="btn btn-primary" onClick={() => onNavigate('pricing')}>
                                Kích hoạt API Token ngay
                            </button>
                        </div>
                    </div>
                </div>
            ) : (
                <div className="glass-panel" style={{ borderLeft: '4px solid var(--success-color)', marginBottom: '2rem', background: 'rgba(16, 185, 129, 0.05)' }}>
                    <h4 style={{ fontSize: '1.1rem', marginBottom: '0.25rem', color: 'var(--success-color)' }}>
                        ✓ Tài khoản đã kích hoạt gói: {activePlan}
                    </h4>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                        Khóa API Token chính thức của bạn đã hoạt động bình thường trên tất cả các tên miền được nhúng.
                    </p>
                </div>
            )}

            {/* Token Card */}
            <div className="glass-panel" style={{ marginBottom: '2rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                    <Key size={18} style={{ color: 'var(--primary-color)' }} />
                    <h4 style={{ fontSize: '1.1rem' }}>API Access Token</h4>
                </div>
                
                <div className="token-card">
                    <span className="token-text">
                        {showToken ? apiToken : '••••••••••••••••••••••••••••••••••••••••••••••••'}
                    </span>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <button 
                            className="theme-toggle" 
                            style={{ width: '36px', height: '36px' }}
                            onClick={() => setShowToken(!showToken)}
                            title={showToken ? 'Ẩn token' : 'Hiện token'}
                        >
                            {showToken ? <EyeOff size={16} /> : <Eye size={16} />}
                        </button>
                        <button 
                            className="theme-toggle" 
                            style={{ width: '36px', height: '36px' }}
                            onClick={handleCopyToken}
                            title="Sao chép token"
                        >
                            {copiedToken ? <Check size={16} style={{ color: 'var(--success-color)' }} /> : <Copy size={16} />}
                        </button>
                        <button 
                            className="theme-toggle" 
                            style={{ width: '36px', height: '36px' }}
                            onClick={onRegenerateToken}
                            title="Tạo lại token mới"
                        >
                            <RefreshCw size={16} />
                        </button>
                    </div>
                </div>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                    ⚠️ Giữ API Token này bí mật và không chia sẻ ở nơi công cộng.
                </p>
            </div>

            {/* Dashboard Tabs */}
            <div className="dashboard-tabs">
                <button 
                    className={`nav-item ${activeSubTab === 'integration' ? 'active' : ''}`}
                    onClick={() => setActiveSubTab('integration')}
                    style={{ background: 'transparent', border: 'none', padding: '0.75rem 1.25rem', borderRadius: '0', borderBottom: activeSubTab === 'integration' ? '2px solid var(--primary-color)' : 'none' }}
                >
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem' }}>
                        <Code size={16} /> Tích hợp Widget
                    </span>
                </button>
                <button 
                    className={`nav-item ${activeSubTab === 'sandbox' ? 'active' : ''}`}
                    onClick={() => setActiveSubTab('sandbox')}
                    style={{ background: 'transparent', border: 'none', padding: '0.75rem 1.25rem', borderRadius: '0', borderBottom: activeSubTab === 'sandbox' ? '2px solid var(--primary-color)' : 'none' }}
                >
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem' }}>
                        <LayoutGrid size={16} /> Sandbox Thử Nghiệm
                    </span>
                </button>
                <button 
                    className={`nav-item ${activeSubTab === 'console' ? 'active' : ''}`}
                    onClick={() => setActiveSubTab('console')}
                    style={{ background: 'transparent', border: 'none', padding: '0.75rem 1.25rem', borderRadius: '0', borderBottom: activeSubTab === 'console' ? '2px solid var(--primary-color)' : 'none' }}
                >
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem' }}>
                        <Terminal size={16} /> API Console
                    </span>
                </button>
                <button 
                    className={`nav-item ${activeSubTab === 'analytics' ? 'active' : ''}`}
                    onClick={() => setActiveSubTab('analytics')}
                    style={{ background: 'transparent', border: 'none', padding: '0.75rem 1.25rem', borderRadius: '0', borderBottom: activeSubTab === 'analytics' ? '2px solid var(--primary-color)' : 'none' }}
                >
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem' }}>
                        <BarChart3 size={16} /> Số liệu thống kê
                    </span>
                </button>
            </div>

            {/* Tab Contents */}
            <div>
                {/* Integration Tab */}
                {activeSubTab === 'integration' && (
                    <div className="glass-panel fade-in flex-col">
                        <h4 style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>Hướng dẫn tích hợp Widget vào Storefront</h4>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
                            Tích hợp nút chọn size AI FitVision cực kỳ dễ dàng vào các nền tảng thương mại điện tử phổ biến chỉ với vài dòng mã:
                        </p>

                        <div className="payment-tab-buttons" style={{ width: 'fit-content' }}>
                            <button className={`payment-tab ${platformTab === 'html' ? 'active' : ''}`} onClick={() => setPlatformTab('html')}>HTML/JS</button>
                            <button className={`payment-tab ${platformTab === 'react' ? 'active' : ''}`} onClick={() => setPlatformTab('react')}>React Component</button>
                            <button className={`payment-tab ${platformTab === 'shopify' ? 'active' : ''}`} onClick={() => setPlatformTab('shopify')}>Shopify Liquid</button>
                        </div>

                        <div className="code-block">
                            <button 
                                className="code-copy-btn"
                                onClick={() => handleCopyCode(getIntegrationCode(platformTab))}
                            >
                                {copiedCode ? 'Đã copy!' : 'Copy Code'}
                            </button>
                            <pre style={{ overflowX: 'auto', margin: '0' }}>{getIntegrationCode(platformTab)}</pre>
                        </div>
                    </div>
                )}

                {/* Sandbox Tab */}
                {activeSubTab === 'sandbox' && (
                    <div className="fade-in">
                        <EmbeddedWidgetDemo apiToken={apiToken} brandsData={brandsData} />
                    </div>
                )}

                {/* API Console Tab */}
                {activeSubTab === 'console' && (
                    <div className="glass-panel fade-in flex-col api-console-panel">
                        <style>{`
                            .api-console-panel {
                                --api-field-bg: color-mix(in srgb, var(--glass-bg) 88%, transparent);
                                --api-field-border: var(--glass-border);
                                --api-result-bg: color-mix(in srgb, var(--glass-bg) 72%, #111827 28%);
                            }

                            .api-console-grid {
                                display: grid;
                                grid-template-columns: minmax(0, 1.35fr) minmax(320px, 1fr);
                                gap: 1.5rem;
                                align-items: stretch;
                            }

                            .api-console-form-grid {
                                display: grid;
                                grid-template-columns: repeat(2, minmax(0, 1fr));
                                gap: 1rem;
                            }

                            .api-console-field {
                                margin: 0;
                            }

                            .api-console-input,
                            .api-console-select {
                                width: 100%;
                                min-height: 52px;
                                box-sizing: border-box;
                                border-radius: 14px;
                                border: 1px solid var(--api-field-border);
                                background-color: var(--api-field-bg);
                                color: var(--text-primary);
                                outline: none;
                                transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
                            }

                            .api-console-input {
                                padding: 0 1rem;
                            }

                            .api-console-select-wrap {
                                position: relative;
                            }

                            .api-console-select {
                                appearance: none;
                                -webkit-appearance: none;
                                -moz-appearance: none;
                                padding: 0 2.75rem 0 1rem;
                                background-image: none !important;
                                background-repeat: no-repeat !important;
                            }

                            .api-console-select-wrap::after {
                                content: "⌄";
                                position: absolute;
                                right: 1rem;
                                top: 50%;
                                transform: translateY(-56%);
                                color: var(--text-secondary);
                                font-size: 1.25rem;
                                line-height: 1;
                                pointer-events: none;
                            }

                            .api-console-input:focus,
                            .api-console-select:focus {
                                border-color: var(--primary-color);
                                box-shadow: 0 0 0 3px color-mix(in srgb, var(--primary-color) 22%, transparent);
                            }

                            .api-console-select option {
                                background: var(--bg-primary, #111827);
                                color: var(--text-primary, #f8fafc);
                            }

                            .api-console-result {
                                min-height: 280px;
                                height: 100%;
                                overflow-y: auto;
                                margin-top: 0.2rem;
                                border-radius: 14px;
                                background: var(--api-result-bg);
                            }

                            @media (max-width: 900px) {
                                .api-console-grid,
                                .api-console-form-grid {
                                    grid-template-columns: 1fr;
                                }
                            }
                        `}</style>

                        <h4 style={{ fontSize: '1.2rem' }}>Thử nghiệm gọi API trực tiếp</h4>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1rem' }}>
                            Trình kiểm tra tương tác cho phép bạn chạy thử JSON API mà không cần cài đặt code.
                        </p>

                        <div className="api-console-grid">
                            <div className="flex-col" style={{ gap: '1rem' }}>
                                <div className="api-console-form-grid">
                                    <div className="input-group api-console-field">
                                        <label className="input-label" htmlFor="api-height">Chiều cao (cm)</label>
                                        <input
                                            id="api-height"
                                            type="number"
                                            min="80"
                                            max="230"
                                            step="1"
                                            inputMode="numeric"
                                            className="glass-input api-console-input"
                                            value={apiConsoleData.height}
                                            onChange={(e) => setApiConsoleData(prev => ({ ...prev, height: Number(e.target.value) || '' }))}
                                        />
                                    </div>
                                    <div className="input-group api-console-field">
                                        <label className="input-label" htmlFor="api-weight">Cân nặng (kg)</label>
                                        <input
                                            id="api-weight"
                                            type="number"
                                            min="20"
                                            max="250"
                                            step="1"
                                            inputMode="numeric"
                                            className="glass-input api-console-input"
                                            value={apiConsoleData.weight}
                                            onChange={(e) => setApiConsoleData(prev => ({ ...prev, weight: Number(e.target.value) || '' }))}
                                        />
                                    </div>
                                </div>

                                <div className="api-console-form-grid">
                                    <div className="input-group api-console-field">
                                        <label className="input-label" htmlFor="api-gender">Giới tính</label>
                                        <div className="api-console-select-wrap">
                                            <select
                                                id="api-gender"
                                                className="glass-input api-console-select"
                                                value={apiConsoleData.gender}
                                                onChange={(e) => setApiConsoleData(prev => ({ ...prev, gender: e.target.value }))}
                                            >
                                                <option value="male">Nam</option>
                                                <option value="female">Nữ</option>
                                            </select>
                                        </div>
                                    </div>
                                    <div className="input-group api-console-field">
                                        <label className="input-label" htmlFor="api-brand">Brand</label>
                                        <div className="api-console-select-wrap">
                                            <select
                                                id="api-brand"
                                                className="glass-input api-console-select"
                                                value={apiConsoleData.brand}
                                                onChange={(e) => setApiConsoleData(prev => ({ ...prev, brand: e.target.value }))}
                                            >
                                                <option value="uniqlo">Uniqlo</option>
                                                <option value="nike">Nike</option>
                                                <option value="adidas">Adidas</option>
                                                <option value="generic">Generic</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>

                                <button
                                    className="btn btn-primary"
                                    style={{ width: '100%', minHeight: '50px', marginTop: '1rem', borderRadius: '14px', fontWeight: 700 }}
                                    onClick={runApiTest}
                                    disabled={isApiLoading || !apiConsoleData.height || !apiConsoleData.weight}
                                >
                                    {isApiLoading ? 'Đang gửi Request...' : 'Gửi Yêu Cầu (Send POST Request)'}
                                </button>
                            </div>

                            <div className="flex-col">
                                <span className="input-label">Kết quả API phản hồi (JSON Response):</span>
                                <div className="code-block api-console-result">
                                    {apiResponse ? (
                                        <pre style={{ margin: '0', whiteSpace: 'pre-wrap' }}>
                                            {JSON.stringify(apiResponse, null, 2)}
                                        </pre>
                                    ) : isApiLoading ? (
                                        <div style={{ color: 'var(--text-muted)', display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', padding: '1rem', textAlign: 'center' }}>
                                            Đang gọi POST /predict...
                                        </div>
                                    ) : (
                                        <div style={{ color: 'var(--text-muted)', display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', padding: '1rem', textAlign: 'center' }}>
                                            Click "Gửi Yêu Cầu" để xem dữ liệu JSON phản hồi
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Analytics Tab */}
                {activeSubTab === 'analytics' && (
                    <div className="flex-col fade-in">
                        {isLoadingStats ? (
                            <div style={{ textAlign: 'center', padding: '3rem 0', color: 'var(--primary-color)' }}>
                                <div style={{ animation: 'float 2s infinite', fontSize: '2rem' }}>⏳</div>
                                Đang tải số liệu thống kê...
                            </div>
                        ) : (
                            <>
                                {/* Stats cards */}
                                <div className="grid-3">
                                    <div className="glass-panel">
                                        <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 'bold' }}>SỐ LƯỢT GỌI API THÀNH CÔNG</div>
                                        <div style={{ fontSize: '2rem', fontWeight: 'bold', margin: '0.5rem 0', color: 'var(--primary-color)' }}>
                                            {stats ? stats.total_calls : '0'} <span style={{ fontSize: '1rem', color: 'var(--text-muted)', fontWeight: 'normal' }}>/ {stats && stats.monthly_limit === 1000000 ? 'Không giới hạn' : (stats ? stats.monthly_limit : '100')}</span>
                                        </div>
                                        <div style={{ fontSize: '0.75rem', color: 'var(--success-color)' }}>
                                            ✓ {stats ? `${stats.api_success_rate}% Thành công` : 'Đang hoạt động'}
                                        </div>
                                    </div>
                                    <div className="glass-panel">
                                        <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 'bold' }}>TỶ LỆ KHÁCH HÀNG CLICK CHỌN SIZE</div>
                                        <div style={{ fontSize: '2rem', fontWeight: 'bold', margin: '0.5rem 0', color: 'var(--success-color)' }}>
                                            {stats && stats.cvr_increase > 0 ? `+${stats.cvr_increase}%` : '--'}
                                        </div>
                                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                                            So với bảng chọn size thông thường
                                        </div>
                                    </div>
                                    <div className="glass-panel">
                                        <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 'bold' }}>TỶ LỆ GIẢM ĐỔI TRẢ SẢN PHẨM</div>
                                        <div style={{ fontSize: '2rem', fontWeight: 'bold', margin: '0.5rem 0', color: '#ec4899' }}>
                                            {stats && stats.returns_reduction > 0 ? `-${stats.returns_reduction}%` : '--'}
                                        </div>
                                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                                            Ước tính từ phản hồi size khớp khách hàng
                                        </div>
                                    </div>
                                </div>

                                {/* Bar usage indicator */}
                                {stats && stats.monthly_limit < 1000000 && (
                                    <div className="glass-panel flex-col" style={{ marginTop: '1rem' }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
                                            <span>Giới hạn băng thông API gói {activePlan || 'Free'}</span>
                                            <span>{stats.monthly_usage_percentage.toFixed(1)}%</span>
                                        </div>
                                        <div style={{ height: '8px', background: 'var(--glass-border)', borderRadius: '4px', overflow: 'hidden' }}>
                                            <div style={{ height: '100%', width: `${stats.monthly_usage_percentage}%`, background: 'var(--primary-color)', borderRadius: '4px' }}></div>
                                        </div>
                                    </div>
                                )}

                                {/* Logs Table */}
                                <div className="glass-panel flex-col" style={{ marginTop: '1.5rem', width: '100%' }}>
                                    <h4 style={{ fontSize: '1.1rem', marginBottom: '1rem' }}>Lịch sử cuộc gọi API gần đây (SQLite)</h4>
                                    {logs.length === 0 ? (
                                        <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '3rem 0' }}>
                                            Chưa có cuộc gọi API nào được thực hiện. 
                                            Hãy thử nghiệm ở Sandbox hoặc Demo trước!
                                        </div>
                                    ) : (
                                        <div style={{ overflowX: 'auto' }}>
                                            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
                                                <thead>
                                                    <tr style={{ borderBottom: '1px solid var(--glass-border)', color: 'var(--text-muted)' }}>
                                                        <th style={{ padding: '0.75rem' }}>Thời gian</th>
                                                        <th style={{ padding: '0.75rem' }}>Chiều cao</th>
                                                        <th style={{ padding: '0.75rem' }}>Cân nặng</th>
                                                        <th style={{ padding: '0.75rem' }}>Giới tính</th>
                                                        <th style={{ padding: '0.75rem' }}>Thương hiệu</th>
                                                        <th style={{ padding: '0.75rem' }}>Size gợi ý</th>
                                                        <th style={{ padding: '0.75rem' }}>Độ tin cậy</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {logs.map((log) => (
                                                        <tr key={log.id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}>
                                                            <td style={{ padding: '0.75rem', color: 'var(--text-muted)' }}>{log.created_at}</td>
                                                            <td style={{ padding: '0.75rem' }}>{log.height} cm</td>
                                                            <td style={{ padding: '0.75rem' }}>{log.weight} kg</td>
                                                            <td style={{ padding: '0.75rem', textTransform: 'capitalize' }}>{log.gender === 'male' ? 'Nam' : 'Nữ'}</td>
                                                            <td style={{ padding: '0.75rem', textTransform: 'capitalize' }}>{log.brand}</td>
                                                            <td style={{ padding: '0.75rem' }}>
                                                                <span style={{ background: 'var(--primary-glow)', color: 'var(--primary-color)', padding: '0.2rem 0.5rem', borderRadius: '4px', fontWeight: 'bold' }}>
                                                                    {log.predicted_size}
                                                                </span>
                                                            </td>
                                                            <td style={{ padding: '0.75rem' }}>{(log.confidence * 100).toFixed(0)}%</td>
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                        </div>
                                    )}
                                </div>
                            </>
                        )}
                    </div>
                )}
            </div>

        </div>
    );
}
