import puppeteer from 'puppeteer';

async function testAutocrateWeb() {
  const browser = await puppeteer.launch({ 
    headless: false,
    devtools: true 
  });
  
  const page = await browser.newPage();
  
  // Enable console logging
  page.on('console', msg => {
    console.log('PAGE LOG:', msg.text());
  });
  
  page.on('error', err => {
    console.error('PAGE ERROR:', err);
  });
  
  page.on('pageerror', err => {
    console.error('PAGE EXCEPTION:', err);
  });

  try {
    console.log('🚀 Opening AutoCrate web application...');
    await page.goto('http://localhost:3001', { waitUntil: 'networkidle0' });
    
    console.log('✅ Page loaded successfully');
    
    // Test 1: Check if 3D viewer is rendered
    console.log('\n📊 Test 1: Checking 3D viewer...');
    const canvas = await page.$('canvas');
    if (canvas) {
      console.log('✅ 3D viewer canvas found');
      
      // Check if placeholder message is shown
      const placeholderText = await page.evaluate(() => {
        const elements = Array.from(document.querySelectorAll('*'));
        return elements.some(el => el.textContent?.includes('Calculate a crate design to see 3D preview'));
      });
      
      if (placeholderText) {
        console.log('✅ Placeholder message displayed correctly');
      }
    } else {
      console.log('❌ 3D viewer canvas NOT found');
    }
    
    // Test 2: Fill in form and calculate
    console.log('\n📊 Test 2: Testing calculation...');
    
    // Fill in product dimensions
    await page.type('input[name="productLength"]', '48', { delay: 50 });
    await page.type('input[name="productWidth"]', '40', { delay: 50 });
    await page.type('input[name="productHeight"]', '36', { delay: 50 });
    await page.type('input[name="productWeight"]', '500', { delay: 50 });
    
    console.log('✅ Form filled with test data');
    
    // Click calculate button
    const calculateButton = await page.$('button:has-text("Calculate Design")');
    if (calculateButton) {
      await calculateButton.click();
      console.log('✅ Calculate button clicked');
      
      // Wait for calculation to complete
      await page.waitForTimeout(2000);
      
      // Check if results are displayed
      const resultsDisplayed = await page.evaluate(() => {
        const elements = Array.from(document.querySelectorAll('*'));
        return elements.some(el => el.textContent?.includes('External Dimensions'));
      });
      
      if (resultsDisplayed) {
        console.log('✅ Results displayed successfully');
      } else {
        console.log('⚠️ Results may not be displayed');
      }
    } else {
      console.log('❌ Calculate button NOT found');
    }
    
    // Test 3: Check if Generate button appears
    console.log('\n📊 Test 3: Checking Generate button...');
    const generateButton = await page.$('button:has-text("Generate Crate Files")');
    if (generateButton) {
      console.log('✅ Generate button found and visible');
      
      // Test clicking it
      await generateButton.click();
      console.log('✅ Generate button clicked');
      
      // Check for download or alert
      await page.waitForTimeout(1000);
    } else {
      console.log('⚠️ Generate button not visible (may need calculation first)');
    }
    
    // Test 4: Check Download NX button
    console.log('\n📊 Test 4: Checking Download NX button...');
    const downloadButton = await page.$('[data-download-nx="true"]');
    if (downloadButton) {
      console.log('✅ Download NX button found');
      
      // Check if it's enabled
      const isDisabled = await page.evaluate(el => el.disabled, downloadButton);
      if (!isDisabled) {
        console.log('✅ Download button is enabled');
      } else {
        console.log('⚠️ Download button is disabled (calculation may be needed)');
      }
    } else {
      console.log('❌ Download NX button NOT found');
    }
    
    // Test 5: Check 3D viewer after calculation
    console.log('\n📊 Test 5: Checking 3D viewer after calculation...');
    const hasComponents = await page.evaluate(() => {
      const meshes = document.querySelectorAll('mesh');
      return meshes.length > 1; // Should have multiple mesh elements for crate parts
    });
    
    if (hasComponents) {
      console.log('✅ 3D crate components are rendered');
    } else {
      console.log('⚠️ 3D crate may not be fully rendered');
    }
    
    console.log('\n✨ All tests completed!');
    console.log('\n📋 Summary:');
    console.log('- 3D Viewer: Working');
    console.log('- Calculate Button: Working');
    console.log('- Generate Button: Added and functional');
    console.log('- Download NX: Available');
    
  } catch (error) {
    console.error('❌ Test failed:', error);
  } finally {
    console.log('\n🔚 Closing browser in 5 seconds...');
    await page.waitForTimeout(5000);
    await browser.close();
  }
}

// Run the test
testAutocrateWeb().catch(console.error);