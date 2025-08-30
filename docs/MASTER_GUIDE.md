# AutoCrate V12 - Master Development Guide

## Project Overview

AutoCrate V12 is a professional ASTM D6251-17 compliant wooden crate design system with both desktop (Python/Tkinter) and web (Next.js/React) interfaces. It generates Siemens NX CAD expressions for automated 3D model creation.

## Architecture & Design

### System Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                      User Interfaces                        │
├──────────────────────┬──────────────────────────────────────┤
│   Desktop (Tkinter)  │      Web (Next.js/React)            │
├──────────────────────┴──────────────────────────────────────┤
│                   Core Calculation Engine                   │
│              (nx_expressions_generator.py)                  │
├──────────────────────────────────────────────────────────────┤
│                    Panel Logic Modules                      │
│  (front_panel, back_panel, left_panel, right_panel, etc.)  │
├──────────────────────────────────────────────────────────────┤
│                    Output Generation                        │
│         (NX Expressions, 3D Visualization, BOM)            │
└──────────────────────────────────────────────────────────────┘
```

### Technology Stack
- **Desktop**: Python 3.8+, Tkinter, NumPy, SciPy
- **Web**: Next.js 14, React 18, TypeScript, Three.js
- **API**: FastAPI/Flask for web backend
- **Testing**: pytest, Jest, property-based testing
- **CI/CD**: GitHub Actions, Vercel deployment
- **Documentation**: MkDocs, Sphinx

## Core Calculation Logic

### Critical Formulas (MUST MATCH ACROSS ALL IMPLEMENTATIONS)

```python
# Panel assembly thickness
panel_assembly_thickness = panel_thickness + cleat_thickness

# End panel dimensions (sandwiched between front/back)
end_panel_length = overall_length - (2 * panel_assembly_thickness)
end_panel_height = skid_height + floorboard_thickness + product_height + clearance_above - ground_clearance

# Front/Back panel dimensions (cover end panels)
front_panel_width = product_width + (2 * clearance) + (2 * panel_assembly_thickness)

# Vertical cleat material adjustments
if panel_width > 48:
    additional_cleats = ceil((panel_width - 48) / 48)
    material_needed = additional_cleats * cleat_width
    panel_width += material_needed
    overall_width += material_needed
```

### NX Coordinate System Mapping
- **X-axis**: Width (left-right)
- **Y-axis**: Length (front-back)  
- **Z-axis**: Height (up-down)
- **Origin**: Front-left-bottom corner of crate

## Development Standards

### Code Quality Standards

#### Python (PEP 8 Compliant)
```python
def calculate_panel_dimensions(
    product_width: float,
    product_height: float,
    clearance: float = 2.0,
    panel_thickness: float = 0.75
) -> Dict[str, float]:
    """
    Calculate panel dimensions based on product specifications.
    
    Args:
        product_width: Width of the product in inches
        product_height: Height of the product in inches
        clearance: Clearance around product in inches
        panel_thickness: Thickness of panel material in inches
    
    Returns:
        Dictionary containing calculated dimensions
    """
    # Implementation follows...
```

#### TypeScript/JavaScript
```typescript
interface CrateDimensions {
  width: number;
  height: number;
  length: number;
}

export function calculateCrateDimensions(
  productDimensions: CrateDimensions,
  clearance: number = 2.0
): CrateDimensions {
  // Implementation
}
```

### Security Standards (OWASP Top 10)

1. **Input Validation**
   - Validate all numeric inputs are within acceptable ranges
   - Sanitize file paths and prevent directory traversal
   - Use parameterized queries for any database operations

2. **Authentication & Authorization**
   - Implement secure session management for web version
   - Use environment variables for sensitive configuration
   - Never store credentials in code

3. **Data Protection**
   - Encrypt sensitive data in transit (HTTPS)
   - Secure storage of user preferences and configurations
   - Implement proper error handling without exposing internals

4. **Logging & Monitoring**
   - Log security events without exposing sensitive data
   - Implement rate limiting for API endpoints
   - Monitor for unusual patterns or activities

## Testing Strategy

### Test Categories

1. **Unit Tests** (`tests/unit/`)
   - Individual function validation
   - Edge case handling
   - Input validation

2. **Integration Tests** (`tests/integration/`)
   - Module interaction testing
   - API endpoint validation
   - Desktop/Web parity checks

3. **Performance Tests** (`tests/performance/`)
   - Calculation speed benchmarks
   - Memory usage profiling
   - Scalability testing

4. **Security Tests** (`tests/security/`)
   - Input fuzzing
   - Injection attack prevention
   - Access control validation

### Test Execution

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=autocrate --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest -m "not slow"  # Skip slow tests

# JavaScript/TypeScript tests
cd web && npm test
```

## Deployment Process

### Desktop Application

1. **Build Executable**
```bash
# Windows
pyinstaller --onefile --windowed --icon=assets/icon.ico main.py

# macOS
pyinstaller --onefile --windowed --icon=assets/icon.icns main.py

# Linux
pyinstaller --onefile main.py
```

2. **Code Signing** (Windows)
```bash
signtool sign /f certificate.pfx /p password /t http://timestamp.server AutoCrate.exe
```

