import { AutoCrateCalculator, generateNXExpression } from './src/lib/autocrate-calculations-fixed.js';
import fs from 'fs';

// Test with exact same parameters as desktop
const calculator = new AutoCrateCalculator();

const result = calculator.calculate(
  { length: 96, width: 48, height: 30, weight: 1000 },
  { panelThickness: 0.75, materialType: 'plywood', lumberSizes: ['1.5x3.5', '1.5x5.5'] },
  2.0,  // clearance
  true, // includeTop
  2.0,  // clearanceAbove
  4.0,  // groundClearance
  1.5,  // cleatThickness
  3.5,  // cleatMemberWidth
  1.5,  // floorboardThickness
  true, // allow3x4Skids
  6.0,  // maxGap
  1.5,  // minCustom
  false // forceCustomBoard
);

const nxExpression = generateNXExpression(result);
const lineCount = nxExpression.split('\n').length;

// Save web output
fs.writeFileSync('web_nx_output.exp', nxExpression);

console.log('='*70);
console.log('WEB NX EXPRESSION GENERATION TEST');
console.log('='*70);
console.log(`Web generated ${lineCount} lines`);

// Extract key values for comparison
const extractValue = (content, param) => {
  const regex = new RegExp(`${param}\\s*=\\s*([^\\n]+)`, 'i');
  const match = content.match(regex);
  return match ? match[1].trim() : 'NOT FOUND';
};

const keyValues = [
  'Overall_Width_OD',
  'Overall_Length_OD',
  'Overall_Height_OD',
  'FP_Panel_Width',
  'FP_Panel_Height',
  'Skid_Count',
  'FB_Count'
];

console.log('\nKey Web Values:');
keyValues.forEach(key => {
  const value = extractValue(nxExpression, key);
  console.log(`  ${key}: ${value}`);
});

// Read desktop output for comparison
if (fs.existsSync('../desktop_nx_output.exp')) {
  const desktopContent = fs.readFileSync('../desktop_nx_output.exp', 'utf-8');
  const desktopLines = desktopContent.split('\n').length;
  
  console.log('\n\nCOMPARISON:');
  console.log(`Desktop: ${desktopLines} lines`);
  console.log(`Web:     ${lineCount} lines`);
  console.log(`Difference: ${Math.abs(desktopLines - lineCount)} lines`);
  
  console.log('\nKey Value Comparison:');
  keyValues.forEach(key => {
    const webValue = extractValue(nxExpression, key);
    const desktopValue = extractValue(desktopContent, key);
    const match = webValue === desktopValue ? '✓' : '✗';
    console.log(`${match} ${key}:`);
    if (webValue !== desktopValue) {
      console.log(`    Desktop: ${desktopValue}`);
      console.log(`    Web:     ${webValue}`);
    }
  });
}

console.log('\nWeb output saved to web_nx_output.exp');