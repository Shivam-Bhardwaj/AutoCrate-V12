#!/usr/bin/env node

/**
 * Update version for deployment
 * This script updates the version.json file with new deployment information
 */

const fs = require('fs');
const path = require('path');

// Read current version.json
const versionPath = path.join(__dirname, '..', 'version.json');
const packagePath = path.join(__dirname, '..', 'package.json');

try {
  // Read current files
  const versionData = JSON.parse(fs.readFileSync(versionPath, 'utf8'));
  const packageData = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
  
  // Get version from package.json
  const newVersion = packageData.version;
  
  // Update version.json
  versionData.version = newVersion;
  versionData.deploymentNumber = (versionData.deploymentNumber || 0) + 1;
  versionData.lastDeployment = new Date().toISOString();
  versionData.buildNumber = Date.now().toString();
  
  // Add to changelog
  if (!versionData.changelog) {
    versionData.changelog = [];
  }
  
  // Get changes from command line or use default
  const changes = process.argv.slice(2);
  if (changes.length === 0) {
    changes.push('Version update');
  }
  
  versionData.changelog.unshift({
    version: newVersion,
    deployment: versionData.deploymentNumber,
    date: versionData.lastDeployment,
    changes: changes,
    commit: process.env.VERCEL_GIT_COMMIT_SHA?.substring(0, 7) || 'local'
  });
  
  // Keep only last 10 deployments in changelog
  versionData.changelog = versionData.changelog.slice(0, 10);
  
  // Write updated version.json
  fs.writeFileSync(versionPath, JSON.stringify(versionData, null, 2));
  
  console.log(`✅ Version updated to ${newVersion}`);
  console.log(`📦 Deployment #${versionData.deploymentNumber}`);
  console.log(`📅 ${versionData.lastDeployment}`);
  console.log(`📝 Changes: ${changes.join(', ')}`);
  
} catch (error) {
  console.error('❌ Error updating version:', error);
  process.exit(1);
}