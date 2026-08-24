# Magician Above

**The Magician without overdub — *as above, so below***

Two variants of the same card. **Above** is the one with no overdub: the loop is
recorded once and played, and everything the pedal can spare goes into the
granular engine. **Below** is the other one, which layers.

## What was taken out

The whole overdub machinery, four modules:

| Module | What it did |
| --- | --- |
| `Once SH` | 1 from the first press of the record stomp, and never falls |
| `Seen AND` | the stomp AND `Once`, so 1 only from the second press |
| `Twice SH` | latched that, once per recording |
| `Sync ADSR` | waited 154 ms and spiked once into `Rec FF FIX` |

They existed for one reason: a `Looper` with overdub latches it internally, and
the CV feeding its `record` block falls out of step. With overdub off there is no
step to fall out of.

`Rec FF FIX` stays — it is what turns `record` on and off from the stomp.

## What had to be rewired

`Play AND` was gated by `Twice SH`, meaning "the loop has been closed", so that
asking for playback mid-record could not disturb the count. With the latch gone
that input would have sat unfed and playback would never have passed at all.

It now reads the inverted `Is Recording`, which the patch already carries, so the
rule is the simpler one: **no playback while recording**.

## No clear

Turning `overdub` off takes the Looper's `reset` block away with it — ten cells
and eight parameters become nine and seven — so the clear had nothing left to
clear. The whole path is gone: `Clear TRI`, `M. Long TRI`, the `tapHold` ADSR
that timed the hold and the `Out Switch` that routed it.

The middle switch does one thing now: **playback**. The stomp reaches its Trigger
directly, with no tap/hold split, and it is called `Play sw`.

Recording again is what replaces the loop.

## The play state

`stop_play` is a **button**: the Looper acts on a change and ignores the value.
So a latched flip flop was the wrong thing to hang on it — its value said nothing
about whether the loop was running, and the lamp read that value. A recording
puts the Looper back into play without touching `stop_play` at all, and the lamp
was wrong from then on.

Two jobs, two paths:

- The Looper takes a **pulse per press**, straight from `M. Tap TRI`.
- The lamp reads `Play state SH`, a written state. A playback press stores its own
  inverse; **a record press stores play outright**. The input is
  `Play sw × NOT(state)` summed with `Rec/Dub`, so during a playback press the
  first term is the inverse and the second is zero, and during a record press the
  other way round.

That last part is what fixes the red. It used to sit at 4 % of the red ramp while
recording, because nothing set the play state; now it is at 98 %.

| | Value | Cap |
| --- | --- | --- |
| Stopped | 0.05157 | orange, 4 % — dark |
| Playing | 0.08673 | orange, 98 % |
| Recording | 0.03673 | red, 98 % |

`Play AND` moved ahead of the Trigger, so while recording no pulse leaves at all.

## Left to set on the pedal

The options are still the Magician's. To finish the variant:

- `Looper` — `overdub: no`, on both `LoopL` and `LoopR`
- `Granular` — `num_grains: 4`
- `Delay w/Mod` — `type: old_tape`
- `G.Density` → `Granular.density` — back to 100 %, currently capped at 79.983 %

106 modules, 184 connections, cpu 50.15.
