# ZOIA patches

Patches for the Empress ZOIA, one directory each.

Every one is a `.bin` you drop on the SD card, alongside whatever has been written about
it. Nothing here needs building or installing.

## Installing one

Copy the `.bin` into the `to_zoia` folder of your SD card, renamed with the slot you want:

```
000_zoia_The_World.bin
```

The pedal takes the number from the file name, so two files sharing one number is the usual
way to end up wondering where a patch went.

## What is here

| Patch | Builds |
| --- | --- |
| [The Magician](patches/the-magician) | Micro-looper, granular and a shared FX bus |
| [The Hierophant](patches/the-hierophant) | Mono, plus the original |
| [The Hierophant MKII](patches/the-hierophant-mk2) | Stereo |
| [The Lovers](patches/the-lovers) | Chorus and vibrato |
| [The World](patches/the-world) | Standard and tape |

`main` carries the patches that are played. One still being built lives on its own
branch until it is — the open draft pull requests are what is in progress.

The written documentation lives at [Zoiatheca](https://github.com/sheoak/zoiatheca), which
draws each patch as the pedal itself. What is in this repository is the patches and the
notes that came with them.

## Layout

```
patches/<name>/
  <Patch>.bin        the patch, always 32768 bytes
  README.md          what it is and how to play it, when one has been written
  SCHEMA.md          how it is built, when one has been written
```

A patch with several builds keeps them side by side in the same directory.

## Checks

```bash
python3 tools/check.py
```

Structure only — every directory has a `.bin`, every `.bin` is the right size, no loose files.
Decoding the format needs the editing skill, which is not public, so CI does not try.

## Licence

MIT. Take them, change them, play them.

## Working on a patch

Each directory carries its own `VERSION` and `CHANGELOG.md`. A git tag would
point at a commit, which here means the whole tree, so the number lives with the
file instead — and shows up in the diff of the change that earned it.

Commits are conventional: `fix(hierophant): keep the launcher lit`. The files a
commit touches decide which patches move; its type decides how far.

```
brew install lefthook && lefthook install   # once, so the hooks run
python3 tools/check.py                      # sizes, layout, versions
python3 tools/release.py --check            # what a release would write
python3 tools/release.py                    # write it
```

The number says a patch changed, never that it is good — that part is you and
the pedal.
