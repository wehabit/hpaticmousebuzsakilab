# Data Preprocessing Pipeline
*Source: Data_preprocessing.docx*

---

## 1. Concatenate Daily Recordings
We typically record multiple files per day:
- Sleep → Maze → Sleep

Concatenate all `.dat` files:
```matlab
bz_ConcatenateDats;
bz_ConcatenateDats_NP2_SpikeGLX(fileInfo);
```
## 2. LFP Extraction
*Downsample concatenated .dat file:*
```matlab
bz_LFPfromDat(basepath);
```
## 3. Ripple Detection
Open .lfp in Neuroscope, select a ripple and noise channel

```matlab
% Ripple channel: CA1 PYR with highest ripple magnitude
% Noise channel: outside of CA1 PYR
ripples = detect_SWRs_Roman(basepath, channel, noise_channel);
```
## 4. Dentate Spike Detection
Open .lfp file using Neuroscope and select a ripple and noise 
```matlab
threshold_lvl = 5;
'HilusChannel'
'MolecularLayerChannel'
```
## 5. Up–Down State Detection
```matlab
addpath(genpath('C:\Users\BuzsakiPC002_misi\Documents\MATLAB\Down_state_Rachel'))

SWChan = 204;
smoothwin = .03;
startbins = 40;
refineDipEstimate = true;

[SlowWaves] = DetectSlowWavesMUA(pwd, SWChan, ...
    'smoothwin', smoothwin, 'startbins', startbins, ...
    'refineDipEstimate', refineDipEstimate);
```
## 6. State Scoring (Automatic brain state scoring)
```matlab
sessionInfo = bz_getSessionInfo(basepath,'editGUI',true); % mark bad channels as bad
SleepScoreMaster(basepath);
```
Background Literature:
https://www.sciencedirect.com/science/article/pii/S0896627316300563?via%3Dihub

Motion estimation: 
https://www.cell.com/neuron/pdf/S0896-6273(14)00781-8.pdf

## 7. State Scoring Manual Curation
Manual curation using TheStateEditor:
https://github.com/buzsakilab/buzcode/tree/master/detectors

## 8. Bad Channel Removal (Neuroscope)
This is a necessary step for spike sorting.

In Neuroscope:

1. Select all the bad channels in the spike group (yellow with three dots).
2. Click **“Remove channels from the group”** — this will move the bad channels into the **? group**.
3. Click on the **? group** (clicking the ? selects all channels in that group) and then choose **“Hide Channel”**. This would make those channels invisible in Neuroscope. Now all channels in the ? mark all look with a empty circle. 

## 9. Artifact Removal
If optogenetic or electrical stimulation is applied, we cut out some pieces
```matlab
RemoveArtefact_dat([basepath filesep basename '.dat'],artefact);
```
## 10. Median Subtraction (Movement noise and noise on all channels removal)
```matlab
removeNoiseFromDat(basepath,'method','substractMedian');
```
## 11. Spike Sorting
Spike_sorted: KS2.5 (Kilosort 2.5)

## 12. Manual Curation
Manual_curation of clusters with phy2

## 13. CellExplorer Processing

```matlab
session = sessionTemplate(basepath,'showGUI',true);
cell_metrics = ProcessCellMetrics('session', session);
```
##  14. Adjust Monosynaptic Connections
Reference:
https://www.sciencedirect.com/science/article/pii/S0896627317309029?via%3Dihub
Only keep textbook examples.
-**	Spike transmission probability:	Will send you a book chapter later on this ** 


## 15. Region Tagging in CellExplorer
Long linear shanks: tag each region

RSC–CA1–CA3 animals: no tagging needed; we use the shanks distributed in one region

RSC–CA1–CA3 animals with DG2 with long coverage: tag each cell in CellExplorer
```matlab
Unit_count

Pyramidal_count

Interneuron_count
```

## 16. Cell_metrics
manual curation of PYR and INT category (easy in hippocampus, other regions are difficult)

## 17. Align TTL Signals
```matlab
[alignedSignal] = Sync_NP_Intan;
```
## 18. Behavioral Analysis
```matlab
[behavior] = CB_LED2Tracking_NP_linearMaze;
```
