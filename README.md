# hpaticmousebuzsakilab
## Workshop Mishi puttogether
You might find it useful for data analysis: https://github.com/misiVoroslakos/Ephys_workshop


## 🧪 Experiment Setup Summary

### 📸 Study Images
Images from this experiment are available here:  
🔗 **https://photos.app.goo.gl/NzK9YqrbCPufYTYV8**


---

### 📅 December 4 — One Mouse, Two Shanks Implanted
The data collected is here (mishi shared with me): https://drive.google.com/drive/u/3/folders/11S4fJvwI5_ZltETXopUXOIprmO7udT9G
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

- Mishi is going to send me the amplifier.dat
- the rest I have them here: https://drive.google.com/drive/u/2/folders/1KCHj2yOEkNIjX9bO9ZMiSj2WCGB7mrga
  
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
- shank 1:  96 to 113
- shank 2: 64 to 95
- shank 3: 32 to 63
- shank 4: 0 to 31

Nick's sugestions 
https://www.frontiersin.org/journals/behavioral-neuroscience/articles/10.3389/fnbeh.2025.1685846/full
https://agencyenterprise.github.io/AnalyzingNeuralTimeSeries-Python/chapter02.html 
book by mike cohen. 
mishis book suggestion was https://mark-kramer.github.io/Case-Studies-Python/01.html


mishi's suggestions 
Mihály Vöröslakos <voroslakos@gmail.com>
Attachments
Dec 4, 2025, 3:11 PM (19 hours ago)
to me, parism@stanford.edu

https://github.com/buzsakilab/buzcode
https://cellexplorer.org/
Check out how to build event structures

https://mark-kramer.github.io/Case-Studies-Python/01.html
https://pynapple.org/
Check PETH peri-event time histogram

https://github.com/MouseLand/Kilosort

If you use Matlab with buzcode

```basepath = pwd;
cd(basepath)
basename = bz_BasenameFromBasepath(basepath);
bz_ConcatenateDats;
%%
bz_LFPfromDat(basepath);

%%
session = sessionTemplate(basepath,'showGUI',true);
%%  
[digital_on,digital_off] = Process_IntanDigitalChannels([basename,'_digitalin.dat']);
save('digitalchannels.mat','digital_on','digital_off');

digiOn = []; digiOff = [];
digiOn = sort([digital_on{1,1};digital_on{1,2};digital_on{1,3};digital_on{1,4}]); %adjust digital channels based on your recording
digiOff = sort([digital_off{1,1};digital_off{1,2};digital_off{1,3};digital_off{1,4}]);
digiAll = sort([digiOn;digiOff]);
%%
trials = floor(length(digiOn)/6);
stimulation = [];
stimulation.startSample = reshape(digiOn(1:trials*6),6,[]);
stimulation.startTime = stimulation.startSample/2e4;
stimulation.endSample = reshape(digiOff(1:trials*6),6,[]);
stimulation.endTime = stimulation.endSample/2e4;
TESmanipulation.On = stimulation.startSample; 
TESmanipulation.Off = stimulation.endSample;
TESmanipulation.timestamps = reshape(stimulation.startTime,[],1);
TESmanipulation.timestamps(1:numel(stimulation.startTime),2) = reshape(stimulation.endTime,[],1);
TESmanipulation.amplitude = [500 -500 1000 -1000 1500 -1500];  %mV
TESmanipulation.center = TESmanipulation.timestamps(:,1) + (TESmanipulation.timestamps(:,2) - TESmanipulation.timestamps(:,1))/2;
TESmanipulation.duration = TESmanipulation.timestamps(:,2) - TESmanipulation.timestamps(:,1);

save([basepath filesep basename '.TESmanipulation.manipulation.mat'],'TESmanipulation');
save([basepath filesep basename '.stimulation.mat'],'stimulation');

channels = unique(cell2mat(session.extracellular.spikeGroups.channels));
removeNoiseFromDat(basepath,'method','substractMedian','ch', channels);   %remove muscle artifacts to get better spike sorting
%% Sleep Scoring
sessionInfo = bz_getSessionInfo(basepath,'editGUI',true); %ECG channel is moved to bad
SleepScoreMaster(basepath);
TheStateEditor
```

SPIKE SORT

