import { useState } from 'react';
import './App.css';

import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import SearchByProfessorPage from './pages/SearchByProfessorPage';
import AboutPage from './pages/AboutPage';
import Header from './components/HeaderBox';
import SearchByCoursePage from './pages/SearchByCoursePage';

type Page = 'login' | 'register' | 'searchProfessor' | 'searchCourse' | 'starred' | 'settings' | 'about';

function App()
{
  const [page, setPage] = useState<Page>('searchProfessor');

  return (
    <div>
      {page !== 'login' && page !== 'register' && <Header setPage={setPage} />}
      
      {page === 'login'
        ? <LoginPage onGoToRegister={() => setPage('register')} />
        : page === 'register'
        ? <RegisterPage onGoToLogin={() => setPage('login')} />
        : page === 'searchProfessor'
        ? <SearchByProfessorPage setPage={setPage} />
        : page === 'searchCourse'
        ? <SearchByCoursePage setPage={setPage} />
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