import { useState } from 'react';

/**
 * @typedef {Object} GradingResult
 * @property {string} category
 * @property {number} score
 * @property {string} feedback
 * @property {string[]} suggestions
 * @property {string} justification
 */

/**
 * @typedef {Object} LanguageQuality
 * @property {number} grammar
 * @property {number} vocabulary
 * @property {number} style
 * @property {string} comments
 */

/**
 * @typedef {Object} AnalysisData
 * @property {string} status
 * @property {number} overall_score
 * @property {GradingResult[]} grading_results
 * @property {string} detailed_feedback
 * @property {string[]} improvement_suggestions
 * @property {LanguageQuality} language_quality
 * @property {string[]} strengths
 * @property {string[]} weaknesses
 * @property {string} error
 */

const AnalysisDisplay = ({ data }) => {
    const [isDetailedFeedbackExpanded, setIsDetailedFeedbackExpanded] = useState(false);

    // Handle error state
    if (data.error) {
        return (
            <div className="max-w-4xl mx-auto p-6">
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative">
                    <strong className="font-bold">Error: </strong>
                    <span className="block sm:inline">{data.error}</span>
                </div>
            </div>
        );
    }

    // Handle loading or empty state
    if (!data || !data.status) {
        return (
            <div className="max-w-4xl mx-auto p-6">
                <div className="bg-gray-50 border border-gray-200 text-gray-700 px-4 py-3 rounded relative">
                    No analysis data available.
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto p-6 space-y-6">
            {/* Overall Score Card */}
            <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-2xl font-bold text-gray-800">Overall Score</h2>
                        <p className="text-gray-600">
                            Status: <span className="font-semibold">{data.status}</span>
                        </p>
                    </div>
                    <div className="text-3xl font-bold text-orange-400">
                        {data.overall_score.toString().substring(0, 4)}/100
                    </div>
                </div>
            </div>

            {/* Language Quality Section */}
            <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-bold text-gray-800 mb-4">Language Quality</h2>
                <div className="grid grid-cols-3 gap-4">
                    <div className="text-center">
                        <div className="text-2xl font-bold text-orange-400">{data.language_quality.grammar}</div>
                        <div className="text-gray-600">Grammar</div>
                    </div>
                    <div className="text-center">
                        <div className="text-2xl font-bold text-orange-400">{data.language_quality.vocabulary}</div>
                        <div className="text-gray-600">Vocabulary</div>
                    </div>
                    <div className="text-center">
                        <div className="text-2xl font-bold text-orange-400">{data.language_quality.style}</div>
                        <div className="text-gray-600">Style</div>
                    </div>
                </div>
                <p className="mt-4 text-gray-600">{data.language_quality.comments}</p>
            </div>

            {/* Grading Results Section */}
            <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-bold text-gray-800 mb-4">Category Breakdown</h2>
                <div className="space-y-4">
                    {data.grading_results.map((result, index) => (
                        <div key={index} className="border-b pb-4 last:border-b-0">
                            <div className="flex justify-between items-center mb-2">
                                <h3 className="font-semibold text-gray-800">{result.criterion}</h3>
                                <span className="font-bold text-orange-400">{result.score}%</span>
                            </div>
                            <p className="text-gray-600 mb-2">{result.feedback}</p>
                        </div>
                    ))}
                </div>
            </div>

            {/* Strengths & Weaknesses Section */}
            <div className="grid grid-cols-2 gap-6">
                <div className="bg-white rounded-lg shadow-md p-6">
                    <h2 className="text-xl font-bold text-gray-800 mb-4">Strengths</h2>
                    <ul className="list-disc pl-5 space-y-2">
                        {data.strengths.map((strength, index) => (
                            <li key={index} className="text-gray-600">{strength}</li>
                        ))}
                    </ul>
                </div>
                <div className="bg-white rounded-lg shadow-md p-6">
                    <h2 className="text-xl font-bold text-gray-800 mb-4">Areas for Improvement</h2>
                    <ul className="list-disc pl-5 space-y-2">
                        {data.weaknesses.map((weakness, index) => (
                            <li key={index} className="text-gray-600">{weakness}</li>
                        ))}
                    </ul>
                </div>
            </div>

            {/* Detailed Feedback Section */}
            <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xl font-bold text-gray-800">Detailed Feedback</h2>
                    <button
                        onClick={() => setIsDetailedFeedbackExpanded(!isDetailedFeedbackExpanded)}
                        className="text-orange-400 hover:text-blue-800"
                    >
                        {isDetailedFeedbackExpanded ? 'Show Less' : 'Show More'}
                    </button>
                </div>
                <div className={`prose max-w-none ${isDetailedFeedbackExpanded ? '' : 'line-clamp-3'}`}>
                    {data.detailed_feedback}
                </div>
            </div>

            {/* Improvement Suggestions */}
            <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-bold text-gray-800 mb-4">Improvement Suggestions</h2>
                <ul className="list-disc pl-5 space-y-2">
                    {data.improvement_suggestions.map((suggestion, index) => (
                        <li key={index} className="text-gray-600">{suggestion}</li>
                    ))}
                </ul>
            </div>

            {/* Error Display (if any) */}
            {data.error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative">
                    {data.error}
                </div>
            )}
        </div>
    );
};

export default AnalysisDisplay;