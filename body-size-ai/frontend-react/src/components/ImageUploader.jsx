import React, { useRef } from 'react';
import { Camera, Upload, X } from 'lucide-react';

export default function ImageUploader({ image, setImage }) {
    const fileInputRef = useRef(null);

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => setImage(e.target.result);
            reader.readAsDataURL(file);
        }
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        e.currentTarget.style.borderColor = 'var(--primary-color)';
    };

    const handleDragLeave = (e) => {
        e.currentTarget.style.borderColor = 'var(--glass-border)';
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.currentTarget.style.borderColor = 'var(--glass-border)';
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => setImage(e.target.result);
            reader.readAsDataURL(file);
        }
    };

    return (
        <div className="glass-panel" style={{ textAlign: 'center' }}>
            <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
                <Camera size={20} color="var(--primary-color)" /> Ảnh của bạn
            </h3>
            
            <div 
                onClick={() => !image && fileInputRef.current?.click()}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                style={{
                    border: '2px dashed var(--glass-border)',
                    borderRadius: 'var(--card-radius)',
                    padding: image ? '0' : '2rem',
                    cursor: image ? 'default' : 'pointer',
                    position: 'relative',
                    overflow: 'hidden',
                    minHeight: '200px',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'center',
                    alignItems: 'center',
                    transition: 'all 0.3s ease'
                }}
            >
                <input 
                    type="file" 
                    hidden 
                    accept="image/*" 
                    ref={fileInputRef} 
                    onChange={handleFileChange}
                />
                
                {image ? (
                    <>
                        <img src={image} alt="Preview" style={{ width: '100%', height: '100%', objectFit: 'contain', maxHeight: '400px' }} />
                        <button 
                            onClick={(e) => { e.stopPropagation(); setImage(null); }}
                            style={{
                                position: 'absolute', top: '10px', right: '10px',
                                background: 'rgba(0,0,0,0.5)', color: 'white', border: 'none',
                                borderRadius: '50%', width: '30px', height: '30px',
                                cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center'
                            }}
                        >
                            <X size={16} />
                        </button>
                    </>
                ) : (
                    <div style={{ color: 'var(--text-secondary)' }}>
                        <Upload size={32} style={{ marginBottom: '1rem', opacity: 0.7 }} />
                        <p style={{ fontWeight: 500 }}>Kéo thả ảnh hoặc <span style={{ color: 'var(--primary-color)' }}>nhấn để chọn</span></p>
                    </div>
                )}
            </div>
        </div>
    );
}
