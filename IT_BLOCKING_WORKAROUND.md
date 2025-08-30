# AutoCrate V12 - IT Blocking Workaround

## The Issue
The IT department or security settings are blocking the Python API server connection between the web app and the desktop calculation engine. This prevents the web app from using the single source of truth for NX expression generation.

## Current Status

### What's Happening
1. **Python API Server**: Cannot connect on localhost:5000 (blocked)
2. **Web App**: Reverted to TypeScript NX generation (not ideal - creates drift)
3. **Desktop App**: Still works perfectly with Python engine

### The Problem
- Web and desktop generate DIFFERENT NX expressions
- This violates the "single source of truth" principle
- Maintenance burden of two calculation engines
- Risk of incompatible outputs

## Solutions

### Option 1: Use Desktop Application Only (Recommended)
For guaranteed correct NX expressions:
1. Use the desktop application: `AutoCrate.exe`
2. This always uses the correct Python calculation engine
3. NX expressions will be 100% accurate

### Option 2: Manual Bridge (If Web Access Needed)
If you must use the web interface:

1. **For Calculations**: Web app works fine (TypeScript calculations are close enough for viewing)

2. **For NX Generation**: Use the desktop app or:
   ```bash
   # Generate NX manually using Python
   python generate_nx_offline.py "{\"productLength\": 96, \"productWidth\": 48, \"productHeight\": 30, \"productWeight\": 1000}"
   ```

### Option 3: Request IT Exception
Ask IT to allow:
- Local connections to `localhost:5000`
- Or whitelist the `api_server.py` process
- Or allow Flask framework connections

## Technical Details

### Why It's Blocked
Common reasons for blocking:
1. **Security Policy**: Blocks all local server connections
2. **Firewall Rules**: Prevents inter-process communication
3. **Antivirus**: Flags Python servers as suspicious
4. **Corporate Proxy**: Interferes with localhost connections

### What Was Changed
Due to the blocking, the web app was modified:

#### Calculator.tsx
```typescript
// OLD: Try Python API first
const apiAvailable = await PythonAPI.checkHealth()
if (apiAvailable) { /* use API */ }

// NEW: Offline mode only
// Use TypeScript calculator for offline operation
const calculator = new AutoCrateCalculator()
```

#### ResultsPanel.tsx
```typescript
// OLD: Python API required for NX
if (!apiAvailable) {
  alert('Python API server required')
  return
}

// NEW: TypeScript generation (creates drift!)
const nxContent = generateNXExpression(results)
```

## Implications

### With IT Blocking (Current State)
- ❌ Two different NX generators (Python vs TypeScript)
- ❌ Potential for different outputs
- ❌ Double maintenance burden
- ⚠️ Risk of incompatible CAD files

### Without IT Blocking (Intended Design)
- ✅ Single source of truth (Python only)
- ✅ Identical outputs guaranteed
- ✅ Single maintenance point
- ✅ Compatible CAD files always

## Recommendations

1. **Short Term**: Use desktop app for NX generation
2. **Medium Term**: Get IT exception for localhost:5000
3. **Long Term**: Deploy API to approved cloud service

## Files Affected

| File | Status | Impact |
|------|--------|--------|
| `api_server.py` | Blocked | Cannot provide Python calculations |
| `web/src/components/Calculator.tsx` | Modified | Using TypeScript fallback |
| `web/src/components/ResultsPanel.tsx` | Modified | Using TypeScript NX generation |
| `web/src/services/python-api.ts` | Unused | API calls fail |

## Testing for IT Blocking

Check if you're affected:
```bash
# Test 1: Can you reach the API?
curl http://localhost:5000/health

# Test 2: Can Python create servers?
python -m http.server 8000

# Test 3: Check firewall rules
netstat -an | findstr 5000
```

If any fail, IT is blocking local servers.

## Contact IT

Request the following exceptions:
```
Application: AutoCrate V12
Process: python.exe (when running api_server.py)
Port: 5000 (TCP, localhost only)
Reason: Engineering calculation server for CAD integration
Risk: Low (localhost only, no external access)
```

---
*Last Updated: August 27, 2024*
*Version: 1.1.0*

**Note: Until IT blocking is resolved, use the desktop application for accurate NX expression generation.**