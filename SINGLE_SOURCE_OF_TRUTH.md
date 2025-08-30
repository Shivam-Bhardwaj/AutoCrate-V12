# AutoCrate V12 - Single Source of Truth for NX Expressions

## The Problem
Previously, AutoCrate had two separate NX expression generators:
1. **Desktop**: Python-based (`autocrate/nx_expressions_generator.py`)
2. **Web**: TypeScript-based (`web/src/lib/autocrate-calculations-fixed.ts`)

This dual implementation caused:
- Different outputs for the same inputs (drift)
- Maintenance burden (fixing bugs in two places)
- Testing complexity (ensuring both match)
- User confusion (web vs desktop differences)

## The Solution: One Engine, Two Interfaces

### Architecture
```
┌─────────────────────────────────────────────┐
│     SINGLE SOURCE OF TRUTH                   │
│  autocrate/nx_expressions_generator.py       │
│     (Desktop Python Engine)                  │
└───────────────┬─────────────────────────────┘
                │
       ┌────────┴────────┐
       │                 │
┌──────▼──────┐  ┌───────▼───────┐
│   Desktop   │  │   Flask API   │
│   GUI App   │  │  api_server.py│
│  (main.py)  │  │  Port 5000    │
└─────────────┘  └───────┬───────┘
                         │
                  ┌──────▼──────┐
                  │   Web App   │
                  │  (Next.js)  │
                  │  Port 3000  │
                  └─────────────┘
```

### Key Changes

1. **Web App Now Uses Python API Only**
   - NO TypeScript NX generation
   - Must have API server running
   - Downloads require Python engine

2. **ResultsPanel.tsx Changes**
   ```typescript
   // OLD: TypeScript fallback
   if (!apiAvailable) {
     nxContent = generateNXExpression(results)  // ❌ REMOVED
   }
   
   // NEW: Python API required
   if (!apiAvailable) {
     alert('Python API server required')  // ✅ ENFORCED
     return
   }
   ```

3. **API Server is Mandatory for Web NX Generation**
   - Start with: `python api_server.py`
   - Or use: `AutoCrate.bat` option A
   - Web won't generate NX without it

## How to Use

### For Development

1. **Start API Server First**
   ```bash
   python api_server.py
   # Runs on http://localhost:5000
   ```

2. **Start Web Dev Server**
   ```bash
   cd web
   npm run dev
   # Runs on http://localhost:3000
   ```

3. **Generate NX Expressions**
   - Calculate crate dimensions
   - Click "Download NX File"
   - API must be running or download fails

### For Production

The API server must be deployed alongside the web app:
- Deploy API to a cloud service (Heroku, AWS Lambda, etc.)
- Update `NEXT_PUBLIC_API_URL` environment variable
- Web app will use production API endpoint

## Testing Consistency

### Verify Desktop Generation
```bash
python test_nx_comparison.py
```
Output:
```
Testing: Standard 96x48x30 @ 1000lbs
  [SUCCESS] Desktop generated: 31082 bytes
  MD5: 926bc1a17fbd6ddd8d753c13ea32a126
```

### Verify Web Uses Same Engine
1. Start API server
2. Generate from web interface
3. Compare MD5 hashes - must match exactly

## Benefits

1. **Zero Drift**: Impossible for outputs to differ
2. **Single Maintenance**: Fix bugs once, deploy everywhere
3. **ASTM Compliance**: One validated calculation engine
4. **Simpler Testing**: Test one engine, trust all outputs
5. **Future Proof**: Add features once, available everywhere

## Important Files

| File | Purpose | Status |
|------|---------|--------|
| `autocrate/nx_expressions_generator.py` | The ONLY NX generator | ✅ Source of truth |
| `api_server.py` | Exposes desktop engine via HTTP | ✅ Required for web |
| `web/src/components/ResultsPanel.tsx` | Downloads NX via API only | ✅ No fallback |
| `web/src/lib/autocrate-calculations-fixed.ts` | TypeScript calculations | ⚠️ NOT used for NX |
| `web/src/services/python-api.ts` | API client service | ✅ Handles all NX |

## Troubleshooting

### "Python API server is not running"
- Solution: Start API server with `python api_server.py`
- The web app CANNOT generate NX without it

### Different outputs between desktop and web
- This should be IMPOSSIBLE now
- If it happens, web is not using the API
- Check browser console for API connection

### API connection failed
- Check API is running: `curl http://localhost:5000/health`
- Check CORS settings in `api_server.py`
- Ensure both servers on same machine or update URLs

## Migration from Dual Engines

### What Changed
- ❌ Removed: TypeScript NX generation (`generateNXExpression`)
- ❌ Removed: Fallback to client-side generation
- ✅ Added: Mandatory Python API for NX
- ✅ Added: Clear user messaging about API requirement

### Why This Matters
- **Engineering Accuracy**: One validated calculation engine
- **Regulatory Compliance**: Single ASTM-compliant implementation
- **User Trust**: Identical outputs regardless of interface
- **Developer Sanity**: Maintain one codebase, not two

## Future Enhancements

1. **Embedded Python**: Use Pyodide to run Python in browser
2. **Serverless**: Deploy as AWS Lambda or Vercel Function
3. **Caching**: Cache generated expressions by parameter hash
4. **Batch API**: Generate multiple configurations at once

---
*Version: 1.1.0*
*Last Updated: August 27, 2024*

**Remember: There is only ONE source of truth for NX expressions - the Python desktop engine.**