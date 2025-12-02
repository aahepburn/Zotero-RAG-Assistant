# Icon Assets

This directory contains icon assets for the desktop application.

## Required Icons

### macOS
- `icon.icns` - macOS icon file (1024x1024 base)

### Windows  
- `icon.ico` - Windows icon file (256x256 base)

### Linux
- `icons/` directory with PNG files:
  - `16x16.png`
  - `32x32.png`
  - `48x48.png`
  - `64x64.png`
  - `128x128.png`
  - `256x256.png`
  - `512x512.png`
  - `1024x1024.png` (optional)

## Generating Icons

If you have a master PNG file (1024x1024 recommended), you can generate all icon formats:

### Using electron-icon-maker (recommended)

```bash
npm install -g electron-icon-maker

# Generate all icons from a master PNG
electron-icon-maker --input=./icon-source.png --output=./build
```

### Manual creation

**For macOS (.icns):**
```bash
# Create iconset directory
mkdir icon.iconset

# Generate different sizes
sips -z 16 16     icon-1024.png --out icon.iconset/icon_16x16.png
sips -z 32 32     icon-1024.png --out icon.iconset/icon_16x16@2x.png
sips -z 32 32     icon-1024.png --out icon.iconset/icon_32x32.png
sips -z 64 64     icon-1024.png --out icon.iconset/icon_32x32@2x.png
sips -z 128 128   icon-1024.png --out icon.iconset/icon_128x128.png
sips -z 256 256   icon-1024.png --out icon.iconset/icon_128x128@2x.png
sips -z 256 256   icon-1024.png --out icon.iconset/icon_256x256.png
sips -z 512 512   icon-1024.png --out icon.iconset/icon_256x256@2x.png
sips -z 512 512   icon-1024.png --out icon.iconset/icon_512x512.png
sips -z 1024 1024 icon-1024.png --out icon.iconset/icon_512x512@2x.png

# Convert to .icns
iconutil -c icns icon.iconset
```

**For Windows (.ico):**
Use ImageMagick:
```bash
convert icon-1024.png -define icon:auto-resize=256,128,96,64,48,32,16 icon.ico
```

Or use an online converter like:
- https://convertio.co/png-ico/
- https://www.icoconverter.com/

## Design Guidelines

### General
- Use simple, recognizable design
- Works well at small sizes (16x16)
- Good contrast
- Avoid fine details

### macOS
- Rounded corners (iOS-style)
- Subtle shadow/depth
- Colorful but professional

### Windows
- Sharp, clear design
- Perspective/3D effects work well
- Often includes subtle shadow

### Linux
- Flat design or subtle gradients
- Clear at all sizes
- Follows Freedesktop.org guidelines

## Current Status

⚠️ **Placeholder icons needed!**

This build directory is currently empty. You need to add your app icons before building installers.

For now, Electron will use default icons, but for a professional release, custom icons are essential.

## Quick Start

Don't have a designer? Here are options:

1. **Use Zotero's logo** (with permission)
2. **Free icon resources:**
   - [Flaticon](https://www.flaticon.com/)
   - [Icons8](https://icons8.com/)
   - [The Noun Project](https://thenounproject.com/)
3. **AI generation:**
   - Use DALL-E, Midjourney, or Stable Diffusion
   - Prompt: "Modern, minimalist app icon for research assistant"
4. **Hire a designer:**
   - Fiverr
   - 99designs
   - Upwork

## Testing Icons

After adding icons, rebuild and test:

```bash
npm run build
npm run package:mac  # (or :win, :linux)
```

Check that:
- Icon appears in dock/taskbar
- Icon appears in app switcher
- Icon appears in Finder/Explorer
- Icon appears in installers
- Icon looks good at all sizes

## Attribution

If using third-party icons, add attribution here:

```
Icon created by [Artist Name] from [Source]
License: [License Type]
```
