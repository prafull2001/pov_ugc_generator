# POV UGC Variation System

## Overview

This system generates **5 unique videos** per meme for distribution across:
- 2 TikTok accounts
- 2 Instagram accounts
- 1 backup account

Each video is genuinely unique (different audio waveforms, visual treatment, timing) to avoid platform duplicate detection.

---

## Caption Variations

All captions stay true to the core POV concept. "POV" is always capitalized.

### Set A: "Stayed up late"
```
1. POV you stayed up too late on a school night
2. POV you stayed up way too late on a school night
3. POV you stayed up late on a school night again
4. POV you stayed up too late on a school night...
5. POV you stayed up late on a school night
```

### Set B: "Sleeping late"
```
1. POV you slept late on a school night
2. POV you slept way too late on a school night
3. POV you slept late on a school night again
4. POV you slept too late on a school night
5. POV you slept late on a school night...
```

### Set C: "Couldn't sleep" (alternate angle)
```
1. POV you couldn't sleep on a school night
2. POV you couldn't fall asleep on a school night
3. POV you couldn't sleep on a school night again
4. POV you couldn't stop scrolling on a school night
5. POV you couldn't put your phone down on a school night
```

**Assignment per account:**
| Account | Platform | Caption Set | Variation # |
|---------|----------|-------------|-------------|
| Account 1 | TikTok | Set A | 1 |
| Account 2 | TikTok | Set B | 1 |
| Account 3 | Instagram | Set A | 2 |
| Account 4 | Instagram | Set B | 2 |
| Account 5 | Backup | Set C | 1 |

---

## Current Video Structure Analysis

Based on your existing clips:

### Intro (~4 seconds)
- Wake up sequence
- Snooze alarm
- Flip phone / camera goes down
- **Audio**: Alarm sound, rustling, breathing

### Meme Section (~2-4 seconds per clip)
- Scrolling through meme content
- **Audio**: Phone scrolling sounds, occasional reactions

### Outro (~9 seconds total, 6 clips)
```
0_start.mov    (0.9s) - Screen time notification appears
1_middle.mov   (0.9s) - Looking at screen
2_middle.mov   (0.5s) - Transition
3_middle.mov   (3.0s) - Reacting to screen time
4_middle.MOV   (0.8s) - Putting phone down
5_end.MOV      (2.7s) - Getting up / final moment
```
- **Audio**: Screen time sound, sighing, getting up sounds

### Endcard (~2-3 seconds)
- Spool branding
- **Audio**: Music/jingle

---

## Audio Recording Guide

### What You Need
- Quiet room (same room you film in)
- Phone or mic for recording
- Voice Memos app or similar

### Recording Session 1: INTRO AUDIO VARIANTS (15 min)

Record **4 versions** of your intro sequence audio. Each should be ~4-5 seconds.

**Take 1 - Standard**
```
[silence 0.5s]
[alarm sound - use your actual alarm]
[rustling/movement sounds]
[sleepy exhale or groan]
[phone pickup sound]
[silence 0.3s]
```

**Take 2 - More tired**
```
[silence 0.5s]
[alarm sound]
[longer pause before moving]
[heavier sigh/groan]
[slower rustling]
[phone pickup]
```

**Take 3 - Quicker reaction**
```
[alarm sound - shorter]
[immediate rustling]
[quick exhale]
[faster phone grab]
```

**Take 4 - Different alarm tone**
```
[different alarm sound if possible]
[movement sounds]
[soft groan]
[phone sounds]
```

**File naming:**
- `intro_audio_v1.wav`
- `intro_audio_v2.wav`
- `intro_audio_v3.wav`
- `intro_audio_v4.wav`

---

### Recording Session 2: REACTION SOUNDS (10 min)

Record **6 generic reaction sounds** (~1-3 seconds each). These go over meme clips.

**Reactions to record:**

1. **Amused exhale** - soft "heh" through nose
   - `reaction_amused.wav`

2. **Surprised intake** - quick breath in, like "oh"
   - `reaction_surprised.wav`

3. **Soft laugh** - quiet chuckle, 2-3 "ha"s
   - `reaction_laugh.wav`

4. **Intrigued hum** - "hmm" or "huh"
   - `reaction_hmm.wav`

5. **Scrolling sounds** - finger on screen, no voice
   - `reaction_scroll.wav`

6. **Light gasp** - subtle intake, mild shock
   - `reaction_gasp.wav`

**Tips:**
- Keep these SHORT (1-2 seconds max)
- Natural, not over-acted
- Record 2-3 takes of each, pick the best

---

### Recording Session 3: OUTRO AUDIO VARIANTS (20 min)

Record **4 versions** matching your 9-second outro sequence.

**Structure to follow:**
```
0.0s - 0.9s:  Screen time notification sound (can use actual sound)
0.9s - 1.8s:  Pause/looking at phone
1.8s - 2.3s:  Small reaction (sigh, "ugh", frustrated exhale)
2.3s - 5.3s:  Longer reaction (groan, putting phone down sounds)
5.3s - 6.1s:  Movement sounds (sheets, shifting)
6.1s - 8.8s:  Getting up sounds (feet on floor, standing)
```

