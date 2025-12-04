# hpaticmousebuzsakilab
## 🧪 Experiment Setup Summary

### 📸 Study Images
Images from this experiment are available here:  
🔗 **https://photos.app.goo.gl/NzK9YqrbCPufYTYV8**


---

### 📅 December 4 — One Mouse, Two Shanks Implanted
**Implant locations:**  
- Hippocampus (dHPC)
- Lateral Entorhinal Cortex (LEC) which is a gateway to hippocampus.

- Coordinate for LEC AP: 3.8 mm, ML: 3.8mm, Depth: as needed@ angle 5 degrees. - H15 probe from Cambridge NeuroTech
- Coordinate for dHPC AP: 1.8, ML: 1.5, Depth: 1 to 1.8 mm - H12_2 probe from Cambridge NeuroTech
HPC Schematics: https://labs.gaidi.ca/mouse-brain-atlas/?ml=1.5&ap=-1.8&dv=3.2


**Stimulation parameters:**  
- **Amplitudes:** 100, 180, 250  
- **Frequencies:** 5, 10, 26, 50  
- **N_REPEATS:** 200  

**Timing:**  
- **Pre-stimulation period:** 15 minutes  
- **Post-stimulation period:** >15 minutes (extended wash-out period)

---

### 📅 December 3 — Same Mouse, One Shank Implanted
**Implant location:**  
- Hippocampus

**Stimulation parameters:**  
- **Amplitudes:** 100, 180, 250  
- **Frequencies:** 5, 26  
- **N_REPEATS:** 200  

**Timing:**  
- **Pre-stimulation period:** 15 minutes  
- **Post-stimulation period:** >15 minutes

**Good/Bad channels:**
Since the LEC channel was not there, delete the the following channels form the XML file 
- 225 to 207 161 to 143
- for anotlomical there is redundency so try to delete those too
- for the dHPC
- shang 1:  96 to 113
- shange 2: 64 to 95
- shange 3: 32 to 63
- shange 4: 0 to 31
 
