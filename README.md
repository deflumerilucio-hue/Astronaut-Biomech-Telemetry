# Multimodal Biomechanical Telemetry Prototype

**Real-time vision-to-FEM pipeline for musculoskeletal monitoring, designed with astronaut rehabilitation in mind.**

![Status](https://img.shields.io/badge/status-research%20prototype-orange)
![Python](https://img.shields.io/badge/Python-OpenCV%20%7C%20MediaPipe-blue)
![MATLAB](https://img.shields.io/badge/MATLAB-App%20Designer%20%7C%20FEM-orange)

**Author:** Lucio De Flumeri, MSc Biomedical Engineering, Aerospace curriculum (LM-21), Università G. d'Annunzio Chieti-Pescara

---

## Overview

This project couples a **Python computer-vision front-end** with a **MATLAB finite-element back-end** to estimate, in real time, a kinematic loading proxy on the lumbar spine and feed it into a 1D non-linear viscoelastic-damage model of trabecular bone.

The motivating use case is **post-flight rehabilitation of astronauts** affected by microgravity-induced musculoskeletal deconditioning: a low-cost, camera-only setup that links posture to a simulated structural response of bone tissue.

> **Scope.** This is a research and portfolio prototype. It is not a validated medical device and not flight hardware. Outputs are qualitative indicators, not clinical measurements.

<!-- TODO: add a demo GIF here (recommended: 10–15 s screen capture of webcam + MATLAB HMI side by side) -->
<!-- ![Demo](assets/demo.gif) -->

---

## Architecture

```
 Webcam ──► Python vision module ──UDP 127.0.0.1:5006 @ ~30 Hz──► MATLAB HMI
            (OpenCV + MediaPipe Holistic)     payload: "strain,stress_index"
                                                                       │
                                               ┌───────────────────────┴───────────────────────┐
                                               ▼                                               ▼
                                     Telemetry buffers                            1D viscoelastic-damage
                                     (sliding window, live plots)                 FEM solver + 3D rendering
```

The two processes are fully decoupled: computer-vision inference runs in Python, numerical computation runs in MATLAB, and the only interface between them is a lightweight UDP stream. The MATLAB app launches and terminates the Python process itself.

---

## Modules

### 1. Python vision module: `sensore_multimodale.py`

| Signal | How it is computed | What it represents |
|---|---|---|
| **Trunk compression proxy (ε)** | Vertical shoulder–hip distance relative to an upright calibration baseline, clamped to a physiological range | A kinematic proxy used to drive the bone model. It is **not** a direct measurement of vertebral strain |
| **Facial tension index (0–100)** | Normalized Euclidean distance between inner-eyebrow landmarks (MediaPipe Face Mesh) | An exploratory proxy for effort or discomfort during exercise. It is **not** a validated stress measure |

Payload format: `strain,stress_index` (CSV string), sent through a non-blocking UDP socket.

### 2. MATLAB HMI and solver: `AeroSport_HMI.mlapp`

- **Constitutive model:** 1D non-linear viscoelasticity with an equilibrium and a non-equilibrium stress branch, coupled to a continuum damage variable *d* ∈ [0, 1].
- **Integration:** predictor–corrector scheme with guards on time-step size (Δt), strain bounds and state variables to keep the solver stable on noisy real-time input.
- **Visualization:** sliding-window telemetry plots and a 3D cylinder that deforms with the computed response.

<!-- TODO: add the constitutive equations actually implemented (stress decomposition, evolution law of d). This is the most convincing section for a technical reviewer. -->

---

## Assumptions and limitations

- The camera gives 2D landmarks only: out-of-plane motion and camera distance affect the compression proxy.
- The mapping from trunk kinematics to vertebral loading is a modelling assumption, not a validated biomechanical relation.
- Material parameters come from the literature on trabecular bone and have not been fitted to subject-specific data.
- The facial index is sensitive to lighting, head pose and individual anatomy.

Stating these limits explicitly is intentional: they define the next validation steps.

---

## Getting started

```bash
pip install -r requirements.txt   # opencv-python, mediapipe, numpy
```

1. Open `AeroSport_HMI.mlapp` in MATLAB (R20XX or later).
2. Press **Start**: the app launches the Python module and begins listening on UDP port 5006.
3. Stand upright in front of the webcam for the calibration baseline, then move.

<!-- TODO: confirm MATLAB version and any required toolboxes -->

---

## Repository structure

```
.
├── sensore_multimodale.py     # Python vision module
├── AeroSport_HMI.mlapp        # MATLAB app (HMI + solver)
├── AeroSport_HMI_export.m     # Readable export of the app code
├── requirements.txt
└── assets/                    # Screenshots and demo GIF
```

---

## Roadmap

- [ ] Replace the webcam proxy with wearable IMUs and compare the two signals
- [ ] Validate the compression proxy against a reference motion-capture recording
- [ ] Port the solver to Python to remove the MATLAB dependency
- [ ] Integrate the variational viscoelastic-plastic-damage bone model from my BSc thesis

---

## Author

**Lucio De Flumeri**, Aerospace Biomedical Engineering, computational biomechanics of bone in microgravity
[LinkedIn](https://www.linkedin.com/in/lucio-de-flumeri/) · deflumerilucio@gmail.com

Feedback and collaboration proposals are welcome.
