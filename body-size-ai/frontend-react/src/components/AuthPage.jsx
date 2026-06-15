import React, { useState } from 'react';
import {
    Sparkles, ArrowLeft, Sun, Moon, Mail, Lock, User,
    Scan, Shirt, Ruler, Eye, EyeOff, Loader2
} from 'lucide-react';

function PoseVisual() {
    const keypoints = [
        { cx: 120, cy: 45, delay: 0 },
        { cx: 120, cy: 85, delay: 0.2 },
        { cx: 85, cy: 100, delay: 0.4 },
        { cx: 155, cy: 100, delay: 0.5 },
        { cx: 70, cy: 140, delay: 0.6 },
        { cx: 170, cy: 140, delay: 0.7 },
        { cx: 120, cy: 160, delay: 0.8 },
        { cx: 95, cy: 220, delay: 1.0 },
        { cx: 145, cy: 220, delay: 1.1 },
        { cx: 85, cy: 290, delay: 1.2 },
        { cx: 155, cy: 290, delay: 1.3 },
    ];

    return (
        <div className="auth-pose-wrap">
            <div className="auth-scan-line" />
            <svg viewBox="0 0 240 340" className="auth-pose-svg" aria-hidden="true">
                <defs>
                    <linearGradient id="bodyGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stopColor="rgba(59,130,246,0.5)" />
                        <stop offset="100%" stopColor="rgba(99,102,241,0.15)" />
                    </linearGradient>
                    <filter id="glow">
                        <feGaussianBlur stdDeviation="3" result="blur" />
                        <feMerge>
                            <feMergeNode in="blur" />
                            <feMergeNode in="SourceGraphic" />
                        </feMerge>
                    </filter>
                </defs>

                {/* Body silhouette */}
                <ellipse cx="120" cy="38" rx="22" ry="26" fill="url(#bodyGrad)" opacity="0.9" />
                <path
                    d="M95 65 Q120 58 145 65 L155 105 Q120 115 85 105 Z"
                    fill="url(#bodyGrad)" opacity="0.85"
                />
                <path
                    d="M88 105 L72 145 L65 195 L78 198 L90 150 L95 170 L95 250 L82 310 L98 312 L102 250 L118 250 L122 312 L138 310 L125 250 L125 170 L130 150 L142 198 L155 195 L148 145 L132 105 Z"
                    fill="url(#bodyGrad)" opacity="0.8"
                />

                {/* Skeleton lines */}
                <g stroke="rgba(96,165,250,0.35)" strokeWidth="1.5" fill="none">
                    <line x1="120" y1="45" x2="120" y2="85" />
                    <line x1="120" y1="85" x2="85" y2="100" />
                    <line x1="120" y1="85" x2="155" y2="100" />
                    <line x1="85" y1="100" x2="70" y2="140" />
                    <line x1="155" y1="100" x2="170" y2="140" />
                    <line x1="120" y1="85" x2="120" y2="160" />
                    <line x1="120" y1="160" x2="95" y2="220" />
                    <line x1="120" y1="160" x2="145" y2="220" />
                    <line x1="95" y1="220" x2="85" y2="290" />
                    <line x1="145" y1="220" x2="155" y2="290" />
                </g>

                {/* Animated keypoints */}
                {keypoints.map((kp, i) => (
                    <g key={i}>
                        <circle
                            cx={kp.cx} cy={kp.cy} r="12"
                            fill="rgba(59,130,246,0.15)"
                            className="auth-kp-ring"
                            style={{ animationDelay: `${kp.delay}s` }}
                        />
                        <circle
                            cx={kp.cx} cy={kp.cy} r="5"
                            fill="#60a5fa"
                            filter="url(#glow)"
                            className="auth-kp-dot"
                            style={{ animationDelay: `${kp.delay}s` }}
                        />
                    </g>
                ))}
            </svg>

            {/* Floating size badges */}
            <div className="auth-float-badge auth-badge-1">
                <Shirt size={14} /> Size M
            </div>
            <div className="auth-float-badge auth-badge-2">
                <Ruler size={14} /> 96cm
            </div>
            <div className="auth-float-badge auth-badge-3">
                <Scan size={14} /> 98.5%
            </div>
        </div>
    );
}

