import React, { useState } from 'react';

function SearchByCourse()
{
  const [search, setSearch] = useState('');
  const [results, setResults] = useState<string[]>([]);

    //temp data-> delete later
  const professorList = [
    "Dr. Smith",
    "Dr. Johnson",
    "Dr. Williams",
    "Dr. Brown",
    "Dr. Garcia",
    "Dr. Miller",
    "Dr. Smath"
  ];

  function handleSearchChange(e: any)
  {
    setSearch(e.target.value);
  }

  function searchProfessor(e: any)
  {
    e.preventDefault();

    //remove this when adding the apii
    const filtered = professorList.filter((prof) =>prof.toLowerCase().includes(search.toLowerCase())); 
    
    // await fetch(...) --> put apu call here when its ready


    setResults(filtered);
  }

  return(
    <div>
        <input
        type="text"
        placeholder="Search Course..."
        onChange={handleSearchChange}
      />

      <button onClick={searchProfessor}>Search</button>

      <ul>
        {results.map((prof, index) => (
          <li key={index}>{prof}</li>
        ))}
      </ul>
    </div>
  );
}

export default SearchByCourse;