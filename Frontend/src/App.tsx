import { useState } from 'react';
import './App.css'
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import SearchByProfessor from './components/SearchByProfessor';

function App()
{
  const [page, setPage] = useState<'login' | 'register' | 'searchProfessor'>('login');

  return page === 'login' /* change this back to the page we want to be shown*/
    ? <LoginPage onGoToRegister={() => setPage('register')} />
    : page === 'register'
    ? <RegisterPage onGoToLogin={() => setPage('login')} />
    : <SearchByProfessor />;

}

export default App;
