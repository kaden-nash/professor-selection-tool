import PageTitle from "./PageTitle";


type Page = 'leaderboard' | 'register' | 'search' | 'starred' | 'settings';

function Header({ setPage }: { setPage: (page: Page) => void })
{
    return(
        <div className="header-wrapper">
            <div className="headerbox">
                <div className="logo">KnightRate</div>

                <div className="nav">
                    <button onClick={() => setPage('leaderboard')}>Leaderboard</button>
                    <button onClick={() => setPage('search')}>Search</button>
                    <button onClick={() => setPage('starred')}>Starred</button>
                    <button onClick={() => setPage('settings')}>Settings</button>
                </div>
            </div>
        </div>
    );
}


export default Header;