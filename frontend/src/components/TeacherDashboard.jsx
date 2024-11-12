import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const TeacherDashboard = () => {
    const [recentAnalyses, setRecentAnalyses] = useState([]);
    const [stats, setStats] = useState({
        totalAnalyses: 0,
        averageScore: 0,
        pendingReviews: 0
    });
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchDashboardData = async () => {
            const token = localStorage.getItem('token');
            try {
                const response = await fetch('/api/teacher/dashboard', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                const data = await response.json();
                setRecentAnalyses(data.recentAnalyses);
                setStats(data.stats);
            } catch (error) {
                console.error('Error fetching dashboard data:', error);
            } finally {
                setIsLoading(false);
            }
        };

        fetchDashboardData();
    }, []);

    if (isLoading) {
        return <div className="flex justify-center items-center h-screen">Loading...</div>;
    }

    return (
        <div className="max-w-7xl mx-auto p-6">
            <h1 className="text-3xl font-bold mb-8">Teacher Dashboard</h1>
            
            {/* Stats Overview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-white p-6 rounded-lg shadow">
                    <h3 className="text-gray-500">Total Analyses</h3>
                    <p className="text-2xl font-bold">{stats.totalAnalyses}</p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow">
                    <h3 className="text-gray-500">Average Score</h3>
                    <p className="text-2xl font-bold">{stats.averageScore}%</p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow">
                    <h3 className="text-gray-500">Pending Reviews</h3>
                    <p className="text-2xl font-bold">{stats.pendingReviews}</p>
                </div>
            </div>

            {/* Quick Actions */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                <Link 
                    to="/TextAnalysisForm"
                    className="bg-blue-600 text-white p-6 rounded-lg shadow hover:bg-blue-700 transition"
                >
                    <h3 className="text-xl font-bold mb-2">New Analysis</h3>
                    <p>Analyze a new text or essay</p>
                </Link>
                {/* <Link 
                    to="/review-pending"
                    className="bg-green-600 text-white p-6 rounded-lg shadow hover:bg-green-700 transition"
                >
                    <h3 className="text-xl font-bold mb-2">Review Pending</h3>
                    <p>Review pending analyses</p>
                </Link> */}
            </div>

            {/* Recent Analyses */}
            <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-bold mb-4">Recent Analyses</h2>
                <div className="space-y-4">
                    {recentAnalyses.map((analysis) => (
                        <div 
                            key={analysis.id}
                            className="border-b pb-4 last:border-b-0 last:pb-0"
                        >
                            <div className="flex justify-between items-center">
                                <div>
                                    <h3 className="font-medium">{analysis.title}</h3>
                                    <p className="text-sm text-gray-500">
                                        {new Date(analysis.date).toLocaleDateString()}
                                    </p>
                                </div>
                                <Link 
                                    to={`/analysis/${analysis.id}`}
                                    className="text-blue-600 hover:text-blue-800"
                                >
                                    View Details
                                </Link>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default TeacherDashboard; 