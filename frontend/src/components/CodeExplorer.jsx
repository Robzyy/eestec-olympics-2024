import React, { useState, useEffect } from 'react';
import Editor from "@monaco-editor/react";
import PropTypes from 'prop-types';
import GradeHistory from './GradeHistory';

const CodeExplorer = ({ analysisResults }) => {
    const [formData, setFormData] = useState({
        code: '// Write your code here',
        assignment_name: '',
        assignment_prompt: '',
        requirements: ['']
    });
    const [serverData, setServerData] = useState({
        status: '',
        error: null,
        overall_score: 0,
        review_results: [],
        detected_language: {
            name: '',
            confidence: 0,
            possible_languages: [],
            features: {}
        },
        improvement_suggestions: []
    });
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [editorLanguage, setEditorLanguage] = useState('javascript');
    const [reviewHistory, setReviewHistory] = useState([]);

    const handleEditorChange = (value) => {
        setFormData(prev => ({ ...prev, code: value }));
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleAnalyzeCode = async () => {
        setIsAnalyzing(true);
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                throw new Error('Not authenticated. Please login first.');
            }

            const response = await fetch('/api/code-review/review', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({
                    code: formData.code,
                    assignment_name: formData.assignment_name,
                    assignment_prompt: formData.assignment_prompt,
                    requirements: formData.requirements.filter(req => req.trim() !== ''),
                    language: editorLanguage
                })
            });

            if (response.status === 401) {
                localStorage.removeItem('token');
                throw new Error('Session expired. Please login again.');
            }

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || 'Analysis failed');
            }

            const data = await response.json();
            setServerData(data);
        } catch (error) {
            console.error('Error:', error);
            setServerData(prev => ({
                ...prev,
                error: error.message,
                status: 'error'
            }));
        } finally {
            setIsAnalyzing(false);
        }
    };


    const fetchReviewHistory = async () => {
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                throw new Error('Not authenticated. Please login first.');
            }

            const response = await fetch('/api/code-review/reviews', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.status === 401) {
                localStorage.removeItem('token');
                throw new Error('Session expired. Please login again.');
            }

            if (!response.ok) {
                throw new Error('Failed to fetch review history');
            }

            const data = await response.json();
            setReviewHistory(data);
        } catch (error) {
            console.error('Error fetching history:', error);
        }
    };

    const filterReviewData = (data) => {
        const {
            status,
            error,
            overall_score,
            review_results,
            detected_language,
            improvement_suggestions
        } = data;

        return {
            status,
            error,
            overall_score,
            review_results,
            detected_language,
            improvement_suggestions
        };
    };


    useEffect(() => {
        fetchReviewHistory();
    }, []);

    return (
        <div className="flex flex-1">
            {/* Main content */}

            <div className="flex-1 p-6">
                {/* Top Bar */}
                <div className="bg-gray-800 p-4 flex items-center justify-between border-b border-gray-700">
                    <div className="flex items-center space-x-4">
                        <select 
                            className="bg-gray-700 text-white px-3 py-2 rounded"
                            value={editorLanguage}
                            onChange={(e) => setEditorLanguage(e.target.value)}
                        >
                            <option value="javascript">JavaScript</option>
                            <option value="python">Python</option>
                            <option value="java">Java</option>
                            <option value="cpp">C++</option>
                            <option value="csharp">C#</option>
                        </select>
                        <button
                            onClick={handleAnalyzeCode}
                            disabled={isAnalyzing}
                            className={`px-4 py-2 rounded-md flex items-center space-x-2 ${
                                isAnalyzing 
                                    ? 'bg-gray-600 cursor-not-allowed' 
                                    : 'bg-orange-500 hover:bg-orange-600'
                            }`}
                        >
                            {isAnalyzing ? (
                                <>
                                    <span className="animate-spin">⚡</span>
                                    <span>Analyzing...</span>
                                </>
                            ) : (
                                <>
                                    <span>⚡</span>
                                    <span>Analyze Code</span>
                                </>
                            )}
                        </button>
                    </div>
                </div>

                {/* Main Content */}
                <div className="flex flex-1 min-h-0">
                    {/* Left Panel - Code Input */}
                    <div className="w-1/2 flex flex-col border-r border-gray-700">
                        <div className="p-4 space-y-4">
                            <input
                                type="text"
                                name="assignment_name"
                                value={formData.assignment_name}
                                onChange={handleInputChange}
                                placeholder="Assignment Name"
                                className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600"
                            />
                            
                            <textarea
                                name="assignment_prompt"
                                value={formData.assignment_prompt}
                                onChange={handleInputChange}
                                placeholder="Assignment Prompt"
                                className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 h-32"
                            />

                            <div className="space-y-2">
                                <div className="flex justify-between items-center">
                                    <span className="text-white">Requirements</span>
                                    <button
                                        onClick={() => setFormData(prev => ({
                                            ...prev,
                                            requirements: [...prev.requirements, '']
                                        }))}
                                        className="text-orange-400 hover:text-orange-300"
                                    >
                                        + Add Requirement
                                    </button>
                                </div>
                                {formData.requirements.map((req, index) => (
                                    <div key={index} className="flex space-x-2">
                                        <input
                                            type="text"
                                            value={req}
                                            onChange={(e) => {
                                                const newReqs = [...formData.requirements];
                                                newReqs[index] = e.target.value;
                                                setFormData(prev => ({
                                                    ...prev,
                                                    requirements: newReqs
                                                }));
                                            }}
                                            placeholder={`Requirement ${index + 1}`}
                                            className="flex-1 bg-gray-700 text-white px-3 py-2 rounded border border-gray-600"
                                        />
                                        {formData.requirements.length > 1 && (
                                            <button
                                                onClick={() => {
                                                    const newReqs = formData.requirements.filter((_, i) => i !== index);
                                                    setFormData(prev => ({
                                                        ...prev,
                                                        requirements: newReqs
                                                    }));
                                                }}
                                                className="text-red-400 hover:text-red-300 px-2"
                                            >
                                                ×
                                            </button>
                                        )}
                                    </div>
                                ))}
                            </div>

                            <div className="h-96 border border-gray-600 rounded">
                                <Editor
                                    height="100%"
                                    language={editorLanguage}
                                    theme="vs-dark"
                                    value={formData.code}
                                    onChange={handleEditorChange}
                                    options={{
                                        minimap: { enabled: true },
                                        fontSize: 14,
                                        padding: { top: 10 },
                                        automaticLayout: true
                                    }}
                                />
                            </div>
                        </div>
                    </div>

                    {/* Right Panel - Analysis Results */}
                    <div className="w-1/2 flex flex-col bg-gray-900 overflow-y-auto">
                        <div className="p-6 space-y-6">
                            {/* Analysis Status */}
                            <div className="bg-gray-800 rounded-lg p-4">
                                <h3 className="text-lg font-semibold text-white mb-4">Analysis Status</h3>
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="bg-gray-700 p-3 rounded">
                                        <div className="text-sm text-gray-400">Status</div>
                                        <div className="text-white font-medium">{serverData.status || 'N/A'}</div>
                                    </div>
                                    <div className="bg-gray-700 p-3 rounded">
                                        <div className="text-sm text-gray-400">Overall Score</div>
                                        <div className="text-orange-400 font-bold text-xl">
                                            {serverData.overall_score ? `${serverData.overall_score}%` : 'N/A'}
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Language Detection */}
                            <div className="bg-gray-800 rounded-lg p-4">
                                <h3 className="text-lg font-semibold text-white mb-4">Language Detection</h3>
                                <div className="space-y-4">
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="bg-gray-700 p-3 rounded">
                                            <div className="text-sm text-gray-400">Detected Language</div>
                                            <div className="text-white font-medium">
                                                {serverData.detected_language?.name || 'N/A'}
                                            </div>
                                        </div>
                                        <div className="bg-gray-700 p-3 rounded">
                                            <div className="text-sm text-gray-400">Confidence</div>
                                            <div className="text-orange-400 font-medium">
                                                {serverData.detected_language?.confidence 
                                                    ? `${serverData.detected_language.confidence}%` 
                                                    : 'N/A'}
                                            </div>
                                        </div>
                                    </div>
                                    
                                    {serverData.detected_language?.possible_languages?.length > 0 && (
                                        <div className="bg-gray-700 p-3 rounded">
                                            <div className="text-sm text-gray-400 mb-2">Other Possibilities</div>
                                            <div className="space-y-1">
                                                {serverData.detected_language.possible_languages.map((lang, idx) => (
                                                    <div key={idx} className="flex justify-between text-sm">
                                                        <span className="text-white">{lang.language}</span>
                                                        <span className="text-orange-400">{lang.score}%</span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Review Results */}
                            {serverData.review_results?.length > 0 && (
                                <div className="bg-gray-800 rounded-lg p-4">
                                    <h3 className="text-lg font-semibold text-white mb-4">Review Results</h3>
                                    <div className="space-y-3">
                                        {Object.entries(serverData.review_results).map(([category, details], idx) => (
                                            <div key={idx} className="bg-gray-700 p-3 rounded">
                                                <div className="text-orange-400 font-medium mb-2">
                                                    {category}
                                                </div>
                                                <div className="text-white text-sm whitespace-pre-wrap">
                                                    {typeof details === 'object' 
                                                        ? JSON.stringify(details, null, 2)
                                                        : details
                                                    }
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Improvement Suggestions */}
                            {serverData.improvement_suggestions?.length > 0 && (
                                <div className="bg-gray-800 rounded-lg p-4">
                                    <h3 className="text-lg font-semibold text-white mb-4">
                                        Improvement Suggestions
                                    </h3>
                                    <div className="space-y-2">
                                        {serverData.improvement_suggestions.map((suggestion, idx) => (
                                            <div key={idx} className="bg-gray-700 p-3 rounded text-white text-sm">
                                                {suggestion}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Error Display */}
                            {serverData.error && (
                                <div className="bg-red-900/50 border border-red-500/50 rounded-lg p-4">
                                    <h3 className="text-lg font-semibold text-red-300">Error</h3>
                                    <p className="text-red-200 mt-2">{serverData.error}</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

CodeExplorer.propTypes = {
    analysisResults: PropTypes.shape({
        status: PropTypes.string,
        error: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
        overall_score: PropTypes.number,
        review_results: PropTypes.arrayOf(PropTypes.shape({
            category: PropTypes.string,
            details: PropTypes.oneOfType([  
                PropTypes.string,
                PropTypes.object
            ])
        })),
        detected_language: PropTypes.shape({
            name: PropTypes.string,
            confidence: PropTypes.number,
            possible_languages: PropTypes.arrayOf(PropTypes.shape({
                language: PropTypes.string,
                score: PropTypes.number
            })),
            features: PropTypes.shape({
                syntax_elements: PropTypes.arrayOf(PropTypes.string),
                programming_paradigms: PropTypes.arrayOf(PropTypes.string),
                language_version_hints: PropTypes.arrayOf(PropTypes.string),
                frameworks_and_libraries: PropTypes.arrayOf(PropTypes.string),
                special_language_features: PropTypes.arrayOf(PropTypes.string)
            })
        }),
        improvement_suggestions: PropTypes.array,
        id: PropTypes.number,
        code: PropTypes.string,
        language: PropTypes.string,
        assignment_name: PropTypes.string,
        assignment_prompt: PropTypes.string,
        requirements: PropTypes.arrayOf(PropTypes.string),
        user_id: PropTypes.number,
        created_at: PropTypes.string,
        updated_at: PropTypes.oneOfType([PropTypes.string, PropTypes.null])
    })
};

export default CodeExplorer;