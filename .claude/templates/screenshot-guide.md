# Screenshot & Notes Quick Guide

## Taking Screenshots

### Windows Built-in (Fastest)
- **Win + Shift + S** → Select area → Auto-copies to clipboard
- **Win + PrtScn** → Full screen → Saves to Pictures\Screenshots
- **Alt + PrtScn** → Current window only

### Where Screenshots Go
```
C:\Users\[YourName]\Pictures\Screenshots\
```
Named like: `Screenshot 2025-08-01 143022.png`

## Quick Note Methods

### Option 1: Sticky Notes (Super Fast)
- **Win + R** → type `stikynot` → Enter
- Type your note
- Stays on screen while you work

### Option 2: Notepad
- **Win + R** → type `notepad` → Enter
- One line per test
- Save as `test_notes_[date].txt`

### Option 3: Use Test Logger
```
python test_logger.py
```
Opens pre-made template file

## Rapid Workflow

### 1. Start Test
- Open AutoCrate
- **Win + Shift + S** (get ready to screenshot)

### 2. Run Test  
- Enter dimensions
- Click generate
- **Immediately screenshot** the result

### 3. Quick Note
- **Win + R** → `stikynot`
- Type: `48x48x48 - worked fine`
- Or: `20x100x20 - error in cleats`

### 4. File Names
Screenshots auto-named by Windows, just note the time:
- `Test at 2:30pm - Screenshot 2025-08-01 143022.png`

## Organization

### Folder Structure
```
Pictures\Screenshots\
  AutoCrate_Tests\
    2025-08-01\
      screenshot1.png
      screenshot2.png
      notes.txt
```

### Quick Setup
1. Make folder: `Pictures\Screenshots\AutoCrate_Tests`
2. New folder for each day: `2025-08-01`
3. Move screenshots there after testing
4. Keep one notes file per day

## Note Format (One Line Each)
```
14:30 - 48x48x48,1000 - ✅ basic works
14:32 - 20x20x100,500 - ❌ cleat error 
14:35 - 100x100x20,2000 - ⚠️ slow but works
```

## Screenshot Tips

### What to Capture
- **Full result window** (most important)
- **Error messages** (if any)
- **Generated file list** (if applicable)
- **Input values** (if not obvious)

### Don't Capture
- Empty screens
- Loading screens
- Your desktop background

## Integration with Testing

### After Screenshots/Notes
1. Copy screenshot names to test log
2. Add one-line observations
3. Ready for prompt refinement when needed

### Example Entry
```
Test: Very tall crate
Input: 20x20x100, 500 lbs
Result: ❌ 
Screenshot: Screenshot 2025-08-01 143522.png
Notes: Horizontal cleats missing on front panel
```

---

**Remember**: Screenshot first, note second, organize later