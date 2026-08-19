# The Magician

**A Mood-inspired micro-looper + granular + FX for the Empress ZOIA**

Inspired by the Chase Bliss Mood, but heavily reworked and expanded — it takes the
"capture and mangle a slice of sound" spirit and builds a different, more open
instrument around it (shared FX bus, granular on the loop, coupled record dry/wet,
true-stereo loopers).

Part of a Tarot-arcana series. The Magician *captures and transmutes*: you loop what
you play, then reshape it with granular processing and a delay/reverb effects bus.
Stereo in / stereo out.

> See [SCHEMA.md](SCHEMA.md) for the signal-path diagrams.

## Signal architecture (aux-send, stereo)

The patch is built like a small studio mixer with **aux sends**, not a simple series
chain:

```
IN (stereo) --+--> LIVE dry (direct) -----------------------> OUT
              +--> Live aux send --\
                                    >--> [DELAY -> REVERB] --> OUT   (shared WET bus)
LOOPER --> GRANULAR --+--> Loop dry (direct) --------------> OUT
                      +--> Loop aux send --/
```

### Shared wet bus

The Delay and the Reverb form **one** wet bus (Delay → Reverb, in series). *Both* the
live signal and the loop feed it through independent aux sends:

| Send | Role |
| --- | --- |
| `FXLive Send` | How much of the **live** signal is sent to the FX |
| `FXLoop Send` | How much of the **loop** is sent to the FX |

Each source is a dry/wet crossfade (dry-direct vs aux-send), so the two sources can
have different wet amounts while sharing a single Delay + Reverb (saves CPU vs
duplicating the effects).

### The granular is not in the FX bus

The granular is placed on the **loop only**, post-looper (it grinds whatever is in the
loop, live). It is *not* part of the Delay/Reverb bus and it does *not* touch the live
signal. So the granular reshapes the loop, and the FX bus adds space/echo to live +
loop.

### Stereo throughout

Two loopers (L and R) run in parallel for a true stereo loop; the sends, crossfades,
delay and reverb are all stereo.

## Record dry / wet

*The important bit: coupled to `Loop FX` on/off.*

What gets baked into the loop when you record depends on the `Loop FX` toggle. This is
intentional and avoids stacking effects.

### `Loop FX` OFF → record the **mix, as heard**

The loop captures exactly what leaves the pedal: the live dry and the wet, already
balanced by `FXLive Send`.

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
in between. A single `Audio Balance` sits in front of the loopers with the mix as its
input 1 and the raw input as its input 2, and the toggle drives its crossfade.

`FXLoop Send` therefore does one job only: how much of the **loop** is sent to the FX bus
at playback. It has no effect on what gets recorded, and none at all while `Loop FX` is
off — with the loop going straight out, there is nothing to send.

## Home page layout (page 0)

**One block per row, and every on/off in column 1.** The block's own controls follow
its toggle across the row; the last column holds whatever that block can do live.

| Row | Colour | Cells |
| --- | --- | --- |
| Clock menu | lime / yellow | eight loop speeds, dark until the menu is opened |
| Clock menu | mango / white | `Clock Menu` launcher, `Clock: reset` |
| Looper | aqua | `L.FX` — `L.Level`, `L.Start`, `L.Clock`, `L.Length` — `L.RevL`, `L.RevR`, `FXLoop Send` |
| Granular | blue | `G.On` — `G.Mix`, `G.Pos`, `G.Pitch`, `G.Length`, `G.Texture`, `G.Density` — `G.Freeze` |
| FX | magenta / purple | `FX On` — `D.Mix`, `D.FB`, `D.Time`, `D.Depth`, `R.Mix`, `R.Decay` — `FXLive Send` |

The delay and the reverb share one row, one toggle and one send. That is what freed
the row the clock menu now sits on.

There is no output level on this page — `Out` runs with its gain control off, so the
master level is whatever the mix adds up to. Trim at the amp or with `L.Level` and the
`Mix` knobs.

The three toggles in column 1 are all orange, dim when the block is out and bright when
it is in. `L.FX` carries a second job: a `CV Invert` on the record state subtracts 5%
from its colour while the looper is running, which drops it one band into red. It is the
record indicator as well as the loop-FX toggle.

The knobs run **aqua → blue → magenta/purple** down the page, in the order the signal
meets them. The delay and the reverb are one band apart on purpose: one row, one bus,
one toggle, one send. Around them, green is anything held or struck — `L.RevL`, `L.RevR`,
`G.Freeze` — and peach is a level going to the shared bus.

## The clock menu

The ZOIA has no menu module, so page `Clock Menu` builds one out of seven. The
launcher lights the top row; picking a speed sets it and shuts the menu.

The eight speeds are just intervals on the looper's geometric `speed_pitch` range,
written into the connection strengths rather than into a knob:

| | ×1/4 | ×1/2 | ×2/3 | ×3/4 | ×1 | ×4/3 | ×3/2 | ×2 | ×3 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| interval | −2 oct | −1 oct | fifth ↓ | fourth ↓ | unity | fourth ↑ | fifth ↑ | +1 oct | +1 oct fifth |
| strength | 29.992 | 39.994 | 44.157 | 45.867 | 50.003 | 54.138 | 55.847 | 59.979 | 65.842 |

Travel on that range is `0.5 + log2(ratio) / 10`, so a tenth of the range is exactly
one octave. All nine land within 2.5 cents, which is the limit of the integer strength
grid.

Unity is not in the menu row: it is the white cap beside the launcher, and it bypasses
the menu so it works without opening anything.

`L.Clock` writes the same looper parameter through a `Sample and Hold`, at 15.849%, so
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
`Freeze state` sits on the `Controls` row with no gesture wired to it if you want it
back under a foot.

## Looper reverse (individual, stereo)

The two loopers (L and R) have **independent** reverse controls, `L.RevL` and `L.RevR` on
the home page. Reversing only one channel splits the stereo image (one side forward, one
side backward) for wide, disorienting textures; reverse both together for a normal full
reverse.

## Notes

- **CPU:** this patch runs *close to the ZOIA's limit*. The reverb is a `Reverb Lite`
  and the granular runs three grains for that reason. What costs at runtime is not the
  module count: **overdub** is the expensive one, and overdubbing while the clock runs
  fast costs more again. Grain density is next. Moving the clock on its own is free.
  Adding modules on top may push it over — trim elsewhere first.
- **MIDI:** 25 CCs, assigned straight onto the parameters rather than through a MIDI
  module. Every knob on the front page, plus the four toggles, the freeze, the two
  reverses and playback. Nothing switches over MIDI that a footswitch cannot do.
- **Stereo:** everything is stereo, and a single cable in works — the ZOIA copies the
  left input to the right, so both sides are fed. Plug in stereo and the two sides stay
  independent, which is what the split reverse and the two loopers are for.

## License

[MIT](LICENSE)
