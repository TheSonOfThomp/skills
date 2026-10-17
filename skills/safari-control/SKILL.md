---
name: safari-control
description: Control Safari on the current host Mac with AppleScript and `osascript`, including opening URLs, reading page state, filling forms, clicking elements, and running JavaScript in the active tab. Use when a workflow must be driven in Safari, when instructions mention Safari AppleScript, or when browser automation on the Mac should stay inside Safari.
inputs:
  - type: none
outputs:
  - type: none
---

# Safari Control

Drive Safari directly on the local host Mac. Prefer `osascript` with `tell application "Safari"` and `do JavaScript` in the current tab of the front window.

## Quick start

1. Bring Safari to the front.
2. Open or reuse the active tab.
3. Inspect page state with JavaScript.
4. Change the DOM with JavaScript before falling back to keystrokes.
5. Re-read state after every major action.

Example check:

```applescript
tell application "Safari"
  do JavaScript "JSON.stringify({url:location.href, title:document.title})" in current tab of front window
end tell
```

## Preferred workflow

1. Open the target URL in Safari.
2. Stabilize the window size if layout matters.
3. Read the visible page state.
4. Use JavaScript for form entry, clicks, and inspection.
5. Dispatch `input` and `change` events after setting input values.
6. Verify the resulting URL, visible text, or app state.

## Input handling

- Prefer `do JavaScript` over `System Events` keystrokes.
- For stubborn inputs, use the native value setter, then dispatch events.
- For buttons and links, prefer DOM `click()`.
- For page-specific dialogs, inspect the DOM first before guessing.

## Fallbacks

- Use `System Events` only for Safari menus, window focus, or OS-level dialogs.
- If a site blocks script-driven interaction, recover the Safari path instead of switching browsers.
- If the page is partially loaded, wait and inspect again before acting.

## Pitfalls

- Do not treat Chrome as the default browser for a Safari-required flow.
- Do not use a Linux browser path when the task explicitly depends on Safari.
- Do not rely on plain keystrokes when the page can be controlled through JavaScript.
- Do not claim success until the page state is verified.

## Example snippet

```applescript
tell application "Safari"
  activate
  tell current tab of front window
    do JavaScript "document.querySelector('button')?.click()"
  end tell
end tell
```

## Advanced features

See [REFERENCE.md](REFERENCE.md) for reusable AppleScript snippets.
