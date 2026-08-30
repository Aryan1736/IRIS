---
name: IRIS Industrial Intelligence
colors:
  surface: '#faf9f6'
  surface-dim: '#dadad7'
  surface-bright: '#faf9f6'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f4f4f0'
  surface-container: '#eeeeeb'
  surface-container-high: '#e8e8e5'
  surface-container-highest: '#e2e3df'
  on-surface: '#1a1c1a'
  on-surface-variant: '#414843'
  inverse-surface: '#2f312f'
  inverse-on-surface: '#f1f1ee'
  outline: '#727973'
  outline-variant: '#c1c8c1'
  surface-tint: '#436652'
  primary: '#022617'
  on-primary: '#ffffff'
  primary-container: '#1a3c2b'
  on-primary-container: '#82a790'
  inverse-primary: '#a9cfb7'
  secondary: '#5f5e5c'
  on-secondary: '#ffffff'
  secondary-container: '#e4e2df'
  on-secondary-container: '#656462'
  tertiary: '#1f2120'
  on-tertiary: '#ffffff'
  tertiary-container: '#343635'
  on-tertiary-container: '#9e9f9d'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#c5ecd3'
  primary-fixed-dim: '#a9cfb7'
  on-primary-fixed: '#002112'
  on-primary-fixed-variant: '#2c4e3b'
  secondary-fixed: '#e4e2df'
  secondary-fixed-dim: '#c8c6c3'
  on-secondary-fixed: '#1b1c1a'
  on-secondary-fixed-variant: '#474745'
  tertiary-fixed: '#e2e3e1'
  tertiary-fixed-dim: '#c6c7c5'
  on-tertiary-fixed: '#1a1c1b'
  on-tertiary-fixed-variant: '#454746'
  background: '#faf9f6'
  on-background: '#1a1c1a'
  surface-variant: '#e2e3df'
typography:
  headline-xl:
    fontFamily: Space Grotesk
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Space Grotesk
    fontSize: 32px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Space Grotesk
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
  body-lg:
    fontFamily: Hanken Grotesk
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Hanken Grotesk
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  label-mono:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: '1.4'
    letterSpacing: 0.1em
  label-mono-sm:
    fontFamily: JetBrains Mono
    fontSize: 10px
    fontWeight: '500'
    lineHeight: '1.4'
    letterSpacing: 0.12em
  headline-xl-mobile:
    fontFamily: Space Grotesk
    fontSize: 36px
    fontWeight: '700'
    lineHeight: '1.1'
spacing:
  unit: 4px
  gutter: 16px
  margin: 24px
  grid_opacity: '0.1'
---

## Brand & Style
The design system is a **Technical Minimalist** framework designed for the rigorous demands of infrastructure monitoring. It moves away from the ephemeral "softness" of consumer SaaS, instead adopting an institutional, analytical posture that evokes the precision of engineering blueprints and architectural documentation.

The aesthetic is governed by **Modern Brutalism**—relying on structural integrity, hairline grids, and high-quality typography rather than decorative effects. It is designed to feel authoritative and permanent, prioritizing data density and legibility over visual flair. The goal is to instill absolute trust in the technical accuracy of the intelligence being presented.

## Colors
The palette is rooted in the "Paper" background—a warm, off-white neutral that reduces eye strain during long-term monitoring sessions. 

- **Forest Green (#1A3C2B):** Used for primary actions, branding, and deep structural elements. It provides a grounded, institutional feel.
- **Primary Dark (#3A3A38):** The workhorse for text, grid lines, and iconography. Used at 20% opacity for hairlines.
- **Functional Accents:** Coral is reserved for critical alerts and status errors; Mint indicates health and successful operations; Gold is utilized for warnings and pending technical transitions.

## Typography
The typographic hierarchy emphasizes technical clarity. 

- **Headlines:** Space Grotesk is used with tight tracking to create a "locked-in" architectural feel. It should be used for project names and major section headers.
- **Body:** Hanken Grotesk (as a high-quality alternative for General Sans) provides a neutral, highly readable canvas for long-form reporting and descriptive text.
- **Technical Metadata:** JetBrains Mono is the dedicated voice for data. Every timestamp, coordinate, or serial number must be set in monospaced type to ensure character alignment and a "field-readout" aesthetic.

## Layout & Spacing
This design system utilizes a **Structural Grid Model**. The layout is guided by a 12-column grid on desktop, but the visual "skeleton" is made explicit through the use of hairline dividers (#3A3A38 at 10-20% opacity).

- **Grid Alignment:** All components must snap to the grid. White space is used as a functional separator rather than just aesthetic padding.
- **Breakpoints:** 
  - Desktop: 1440px+ (12 columns, 24px margins)
  - Tablet: 768px - 1439px (8 columns, 16px margins)
  - Mobile: <768px (4 columns, 12px margins)
- **Data Density:** In detail views, spacing is tightened to allow for maximum information visibility without scrolling.

## Elevation & Depth
Depth is strictly two-dimensional. This design system rejects the concept of Z-axis elevation (shadows) in favor of **Tonal Layering** and **Line-work**.

- **Flat Surfaces:** All cards and containers are flat color blocks.
- **Dividers:** Hierarchy is established through 1px hairline borders. Use vertical and horizontal lines to box in data clusters, mimicking a spreadsheet or a technical drawing.
- **Overlays:** When modals or dropdowns are required, they use a solid stroke and zero shadow. A slight background tint (e.g., 5% Primary Dark) can be used to distinguish the active layer.

## Shapes
Shapes are defined by **sharpness and precision**. 
- The default border radius is **0px** to maintain the "blueprint" aesthetic. 
- A maximum radius of **2px** is permitted only for interactive elements (buttons, inputs) to provide a microscopic hint of "clickability" without breaking the rigid geometry of the system.

## Components
Consistent technical styling for core elements:

- **Buttons:** Solid Forest Green for primary; hairline border for secondary. Labels must be uppercase JetBrains Mono.
- **Input Fields:** 1px hairline border bottom or full box. No rounded corners. Use a subtle highlight on focus using Accent Mint.
- **Chips/Status Tags:** Rectangular boxes with 0px radius. Use a small solid color square icon next to the monospaced label to indicate status (e.g., a Coral square for 'ALARM').
- **Cards:** Defined by a 1px hairline border. No shadow. Header area separated by a horizontal hairline.
- **Data Visualization:** Line charts must use 1.5px stroke width. Areas should use a low-opacity fill of the line color. No smoothing/curving of lines; data points should be connected with straight segments to represent "true" data transitions.
- **Imagery:** All infrastructure photography must use `mix-blend-mode: luminosity` at 90% opacity to integrate into the page. On hover, transition to full color over 200ms.