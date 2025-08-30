/**
 * Python API Client Service
 * Communicates with the Python Flask server to use the exact desktop calculation engine
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

export interface CrateParameters {
  productLength: number;
  productWidth: number;
  productHeight: number;
  productWeight: number;
  quantity: number;
  panelThickness: number;
  cleatThickness: number;
  cleatMemberWidth: number;
  clearance: number;
  clearanceAbove: number;
  groundClearance: number;
  floorboardThickness: number;
  skidHeight: number;
  safetyFactor: number;
  allow3x4Skids?: boolean;
}

export interface CalculationResult {
  success: boolean;
  calculations?: {
    overallDimensions: {
      width: number;
      length: number;
      height: number;
    };
    panelDimensions: {
      front: {
        width: number;
        height: number;
      };
      back: {
        width: number;
        height: number;
      };
      end: {
        length: number;
        height: number;
      };
      top: {
        length: number;
        width: number;
      };
    };
    weights: {
      productWeight: number;
      quantity: number;
      totalWeight: number;
      designLoad: number;
    };
    materials: {
      panelThickness: number;
      cleatThickness: number;
      panelAssemblyThickness: number;
    };
  };
  error?: string;
  engine: string;
  timestamp: string;
}

export interface NXGenerationResult {
  success: boolean;
  expressions?: string;
  filename?: string;
  error?: string;
  engine: string;
  timestamp: string;
}

/**
 * Check if the Python API server is running
 */
export async function checkAPIHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    const data = await response.json();
    return data.status === 'healthy';
  } catch (error) {
    console.error('Python API not available:', error);
    return false;
  }
}

/**
 * Calculate crate dimensions using the Python engine
 */
export async function calculateCrateDimensions(
  params: CrateParameters
): Promise<CalculationResult> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/calculate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    });

    const data = await response.json();
    return data;
  } catch (error) {
    return {
      success: false,
      error: `Failed to connect to Python API: ${error}`,
      engine: 'error',
      timestamp: new Date().toISOString(),
    };
  }
}

/**
 * Generate NX expressions using the Python engine
 */
export async function generateNXExpressions(
  params: CrateParameters
): Promise<NXGenerationResult> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/generate-nx`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    });

    const data = await response.json();
    return data;
  } catch (error) {
    return {
      success: false,
      error: `Failed to connect to Python API: ${error}`,
      engine: 'error',
      timestamp: new Date().toISOString(),
    };
  }
}

/**
 * Download NX expression file
 */
export async function downloadNXExpressions(
  params: CrateParameters
): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/generate-nx`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ ...params, download: true }),
    });

    if (!response.ok) {
      throw new Error('Failed to generate NX expressions');
    }

    // Get filename from response headers or use default
    const contentDisposition = response.headers.get('content-disposition');
    const filenameMatch = contentDisposition?.match(/filename="(.+)"/);
    const filename = filenameMatch ? filenameMatch[1] : 'crate_expressions.exp';

    // Download the file
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Failed to download NX expressions:', error);
    throw error;
  }
}

/**
 * Validate crate specifications against ASTM standards
 */
export async function validateSpecifications(
  params: Partial<CrateParameters>
): Promise<{
  success: boolean;
  valid?: boolean;
  warnings?: string[];
  designLoad?: number;
  totalWeight?: number;
  error?: string;
}> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/validate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    });

    const data = await response.json();
    return data;
  } catch (error) {
    return {
      success: false,
      error: `Failed to connect to Python API: ${error}`,
    };
  }
}

// Export default API object for convenience
export const PythonAPI = {
  checkHealth: checkAPIHealth,
  calculate: calculateCrateDimensions,
  generateNX: generateNXExpressions,
  downloadNX: downloadNXExpressions,
  validate: validateSpecifications,
};

export default PythonAPI;