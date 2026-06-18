/**
 * @file actuator.cpp
 *
 * @brief actuator control
 *
 * @author Jason Ho
 * Contact: jho@zeitgeistus.com
 *
 * 2026-06-17 SYNC ADDITIONS (for neural-recording alignment), all marked "// SYNC":
 *   - SYNC_CYCLE_PIN : toggles a clean square once per carrier cycle (rising edge at
 *                      sine index 0) -> wire to an Intan DIGITAL input = phase clock.
 *   - TRIAL_GATE_PIN : HIGH for the whole ON window (amplitude > 0), LOW otherwise
 *                      -> wire to an Intan DIGITAL input = trial timing.
 *   Set both pin numbers below before flashing. (The ANALOG accelerometer goes
 *   straight into an Intan ADC input -- that is hardware only, no firmware here.)
 */

#include "actuator.h"
#include "logger.h"
#include "timer.h"


// ###  TACTOR ###
#define BST_SHDN_PIN 13  // Tactor driver enable
// 2026-04-02: Keep old comment for traceability only.
// #define PWM_PIN 12       // Tactor Driver enable status LED (Orange)
// 2026-04-02: PWM pin comment corrected for maintainability.
#define PWM_PIN 12       // Tactor PWM pin
// 2026-04-02: Keep old comment for traceability only.
// #define LED_PIN 11       // Tactor PWM pin
// 2026-04-02: LED pin comment corrected for maintainability.
#define LED_PIN 11       // Tactor status LED (Orange)

// SYNC 2026-06-17: set these to the two free GPIOs you wire to the Intan DIGITAL inputs.
//   (11/12/13 are taken above by LED/PWM/BST_SHDN -- pick other free pins.)
#ifndef SYNC_CYCLE_PIN
#define SYNC_CYCLE_PIN  (0xFFu)   // <<< FILL IN: per-carrier-cycle phase marker
#endif
#ifndef TRIAL_GATE_PIN
#define TRIAL_GATE_PIN  (0xFFu)   // <<< FILL IN: HIGH during the ON window
#endif
#if (SYNC_CYCLE_PIN == 0xFFu) || (TRIAL_GATE_PIN == 0xFFu)
#warning "SYNC: set SYNC_CYCLE_PIN and TRIAL_GATE_PIN to your wired GPIO numbers before flashing."
#endif

// 2026-04-02: Replace magic constants with explicit waveform/timer constants.
#define SINE_TABLE_SIZE (256u)
#define SINE_INDEX_MASK (SINE_TABLE_SIZE - 1u)
#define TIMER2_TICK_HZ  (1000000UL)
#define DEFAULT_SINE_FREQ_HZ (600u)
#define MAX_ACTUATOR_FREQ_LIMIT (250u) // 2026-04-02: Clamp requested actuator frequency to safe max (Hz).

// 2026-04-02: Keep old variables as comments for traceability only.
// volatile uint8_t sine_index1 = 0;

// 2026-04-02: Keep old 50-point table as comments for traceability only.
// const unsigned char sine[50] =
// {
//     128, 144, 160, 175, 189, 203, 215, 226, 235, 243, 249, 253, 255,
//     255, 253, 249, 243, 235, 226, 215, 203, 189, 175, 160, 144, 128,
//     112, 96, 81, 67, 53, 41, 30, 21, 13, 7, 3, 1, 1, 3, 7, 13, 21,
//     30, 41, 53, 67, 81, 96, 112
// };