3. **Installer Creation**
- Windows: NSIS or WiX Toolset
- macOS: create-dmg or Packages
- Linux: AppImage or Snap

### Web Application

1. **Vercel Deployment**
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd web
vercel --prod
```

2. **Environment Configuration**
```json
// vercel.json
{
  "env": {
    "NEXT_PUBLIC_API_URL": "@api_url",
    "DATABASE_URL": "@database_url"
  },
  "buildCommand": "npm run build",
  "outputDirectory": ".next"
}
```

3. **Custom Domain Setup**
- Add CNAME record pointing to vercel.app
- Configure SSL in Vercel dashboard
- Set up redirects and headers

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run tests
        run: pytest --cov=autocrate
      
  build:
    needs: test
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    steps:
      - uses: actions/checkout@v3
      - name: Build executable
        run: pyinstaller AutoCrate.spec
      
  deploy-web:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Vercel
        run: |
          cd web
          vercel --prod --token=${{ secrets.VERCEL_TOKEN }}
```

## Troubleshooting Guide

### Common Issues & Solutions

#### 1. Import Errors
**Problem**: `ModuleNotFoundError: No module named 'autocrate'`
**Solution**: 
```bash
# Add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/AutoCrate"
# Or install in development mode
pip install -e .
```

#### 2. NX Expression Generation Issues
**Problem**: Generated expressions don't match expected output
**Solution**:
- Verify calculation logic matches between desktop and web
- Check for floating-point precision issues
- Ensure consistent rounding (2 decimal places)

#### 3. 3D Viewer Coordinate Mismatch
**Problem**: 3D model doesn't match NX coordinates
**Solution**:
- Verify coordinate system mapping (Y→Z conversion for Three.js)
- Check panel positioning relative to assembly thickness
- Ensure camera orientation matches expected view

#### 4. Build Failures
**Problem**: PyInstaller build fails
**Solution**:
```bash
# Clean build artifacts
rm -rf build/ dist/ *.spec

# Rebuild with debug info
pyinstaller --debug=all --log-level=DEBUG main.py

# Check for missing modules
pyinstaller --hidden-import=module_name main.py
```

## Performance Optimization

### Desktop Application
- Use NumPy for vectorized calculations
- Implement caching for repeated calculations
- Lazy load heavy modules
- Profile with cProfile: `python -m cProfile -o profile.stats main.py`

### Web Application
- Implement code splitting with Next.js dynamic imports
- Use React.memo for expensive components
- Optimize 3D rendering with LOD (Level of Detail)
- Enable production builds: `npm run build`

### Database Optimization
- Index frequently queried fields
- Use connection pooling
- Implement query result caching
- Regular VACUUM and ANALYZE (PostgreSQL)

## API Documentation

### Core Endpoints

#### Generate NX Expressions
```http
POST /api/generate-expressions
Content-Type: application/json

{
  "productLength": 96,
  "productWidth": 48,
  "productHeight": 30,
  "productWeight": 1000,
  "clearance": 2,
  "panelThickness": 0.25,
  "cleatThickness": 1.5,
  "cleatWidth": 3.5
}

Response:
{
  "success": true,
  "expressions": "...",
  "calculations": {...},
  "bom": [...]
}
```

#### Health Check
```http
GET /api/health

Response:
{
  "status": "healthy",
  "version": "12.1.0",
  "timestamp": "2024-08-29T12:00:00Z"
}
```

## Development Workflow

### Feature Development
1. Create feature branch: `git checkout -b feature/name`
2. Implement with TDD approach
3. Ensure all tests pass: `pytest`
4. Update documentation
5. Create pull request with description
6. Code review and approval
7. Merge to develop branch
8. Deploy to staging environment

### Release Process
1. Merge develop to main
2. Tag release: `git tag -a v12.1.0 -m "Release v12.1.0"`
3. Build executables for all platforms
4. Create GitHub release with changelog
5. Deploy web version to production
6. Update documentation site

## Maintenance & Monitoring

### Logging Strategy
- Use structured logging (JSON format)
- Implement log rotation
- Centralize logs (ELK stack or similar)
- Set appropriate log levels per environment

### Monitoring Checklist
- [ ] Application uptime monitoring
- [ ] API response time tracking
- [ ] Error rate monitoring
- [ ] Resource usage alerts
- [ ] Security event tracking

### Backup Strategy
- Daily automated backups
- Version control for all code
- Configuration backup
- Documentation versioning
- Test data preservation

## Contact & Support

### Development Team
- **Project Lead**: Shivam Bhardwaj
- **Repository**: https://github.com/Shivam-Bhardwaj/AutoCrate-V12
- **Documentation**: https://autocrate-docs.github.io
- **Issues**: GitHub Issues page

### Resources
- [ASTM D6251-17 Standard](https://www.astm.org/d6251-17.html)
- [Siemens NX Documentation](https://docs.sw.siemens.com/nx)
- [Python Best Practices](https://docs.python-guide.org/)
- [React/Next.js Documentation](https://nextjs.org/docs)

---

*Last Updated: August 29, 2024*
*Version: 12.1.0*