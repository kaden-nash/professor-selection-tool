import React from "react";
import SearchByCourse from "../components/SearchByCourse";

type Props = {
  setPage: (page: any) => void;
};

function SearchByCoursePage({ setPage }: Props)
{
    return(
        <div className="page">
            <h2>Search for UCF courses</h2>
            <div className="search-type">
                <label>
                    <input
                        type="radio"
                        name="searchType"
                        onChange={() => setPage('searchProfessor')}
                    />Name
                </label>

                <label>
                    <input
                        type="radio"
                        name="searchType"
                        checked
                        onChange={() => setPage('searchCourse')}
                    />Course
                </label>
            </div>    
            <SearchByCourse />

        </div>
    );

}

export default SearchByCoursePage;