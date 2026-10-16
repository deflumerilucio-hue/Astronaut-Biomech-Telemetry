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
 Webcam ──► Python vision module ──UDP 127.0.0.1:5006 @ frame rate──► MATLAB HMI
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
| **Trunk compression proxy (ε)** | Vertical shoulder–hip distance compared with an upright baseline (`baseline_eretta = 0.634`, normalized image units), linearly scaled and clamped to [0, 0.020] | A kinematic proxy used to drive the bone model. It is **not** a direct measurement of vertebral strain |
| **Facial tension index (0–100)** | Euclidean distance between inner-eyebrow landmarks 107 and 336 (MediaPipe Face Mesh), linearly mapped and clamped to [0, 100] | An exploratory proxy for effort or discomfort during exercise. It is **not** a validated stress measure |

Payload format: `strain,stress_index` (CSV string), sent through a non-blocking UDP socket.

### 2. MATLAB HMI and solver: `AeroSport_HMI.mlapp` (private)

> The MATLAB application and the constitutive solver are kept in a private repository. Their design is described below; code access can be discussed for research collaborations.

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
pip install -r requirements.txt   # opencv-python, mediapipe
```

```bash
python sensore_multimodale.py
```

The module opens the webcam, overlays the skeleton and face mesh with live values, and streams `strain,stress_index` to `127.0.0.1:5006` at the camera frame rate. Any UDP listener on that port can consume the stream (e.g. `nc -ul 5006` to inspect it). Press `ESC` to quit.

The upright baseline depends on camera placement: check the `Dist Raw Tronco` value shown on screen while standing and adjust `baseline_eretta` accordingly.

---

## Repository structure

```
.
├── sensore_multimodale.py     # Python vision module (public)
└── requirements.txt
                               # MATLAB HMI + solver: private
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
