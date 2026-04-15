# UCF Catalog Scraper Specifications

Use the following logic to crawl and extract course titles from the UCF Undergraduate Catalog.

## 📍 Target URLs
- **Root URL:** `https://www.ucf.edu/catalog/undergraduate/#/courses`
- **Sub-pages:** Derived dynamically from the links found on the Root URL.

---

## 🛠️ Step 1: Extract Group Links (Root Page)
1. Locate the container: `div.style__groups___IUc1d`
2. Target the child `<ul>` and iterate through all `<li>` elements.
3. For each `<li>`, find the `<a>` tag with class `style__linkButton___zlNe4`.
4. **Action:** Extract and save the URL from the `href` attribute.

## 🛠️ Step 2: Extract Course Titles (Sub-pages)
For every URL extracted in Step 1, navigate to the page and perform the following:
1. Locate every `div` with class `style__columns___K01Hv`.
2. Find the single `<a>` tag nested within that div.
   - *Example Target:* `<a href="...">ADE4382 - Teaching Adult Learners...</a>`
3. **Action:** Extract only the **inner text** (the course code and name). **Do not** save the link.

---

## 💾 Data Output Requirements
- **Format:** JSON
- **Structure:** A single JSON object containing an array of strings.
- **Content:** The array should only contain the course title strings.

**Expected Output Example:**
```json
{
  "courses": [
    "ADE4382 - Teaching Adult Learners in Technical Programs",
    "COP3502C - Computer Science I",
    "..."
  ]
}