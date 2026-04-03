import PageTitle from "../components/PageTitle";

function SearchByProfessorPage()
{
    return(
        <div className="page">
            <div className="header">
                <PageTitle />
            </div>
            <div className="content">
                <h2>Search by Professor</h2>
                <SearchByProfessorPage />
            </div>
        </div>
    );

}

export default SearchByProfessorPage;