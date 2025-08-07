# AutoCrate Coding Standards

## Overview
This document establishes coding standards for the AutoCrate project to ensure consistency, maintainability, and cross-platform compatibility.

## Character Set Requirements

### ASCII-Only Policy
**MANDATORY**: All code, comments, and text output must use ASCII characters only (0-127).

#### Prohibited Characters
- **Emoji**: ✓ ✗ ❌ ⚠️ 🚀 📝 💡 🔧 etc.
- **Unicode symbols**: → ← ↑ ↓ • ◦ ★ ☆ etc.
- **Special punctuation**: " " ' ' – — … etc.

#### Approved Replacements
Use these ASCII alternatives:

| Prohibited | ASCII Alternative | Usage |
|------------|------------------|-------|
| ✓ ✅ | `[PASS]`, `SUCCESS`, `OK` | Success indicators |
| ❌ ✗ | `[FAIL]`, `ERROR`, `FAILED` | Failure indicators |
| ⚠️ | `[WARNING]`, `WARN`, `CAUTION` | Warning indicators |
| 📝 | `[INFO]`, `NOTE`, `LOG` | Information markers |
| 🔧 | `[CONFIG]`, `SETUP`, `TOOL` | Configuration/tools |
| → | `->`, `-->` | Arrows |
| • | `-`, `*` | Bullet points |
| " " | `"` | Quote marks |

### Rationale
1. **Cross-platform compatibility**: ASCII ensures display on all systems
2. **Terminal/console support**: Many systems don't render Unicode properly
3. **Log file integrity**: ASCII prevents encoding issues in logs
4. **Screen reader accessibility**: ASCII is universally supported
5. **Code maintainability**: Reduces character encoding complexities

## Implementation Requirements

### Code Reviews
All code changes must be reviewed for ASCII compliance before merging.

### Automated Validation
Implement pre-commit hooks to detect non-ASCII characters:

```bash
# Example validation command
grep -P "[^\x00-\x7F]" *.py
```

### Documentation Standards
- Use plain ASCII in all documentation
- Prefer clear descriptive text over symbolic representations
- Example: Use "PASSED" instead of "✓"

### User Interface Guidelines
- Status messages must use ASCII text
- Error messages must use ASCII characters
- Configuration files must be ASCII-encoded

## Exception Handling
No exceptions are permitted for this policy. If special characters are absolutely required:
1. Document the specific technical requirement
2. Get approval from project maintainers
3. Implement fallback ASCII alternatives
4. Add comments explaining the necessity

## Validation Tools

### Manual Check Command
```bash
# Search for non-ASCII characters in Python files
find . -name "*.py" -exec grep -P "[^\x00-\x7F]" {} +
```

### Pre-commit Hook Example
```python
#!/usr/bin/env python3
"""Pre-commit hook to prevent non-ASCII characters."""
import sys
import re

def check_ascii_only(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if not all(ord(char) < 128 for char in line):
                non_ascii = [char for char in line if ord(char) >= 128]
                print(f"Non-ASCII characters in {filename}:{line_num}: {non_ascii}")
                return False
    return True
```

## Enforcement
- **Pre-commit**: Automated checks prevent non-ASCII commits
- **CI/CD**: Build pipeline validates ASCII compliance
- **Code review**: Manual verification required
- **Documentation**: Standards must be followed in all docs

## Legacy Code Migration
Existing non-ASCII characters have been systematically replaced with ASCII equivalents. Future modifications must maintain ASCII compliance.

## Professional Language Standards

### Professional Terminology Requirements
**MANDATORY**: All code, comments, and documentation must use professional engineering terminology.

#### Prohibited Language
- **Slang/Informal**: "bug", "hack", "kludge", "wonky", "weird", "crazy"
- **Casual intensifiers**: "very", "really", "super", "totally", "pretty"
- **Informal expressions**: "clearly better", "obviously", "just", "simply"
- **Placeholder terms**: "foo", "bar", "baz", "stuff", "things", "thingy"
- **Casual speech**: "gonna", "kinda", "sorta", "yeah", "nope"

#### Professional Replacements

| Informal | Professional Alternative |
|----------|-------------------------|
| "bug" | "defect", "issue", "anomaly" |
| "hack" / "kludge" | "temporary solution", "workaround" |
| "very large" | "maximum capacity", "high-volume" |
| "clearly better" | "optimal", "preferred", "more efficient" |
| "weird behavior" | "unexpected behavior", "anomalous response" |
| "wonky" | "unstable", "inconsistent" |
| "stuff" / "things" | "components", "elements", "parameters" |

### Documentation Standards
- Use precise technical terminology
- Avoid subjective adjectives without quantification
- Replace casual language with engineering specifications
- Use formal sentence structure in comments

### Code Comment Guidelines
```python
# Professional: "Optimal configuration requires fewer material sheets"
# Unprofessional: "This way is clearly better"

# Professional: "Validation test for horizontal splice calculations"
# Unprofessional: "Bug test for splice stuff"
```

### Error Messages and Logs
- Use formal, descriptive language
- Specify exact conditions and expected behavior
- Avoid casual expressions in user-facing messages

---

**Effective Date**: 2025-08-07  
**Version**: 1.1  
**Applies to**: All AutoCrate code, documentation, and configuration files