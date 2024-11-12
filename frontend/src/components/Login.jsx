import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Login = () => {
    const [formData, setFormData] = useState({
        username: '',
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
            // Convert form data to URLSearchParams as required by OAuth2
            const params = new URLSearchParams();
            params.append('username', formData.username);
            params.append('password', formData.password);

            const response = await fetch('/api/auth/token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: params
            });

            if (!response.ok) {
                throw new Error('Invalid credentials');
            }

            const data = await response.json();

            // Store the token in localStorage
            localStorage.setItem('token', data.access_token);

            // Redirect to home or dashboard
            navigate('/');
        } catch (err) {
            setError(err.message);
        }
    };

    return (
        <div className='bg-[url("formbg.png")] h-screen flex justify-center items-center'>
            <div className='flex p-2 h-screen items-center w-[560px]'>
                <div className='bg-gray-100 rounded-md w-full p-10'>
                    <h2 className='text-xl font-bold mb-2 text-center'>Sign in</h2>
                    {error && <p style={{ color: 'red' }}>{error}</p>}
                    <form onSubmit={handleSubmit}>
                        <div className='flex flex-col border-black rounded-md gap-2'>
                            <label htmlFor="username">Username:</label>
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
                        <div className='flex flex-col border-black rounded-md py-2 gap-2'>
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
                            <button type="submit" className='border-2 border-orange-300 bg-orange-300 hover:bg-orange-400 focus:bg-orange-400 transition-colors text-black font-medium rounded-md w-full p-2'>Sign in</button>
                        </div>
                        <div className='flex justify-between'>
                            <a href="/register" className='text-blue-500'>Create a new account</a>
                            <p className='text-blue-500'>Forgot password?</p>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default Login;