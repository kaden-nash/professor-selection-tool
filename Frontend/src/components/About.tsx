function About()
    {
        return(
            <div className="about-container">

                <h1 className="title">How It Works</h1>
                <p className="subtitle">Talk about scoring algo + archetypes</p>

                <hr />

                <div className="score-section">
                    <p><strong>Retake Score:</strong> Description here</p>
                    <p><strong>Quality Score:</strong> Description here</p>
                    <p><strong>Difficulty Score:</strong> Description here</p>
                </div>

                <hr />

                <div className="archetype">
                    <img src="/unicorn.png" alt="Unicorn" />
                    <div>
                        <h3>The Unicorn</h3>
                        <p>Description...</p>
                    </div>
                </div>

                <div className="archetype">
                    <img src="/unicorn.png" alt="Mastermind" />
                    <div>
                        <h3>The Mastermind</h3>
                        <p>Description...</p>
                    </div>
                </div>

                <div className="archetype">
                    <img src="/unicorn.png" alt="Saboteur" />
                    <div>
                        <h3>The Saboteur</h3>
                        <p>Description...</p>
                    </div>
                </div>

                <div className="archetype">
                    <img src="/unicorn.png" alt="NPC" />
                    <div>
                        <h3>The NPC</h3>
                        <p>Description...</p>
                    </div>
                </div>

            </div>
        );
    }

    export default About;
