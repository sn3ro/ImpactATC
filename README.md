# ImpactATC

**Macros, integration examples, and user-modifiable components for the ImpactATC automatic tool changer.**

ImpactATC is a CNC automatic tool change system that uses an **impact driver mechanism** to generate the torque required for tightening and loosening the collet nut. This approach enables higher and more consistent torque compared to typical hobby ATC systems. At its default settings, ImpactATC tightens the ER20 nut to around 35Nm.

This repository provides the **essential files needed to integrate and use ImpactATC**, including CNC macros and selected user-serviceable hardware components.

---

## 📦 What’s in this repository

- CNC macros for tool changing (e.g. LinuxCNC)
- Basic integration examples
- Selected 3D-printable parts for user interfacing (e.g. nut holder)

This repository **does not contain the full mechanical design** of ImpactATC.

---

## 📁 Repository Structure (once all the files are added)


```markdown
ImpactATC/
├─ macros/            # CNC tool-change macros and control logic
│  ├─ linuxcnc/       # LinuxCNC-specific macros (M6, subroutines, HAL)
│  └─ README.md       # Notes on usage and configuration
│
├─ hardware/          # User-modifiable hardware components only
│  ├─ stl/            # 3D-printable parts (e.g. nut holder)
│  ├─ step/           # Optional reference CAD (non-critical parts only)
│  └─ README.md       # Scope and limitations of shared hardware
│
├─ docs/              # Basic setup and integration guidance
│  └─ setup.md        # Initial setup instructions
│
└─ README.md
```
---

## ⚙️ How It Works

ImpactATC uses a mechanism inspired by an **impact driver**:

- Rotational energy is accumulated and released in controlled impacts  
- These impacts generate high peak torque  
- This enables reliable tightening and loosening of the collet nut  

This method provides improved performance over systems relying on friction or limited mechanical leverage.

---

## 🛠 Getting Started

1. Download the required macros from `macros/`  
2. Print any required parts from `hardware/`  
3. Follow setup instructions in `docs/`  
4. Integrate with your CNC controller  

---

## 🔒 Notes on Design Files

Only a subset of hardware files is included in this repository.

These are provided to:
- Allow integration with ImpactATC
- Enable user modification of interface components

They are **not a complete representation of the system design**.

---

## ⚠️ Safety

ImpactATC involves high torque and dynamic mechanical loading.

- Test carefully at low speeds  
- Ensure all components are securely mounted  
- Use appropriate guarding and PPE  

You are responsible for the safe operation of your machine.

---

## 📜 License

This project is licensed under the **MIT License**.

You are free to use, modify, and adapt the provided files.  
See the `LICENSE` file for details.

---

## 📬 Feedback

If you have questions or suggestions, feel free to open an Issue.
