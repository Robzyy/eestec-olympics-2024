import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const TextAnalysisForm = ({ onAnalysisComplete }) => {
    const [formData, setFormData] = useState({
        text: '',
        subject: '',
        level: '',
        grading_criteria: [
            {
                category: '',
                weight: 1,
                description: '',
                min_score: 0,
                max_score: 100
            }
        ],
        assignment_requirements: {
            title: '',
            description: '',
            word_count: {
                min: 0
            },
            special_instructions: ''
        },
        rubric_type: 'academic'
    });
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();
    const [activeSection, setActiveSection] = useState('basic');

    // Check authentication on component mount
    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            navigate('/login');
        }
    }, [navigate]);

    const handleTextChange = (e) => {
        setFormData(prev => ({
            ...prev,
            text: e.target.value
        }));
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleRequirementsChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            assignment_requirements: {
                ...prev.assignment_requirements,
                [name]: value
            }
        }));
    };

    const handleWordCountChange = (e) => {
        const { value } = e.target;
        setFormData(prev => ({
            ...prev,
            assignment_requirements: {
                ...prev.assignment_requirements,
                word_count: {
                    min: parseInt(value) || 0
                }
            }
        }));
    };

    const handleCriteriaChange = (index, field, value) => {
        setFormData(prev => {
            const newCriteria = [...prev.grading_criteria];
            newCriteria[index] = {
                ...newCriteria[index],
                [field]: field === 'weight' ? parseFloat(value) : value
            };
            return {
                ...prev,
                grading_criteria: newCriteria
            };
        });
    };

    const addCriteria = () => {
        setFormData(prev => ({
            ...prev,
            grading_criteria: [
                ...prev.grading_criteria,
                {
                    category: '',
                    weight: 1,
                    description: '',
                    min_score: 0,
                    max_score: 100
                }
            ]
        }));
    };

    const removeCriteria = (index) => {
        setFormData(prev => ({
            ...prev,
            grading_criteria: prev.grading_criteria.filter((_, i) => i !== index)
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);

        const token = localStorage.getItem('token');
        if (!token) {
            navigate('/login');
            return;
        }

        try {
            const response = await fetch('/api/grading/grade', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify(formData),
            });

            if (response.status === 401) {
                localStorage.removeItem('token');
                navigate('/login');
                return;
            }

            if (!response.ok) {
                throw new Error('Analysis failed');
            }

            const data = await response.json();
            onAnalysisComplete(data);
        } catch (error) {
            console.error('Error:', error);
            onAnalysisComplete({ error: error.message });
        } finally {
            setIsLoading(false);
        }
    };

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);
        
        // Add other fields
        formData.append('subject', formData.subject || '');
        formData.append('level', formData.level || '');
        formData.append('grading_criteria', formData.grading_criteria || '');
        formData.append('assignment_requirements', formData.assignment_requirements || '');
        formData.append('rubric_type', formData.rubric_type || '');

        try {
            const token = localStorage.getItem('token');
            if (!token) {
                throw new Error('Not authenticated');
            }

            const response = await fetch('/api/grading/upload', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });

            if (!response.ok) {
                throw new Error('Upload failed');
            }

            const data = await response.json();
            // Update the text area with the extracted text
            setFormData(prev => ({
                ...prev,
                text: data.text
            }));
        } catch (error) {
            console.error('Error uploading file:', error);
        }
    };

    // Function to handle section clicks
    const handleSectionClick = (sectionName, e) => {
        // Prevent the default details element behavior
        e.preventDefault();
        setActiveSection(activeSection === sectionName ? null : sectionName);
    };

    return (
        <div className="max-w-4xl p-6 overflow-y-scroll">
            <form onSubmit={handleSubmit} className="space-y-6">
                {/* Basic Information Section */}
                <details 
                    className="group bg-white shadow rounded-lg" 
                    open={activeSection === 'basic'}
                >
                    <summary 
                        className="list-none cursor-pointer p-4 flex justify-between items-center"
                        onClick={(e) => handleSectionClick('basic', e)}
                    >
                        <h3 className="text-lg font-medium text-gray-900">Basic Information</h3>
                        <span className="transform group-open:rotate-180 transition-transform">
                            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                            </svg>
                        </span>
                    </summary>
                    <div className="p-4 border-t">
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Subject</label>
                                <input
                                    type="text"
                                    name="subject"
                                    value={formData.subject}
                                    onChange={handleInputChange}
                                    className="border-2 border-zinc-300 focus:border-zinc-300 bg-inherit rounded-md p-2 w-full"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Level</label>
                                <input
                                    type="text"
                                    name="level"
                                    value={formData.level}
                                    onChange={handleInputChange}
                                    className="border-2 border-zinc-300 focus:border-zinc-300 bg-inherit rounded-md p-2 w-full"
                                    required
                                />
                            </div>
                        </div>
                    </div>
                </details>

                {/* Assignment Requirements Section */}
                <details 
                    className="group bg-white shadow rounded-lg"
                    open={activeSection === 'requirements'}
                >
                    <summary 
                        className="list-none cursor-pointer p-4 flex justify-between items-center"
                        onClick={(e) => handleSectionClick('requirements', e)}
                    >
                        <h3 className="text-lg font-medium text-gray-900">Assignment Requirements</h3>
                        <span className="transform group-open:rotate-180 transition-transform">
                            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                            </svg>
                        </span>
                    </summary>
                    <div className="p-4 border-t space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Title</label>
                            <input
                                type="text"
                                name="title"
                                value={formData.assignment_requirements.title}
                                onChange={handleRequirementsChange}
                                className="border-2 border-zinc-300 focus:border-zinc-300 bg-inherit rounded-md p-2 w-full"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Description</label>
                            <textarea
                                name="description"
                                value={formData.assignment_requirements.description}
                                onChange={handleRequirementsChange}
                                className="border-2 border-zinc-300 focus:border-zinc-300 bg-inherit rounded-md p-2 w-full"
                                rows="3"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Minimum Word Count</label>
                            <input
                                type="number"
                                value={formData.assignment_requirements.word_count.min}
                                onChange={handleWordCountChange}
                                className="border-2 border-zinc-300 focus:border-zinc-300 bg-inherit rounded-md p-2 w-full"
                                min="0"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Special Instructions</label>
                            <textarea
                                name="special_instructions"
                                value={formData.assignment_requirements.special_instructions}
                                onChange={handleRequirementsChange}
                                className="border-2 border-zinc-300 focus:border-zinc-300 bg-inherit rounded-md p-2 w-full"
                                rows="2"
                            />
                        </div>
                    </div>
                </details>

                {/* Grading Criteria Section */}
                <details 
                    className="group bg-white shadow rounded-lg"
                    open={activeSection === 'criteria'}
                >
                    <summary 
                        className="list-none cursor-pointer p-4 flex justify-between items-center"
                        onClick={(e) => handleSectionClick('criteria', e)}
                    >
                        <h3 className="text-lg font-medium text-gray-900">Grading Criteria</h3>
                        <span className="transform group-open:rotate-180 transition-transform">
                            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                            </svg>
                        </span>
                    </summary>
                    <div className="p-4 border-t">
                        <button
                            type="button"
                            onClick={addCriteria}
                            className="mb-4 px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-500"
                        >
                            + Add Criteria
                        </button>
                        <div className="space-y-4">
                            {formData.grading_criteria.map((criteria, index) => (
                                <div key={index} className="border p-4 rounded-md space-y-3">
                                    
                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700">Category</label>
                                            <input
                                                type="text"
                                                value={criteria.category}
                                                onChange={(e) => handleCriteriaChange(index, 'category', e.target.value)}
                                                className="border-2 border-zinc-300 focus:border-zinc-300 bg-inherit rounded-md p-2 w-full"
                                                required
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700">Weight</label>
                                            <input
                                                type="number"
                                                value={criteria.weight}
                                                onChange={(e) => handleCriteriaChange(index, 'weight', e.target.value)}
                                                className="border-2 border-zinc-300 focus:border-zinc-300 bg-inherit rounded-md p-2 w-full"
                                                step="0.1"
                                                min="0"
                                                required
                                            />
                                        </div>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700">Description</label>
                                        <textarea
                                            value={criteria.description}
                                            onChange={(e) => handleCriteriaChange(index, 'description', e.target.value)}
                                            className="border-2 border-zinc-300 focus:border-zinc-300 bg-inherit rounded-md p-2 w-full"
                                            rows="2"
                                            required
                                        />
                                    </div>
                                    <div className="flex justify-end">
                                        {index > 0 && (
                                            <button
                                                type="button"
                                                onClick={() => removeCriteria(index)}
                                                className="text-red-600 hover:text-red-500"
                                            >
                                                Remove
                                            </button>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </details>

                {/* Essay Text Section */}
                <details 
                    className="group bg-white shadow rounded-lg"
                    open={activeSection === 'essay'}
                >
                    <summary 
                        className="list-none cursor-pointer p-4 flex justify-between items-center"
                        onClick={(e) => handleSectionClick('essay', e)}
                    >
                        <h3 className="text-lg font-medium text-gray-900">Essay Text</h3>
                        <span className="transform group-open:rotate-180 transition-transform">
                            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                            </svg>
                        </span>
                    </summary>
                    <div className="p-4 border-t">
                        <textarea
                            value={formData.text}
                            onChange={handleTextChange}
                            className="border-2 border-zinc-300 focus:border-zinc-300 bg-inherit rounded-md p-2 w-full h-64"
                            placeholder="Enter your text here..."
                            required
                        />
                    </div>
                </details>

                {/* Add file upload button */}
                <div className="flex items-center space-x-4">
                    <label className="flex items-center space-x-2 bg-gray-700 hover:bg-gray-600 text-white px-3 py-2 rounded cursor-pointer">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                        </svg>
                        <span>Upload File</span>
                        <input
                            type="file"
                            accept=".pdf,.png,.jpg,.jpeg"
                            onChange={handleFileUpload}
                            className="hidden"
                        />
                    </label>
                    {/* You can add a loading indicator or file name display here */}
                </div>

                {/* Submit Button */}
                <button
                    type="submit"
                    disabled={isLoading}
                    className={`w-full py-3 px-4 text-white font-medium rounded-lg transition-colors 
                        ${isLoading
                            ? 'bg-gray-400 cursor-not-allowed'
                            : 'bg-orange-300 hover:bg-orange-400'
                        }`}
                >
                    {isLoading ? 'Analyzing...' : 'Analyze Text'}
                </button>
            </form>
        </div>
    );
};
export default TextAnalysisForm;
