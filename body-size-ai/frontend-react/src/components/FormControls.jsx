import React from 'react';

const brands = [
    { value: 'generic', label: 'Chung (Generic)' },
];

const regionsMap = {
    asia: 'Châu Á / Asian Fit',
    eu: 'Châu Âu / EU Fit',
    us: 'Mỹ / US Fit',
};

export default function FormControls({ formData, setFormData, brandsData = [] }) {
    const handleChange = (e) => {
        const { name, value } = e.target;

        if (name === 'brand') {
            const brandInfo = brandsData.find((b) => b.name === value);
            const nextRegion = brandInfo?.available_regions?.[0] || 'asia';

            setFormData((prev) => ({
                ...prev,
                brand: value,
                region: nextRegion,
            }));
            return;
        }

        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const currentBrand = brandsData.find((b) => b.name === formData.brand);
    const availableRegions = currentBrand?.available_regions || ['asia'];

    return (
        <div className="fv-form-card">
            <div className="fv-form-grid">
                <Field label="Chiều cao" suffix="cm">
                    <input
                        type="number"
                        name="height"
                        className="fv-input"
                        value={formData.height}
                        onChange={handleChange}
                        min="100"
                        max="250"
                        placeholder="175"
                    />
                </Field>

                <Field label="Cân nặng" suffix="kg">
                    <input
                        type="number"
                        name="weight"
                        className="fv-input"
                        value={formData.weight}
                        onChange={handleChange}
                        min="30"
                        max="300"
                        placeholder="65"
                    />
                </Field>
            </div>

            <div className="fv-field">
                <label className="fv-label">Giới tính</label>
                <div className="fv-segment">
                    <button
                        type="button"
                        className={`fv-segment-btn ${formData.gender === 'male' ? 'active' : ''}`}
                        onClick={() => setFormData((prev) => ({ ...prev, gender: 'male' }))}
                    >
                        <span>Nam</span>
                    </button>

                    <button
                        type="button"
                        className={`fv-segment-btn ${formData.gender === 'female' ? 'active' : ''}`}
                        onClick={() => setFormData((prev) => ({ ...prev, gender: 'female' }))}
                    >
                        <span>Nữ</span>
                    </button>
                </div>
            </div>

            <div className="fv-form-grid">
                <Field label="Thương hiệu">
                    <select
                        name="brand"
                        className="fv-select"
                        value={formData.brand}
                        onChange={handleChange}
                    >
                        {brands.map((b) => (
                            <option key={b.value} value={b.value}>{b.label}</option>
                        ))}

                        {brandsData.map((b) => (
                            <option key={b.name} value={b.name}>
                                {b.name.charAt(0).toUpperCase() + b.name.slice(1)}
                            </option>
                        ))}
                    </select>
                </Field>

                <Field label="Khu vực / Form">
                    <select
                        name="region"
                        className="fv-select"
                        value={formData.region}
                        onChange={handleChange}
                    >
                        {availableRegions.map((r) => (
                            <option key={r} value={r}>
                                {regionsMap[r] || r.toUpperCase()}
                            </option>
                        ))}
                    </select>
                </Field>
            </div>

            <Field label="Sản phẩm cần mua">
                <div className="fv-product-options">
                    {[
                        { value: 'both', label: 'Cả bộ', desc: 'Áo & quần' },
                        { value: 'shirt', label: 'Chỉ áo', desc: 'Upper body' },
                        { value: 'pants', label: 'Chỉ quần', desc: 'Lower body' },
                    ].map((item) => (
                        <button
                            key={item.value}
                            type="button"
                            className={`fv-product-card ${formData.garmentType === item.value ? 'active' : ''}`}
                            onClick={() => setFormData((prev) => ({ ...prev, garmentType: item.value }))}
                        >
                            <strong>{item.label}</strong>
                            <small>{item.desc}</small>
                        </button>
                    ))}
                </div>
            </Field>
        </div>
    );
}

function Field({ label, suffix, children }) {
    return (
        <div className="fv-field">
            <div className="fv-label-row">
                <label className="fv-label">{label}</label>
                {suffix && <span className="fv-suffix">{suffix}</span>}
            </div>
            {children}
        </div>
    );
}