#!/usr/bin/env python3
"""
Development environment setup script for AutoCrate.

This script sets up the development environment, installs dependencies,
and configures development tools.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


class DevSetup:
    """Handles development environment setup."""
    
    def __init__(self, project_root: Path):
        """
        Initialize development setup.
        
        Args:
            project_root: Path to project root directory
        """
        self.project_root = project_root
        self.requirements_file = project_root / "requirements.txt"
        self.dev_requirements = [
            "pytest>=7.0",
            "pytest-cov>=4.0", 
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
            "pre-commit>=3.0",
            "pyinstaller>=6.0",
        ]
    
    def check_python_version(self):
        """Check if Python version is compatible."""
        print("Checking Python version...")
        
        version = sys.version_info
        print(f"Python version: {version.major}.{version.minor}.{version.micro}")
        
        if version.major < 3 or (version.major == 3 and version.minor < 9):
            print("ERROR: Python 3.9 or higher is required")
            return False
        
        print("Python version is compatible.")
        return True
    
    def create_virtual_environment(self, venv_name="venv"):
        """Create virtual environment."""
        print(f"Creating virtual environment: {venv_name}")
        
        venv_path = self.project_root / venv_name
        
        if venv_path.exists():
            print("Virtual environment already exists.")
            return True
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "venv", str(venv_path)
            ], check=True)
            
            print(f"Virtual environment created at: {venv_path}")
            print("To activate it, run:")
            
            if os.name == 'nt':  # Windows
                print(f"  {venv_path}\\Scripts\\activate")
            else:  # Unix-like
                print(f"  source {venv_path}/bin/activate")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Failed to create virtual environment: {e}")
            return False
    
    def install_dependencies(self):
        """Install project dependencies."""
        print("Installing dependencies...")
        
        # Install development dependencies
        try:
            cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "pip"]
            subprocess.run(cmd, check=True)
            
            cmd = [sys.executable, "-m", "pip", "install"] + self.dev_requirements
            subprocess.run(cmd, check=True)
            
            print("Development dependencies installed successfully.")
            
        except subprocess.CalledProcessError as e:
            print(f"Failed to install dependencies: {e}")
            return False
        
        # Install project in development mode
        try:
            cmd = [sys.executable, "-m", "pip", "install", "-e", "."]
            subprocess.run(cmd, check=True, cwd=self.project_root)
            print("Project installed in development mode.")
            
        except subprocess.CalledProcessError as e:
            print(f"Failed to install project in development mode: {e}")
            print("This is expected if pyproject.toml is not fully configured yet.")
        
        return True
    
    def setup_pre_commit(self):
        """Set up pre-commit hooks."""
        print("Setting up pre-commit hooks...")
        
        # Create .pre-commit-config.yaml if it doesn't exist
        pre_commit_config = self.project_root / ".pre-commit-config.yaml"
        
        if not pre_commit_config.exists():
            config_content = """repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-merge-conflict
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203,W503]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        args: [--ignore-missing-imports]
"""
            
            with open(pre_commit_config, 'w') as f:
                f.write(config_content)
            
            print(f"Created pre-commit configuration: {pre_commit_config}")
        
        # Install pre-commit hooks
        try:
            cmd = [sys.executable, "-m", "pre_commit", "install"]
            subprocess.run(cmd, check=True, cwd=self.project_root)
            print("Pre-commit hooks installed successfully.")
            
        except subprocess.CalledProcessError as e:
            print(f"Failed to install pre-commit hooks: {e}")
            return False
        
        return True
    
    def create_dev_scripts(self):
        """Create useful development scripts."""
        print("Creating development scripts...")
        
        scripts_dir = self.project_root / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        
        # Create test script
        test_script = scripts_dir / "test.py"
        if not test_script.exists():
            test_content = '''#!/usr/bin/env python3
"""Run tests with coverage reporting."""

import subprocess
import sys
from pathlib import Path

def main():
    """Run pytest with coverage."""
    project_root = Path(__file__).parent.parent
    
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "--cov=src/autocrate",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--verbose"
    ]
    
    return subprocess.call(cmd, cwd=project_root)

if __name__ == "__main__":
    sys.exit(main())
'''
            with open(test_script, 'w') as f:
                f.write(test_content)
            print(f"Created test script: {test_script}")
        
        # Create lint script
        lint_script = scripts_dir / "lint.py"
        if not lint_script.exists():
            lint_content = '''#!/usr/bin/env python3
"""Run code linting and formatting."""

import subprocess
import sys
from pathlib import Path

def main():
    """Run linting tools."""
    project_root = Path(__file__).parent.parent
    
    print("Running Black (code formatting)...")
    result1 = subprocess.call([
        sys.executable, "-m", "black", "src/", "tests/", "scripts/"
    ], cwd=project_root)
    
    print("\\nRunning Flake8 (linting)...")
    result2 = subprocess.call([
        sys.executable, "-m", "flake8", "src/", "tests/", "scripts/"
    ], cwd=project_root)
    
    print("\\nRunning MyPy (type checking)...")
    result3 = subprocess.call([
        sys.executable, "-m", "mypy", "src/autocrate/"
    ], cwd=project_root)
    
    return max(result1, result2, result3)

if __name__ == "__main__":
    sys.exit(main())
'''
            with open(lint_script, 'w') as f:
                f.write(lint_content)
            print(f"Created lint script: {lint_script}")
        
        return True
    
    def setup_vscode_config(self):
        """Set up VS Code configuration."""
        print("Setting up VS Code configuration...")
        
        vscode_dir = self.project_root / ".vscode"
        vscode_dir.mkdir(exist_ok=True)
        
        # Settings
        settings_file = vscode_dir / "settings.json"
        if not settings_file.exists():
            settings = {
                "python.defaultInterpreterPath": "./venv/Scripts/python.exe",
                "python.linting.enabled": True,
                "python.linting.flake8Enabled": True,
                "python.linting.mypyEnabled": True,
                "python.formatting.provider": "black",
                "python.testing.pytestEnabled": True,
                "python.testing.pytestArgs": ["tests/"],
                "files.exclude": {
                    "**/__pycache__": True,
                    "**/*.pyc": True,
                    ".pytest_cache": True,
                    ".coverage": True,
                    "htmlcov": True,
                    "build": True,
                    "dist": True,
                }
            }
            
            import json
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            print(f"Created VS Code settings: {settings_file}")
        
        # Launch configuration
        launch_file = vscode_dir / "launch.json"
        if not launch_file.exists():
            launch_config = {
                "version": "0.2.0",
                "configurations": [
                    {
                        "name": "Python: AutoCrate",
                        "type": "python",
                        "request": "launch",
                        "program": "${workspaceFolder}/src/autocrate/gui/main_app.py",
                        "console": "integratedTerminal",
                        "cwd": "${workspaceFolder}",
                        "env": {
                            "PYTHONPATH": "${workspaceFolder}/src"
                        }
                    },
                    {
                        "name": "Python: Current File",
                        "type": "python",
                        "request": "launch",
                        "program": "${file}",
                        "console": "integratedTerminal",
                        "cwd": "${workspaceFolder}"
                    }
                ]
            }
            
            import json
            with open(launch_file, 'w') as f:
                json.dump(launch_config, f, indent=2)
            
            print(f"Created VS Code launch config: {launch_file}")
        
        return True
    
    def create_requirements_txt(self):
        """Create requirements.txt file."""
        print("Creating requirements.txt...")
        
        if not self.requirements_file.exists():
            # Basic runtime requirements (AutoCrate has minimal dependencies)
            requirements = [
                "# AutoCrate Runtime Requirements",
                "# (AutoCrate uses mostly standard library)",
                "",
                "# Development Dependencies",
                "pytest>=7.0",
                "pytest-cov>=4.0", 
                "black>=23.0",
                "flake8>=6.0",
                "mypy>=1.0",
                "pre-commit>=3.0",
                "",
                "# Build Dependencies", 
                "pyinstaller>=6.0",
            ]
            
            with open(self.requirements_file, 'w') as f:
                f.write('\n'.join(requirements))
            
            print(f"Created requirements file: {self.requirements_file}")
        
        return True
    
    def print_next_steps(self):
        """Print next steps for the developer."""
        print("\n" + "=" * 60)
        print("Development Environment Setup Complete!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Activate virtual environment (if created)")
        print("2. Run tests: python scripts/test.py")
        print("3. Run linting: python scripts/lint.py")
        print("4. Build application: python scripts/build.py")
        print()
        print("Development commands:")
        print("- Run app: python src/autocrate/gui/main_app.py")
        print("- Run tests: pytest")
        print("- Format code: black src/ tests/ scripts/")
        print("- Check linting: flake8 src/ tests/ scripts/")
        print("- Type checking: mypy src/autocrate/")
        print()
        print("Happy coding!")
    
    def full_setup(self, create_venv=True, venv_name="venv"):
        """Run full development environment setup."""
        print("Setting up AutoCrate development environment...")
        
        if not self.check_python_version():
            return False
        
        if create_venv:
            if not self.create_virtual_environment(venv_name):
                return False
        
        if not self.install_dependencies():
            return False
        
        if not self.create_requirements_txt():
            return False
        
        if not self.setup_pre_commit():
            return False
        
        if not self.create_dev_scripts():
            return False
        
        if not self.setup_vscode_config():
            return False
        
        self.print_next_steps()
        return True


def main():
    """Main entry point for development setup."""
    parser = argparse.ArgumentParser(description="Set up AutoCrate development environment")
    parser.add_argument('--no-venv', action='store_true',
                        help='Skip virtual environment creation')
    parser.add_argument('--venv-name', default='venv',
                        help='Name for virtual environment (default: venv)')
    
    args = parser.parse_args()
    
    project_root = Path(__file__).parent.parent
    dev_setup = DevSetup(project_root)
    
    success = dev_setup.full_setup(
        create_venv=not args.no_venv,
        venv_name=args.venv_name
    )
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())