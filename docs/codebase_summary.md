# AutoCrate V12 Codebase Summary

## Project Structure Overview

AutoCrate V12 is a professional crate design application with both desktop and web interfaces, featuring comprehensive testing and deployment automation.

## Core Files Map

### Entry Points
- **`main.py`** - Desktop application launcher with logging and error handling
- **`web/src/app/page.tsx`** - Main web application interface
- **`api/main.py`** - Web API server entry point

### Core Calculation Engine
- **`autocrate/nx_expressions_generator.py`** - Main NX expression generation engine
- **`autocrate/front_panel_logic.py`** - Front panel dimension calculations
- **`autocrate/back_panel_logic.py`** - Back panel dimension calculations  
- **`autocrate/left_panel_logic.py`** - Left panel dimension calculations
- **`autocrate/right_panel_logic.py`** - Right panel dimension calculations
- **`autocrate/top_panel_logic.py`** - Top panel dimension calculations
- **`autocrate/end_panel_logic.py`** - End panel dimension calculations
- **`autocrate/skid_logic.py`** - Skid/base structure calculations
- **`autocrate/floorboard_logic.py`** - Floorboard layout calculations
- **`web/src/lib/autocrate-calculations-fixed.ts`** - Web version calculations (matches desktop logic)

### UI Components (Desktop)
- **GUI Framework**: Tkinter-based interface in `nx_expressions_generator.py`
- **Input Forms**: Parameter entry for dimensions, weight, materials
- **Results Display**: Expression output and calculation results

### UI Components (Web)
- **`web/src/components/Calculator.tsx`** - Main calculation interface
- **`web/src/components/ProfessionalCrateViewer-fixed.tsx`** - 3D visualization with correct NX coordinates
- **`web/src/components/ResultsPanel.tsx`** - Calculation results display
- **`web/src/components/BOMPanel.tsx`** - Bill of materials display

### Logging & Debugging
- **`autocrate/debug_logger.py`** - Comprehensive logging system with JSON structured logs
- **`autocrate/startup_analyzer.py`** - Automatic startup health checks and previous run analysis
- **`autocrate/log_analyst.py`** - Intelligent log analysis and insights

### Testing Infrastructure  
- **`test_nx_generation_comparison.py`** - Desktop vs web calculation validation
- **`run_tests.py`** - Comprehensive test runner with reporting
- **`autocrate/test_agent.py`** - AI-powered automated testing agent
- **`test_*.py` files** - Individual test modules for specific components

### Configuration & Setup
- **`requirements.txt`** - Python dependencies for desktop application
- **`web/package.json`** - Node.js dependencies for web application  
- **`package.json`** - Monorepo configuration with scripts
- **`AutoCrate.bat`** - Master control script for all operations

### Build & Deployment
- **`AutoCrate.spec`** - PyInstaller configuration for executable builds
- **`web/vercel.json`** - Vercel deployment configuration
- **`Dockerfile`** - Container configuration for API server

### Documentation
- **`README.md`** - Main project documentation with features and setup
- **`CLAUDE.md`** - AI development guide and project instructions  
- **`CHANGELOG.md`** - Version history and changes
- **Various `.md` files** - Specialized documentation for different aspects

## Key Connections & Dependencies

### Data Flow
1. **User Input** → Desktop GUI or Web Interface
2. **Validation** → Input parameter checking and sanitization
3. **Core Engine** → `nx_expressions_generator.py` processes calculations
4. **Panel Logic** → Individual panel modules calculate dimensions
5. **Output Generation** → NX expressions file (.exp) and 3D visualization
6. **Results Display** → Desktop results window or web results panel

### Module Dependencies
```
main.py
├── autocrate/debug_logger.py
├── autocrate/startup_analyzer.py  
└── autocrate/nx_expressions_generator.py
    ├── autocrate/front_panel_logic.py
    ├── autocrate/back_panel_logic.py
    ├── autocrate/left_panel_logic.py
    ├── autocrate/right_panel_logic.py
    ├── autocrate/top_panel_logic.py
    ├── autocrate/end_panel_logic.py
    ├── autocrate/skid_logic.py
    └── autocrate/floorboard_logic.py

web/src/app/page.tsx
├── web/src/components/Calculator.tsx
├── web/src/components/ProfessionalCrateViewer-fixed.tsx
├── web/src/components/ResultsPanel.tsx
└── web/src/lib/autocrate-calculations-fixed.ts
```

### Critical Consistency Points
- **Calculation Logic**: Desktop and web must produce identical results
- **Coordinate Systems**: NX expressions use X/Y/Z, Three.js uses X/Z/Y mapping  
- **Material Adjustments**: Vertical cleat material additions must match exactly
- **Rounding**: All dimensions rounded to 2 decimal places consistently

## File Categories by Purpose

### Core Business Logic (18 files)
- All files in `autocrate/` directory containing calculation logic
- `web/src/lib/autocrate-calculations-fixed.ts` (web equivalent)

### User Interface (8 files)
- Desktop: GUI embedded in `nx_expressions_generator.py`
- Web: React components in `web/src/components/`

### Testing & Quality (25+ files)  
- Test files: `test_*.py` pattern
- Quality tools: logging, analysis, debugging utilities

### Configuration & Build (12 files)
- Package management: `package.json`, `requirements.txt`
- Build configs: `*.spec`, `Dockerfile`, `vercel.json`
- Control scripts: `AutoCrate.bat`, various `.bat` files

### Documentation (15+ files)
- User docs: `README.md`, usage guides
- Technical docs: `CLAUDE.md`, implementation notes
- Generated logs and reports in `logs/` directories

## Development Workflow

### Local Development
1. **Desktop**: Run `python main.py` or use `AutoCrate.bat`
2. **Web**: Run `npm run dev` from `web/` directory  
3. **API**: Run `python api/main.py` for backend services
4. **Tests**: Use `run_tests.py` or `pytest` for validation

### Build Process
1. **Desktop**: `pyinstaller` creates standalone executable
2. **Web**: `npm run build` creates optimized static files
3. **Deployment**: Vercel handles web deployment automatically

### Quality Assurance
- Automated tests verify calculation accuracy
- Cross-platform compatibility testing
- Performance benchmarking for calculation speed
- Code style enforcement through linting

This codebase represents a mature, well-tested engineering application with comprehensive documentation and professional development practices.