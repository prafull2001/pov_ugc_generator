# POV UGC Video Generator

This tool automatically creates multiple POV-style videos by combining your intro, meme clips, and outro.

**Result:** Put in 10 meme clips, get 10 complete videos ready for captions in CapCut!

---

## Quick Start (Mac)

### Step 1: Run Setup (One Time Only)

Open **Terminal** (press `Cmd + Space`, type "Terminal", press Enter).

Copy and paste this command:

```
cd ~/Desktop/pov_ugc_generator && bash setup.sh
```

Press Enter and wait for it to finish. You may be asked for your password.

---

### Step 2: Organize Your Videos

After setup, you'll have these folders:

```
pov_ugc_generator/
├── input/
│   ├── intro/     <- Put your WAKE-UP clip here (1 video)
│   ├── memes/     <- Put ALL your MEME clips here (as many as you want)
│   └── outro/     <- Put your SCREEN-TIME-BLOCK clip here (1 video)
└── output/        <- Your finished videos will appear here!
```

**What goes where:**

| Folder | What to Put | How Many |
|--------|-------------|----------|
| `input/intro/` | The clip where you wake up, snooze alarm, flip phone, camera goes down | Just 1 |
| `input/memes/` | All your meme-scrolling clips | As many as you want! |
| `input/outro/` | The clip where screen time blocks the app and you get up | Just 1 |

**Tip:** Rename your meme clips to something descriptive (e.g., `funny_cat.mp4`, `sports_meme.mp4`) - the name will appear in the output file name!

---

### Step 3: Generate Videos

Open **Terminal** and run:

```
cd ~/Desktop/pov_ugc_generator && python3 generate_videos.py
```

Wait for it to finish. Your videos will be in the `output` folder!

---

### Step 4: Add Captions in CapCut

Import the generated videos from the `output` folder into CapCut and add your captions.

---

## Making New Videos Later

1. Clear out the `input/memes/` folder (or add new memes)
2. Clear out the `output/` folder
3. Run: `cd ~/Desktop/pov_ugc_generator && python3 generate_videos.py`

You can keep the same intro and outro - just swap the memes!

---

## Troubleshooting

### "command not found: python3"
Run the setup script again: `cd ~/Desktop/pov_ugc_generator && bash setup.sh`

### "No intro video found" or "No outro video found"
Make sure you put exactly 1 video file in `input/intro/` and 1 in `input/outro/`

### "No meme videos found"
Add at least one video to `input/memes/`

### Videos look weird or have wrong dimensions
All your clips should be recorded in the same orientation (vertical). The tool will try to normalize them, but it works best when all clips match.

### The process is taking forever
Video processing takes time! For 10 meme clips, expect 5-15 minutes depending on video length and your computer speed.

---

## Supported Video Formats

- `.mp4` (recommended)
- `.mov`
- `.avi`
- `.mkv`
- `.m4v`

---

## Windows Setup (Manual)

1. Download and install Python from https://www.python.org/downloads/
   - **Important:** Check "Add Python to PATH" during installation

2. Download FFmpeg from https://ffmpeg.org/download.html
   - Extract the zip file
   - Add the `bin` folder to your system PATH

3. Create the folder structure manually:
   - `input/intro/`
   - `input/memes/`
   - `input/outro/`
   - `output/`

4. Run in Command Prompt:
   ```
   cd Desktop\pov_ugc_generator
   python generate_videos.py
   ```

---

## Future Plans

- **Slideshow Automation Creator** - A tool to automatically generate slideshows from images with transitions, music, and text overlays. This would complement the POV video generator by providing another content creation workflow for social media.
