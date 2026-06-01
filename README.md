# Static Site Generator

A Python-based static site generator that converts Markdown files into a structured website.

## Overview
- **Parsing:** Breaks Markdown into logical blocks (paragraphs, lists, code, etc.).
- **Node Tree:** Converts content into an internal HTML node tree.
- **Templating:** Injects generated HTML into a master template.
- **Recursion:** Processes directories to maintain the source structure.

## Key Takeaways
* **Pipeline Architecture:** I learned to manage data flow from raw text through node parsing to final rendering.
* **Idempotency:** I ensured that each build process is deterministic, meaning it produces the same result regardless of how many times it is run, preventing state corruption.

## Challenges & Solutions

### 1. Asset Path Resolution
Deploying to a subdirectory (GitHub Pages) caused broken links to CSS and images because the site wasn't at the server root.
* **Solution:** Introduced a `{{ BasePath }}` variable in the template. This dynamically prefixes assets so they always resolve correctly relative to the site root.


### 2. Path Corruption
The generator was recursively modifying links on subsequent builds, leading to corrupted URLs (e.g., `/path/path/file.css`).
* **Solution:** I refactored the pipeline to separate raw content from final HTML injection. Transformations now happen exactly once, preventing the generator from modifying its own already-processed output.
