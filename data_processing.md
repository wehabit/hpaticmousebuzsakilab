Concatenated
-	We typically record multiple files a day
o	Sleep – maze – sleep 
-	During this step we concatenate each file recorded during the day.
o	bz_ConcatenateDats;
o	bz_ConcatenateDats_NP2_SpikeGLX(fileInfo);

LFP
-	Down sampling of concatenated .dat file.
o	bz_LFPfromDat(basepath);

Ripple detection
-	Open .lfp file using Neuroscope and select a ripple and noise channel
o	ripple channel: channel in CA1 PYR with highest magnitude of ripple
o	noise channel: outside of CA1 PYR
o	ripples = detect_SWRs_Roman(basepath,channel,noise_channel)
Dentate Spike detection
-	Open .lfp file using Neuroscope and select a ripple and noise channel
o	threshold_lvl = 5;
o	'HilusChannel'
o	'MolecularLayerChannel'

Up-Down states detected
addpath(genpath('C:\Users\BuzsakiPC002_misi\Documents\MATLAB\Down_state_Rachel'))
SWChan = 204;
smoothwin = .03;
startbins = 40;
refineDipEstimate = true;
[SlowWaves] = DetectSlowWavesMUA(pwd,SWChan,'smoothwin',smoothwin,'startbins',startbins,'refineDipEstimate',refineDipEstimate);

Statescoring
-	Automatic brain state scoring
o	sessionInfo = bz_getSessionInfo(basepath,'editGUI',true); %bad channels are marked as bad
o	SleepScoreMaster(basepath);

-	Background literature
o	https://www.sciencedirect.com/science/article/pii/S0896627316300563?via%3Dihub
-	Motion estimation
o	https://www.cell.com/neuron/pdf/S0896-6273(14)00781-8.pdf 
Statescoring manual curation
-	Manual curation using TheStateEditor
o	https://github.com/buzsakilab/buzcode/tree/master/detectors
Bad channels removed (Neuroscope)
-	necessary for proper spike sorting
o	this should be done in Neuroscope Spike group
o	It’s done properly if the channels are moved to a group with a question mark next to them
Artifact removed
-	if optogenetic or electrical stimulation is applied, we cut out some pieces
o	RemoveArtefact_dat([basepath filesep basename '.dat'],artefact);

Median subtraction
-	helps with spike sorting to remove movement artifacts
o	removeNoiseFromDat(basepath,'method','substractMedian');   %remove muscle artifacts to get better spike sorting

Spike_sorted
-	KS2.5
Manual_curation
-	Using phy2 manual curation of clusters
CellExplorer
-	session = sessionTemplate(basepath,'showGUI',true);
-	cell_metrics = ProcessCellMetrics('session', session);

Adjust monosynaptic connections
-	https://www.sciencedirect.com/science/article/pii/S0896627317309029?via%3Dihub
-	I only keep textbook examples
-	Spike transmission probability
o	Will send you a book chapter later on this.
Region tagged in CellExplorer
-	if you record with a long ‘linear’ shank, you need to tag regions
-	in RSC-CA1-CA3 animals, we use the shanks distributed in one region, no need to tag regions, but in DG2 with long coverage, we need to tag each cell in CellExplorer
Unit_count
Pyramidal_count
Interneuron_count
Cell_metrics
-	manual curation of PYR and INT category (easy in hippocampus, other regions are difficult)
Align TTL signals
-	[alignedSignal] = Sync_NP_Intan;
Analyze behavior
[behavior] = CB_LED2Tracking_NP_linearMaze;

