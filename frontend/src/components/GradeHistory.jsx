import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';

const GradeHistory = ({ type = 'paper', onHistoryItemClick, onReviewSelect }) => {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchHistory = async () => {
            setLoading(true);
            try {
                const endpoint = type === 'paper' 
                    ? '/api/grading/grades' 
                    : '/api/code-review/reviews';
                
                const response = await fetch(`${endpoint}?skip=0&limit=10`, {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    }
                });

                if (!response.ok) {
                    throw new Error('Failed to fetch history');
                }

                const data = await response.json();
                setHistory(data);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchHistory();
    }, [type]);

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    };

    if (loading) {
        return (
            <aside className="w-64 bg-gray-50 border-r border-gray-200 p-6">
                <h2 className="text-xl font-semibold mb-4">History</h2>
                <div className="animate-pulse space-y-4">
                    {[...Array(5)].map((_, i) => (
                        <div key={i} className="bg-gray-200 h-20 rounded-lg"></div>
                    ))}
                </div>
            </aside>
        );
    }

    if (error) {
        return (
            <aside className="w-64 bg-gray-50 border-r border-gray-200 p-6">
                <h2 className="text-xl font-semibold mb-4">History</h2>
                <div className="text-red-500 text-sm">{error}</div>
            </aside>
        );
    }

    return (
        <aside className="w-64 bg-gray-50 border-r border-gray-200 p-6">
            <h2 className="text-xl font-semibold mb-4">
                {type === 'paper' ? 'Paper History' : 'Code Review History'}
            </h2>
            <div className="space-y-4">
                {history.map((item) => (
                    <button
                        key={item.id}
                        onClick={() => onHistoryItemClick(item)}
                        className="w-full bg-white p-4 rounded-lg shadow-sm border border-gray-200 
                                 hover:border-orange-300 transition-colors text-left"
                    >
                        <div className="text-sm text-gray-600">
                            {formatDate(item.created_at)}
                        </div>
                        <div className="font-medium my-1">
                            {type === 'paper' ? item.subject : item.assignment_name}
                        </div>
                        <div className="text-orange-400 font-semibold">
                            Score: {item.overall_score}%
                        </div>
                        {type === 'code' && (
                            <div className="text-xs text-gray-500 mt-1">
                                Language: {item.language}
                            </div>
                        )}
                    </button>
                ))}
                {history.length === 0 && (
                    <div className="text-gray-500 text-center py-4">
                        No history available
                    </div>
                )}
            </div>
        </aside>
    );
};

GradeHistory.propTypes = {
    type: PropTypes.oneOf(['paper', 'code']),
    onHistoryItemClick: PropTypes.func.isRequired,
    onReviewSelect: PropTypes.func
};

export default GradeHistory; 