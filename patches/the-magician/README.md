# The Magician

A fine-tuned micro-looper with a granular engine, a delay, a reverb. Loop anything and it
comes back changed — barely, or beyond recognition — while you keep playing over the top.

Part of a Tarot-arcana series — the Magician *captures and transmutes*. Inspired by the
Chase Bliss Mood MKII.

> See [SCHEMA.md](SCHEMA.md) for the signal-path diagrams.

## Most of the work is in the looper

The ZOIA's Looper module does the recording. It does not behave the way a looper pedal
should. Three problems had to be solved before the rest of the patch was worth building.

**1. The module never says what it is doing.** Record runs straight into overdub, with no
playback state in between. Dropping the record control back to zero does not release it.
From the second press on, the control says one thing and the module does another. So the
patch keeps its own state — recording, playing, overdubbing — in its own cells, and
everything else reads that instead of the control.

The looper can also stop on its own. Fill the 16-second buffer and it stops recording
without telling anyone. A timer starts with the recording and fires a press of its own at
the limit, so the tracked state stops when the module does.

**2. Overdub could not be refused, and refusing it used to click.** Only a fresh rising
edge gets the looper out of overdub. So the patch toggles the record flip-flop a second
time, a short moment after your second press. The second press then leaves you in
playback, and the third one overdubs. The delay is what keeps it quiet: an earlier
version pulled `restart_playback` instead, and restarting playback crackles every time
you stop.

**3. Clear has to clear everything.** A long press on the middle switch resets the loop,
the press counter and the record state together. Reset the module alone and the patch
still believes there is a loop, so the next press lands in the wrong state.

