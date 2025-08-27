# AutoCrate V12 Web Version

Professional ASTM-compliant wooden crate design system with 3D visualization, BOM generation, and comprehensive reporting.

## Features

- **3D Visualization**: Interactive Three.js viewer with exploded views
- **Real-time Calculations**: Instant crate design based on product dimensions
- **BOM Generator**: Complete bill of materials with cost estimation
- **Report Generation**: Professional PDF reports and compliance certificates
- **ASTM Compliance**: Full compliance with ASTM D6251-17 standards
- **Material Optimization**: Cutting pattern optimization to minimize waste
- **Multi-platform**: Works on desktop, tablet, and mobile devices

## Tech Stack

- **Frontend**: Next.js 14, React, TypeScript, Material-UI, Three.js
- **Backend**: FastAPI (Python), Pydantic
- **3D**: Three.js, React Three Fiber
- **State**: Zustand
- **Deployment**: Vercel

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.9+
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Shivam-Bhardwaj/AutoCrate-V12.git
cd AutoCrate-V12
```

2. Install dependencies:
```bash
# Install all dependencies
npm run install:all

# Or manually:
cd web && npm install
cd ../api && pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# web/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000/api

# api/.env
SECRET_KEY=your-secret-key
ENVIRONMENT=development
```

### Development

Run both frontend and backend:
```bash
npm run dev
```

Or run separately:
```bash
# Terminal 1 - API
cd api && uvicorn main:app --reload --port 8000

# Terminal 2 - Web
cd web && npm run dev
```

Access the application:
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/api/docs

### Building for Production

```bash
# Build Next.js app
cd web && npm run build

# Test production build
npm run start
```

## API Endpoints

### Core Endpoints

- `POST /api/calculate` - Calculate crate design
- `POST /api/validate` - Validate input parameters
- `POST /api/3d-geometry` - Get 3D geometry data
- `GET /api/materials` - Get available materials
- `GET /api/standards` - Get ASTM standards info

### Export Endpoints

- `GET /api/export/nx_expression/{id}` - Download NX expression file
- `POST /api/export/bom` - Generate BOM (Excel/CSV)
- `GET /api/export/report/{id}` - Generate PDF report

## Deployment

### Deploy to Vercel

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy:
```bash
vercel
```

3. Follow the prompts to configure your deployment

### Environment Variables for Production

Set these in Vercel dashboard:
- `PYTHON_VERSION`: 3.9
- `SECRET_KEY`: Your secure secret key
- `DATABASE_URL`: (if using database)

## Project Structure

```
AutoCrate-V12/
├── web/                    # Next.js frontend
│   ├── src/
│   │   ├── app/           # App router pages
│   │   ├── components/    # React components
│   │   ├── lib/          # Utilities and API client
│   │   └── store/        # Zustand store
│   └── public/           # Static assets
├── api/                   # FastAPI backend
│   ├── main.py          # API entry point
│   └── requirements.txt  # Python dependencies
├── autocrate/            # Core calculation modules
│   ├── front_panel_logic.py
│   ├── back_panel_logic.py
│   └── ...
└── vercel.json          # Vercel configuration
```

## Features in Detail

### 3D Visualization
- Real-time rotation and zoom
- Exploded view with adjustable distance
- Panel highlighting on hover
- Dimension annotations
- Multiple view angles (front, side, top, 3D)

### BOM Generator
- Complete materials list
- Cost calculations with markup
- Optimization suggestions
- Export to Excel, CSV, PDF
- Supplier integration ready

### Report Generation
- Engineering reports with calculations
- Customer quotes with pricing
- Assembly instructions
- ASTM compliance certificates
- QR codes for digital access

## Testing

```bash
# Run all tests
npm test

# API tests
cd api && pytest

# Frontend tests
cd web && npm test
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Proprietary - All rights reserved

## Support

For support, email support@autocrate.com or visit our [documentation](https://docs.autocrate.com)

## Acknowledgments

- ASTM International for D6251-17 standards
- Three.js community for 3D visualization
- Vercel for hosting platform