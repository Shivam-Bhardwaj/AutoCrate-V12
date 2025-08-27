// API configuration
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api';

export interface Product {
  length: number;
  width: number;
  height: number;
  weight: number;
}

export interface Materials {
  panel_thickness: number;
  material_type: string;
  lumber_sizes?: string[];
}

export interface CrateRequest {
  product: Product;
  materials: Materials;
  clearance: number;
  include_top: boolean;
}

export interface CrateResponse {
  crate_dimensions: any;
  panels: any;
  materials: any;
  cost_estimate: any;
  bom: any;
  validation: any;
}

class ApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_URL;
  }

  async calculateCrate(request: CrateRequest): Promise<CrateResponse> {
    const response = await fetch(`${this.baseUrl}/calculate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error('Failed to calculate crate');
    }

    return response.json();
  }

  async exportNXExpression(request: CrateRequest): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/export/nx_expression`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error('Failed to export NX expression');
    }

    return response.blob();
  }

  async exportBOM(request: CrateRequest): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/export/bom`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error('Failed to export BOM');
    }

    return response.blob();
  }

  async exportReport(request: CrateRequest): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/export/report`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error('Failed to export report');
    }

    return response.blob();
  }

  async validate(request: CrateRequest): Promise<any> {
    const response = await fetch(`${this.baseUrl}/validate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error('Failed to validate');
    }

    return response.json();
  }
}

export default new ApiService();