One lamp reports all of it — the cell beside `Clock Menu` on the front page. Dark when
the loop is empty, red while recording, sky blue while playing, pink while overdubbing.
[The looper state machine](#the-looper-state-machine) has the detail.

## Signal architecture (aux-send, stereo)

The patch is built like a small studio mixer with **aux sends**, not a simple series
chain:

```
IN (stereo) --+--> LIVE dry (direct) -----------------------> OUT
              +--> Live aux send --\
                                    >--> [DELAY -> REVERB] --> OUT   (shared WET bus)
LOOPER (mono) --> GRANULAR --+--> Loop dry (direct) ---------> OUT
                      +--> Loop aux send --/
```

### Shared wet bus

The Delay and the Reverb form **one** wet bus (Delay → Reverb, in series). *Both* the
live signal and the loop feed it through independent aux sends:

| Send | Role |
| --- | --- |
| `Live Send FX` | How much of the **live** signal is sent to the FX |
| `Loop Send FX` | How much of the **loop** is sent to the FX |

Each source is a dry/wet crossfade (dry-direct vs aux-send), so the two sources can
have different wet amounts while sharing a single Delay + Reverb.

### The granular is not in the FX bus

The granular is placed on the **loop only**, post-looper (it grinds whatever is in the
loop, live). It is *not* part of the Delay/Reverb bus and it does *not* touch the live
signal. So the granular reshapes the loop, and the FX bus adds space/echo to live +
loop.

### The low cut is on what the granular is fed

`Loop HPF` sits between the looper and the granular — it filters the granular's **input**,
not the grains it produces, and not the loop. The leg that carries the loop straight to
the output takes the looper unfiltered, so the phrase keeps its bottom while the granular
voice above it can be thinned.

Grains cannot hold bass anyway: a 50 Hz cycle is 20 ms, longer than a short grain, so low
content comes back as thumps rather than pitch. Cutting it before the grains are taken
also keeps it out of the shared reverb.

One consequence worth knowing: because only the granular leg is filtered, `Grain Blend`
moves the bass as well as the texture. That is the point rather than a defect here — the
live path is a separate full-range leg, so the mix never loses its bottom, and one knob
takes the loop from a full-range foundation to a thinner texture.

The knob spans **27.5 Hz to 880 Hz**: `Loop HPF` drives the filter's frequency at 50%, so
the bottom of its travel is genuinely off. It defaults to 0. Resonance sits at the
module's minimum, Q = 1.

### Stereo where it counts

**The live path is stereo end to end.** What you play reaches the output on its own
two channels and never touches the looper.

**The loop is mono.** One Looper, fed by both sides of the record mix at half strength
each, so a mono source comes back at the level you played it. The stereo is rebuilt
after it: the granular runs in stereo, and so do the sends, the crossfades, the delay
and the reverb.

A single Looper is the right trade here. A guitar into one jack fills both channels
with the same audio, so a second Looper buys nothing and costs a second buffer, a
second resampler on every clock setting off unity, and a second reverse control.

## Record dry / wet

*The important bit: coupled to `Loop FX` on/off.*

What gets baked into the loop when you record depends on the `Loop FX` toggle. This is
intentional and avoids stacking effects.

### `Loop FX` OFF → record the **mix, as heard**

The loop captures exactly what leaves the pedal: the live dry and the wet, already
balanced by `Live Send FX`.

Rationale: with Loop FX off, the loop is not re-sent to the FX at playback, so you want
the effect character frozen into the recording. Playback = the wet you performed, fixed.
In this case the granular is **post-FX**.

### `Loop FX` ON → record **dry**

The loop captures the raw input, at full, whatever the sends are doing.

Rationale: with Loop FX on, the loop *is* routed to the FX bus at playback (live effects
applied to the loop). Recording dry avoids stacking (baked FX + live FX = mush /
runaway). You get live, tweakable effects on a clean loop. In this case the granular is
**pre-FX**.

### One switch, not a level

`Loop FX` picks between the two sources outright — there is no amount to set and nothing
in between. A single `Audio Balance` sits in front of the looper with the mix as its
input 1 and the raw input as its input 2, and the toggle drives its crossfade.

`Loop Send FX` therefore does one job only: how much of the **loop** is sent to the FX bus
at playback. It has no effect on what gets recorded, and none at all while `Loop FX` is
off — with the loop going straight out, there is nothing to send.

## Home page layout (page 0)

**One block per row, and every on/off in column 1.** The block's own controls follow
its toggle across the row; the last column holds whatever that block can do live.

| Row | Colour | Cells |
| --- | --- | --- |
| Clock menu | lime / white / yellow | eight loop speeds, dark until the menu is opened |
| Clock menu | mango / yellow | `Clock Menu` launcher, and the loop-state lamp beside it |
| Looper | aqua | `Loop FX` — `Loop Level`, `Loop Start`, `Loop Clock`, `Loop Length`, `Loop HPF` — `Loop Send FX` — `Loop Reverse` |
| Granular | blue | `Grain On` — `Grain Blend`, `Grain Pos`, `Grain Pitch`, `Grain Length`, `Grain Texture`, `Grain Density` — `Grain Freeze` |
| FX | magenta / purple | `FX On` — `Dly Mix`, `Dly FB`, `Dly Time`, `Rvb Mix`, `Rvb Decay` — `Live Send FX` |

Cell names spell out the block they belong to, so a cell says what it is without the
legend: `Dly`, `Rvb`, `Grain`, `Loop`.

The delay and the reverb share one row, one toggle and one send. That is what freed
the row the clock menu now sits on. The two knobs that did not fit, `Dly Depth` and
`Dly Rate`, sit on page `Settings` together.

There is no output level on this page — `Out` runs with its gain control off, so the
master level is whatever the mix adds up to. Trim at the amp or with `Loop Level` and the
`Mix` knobs.

The three toggles in column 1 are all orange, dim when the block is out and bright when
it is in. They say nothing about the loop: the record state has its own lamp on the row
above, so a toggle only ever means on or off.

The knobs run **aqua → blue → magenta/purple** down the page, in the order the signal
meets them. The delay and the reverb are one band apart on purpose: one row, one bus,
one toggle, one send. Around them, green is anything held or struck — `Loop Reverse` and
`Grain Freeze`, each at the end of its own row — and peach is a level going to the shared
bus.

## The clock menu

The ZOIA has no menu module, so page `Clock Menu` builds one out of seven. The
launcher lights the top row; picking a speed sets it and shuts the menu.

The eight speeds are just intervals on the looper's geometric `speed_pitch` range,
written into the connection strengths rather than into a knob:

| | ×1/4 | ×1/2 | ×2/3 | ×3/4 | ×1 | ×4/3 | ×3/2 | ×2 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| interval | −2 oct | −1 oct | fifth ↓ | fourth ↓ | unity | fourth ↑ | fifth ↑ | +1 oct |
| strength | 29.992 | 39.994 | 44.157 | 45.867 | 50.003 | 54.138 | 55.847 | 59.979 |

Travel on that range is `0.5 + log2(ratio) / 10`, so a tenth of the range is exactly
one octave. All eight land within 2.5 cents, which is the limit of the integer strength
grid.

The row reads slow to fast, and the colour says which half you are in: the four below
unity are lime, the three above are yellow. Unity is the white cap in the middle. It
writes the speed straight to the hold as well as through the menu, so it is the one
choice that cannot be knocked off by a rounding error.

`Loop Clock` writes the same looper parameter through a `Sample and Hold`, at 15.849%, so
the knob spans exactly ×1/3 to ×3. Two triggers watch it — one direct, one through a
`CV Invert` — so a move in either direction pulses a multiplier and pushes the knob's
value into the hold. The menu and the knob therefore overwrite each other, and whichever
moved last owns the speed.

## Stompswitches

| Switch | Tap | Hold |
| --- | --- | --- |
| **Left** — Record | Record → stop/play → overdub | — |
| **Mid** — Playback/Clear | Playback on/off | Clear / reset the loop |
| **Right** — FX/Loop FX | FX bus on/off | Loop FX on/off |

The left switch has no hold, so that it fires with no latency: it drives the record
flip-flop directly. Playback moved to the middle switch.

Granular freeze lost its footswitch in that move. It stays on the front page, and
`Freeze` sits on page `Controls` with no gesture wired to it if you want it back under
a foot.

## The looper state machine

Four pages hold it — `Record`, `Auto Stop`, `Playback`, `Clear` — and most of the cells
on them do nothing but remember.

| Cell | What it holds |
| --- | --- |
| `Once SH` | a loop has been started at least once |
| `Twice SH` | the second press has happened, so overdub is next |
| `Is Recording SH` | the tracked record state |
| `Is Playing SH` | the tracked play state |

Every press arrives at one `Value`, `Rec midi`, so the left switch, the MIDI CC and the
auto-stop all take the same road and nothing downstream has to know which one it was.

- `Left Tap TRI` narrows the press to an instant. A stompswitch is a gate, not a pulse,
  and a Sample and Hold triggered by a gate samples for the whole press.
- `Rec Toggle` is an AND with *not recording*, so a press flips the record state instead
  of chasing it. On a clear the press is absent, so the same cell reads zero and the
  state is forced low rather than toggled.
- `Auto Stop ADSR` starts with the recording, delay `0.88`. If a second press has not
  arrived by the time it ends, `Auto Stop Rec` presses record for you.
- `OD Bypass ADSR`, delay `0.44`, is the second toggle that cancels overdub.
- `Clear TRI` resets `Once SH`, `Twice SH` and `Is Recording SH` in one gesture.
- `REC Light` is an `In Switch`. The three states add into one selector, and it picks the
  colour the lamp shows: dark, red, sky blue, pink.

Playback is locked out while recording — `Play Press` is an AND with *not recording* — so
the middle switch cannot fight the left one.

## Notes

- **MIDI:** 28 CCs, assigned straight onto the parameters rather than through a MIDI
  module. Every knob on the front page, plus the toggles, the freeze, the reverse, the
  playback, and record and clear. Nothing switches over MIDI that a footswitch cannot do.
- **Stereo:** a single cable in works — the ZOIA copies the left input to the right.
  Plug in stereo and your live signal keeps its two sides all the way to the output;
  only the loop is summed to mono.

## License

[MIT](LICENSE)
