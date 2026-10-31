# DESIGN.md — Avatar-Chat-Interface Design System

## 1. Overview & Aesthetic Vision
The **Avatar-Chat-Interface** frontend is engineered with an advanced, futuristic dark-mode cybernetic aesthetic tailored for real-time 3D AI interaction. It blends deep obsidian void tones (`#07080d`) with reactive glassmorphism, crisp typography, and multi-layered atmospheric lighting in cyan, electric blue, and ultraviolet.

> **Stitch MCP Status**: Checked. Stitch MCP authentication server requires manual cloud configuration / dynamic client registration. Falling back seamlessly to the production-grade custom design token system specified in the architectural guidelines.

---

## 2. Color Palette & Atmospheric Accents

### Core Canvas & Surfaces
| Token | Hex Value | Role & Usage |
|:---|:---|:---|
| `--bg-base` | `#07080d` | Deep space obsidian primary background |
| `--bg-canvas` | `#0a0c14` | 3D scene viewport base gradient |
| `--surface-glass` | `rgba(13, 17, 28, 0.72)` | Primary frosted glass containers |
| `--surface-glass-border` | `rgba(56, 189, 248, 0.16)` | Subtle luminous container borders |
| `--surface-glass-hover` | `rgba(20, 26, 43, 0.82)` | Hover state for interactive cards |

### Neon & Accent Lighting
| Token | Hex Value | Role & Usage |
|:---|:---|:---|
| `--neon-cyan` | `#00f2fe` | Primary highlight, HUD telemetry, active state |
| `--neon-blue` | `#38bdf8` | Secondary action buttons, interactive hover borders |
| `--neon-violet` | `#8b5cf6` | Ambient gradient accent, subtle backlighting |
| `--neon-purple` | `#c084fc` | Assistant badge highlight and tertiary glow |
| `--status-online` | `#10b981` | Assistant online pill indicator (pulsing glow) |
| `--status-active` | `#06b6d4` | Microphone recording / audio activity indicator |

### Typography & Text Hierarchy
| Token | Hex Value | Role & Usage |
|:---|:---|:---|
| `--text-primary` | `#f1f5f9` | Primary headings, prompts, user dialogue |
| `--text-secondary` | `#94a3b8` | Assistant body copy, timestamps, telemetry labels |
| `--text-muted` | `#64748b` | Inactive placeholders, auxiliary metadata |
| `--text-accent` | `#38bdf8` | Interactive links, system tags, badges |

---

## 3. Typography
- **Primary Interface Font**: `Inter`, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif
- **Code & Telemetry Font**: `JetBrains Mono`, "Fira Code", monospace
- **Scale**:
  - Brand Header: `1.25rem` (20px), Semi-Bold / 700 with letter-spacing `0.05em`
  - Body / Dialogue: `0.9375rem` (15px), Regular / 400, line-height `1.6`
  - Captions / Timestamps: `0.75rem` (12px), Medium / 500, letter-spacing `0.025em`

---

## 4. Spacing, Geometry & Glassmorphism
- **Border Radius**:
  - Glass Containers: `16px` (`rounded-2xl`)
  - Buttons & Inputs: `12px` (`rounded-xl`)
  - Badges & Status Pills: `9999px` (`rounded-full`)
- **Backdrop Blur**: `backdrop-blur-md` (12px) to `backdrop-blur-lg` (16px) with saturation boost (`saturate-150`)
- **Shadows & Glows**:
  - Ambient Glow: `0 0 25px rgba(0, 242, 254, 0.12)`
  - Active Element Glow: `0 0 20px rgba(56, 189, 248, 0.28), 0 0 40px rgba(139, 92, 246, 0.16)`

---

## 5. Viewport Layout Blueprint (Split Screen)
```
+-------------------------------------------------------------+------------------------------------+
|  3D AVATAR HERO CANVAS (~68% width)                        | CONVERSATION SIDEBAR (~32% width)  |
|                                                             |                                    |
|  - Realtime Low-Poly Android / Humanoid Bust                | - Brand: Avatar-Chat-Interface     |
|  - 60 FPS Cursor Tracking & Gazing Interpolation (lerp)     | - Status: Glowing Online Pill     |
|  - Idle Floating / Breathing Harmonic Oscillator            | - Action: Clear Chat Button        |
|  - Atmospheric Depth Grid + Dynamic Rim & Point Lights     |------------------------------------|
|  - Depth Fog (`#07080d`) blending into background          | Scrollable Message Stream:         |
|                                                             |   - User Card (Right-aligned)      |
|                                                             |   - Assistant Card (Left-aligned)  |
|                                                             |   - Code highlighting & Markdown   |
|                                                             |------------------------------------|
|                                                             | Docked Input Toolbar:              |
|                                                             |   - Auto-resizing textarea         |
|                                                             |   - Attachment & Voice Toggles     |
|                                                             |   - Glowing Send button            |
+-------------------------------------------------------------+------------------------------------+
```

