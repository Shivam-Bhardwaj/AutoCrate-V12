// Test web NX expression generation
import { AutoCrateCalculator } from './web/src/lib/autocrate-calculations-fixed.js';

const calculator = new AutoCrateCalculator();

// Test parameters matching desktop defaults
const product = {
  length: 96,
  width: 48,
  height: 30,
  weight: 1000
};

const materials = {
  panelThickness: 0.75,
  materialType: 'plywood',
  lumberSizes: ['2x4', '2x6', '2x8']
};

const result = calculator.calculate(
  product,
  materials,
  2,     // clearance
  false, // includeTop
  2,     // clearanceAbove
  4,     // groundClearance
  1.5,   // cleatThickness
  3.5,   // cleatMemberWidth
  1.5,   // floorboardThickness
  true,  // allow3x4Skids
  6,     // maxGap
  1.5,   // minCustom
  false  // forceCustomBoard
);

console.log("Web NX Generation Results:");
console.log("===========================");
console.log(`Overall Width OD: ${result.crate_dimensions.overall_width_od}`);
console.log(`Overall Length OD: ${result.crate_dimensions.overall_length_od}`);
console.log(`Front Panel Width: ${result.panels.front.width}`);
console.log(`Front Panel Height: ${result.panels.front.height}`);
console.log(`End Panel Length: ${result.panels.left.length || result.panels.left.width}`);
console.log(`End Panel Height: ${result.panels.left.height}`);
console.log(`Skid Count: ${result.skid_parameters.count}`);
console.log("\nFull dimensions object:");
console.log(JSON.stringify(result.crate_dimensions, null, 2));
console.log("\nFull panels object:");
console.log(JSON.stringify({
  front: { width: result.panels.front.width, height: result.panels.front.height },
  back: { width: result.panels.back.width, height: result.panels.back.height },
  left: { width: result.panels.left.width, height: result.panels.left.height, length: result.panels.left.length },
  right: { width: result.panels.right.width, height: result.panels.right.height, length: result.panels.right.length }
}, null, 2));