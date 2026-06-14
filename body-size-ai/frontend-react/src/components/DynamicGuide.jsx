import React from 'react';
import { Lightbulb } from 'lucide-react';

export default function DynamicGuide({ garmentType }) {
    const guides = {
        both: {
            title: 'Hướng dẫn chụp toàn thân',
            tips: [
                'Đứng thẳng, chụp toàn thân từ đầu đến chân.',
                'Mặc quần áo vừa vặn (không quá rộng).',
                'Nền đơn giản, ánh sáng đủ.',
                'Hai tay buông tự nhiên, không khoanh tay.'
            ]
        },
        shirt: {
            title: 'Hướng dẫn chụp nửa thân trên',
            tips: [
                'Chụp từ đỉnh đầu xuống qua hông một chút.',
                'Nên đứng hoặc ngồi thẳng lưng.',
                'Hai vai song song, không nghiêng người.',
                'Tránh mặc áo khoác quá dày.'
            ]
        },
        pants: {
            title: 'Hướng dẫn chụp nửa thân dưới',
            tips: [
                'Chụp từ phần eo/hông xuống gót chân.',
                'Hai chân đứng thẳng, khép hờ.',
                'Mặc quần ôm vừa hoặc quần short để hệ thống đo chính xác hơn.',
                'Nền tương phản tốt với màu quần.'
            ]
        }
    };

    const guide = guides[garmentType] || guides['both'];

    return (
        <div style={{
            background: 'rgba(59, 130, 246, 0.1)',
            borderLeft: '4px solid var(--primary-color)',
            padding: '1rem',
            borderRadius: '0 var(--card-radius) var(--card-radius) 0',
            marginBottom: '1.5rem',
            animation: 'fadeIn 0.3s ease-in'
        }}>
            <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--primary-color)', marginBottom: '0.5rem' }}>
                <Lightbulb size={18} /> {guide.title}
            </h4>
            <ul style={{ paddingLeft: '1.5rem', color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: '1.6' }}>
                {guide.tips.map((tip, idx) => (
                    <li key={idx}>{tip}</li>
                ))}
            </ul>
        </div>
    );
}
