# Testing Notes Template

## Quick Reference for Test Documentation

### Test Session Info
- **Date**: [YYYY-MM-DD]
- **Time**: [HH:MM]
- **Tester**: [Name]
- **Environment**: [Dev/Production/Streamlit]
- **AutoCrate Version**: [Version]

### Test Scenario
**What are you testing?**
- [ ] New feature
- [ ] Bug reproduction
- [ ] Edge case validation
- [ ] Performance testing
- [ ] UI/UX evaluation
- [ ] Other: ___________

**Specific focus**:
[Describe what you're specifically looking at]

### Test Setup
**Inputs/Configuration**:
- Product dimensions: L___ x W___ x H___
- Weight: ___ lbs
- Clearances: ___
- Material settings: ___
- Other parameters: ___

**Environment details**:
- OS: ___
- Python version: ___
- Special conditions: ___

### Execution Log
**Step-by-step record**:
1. [Action taken]
   - Input: ___
   - Expected: ___
   - Actual: ___

2. [Action taken]
   - Input: ___
   - Expected: ___
   - Actual: ___

[Continue as needed...]

### Screenshots/Evidence
**File references**:
- Screenshot 1: [filename/description]
- Screenshot 2: [filename/description]
- Log files: [location]
- Generated files: [location]

### Results Summary
**What worked**:
- ✅ [Success item 1]
- ✅ [Success item 2]

**What didn't work**:
- ❌ [Issue 1]
- ❌ [Issue 2]

**Unexpected behaviors**:
- ⚠️ [Observation 1]
- ⚠️ [Observation 2]

### Analysis & Insights
**Root causes**:
[Your analysis of why things happened]

**Patterns noticed**:
[Any patterns across tests]

**Edge cases discovered**:
[New edge cases to consider]

### Next Steps
**Immediate actions**:
- [ ] [Action item 1]
- [ ] [Action item 2]

**For further investigation**:
- [ ] [Research item 1]
- [ ] [Research item 2]

**Prompt preparation needed**:
- [ ] Need prompt for: [specific agent]
- [ ] Context to include: ___
- [ ] Expected deliverable: ___

### Notes for Prompt Refinement
**Raw observations**:
[Stream of consciousness notes]

**Questions to explore**:
- [Question 1]
- [Question 2]

**Context for AI agents**:
[What background info will agents need]

---

## Quick Prompt Starter Template

When ready to engage an agent, use this structure:

```
## Context
AutoCrate v12.0.2 testing on [environment]
[Relevant technical background from testing]

## Objective  
[What you want the agent to accomplish]

## Test Evidence
[Reference to your testing notes and screenshots]

## Specifications
[Specific requirements based on your findings]

## Expected Deliverable
[What you want as output]
```

## Agent Selection Guide

**For AutoCrate-specific development**:
→ Use `nx-expression-engineer` agent

**For general research/analysis**:
→ Use `general-purpose` agent  

**For prompt refinement**:
→ Use this prompt-engineering workflow

**For complex multi-step tasks**:
→ Start with prompt refinement, then hand off to appropriate specialist