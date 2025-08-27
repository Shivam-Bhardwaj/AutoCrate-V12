const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class VersionManager {
  constructor() {
    this.versionFile = path.join(__dirname, '..', 'version.json');
    this.changelogFile = path.join(__dirname, '..', '..', 'CHANGELOG.md');
    this.packageFile = path.join(__dirname, '..', 'package.json');
  }

  // Load current version data
  loadVersion() {
    try {
      return JSON.parse(fs.readFileSync(this.versionFile, 'utf8'));
    } catch (error) {
      // Default version structure
      return {
        version: '1.0.0',
        deploymentNumber: 0,
        lastDeployment: null,
        environment: 'development',
        buildNumber: '0',
        gitCommit: '',
        changelog: []
      };
    }
  }

  // Save version data
  saveVersion(versionData) {
    fs.writeFileSync(this.versionFile, JSON.stringify(versionData, null, 2));
  }

  // Get current git commit hash
  getGitCommit() {
    try {
      return execSync('git rev-parse --short HEAD').toString().trim();
    } catch (error) {
      return 'unknown';
    }
  }

  // Get current git branch
  getGitBranch() {
    try {
      return execSync('git rev-parse --abbrev-ref HEAD').toString().trim();
    } catch (error) {
      return 'unknown';
    }
  }

  // Increment version based on type
  incrementVersion(type = 'patch') {
    const versionData = this.loadVersion();
    const [major, minor, patch] = versionData.version.split('.').map(Number);
    
    let newVersion;
    switch (type) {
      case 'major':
        newVersion = `${major + 1}.0.0`;
        break;
      case 'minor':
        newVersion = `${major}.${minor + 1}.0`;
        break;
      case 'patch':
      default:
        newVersion = `${major}.${minor}.${patch + 1}`;
        break;
    }
    
    versionData.version = newVersion;
    return versionData;
  }

  // Prepare for deployment
  prepareDeployment(environment = 'production', changes = []) {
    const versionData = this.loadVersion();
    
    // Increment deployment number
    versionData.deploymentNumber += 1;
    
    // Update deployment info
    versionData.lastDeployment = new Date().toISOString();
    versionData.environment = environment;
    versionData.buildNumber = Date.now().toString();
    versionData.gitCommit = this.getGitCommit();
    versionData.gitBranch = this.getGitBranch();
    
    // Add changes to changelog
    if (changes.length > 0) {
      versionData.changelog.unshift({
        version: versionData.version,
        deployment: versionData.deploymentNumber,
        date: versionData.lastDeployment,
        changes: changes,
        commit: versionData.gitCommit
      });
      
      // Keep only last 20 entries
      versionData.changelog = versionData.changelog.slice(0, 20);
    }
    
    // Save updated version
    this.saveVersion(versionData);
    
    // Update package.json version
    this.updatePackageVersion(versionData.version);
    
    return versionData;
  }

  // Update package.json version
  updatePackageVersion(version) {
    try {
      const packageData = JSON.parse(fs.readFileSync(this.packageFile, 'utf8'));
      packageData.version = version;
      fs.writeFileSync(this.packageFile, JSON.stringify(packageData, null, 2));
    } catch (error) {
      console.error('Failed to update package.json:', error);
    }
  }

  // Generate deployment report
  generateReport() {
    const versionData = this.loadVersion();
    
    console.log('\n' + '='.repeat(60));
    console.log('DEPLOYMENT INFORMATION');
    console.log('='.repeat(60));
    console.log(`Version:        ${versionData.version}`);
    console.log(`Deployment #:   ${versionData.deploymentNumber}`);
    console.log(`Environment:    ${versionData.environment}`);
    console.log(`Build Number:   ${versionData.buildNumber}`);
    console.log(`Git Commit:     ${versionData.gitCommit}`);
    console.log(`Git Branch:     ${versionData.gitBranch}`);
    console.log(`Last Deploy:    ${versionData.lastDeployment || 'Never'}`);
    console.log('='.repeat(60));
    
    if (versionData.changelog.length > 0) {
      console.log('\nRECENT CHANGES:');
      versionData.changelog.slice(0, 5).forEach(entry => {
        console.log(`\nv${entry.version} (Deployment #${entry.deployment})`);
        console.log(`  Date: ${new Date(entry.date).toLocaleDateString()}`);
        entry.changes.forEach(change => {
          console.log(`  - ${change}`);
        });
      });
    }
    
    console.log('\n' + '='.repeat(60) + '\n');
  }

  // Update changelog file
  updateChangelogFile(changes) {
    const versionData = this.loadVersion();
    const date = new Date().toISOString().split('T')[0];
    
    let changelog = fs.readFileSync(this.changelogFile, 'utf8');
    
    // Find the [Unreleased] section
    const unreleasedIndex = changelog.indexOf('## [Unreleased]');
    
    if (unreleasedIndex !== -1) {
      // Create new version entry
      const newEntry = `## [${versionData.version}] - ${date} - Deployment #${versionData.deploymentNumber}\n\n### Changes\n${changes.map(c => `- ${c}`).join('\n')}\n\n`;
      
      // Insert after [Unreleased] section
      const beforeUnreleased = changelog.substring(0, unreleasedIndex + '## [Unreleased]'.length + 1);
      const afterUnreleased = changelog.substring(unreleasedIndex + '## [Unreleased]'.length + 1);
      
      changelog = beforeUnreleased + '\n\n' + newEntry + afterUnreleased;
      
      fs.writeFileSync(this.changelogFile, changelog);
    }
  }
}

// CLI interface
if (require.main === module) {
  const manager = new VersionManager();
  const args = process.argv.slice(2);
  const command = args[0];
  
  switch (command) {
    case 'increment':
      const type = args[1] || 'patch';
      const updated = manager.incrementVersion(type);
      manager.saveVersion(updated);
      console.log(`Version incremented to ${updated.version}`);
      break;
      
    case 'deploy':
      const env = args[1] || 'production';
      const changes = args.slice(2);
      const deployment = manager.prepareDeployment(env, changes);
      manager.generateReport();
      if (changes.length > 0) {
        manager.updateChangelogFile(changes);
      }
      break;
      
    case 'report':
      manager.generateReport();
      break;
      
    case 'current':
      const current = manager.loadVersion();
      console.log(`Current version: ${current.version} (Deployment #${current.deploymentNumber})`);
      break;
      
    default:
      console.log('Usage:');
      console.log('  node version-manager.js increment [major|minor|patch]');
      console.log('  node version-manager.js deploy [environment] [change1] [change2] ...');
      console.log('  node version-manager.js report');
      console.log('  node version-manager.js current');
  }
}

module.exports = VersionManager;