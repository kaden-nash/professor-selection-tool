import { useState } from 'react';
import './App.css';

import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import SearchByProfessorPage from './pages/SearchByProfessorPage';

type Page = 'login' | 'register' | 'search' | 'starred' | 'settings';

function App()
{
  const [page, setPage] = useState<Page>('search');

  return page === 'login'
  ? <LoginPage onGoToRegister={() => setPage('register')} />
  : page === 'register'
  ? <RegisterPage onGoToLogin={() => setPage('login')} />
  : page === 'search'
  ? <SearchByProfessorPage setPage={setPage} />
  : page === 'starred'
  ? <div>Starred Page</div>
  : page === 'settings'
  ? <div>Settings Page</div>
  : null;
}

export default App;