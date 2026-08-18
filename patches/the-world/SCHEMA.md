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
    P.State ──┐                    F.State ──┐                    C.State ──┐
              ├─► Phaser.mix                 ├─► Flanger.mix                ├─► Chorus.mix
    NEG1 ─────┘                    NEG1 ─────┘                    NEG1 ─────┘

    mix = base + FlipFlop + (−1)      FF=1 → base      FF=0 → negative
```

`NEG1` is one shared `Value` at −1, option `output: -1 to 1`. A single CV output feeds all
three mixes.

```
    D.State ──┬─────────────────► D.VCA In.level_control
              └─► D.NOT ────────► D.VCA Dry.level_control   (partagé avec D.ON AND)

    T.State ──┬─────────────────► T.VCA Wet.level_control
              └─► T.Byp NOT ────► T.VCA Dry.level_control
```

VCA `level_control` is in dB: `0` is −∞ and `1` is exactly 0 dB, so the endpoints are mute
and unity. `T.State` is toggled by `R.Short`.

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

Taken verbatim from the Hierophant. The Trigger self-loops present in that patch are a bug
and are deliberately **not** reproduced here.

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

Columns are effects, rows are parameters.

```
        P             F             C            D           T
row 0   P.Rate        F.Rate        C.Rate       D.Time      T.Low
row 1   P.Reso        F.Regen       C.Width      D.Fbk       T.Mid
row 2   P.Width       F.Width       C.Tone       D.Mod       T.MidFrq
row 3   —             F.Tone        C.Mix        D.Mix       T.High
row 4   P.On/Off      F.On/Off      C.On/Off     D.On/Off    T.On/Off
```

Columns 6 and 7 carry the two meters, `VU L1–L5` and `VU R1–R5`, bottom row loudest.

## Conventions

Value names are `X.Param`, where `P` phaser, `F` flanger, `C` chorus, `D` delay, `T` tone.

A block placed past cell 39 is **deliberate** — it is how an unwanted output is hidden,
instead of covering it with an unlit Pixel. Do not "fix" it.
