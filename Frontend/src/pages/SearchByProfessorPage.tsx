import PageTitle from "../components/PageTitle";
import SearchByProfessor from "../components/SearchByProfessor";

type Props = {
  setPage: (page: any) => void;
};

function SearchByProfessorPage({ setPage }: Props)
{
  return(
    <div className="page">
      {/* <PageTitle /> */}

      <h2>Search for UCF Professors</h2>

      <div className="search-type">
        <label>
          <input
            type="radio"
            name="searchType"
            checked
            onChange={() => setPage('searchProfessor')}
          />
          Name
        </label>

        <label>
          <input
            type="radio"
            name="searchType"
            onChange={() => setPage('searchCourse')}
          />
          Course
        </label>
      </div>

      <SearchByProfessor />
    </div>
  );
}

export default SearchByProfessorPage;