export default function AuthPage({
    mode,
    onSwitchMode,
    onSubmit,
    onNavigateHome,
    form,
    setForm,
    authError,
    isSubmitting,
    theme,
    toggleTheme,
    rememberMe,
    setRememberMe,
}) {
    const [showPassword, setShowPassword] = useState(false);
    const isRegister = mode === 'register';

    return (
        <div className="auth-page">
            <div className="auth-bg-grid" />
            <div className="auth-orb auth-orb-1" />
            <div className="auth-orb auth-orb-2" />
            <div className="auth-orb auth-orb-3" />

            {/* Header */}
            <header className="auth-header">
                <button className="auth-back-btn" onClick={onNavigateHome} type="button">
                    <ArrowLeft size={18} />
                    <span>Trang chủ</span>
                </button>

                <div className="auth-logo" onClick={onNavigateHome}>
                    <div className="auth-logo-icon">
                        <Sparkles size={18} fill="white" />
                    </div>
                    <span>FitVision AI</span>
                </div>

                <button className="theme-toggle" onClick={toggleTheme} type="button">
                    {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
                </button>
            </header>

            <div className="auth-layout">
                {/* Left — Visual panel */}
                <div className="auth-visual-panel">
                    <div className="auth-visual-content">
                        <div className="auth-visual-badge">
                            <Scan size={14} />
                            AI Body Measurement
                        </div>

                        <h1 className="auth-visual-title">
                            Đo size thông minh<br />
                            <span>bằng 1 bức ảnh</span>
                        </h1>

                        <p className="auth-visual-desc">
                            Công nghệ Pose Estimation phân tích tư thế cơ thể, gợi ý size áo quần chuẩn xác và mô phỏng 3D trực quan.
                        </p>

                        <PoseVisual />

                        <div className="auth-stats-row">
                            <div className="auth-stat-chip">
                                <strong>+32%</strong>
                                <span>CVR</span>
                            </div>
                            <div className="auth-stat-chip">
                                <strong>95%</strong>
                                <span>Độ chính xác</span>
                            </div>
                            <div className="auth-stat-chip">
                                <strong>-45%</strong>
                                <span>Đổi trả</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Right — Form panel */}
                <div className="auth-form-panel">
                    <div className="auth-form-card">
                        <div className="auth-form-header">
                            <h2>{isRegister ? 'Tạo tài khoản' : 'Chào mừng trở lại'}</h2>
                            <p>
                                {isRegister
                                    ? 'Đăng ký để truy cập Developer Dashboard và API Token'
                                    : 'Đăng nhập để quản lý API và theo dõi analytics'}
                            </p>
                        </div>

                        {/* Tab switcher */}
                        <div className="auth-tabs">
                            <button
                                type="button"
                                className={`auth-tab ${!isRegister ? 'active' : ''}`}
                                onClick={() => onSwitchMode('login')}
                            >
                                Đăng nhập
                            </button>
                            <button
                                type="button"
                                className={`auth-tab ${isRegister ? 'active' : ''}`}
                                onClick={() => onSwitchMode('register')}
                            >
                                Đăng ký
                            </button>
                            <div
                                className="auth-tab-indicator"
                                style={{ transform: isRegister ? 'translateX(100%)' : 'translateX(0)' }}
                            />
                        </div>

                        <form onSubmit={onSubmit} className="auth-form" key={mode} autoComplete="off">
                            <div className={`auth-form-fields ${isRegister ? 'register-mode' : 'login-mode'}`}>
                                {isRegister && (
                                    <div className="auth-field auth-field-animate">
                                        <label htmlFor="fullName">Họ và tên</label>
                                        <div className="auth-input-wrap">
                                            <User size={18} className="auth-input-icon" />
                                            <input
                                                id="fullName"
                                                type="text"
                                                className="auth-input"
                                                placeholder="Nguyễn Văn A"
                                                value={form.fullName}
                                                onChange={(e) => setForm(prev => ({ ...prev, fullName: e.target.value }))}
                                                required={isRegister}
                                                autoComplete="name"
                                            />
                                        </div>
                                    </div>
                                )}

                                <div className="auth-field auth-field-animate">
                                    <label htmlFor="email">Gmail / Email</label>
                                    <div className="auth-input-wrap">
                                        <Mail size={18} className="auth-input-icon" />
                                        <input
                                            id="email"
                                            name="fv-auth-email"
                                            type="email"
                                            className="auth-input"
                                            placeholder="example@gmail.com"
                                            value={form.email}
                                            onChange={(e) => setForm(prev => ({ ...prev, email: e.target.value }))}
                                            required
                                            autoComplete={isRegister ? 'email' : (rememberMe ? 'email' : 'off')}
                                        />
                                    </div>
                                </div>

                                <div className="auth-field auth-field-animate">
                                    <label htmlFor="password">
                                        Mật khẩu
                                        {isRegister && <span className="auth-label-hint">ít nhất 6 ký tự</span>}
                                    </label>
                                    <div className="auth-input-wrap">
                                        <Lock size={18} className="auth-input-icon" />
                                        <input
                                            id="password"
                                            name="fv-auth-password"
                                            type={showPassword ? 'text' : 'password'}
                                            className="auth-input auth-input-password"
                                            placeholder={isRegister ? 'Nhập mật khẩu (≥ 6 ký tự)' : 'Nhập mật khẩu'}
                                            value={form.password}
                                            onChange={(e) => setForm(prev => ({ ...prev, password: e.target.value }))}
                                            minLength={isRegister ? 6 : 1}
                                            required
                                            autoComplete={isRegister ? 'new-password' : (rememberMe ? 'current-password' : 'new-password')}
                                        />
                                        <button
                                            type="button"
                                            className="auth-password-toggle"
                                            onClick={() => setShowPassword(v => !v)}
                                            tabIndex={-1}
                                        >
                                            {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                                        </button>
                                    </div>
                                </div>

                                {!isRegister && (
                                    <label className="auth-remember">
                                        <input
                                            type="checkbox"
                                            checked={rememberMe}
                                            onChange={(e) => setRememberMe(e.target.checked)}
                                        />
                                        <span className="auth-remember-box" />
                                        <span className="auth-remember-text">Ghi nhớ đăng nhập</span>
                                    </label>
                                )}
                            </div>

                            {authError && (
                                <div className="auth-error" role="alert">
                                    {authError}
                                </div>
                            )}

                            <button
                                type="submit"
                                className="auth-submit-btn"
                                disabled={isSubmitting}
                            >
                                {isSubmitting ? (
                                    <>
                                        <Loader2 size={20} className="auth-spinner" />
                                        Đang xử lý...
                                    </>
                                ) : (
                                    <>
                                        <Sparkles size={18} />
                                        {isRegister ? 'Đăng ký tài khoản' : 'Đăng nhập'}
                                    </>
                                )}
                            </button>
                        </form>

                        <p className="auth-footer-note">
                            Tài khoản được lưu an toàn với mật khẩu mã hóa trên SQLite database.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
