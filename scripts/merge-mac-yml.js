#!/usr/bin/env node
/**
 * Merge multiple latest-mac.yml files from different architectures
 * This ensures electron-updater can find updates for both x64 and arm64
 */

const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

function mergeYmlFiles(x64Path, arm64Path, outputPath) {
  console.log('Merging macOS update manifests...');
  
  // Read both yml files
  const x64Content = fs.readFileSync(x64Path, 'utf8');
  const arm64Content = fs.readFileSync(arm64Path, 'utf8');
  
  // Parse YAML
  const x64Data = yaml.load(x64Content);
  const arm64Data = yaml.load(arm64Content);
  
  console.log('x64 data:', JSON.stringify(x64Data, null, 2));
  console.log('arm64 data:', JSON.stringify(arm64Data, null, 2));
  
  // Merge files arrays (electron-updater needs both architectures listed)
  const mergedData = {
    version: x64Data.version, // Should be the same for both
    releaseDate: x64Data.releaseDate,
    files: []
  };
  
  // Add x64 files
  if (x64Data.files) {
    mergedData.files.push(...x64Data.files);
  } else if (x64Data.path) {
    // Single file format
    mergedData.files.push({
      url: x64Data.path,
      sha512: x64Data.sha512,
      size: x64Data.size
    });
  }
  
  // Add arm64 files
  if (arm64Data.files) {
    mergedData.files.push(...arm64Data.files);
  } else if (arm64Data.path) {
    // Single file format
    mergedData.files.push({
      url: arm64Data.path,
      sha512: arm64Data.sha512,
      size: arm64Data.size
    });
  }
  
  // Add any additional fields from the newer format
  if (x64Data.path) {
    mergedData.path = x64Data.path;
    mergedData.sha512 = x64Data.sha512;
    mergedData.size = x64Data.size;
  }
  
  // Add release notes if present
  if (x64Data.releaseNotes) {
    mergedData.releaseNotes = x64Data.releaseNotes;
  } else if (arm64Data.releaseNotes) {
    mergedData.releaseNotes = arm64Data.releaseNotes;
  }
  
  // Write merged file
  const mergedYaml = yaml.dump(mergedData);
  fs.writeFileSync(outputPath, mergedYaml, 'utf8');
  
  console.log('✓ Merged manifest created:');
  console.log(mergedYaml);
  console.log(`Written to: ${outputPath}`);
}

// Main execution
if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.length !== 3) {
    console.error('Usage: merge-mac-yml.js <x64-yml> <arm64-yml> <output-yml>');
    process.exit(1);
  }
  
  const [x64Path, arm64Path, outputPath] = args;
  
  if (!fs.existsSync(x64Path)) {
    console.error(`Error: x64 yml file not found: ${x64Path}`);
    process.exit(1);
  }
  
  if (!fs.existsSync(arm64Path)) {
    console.error(`Error: arm64 yml file not found: ${arm64Path}`);
    process.exit(1);
  }
  
  try {
    mergeYmlFiles(x64Path, arm64Path, outputPath);
  } catch (error) {
    console.error('Error merging yml files:', error);
    process.exit(1);
  }
}

module.exports = { mergeYmlFiles };