// 2026-04-02: 256-point sine table improves waveform smoothness and reduces audible stepping.
// SYNC 2026-06-17: STANDARD mid-rise table = the production waveform (test table below is
// DISABLED via #if 0). index 0 = rising zero-crossing, so SYNC_CYCLE_PIN's rising edge marks
// stimulus phase 0 deg (the conventional reference, and the max-slope point => precise mark).
const uint8_t sine_table[SINE_TABLE_SIZE] =
{
    128, 131, 134, 137, 140, 143, 146, 149, 152, 155, 158, 162, 165, 167, 170, 173,
    176, 179, 182, 185, 188, 190, 193, 196, 198, 201, 203, 206, 208, 211, 213, 215,
    218, 220, 222, 224, 226, 228, 230, 232, 234, 235, 237, 238, 240, 241, 243, 244,
    245, 246, 248, 249, 250, 250, 251, 252, 253, 253, 254, 254, 254, 255, 255, 255,
    255, 255, 255, 255, 254, 254, 254, 253, 253, 252, 251, 250, 250, 249, 248, 246,
    245, 244, 243, 241, 240, 238, 237, 235, 234, 232, 230, 228, 226, 224, 222, 220,
    218, 215, 213, 211, 208, 206, 203, 201, 198, 196, 193, 190, 188, 185, 182, 179,
    176, 173, 170, 167, 165, 162, 158, 155, 152, 149, 146, 143, 140, 137, 134, 131,
    128, 124, 121, 118, 115, 112, 109, 106, 103, 100, 97, 93, 90, 88, 85, 82,
    79, 76, 73, 70, 67, 65, 62, 59, 57, 54, 52, 49, 47, 44, 42, 40,
    37, 35, 33, 31, 29, 27, 25, 23, 21, 20, 18, 17, 15, 14, 12, 11,
    10, 9, 7, 6, 5, 5, 4, 3, 2, 2, 1, 1, 1, 0, 0, 0,
    0, 0, 0, 0, 1, 1, 1, 2, 2, 3, 4, 5, 5, 6, 7, 9,
    10, 11, 12, 14, 15, 17, 18, 20, 21, 23, 25, 27, 29, 31, 33, 35,
    37, 40, 42, 44, 47, 49, 52, 54, 57, 59, 62, 65, 67, 70, 73, 76,
    79, 82, 85, 88, 90, 93, 97, 100, 103, 106, 109, 112, 115, 118, 121, 124,
};

// SYNC 2026-06-17: TEST-ONLY phase-shifted table (index 0 = waveform minimum), kept for
// startup-transient experiments. DISABLED for production via #if 0; the STANDARD table
// above is the one compiled. Do not enable both (redefinition).
#if 0
const uint8_t sine_table[SINE_TABLE_SIZE] =
 {
     0, 0, 0, 0, 1, 1, 1, 2, 2, 3, 4, 5, 5, 6, 7, 9,
     10, 11, 12, 14, 15, 17, 18, 20, 21, 23, 25, 27, 29, 31, 33, 35,
     37, 40, 42, 44, 47, 49, 52, 54, 57, 59, 62, 65, 67, 70, 73, 76,
     79, 82, 85, 88, 90, 93, 97, 100, 103, 106, 109, 112, 115, 118, 121, 124,
     128, 131, 134, 137, 140, 143, 146, 149, 152, 155, 158, 162, 165, 167, 170, 173,
     176, 179, 182, 185, 188, 190, 193, 196, 198, 201, 203, 206, 208, 211, 213, 215,
     218, 220, 222, 224, 226, 228, 230, 232, 234, 235, 237, 238, 240, 241, 243, 244,
    245, 246, 248, 249, 250, 250, 251, 252, 253, 253, 254, 254, 254, 255, 255, 255,
     255, 255, 255, 255, 254, 254, 254, 253, 253, 252, 251, 250, 250, 249, 248, 246,
     245, 244, 243, 241, 240, 238, 237, 235, 234, 232, 230, 228, 226, 224, 222, 220,
     218, 215, 213, 211, 208, 206, 203, 201, 198, 196, 193, 190, 188, 185, 182, 179,
     176, 173, 170, 167, 165, 162, 158, 155, 152, 149, 146, 143, 140, 137, 134, 131,
     128, 124, 121, 118, 115, 112, 109, 106, 103, 100, 97, 93, 90, 88, 85, 82,
     79, 76, 73, 70, 67, 65, 62, 59, 57, 54, 52, 49, 47, 44, 42, 40,
     37, 35, 33, 31, 29, 27, 25, 23, 21, 20, 18, 17, 15, 14, 12, 11,
     10, 9, 7, 6, 5, 5, 4, 3, 2, 2, 1, 1, 1, 0, 0, 0,
};
#endif  // SYNC 2026-06-17: end of disabled test table
// 2026-04-02: Shared ISR/main-loop state to remove waveform jitter from loop timing.
static volatile uint8_t g_sine_index = 0u;
static volatile uint8_t g_output_level = 0u;
static volatile bool g_pwm_active = false;


