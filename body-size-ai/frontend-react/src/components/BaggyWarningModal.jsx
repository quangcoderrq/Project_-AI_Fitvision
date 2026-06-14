import React from 'react';
import { AlertTriangle } from 'lucide-react';

export default function BaggyWarningModal({ isOpen, message, onConfirm, onCancel }) {
    if (!isOpen) return null;

    return (
        <div style={{
            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
            background: 'rgba(0, 0, 0, 0.6)',
            backdropFilter: 'blur(4px)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            zIndex: 1000,
            animation: 'fadeIn 0.2s ease-out'
        }}>
            <div className="glass-panel" style={{ maxWidth: '400px', width: '90%', textAlign: 'center' }}>
                <AlertTriangle size={48} color="var(--warning-color)" style={{ margin: '0 auto 1rem' }} />
                <h3 style={{ marginBottom: '1rem' }}>Phát hiện quần áo rộng</h3>
                <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem', lineHeight: '1.5' }}>
                    {message || "Hệ thống phát hiện bạn có thể đang mặc quần áo rộng. Điều này có thể làm sai lệch số đo thực tế. Bạn có muốn hệ thống tự động điều chỉnh và tiếp tục không?"}
                </p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    <button className="btn btn-primary" onClick={onConfirm}>Vẫn tiếp tục (Điều chỉnh tự động)</button>
                    <button className="btn btn-secondary" onClick={onCancel}>Hủy & Chụp lại ảnh</button>
                </div>
            </div>
        </div>
    );
}
