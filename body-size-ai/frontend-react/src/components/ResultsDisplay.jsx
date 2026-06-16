import React, { useState } from 'react';
import { ShoppingBag, Eye, MessageSquare, Check, Loader2 } from 'lucide-react';
import { submitFeedback } from '../api';

export default function ResultsDisplay({ result, garmentType, onView3D }) {
    const [feedbackSent, setFeedbackSent] = useState(false);
    const [feedbackLoading, setFeedbackLoading] = useState(false);
    const [feedbackError, setFeedbackError] = useState(null);

    if (!result) return null;

    const renderSizeCard = (title, sizeData, defaultSize, icon) => {
        const size = sizeData?.recommended_size || defaultSize;
        const confidence = sizeData
            ? Math.round(sizeData.confidence * 100)
            : Math.round(result.confidence * 100);

        const reason = sizeData?.reason;
        const altSizes = sizeData?.alternative_sizes || [];

        return (
            <div className="glass-panel" style={{ flex: 1, textAlign: 'center', background: 'rgba(255,255,255,0.02)' }}>
                <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>{icon}</div>
                <h4 style={{ color: 'var(--text-secondary)' }}>{title}</h4>

                <div style={{
                    fontSize: '3rem',
                    fontWeight: 700,
                    color: 'var(--primary-color)',
                    margin: '0.5rem 0'
                }}>
                    {size || '-'}
                </div>

                <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                    Độ tin cậy: {confidence}%
                </div>

                {reason && (
                    <div style={{
                        fontSize: '0.85rem',
                        color: 'var(--warning-color)',
                        marginTop: '0.5rem',
                        lineHeight: 1.4
                    }}>
                        {reason}
                    </div>
                )}

                {altSizes.length > 0 && (
                    <div style={{ marginTop: '1rem' }}>
                        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                            Size thay thế:{' '}
                        </span>

                        {altSizes.map((s) => (
                            <span
                                key={s}
                                style={{
                                    display: 'inline-block',
                                    padding: '2px 8px',
                                    margin: '0 2px',
                                    background: 'rgba(255,255,255,0.1)',
                                    borderRadius: '10px',
                                    fontSize: '0.8rem'
                                }}
                            >
                                {s}
                            </span>
                        ))}
                    </div>
                )}
            </div>
        );
    };

    const handleFeedback = async (overallFeedback, issueArea = null) => {
        if (!result?.prediction_log_id) {
            setFeedbackError('Không tìm thấy mã dự đoán để gửi feedback.');
            return;
        }

        setFeedbackLoading(true);
        setFeedbackError(null);

        const payload = {
            prediction_log_id: result.prediction_log_id,

            selected_shirt_size: result.shirt_size?.recommended_size || null,
            selected_pants_size: result.pants_size?.recommended_size || null,

            shirt_feedback: garmentType === 'pants' ? null : overallFeedback,
            pants_feedback: garmentType === 'shirt' ? null : overallFeedback,

            overall_feedback: overallFeedback,
            issue_area: issueArea,

            feedback_note: null,
            returned_or_exchanged: false
        };

        const res = await submitFeedback(payload);

        setFeedbackLoading(false);

        if (res.success) {
            setFeedbackSent(true);
        } else {
            setFeedbackError(res.error || 'Gửi feedback thất bại.');
        }
    };

    const showShirt = garmentType === 'both' || garmentType === 'shirt';
    const showPants = garmentType === 'both' || garmentType === 'pants';

    return (
        <div className="fade-in">
            <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
                {showShirt && renderSizeCard('Size Áo', result.shirt_size, result.predicted_size, '👕')}
                {showPants && renderSizeCard('Size Quần', result.pants_size, result.predicted_size, '👖')}
            </div>

            {typeof result.pose_quality === 'number' && (
                <div
                    className="glass-panel"
                    style={{
                        marginBottom: '1rem',
                        padding: '1rem',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        gap: '1rem'
                    }}
                >
                    <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                        Chất lượng ảnh phân tích
                    </span>

                    <strong style={{
                        color:
                            result.pose_quality >= 0.8
                                ? 'var(--success-color)'
                                : result.pose_quality >= 0.62
                                    ? 'var(--warning-color)'
                                    : 'var(--error-color)'
                    }}>
                        {Math.round(result.pose_quality * 100)}%
                    </strong>
                </div>
            )}

            <button
                className="btn btn-primary"
                style={{ width: '100%', marginBottom: '1rem', background: 'var(--success-color)' }}
            >
                <ShoppingBag size={20} /> Áp dụng Size vào Giỏ hàng
            </button>

            <button
                className="btn btn-secondary"
                style={{ width: '100%', marginBottom: '1.5rem' }}
                onClick={onView3D}
            >
                <Eye size={20} /> Xem mô hình 3D
            </button>

            {result.prediction_log_id && (
                <div className="glass-panel" style={{ marginBottom: '1.5rem', textAlign: 'center' }}>
                    {!feedbackSent ? (
                        <>
                            <h4 style={{
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                gap: '0.5rem',
                                marginBottom: '0.5rem'
                            }}>
                                <MessageSquare size={18} />
                                Gợi ý size này có phù hợp không?
                            </h4>

                            <p style={{
                                color: 'var(--text-secondary)',
                                fontSize: '0.9rem',
                                marginBottom: '1rem'
                            }}>
                                Feedback của bạn giúp FitVision AI học và gợi ý size chính xác hơn.
                            </p>

                            <div style={{
                                display: 'flex',
                                gap: '0.5rem',
                                justifyContent: 'center',
                                flexWrap: 'wrap'
                            }}>
                                <button
                                    className="btn btn-secondary"
                                    disabled={feedbackLoading}
                                    onClick={() => handleFeedback('fit')}
                                >
                                    Vừa
                                </button>

                                <button
                                    className="btn btn-secondary"
                                    disabled={feedbackLoading}
                                    onClick={() => handleFeedback('tight')}
                                >
                                    Hơi chật
                                </button>

                                <button
                                    className="btn btn-secondary"
                                    disabled={feedbackLoading}
                                    onClick={() => handleFeedback('loose')}
                                >
                                    Hơi rộng
                                </button>

                                <button
                                    className="btn btn-secondary"
                                    disabled={feedbackLoading}
                                    onClick={() => handleFeedback('wrong')}
                                >
                                    Sai size
                                </button>
                            </div>

                            {feedbackLoading && (
                                <div style={{
                                    marginTop: '1rem',
                                    color: 'var(--text-secondary)',
                                    display: 'flex',
                                    justifyContent: 'center',
                                    alignItems: 'center',
                                    gap: '0.5rem'
                                }}>
                                    <Loader2 size={16} className="spinner" />
                                    Đang lưu feedback...
                                </div>
                            )}

                            {feedbackError && (
                                <p style={{
                                    color: 'var(--error-color)',
                                    marginTop: '0.75rem',
                                    fontSize: '0.85rem'
                                }}>
                                    {feedbackError}
                                </p>
                            )}
                        </>
                    ) : (
                        <div style={{
                            color: 'var(--success-color)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '0.5rem'
                        }}>
                            <Check size={18} />
                            Cảm ơn bạn! Feedback đã được lưu.
                        </div>
                    )}
                </div>
            )}

            {result.measurements && (
                <div className="glass-panel">
                    <h4 style={{
                        marginBottom: '1rem',
                        borderBottom: '1px solid var(--glass-border)',
                        paddingBottom: '0.5rem'
                    }}>
                        📏 Số đo dự đoán
                    </h4>

                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fill, minmax(100px, 1fr))',
                        gap: '1rem'
                    }}>
                        {Object.entries(result.measurements).map(([key, value]) => (
                            <div key={key} style={{ textAlign: 'center' }}>
                                <div style={{
                                    fontSize: '0.8rem',
                                    color: 'var(--text-muted)',
                                    textTransform: 'capitalize'
                                }}>
                                    {key
                                        .replace('_cm', '')
                                        .replace('_circumference', '')
                                        .replace('_width', '')}
                                </div>

                                <div style={{ fontWeight: 600 }}>
                                    {value > 0 ? `${value.toFixed(1)} cm` : '-'}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}