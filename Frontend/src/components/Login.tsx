import { useState } from 'react';

function Login({ onGoToRegister }: { onGoToRegister: () => void })
{
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState('');

    async function doLogin(event: React.FormEvent): Promise<void>
    {
        event.preventDefault();
        try
        {
            const res = await fetch('https://professor-selection-tool.onrender.com/api/auth/login',
            {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password }),
            });
            const data = await res.json();
            if (res.ok)
            {
                localStorage.setItem('token', data.token);
                setMessage('Login successful!');
            }
            else
            {
                setMessage(data.msg || 'Login failed');
            }
        }
        catch (err)
        {
            setMessage('Server error');
        }
    }

    return(

        <div id="loginDiv">
        <h2 className="welcome-text">Welcome Back</h2>
        <input type="button" id="registerButton" className="buttons" value="Don't have an account? Sign Up" onClick={onGoToRegister} />
        <form onSubmit={doLogin}>
            <body className="login-body">Email</body>
            <input type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} />
            <input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} />
            <input type="submit" id="loginButton" className="buttons" value="Sign in" />
        </form>
        
        <span id="loginResult">{message}</span>
        </div>
    );
};

export default Login;
