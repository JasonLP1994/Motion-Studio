# Rendering 3D on a cloud render farm (beginner guide)

For the 3D pieces made in this workspace with Blender. Claude builds the scene and hands you **one
self-contained `.blend` file**. A render farm renders it on fast GPUs, you pay the farm directly, and the
finished frames come back here for sound, checks and the final MP4.

Claude never creates farm accounts, uploads files or pays for you. Those steps are yours.

## Which farm
- **RebusFarm:** the cheapest per GHz-hour of the ones checked (about 1.39 cents). Desktop uploader app.
- **GarageFarm:** simple, with a Blender add-on and Low/Medium/High priority. A third-party site reports
  starter credit for new accounts; check their site.
- Avoid **SheepIt** for your own work: it's free, but your file is rendered on strangers' computers.

Prices change. The farm always shows a quote before you pay, and that quote is the real number.

## Step by step
1. **Get the file.** Claude saves it in `renders/farm/<name>.blend` (local only, never on GitHub) and sends
   it to you in chat. Everything is packed inside: models, textures and masks. Nothing else is needed.
2. **Make an account** on the farm's website and add a small amount of credit. For a first test, a single
   frame costs pennies.
3. **Upload the `.blend`** with the farm's website, desktop uploader or Blender add-on.
4. **Check the job settings** on the farm. The file already sets all of these:

   | Setting | Value |
   |---|---|
   | Software | Blender (the version Claude names in chat, e.g. 4.0) |
   | Renderer | Cycles |
   | Device | GPU if offered (cheaper and faster), otherwise CPU |
   | Frames | as set in the file (Claude tells you the range, e.g. 1-600) |
   | Output | PNG frames: `render/<name>_0001.png`, `_0002.png` ... |
   | Resolution | 1920×1080 |

   Leave the samples and denoiser as they are: 128 samples plus OpenImageDenoise.
5. **Start with a test:** render 1-3 frames first and check they look right.
6. **Render the full range**, then download the frames as a ZIP.
7. **Bring them back:** put the ZIP or the frames in `inputs/farm/<name>/` and tell Claude. Claude:
   - joins the frames into an MP4;
   - adds the sound mix at about -14 LUFS;
   - checks frames from the whole video and scores it;
   - saves it as the next version in `renders/`.

## Animations that come as a folder (ZIP)
Some animations use per-frame maps that Blender can't pack inside the `.blend` (for example
PaintedStatue's `floor/m_####.png` liquid maps). Then Claude sends a **ZIP of a folder**: the `.blend`,
`floor/`, `rome_mask.png` and a README. Upload the **whole ZIP or folder** to the farm (most accept a
ZIP or project folder), not just the `.blend`, or the pool and ROME liquid will be missing.
- The file is saved with preview settings: 64 samples, denoiser, no motion blur. For the final, set
  Render > Samples to 128 and tick Motion Blur (shutter 0.5) before uploading, or ask the farm to override.
- Frames: 1-600 at 30 fps, 1920x1080, PNG to `render/painted_statue_####.png`.

## Why frames and not an MP4 from the farm
If one frame fails or a node crashes, only that frame is re-rendered. The sound is added here, mixed and
checked, so the farm's output stays silent.

## Cost check before you start
Claude estimates the cost from local test renders (see the chat for each job). For the PaintedStatue piece
the estimate was about 310 GHz-hours for 600 frames: roughly $5 on RebusFarm and $7-22 on GarageFarm,
depending on priority, so budget $10-30 including a re-render.
