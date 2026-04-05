import { useState } from 'react';
import './App.css';

import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import SearchByProfessorPage from './pages/SearchByProfessorPage';
import AboutPage from './pages/AboutPage';
import Header from './components/HeaderBox';

type Page = 'login' | 'register' | 'search' | 'starred' | 'settings' | 'about';

function App()
{
  const [page, setPage] = useState<Page>('search');

  return (
    <div>
      {page !== 'login' && <Header setPage={setPage} />}
      
      {page === 'login'
        ? <LoginPage onGoToRegister={() => setPage('register')} />
        : page === 'register'
        ? <RegisterPage onGoToLogin={() => setPage('login')} />
        : page === 'search'
        ? <SearchByProfessorPage />
        : page === 'about'
        ? <AboutPage />
        : page === 'starred'
        ? <div>Starred Page</div>
        : page === 'settings'
        ? <div>Settings Page</div>
        : null}
    </div>
  );
}

export default App;