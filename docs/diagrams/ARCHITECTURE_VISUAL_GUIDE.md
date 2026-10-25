# Integration Hub architecture visual

The diagram follows an incident from the engineer workspace through the API, evidence retrieval, LangGraph analysis and verification, human approval, and local ticket/memory writes. The lower panels explain the supporting services. Optional cloud adapters are visually separated from the active local stack. Motion illustrates flow; it is not live telemetry.

## Files

- `integration-hub-architecture-animated.gif`: 1800 x 1200, 100 frames, 8-second continuous loop. Use in presentations that support animated GIFs. Some viewers show only the first frame.
- `integration-hub-architecture-animated.html`: self-contained browser presentation with smooth vector animation; no external fonts, libraries, or network requests.
- `integration-hub-architecture-animated.svg`: editable vector source with native SVG animation. Static SVG editors may display only one frame.
- `integration-hub-architecture-animated.png`: 2400 x 1600 static poster for slides and documents.

Open the HTML or GIF in a browser to view the animation. The PNG is best for printing or where motion is unsupported. All labels remain visible throughout the loop.

## Regenerate on this Windows machine

Run from `C:\Projects\integration-hub` using the existing project environment. The renderer uses an isolated headless Microsoft Edge profile, Windows System.Drawing, and the installed NumPy, httpx and websockets packages. No software installation or paid service is required.

```powershell
.\.venv\Scripts\python.exe -B docs/diagrams/build_architecture_animation.py
& .\docs\diagrams\encode_architecture_frames.ps1 -Mode sample
.\.venv\Scripts\python.exe -B docs/diagrams/assemble_architecture_gif.py palette
& .\docs\diagrams\encode_architecture_frames.ps1 -Mode encode
.\.venv\Scripts\python.exe -B docs/diagrams/assemble_architecture_gif.py assemble
```

Render intermediates and the isolated browser profile are placed under `runtime/architecture-animation`. The encoder uses an adaptive palette and transparent frame differences to retain readable labels while limiting GIF size.

## Verification

- Editable SVG parsed successfully; all text fits the canvas horizontally.
- PNG and a decoded middle GIF frame visually inspected for label readability and layout.
- GIF decoded using Windows System.Drawing: 1800 x 1200, 100 frames, 80 ms per frame, infinite looping.
- Cloud operations and container runtime are labeled unverified; no automatic production remediation is implied.