// Global actuator
Actuator MM3C(PWM_PIN);


// 2026-04-02: Centralized frequency -> timer compare conversion to avoid duplicated magic math.
static void timer2_set_sine_frequency(uint16_t freq_hz)
{
    if (freq_hz == 0u)
    {
        return;
    }

    const uint16_t bounded_freq_hz = (freq_hz > MAX_ACTUATOR_FREQ_LIMIT) ? MAX_ACTUATOR_FREQ_LIMIT : freq_hz; // 2026-04-02: Limit requested frequency to configured maximum.
    const uint32_t denominator = ((uint32_t) bounded_freq_hz) * SINE_TABLE_SIZE; // 2026-04-02: Use bounded frequency for timer compare calculation.
    uint32_t cc_value = (TIMER2_TICK_HZ + (denominator / 2u)) / denominator;

    if (cc_value == 0u)
    {
        cc_value = 1u;
    }

    NRF_TIMER2->CC[0] = (uint16_t) cc_value;
}


void drv_en() {
    // Serial.println("drv_en");
    // 2026-04-02: Old behavior kept for traceability only.
    // HwPWM0.begin();
    // digitalWrite(BST_SHDN_PIN, HIGH);  //Tactor Driver enabled
    // digitalWrite(LED_PIN, HIGH);       // Tactor PWM LED on (no need to keep it ons)

    // 2026-04-02: Enable hardware only on transition to reduce repeated begin() calls.
    if (!g_pwm_active) {
        HwPWM0.begin();
        digitalWrite(BST_SHDN_PIN, HIGH);  // Tactor Driver enabled
        digitalWrite(LED_PIN, HIGH);       // Tactor status LED on
        g_pwm_active = true;
    }
}

void drv_dis() {
    // Serial.println("drv_dis");
    // 2026-04-02: Old behavior kept for traceability only.
    // digitalWrite(BST_SHDN_PIN, LOW);  //Tactor Driver disabled
    // digitalWrite(LED_PIN, LOW);       // Tactor PWM LED off
    // HwPWM0.stop();

    // 2026-04-02: Disable hardware only on transition and clear ISR-shared output level.
    if (g_pwm_active) {
        g_pwm_active = false;
        g_output_level = 0u;
        digitalWrite(BST_SHDN_PIN, LOW);  // Tactor Driver disabled
        digitalWrite(LED_PIN, LOW);       // Tactor status LED off
        digitalWrite(SYNC_CYCLE_PIN, LOW); // SYNC: park phase-marker line low while idle
        digitalWrite(TRIAL_GATE_PIN, LOW); // SYNC: trial gate low while idle
        HwPWM0.stop();
    }
}


void actuator_init(
    void)
{
    // TACTOR and LED for TACTOR
    pinMode(BST_SHDN_PIN,OUTPUT); //PIN for the tactors
    pinMode(LED_PIN, OUTPUT); // Tactor PWM LED off

    // SYNC 2026-06-17: outputs for the neural-recording sync lines.
    pinMode(SYNC_CYCLE_PIN, OUTPUT);
    pinMode(TRIAL_GATE_PIN, OUTPUT);
    digitalWrite(SYNC_CYCLE_PIN, LOW);
    digitalWrite(TRIAL_GATE_PIN, LOW);

    // setup pwm
    HwPWM0.addPin(PWM_PIN);
    HwPWM0.setResolution(8); // 256 values  16e6/2^8 = 62.5 kHz base frequency

    // timer 2 for PWM frequency
    NRF_TIMER2->TASKS_STOP = 1;
    NRF_TIMER2->MODE = TIMER_MODE_MODE_Timer;  // Set the timer in Counter Mode
    NRF_TIMER2->BITMODE = TIMER_BITMODE_BITMODE_16Bit;     // Set counter to 16 bit resolution
    NRF_TIMER2->PRESCALER = 4;   // Prescaler = 4 gives 1MHz counter

    //tactor specific (MM3C)
    /*
    NRF_TIMER2->CC[0] = 235;
    // value for compare register 0: 1e6/235/50 = 85Hz (Resonant frequency for MM3C)
    // this is basically "clear timer counter on compare match"
    */
    // 2026-04-02: Keep old hardcoded line for traceability only.
    // NRF_TIMER2->CC[0] = 33;    // value for compare register 0: 1e6/33/50 = 600Hz (Resonant frequency TEAX14)
    // 2026-04-02: Use centralized helper with 256-point sine table.
    timer2_set_sine_frequency(DEFAULT_SINE_FREQ_HZ);

    // this is basically "clear timer counter on compare match"
    NRF_TIMER2->SHORTS = (TIMER_SHORTS_COMPARE0_CLEAR_Enabled << TIMER_SHORTS_COMPARE0_CLEAR_Pos);

    // enable interrupt at IP
    NRF_TIMER2->INTENSET = (TIMER_INTENSET_COMPARE0_Enabled << TIMER_INTENSET_COMPARE0_Pos);
    // NVIC_SetPriority(TIMER2_IRQn, 6); // can't use 0,1,2,4,5
    NVIC_EnableIRQ(TIMER2_IRQn); // enable isr in interrupt controller

    // start the timer
    NRF_TIMER2->TASKS_START = 1;
}


