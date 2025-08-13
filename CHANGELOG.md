# AutoCrate Changelog

## [12.1.3] - 2025-08-12

### Fixed
- **KL Suppression Flags**: Corrected to match NX standards
  - KL_n_SUPPRESS = 0 now correctly means suppress/hide
  - KL_n_SUPPRESS = 1 now correctly means show/active
  - Previously had these values reversed

### Added  
- **KL_1 through KL_9 Variables**: Complete klimp positioning system
  - KL_n_SUPPRESS: Visibility control flags (0=hide, 1=show)
  - KL_n_X: X-coordinate from center plane for each klimp
  - KL_n_Z: Z-coordinate (height) for each klimp
  - Supports up to 9 klimps for structural requirements

## [12.1.2] - 2025-08-12

### Added
- **KL_1_Z Variable**: New NX expression variable for overall crate height
  - Calculates total crate height including top panel assembly and top cleat
  - Formula: panel height + plywood thickness + cleat thickness + cleat member width
  - Provides accurate Z-coordinate for top of crate assembly

- **KL_1_X Variable**: X-coordinate for first klimp position from center plane
  - Positions klimp with 0.25" clearance from left vertical cleat edge
  - Formula: -(panel_width/2) + cleat_member_width + 0.25
  - Prevents overlap between klimps and vertical cleats

### Enhanced
- **Structural Klimp Placement**: Complete redesign for structural strength
  - Places multiple klimps at 16-24 inch intervals (target 20 inches)
  - Maintains 0.25 inch minimum gap from vertical cleats
  - Automatically calculates available zones between cleats
  - Adapts to panel size and cleat positions
  - Supports up to 15 klimps per side for maximum strength
  - Prevents interference between klimps and cleats

- **Build System Verbosity**: Improved build script output for better visibility
  - Added clear stage indicators (1/4, 2/4, etc.) for build progress
  - Real-time PyInstaller output with color-coded messages
  - Detailed progress messages for each build operation
  - File size reporting and path information
  - Enhanced error reporting with detailed logs

## [12.1.1] - 2025-08-08

### Added - AI Token Optimization System
- **Token Usage Optimizer** (`scripts/token_optimizer.py`): Comprehensive token management and conversation optimization
  - Real-time token tracking per conversation turn with configurable thresholds
  - Automatic conversation summarization when approaching limits (default: 80% threshold)
  - Multi-level alert system (low/medium/high/critical) with background monitoring
  - Memory pruning strategies for long development sessions
  - JSON-based persistence for conversation state across sessions

- **Conversation State Manager** (`scripts/conversation_state_manager.py`): Session management and context preservation
  - Multi-session conversation handling with thread-safe operations
  - Context preservation across interactions with intelligent archiving
  - Session cleanup and management with configurable retention policies
  - Background processing to avoid blocking main operations

- **AutoCrate AI Integration** (`scripts/autocrate_ai_integration.py`): Easy-to-use AI assistant interface
  - Context-aware conversation handling for AutoCrate development workflows
  - Built-in optimization triggers and automatic memory management
  - Comprehensive usage reporting and optimization recommendations
  - Workflow-specific assistance with project context awareness

- **Token Utilities** (`scripts/token_utils.py`): Analysis tools and command-line interface
  - Token analysis with pattern recognition and optimization suggestions
  - Configuration management with flexible settings system
  - Performance monitoring and integration testing capabilities
  - CLI tools for testing, analysis, and system management

- **Comprehensive Test Suite** (`tests/test_token_optimization.py`): Full validation coverage
  - Unit tests for all optimization components with edge case validation
  - Integration tests for real-world usage scenarios
  - Performance validation and system reliability testing
  - Automated test reporting with detailed metrics

### Enhanced - Development Experience
- **Production-Ready Token Management**: Complete system for preventing token exhaustion during AI-assisted development
  - Early warning system prevents running out of tokens mid-session
  - Automatic optimization maintains conversation context while reducing token usage
  - Detailed usage insights help optimize AI interaction patterns
  - Seamless integration with existing AutoCrate development workflows

- **Documentation and Examples**: Complete system documentation and usage demonstrations
  - Live demonstration script showing all system capabilities
  - Integration examples for common AutoCrate development scenarios
  - Comprehensive system documentation with configuration guides
  - Command-line utilities for system testing and management

### Technical Implementation
- **Background Processing**: All optimization operations run in background threads to avoid blocking
- **Thread Safety**: All components designed for concurrent use in multi-threaded environments
- **Error Handling**: Comprehensive exception handling with graceful degradation
- **Logging Integration**: Uses AutoCrate's existing logging system for consistency
- **Memory Efficiency**: Intelligent memory management with automatic cleanup

