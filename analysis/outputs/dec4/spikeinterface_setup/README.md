# Dec 4 SpikeInterface Setup

This folder verifies that SpikeInterface can open the Dec 4 raw binary.

- Raw data: `Haptic_Stim_session2_251204_131403/amplifier.dat`
- Raw channels: `256`
- Good channels after confirmed bad-channel exclusion: `210`
- Sampling rate: `20000.0 Hz`
- Dtype: `int16`

Outputs:

- `recording_json/recording.json`: SpikeInterface recording description.
- `spikeinterface_trace_sanity.png`: short raw-trace sanity plot.
- `spikeinterface_setup_summary.json`: metadata summary.

The raw binary is not modified. Channel locations are provisional until exact
Cambridge NeuroTech H12_2/H15 geometry and adapter wiring are confirmed.
