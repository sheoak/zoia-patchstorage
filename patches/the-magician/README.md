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

One effect per row: its mix first, then its knobs, then whatever it can do live, and
its on/off in the last column.

| Row | Colour | Cells |
| --- | --- | --- |
| Looper | aqua | `L.Level`, `L.Start`, `L.Length`, `L.Clock` — `L.RevL`, `L.RevR`, `L.FX` |
| Granular | sky | `G.Mix`, `G.Pos`, `G.Length`, `G.Pitch`, `G.Density`, `G.Texture` — `G.Freeze`, `G.On` |
| Delay | pink | `D.Mix`, `D.FB`, `D.Time`, `D.Depth`, `D.Rate` — `D.On` |
| Reverb | purple | `R.Mix`, `R.Decay`, `R.Low`, `R.High` — `R.On` |
| Sends | mango / aqua | `FXLive Send`, `FXLoop Send` — `FX On` |

Every mix sits under the same finger, and every on/off down the right edge.

There is no output level on this page — `Out` runs with its gain control off, so the
master level is whatever the mix adds up to. Trim at the amp or with `L.Level` and the
`Mix` knobs.

On/off indicators use one shared colour scheme (dim = off, bright = on). `FX On` is the
master wet on/off; `Loop FX` flips the loop routing + record dry/wet behaviour described
above.

## Stompswitches (tap / hold)

| Switch | Tap | Hold |
| --- | --- | --- |
| **Left** (Rec/Dub) | Record / Overdub | Play / Stop |
| **Mid** (Frz/Clr) | Granular Freeze | Clear / reset the loop |
| **Right** (Wet) | FX bus on/off | Loop FX on/off |

## Looper reverse (individual, stereo)

The two loopers (L and R) have **independent** reverse controls, `L.RevL` and `L.RevR` on
the home page. Reversing only one channel splits the stereo image (one side forward, one
side backward) for wide, disorienting textures; reverse both together for a normal full
reverse.

## Notes

- **CPU:** this patch runs *close to the ZOIA's limit*. The granular, the reverb and the
  delay are the heavy modules. If you hit CPU errors, lower the granular's grain count,
  or swap the Hall reverb for a lighter one. Adding modules on top may push it over —
  trim elsewhere first.
- **MIDI:** most parameters are mapped to MIDI CC (channel 12) for external control.
- **Stereo:** everything is stereo — use stereo I/O for the full effect (mono in will
  leave one side of the stereo field empty on the direct paths).

## License

[MIT](LICENSE)