// Timer ISR
extern "C"
{
    void TIMER2_IRQHandler()
    {
        if (NRF_TIMER2->EVENTS_COMPARE[0])
        {
            // 2026-04-02: Clear event immediately to reduce ISR re-entry jitter.
            NRF_TIMER2->EVENTS_COMPARE[0] = 0;

            // 2026-04-02: Keep old index update for traceability only.
            // if(++sine_index1 == 50)
            // {
            //     sine_index1 = 0;
            // }

            // 2026-04-02: Wrap index with mask for 256-point table.
            g_sine_index = (uint8_t) ((g_sine_index + 1u) & SINE_INDEX_MASK);

            // SYNC 2026-06-17: per-carrier-cycle phase marker, ONLY while actually
            // delivering (amplitude > 0). Square wave at the carrier frequency: rising
            // edge at index 0 (= rising zero-crossing for the standard table => stimulus
            // phase 0 deg), falling edge at the half-cycle. Parked LOW during OFF/idle
            // (see UpdateLevel / drv_dis). Each rising edge is a fixed-phase reference.
            if (g_pwm_active && g_output_level > 0u)
            {
                if (g_sine_index == 0u)
                {
                    digitalWrite(SYNC_CYCLE_PIN, HIGH);
                }
                else if (g_sine_index == (uint8_t) (SINE_TABLE_SIZE / 2u))
                {
                    digitalWrite(SYNC_CYCLE_PIN, LOW);
                }
            }

            // 2026-04-02: Write PWM in ISR for deterministic sample timing.
            if (g_pwm_active)
            {
                const uint16_t duty_cycle = ((uint16_t) sine_table[g_sine_index] * g_output_level) / 255u;
                HwPWM0.writePin(PWM_PIN, duty_cycle, false);
            }
        }
    }
}


void actuator_task(
    void)
{
    // 2026-04-02: Keep old behavior for traceability only.
    // if(MM3C.Effects.isEmpty())
    // {
    //     drv_dis();  // turn off boost converter
    // } else
    // {
    //     drv_en();  //turn the PWM driver and LED on
    // }

    // 2026-04-02: Transition-only driver control avoids repeated begin()/stop() calls per loop.
    static bool driver_enabled = false;
    const bool has_effects = !MM3C.Effects.isEmpty();

    if (has_effects)
    {
        if (!driver_enabled)
        {
            drv_en();
            driver_enabled = true;
        }
    }
    else
    {
        if (driver_enabled)
        {
            drv_dis();
            driver_enabled = false;
        }
    }

    MM3C.Update();
}


