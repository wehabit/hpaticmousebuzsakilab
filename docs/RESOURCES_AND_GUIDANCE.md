# Resources And Guidance

This file preserves the resource links and collaborator guidance that used to
live in the root README.

## Workshop

Misi's ephys workshop:

- https://github.com/misiVoroslakos/Ephys_workshop

## Nick's Suggestions

- Frontiers article:
  https://www.frontiersin.org/journals/behavioral-neuroscience/articles/10.3389/fnbeh.2025.1685846/full
- Analyzing Neural Time Series in Python:
  https://agencyenterprise.github.io/AnalyzingNeuralTimeSeries-Python/chapter02.html
- Book by Mike Cohen

## Misi's Suggestions

From Mihaly Voroslakos, Dec 4, 2025:

- Buzcode:
  https://github.com/buzsakilab/buzcode
- CellExplorer:
  https://cellexplorer.org/
- Mark Kramer case studies:
  https://mark-kramer.github.io/Case-Studies-Python/01.html
- Pynapple:
  https://pynapple.org/
- Kilosort:
  https://github.com/MouseLand/Kilosort

Notes:

- Check how to build event structures.
- Check PETH/peri-event time histogram examples.

## MATLAB / Buzcode Guidance From Original README

The project is now Python-first, but the original MATLAB/Buzcode notes are
preserved here for comparison and for collaborators who prefer MATLAB.

```matlab
basepath = pwd;
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

## Spike Sorting References

- Kilosort:
  https://github.com/MouseLand/Kilosort
- CellExplorer:
  https://cellexplorer.org/
- Buzcode:
  https://github.com/buzsakilab/buzcode

Current repo spike-sorting notes:

- `docs/KILOSORT_PYNAPPLE_PLAN.md`
- `docs/PHY_DEC3_SETUP.md`
- `analysis/outputs/dec3/cluster_quality/index.html`
- `analysis/outputs/dec3/spike_peth_high_confidence/index.html`
