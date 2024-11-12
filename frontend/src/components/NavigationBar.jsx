import React from 'react';
import PropTypes from 'prop-types';

const NavigationBar = ({ 
    currentSection = 'paper',
    onSectionChange
}) => {
    return (
        <nav className="bg-orange-200 text-black px-8 py-4 flex justify-between items-center">
            <div className="text-xl font-bold">GradeHealer</div>
            <div className="inline-flex rounded-lg p-1 bg-gray-100">
                <button
                    onClick={() => onSectionChange('paper')}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-colors
                        ${currentSection === 'paper' 
                            ? 'bg-orange-300 text-gray-900' 
                            : 'text-black hover:text-gray-600'
                        }`}
                >
                    Paper Analysis
                </button>
                <button
                    onClick={() => onSectionChange('code')}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-colors
                        ${currentSection === 'code' 
                            ? 'bg-orange-300 text-gray-900' 
                            : 'text-black hover:text-gray-600'
                        }`}
                >
                    Code Explorer
                </button>
            </div>
        </nav>
    );
};

NavigationBar.propTypes = {
    currentSection: PropTypes.oneOf(['paper', 'code']),
    onSectionChange: PropTypes.func.isRequired
};

export default NavigationBar; 