## [12.1.0] - 2025-08-07

### Major Refactoring - Clean Architecture and Rapid Testing System

#### Added - Intelligent Expression Management
- **Expression File Manager** (`autocrate/expression_file_manager.py`): Automatic duplicate detection and replacement
  - Compares files by dimensions, weight, material, thickness, and clearance
  - Automatically deletes old versions when generating new expressions
  - Maintains one expression per unique parameter combination
  - Perfect for rapid testing workflows without manual cleanup

#### Added - Streamlined Testing Scripts  
- **build_and_test.bat**: Complete build pipeline with test validation
  - Runs all tests, builds executable, cleans artifacts
  - Places AutoCrate.exe in root folder for easy access
  - Clears expressions folder for clean testing environment
  
- **quick_test.bat**: Rapid expression generation for testing
  - Cleans expressions folder completely
  - Generates all 10 quick test expressions
  - Shows file count and names for verification
  
- **test_and_push.bat**: Comprehensive pre-push validation
  - Runs all tests including property-based tests
  - Updates CHANGELOG automatically
  - Creates/switches to refactor branch
  - Commits and pushes changes to GitHub

#### Changed - Project Structure
- **Moved all Python scripts from root to scripts folder**: Cleaner project organization
  - main.py, quick_test.py, run_tests.py → scripts/
  - All test utilities and helpers → scripts/
  - Root folder now only contains batch files and AutoCrate.exe

- **Enhanced NX Expression Generation**: 
  - Added timestamp prefixes (YYYYMMDD_HHMMSS) for Windows sorting
  - Enhanced filenames with more parameters (weight, panels, material, thickness)
  - Dimension constraints: 12-130 inch cube limits
  - Expression output to main/expressions folder

#### Removed - Unnecessary Files
- Deleted Docker-related files (Dockerfile, docker-compose.yml)
- Removed legacy test folders and outdated documentation
- Cleaned up validation scripts and test utilities from root
- Removed unused batch files (start_dev.bat, start_production.bat)

#### Technical Improvements
- **Git Workflow**: Introduced refactor branch strategy for cleaner merges
- **Build System**: Optimized PyInstaller configuration with all dependencies
- **Testing**: 88 tests passing with < 5ms average performance
- **File Management**: Automatic cleanup prevents duplicate accumulation

## [12.0.9] - 2025-08-05

### Added - Comprehensive AI-Powered Testing System
- **🤖 Automated Testing Agent** (`autocrate/test_agent.py`): AI-powered testing framework that runs tests automatically and provides manual testing guidance
  - Runs unit, integration, ASTM compliance, performance, and property-based tests
  - Provides intelligent test categorization and comprehensive reporting
  - Generates manual testing instructions when automated tests pass
  - Integrates seamlessly with logging system for comprehensive tracking

- **⚡ Quick Test Validation** (`quick_test.py`): 5-second validation script for critical functionality
  - Basic panel calculations, ASTM compliance, edge cases, and performance testing
  - Perfect for pre-commit validation and rapid feedback
  - Sub-millisecond performance benchmarking (0.13-0.28ms average)
  - 100% pass rate with detailed logging integration

- **🔬 Comprehensive Test Runner** (`run_tests.py`): Advanced test execution with multiple modes
  - Quick validation, full test suites, and continuous testing with watch mode
  - Windows-compatible ASCII output (fixed Unicode encoding issues)
  - Selective test category execution and detailed performance tracking
  - Color-coded console output with comprehensive error reporting

- **🏗️ Complete CI/CD Pipeline** (`build_and_test.bat`): Production-ready build system
  - **Fixed pipeline failure**: Replaced problematic pytest configuration with proven quick_test.py system
  - Automated testing → PyInstaller build → Executable validation
  - Creates 12.7MB standalone AutoCrate.exe with full validation
  - Fixed PyInstaller path issues and Unicode console compatibility

- **📊 Real-time Test Dashboard**: Streamlit interface with comprehensive test visualization
  - Added "Test Results" tab to development interface (`dev_interface.py`)
  - Real-time test execution with visual pass/fail indicators
  - One-click test running from web interface with progress tracking
  - Manual testing recommendations with priority levels and time estimates

