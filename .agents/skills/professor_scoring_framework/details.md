
## High-Level Goal
We will likely need to add many scoring metrics as we go. Build this system with modularity, the principle of encapsulating what varies, and high reusability in mind. There will be lots of variation and edits to this system.

## Implementation Requirements

### Required Design Elements
These design patterns are required, but feel free to use others that align with the high-level goal for problems not specifically addressed below. 

- create the scoring algorithms with the strategy pattern in mind.
- the main engine should have a list of analysis classes which it performs for every professor record.
- Each analysis class will produce a JSON key value pair where the keys are the name of the metric is measures and the values are the scores it calculated.

### Data Input/Output
- Read in all of professor_data.json at the beginning of the run.
- write the entire updated list of professors and their review metrics straight to professor_ratings.json once at the end of the run as normal JSON. 
- The engine will take the JSONs produced by the analysis classes and stitch them onto the resultant professor JSON object with a key of "scores" and value of the an object which contains the pairs produced by every analysis class.