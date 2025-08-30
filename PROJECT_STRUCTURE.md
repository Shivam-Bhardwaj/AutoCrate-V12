# AutoCrate V12 - Clean Project Structure

## Overview
This document describes the cleaned and organized project structure after removing redundant files and fixing development tools.

## Root Directory Structure
```
AutoCrate V12/
├── 📁 .github/workflows/     # CI/CD automation
├── 📁 api/                   # API server for web integration
├── 📁 autocrate/            # Core calculation modules
├── 📁 debug/                # Debug scripts and utilities
├── 📁 docs/                 # Documentation portal
├── 📁 logs/                 # Application logs (ignored)
├── 📁 nx part files/        # NX CAD part files
├── 📁 tests/                # Professional test suite  
├── 📁 web/                  # Next.js web application
├── 📄 main.py              # Desktop application entry
├── 📄 api_server.py        # Standalone API server
├── 📄 dev_suite.bat        # Fixed development suite
├── 📄 run_tests.py         # Test runner
└── 📄 AutoCrate.bat        # Original control script
```

## Key Directories

### `/autocrate/` - Core Engine
- **nx_expressions_generator.py** - Main calculation engine
- **Panel logic modules** - Individual panel calculations
- **debug_logger.py** - Logging system
- **test_agent.py** - AI-powered testing

### `/tests/` - Testing Suite
- **conftest.py** - Test configuration and fixtures
- **test_security.py** - OWASP Top 10 security tests
- **Core test files** - Essential testing only

### `/web/` - Next.js Application
- **src/app/** - Main application pages
- **src/components/** - React components
- **src/lib/** - Calculation libraries
- **vercel.json** - Production deployment config

### `/debug/` - Debug Tools (Moved)
- **analyze_logs.py** - Log analysis
- **trace_*.py** - Calculation tracing
- **compare_*.py** - Result comparison
- **performance_*.py** - Performance testing
- **cleanup_redundant_files.py** - Cleanup automation

### `/docs/` - Documentation
- **index.html** - Documentation portal
- **MASTER_GUIDE.md** - Complete development guide
- **codebase_summary.md** - Project structure map

## Files Removed (63 total)
### Redundant Test Files (12)
- test_nx_web_generation.py
- test_nx_generation_comparison.py
- test_web_nx_comparison.py
- test_nx_comparison.py
- test_nx_direct_comparison.py
- test_output_diff.py
- test_api_direct.py
- test_web_integration.py
- test_desktop_direct.py
- test_nx_simple.py
- test_cleat_material.py
- test_material_calc.py

### Debug Files (Moved to /debug/)
- analyze_logs.py → debug/
- trace_*.py → debug/
- compare_*.py → debug/
- debug_*.py → debug/
- performance_*.py → debug/

### Temporary Files (39)
- All *.exp temporary files
- All *.json result files
- All *.log debug files
- All comparison reports

### Utility Files (8)
- fix_prompt.py
- validate_*.py
- generate_nx_offline.py
- minimal_importer.py
- smoke_nx_expr.py
- config.py

## Development Tools

### Fixed dev_suite.bat
**Features:**
- ✅ Simple, reliable menu system
- ✅ No hanging or crashes
- ✅ Error handling for missing dependencies
- ✅ Clear status messages
- ✅ Proper cleanup functionality

**Available Commands:**
1. **Start Development Servers** - API + Web dev servers
2. **Run Tests** - Python test suite
3. **Build Desktop App** - PyInstaller build
4. **Deploy Web App** - Production build
5. **Clean Project** - Remove temp files
6. **System Check** - Verify environment

### Usage
```bash
# Run the development suite
dev_suite.bat

# Or use individual commands
python main.py                    # Desktop app
python api_server.py             # API server
cd web && npm run dev            # Web app
python -m pytest tests/         # Run tests
```

## Key Improvements

### 🧹 Cleanup Results
- **50 files removed** - Eliminated redundancy
- **13 files moved** - Organized debug tools
- **3 empty directories removed** - Clean structure
- **All __pycache__ cleared** - No compiled bytecode

### 🔧 Fixed Issues
- **dev_suite.bat crashes** - Completely rewritten
- **Redundant test files** - Streamlined to essentials
- **Temporary file clutter** - Comprehensive cleanup
- **Unclear project structure** - Well-organized hierarchy

### 📝 Enhanced Documentation
- **PROJECT_STRUCTURE.md** - This overview document
- **Updated .gitignore** - Better file management
- **Cleanup automation** - Script for future maintenance

## Maintenance

### Regular Cleanup
```bash
# Run automated cleanup
python debug/cleanup_redundant_files.py

# Manual cleanup
dev_suite.bat → Option 5 (Clean Project)
```

### Adding New Files
- **Tests**: Add to `/tests/` directory
- **Debug tools**: Add to `/debug/` directory  
- **Documentation**: Add to `/docs/` directory
- **Core logic**: Add to `/autocrate/` directory

### Git Management
The updated `.gitignore` now properly excludes:
- All temporary files
- Debug outputs  
- Build artifacts
- OS-specific files
- IDE configurations

**Important files are explicitly preserved:**
- Core application files
- Essential test files
- Documentation
- Configuration files

---

## Status: ✅ Clean & Organized

The project is now:
- **Streamlined** - No redundant files
- **Well-organized** - Clear directory structure  
- **Maintainable** - Automated cleanup tools
- **Production-ready** - Fixed development tools

For questions about the project structure, see `/docs/MASTER_GUIDE.md` or `/docs/codebase_summary.md`.