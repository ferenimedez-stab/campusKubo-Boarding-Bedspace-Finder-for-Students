# CampusKubo — Architecture Overview

This file provides a simple architectural diagram and explanation for the CampusKubo application. A PlantUML source file is included alongside this document so you can render a PNG/SVG if you prefer a visual image.

## ASCII Block Diagram (simple)
```
    [Flet UI (Desktop / Web client)]
                  |
                  v
    [Views & Components (Flet)]  <--->  [SessionState & Navigation]
                  |
                  v
    [Services Layer]
      - auth_service
      - listing_service
      - reservation_service
      - notification_service
                  |
                  v
    [Storage Layer]
      - SQLite (app/storage/campuskubo.db)
      - Local uploads (assets/uploads/)

Emerging / Optional Layers:
  - Real-time server (WebSocket / FastAPI) <--> Services Layer
  - AI Inference (local model or external API) <--> Services Layer
  - Sync & Cache layer (optional remote API + local cache)
```

## Components & Responsibilities
- Flet UI: single-page views, navbars, components, dialogs. Responsible for UI state and presentation.
- Views & Components: UI-level composition and the live-search / focus-preserving patterns.
- SessionState & Navigation: manages session last_activity, RBAC, and nav history stack.
- Services Layer: orchestrates business logic; single responsibility services (auth, listing, reservation, notifications).
- Storage Layer: primary persistence (SQLite) and local file storage for uploads.

## PlantUML (renderable)
- The `docs/architecture.puml` file contains a PlantUML source you can render locally or with an online PlantUML renderer.

Render example (local):
```bash
# Install plantuml (or use a container) and Graphviz, then:
plantuml docs/architecture.puml
# Produces docs/architecture.png
```

## Notes
- This design favors simplicity and ease of local development (SQLite, local file uploads) while enabling optional extensions (WebSocket server, AI inference, remote sync) via a clearly separated services layer and feature flags.
