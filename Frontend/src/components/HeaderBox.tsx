type Page = 'login' | 'register' | 'search' | 'about' | 'starred' | 'settings';

function Header({ setPage }: { setPage: (page: any) => void })
{
    return(
        <div className="header-wrapper">
            <div className="headerbox">
                <h1 className="title">KnightRate</h1>

                <div className="nav-buttons"> {/* ✅ GROUP THEM */}
                    <button onClick={() => setPage('about')}>About</button>
                    <button onClick={() => setPage('search')}>Search</button>
                    <button onClick={() => setPage('starred')}>Starred</button>
                    <button onClick={() => setPage('settings')}>Settings</button>
                </div>
            </div>
        </div>
    );
}

export default Header;