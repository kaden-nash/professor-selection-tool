type Page = 'login' | 'register' | 'searchProfessor' | 'about' | 'starred' | 'settings';

function Header({ setPage }: { setPage: (page: any) => void })
{
    return(
        <div className="header-wrapper">
            <div className="headerbox">
                <h1 className="title">KnightRate</h1>

                <div className="nav-buttons"> 
                    <button onClick={() => setPage('about')}>About</button>
                    <button onClick={() => setPage('searchProfessor')}>Search</button>
                    <button onClick={() => setPage('starred')}>Starred</button>
                    <button onClick={() => setPage('settings')}>Settings</button>
                </div>
            </div>
        </div>
    );
}

export default Header;