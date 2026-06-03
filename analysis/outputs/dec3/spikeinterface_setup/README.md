# Dec 3 SpikeInterface Setup

This folder verifies that SpikeInterface can open the Dec 3 raw binary.

- Raw data: `/Users/paris/Documents/Buzsaki Lab/Haptic_Stim_session1_251203_143031/amplifier.dat`
- Raw channels: `128`
- Good channels after confirmed bad-channel exclusion: `119`
- Sampling rate: `20000 Hz`
- Dtype: `int16`

Outputs:

- `recording_json/recording.json`: SpikeInterface recording description.
- `spikeinterface_trace_sanity.png`: short raw-trace sanity plot.
- `spikeinterface_setup_summary.json`: metadata summary.

The raw binary is not modified. Channel locations are provisional until exact
Cambridge NeuroTech H12_2 geometry is confirmed.
