
### Plan
- Calculate Quality and Friction scores
- Calculate archetype taking into account all metrics
- Calculate global score
- Calculate a polarizing professor metric
- Capture top 3 tags
- Calculate time last taught
- Handle fallout of having would_take_again_percent being a string in overall score calculation
- Delete profs w/ <5 reviews from data
- Fix courses taught not being properly recorded in most professors
    - Choose only classes appended with H to survive and have a letter beyond course code

- Calculate global averages
- Replace "unavailable" would_take_again_score with global average

## Limitations
- Band-aid on bullet hole:
    - Graduate classes should be scraped from the course catalog. Currently there is no validation of those courses. Whatever a student puts goes. 
    - Profs with <5 reviews are not on here currently
    - Searching by course will only yield professors who have taught the course in the past.
    - archetype currently has hardcoded global average values from April 2026