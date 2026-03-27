import { useState } from 'react';
import './App.css'
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';

function App()
{
  const [page, setPage] = useState<'login' | 'register'>('login');

  return page === 'login'
    ? <LoginPage onGoToRegister={() => setPage('register')} />
    : <RegisterPage onGoToLogin={() => setPage('login')} />;
}

export default App;
