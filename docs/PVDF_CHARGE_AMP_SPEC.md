# PVDF Charge-Amplifier Front-End — spec for the delivered-vibration sensor

Reference design for the small board that conditions the **PVDF force sensor**
(in the tactor→skin path) into a clean analog voltage for an **Intan analog
input**. Tuned to this rig's confirmed constraints. This is a starting design
for the hardware engineer to review/validate, not a final layout.

## Confirmed constraints (drive the component values)
- **Intan analog input range: 0–3.3 V, single-ended (unipolar).**
  From `info.rhd` → `eval_board_mode = 0` = Intan RHD2000 USB evaluation board.
  → the conditioned signal must be **biased to mid-scale ≈ 1.65 V** and swing
  within 0–3.3 V.
- **Lowest carrier = 5 Hz** → high-pass corner must be **≤ 0.5 Hz** so phase is
  not distorted in-band.
- **Amplitudes 100 / 180 / 250** → set gain so the loudest (250) nearly fills the
  range without clipping and the quietest (100) stays well above noise.
- PVDF is a **high-impedance charge source** → needs a charge amp located **at
  the sensor**, not long wires into the Intan.

## Topology
Standard inverting **charge amplifier** (output referenced to a 1.65 V mid-rail),
followed by a series/anti-alias/clamp output stage into the Intan ADC.

```
        PVDF film
        (charge source)            Cf  (1 nF)
                          ┌──────────||──────────┐
                          │                       │
                          │        Rf (1 GΩ)      │
                          ├────────/\/\/\─────────┤
                          │                       │
  signal electrode ───────┤ (−)\                  │
                          │     \____             │
                          │     /    \────────────┴───► Vout
  ground electrode ──┐    │    /   U1 (OPA320, RRIO,
                     │  ┌─┤ (+)/    FET-input, 3.3 V single supply)
                    GND │ │   /
                        │ └──/
                        │
                  Vref = 1.65 V  ◄── 3.3 V through Rd1/Rd2 (100k/100k) + Cref (1 µF) to GND
                                     (high-Z node; no buffer needed)

  Vout ──[ Rs 1k ]──┬──[ Raa 1k ]──┬───────────────► Intan ADC-in (0–3.3 V)
                    │              │
              (D1 BAT54S        Caa 100 nF
            clamp to GND        to GND  (anti-alias ~1.6 kHz)
              and to 3.3 V)
```

- AC transfer (above the high-pass corner): **Vout ≈ 1.65 V − Q/Cf**, i.e. the
  vibration appears as a voltage swing around 1.65 V with size set by `Cf`.
- High-pass corner: **f_hp = 1 / (2π·Rf·Cf) = 1/(2π·1e9·1e-9) ≈ 0.16 Hz** ✓ (≤0.5 Hz).

## Component table
| Ref | Value / part | Purpose |
|---|---|---|
| U1 | **OPA320** (or OPA376 / MCP6001) — rail-to-rail I/O, FET input, ≤1 pA bias, 3.3 V | the charge amplifier |
| Cf | **1 nF**, C0G/NP0 | sets gain (Vout_ac = −Q/Cf). **Tune** so amp250 nearly fills the range |
| Rf | **1 GΩ** | DC-bias path + sets high-pass corner (≈0.16 Hz with Cf=1 nF) |
| Rd1, Rd2 | **100 kΩ** each | 3.3 V → 1.65 V mid-rail reference divider |
| Cref | **1 µF** | filters/stabilizes the 1.65 V reference |
| Rs | **1 kΩ** | series isolation + clamp current limit |
| Raa / Caa | **1 kΩ / 100 nF** | optional anti-alias LPF (~1.6 kHz; sensor BW ≪ this) |
| D1 | **BAT54S** dual Schottky | clamp ADC input to GND / 3.3 V (overrange protection) |
| Supply | **3.3 V** (same domain as the Intan analog reference) | single supply |

## Design / build notes
1. **Gain (Cf) is the one value to tune on the bench** with the actual film and
   real drive levels: if amp250 clips, increase Cf; if amp100 is near noise,
   decrease Cf. Start at 1 nF.
2. **Keep f_hp ≤ 0.5 Hz** — don't shrink Rf much below 1 GΩ. The big resistor is
   the price of clean low-frequency phase.
3. **Locate U1 + Cf + Rf right at the sensor** (short high-Z leads); send the
   low-impedance `Vout` down the cable to the Intan.
4. **Guard the high-Z node**: a guard ring at Vref potential around the (−) input
   and Rf to control leakage/drift.
5. **Single 3.3 V supply, output centered at 1.65 V**: confirm U1 is rail-to-rail
   and its bias current × 1 GΩ is a tolerable offset (OPA320 ≈ 0.2 pA → ~0.2 mV).
6. **Bench check before the session**: at rest `Vout ≈ 1.65 V`; during amp250 the
   peaks stay within ~0.2–3.1 V (no clipping); the waveform is a clean copy of the
   drive frequency.

## Why these choices (ties to the study)
- 1.65 V bias ← the Intan board is unipolar 0–3.3 V (so we center, not 0 V).
- 0.16 Hz high-pass ← below 5 Hz so the lowest carrier's phase is undistorted
  (phase is the whole point — see entrainment goal).
- Continuous analog into the Intan (not the actuator MCU) ← shares the 20 kHz
  neural clock, adds no stimulus delay/jitter.
