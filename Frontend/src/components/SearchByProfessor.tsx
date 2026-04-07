import React, { useState } from 'react';

function SearchByProfessor()
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
      <div className='professorSearchBox'>
          <input
          type="text"
          placeholder="Search Professor..."
          onChange={handleSearchChange}
          />
      </div>

      <button onClick={searchProfessor}>Search</button>

      <ul>
        {results.map((prof, index) => (
          <li key={index}>{prof}</li>
        ))}
      </ul>
    </div>
  );
}

export default SearchByProfessor;