// src/App.jsx
import React, { useState } from 'react';
import TextAnalysisForm from './components/TextAnalysisForm';
import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import AnalysisDisplay from './components/AnalysisDisplay';

import Dashboard from './components/Dashboard';


// Create a wrapper component to use navigate
function AppContent() {
    const navigate = useNavigate();
    const [analysisData, setAnalysisData] = useState(null);

    const handleAnalysis = (data) => {
        setAnalysisData(data);
        navigate('/analysis-result');
    };

    return (
        <Routes>
            {/* <Route path="/" element={<TeacherDashboard />} /> */}
            <Route path="/" element={<Dashboard />} />

            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route 
                path="/analysis" 
                element={<TextAnalysisForm onAnalyze={handleAnalysis} />} 
            />
            <Route
                path="/analysis-result"
                element={
                    <AnalysisDisplay
                        data={analysisData}
                        onNoData={() => navigate('/')}
                    />
                }
            />
            {/* ... other routes ... */}
        </Routes>
    );
}

function App() {
    return (
        <BrowserRouter>
            <AppContent />
        </BrowserRouter>
    );
}

export default App;
