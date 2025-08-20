# AutoCrate v12.1.4

**AI-Enhanced Automated Crate Design System**

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![ASTM](https://img.shields.io/badge/ASTM-compliant-orange.svg)](https://www.astm.org/)
[![NX](https://img.shields.io/badge/Siemens-NX-blue.svg)](https://www.siemens.com/nx)

AutoCrate is a sophisticated Python application that automates the generation of manufacturing data for shipping crates. It features an intuitive GUI and produces Siemens NX expressions files (.exp) that drive parametric CAD models for automated 3D model and drawing creation.

## 🚀 Key Features

- **Automated Crate Design**: Complete structural calculations for skids, panels, cleats, and klimps
- **ASTM Compliance**: Built-in engineering standards and safety factors
- **Material Optimization**: Intelligent plywood layout algorithms minimize waste
- **Advanced Klimp System**: 30 configurable L-brackets with 6DOF quaternion orientation
- **NX Integration**: Seamless parametric CAD model generation
- **Real-time Cost Analysis**: Material and labor cost estimation
- **AI-Enhanced Development**: Advanced testing, logging, and optimization systems

## 📋 System Requirements

- **OS**: Windows 10/11 (64-bit)
- **Python**: 3.8+ (recommended: 3.11)
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 500MB free disk space
- **CAD**: Siemens NX (for model generation)

## 🔧 Quick Start

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-org/autocrate.git
cd autocrate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Verify installation
quick_test.bat

# 4. Build executable (optional)
build.bat
```

### Basic Usage

1. **Launch**: Run `AutoCrate.exe` or `python autocrate/nx_expressions_generator.py`
2. **Input**: Enter product dimensions, weight, and materials
3. **Generate**: Create NX expressions file
4. **Import**: Load expressions into Siemens NX parametric model

## 🏗️ Architecture

```
AutoCrate/
├── autocrate/                    # Core application modules
│   ├── nx_expressions_generator.py         # Main application & GUI
│   ├── klimp_placement_logic_all_sides.py  # Klimp positioning system
│   ├── klimp_quaternion_integration.py     # 6DOF orientation system
│   ├── *_panel_logic.py                    # Panel calculation modules
│   ├── plywood_layout_generator.py         # Material optimization
│   └── skid_logic.py                       # Load-based skid sizing
├── tests/                        # Comprehensive test suite
├── scripts/                      # Build and utility scripts
├── expressions/                  # Generated NX expression files
├── logs/                         # Application and debug logs
└── docs/                         # Complete documentation
```

## 🔬 Klimp System

AutoCrate features an advanced klimp (L-bracket) system for structural reinforcement:

- **30 Positions**: KL_1-10 (top), KL_11-20 (left), KL_21-30 (right)
- **6DOF Control**: Quaternion-based orientation with direction vectors
- **Smart Placement**: Automatic optimization avoiding cleat interference
- **NX Integration**: Full parametric control with suppress flags

### Example NX Variables
```
[Inch]KL_1_X = -42.250          // Position coordinates
[Inch]KL_1_Y = 0.000
[Inch]KL_1_Z = 40.500

KL_1_Q_W = 1.000000             // Quaternion orientation
KL_1_Q_X = 0.000000
KL_1_Q_Y = 0.000000
KL_1_Q_Z = 0.000000

KL_1_X_DIR_X = 1.000000         // Direction vectors
KL_1_X_DIR_Y = 0.000000         // for 6DOF control
KL_1_X_DIR_Z = 0.000000

KL_1_SUPPRESS = 0               // 0=show, 1=hide
```

## 🧪 Testing

AutoCrate includes comprehensive testing infrastructure:

```bash
# Run all tests
python -m pytest tests/ -v

# Quick validation
quick_test.bat

# Specific module tests
python -m pytest tests/test_klimp_system.py -v

# Property-based testing
python -m pytest tests/test_property_based.py -v
```

## 📚 Documentation

- **Complete Guide**: Open `docs/index.html` in your browser for full documentation
- **API Reference**: Detailed function documentation with examples
- **NX Integration**: Step-by-step Siemens NX setup instructions
- **Troubleshooting**: Common issues and solutions

## 🔧 Development

### Key Development Principles
- **ASTM Compliance**: All calculations follow industry standards
- **NX Compatibility**: Variables designed for seamless CAD integration
- **Modular Design**: Each component is independently testable
- **Performance Optimization**: Efficient algorithms for complex calculations

### Adding Features
1. Create feature branch
2. Implement with comprehensive tests
3. Validate with `quick_test.bat`
4. Update documentation
5. Submit pull request

## 🐛 Troubleshooting

### Common Issues

**Application won't start:**
```bash
python --version                    # Check Python version
pip install -r requirements.txt    # Reinstall dependencies
```

**Expression generation fails:**
- Check input parameter ranges
- Review logs in `logs/` directory
- Run `quick_test.bat` for system validation

**NX import issues:**
- Ensure expressions are ASCII-only
- Verify coordinate system settings
- Check suppress flag values

## 📊 Performance

- **Design Time**: Reduced from hours to minutes
- **Material Waste**: Optimized plywood layouts save 15-25%
- **Accuracy**: ASTM-compliant calculations ensure structural integrity
- **Scalability**: Handles crates from 12"×12"×12" to 130"×130"×130"

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Add comprehensive tests
4. Update documentation
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with advanced AI collaboration techniques
- ASTM standards compliance
- Modern software architecture principles
- Comprehensive testing methodologies

## 📞 Support

For support and questions:

1. Check the `logs/` directory for detailed error information
2. Run `quick_test.bat` to validate system state
3. Review the complete documentation at `docs/index.html`
4. Create an issue on GitHub with reproduction steps

---

**AutoCrate v12.1.4** - Transforming crate design through automation, AI enhancement, and engineering excellence.

*Built with Python, powered by algorithms, enhanced by AI.*