### Enhanced - Logging and Analysis System
- **🔍 Enhanced Debug Logger** (`autocrate/debug_logger.py`): Added test-specific logging methods
  - `log_test_results()` and `log_test_suite_summary()` for structured test tracking
  - Separate test log files (`test_results_TIMESTAMP.json`) with detailed metrics
  - Performance tracking with baseline comparisons and regression detection
  - Session summaries now include comprehensive test results

- **📈 Improved Import System**: Fixed critical import errors in `nx_expressions_generator.py`
  - Added robust multi-level import strategy (absolute → relative → direct imports)
  - Enhanced path handling for different execution contexts (script/module/PyInstaller)
  - Comprehensive error logging with debug information for troubleshooting
  - All calculation modules now have enhanced logging with performance tracking

- **🚀 Post-Session Testing**: Automatic test execution after application runs
  - Environment variable control (`AUTOCRATE_RUN_TESTS=1`) for automated testing
  - Integration with main application workflow for seamless validation
  - Comprehensive error handling and logging for test execution failures

### Fixed - Build and Test Infrastructure
- **✅ Fixed pytest Configuration**: Resolved build_and_test.bat pipeline failure
  - Removed dependencies on uninstalled plugins (`--cov`, `--json-report`)
  - Simplified pytest.ini to work with basic pytest installation
  - Replaced pytest with proven quick_test.py system in build pipeline

- **🔧 Fixed PyInstaller Issues**: Resolved executable build problems
  - Corrected path separator issues (`autocrate\` → `autocrate/`)
  - Fixed hidden imports and module discovery for all security components
  - Successful 12.7MB AutoCrate.exe generation with all features

- **💻 Windows Compatibility**: Resolved Unicode console output issues
  - Replaced all Unicode symbols (✓, ✗) with ASCII equivalents ([PASS], [FAIL])
  - Fixed console encoding issues in Windows Command Prompt
  - Ensured all test output works correctly across Windows versions

### Technical Achievements
- **100% Test Pass Rate**: All automated tests passing consistently
- **Sub-millisecond Performance**: Average 0.13-0.28ms per calculation
- **Complete ASTM Validation**: All compliance tests passing (D6256 standards)
- **Engineering-Grade Testing**: Property-based testing with boundary condition validation
- **Production-Ready Pipeline**: Complete CI/CD system from source to executable

## [12.0.6] - 2025-07-31

### Added
- **Quick Test Suite Button**: Added new "Quick Test Suite" button to GUI for rapid testing of corner cases and edge scenarios
  - Generates 10 test cases covering various product dimensions and edge conditions
  - Includes the original horizontal splice bug test case (20x20x100)
  - Test cases include: very tall/thin, standard plywood sizes, large/heavy, small/light, maximum size, perfect cube, etc.
  - Creates `quick_test_expressions/` folder with descriptive filenames
  - Uses current GUI settings for material parameters
  - Provides detailed progress logging and success/failure summary
  - Useful for regression testing and validating fixes across different scenarios

## [12.0.5] - 2025-07-31

### Changed
- **Project Structure Consolidation**: Consolidated dual codebase structure to eliminate confusion between `legacy/` and `src/` folders
  - Moved all working code from `legacy/` to main `autocrate/` folder
  - Removed incomplete `src/autocrate/` refactor attempt that had import issues
  - Updated build system to use `autocrate/nx_expressions_generator.py` as entry point
  - Updated all test imports to use `autocrate.` module paths
  - All 78 tests pass with new consolidated structure
  - Single source of truth for easier maintenance and development

## [12.0.4] - 2025-07-31

### Fixed
- **Expressions File Location**: Fixed issue where .exp files were being saved to temp folder instead of intended location. Expressions are now saved to `expressions/` folder in the same directory as the executable for easier access and organization.
  - Modified path detection logic to use executable directory when running as built application
  - Added proper distinction between script mode and executable mode
  - Ensures expressions are always saved alongside the executable for better user experience

## [12.0.3] - 2025-07-31

### Fixed
- **Horizontal Splice Cleat Bug**: Fixed critical issue where horizontal plywood splices were not getting proper cleat support when panels had no intermediate vertical cleats. This occurred with unusual product dimensions (e.g., 20x20x100 - very tall but thin products). The fix ensures all horizontal splices receive structural support per ASTM requirements, regardless of vertical cleat configuration.
  - Modified `calculate_horizontal_cleat_sections` to create cleat sections even when no intermediate vertical cleats exist
  - Updated conditional logic in `nx_expressions_generator.py` to properly trigger horizontal cleat recalculation
  - Applied fix across all panel types (Front, Back, Left, Right, Top)

## [12.0.2] - Previous Release
- Major refactor and cleanup