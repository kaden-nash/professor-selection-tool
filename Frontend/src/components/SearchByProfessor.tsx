import { useState } from 'react';

function SearchByProfessor()
{
    const [search, setSearch] = useState('');
    const [results, setResults] = useState<string[]>([]);
    const [message, setMessage] = useState('');

    async function handleSearch(event: React.FormEvent): Promise<void>
    {
        event.preventDefault();

        try
        {
            const res = await fetch('https://professor-selection-tool.onrender.com/api/professors/professors', /*Change this to the correct api */
            {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: search }),
            });

            const data = await res.json();

            if (res.ok)
            {
                setResults(data.results || []);
                setMessage('Search successful');
            }
            else
            {
                setMessage(data.msg || 'Search failed');
            }
        }
        catch (err)
        {
            setMessage('Server error');
        }
    }

    return(
        <div className="searchDiv">

            <form onSubmit={handleSearch}>
                <input
                    type="text"
                    placeholder="Enter professor name"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                />

                <button type="submit">Search</button>
            </form>

            <p>{message}</p>

            <ul>
                {results.map((prof, index) => (
                    <li key={index}>{prof}</li>
                ))}
            </ul>

        </div>
    );
}

export default SearchByProfessor;