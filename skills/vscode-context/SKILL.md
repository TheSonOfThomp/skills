---
name: vscode-context
description: List open files in the VSCode instance containing this terminal and offer to read selected ones into conversation context
inputs:
  - name: file_selection
    type: string
    required: false
    description: Which listed files to read into context — numbers, a range (e.g. 1-3), 'all', or 'none'
outputs:
  - name: open_files_list
    type: text
    description: Numbered list of files currently open in the VSCode workspace (relative to git root)
  - name: read_files
    type: glob
    description: The selected open files read into conversation context
---

You are surfacing the files currently open in the user's VSCode editor so they can be added to the conversation context.

## Steps

### 1. Extract open files

Delegate to the bundled script, which locates the workspace storage folder(s) for the current git root and extracts open file paths (relative to the git root), one per line. Run it from the user's working directory, not from the skill directory, so it finds the right git root:

```bash
node "<this skill's directory>/scripts/vscode-extract.ts"
```

### 2. Handle errors

If the script exits with an error or prints an `ERROR:` line, report the message clearly to the user and stop. Common causes:
- Terminal is not inside a VSCode window (`TERM_PROGRAM` won't be `vscode`)
- The project folder isn't open as a VSCode workspace root

### 3. Present the list

Display the open files as a numbered list:

```
Open files in VSCode (N total):
1. path/to/FileA.ts
2. path/to/FileB.java
...
```

Paths are shown relative to the git root.

### 4. Ask which files to read

Ask: **"Which of these would you like me to read into context? Enter numbers, a range (e.g. 1-3), 'all', or 'none'."**

Then use the Read tool to read the selected files and confirm they are now in context.
