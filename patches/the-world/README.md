# The World

Part of the Arcana series of patches for the Empress ZOIA.

Mono or stereo in, mono or stereo out. A pedalboard in one patch: phaser, flanger, chorus,
tape delay and a three-band EQ, in series. Each one switches by foot, by the screen, or
over MIDI, and the three never drift apart.

The front page is a grid: **one row per effect**, in the order the signal meets them, and
the columns grouped by what the knob does. The on/off button is the first cell of each row;
the last two columns are the input meters, red at the top.

| | on/off | mix | tone / time | rate | width / depth | intensity |
| --- | --- | --- | --- | --- | --- | --- |
| **Phaser** | ● | | | Rate | Width | Resonance |
| **Flanger** | ● | | Tone | Rate | Width | Regen |
| **Chorus** | ● | Mix | Tone | Rate | Width | |
| **Delay** | ● | Mix | Time | Rate | Depth | Feedback |
| **EQ** | ● | | Low | Mid | Mid freq | High |

The EQ is the exception: no modulation, so its row is just its four bands.

| Switch | Short | Long |
| --- | --- | --- |
| Left | Phaser | Flanger |
| Middle | Chorus | Delay |
| Right | Bypass | EQ |

The right switch follows the enclosure rather than the chain: a short press bypasses the
pedal, which is what the word printed under it says.

Every knob and every state is on MIDI, one decade per effect, with force-on and force-off
pairs so a controller can set up a song rather than toggle from wherever it was left.

Played and documented at [zoiatheca](https://github.com/sheoak/zoiatheca).
