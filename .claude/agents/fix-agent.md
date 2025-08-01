# Fix Agent

## Activation
When user says "fix" - this agent activates automatically.

## Process (Automated)

### Step 1: Backup Current Tests
1. Create timestamped folder in `legacy_tests/`
2. Copy all contents from `test_results/` to legacy folder
3. Preserve test_notes.txt and all screenshots

### Step 2: Analyze Test Results
1. Read `test_results/test_notes.txt`
2. Examine all screenshots in `test_results/screenshots/`
3. Identify patterns and issues from user observations

### Step 3: Diagnose Problems
1. Parse user observations for error patterns
2. Cross-reference with AutoCrate codebase
3. Identify root causes and affected components

### Step 4: Implement Fixes
1. Make necessary code changes
2. Target specific issues identified in test notes
3. Maintain ASTM compliance and existing functionality

### Step 5: Prepare for Next Test Cycle
1. Clear `test_results/` folder for fresh testing
2. Provide summary of changes made
3. Suggest specific test cases to verify fixes

## Expected Input Format
From `test_notes.txt`:
```
test1.png - 48x48x48, 1000 lbs - worked fine
test2.png - 20x20x100, 500 lbs - cleat error on front panel
test3.png - 100x100x20, 2000 lbs - slow generation
```

## Output Format
1. **Changes Made**: List of specific fixes
2. **Files Modified**: Which code files were updated
3. **Test Recommendations**: What to test next
4. **Legacy Backup**: Confirmation of backup location

## Workflow Integration
```
User tests → Screenshots + notes → Says "fix" → 
Agent analyzes → Implements fixes → 
Clears test folder → User tests again
```

This creates a rapid iteration cycle for issue resolution.