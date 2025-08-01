# Simple Test Folder Setup

## Create Test Folder
```
AutoCrate V12\test_results\
  ├── screenshots\
  └── test_notes.txt
```

## Setup Steps
1. Make folder: `test_results`
2. Make subfolder: `test_results\screenshots`
3. Create file: `test_results\test_notes.txt`

## How to Use

### 1. Take Screenshot
- **Win + Shift + S** → Select area
- **Ctrl + V** in Paint → Save to `test_results\screenshots\`
- Name it: `test1.png`, `test2.png`, etc.

### 2. Write in test_notes.txt
```
test1.png - 48x48x48, 1000 lbs - basic crate worked fine
test2.png - 20x20x100, 500 lbs - error with horizontal cleats
test3.png - 100x100x20, 2000 lbs - slow but generated correctly
```

## Simple Format
```
[screenshot_name] - [dimensions, weight] - [what happened]
```

That's it. One folder, one text file, screenshots numbered.