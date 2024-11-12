import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Register = () => {
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: ''
    });
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await fetch('/api/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Registration failed');
            }

            // Registration successful
            navigate('/login');
        } catch (err) {
            setError(err.message);
        }
    };

    return (
        <div className='bg-[url("formbg.png")] h-screen flex justify-center items-center'>
            <div className='flex p-2 h-screen items-center w-[560px]'>
                <div className='bg-gray-100 rounded-md w-full p-10'>
                    <h2 className='text-xl font-bold mb-2 text-center'>Register</h2>
                    {error && <p className='text-red-500'>{error}</p>}
                    <form onSubmit={handleSubmit}>
                        <div className='flex flex-col border-black rounded-md py-1 gap-2'>
                            <label htmlFor="username" c>Username:</label>
                            <input
                                type="text"
                                id="username"
                                name="username"
                                value={formData.username}
                                onChange={handleChange}
                                className='border-2 border-orange-300 focus:border-orange-300 bg-inherit rounded-md p-2'
                                required
                            />
                        </div>
                        <div className='flex flex-col border-black rounded-md py-1 gap-2'>
                            <label htmlFor="email">Email:</label>
                            <input
                                type="email"
                                id="email"
                                name="email"
                                value={formData.email}
                                onChange={handleChange}
                                className='border-2 border-orange-300 focus:border-orange-300 bg-inherit rounded-md p-2'
                                required
                            />
                        </div>
                        <div className='flex flex-col border-black rounded-md py-1 gap-2'>
                            <label htmlFor="password">Password:</label>
                            <input
                                type="password"
                                id="password"
                                name="password"
                                value={formData.password}
                                onChange={handleChange}
                                className='border-2 border-orange-300 focus:border-orange-300 bg-inherit rounded-md p-2'
                                required
                            />
                        </div>
                        <div className="my-4">
                            <button type="submit" className='border-2 border-orange-300 bg-orange-300 hover:bg-orange-400 focus:bg-orange-400 transition-colors text-black font-medium rounded-md w-full p-2'>Register</button>
                        </div>
                        <div className='flex justify-between'>
                            <a href="/login" className='text-blue-500'>Sign in instead</a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default Register;