void actuator_play_default_pattern(
    void)
{
    pattern_s* default_pattern = logger_pattern_get(true);
    uint8_t seq_len = default_pattern->len;
    play_mode_e play_mode = default_pattern->play_mode;

    uint8_t cont = (TIMER == play_mode) ? 1u : (uint8_t) play_mode;

    for (int i=0; i<seq_len; i++)
    {
        Sequence_s seq = default_pattern->seq_list[i];

        if ('M' == seq.seq_type)
        {
            MM3C.AddEffect(seq.mSeq.startAmplitude, seq.mSeq.endAmplitude, seq.mSeq.durationMillis, seq.mSeq.frequency, cont);
        } else if ('P' == seq.seq_type)
        {
            MM3C.AddEffect(seq.pSeq.amplitude, seq.pSeq.amplitude, seq.pSeq.onDurationMillis, seq.pSeq.frequency, cont);
            MM3C.AddEffect(0, 0, seq.pSeq.offDurationMillis, seq.pSeq.frequency, cont);
        }
    }

    if (TIMER == play_mode)
    {
        timer_start(default_pattern->time);
    }
}



Actuator::Actuator(uint8_t pin)
{
    PWMPin = pin;
    startMillis = 0;
    OutputLevel = 0;
    start_pos = 1;
    end_pos = 1;
    current_pos = 0;
}

void Actuator::NewStartPos()
{
    start_pos = end_pos;
}

void Actuator::AddEffect(uint8_t start_level, uint8_t stop_level, uint16_t duration, uint16_t freq, uint8_t cont)
{
    Effect* eft = new Effect(start_level, stop_level, duration, freq, cont, end_pos);
    if (eft == NULL) {
        //Serial.println("out of memory !!!!!!!!!!!!!!");
        return;
    }

    //Serial.print("Add() pin # "); Serial.print(PWMPin);
    //Serial.print(" Duration: "); Serial.print(duration);
    //Serial.print(" Freq: "); Serial.print(freq);
    //Serial.print(" PUSH Effect # "); Serial.print(eft->EffectNum);
    //Serial.print(" Continuous = "); Serial.println(eft->Continuous);

    Effects.push(eft);
    end_pos++; // update end position

    // reset startMillis if this is the only effect in the queue
    if (Effects.count() == 1) {
        startMillis = millis();
        if (freq != 0) { // set frequency
            // 2026-04-02: Keep old hardcoded formula for traceability only.
            // NRF_TIMER2->CC[0] = 20000/freq;
            // 2026-04-02: Centralized frequency conversion keeps formula consistent with table size.
            timer2_set_sine_frequency(freq);
            // Serial.print(" settting freq to "); Serial.println(freq);
        }
    }
}


void Actuator::Update()
{
    if (Effects.isEmpty()) {
        // queue is empty, reset state and other variables and return
        OutputLevel = 0; // main loop will turn off boost converter if both actuators have 0 output
        // 2026-04-02: Ensure ISR sees zero level when queue is empty.
        g_output_level = 0u;
        digitalWrite(TRIAL_GATE_PIN, LOW); // SYNC: no trial running
        start_pos = 1;
        end_pos = 1;
        current_pos = 0;
        startMillis = millis(); // reset start time
        return;
    }

    /* remove current effect if stale */
    if (Effects.peek()->EffectNum < current_pos && current_pos <= start_pos) {
        // this effect is stale, pop and delete
        // Serial.println(); Serial.print(millis()); Serial.println(" milliseconds");
        // Serial.print("Update: pin "); Serial.print(PWMPin);
        // Serial.print(" pop and delete STALE effect num ");
        // Serial.println(Effects.peek()->EffectNum);
        delete(Effects.pop());
        //current_pos++;
        return;
    }

    /* remove stale effects when continuous == 2 */
    if (Effects.peek()->EffectNum < start_pos && Effects.peek()->Continuous == 2) {
        // Serial.println(); Serial.print(millis()); Serial.println(" milliseconds");
        // Serial.print("Update: pin "); Serial.print(PWMPin);
        // Serial.print(" pop and delete SUPERSEDED effect num ");
        // Serial.println(Effects.peek()->EffectNum);
        delete(Effects.pop());
        current_pos++;
        return;
    }

    /* update queue when an effect has expired */
    if ( (millis() - startMillis) >= (Effects.peek()->Duration)) {
        UpdateQueue();
        startMillis = millis(); // start time for next effect
    }

    /*  Start or continue playing an effect.  This only updates OutputLevel not frequency */
    if (!Effects.isEmpty()) // UpdateQueue might have emptied the queue!
    {
        UpdateLevel();
    }
}


