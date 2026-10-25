# Reference-style architecture stack

This is a separate portrait design inspired by the user-supplied reference GIF's dark background, dotted grid, colored layer labels and flowing connections. All architecture content belongs to Integration Hub. The previous `integration-hub-architecture-animated.*` assets remain unchanged; the generator checks their SHA-256 hashes before and after rendering.

- `integration-hub-architecture-stack.gif`: 1600 x 2100, 100 frames, 8-second infinite loop.
- `integration-hub-architecture-stack.png`: static presentation poster.
- `integration-hub-architecture-stack.svg`: editable vector artwork with animation.
- `integration-hub-architecture-stack.html`: standalone browser animation, without external assets or network requests.

The frontend reflects the recent UI revision: visible-tab polling, connection recovery and review dialogs. Local services and optional cloud extensions are distinguished. Connections illustrate architectural relationships; they are not live telemetry. Container and cloud runtime verification are not claimed.

To regenerate from the project root, using the existing environment:

```powershell
.\.venv\Scripts\python.exe -B docs/diagrams/build_architecture_stack.py
```

The renderer reuses the existing local helper scripts without modifying them. It uses installed Edge, Python packages and Windows System.Drawing; no new software or paid API calls are needed. Intermediate frames are stored in `runtime/architecture-stack`.

Verification: SVG parses; all labels fit the canvas horizontally; rendered poster visually checked; encoded GIF decoded as 1600 x 2100, 100 frames, 80 ms per frame, infinite loop. Original artwork hashes remained unchanged.
