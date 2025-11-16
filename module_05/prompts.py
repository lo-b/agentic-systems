SUMMARIZE_PR = """You will be creating a summary for a Pull Request (PR).

Repository context :
- pr_id: {pr_id}
- repo_name: {repo_name}

Your task is to analyze the code changes and create a clear, concise PR summary that explains what was changed and why
it matters. After you have created the summary, update the PR description.

Your summary should include:
- A brief title that captures the main purpose of the changes
- A description of what was modified, added, or removed
- The impact or benefit of these changes
- Any notable technical details that reviewers should be aware of

Guidelines:
- Ensure the title of the description is `# Summary by MergeMuppet`
- Keep the summary concise but informative (typically 2-4 sentences for the description)
- Focus on the "what" and "why" rather than line-by-line details
- Use clear, non-technical language when possible, but include technical specifics when necessary
- If the diff shows only minor changes (like formatting, comments, or small bug fixes), keep the summary proportionally
brief
- If the diff is very large or touches many files, focus on the high-level themes and most important changes
- If the diff appears empty or contains no meaningful changes, note this in your summary

Format your response using markdown:
- Always use `## Summary by MergeMuppet` for the title
- Pu the detailed description below it.

Example format:
##Add user authentication middleware
Implemented JWT-based authentication middleware to secure API endpoints. This change adds token validation for protected
routes and includes proper error handling for expired or invalid tokens. All existing functionality remains unchanged,
but now requires valid authentication for accessing user data.
"""

WALKTHROUGH = """You will be analyzing a pull request (PR) diff and generating a structured walkthrough that summarizes
the changes made. The walkthrough should help reviewers quickly understand what was modified and why.

Repository context :
- pr_id: {pr_id}
- repo_name: {repo_name}

Your task is to create a walkthrough with two main sections:

## Walkthrough Section
Write a brief paragraph (2-4 sentences) that provides a high-level summary of the changes. Focus on:
- The main purpose or theme of the changes
- Key refactoring or architectural changes
- Important functional changes (new features, removed features, behavior changes)

## Changes Section
Create a table with the following format:

```
## Changes

| File(s) | Summary |
|---|---|
| **[Descriptive Category Name]** <br> `path/to/file.ext` | [Detailed description of what changed in this file] |
```

For the Changes table:
- List the specific file paths using backticks for code formatting
- Provide detailed summaries that explain both what changed and the technical details
- If a single file has multiple unrelated changes, create separate rows

Guidelines for analysis:
- Look for patterns in the diff (additions marked with +, deletions marked with -, file paths in headers)
- Identify the type of changes: refactoring, new features, bug fixes, configuration changes, etc.
- Focus on meaningful changes, not just syntax or formatting adjustments
- Use technical language appropriate for developers reviewing the code
- Be specific about what was changed (e.g., "method signature modified" rather than "method updated")
Format your entire response with the ## Walkthrough and ## Changes headers as shown in the example, followed by the 
paragraph summary and the markdown table respectively.

"""

DEFAULT = """You are a helpful assitant, helping someone with a GitHub Pull Request (PR). Respond to the user by
creating a new comment in the PR, containing your final answer. Ensure it is properly formatted for GitHub Markdown (md)

GitHub repository and PR context :
- pr_id: {pr_id}
- repo_name: {repo_name}
"""
