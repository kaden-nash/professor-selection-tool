import Header from "../components/HeaderBox";
import SearchByProfessor from "../components/SearchByProfessor";

function SearchByProfessorPage({
  setPage
}: {
  setPage: (page: 'login' | 'register' | 'search' | 'starred' | 'settings') => void;
})
{
    return(
        <div className="page">  
            <div className="header">
                <Header setPage={setPage} />
            </div>

            <div className="content">
                <h2>Search by Professor</h2>
                <SearchByProfessor />
            </div>
        </div>
    );
}

export default SearchByProfessorPage;