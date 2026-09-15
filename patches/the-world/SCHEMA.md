# The World — diagrams

## Audio path

```
Audio In ─► Phaser ─► Flanger ─► Chorus ─┬─► D.VCA In ─► Delay ──┐
                                         │                        ├─┬─► Tone ─► T.VCA Wet ─┐
                                         └─► D.VCA Dry ──────────┘ │                       ├─► Audio Out
                                                                   └────► T.VCA Dry ───────┘
```

Phaser, flanger and chorus are permanently inline — they are silenced by pushing their
`mix` negative, not by routing around them. Only the delay and the tone control have a real
bypass, because the first accumulates a tail and the second has no mix parameter.

```
    Phsr State FF ─┐          Flngr State FF ─┐           Chr State FF ─┐
                   ├─► Phaser.mix             ├─► Flanger.mix           ├─► Chorus.mix
    NEG1 ──────────┘          NEG1 ───────────┘           NEG1 ─────────┘

    mix = base + FlipFlop + (−1)      FF=1 → base      FF=0 → negative
```

`NEG1` is one shared `Value` at −1, option `output: -1 to 1`. A single CV output feeds all
three mixes.

```
    Dly State FF ──┬──────────────► D.VCA In.level_control
                   └─► D.NOT ────► D.VCA Dry.level_control   (shared with D.ON AND)

    EQ State FF ───┬──────────────► T.VCA Wet.level_control
                   └─► T.Byp NOT ► T.VCA Dry.level_control
```

VCA `level_control` is in dB: `0` is −∞ and `1` is exactly 0 dB, so the endpoints are mute
and unity. `D.NOT` does double duty: it drives the dry VCA and it is the *not the current
state* input of `D.ON AND`, so the force pair costs no extra gate.

`EQ State FF` is toggled by `Right Hold TRI`, the **long** press. The short press bypasses
the pedal.

## One effect, three ways to switch it

Everything converges on a single CV Flip Flop, so foot, screen and MIDI can never drift
apart.

```
  Stompswitch ──► ADSR ──► Out Switch ──┬──► Short Trigger ──┐
                    │                   └──► Long Trigger ───┤
                    │  ADSR.cv_output                        │
                    └───────────────────────────────────────►│
                                                             │
  UI Button.cv_output ───────────────────────────────────────┤
                                                             ▼
  CC force ON  ──► [AND] ◄── [NOT] ◄──┐               ┌─► CV FLIP FLOP ──┬─► Audio Out Switch L .in_select
                     └────────────────┼───────────────┘        │         ├─► Audio Out Switch R .in_select
  CC force OFF ──► [AND] ◄────────────┘                        │         └─► UI Button .in   (colour feedback)
                     └───────────────────────────────────────► │
                                                               └─► (state)
```

### Why two AND gates

A CV Flip Flop has only `cv_input` and `cv_output` — no set, no reset. You cannot force it.
So instead you toggle it *conditionally*, which reaches the same result:

| state | pulse | AND output | result |
|---|---|---|---|
| 0 | force ON | 1 | toggles → **1** |
| 1 | force ON | 0 | nothing → stays **1** |
| 1 | force OFF | 1 | toggles → **0** |
| 0 | force OFF | 0 | nothing → stays **0** |

`Logic Gate` `cv_out` is logical block **39** regardless of `num_of_inputs`.

## Tap vs hold

```
Stompswitch ─┬─► ADSR.gate_input
             └─► Out Switch.out_select
                     ▲
   ADSR.cv_output ───┘ (cv_input)

   Out Switch.cv_output_1 ──► Short   (tap — fires on release)
   Out Switch.cv_output_2 ──► Long    (hold past the threshold)
```

ADSR options: `initial_delay: on`, `immediate_release: on`, `time_scale: exponent`.
`parameters_raw = [0, 32940, 0, 0]` — the second value is the delay, ≈ 0.5 s, and it *is*
the tap/hold threshold. Raise it and taps get more forgiving; lower it and holds trigger
sooner.

Taken from the Hierophant, which is where the shape of this comes from.

## Metering

```
Audio In.output_L ──► Env Follower (log) ──┬─► Comparator 1 (0.35) ──► Pixel
                                           ├─► Comparator 2 (0.55) ──► Pixel
                                           ├─► Comparator 3 (0.70) ──► Pixel
                                           ├─► Comparator 4 (0.80) ──► Pixel
                                           └─► Comparator 5 (0.88) ──► Pixel
```

Same again for the right channel. The threshold is the Comparator's own
`parameters_raw[1]` (its `cv_negative_input` used as a param) — there is no Value module
per segment. Segment colour is the Pixel module's colour; no logic is involved in making
the top segments red.

## Home page layout

Rows are effects, columns are themes.

Transposed 2026-09-01: effects were columns, they are rows now, and the columns carry a
theme so the same kind of knob lines up down the page.

```
        on/off        mix        tone/time    rate        width/depth  intensity
row 0   Phsr On/Off   —          —            Phsr Rate   Phsr Width   Phsr Reso
row 1   Flngr On/Off  —          Flngr Tone   Flngr Rate  Flngr Width  Flngr Regen
row 2   Chr On/Off    Chr Mix    Chr Tone     Chr Rate    Chr Width    —
row 3   Dly On/Off    Dly Mix    Dly Time     Dly Rate    Dly Depth    Dly Fbk
row 4   EQ On/Off     —          EQ Low       EQ Mid      EQ MidFrq    EQ High
```

The EQ row does not follow the themes — it has no modulation, so its four bands simply
fill columns 3 to 6.

Columns 7 and 8 carry the two meters, `VU L1–L5` and `VU R1–R5`. **`L5` is the top row and
the loudest**: green at the bottom, then lima, mango, orange, red.

`Dly Mod` became `Dly Depth` in the same pass, and `Dly Rate` was added beside it — the
delay's `mod_rate`, which nothing had reached before.

## Conventions

Front-page names are `<block> <param>`, the block spelt short: `Phsr`, `Flngr`, `Chr`,
`Dly`, `EQ`. Internal pages keep the one-letter form — `P.ON AND`, `D.NOT`, `T.VCA Wet` —
where the page already says which block is meant.

A block placed past cell 39 is **deliberate** — it is how an unwanted output is hidden,
instead of covering it with an unlit Pixel. Do not "fix" it.
