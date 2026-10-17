# Safari Control Reference

Reusable AppleScript snippets for Safari automation on the local host Mac.

## Open a URL

```applescript
tell application "Safari"
  activate
  open location "https://example.com"
end tell
```

## Read page state

```applescript
tell application "Safari"
  do JavaScript "JSON.stringify({url:location.href, title:document.title, readyState:document.readyState})" in current tab of front window
end tell
```

## Set an input value and dispatch events

```applescript
tell application "Safari"
  do JavaScript "(() => { const el = document.querySelector('input'); if (!el) return 'missing'; const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set; setter.call(el, 'hello'); el.dispatchEvent(new Event('input', { bubbles: true })); el.dispatchEvent(new Event('change', { bubbles: true })); return el.value; })()" in current tab of front window
end tell
```

## Click an element

```applescript
tell application "Safari"
  do JavaScript "document.querySelector('button')?.click()" in current tab of front window
end tell
```

## Focus Safari and the front tab

```applescript
tell application "Safari"
  activate
  set current tab of front window to current tab of front window
end tell
```

## Inspect visible text

```applescript
tell application "Safari"
  do JavaScript "document.body.innerText.slice(0, 2000)" in current tab of front window
end tell
```

## Read localStorage

```applescript
tell application "Safari"
  do JavaScript "localStorage.getItem('key') || ''" in current tab of front window
end tell
```
