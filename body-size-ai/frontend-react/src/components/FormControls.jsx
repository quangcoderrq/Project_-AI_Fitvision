import React from 'react';

export default function FormControls({ formData, setFormData, brandsData }) {
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
        
        // Auto update region if brand changes
        if (name === 'brand') {
            const brandInfo = brandsData.find(b => b.name === value);
            if (brandInfo && brandInfo.available_regions?.length > 0) {
                setFormData(prev => ({ ...prev, brand: value, region: brandInfo.available_regions[0] }));
            }
        }
    };

    const handleGender = (gender) => {
        setFormData(prev => ({ ...prev, gender }));
    };

    // Get current brand regions
    const currentBrand = brandsData.find(b => b.name === formData.brand);
    const availableRegions = currentBrand?.available_regions || ['asia'];

    return (
        <div className="flex-col">
            <div className="grid-2">
                <div className="input-group">
                    <label className="input-label">Chiều cao (cm)</label>
                    <input 
                        type="number" 
                        name="height"
                        className="glass-input" 
                        value={formData.height} 
                        onChange={handleChange}
                        min="100" max="250"
                    />
                </div>
                <div className="input-group">
                    <label className="input-label">Cân nặng (kg)</label>
                    <input 
                        type="number" 
                        name="weight"
                        className="glass-input" 
                        value={formData.weight} 
                        onChange={handleChange}
                        min="30" max="300"
                    />
                </div>
            </div>

            <div className="grid-2">
                <div className="input-group">
                    <label className="input-label">Giới tính</label>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <button 
                            className={`btn ${formData.gender === 'male' ? 'btn-primary' : 'btn-secondary'}`} 
                            style={{ flex: 1 }}
                            onClick={() => handleGender('male')}
                        >
                            👨 Nam
                        </button>
                        <button 
                            className={`btn ${formData.gender === 'female' ? 'btn-primary' : 'btn-secondary'}`} 
                            style={{ flex: 1 }}
                            onClick={() => handleGender('female')}
                        >
                            👩 Nữ
                        </button>
                    </div>
                </div>
                <div className="input-group">
                    <label className="input-label">Thương hiệu</label>
                    <select name="brand" className="glass-input" value={formData.brand} onChange={handleChange}>
                        <option value="generic">Chung (Generic)</option>
                        {brandsData.map(b => (
                            <option key={b.name} value={b.name}>{b.name.charAt(0).toUpperCase() + b.name.slice(1)}</option>
                        ))}
                    </select>
                </div>
            </div>

            <div className="grid-2">
                <div className="input-group">
                    <label className="input-label">Khu vực / Form</label>
                    <select name="region" className="glass-input" value={formData.region} onChange={handleChange}>
                        {availableRegions.map(r => (
                            <option key={r} value={r}>{r === 'asia' ? 'Châu Á (Asia)' : r.toUpperCase()}</option>
                        ))}
                    </select>
                </div>
                <div className="input-group">
                    <label className="input-label">Sản phẩm cần mua</label>
                    <select name="garmentType" className="glass-input" value={formData.garmentType} onChange={handleChange}>
                        <option value="both">Cả bộ (Áo & Quần)</option>
                        <option value="shirt">Chỉ Áo</option>
                        <option value="pants">Chỉ Quần</option>
                    </select>
                </div>
            </div>
            
            {/* Image type hidden normally, but we can sync it with garment type in parent, or let user override */}
        </div>
    );
}
