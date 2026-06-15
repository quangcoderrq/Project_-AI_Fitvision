const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export const fetchBrands = async () => {
    try {
        const res = await fetch(`${API_BASE}/brands`);
        return await res.json();
    } catch (error) {
        console.error('Error fetching brands:', error);
        return { brands: [] };
    }
};

export const predictSize = async (payload, apiToken = null) => {
    try {
        const headers = { 'Content-Type': 'application/json' };
        
        // Attach JWT session or API Token
        const activeToken = apiToken || localStorage.getItem('fv_api_token');
        const jwtToken = localStorage.getItem('fv_jwt_token');
        
        if (activeToken) {
            headers['X-API-Token'] = activeToken;
        } else if (jwtToken) {
            headers['Authorization'] = `Bearer ${jwtToken}`;
        } else {
            // Fallback for public demo landing page so it doesn't break
            headers['X-API-Token'] = 'fv_demo_guest_key';
        }

        const res = await fetch(`${API_BASE}/predict`, {
            method: 'POST',
            headers,
            body: JSON.stringify(payload)
        });
        return await res.json();
    } catch (error) {
        console.error('Error predicting size:', error);
        return { success: false, error: error.message };
    }
};

const parseApiError = (data, fallback) => {
    if (data?.error) return data.error;
    if (Array.isArray(data?.detail)) {
        return data.detail.map((item) => item.msg).join(', ');
    }
    if (typeof data?.detail === 'string') return data.detail;
    return fallback;
};

export const register = async (fullName, email, password) => {
    try {
        const res = await fetch(`${API_BASE}/api/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ full_name: fullName, email, password })
        });
        const data = await res.json();
        if (!res.ok) {
            return { success: false, error: parseApiError(data, 'Đăng ký thất bại') };
        }
        return data;
    } catch (error) {
        console.error('Registration failed:', error);
        return { success: false, error: error.message };
    }
};

export const login = async (email, password) => {
    try {
        const res = await fetch(`${API_BASE}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await res.json();
        if (!res.ok) {
            return { success: false, error: parseApiError(data, 'Đăng nhập thất bại') };
        }
        return data;
    } catch (error) {
        console.error('Login failed:', error);
        return { success: false, error: error.message };
    }
};

export const fetchProfile = async () => {
    try {
        const jwtToken = localStorage.getItem('fv_jwt_token');
        if (!jwtToken) return null;
        
        const res = await fetch(`${API_BASE}/api/auth/me`, {
            headers: { 'Authorization': `Bearer ${jwtToken}` }
        });
        if (res.status === 401) {
            localStorage.clear();
            return null;
        }
        return await res.json();
    } catch (error) {
        console.error('Fetch profile failed:', error);
        return null;
    }
};

export const regenerateToken = async () => {
    try {
        const jwtToken = localStorage.getItem('fv_jwt_token');
        if (!jwtToken) return null;
        
        const res = await fetch(`${API_BASE}/api/auth/regenerate-token`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${jwtToken}` }
        });
        return await res.json();
    } catch (error) {
        console.error('Regenerate token failed:', error);
        return null;
    }
};

export const subscribe = async (planName) => {
    try {
        const jwtToken = localStorage.getItem('fv_jwt_token');
        if (!jwtToken) return null;
        
        const res = await fetch(`${API_BASE}/api/auth/subscribe`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${jwtToken}` 
            },
            body: JSON.stringify({ plan_name: planName })
        });
        return await res.json();
    } catch (error) {
        console.error('Subscription failed:', error);
        return null;
    }
};

export const fetchLogs = async () => {
    try {
        const jwtToken = localStorage.getItem('fv_jwt_token');
        if (!jwtToken) return [];
        
        const res = await fetch(`${API_BASE}/api/analytics/logs`, {
            headers: { 'Authorization': `Bearer ${jwtToken}` }
        });
        return await res.json();
    } catch (error) {
        console.error('Fetch logs failed:', error);
        return [];
    }
};

export const fetchStats = async () => {
    try {
        const jwtToken = localStorage.getItem('fv_jwt_token');
        if (!jwtToken) return null;
        
        const res = await fetch(`${API_BASE}/api/analytics/stats`, {
            headers: { 'Authorization': `Bearer ${jwtToken}` }
        });
        return await res.json();
    } catch (error) {
        console.error('Fetch stats failed:', error);
        return null;
    }
};