void Actuator::UpdateLevel()
{
    unsigned long currentMillis = millis();

    uint8_t  srt = Effects.peek()->StartLevel;
    uint8_t  stp = Effects.peek()->StopLevel;
    uint16_t dur = Effects.peek()->Duration;

    // calculate output level
    if ( stp >= srt)
        OutputLevel = (stp - srt) * (currentMillis - startMillis) / dur + srt;
    else
        OutputLevel =  srt - (srt - stp) * (currentMillis - startMillis) / dur;

    // 2026-04-02: Keep old loop-driven PWM write for traceability only.
    // HwPWM0.writePin(PWMPin, sine[sine_index1] * (float)OutputLevel / 255, 0);

    // 2026-04-02: Publish only amplitude in loop; ISR owns sample-accurate PWM writes.
    g_output_level = OutputLevel;

    // SYNC 2026-06-17: per-trial ON/OFF gate -> Intan digital-in.
    // HIGH while the actuator is actually driving (ON effect, amplitude>0); the OFF
    // sub-effect has amplitude 0, so this goes LOW between buzzes within a block.
    digitalWrite(TRIAL_GATE_PIN, (OutputLevel > 0u) ? HIGH : LOW);
    if (OutputLevel == 0u)
    {
        digitalWrite(SYNC_CYCLE_PIN, LOW);  // SYNC: park phase marker low during OFF sub-period
    }
}


void Actuator::UpdateQueue()
{
    // update position tracking
    if (current_pos++ >= end_pos)
        current_pos = start_pos;

    //  Serial.println(); Serial.print(millis()); Serial.println(" milliseconds");
    //  Serial.print("UpdateQueue: PWMPin: "); Serial.print(PWMPin);
    //  Serial.print("\tCount: "); Serial.print(Effects.count());
    //  Serial.print("\tcurrent_pos: "); Serial.print(current_pos);
    //  Serial.print("\tstart_pos: "); Serial.print(start_pos);
    //  Serial.print("\tend_pos: "); Serial.println(end_pos);

    // store the expired effect, we might need to push it
    Effect* expired_effect = Effects.pop();
    //  Serial.print("UpdateQueue: pop EXPIRED effect num: ");
    //  Serial.println(expired_effect->EffectNum);

    // change frequency for next effect, if there is one.
    if (!Effects.isEmpty()) {
        next_freq = Effects.peek()->Frequency;
        if (next_freq != 0) {
            // 2026-04-02: Keep old hardcoded formula for traceability only.
            // NRF_TIMER2->CC[0] = 20000/next_freq;
            // 2026-04-02: Centralized frequency conversion keeps formula consistent with table size.
            timer2_set_sine_frequency(next_freq);
            // Serial.print("UpdateQueue: settting pin 9 freq to "); Serial.println(next_freq);
        }
    }

    if (expired_effect->EffectNum < start_pos) {
        // the expired effect is stale
        // Serial.print("UpdateQueue: delete STALE effect num ");
        // Serial.println(expired_effect->EffectNum);
        delete(expired_effect);
        return; // next call to update will evaluate next effect
    }

    if (expired_effect->Continuous == 1) {
        // add expired effect to end of queue
        // Serial.print("UpdateQueue: continuous, PUSH effect num: ");
        // Serial.println(expired_effect->EffectNum);
        Effects.push(expired_effect);
    } else { // Continuous == 0 or Continuous == 2
        // expired effect is not continuous, free memory
        // Serial.print("UpdateQueue: not continuous, DELETE effect # ");
        // Serial.println(expired_effect->EffectNum);
        delete(expired_effect);
    }
}


void Actuator::ClearQueue()
{
    while (!Effects.isEmpty()) {
        // Serial.print("ClearQueue: deleting effect # "); Serial.println(Effects.peek()->EffectNum);
        delete(Effects.pop());
    }

    // 2026-04-02: Ensure waveform output is reset when queue is explicitly cleared.
    g_output_level = 0u;
    digitalWrite(TRIAL_GATE_PIN, LOW); // SYNC: no trial running

    start_pos = 1;
    end_pos = 1;
    current_pos = 0;
}


bool Actuator::queueIsEmpty()
{
    return Effects.isEmpty();
}
