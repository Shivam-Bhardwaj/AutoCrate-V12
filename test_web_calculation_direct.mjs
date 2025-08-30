// Direct test of web calculation module
import { AutoCrateCalculator } from './web/src/lib/autocrate-calculations-fixed.ts';

const calculator = new AutoCrateCalculator();

// Test parameters matching desktop test
const result = calculator.calculate(
  {
    length: 96,
    width: 48,
    height: 30,
    weight: 1000
  },
  {
    panelThickness: 0.75,
    materialType: 'plywood',
    lumberSizes: ['2x4', '2x6', '2x8']
  },
  2,      // clearance
  false,  // includeTop
  2,      // clearanceAbove
  4,      // groundClearance
  1.5,    // cleatThickness
  3.5,    // cleatMemberWidth
  1.5,    // floorboardThickness
  true,   // allow3x4Skids
  6,      // maxGap
  1.5,    // minCustom
  false   // forceCustomBoard
);

console.log("=".repeat(60));
console.log("WEB CALCULATION RESULTS:");
console.log("=".repeat(60));
console.log(`Overall Width OD: ${result.crate_dimensions.overall_width_od}`);
console.log(`Overall Length OD: ${result.crate_dimensions.overall_length_od}`);
console.log(`Front Panel Width: ${result.panels.front.width}`);
console.log(`Front Panel Height: ${result.panels.front.height}`);
console.log(`End Panel Length: ${result.panels.left.width}`);
console.log(`End Panel Height: ${result.panels.left.height}`);
console.log(`Skid Count: ${result.skid_parameters.count}`);

console.log("\n" + "=".repeat(60));
console.log("COMPARISON WITH DESKTOP:");
console.log("=".repeat(60));
console.log("Desktop Values:");
console.log("  Overall Width OD: 52.0");
console.log("  Overall Length OD: 105.0");
console.log("  Front Panel Width: 56.5");
console.log("  Front Panel Height: 33.5");
console.log("  End Panel Length: 100.5");
console.log("  End Panel Height: 33.0");

console.log("\nWeb Values:");
console.log(`  Overall Width OD: ${result.crate_dimensions.overall_width_od}`);
console.log(`  Overall Length OD: ${result.crate_dimensions.overall_length_od}`);
console.log(`  Front Panel Width: ${result.panels.front.width}`);
console.log(`  Front Panel Height: ${result.panels.front.height}`);
console.log(`  End Panel Length: ${result.panels.left.width}`);
console.log(`  End Panel Height: ${result.panels.left.height}`);

console.log("\nDifferences:");
console.log(`  Overall Width OD: ${(result.crate_dimensions.overall_width_od - 52.0).toFixed(3)}`);
console.log(`  Overall Length OD: ${(result.crate_dimensions.overall_length_od - 105.0).toFixed(3)}`);
console.log(`  Front Panel Width: ${(result.panels.front.width - 56.5).toFixed(3)}`);
console.log(`  Front Panel Height: ${(result.panels.front.height - 33.5).toFixed(3)}`);
console.log(`  End Panel Length: ${(result.panels.left.width - 100.5).toFixed(3)}`);
console.log(`  End Panel Height: ${(result.panels.left.height - 33.0).toFixed(3)}`);