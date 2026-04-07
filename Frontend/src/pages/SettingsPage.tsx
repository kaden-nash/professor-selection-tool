import { useEffect, useState } from "react";


function SettingsPage()
{
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    useEffect(() => 
    {
        const fetchUser = async () =>
        {
            let ud:any = localStorage.getItem("user_data");
            let user = JSON.parse(ud);

            let obj = { userId: user.id };
            let js = JSON.stringify(obj);

            try
            {
                const response = await fetch(
                    'http://localhost:5000/api/getuser',
                    {
                        method: 'POST',
                        body: js,
                        headers: { 'Content-Type': 'application/json' }
                    }
                );

                let txt = await response.text();
                let res = JSON.parse(txt);

                if (res.error.length > 0)
                {
                    console.log(res.error);
                }
                else
                {
                    setEmail(res.email);
                    setPassword(res.password);
                }
            }
            catch(error:any)
            {
                console.log(error.toString());
            }
        };

        fetchUser();
    }, []);

    return(
        <div className="settings-page">

            <h1 className="settings-title">Settings</h1>

            <div className="settings-container">

                <label>Email:</label>
                <input type="text" value={email} readOnly />

                <label>Password:</label>
                <input type="text" value={password} readOnly />

                <button 
                    className="signout-button"
                    onClick={() => {
                        localStorage.removeItem("user_data");
                        window.location.href = "/";
                    }}
                >
                    Sign out
                </button>

            </div>
        </div>
    );
}

export default SettingsPage;