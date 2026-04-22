
# 1. Parsing through courses.json strings

## Objective
- The objective of this step is to read through courses.json and do some things:
    - parse through each string representing a class
    - store it into a new file called courses_cleaned.json as part of a courses list.

## Specs
example course string:
- "ADE4382 - Teaching Adult Learners in Technical Programs"

parse as: 
- "ADE" - course code
- "4382" - course number
- "Teaching Adult Learners in Technical Programs" - course name

Special case: classes with more letters at the end of the course number. 
- These classes have H, K, C, or L (or maybe others) at the end of their course number
- To fix this problem, 2 new fields must be added to each course info object.
- hasHonorsVersion set to false by default.
- hasLab set to false by default.
- if you come across a class that has an honors version (an H or K ending) , change it to true for the base class object.
- if you come across a class that has a Lab version (L), change the hasLab to true for the base class object.
- In any case that there is a letter following a course number, remove it from the final course number you save.

# 2. Parsing through rmp_data.json's reviews

## Objective
Read through rmp_data.json and perform some changes for each review in the file.
Save the changed data to a new file called rmp_data_cleaned.json

## Specs
The reviews are have already been parsed into JSON, but we'll need to wade through each review and implement these changes. 

the "class" attribute is usually of the form "XXX1234" where X's are letters and 1234 are placeholders for numbers
However, there will be some with "XXX1234X" and some that just break this rule altogether (eg "VARIOUSXX").

For the classes that contain XXX1234X, simply remove the X. 

For any class that has more than XXX1234X, less than XXX1234, or breaks the expected pattern of XXX1234 in any other way, simply put "unknown" as class.

# 3. Parsing through ucf_catalog_professors.json

## Objective
- The objective of this step is to read through ucf_catalog_professors.json, parse it into json, and save it into a new file, "ucf_catalog_professors_cleaned.json"

## Specs
example prof string:
- "Abbas, Hadi, Professor of School of Visual Arts & Design (8/8/1995), M.F.A. (Wichita State University)"

parse as:
- "Abbas" - last name
- "Hadi" - first name
- "Professor" - role
- "School of Visual Arts and Design" - field of study
- (8/8/1995) - date prof joined UCF (please separate this into Date object from a date package someone has already made)
- "M.F.A" - level of education
- "(Wichita State University)" - prof graduated from
- remove all parenthesis from final forms of data.

Add this field to the object:
- isEmeritus - defaulted to false

at the end of the normal professors, there will be a series of strings for emeritus professors

example emeritus string: 
- "ABBOTT, DAVID W.,Professor Emeritus"
-
parse as: 
- "Abbott" - last name
- "David" - first name

Add this field to the object
- isEmeritus - true

Special case:
- Some names will have dashes and apostrophies in them. be ready for that.

# 4. Correlating data from ucf_catalog_professors.json and rmp_data.json

## Objective
Compose a new file professor_data.json that contains all the unique information found about a professor.

## Specs
- Take the fields from professor objects in ucf_catalog_professors_cleaned.json that are not found in rmp_data_cleaned's professors and add them to rmp_data_cleaned's professor objects 
- The fields to add: isEmeritus, role, field of study, date prof joined UCF, level of education, prof graduate from

Ensure you store these new professor objects in a file called professor_data.json

You should attempt to correlate these records by name. 
However, names are not always unique.

Special case during correlation: two profs of same name
    - update the professor object in rmp_data_cleaned.json who has the earliest first review date with the attributes of the professor in ucf_catalog_professors_cleaned.json who has the earliest start date. 
    - edge case that will be left unhandled due to complexity:
        - professors of identical names start on identical dates
        - professors of identical names where both first reviews are after both professors exist