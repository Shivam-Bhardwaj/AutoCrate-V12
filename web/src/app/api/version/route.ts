import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export const dynamic = 'force-dynamic';

export async function GET() {
  try {
    // Read version.json file
    const versionPath = path.join(process.cwd(), 'version.json');
    
    if (!fs.existsSync(versionPath)) {
      return NextResponse.json(
        { 
          version: '1.0.0',
          deploymentNumber: 0,
          lastDeployment: null,
          environment: 'development',
          buildNumber: '0',
          gitCommit: '',
          changelog: []
        },
        { status: 200 }
      );
    }
    
    const versionData = JSON.parse(fs.readFileSync(versionPath, 'utf8'));
    
    // Add server-side information
    versionData.serverTime = new Date().toISOString();
    versionData.nodeVersion = process.version;
    
    return NextResponse.json(versionData, {
      status: 200,
      headers: {
        'Cache-Control': 'no-store, no-cache, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      }
    });
  } catch (error) {
    console.error('Error reading version data:', error);
    return NextResponse.json(
      { error: 'Failed to fetch version information' },
      { status: 500 }
    );
  }
}