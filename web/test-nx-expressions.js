// Test script to verify comprehensive NX expression generation
// Run with: node test-nx-expressions.js

const { AutoCrateCalculator, generateNXExpression } = require('./src/lib/autocrate-calculations.ts');

// Test data matching desktop version
const testData = {
  product: {
    length: 72,
    width: 48,
    height: 36,
    weight: 1500
  },
  materials: {
    panelThickness: 0.75,
    materialType: 'plywood',
    lumberSizes: ['1.5x3.5', '1.5x5.5']
  },
  clearance: 2.0,
  includeTop: true
};

console.log('Testing comprehensive NX expression generation...');
console.log('Input parameters:', testData);

try {
  const calculator = new AutoCrateCalculator();
  
  const result = calculator.calculate(
    testData.product,
    testData.materials,
    testData.clearance,
    testData.includeTop,
    2.0, // clearanceAbove
    4.0, // groundClearance
    1.5, // cleatThickness
    3.5, // cleatMemberWidth
    1.5, // floorboardThickness
    true, // allow3x4Skids
    6.0, // maxGap
    1.5, // minCustom
    false // forceCustomBoard
  );
  
  console.log('\n=== Calculation Results ===');
  console.log('Crate dimensions:', result.crate_dimensions);
  console.log('Skid parameters:', result.skid_parameters);
  console.log('Floorboard instances count:', result.floorboard_parameters.instances.length);
  console.log('Front panel components:', Object.keys(result.panels.front.components));
  
  const nxExpression = generateNXExpression(result);
  const lineCount = nxExpression.split('\n').length;
  
  console.log('\n=== NX Expression File ===');
  console.log('Total lines generated:', lineCount);
  console.log('Expected lines (desktop): ~767');
  console.log('Match status:', lineCount > 500 ? 'COMPREHENSIVE ✓' : 'LIMITED ✗');
  
  // Check for key sections
  const hasSkidParams = nxExpression.includes('SKID PARAMETERS');
  const hasFloorboardInstances = nxExpression.includes('FB_Inst_1_Suppress_Flag');
  const hasIntermediateCleats = nxExpression.includes('Intermediate_Vertical_Cleat');
  const hasKlimps = nxExpression.includes('FP_Klimp_Count');
  const hasPlywoodLayout = nxExpression.includes('Plywood_1_Active');
  
  console.log('\n=== Section Verification ===');
  console.log('Skid Parameters:', hasSkidParams ? '✓' : '✗');
  console.log('Floorboard Instances:', hasFloorboardInstances ? '✓' : '✗');
  console.log('Intermediate Cleats:', hasIntermediateCleats ? '✓' : '✗');
  console.log('Klimps (Clamps):', hasKlimps ? '✓' : '✗');
  console.log('Plywood Layouts:', hasPlywoodLayout ? '✓' : '✗');
  
  const allSections = hasSkidParams && hasFloorboardInstances && hasIntermediateCleats && hasKlimps && hasPlywoodLayout;
  console.log('\nOverall Status:', allSections ? 'COMPREHENSIVE MATCH ✓' : 'MISSING SECTIONS ✗');
  
  // Save sample output for comparison
  const fs = require('fs');
  const outputFile = 'web-nx-expression-sample.exp';
  fs.writeFileSync(outputFile, nxExpression);
  console.log(`\nSample output saved to: ${outputFile}`);
  
} catch (error) {
  console.error('Test failed:', error);
}