import React, { useState } from 'react';
import TextAnalysisForm from './TextAnalysisForm';
import AnalysisDisplay from './AnalysisDisplay';
import NavigationBar from './NavigationBar';
import CodeExplorer from './CodeExplorer';
import GradeHistory from './GradeHistory';

const Dashboard = () => {
    const [analysisResults, setAnalysisResults] = useState(null);
    const [currentSection, setCurrentSection] = useState('paper');

    const handleAnalysisComplete = (results) => {
        setAnalysisResults(results);
    };

    const handleSectionChange = (section) => {
        setCurrentSection(section);
        setAnalysisResults(null); // Clear results when switching sections
    };

    const handleHistoryItemClick = async (item) => {
        try {
            const endpoint = currentSection === 'paper'
                ? `/api/grading/grades/${item.id}`
                : `/api/code-review/reviews/${item.id}`;

            const response = await fetch(endpoint, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) {
                throw new Error('Failed to fetch details');
            }

            const data = await response.json();
            setAnalysisResults(data);
        } catch (error) {
            console.error('Error fetching details:', error);
            // Handle error appropriately
        }
    };

    return (
        <div className="min-h-screen flex flex-col">
            <NavigationBar
                currentSection={currentSection}
                onSectionChange={handleSectionChange}
            />

            {currentSection === 'paper' ? (
                <div className="flex flex-1">
                    <GradeHistory 
                        type="paper"
                        onHistoryItemClick={handleHistoryItemClick}
                    />

                    <div className="flex-1 flex overflow-hidden xl:flex-row flex-col">
                        {/* Form Section */}
                        <div className="w-full overflow-y-auto border-r border-gray-200">
                            <div className="p-8">
                                <h1 className="text-3xl font-bold mb-8">Text Analysis</h1>
                                <TextAnalysisForm onAnalysisComplete={handleAnalysisComplete} />
                            </div>
                        </div>

                        {/* Results Section */}
                        <div className="w-full overflow-y-auto bg-gray-50">
                            <div className="p-8">
                                <h2 className="text-2xl font-bold mb-6">Analysis Results</h2>
                                {analysisResults ? (
                                    <AnalysisDisplay data={analysisResults} />
                                ) : (
                                    <div className="bg-white rounded-lg shadow-sm p-6 text-gray-500">
                                        Submit your text for analysis to see results here.
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            ) : (
                <div className="flex flex-1">
                    <GradeHistory 
                        type="code"
                        onHistoryItemClick={handleHistoryItemClick}
                    />
                    <div className="flex-1 bg-gray-900">
                        <CodeExplorer />
                    </div>
                </div>
            )}
        </div>
    );
};

export default Dashboard;