**Take 1 - Annoyed**
```
[screen time ding]
[pause]
[frustrated sigh - "ugh"]
[phone toss onto bed/table]
[sheets rustling]
[feet hitting floor, standing up]
```

**Take 2 - Resigned**
```
[screen time ding]
[longer pause]
[defeated exhale]
[gentle phone put-down]
[slow movement]
[reluctant getting up]
```

**Take 3 - Sleepy acceptance**
```
[screen time ding]
[yawn or sleepy sound]
[mumbled "fine" or exhale]
[phone down]
[stretching sounds]
[slow rise]
```

**Take 4 - Quick compliance**
```
[screen time ding]
[brief pause]
[quick exhale]
[phone down fast]
[immediate movement]
[getting up quickly]
```

**File naming:**
- `outro_audio_v1.wav`
- `outro_audio_v2.wav`
- `outro_audio_v3.wav`
- `outro_audio_v4.wav`

---

## New Folder Structure

```
pov_ugc_generator/
├── input/
│   ├── intro/
│   │   ├── video/
│   │   │   └── intro_base.mov          # Your existing intro video
│   │   └── audio/
│   │       ├── intro_audio_v1.wav
│   │       ├── intro_audio_v2.wav
│   │       ├── intro_audio_v3.wav
│   │       └── intro_audio_v4.wav
│   │
│   ├── reactions/
│   │   ├── reaction_amused.wav
│   │   ├── reaction_surprised.wav
│   │   ├── reaction_laugh.wav
│   │   ├── reaction_hmm.wav
│   │   ├── reaction_scroll.wav
│   │   └── reaction_gasp.wav
│   │
│   ├── outro/
│   │   ├── video/
│   │   │   ├── 0_start.mov
│   │   │   ├── 1_middle.mov
│   │   │   ├── 2_middle.mov
│   │   │   ├── 3_middle.mov
│   │   │   ├── 4_middle.MOV
│   │   │   └── 5_end.MOV
│   │   └── audio/
│   │       ├── outro_audio_v1.wav
│   │       ├── outro_audio_v2.wav
│   │       ├── outro_audio_v3.wav
│   │       └── outro_audio_v4.wav
│   │
│   ├── memes/
│   │   └── [your meme clips]
│   │
│   └── endcard/
│       └── endcard.mov
│
├── batch_output/
│   ├── acc1/
│   ├── acc2/
│   ├── acc3/
│   ├── acc4/
│   └── acc5/
│
├── generate_videos.py          # Original single-output script
├── generate_variations.py      # NEW: Multi-variation script
└── config.json                 # NEW: Variation settings
```

---

## Variation Matrix

For each meme, the script generates 5 unique combinations:

| Output | Intro Audio | Reaction | Outro Audio | Visual Preset | Caption |
|--------|-------------|----------|-------------|---------------|---------|
| TikTok 1 | v1 | amused | v1 | Preset A | Set A-1 |
| TikTok 2 | v2 | laugh | v2 | Preset B | Set B-1 |
| Instagram 1 | v3 | surprised | v3 | Preset C | Set A-2 |
| Instagram 2 | v4 | hmm | v4 | Preset D | Set B-2 |
| Backup | v1 | gasp | v2 | Preset E | Set C-1 |

### Visual Presets

Each preset applies subtle but detectable differences:

| Preset | Brightness | Saturation | Speed | Crop Offset | Audio Pitch |
|--------|------------|------------|-------|-------------|-------------|
| A | +0% | +0% | 1.00x | 0px | +0 cents |
| B | +3% | +5% | 1.01x | 8px left | +15 cents |
| C | -2% | +3% | 0.99x | 8px right | -10 cents |
| D | +2% | -3% | 1.02x | 8px top | +20 cents |
| E | -3% | +8% | 0.98x | 8px bottom | -15 cents |

---

## Recording Checklist

Before your recording session:

- [ ] Quiet room, no background noise
- [ ] Phone charged
- [ ] Voice Memos app ready
- [ ] This guide open for reference

### Session 1: Intro Audio (~15 min)
- [ ] Take 1 recorded
- [ ] Take 2 recorded
- [ ] Take 3 recorded
- [ ] Take 4 recorded
- [ ] Files transferred and renamed

### Session 2: Reactions (~10 min)
- [ ] Amused exhale recorded
- [ ] Surprised intake recorded
- [ ] Soft laugh recorded
- [ ] Intrigued hum recorded
- [ ] Scrolling sounds recorded
- [ ] Light gasp recorded
- [ ] Files transferred and renamed

### Session 3: Outro Audio (~20 min)
- [ ] Take 1 (annoyed) recorded
- [ ] Take 2 (resigned) recorded
- [ ] Take 3 (sleepy) recorded
- [ ] Take 4 (quick) recorded
- [ ] Files transferred and renamed

**Total recording time: ~45 minutes**

---

## Next Steps

1. Record all audio variants following this guide
2. Organize files into the new folder structure
3. Run the variation generator script (to be built)
4. Review outputs before uploading to accounts
5. Track which variation went to which account (avoid repeats)
