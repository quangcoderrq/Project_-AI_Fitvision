const API_BASE = typeof window !== 'undefined' && window.location.origin.includes('5173')
    ? 'http://127.0.0.1:8000'
    : (typeof window !== 'undefined' ? window.location.origin : 'http://127.0.0.1:8000');

export const fetchBrands = async () => {
    try {
        const res = await fetch(`${API_BASE}/brands`);
        return await res.json();
    } catch (error) {
        console.error('Error fetching brands:', error);
        return { brands: [] };
    }
};

export const predictSize = async (payload) => {
    try {
        const res = await fetch(`${API_BASE}/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        return await res.json();
    } catch (error) {
        console.error('Error predicting size:', error);
        return { success: false, error: error.message };
    }
};
