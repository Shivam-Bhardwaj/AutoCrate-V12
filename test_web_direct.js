// Test web API directly
const testData = {
  product_length: 96,
  product_width: 48,
  product_height: 30,
  product_weight: 1000,
  panel_thickness: 0.25,
  assembly_time_code: 2.0,
  panel_grade_code: "ASTM"
};

async function testWebAPI() {
  try {
    const response = await fetch('http://localhost:3000/api/generate-nx', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(testData)
    });
    
    const data = await response.json();
    
    if (data.expressions) {
      // Find the problematic lines
      const lines = data.expressions.split('\n');
      const problemLines = lines.filter(line => 
        line.includes('LP_Panel_Assembly_Width') || 
        line.includes('RP_Panel_Assembly_Width') ||
        line.includes('PANEL_End_Assy_Overall_Width') ||
        line.includes('LP_Panel_Assembly_Length') ||
        line.includes('RP_Panel_Assembly_Length')
      );
      
      console.log('Found relevant lines:');
      problemLines.forEach(line => console.log(line));
      
      // Save full output for analysis
      require('fs').writeFileSync('web_test_output.exp', data.expressions);
      console.log('\nFull output saved to web_test_output.exp');
    } else {
      console.log('Error:', data);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

// Wait a moment for server to be ready
setTimeout(testWebAPI, 2000);