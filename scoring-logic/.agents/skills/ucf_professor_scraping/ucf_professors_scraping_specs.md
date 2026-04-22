# UCF Catalog Scraper Specifications

Use the following logic to crawl and extract professor data from the UCF Undergraduate Catalog.

## Target URLs
- **Root URL:** `https://www.ucf.edu/catalog/undergraduate/#/content/66bcc88ef93938001c548385`
- **Sub-pages:** None

---

## Step 1: Extract Group Links (Root Page)
1. Locate the container: `div.style__contentBody___gEuR0`
2. Target the child `<p>`  elements (of which there are many).
3. For each `<p>`, except the one that lacks a strong attribute, do step 4.
4. **Action:** 
    - Extract and save the text from the strong attribute. 
    - Extract and save the text containing 

## Step 2: Saving Text
1. Concatenate all the strings together in the order you extracted them

---

## 💾 Data Output Requirements
- **Format:** JSON
- **Structure:** A single JSON object containing an array of strings.
- **Content:** The array should only contain the professor data strings.

**Expected Output Example:**
```json
{
  "courses": [
    "Abbas, Hadi, Professor of School of Visual Arts & Design (8/8/1995), M.F.A. (Wichita State University)"
    "Abdallah, Nazih, Lecturer of Electrical Engineering Computer Science (12/21/2000), Ph.D. (University de Paris IX-Dauphin)"
    "..."
  ]
}