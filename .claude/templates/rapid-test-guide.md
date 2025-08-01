# Rapid Testing Guide

## Quick Test Setup (Pick One)

### Option 1: Dev Interface (Fastest)
```
start_dev.bat
```
- Hot reload
- Instant results
- Best for quick iterations

### Option 2: Production Build
```
start_production.bat
```
- Full executable test
- Real user experience

### Option 3: Quick Test Suite
```
Open AutoCrate → Quick Test Suite button
```
- 10 automatic test cases
- Good for regression testing

## Test Process (3 Steps)

### Step 1: Setup Test
1. Pick dimensions: `L x W x H`
2. Set weight: `XXX lbs`
3. Click generate

### Step 2: Record Results
**Quick Note**: [One sentence what you're testing]

**Screenshot**: [Drag image here or paste filename]

**Result**: ✅ Works / ❌ Broken / ⚠️ Weird

### Step 3: Log Details (If Needed)
```
Test: [short description]
Input: L_W_H_weight
Result: [what happened]
Issue: [if broken, what's wrong]
```

## Speed Testing Order

### Level 1: Basic Function (30 seconds)
- Standard size: `48x48x48, 1000 lbs`
- Does it generate expressions?
- Screenshot result

### Level 2: Edge Cases (2 minutes)
- Very tall: `20x20x100, 500 lbs`
- Very wide: `100x100x20, 2000 lbs`
- Very small: `12x12x12, 50 lbs`

### Level 3: Problem Cases (5 minutes)
- Known bug dimensions
- Extreme values
- Special configurations

## Test Log Template

```
## [Date] - [Feature Name]

### Quick Tests
- Basic: ✅/❌ [screenshot]
- Edge 1: ✅/❌ [screenshot] 
- Edge 2: ✅/❌ [screenshot]

### Notes
[One line per observation]

### Next
[What to test next or who to tell]
```

## Auto-Log Script (Optional)

For automated result capture:
```python
# test_logger.py - Run this to auto-capture some results
# Just put in same folder and run: python test_logger.py
```

## Common Test Scenarios

### 1. Panel Logic Test
- Input: `48x48x48, 1000`
- Look for: All panels have cleats
- Screenshot: Expression file or GUI result

### 2. Splice Test  
- Input: `96x96x30, 2000`
- Look for: Horizontal splices get cleats
- Screenshot: Any splice-related output

### 3. Edge Dimensions
- Input: `20x20x100, 500`
- Look for: No crashes, reasonable output
- Screenshot: Overall result

### 4. Quick Regression
- Use Quick Test Suite button
- Look for: All 10 tests pass
- Screenshot: Final summary

---

**Remember**: Basic text + image = complete test record