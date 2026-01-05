#!/usr/bin/env node
const sharp = require('sharp');
const fs = require('fs');
const path = require('path');
const png2icons = require('png2icons');

const inputSvg = path.join(__dirname, '../build/icon.svg');
const outputDir = path.join(__dirname, '../build');
const iconsDir = path.join(__dirname, '../build/icons');

// Ensure icons directory exists
if (!fs.existsSync(iconsDir)) {
  fs.mkdirSync(iconsDir, { recursive: true });
}

async function generateIcons() {
  console.log('Generating icons from SVG...');
  
  // Generate a high-res PNG first (1024x1024)
  const png1024 = path.join(outputDir, 'icon-1024.png');
  await sharp(inputSvg)
    .resize(1024, 1024)
    .png()
    .toFile(png1024);
  console.log('✓ Generated 1024x1024 PNG');
  
  // Generate various PNG sizes for Linux
  const sizes = [16, 24, 32, 48, 64, 128, 256, 512];
  for (const size of sizes) {
    const output = path.join(iconsDir, `${size}x${size}.png`);
    await sharp(inputSvg)
      .resize(size, size)
      .png()
      .toFile(output);
    console.log(`✓ Generated ${size}x${size} PNG`);
  }
  
  // Read the 1024x1024 PNG for icon generation
  const pngBuffer = fs.readFileSync(png1024);
  
  // Generate .icns for macOS
  try {
    const icnsOutput = path.join(outputDir, 'icon.icns');
    const icnsBuffer = png2icons.createICNS(pngBuffer, png2icons.BICUBIC, 0);
    fs.writeFileSync(icnsOutput, icnsBuffer);
    console.log('✓ Generated icon.icns for macOS');
  } catch (err) {
    console.error('Failed to generate .icns:', err.message);
  }
  
  // Generate .ico for Windows
  try {
    const icoOutput = path.join(outputDir, 'icon.ico');
    const icoBuffer = png2icons.createICO(pngBuffer, png2icons.BICUBIC, 0, false);
    fs.writeFileSync(icoOutput, icoBuffer);
    console.log('✓ Generated icon.ico for Windows');
  } catch (err) {
    console.error('Failed to generate .ico:', err.message);
  }
  
  console.log('\n✓ All icons generated successfully!');
  console.log(`  - macOS: ${outputDir}/icon.icns`);
  console.log(`  - Windows: ${outputDir}/icon.ico`);
  console.log(`  - Linux: ${iconsDir}/[16-512]x[16-512].png`);
}

generateIcons().catch(err => {
  console.error('Error generating icons:', err);
  process.exit(1);
});
