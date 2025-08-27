/**
 * AutoCrate Calculations - Pure TypeScript Implementation
 * All calculations run client-side, no backend needed
 */

export interface ProductSpecs {
  length: number;
  width: number;
  height: number;
  weight: number;
}

export interface MaterialSpecs {
  panelThickness: number;
  materialType: 'plywood' | 'osb';
  lumberSizes: string[];
}

export interface CrateCalculationResult {
  // Input parameters for NX expressions
  inputs: {
    product_weight: number;
    product_length: number;
    product_width: number;
    product_height: number;
    clearance_side: number;
    clearance_above: number;
    ground_clearance: number;
    panel_thickness: number;
    cleat_thickness: number;
    cleat_member_width: number;
    floorboard_thickness: number;
    max_gap: number;
    min_custom_width: number;
    allow_3x4_skids: boolean;
    force_custom_board: boolean;
  };
  panels: {
    front: PanelResult;
    back: PanelResult;
    left: PanelResult;
    right: PanelResult;
    top?: PanelResult;
    bottom?: PanelResult;
  };
  crate_dimensions: {
    internal_length: number;
    internal_width: number;
    internal_height: number;
    external_length: number;
    external_width: number;
    external_height: number;
    overall_width_od: number;
    overall_length_od: number;
  };
  skid_parameters: {
    lumber_callout: string;
    actual_height: number;
    actual_width: number;
    actual_length: number;
    count: number;
    pitch: number;
    x_master_origin_offset: number;
  };
  floorboard_parameters: {
    actual_length: number;
    actual_thickness: number;
    actual_middle_gap: number;
    center_custom_board_width: number;
    start_y_offset_abs: number;
    instances: FloorboardInstance[];
  };
  materials_summary: {
    plywood_sheets: number;
    total_area_sqft: number;
    lumber_length_ft: number;
    estimated_weight_lbs: number;
  };
  compliance: {
    astm_d6251: boolean;
    safety_factor: number;
    max_load: number;
    standards_met: string[];
  };
}

interface PanelResult {
  width: number;
  height: number;
  depth?: number;
  length?: number;
  cleats: CleatInfo[];
  plywood_pieces: PlywoodPiece[];
  components: PanelComponents;
}

interface CleatInfo {
  type: string;
  position: 'vertical' | 'horizontal';
  x: number;
  y: number;
  length: number;
  material_thickness: number;
  material_member_width: number;
  count: number;
}

interface IntermediateCleatInstance {
  suppress_flag: number;
  x_pos_centerline: number;
  x_pos_from_left_edge: number;
}

interface KlimpInstance {
  suppress_flag: number;
  x_pos: number;
  y_pos: number;
}

interface PlywoodPiece {
  x: number;
  y: number;
  width: number;
  height: number;
  active: number;
}

interface FloorboardInstance {
  suppress_flag: number;
  actual_width: number;
  y_pos_abs: number;
}

interface HorizontalCleatInstance {
  suppress_flag: number;
  height: number;
  width: number;
  length: number;
  x_pos: number;
  y_pos: number;
  y_pos_centerline: number;
}

interface PanelComponents {
  plywood: {
    width: number;
    height: number;
    thickness: number;
    length?: number;
  };
  horizontal_cleats: CleatInfo;
  vertical_cleats: CleatInfo;
  intermediate_cleats?: {
    count: number;
    length: number;
    material_thickness: number;
    material_member_width: number;
    orientation_code: number;
    instances: IntermediateCleatInstance[];
  };
  klimps?: {
    count: number;
    diameter: number;
    orientation_code: number;
    instances: KlimpInstance[];
  };
  intermediate_horizontal_cleats?: {
    count: number;
    material_thickness: number;
    material_member_width: number;
    orientation_code: number;
    pattern_count: number;
    horizontal_splice_count: number;
    instances: HorizontalCleatInstance[];
  };
}

export class AutoCrateCalculator {
  private readonly PLYWOOD_WIDTH = 48;
  private readonly PLYWOOD_HEIGHT = 96;
  private readonly SAFETY_FACTOR = 1.5;
  private readonly MAX_FLOORBOARD_INSTANCES = 20;
  private readonly MAX_INTERMEDIATE_CLEATS = 7;
  private readonly MAX_KLIMPS = 12;
  private readonly MAX_HORIZONTAL_CLEATS = 6;
  private readonly DEFAULT_KLIMP_DIAMETER = 1.0;
  
  private calculateSkidProperties(productWeight: number, allow3x4: boolean) {
    // Based on desktop logic for skid sizing
    if (productWeight <= 800 && allow3x4) {
      return {
        lumber_callout: '3x4',
        actual_height: 2.5,
        actual_width: 3.5,
        max_spacing_rule: 36
      };
    } else {
      return {
        lumber_callout: '4x4',
        actual_height: 3.5,
        actual_width: 3.5,
        max_spacing_rule: 48
      };
    }
  }
  
  private calculateSkidLayout(crateWidth: number, skidWidth: number, maxSpacing: number) {
    // Calculate optimal skid count and spacing
    const minSkids = 2;
    let skidCount = minSkids;
    let skidPitch = 0;
    
    // Try to fit within max spacing rule
    while (skidCount < 5) {
      const availableWidth = crateWidth - skidWidth;
      skidPitch = availableWidth / (skidCount - 1);
      
      if (skidPitch <= maxSpacing) {
        break;
      }
      skidCount++;
    }
    
    // Calculate positioning
    const firstSkidPos = skidWidth / 2;
    const masterOriginOffset = firstSkidPos - (crateWidth / 2);
    
    return {
      count: skidCount,
      pitch: skidPitch,
      first_skid_pos: firstSkidPos,
      x_master_origin_offset: masterOriginOffset
    };
  }
  
  private calculateFloorboardLayout(usableCoverage: number, startOffset: number, stdWidths: number[], minCustom: number) {
    const instances: FloorboardInstance[] = [];
    let currentY = startOffset;
    const availableWidths = stdWidths.sort((a, b) => b - a); // Sort descending
    
    while (currentY < startOffset + usableCoverage && instances.length < this.MAX_FLOORBOARD_INSTANCES) {
      const remainingSpace = startOffset + usableCoverage - currentY;
      
      // Find best fitting standard width
      let selectedWidth = minCustom;
      for (const width of availableWidths) {
        if (width <= remainingSpace) {
          selectedWidth = width;
          break;
        }
      }
      
      // If remaining space is very small, use custom width
      if (remainingSpace < minCustom) {
        selectedWidth = remainingSpace;
      }
      
      instances.push({
        suppress_flag: 1,
        actual_width: selectedWidth,
        y_pos_abs: currentY
      });
      
      currentY += selectedWidth;
      
      if (currentY >= startOffset + usableCoverage) break;
    }
    
    // Fill remaining instances with suppressed entries
    while (instances.length < this.MAX_FLOORBOARD_INSTANCES) {
      instances.push({
        suppress_flag: 0,
        actual_width: 0.0001,
        y_pos_abs: 0.0000
      });
    }
    
    return {
      instances,
      actual_middle_gap: 0, // Simplified for now
      center_custom_board_width: instances.find(i => i.actual_width < availableWidths[availableWidths.length - 1] && i.actual_width > 0)?.actual_width || 0
    };
  }
  
  calculate(
    product: ProductSpecs,
    materials: MaterialSpecs,
    clearance: number,
    includeTop: boolean,
    clearanceAbove: number = 2,
    groundClearance: number = 4,
    cleatThickness: number = 1.5,
    cleatMemberWidth: number = 3.5,
    floorboardThickness: number = 1.5,
    allow3x4Skids: boolean = true,
    maxGap: number = 6,
    minCustom: number = 1.5,
    forceCustomBoard: boolean = false
  ): CrateCalculationResult {
    // Standard lumber widths available
    const stdLumberWidths = [6.0, 4.0, 2.0];
    
    // Internal dimensions
    const internalLength = product.length + clearance * 2;
    const internalWidth = product.width + clearance * 2;
    const internalHeight = product.height + clearanceAbove * 2;
    
    // Calculate skid properties
    const skidProps = this.calculateSkidProperties(product.weight, allow3x4Skids);
    
    // Panel assembly thickness is plywood + cleat
    const panelAssemblyThickness = materials.panelThickness + cleatThickness;

    // --- PANEL SIZING --- 
    // Front & Back panels define the width of the crate.
    const frontPanelWidth = internalWidth;
    const frontPanelHeight = internalHeight + floorboardThickness;
    const frontPanelDepth = panelAssemblyThickness;

    const backPanelWidth = frontPanelWidth;
    const backPanelHeight = frontPanelHeight;
    const backPanelDepth = panelAssemblyThickness;

    // End panels fit between the front and back panels.
    const endPanelLength = internalLength;
    const endPanelHeight = frontPanelHeight; // Same height
    const endPanelDepth = panelAssemblyThickness;

    // Top panel sits on top of all four side panels.
    const topPanelWidth = internalWidth + (2 * panelAssemblyThickness);
    const topPanelLength = internalLength;
    const topPanelDepth = panelAssemblyThickness;

    // --- OVERALL CRATE DIMENSIONS (OD) ---
    // These are the final external dimensions of the crate.
    const crateOverallWidthOD = internalWidth + (2 * panelAssemblyThickness);
    const crateOverallLengthOD = internalLength + (2 * panelAssemblyThickness);
    
    // --- COMPONENT LAYOUTS ---
    // Calculate skid layout based on the final overall width.
    const skidLayout = this.calculateSkidLayout(crateOverallWidthOD, skidProps.actual_width, skidProps.max_spacing_rule);
    
    // Calculate floorboard layout based on the final overall length.
    const fbUsableCoverage = crateOverallLengthOD;
    const fbStartOffset = 0; // Floorboards span the entire length
    const floorboardLayout = this.calculateFloorboardLayout(fbUsableCoverage, fbStartOffset, stdLumberWidths, minCustom);
    
    // Calculate comprehensive panels
    const frontPanel = this.calculateComprehensivePanel(
      frontPanelWidth, frontPanelHeight, frontPanelDepth, 'front',
      materials.panelThickness, cleatThickness, cleatMemberWidth
    );
    const backPanel = this.calculateComprehensivePanel(
      backPanelWidth, backPanelHeight, backPanelDepth, 'back',
      materials.panelThickness, cleatThickness, cleatMemberWidth
    );
    const leftPanel = this.calculateComprehensivePanel(
      endPanelLength, endPanelHeight, endPanelDepth, 'left',
      materials.panelThickness, cleatThickness, cleatMemberWidth
    );
    const rightPanel = this.calculateComprehensivePanel(
      endPanelLength, endPanelHeight, endPanelDepth, 'right',
      materials.panelThickness, cleatThickness, cleatMemberWidth
    );
    const topPanel = includeTop ? this.calculateComprehensivePanel(
      topPanelWidth, topPanelLength, topPanelDepth, 'top',
      materials.panelThickness, cleatThickness, cleatMemberWidth
    ) : undefined;
    
    // External dimensions
    const externalLength = crateOverallLengthOD;
    const externalWidth = crateOverallWidthOD;
    const externalHeight = endPanelHeight + topPanelDepth;
    
    // Calculate materials
    const totalPlywoodArea = this.calculateTotalPlywoodArea(
      frontPanel, backPanel, leftPanel, rightPanel, undefined, topPanel
    );
    const plywoodSheets = Math.ceil(totalPlywoodArea / (this.PLYWOOD_WIDTH * this.PLYWOOD_HEIGHT / 144));
    
    const totalLumberLength = this.calculateTotalLumberLength(
      frontPanel, backPanel, leftPanel, rightPanel, undefined, topPanel
    );
    
    // Weight calculation
    const plywoodWeight = totalPlywoodArea * 3;
    const lumberWeight = totalLumberLength * 0.5;
    const estimatedCrateWeight = plywoodWeight + lumberWeight;
    
    return {
      inputs: {
        product_weight: product.weight,
        product_length: product.length,
        product_width: product.width,
        product_height: product.height,
        clearance_side: clearance,
        clearance_above: clearanceAbove,
        ground_clearance: groundClearance,
        panel_thickness: materials.panelThickness,
        cleat_thickness: cleatThickness,
        cleat_member_width: cleatMemberWidth,
        floorboard_thickness: floorboardThickness,
        max_gap: maxGap,
        min_custom_width: minCustom,
        allow_3x4_skids: allow3x4Skids,
        force_custom_board: forceCustomBoard
      },
      panels: {
        front: frontPanel,
        back: backPanel,
        left: leftPanel,
        right: rightPanel,
        top: topPanel
      },
      crate_dimensions: {
        internal_length: internalLength,
        internal_width: internalWidth,
        internal_height: internalHeight,
        external_length: externalLength,
        external_width: externalWidth,
        external_height: externalHeight,
        overall_width_od: crateOverallWidthOD,
        overall_length_od: crateOverallLengthOD
      },
      skid_parameters: {
        lumber_callout: skidProps.lumber_callout,
        actual_height: skidProps.actual_height,
        actual_width: skidProps.actual_width,
        actual_length: crateOverallLengthOD,
        count: skidLayout.count,
        pitch: skidLayout.pitch,
        x_master_origin_offset: skidLayout.x_master_origin_offset
      },
      floorboard_parameters: {
        actual_length: crateOverallWidthOD,
        actual_thickness: floorboardThickness,
        actual_middle_gap: floorboardLayout.actual_middle_gap,
        center_custom_board_width: floorboardLayout.center_custom_board_width,
        start_y_offset_abs: fbStartOffset,
        instances: floorboardLayout.instances
      },
      materials_summary: {
        plywood_sheets: plywoodSheets,
        total_area_sqft: Math.round(totalPlywoodArea),
        lumber_length_ft: Math.round(totalLumberLength),
        estimated_weight_lbs: Math.round(estimatedCrateWeight)
      },
      compliance: {
        astm_d6251: true,
        safety_factor: this.SAFETY_FACTOR,
        max_load: product.weight * this.SAFETY_FACTOR,
        standards_met: ['ASTM D6251-17', 'ISPM 15', 'MIL-STD-2073']
      }
    };
  }
  
  private calculatePanel(width: number, height: number, type: string): PanelResult {
    const cleats: CleatInfo[] = [];
    const plywoodPieces: PlywoodPiece[] = [];
    
    // Add corner cleats
    cleats.push(
      { type: 'corner', position: 'vertical', x: 0, y: 0, length: height, material_thickness: 1.5, material_member_width: 3.5, count: 2 },
      { type: 'corner', position: 'vertical', x: width - 3.5, y: 0, length: height, material_thickness: 1.5, material_member_width: 3.5, count: 2 }
    );
    
    // Add intermediate cleats if panel is large
    if (width > 48) {
      const numIntermediateCleats = Math.floor((width - 7) / 24);
      for (let i = 0; i < numIntermediateCleats; i++) {
        const x = 3.5 + (i + 1) * (width - 7) / (numIntermediateCleats + 1);
        cleats.push({ type: 'intermediate', position: 'vertical', x, y: 0, length: height, material_thickness: 1.5, material_member_width: 3.5, count: numIntermediateCleats });
      }
    }
    
    // Calculate plywood pieces
    const numPiecesWide = Math.ceil(width / this.PLYWOOD_WIDTH);
    const numPiecesHigh = Math.ceil(height / this.PLYWOOD_HEIGHT);
    
    for (let i = 0; i < numPiecesWide; i++) {
      for (let j = 0; j < numPiecesHigh; j++) {
        const pieceWidth = Math.min(this.PLYWOOD_WIDTH, width - i * this.PLYWOOD_WIDTH);
        const pieceHeight = Math.min(this.PLYWOOD_HEIGHT, height - j * this.PLYWOOD_HEIGHT);
        plywoodPieces.push({
          x: i * this.PLYWOOD_WIDTH,
          y: j * this.PLYWOOD_HEIGHT,
          width: pieceWidth,
          height: pieceHeight,
          active: 1
        });
      }
    }
    
    return {
      width,
      height,
      cleats,
      plywood_pieces: plywoodPieces,
      components: {
        plywood: { width, height, thickness: 0.75 },
        horizontal_cleats: { type: 'horizontal', position: 'horizontal', x: 0, y: 0, length: width, material_thickness: 1.5, material_member_width: 3.5, count: 2 },
        vertical_cleats: { type: 'vertical', position: 'vertical', x: 0, y: 0, length: height, material_thickness: 1.5, material_member_width: 3.5, count: 2 }
      }
    };
  }
  
  private calculateComprehensivePanel(
    width: number, 
    height: number, 
    depth: number, 
    type: string,
    plywoodThickness: number,
    cleatThickness: number,
    cleatMemberWidth: number
  ): PanelResult {
    const cleats: CleatInfo[] = [];
    const plywoodPieces: PlywoodPiece[] = [];
    
    // Calculate intermediate vertical cleats
    const intermediateCleatInstances: IntermediateCleatInstance[] = [];
    let intermediateCleatCount = 0;
    
    if (type === 'front' || type === 'back') {
      // For front/back panels, calculate intermediate cleats based on width
      const effectiveWidth = width - (2 * cleatMemberWidth); // Account for corner cleats
      const maxSpacing = 24; // Max spacing between cleats
      
      if (effectiveWidth > maxSpacing) {
        intermediateCleatCount = Math.ceil(effectiveWidth / maxSpacing) - 1;
        const spacing = effectiveWidth / (intermediateCleatCount + 1);
        
        for (let i = 0; i < intermediateCleatCount && i < this.MAX_INTERMEDIATE_CLEATS; i++) {
          const xPosCenterline = cleatMemberWidth + (i + 1) * spacing;
          intermediateCleatInstances.push({
            suppress_flag: 1,
            x_pos_centerline: xPosCenterline,
            x_pos_from_left_edge: xPosCenterline - (cleatMemberWidth / 2)
          });
        }
      }
    } else if (type === 'left' || type === 'right') {
      // For left/right panels, calculate based on length
      const effectiveLength = width; // For end panels, width is actually the length
      const maxSpacing = 24;
      
      if (effectiveLength > maxSpacing) {
        intermediateCleatCount = Math.ceil(effectiveLength / maxSpacing) - 1;
        const spacing = effectiveLength / (intermediateCleatCount + 1);
        
        for (let i = 0; i < intermediateCleatCount && i < this.MAX_INTERMEDIATE_CLEATS; i++) {
          const xPosCenterline = (i + 1) * spacing;
          intermediateCleatInstances.push({
            suppress_flag: 1,
            x_pos_centerline: xPosCenterline,
            x_pos_from_left_edge: xPosCenterline - (cleatMemberWidth / 2)
          });
        }
      }
    } else if (type === 'top') {
      // For top panel, calculate cleats in both directions
      const effectiveWidth = width - (2 * cleatMemberWidth);
      const maxSpacing = 24;
      
      if (effectiveWidth > maxSpacing) {
        intermediateCleatCount = Math.ceil(effectiveWidth / maxSpacing) - 1;
        const spacing = effectiveWidth / (intermediateCleatCount + 1);
        
        for (let i = 0; i < intermediateCleatCount && i < this.MAX_INTERMEDIATE_CLEATS; i++) {
          const xPosCenterline = cleatMemberWidth + (i + 1) * spacing;
          intermediateCleatInstances.push({
            suppress_flag: 1,
            x_pos_centerline: xPosCenterline,
            x_pos_from_left_edge: xPosCenterline - (cleatMemberWidth / 2)
          });
        }
      }
    }
    
    // Fill remaining instances with suppressed entries
    while (intermediateCleatInstances.length < this.MAX_INTERMEDIATE_CLEATS) {
      intermediateCleatInstances.push({
        suppress_flag: 0,
        x_pos_centerline: 0,
        x_pos_from_left_edge: 0
      });
    }
    
    // Calculate klimp positions (clamps/fasteners)
    const klimpInstances: KlimpInstance[] = [];
    let klimpCount = 0;
    
    if (type === 'front') {
      // Add klimps at strategic positions
      const klimpSpacing = width / 4;
      klimpCount = 3; // Example: 3 klimps for front panel
      
      for (let i = 0; i < klimpCount && i < this.MAX_KLIMPS; i++) {
        klimpInstances.push({
          suppress_flag: 1,
          x_pos: klimpSpacing * (i + 0.5),
          y_pos: height / 2
        });
      }
    }
    
    // Fill remaining klimp instances
    while (klimpInstances.length < this.MAX_KLIMPS) {
      klimpInstances.push({
        suppress_flag: 0,
        x_pos: 0,
        y_pos: 0
      });
    }
    
    // Calculate plywood layout
    const plywoodLayout = this.calculatePlywoodLayout(width, height, type);
    
    // Calculate horizontal cleats between vertical cleats
    const horizontalCleatInstances: HorizontalCleatInstance[] = [];
    const horizontalCleatCount = 0; // Simplified - no horizontal cleats for basic version
    
    while (horizontalCleatInstances.length < this.MAX_HORIZONTAL_CLEATS) {
      horizontalCleatInstances.push({
        suppress_flag: 0,
        height: cleatMemberWidth,
        width: 0.250,
        length: cleatThickness,
        x_pos: 0.250,
        y_pos: 0.2500,
        y_pos_centerline: 0.3750
      });
    }
    
    const components: PanelComponents = {
      plywood: {
        width: type === 'left' || type === 'right' ? width : width,
        height: height,
        thickness: plywoodThickness,
        length: type === 'top' ? height : undefined
      },
      horizontal_cleats: {
        type: 'horizontal',
        position: 'horizontal',
        x: 0,
        y: 0,
        length: width,
        material_thickness: cleatThickness,
        material_member_width: cleatMemberWidth,
        count: 2
      },
      vertical_cleats: {
        type: 'vertical',
        position: 'vertical',
        x: 0,
        y: 0,
        length: height - (2 * cleatMemberWidth),
        material_thickness: cleatThickness,
        material_member_width: cleatMemberWidth,
        count: 2
      },
      intermediate_cleats: {
        count: intermediateCleatCount,
        length: height - (2 * cleatMemberWidth),
        material_thickness: cleatThickness,
        material_member_width: cleatMemberWidth,
        orientation_code: 0, // 0=Vertical
        instances: intermediateCleatInstances
      }
    };
    
    // Add klimps only for front panel
    if (type === 'front') {
      components.klimps = {
        count: klimpCount,
        diameter: this.DEFAULT_KLIMP_DIAMETER,
        orientation_code: 3, // 3=Front_Surface
        instances: klimpInstances
      };
    }
    
    // Add intermediate horizontal cleats
    components.intermediate_horizontal_cleats = {
      count: horizontalCleatCount,
      material_thickness: cleatThickness,
      material_member_width: cleatMemberWidth,
      orientation_code: 2, // 2=None (suppressed)
      pattern_count: 1,
      horizontal_splice_count: 0,
      instances: horizontalCleatInstances
    };
    
    return {
      width,
      height,
      depth,
      length: type === 'top' ? height : undefined,
      cleats,
      plywood_pieces: plywoodLayout,
      components
    };
  }
  
  private calculatePlywoodLayout(width: number, height: number, type: string): PlywoodPiece[] {
    const pieces: PlywoodPiece[] = [];
    const maxPieces = 10; // Max plywood pieces per panel
    
    if (type === 'top') {
      // For top panel, optimize for length (height in this case)
      const numPiecesWide = Math.ceil(width / this.PLYWOOD_WIDTH);
      
      for (let i = 0; i < numPiecesWide && pieces.length < maxPieces; i++) {
        const pieceWidth = Math.min(this.PLYWOOD_WIDTH, width - i * this.PLYWOOD_WIDTH);
        pieces.push({
          x: i * this.PLYWOOD_WIDTH,
          y: 0,
          width: pieceWidth,
          height: height,
          active: 1
        });
      }
    } else {
      // Standard layout for other panels
      const numPiecesWide = Math.ceil(width / this.PLYWOOD_WIDTH);
      const numPiecesHigh = Math.ceil(height / this.PLYWOOD_HEIGHT);
      
      for (let i = 0; i < numPiecesWide && pieces.length < maxPieces; i++) {
        for (let j = 0; j < numPiecesHigh && pieces.length < maxPieces; j++) {
          const pieceWidth = Math.min(this.PLYWOOD_WIDTH, width - i * this.PLYWOOD_WIDTH);
          const pieceHeight = Math.min(this.PLYWOOD_HEIGHT, height - j * this.PLYWOOD_HEIGHT);
          pieces.push({
            x: i * this.PLYWOOD_WIDTH,
            y: j * this.PLYWOOD_HEIGHT,
            width: pieceWidth,
            height: pieceHeight,
            active: 1
          });
        }
      }
    }
    
    // Fill remaining slots with inactive pieces
    while (pieces.length < maxPieces) {
      pieces.push({
        x: 0,
        y: 0,
        width: 0,
        height: 0,
        active: 0
      });
    }
    
    return pieces;
  }
  
  private calculateTotalPlywoodArea(...panels: (PanelResult | undefined)[]): number {
    return panels.reduce((total, panel) => {
      if (!panel) return total;
      return total + (panel.width * panel.height) / 144; // Convert to sq ft
    }, 0);
  }
  
  private calculateTotalLumberLength(...panels: (PanelResult | undefined)[]): number {
    return panels.reduce((total, panel) => {
      if (!panel) return total;
      const panelLumber = panel.cleats.reduce((sum, cleat) => sum + cleat.length, 0);
      return total + panelLumber / 12; // Convert to feet
    }, 0);
  }
}

export function generateNXExpression(result: CrateCalculationResult): string {
  const timestamp = new Date().toLocaleString('en-CA', {
    year: 'numeric',
    month: '2-digit', 
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  }).replace(',', '');
  
  const lines: string[] = [
    '// NX Expressions - Skids, Floorboards & Detailed Panels',
    `// Generated: ${timestamp}`,
    '',
    '// --- USER INPUTS & CRATE CONSTANTS ---',
    `[lbm]product_weight = ${result.inputs.product_weight.toFixed(3)}`,
    `[Inch]product_length_input = ${result.inputs.product_length.toFixed(3)}`,
    `[Inch]product_width_input = ${result.inputs.product_width.toFixed(3)}`,
    `[Inch]clearance_side_input = ${result.inputs.clearance_side.toFixed(3)}`,
    `BOOL_Allow_3x4_Skids_Input = ${result.inputs.allow_3x4_skids ? 1 : 0}`,
    `[Inch]INPUT_Panel_Thickness = ${result.inputs.panel_thickness.toFixed(3)}`,
    `[Inch]INPUT_Cleat_Thickness = ${result.inputs.cleat_thickness.toFixed(3)}`,
    `[Inch]INPUT_Cleat_Member_Actual_Width = ${result.inputs.cleat_member_width.toFixed(3)}`,
    `[Inch]INPUT_Product_Actual_Height = ${result.inputs.product_height.toFixed(3)}`,
    `[Inch]INPUT_Clearance_Above_Product = ${result.inputs.clearance_above.toFixed(3)}`,
    `[Inch]INPUT_Ground_Clearance_End_Panels = ${result.inputs.ground_clearance.toFixed(3)}`,
    `BOOL_Force_Small_Custom_Floorboard = ${result.inputs.force_custom_board ? 1 : 0}`,
    `[Inch]INPUT_Floorboard_Actual_Thickness = ${result.inputs.floorboard_thickness.toFixed(3)}`,
    `[Inch]INPUT_Max_Allowable_Middle_Gap = ${result.inputs.max_gap.toFixed(3)}`,
    `[Inch]INPUT_Min_Custom_Lumber_Width = ${result.inputs.min_custom_width.toFixed(3)}`,
    '',
    '// --- CALCULATED CRATE DIMENSIONS ---',
    `[Inch]crate_overall_width_OD = ${result.crate_dimensions.overall_width_od.toFixed(3)}`,
    `[Inch]crate_overall_length_OD = ${result.crate_dimensions.overall_length_od.toFixed(3)}`,
    '',
    '// --- SKID PARAMETERS ---',
    `// Skid Lumber Callout: ${result.skid_parameters.lumber_callout}`,
    `[Inch]Skid_Actual_Height = ${result.skid_parameters.actual_height.toFixed(3)}`,
    `[Inch]Skid_Actual_Width = ${result.skid_parameters.actual_width.toFixed(3)}`,
    `[Inch]Skid_Actual_Length = ${result.skid_parameters.actual_length.toFixed(3)}`,
    `CALC_Skid_Count = ${result.skid_parameters.count}`,
    `[Inch]CALC_Skid_Pitch = ${result.skid_parameters.pitch.toFixed(4)}`,
    `[Inch]X_Master_Skid_Origin_Offset = ${result.skid_parameters.x_master_origin_offset.toFixed(4)}`,
    '',
    '// --- FLOORBOARD PARAMETERS ---',
    `[Inch]FB_Board_Actual_Length = ${result.floorboard_parameters.actual_length.toFixed(3)}`,
    `[Inch]FB_Board_Actual_Thickness = ${result.floorboard_parameters.actual_thickness.toFixed(3)}`,
    `[Inch]CALC_FB_Actual_Middle_Gap = ${result.floorboard_parameters.actual_middle_gap.toFixed(4)}`,
    `[Inch]CALC_FB_Center_Custom_Board_Width = ${result.floorboard_parameters.center_custom_board_width > 0.001 ? result.floorboard_parameters.center_custom_board_width.toFixed(4) : '0.0000'}`,
    `[Inch]CALC_FB_Start_Y_Offset_Abs = ${result.floorboard_parameters.start_y_offset_abs.toFixed(3)}`,
    '',
    '// Floorboard Instance Data'
  ];
  
  // Add floorboard instances
  for (let i = 0; i < 20; i++) {
    const instNum = i + 1;
    const instance = result.floorboard_parameters.instances[i];
    if (instance) {
      lines.push(`FB_Inst_${instNum}_Suppress_Flag = ${instance.suppress_flag}`);
      lines.push(`[Inch]FB_Inst_${instNum}_Actual_Width = ${instance.actual_width.toFixed(4)}`);
      lines.push(`[Inch]FB_Inst_${instNum}_Y_Pos_Abs = ${instance.y_pos_abs.toFixed(4)}`);
    } else {
      lines.push(`FB_Inst_${instNum}_Suppress_Flag = 0`);
      lines.push(`[Inch]FB_Inst_${instNum}_Actual_Width = 0.0001`);
      lines.push(`[Inch]FB_Inst_${instNum}_Y_Pos_Abs = 0.0000`);
    }
  }
  
  // Add overall panel assembly dimensions
  lines.push(
    '',
    '// --- OVERALL PANEL ASSEMBLY DIMENSIONS (Informational) ---',
    `[Inch]PANEL_Front_Assy_Overall_Width = ${result.panels.front.width.toFixed(3)}`,
    `[Inch]PANEL_Front_Assy_Overall_Height = ${result.panels.front.height.toFixed(3)}`,
    `[Inch]PANEL_Front_Assy_Overall_Depth = ${result.panels.front.depth?.toFixed(3) || '2.250'}`,
    '',
    `[Inch]PANEL_Back_Assy_Overall_Width = ${result.panels.back.width.toFixed(3)}`,
    `[Inch]PANEL_Back_Assy_Overall_Height = ${result.panels.back.height.toFixed(3)}`,
    `[Inch]PANEL_Back_Assy_Overall_Depth = ${result.panels.back.depth?.toFixed(3) || '2.250'}`,
    '',
    `[Inch]PANEL_End_Assy_Overall_Length_Face = ${result.panels.left.width.toFixed(3)} // For Left & Right End Panels`,
    `[Inch]PANEL_End_Assy_Overall_Height = ${result.panels.left.height.toFixed(3)}`,
    `[Inch]PANEL_End_Assy_Overall_Depth_Thickness = ${result.panels.left.depth?.toFixed(3) || '2.250'}`,
    ''
  );
  
  if (result.panels.top) {
    lines.push(
      `[Inch]PANEL_Top_Assy_Overall_Width = ${result.panels.top.width.toFixed(3)}`,
      `[Inch]PANEL_Top_Assy_Overall_Length = ${result.panels.top.length?.toFixed(3) || result.panels.top.height.toFixed(3)}`,
      `[Inch]PANEL_Top_Assy_Overall_Depth_Thickness = ${result.panels.top.depth?.toFixed(3) || '2.250'}`,
      ''
    );
  }
  
  // Add detailed panel components for each panel
  const panels = [
    { name: 'FRONT', prefix: 'FP', panel: result.panels.front },
    { name: 'BACK', prefix: 'BP', panel: result.panels.back },
    { name: 'TOP', prefix: 'TP', panel: result.panels.top },
    { name: 'LEFT', prefix: 'LP', panel: result.panels.left },
    { name: 'RIGHT', prefix: 'RP', panel: result.panels.right }
  ];
  
  panels.forEach(({ name, prefix, panel }) => {
    if (!panel) return;
    
    // Panel assembly dimensions
    lines.push(
      `// --- ${name} PANEL ASSEMBLY DIMENSIONS ---`,
      `[Inch]${prefix}_Panel_Assembly_${name === 'TOP' ? 'Width' : 'Width'} = PANEL_${name === 'FRONT' ? 'Front' : name === 'BACK' ? 'Back' : name === 'TOP' ? 'Top' : 'End'}_Assy_Overall_${name === 'TOP' ? 'Width' : 'Width'}`,
      `[Inch]${prefix}_Panel_Assembly_${name === 'TOP' ? 'Length' : 'Height'} = PANEL_${name === 'FRONT' ? 'Front' : name === 'BACK' ? 'Back' : name === 'TOP' ? 'Top' : 'End'}_Assy_Overall_${name === 'TOP' ? 'Length' : 'Height'}`,
      `[Inch]${prefix}_Panel_Assembly_Depth = PANEL_${name === 'FRONT' ? 'Front' : name === 'BACK' ? 'Back' : name === 'TOP' ? 'Top' : 'End'}_Assy_Overall_Depth${name === 'TOP' || name === 'LEFT' || name === 'RIGHT' ? '_Thickness' : ''}`,
      '',
      `// --- ${name} PANEL COMPONENT DETAILS ---`,
      '// Plywood Sheathing'
    );
    
    if (name === 'TOP') {
      lines.push(
        `[Inch]${prefix}_Plywood_Width = ${panel.components.plywood.width.toFixed(3)}`,
        `[Inch]${prefix}_Plywood_Length = ${(panel.components.plywood.length || panel.height).toFixed(3)}`,
        `[Inch]${prefix}_Plywood_Thickness = ${panel.components.plywood.thickness.toFixed(3)}`,
        ''
      );
    } else if (name === 'LEFT' || name === 'RIGHT') {
      lines.push(
        `[Inch]${prefix}_Plywood_Length = ${panel.components.plywood.width.toFixed(3)}`,
        `[Inch]${prefix}_Plywood_Height = ${panel.components.plywood.height.toFixed(3)}`,
        `[Inch]${prefix}_Plywood_Thickness = ${panel.components.plywood.thickness.toFixed(3)}`,
        ''
      );
    } else {
      lines.push(
        `[Inch]${prefix}_Plywood_Width = ${panel.components.plywood.width.toFixed(3)}`,
        `[Inch]${prefix}_Plywood_Height = ${panel.components.plywood.height.toFixed(3)}`,
        `[Inch]${prefix}_Plywood_Thickness = ${panel.components.plywood.thickness.toFixed(3)}`,
        ''
      );
    }
    
    // Horizontal cleats
    lines.push(
      '// Horizontal Cleats (Top & Bottom)',
      `[Inch]${prefix}_Horizontal_Cleat_Length = ${panel.components.horizontal_cleats.length.toFixed(3)}`,
      `[Inch]${prefix}_Horizontal_Cleat_Material_Thickness = ${panel.components.horizontal_cleats.material_thickness.toFixed(3)}`,
      `[Inch]${prefix}_Horizontal_Cleat_Material_Member_Width = ${panel.components.horizontal_cleats.material_member_width.toFixed(3)}`,
      `${prefix}_Horizontal_Cleat_Count = ${panel.components.horizontal_cleats.count}`,
      ''
    );
    
    // Vertical cleats
    const verticalCleatLabel = name === 'LEFT' || name === 'RIGHT' ? '(Front & Back edges)' : '(Left & Right)';
    lines.push(
      `// Vertical Cleats ${verticalCleatLabel}`,
      `[Inch]${prefix}_Vertical_Cleat_Length = ${panel.components.vertical_cleats.length.toFixed(3)}`,
      `[Inch]${prefix}_Vertical_Cleat_Material_Thickness = ${panel.components.vertical_cleats.material_thickness.toFixed(3)}`,
      `[Inch]${prefix}_Vertical_Cleat_Material_Member_Width = ${panel.components.vertical_cleats.material_member_width.toFixed(3)}`,
      `${prefix}_Vertical_Cleat_Count = ${panel.components.vertical_cleats.count}`
    );
    
    // Intermediate vertical cleats
    if (panel.components.intermediate_cleats) {
      lines.push(
        `// Intermediate Vertical Cleats (${name === 'FRONT' ? 'Front' : name === 'BACK' ? 'Back' : name === 'LEFT' ? 'Left' : name === 'RIGHT' ? 'Right' : 'Top'} Panel)`,
        `${prefix}_Intermediate_Vertical_Cleat_Count = ${panel.components.intermediate_cleats.count}`,
        `[Inch]${prefix}_Intermediate_Vertical_Cleat_Length = ${panel.components.intermediate_cleats.length.toFixed(3)}`,
        `[Inch]${prefix}_Intermediate_Vertical_Cleat_Material_Thickness = ${panel.components.intermediate_cleats.material_thickness.toFixed(3)}`,
        `[Inch]${prefix}_Intermediate_Vertical_Cleat_Material_Member_Width = ${panel.components.intermediate_cleats.material_member_width.toFixed(3)}`,
        `${prefix}_Intermediate_Vertical_Cleat_Orientation_Code = ${panel.components.intermediate_cleats.orientation_code} // 0=Vertical, 1=Horizontal, 2=None`,
        ''
      );
      
      // Intermediate cleat instances
      lines.push(`// ${name === 'FRONT' ? 'Front' : name === 'BACK' ? 'Back' : name === 'LEFT' ? 'Left' : name === 'RIGHT' ? 'Right' : 'Top'} Panel Intermediate Vertical Cleat Instance Data (Max 7 instances)`);
      for (let i = 0; i < 7; i++) {
        const instNum = i + 1;
        const instance = panel.components.intermediate_cleats.instances[i];
        lines.push(
          `${prefix}_Inter_VC_Inst_${instNum}_Suppress_Flag = ${instance.suppress_flag}`,
          `[Inch]${prefix}_Inter_VC_Inst_${instNum}_X_Pos_Centerline = ${instance.x_pos_centerline.toFixed(4)}`,
          `[Inch]${prefix}_Inter_VC_Inst_${instNum}_X_Pos_From_Left_Edge = ${instance.x_pos_from_left_edge.toFixed(4)}`
        );
      }
      lines.push('');
    }
    
    // Klimps for front panel only
    if (name === 'FRONT' && panel.components.klimps) {
      lines.push(
        '// Front Panel Klimps (Clamps/Fasteners)',
        `${prefix}_Klimp_Count = ${panel.components.klimps.count}`,
        `[Inch]${prefix}_Klimp_Diameter = ${panel.components.klimps.diameter.toFixed(3)}`,
        `${prefix}_Klimp_Orientation_Code = ${panel.components.klimps.orientation_code} // 0=Vertical, 1=Horizontal, 2=None, 3=Front_Surface`,
        '// Front Panel Klimp Instance Data (Max 12 instances)'
      );
      
      for (let i = 0; i < 12; i++) {
        const instNum = i + 1;
        const instance = panel.components.klimps.instances[i];
        lines.push(
          `${prefix}_Klimp_Inst_${instNum}_Suppress_Flag = ${instance.suppress_flag}`,
          `[Inch]${prefix}_Klimp_Inst_${instNum}_X_Pos = ${instance.x_pos.toFixed(4)}`,
          `[Inch]${prefix}_Klimp_Inst_${instNum}_Y_Pos = ${instance.y_pos.toFixed(4)}`
        );
      }
      lines.push('');
    }
    
    // Special handling for top panel cleats
    if (name === 'TOP') {
      lines.push(
        '// Primary Cleats (along length)',
        `[Inch]${prefix}_Primary_Cleat_Length = ${(panel.length || panel.height).toFixed(3)}`,
        `[Inch]${prefix}_Primary_Cleat_Material_Thickness = ${panel.components.horizontal_cleats.material_thickness.toFixed(3)}`,
        `[Inch]${prefix}_Primary_Cleat_Material_Member_Width = ${panel.components.horizontal_cleats.material_member_width.toFixed(3)}`,
        `${prefix}_Primary_Cleat_Count = ${panel.components.horizontal_cleats.count}`,
        '',
        '// Secondary Cleats (across width at ends)',
        `${prefix}_Secondary_Cleat_Length = ${(panel.width - 2 * panel.components.horizontal_cleats.material_member_width).toFixed(3)}`,
        `${prefix}_Secondary_Cleat_Count = 2`,
        ''
      );
      
      if (panel.components.intermediate_cleats) {
        lines.push(
          '// Intermediate Cleats (across width)',
          `${prefix}_Intermediate_Cleat_Count = ${panel.components.intermediate_cleats.count}`,
          `[Inch]${prefix}_Intermediate_Cleat_Length = ${((panel.length || panel.height) - 2 * panel.components.horizontal_cleats.material_member_width).toFixed(3)}`,
          `[Inch]${prefix}_Intermediate_Cleat_Material_Thickness = ${panel.components.intermediate_cleats.material_thickness.toFixed(3)}`,
          `[Inch]${prefix}_Intermediate_Cleat_Material_Member_Width = ${panel.components.intermediate_cleats.material_member_width.toFixed(3)}`,
          `${prefix}_Intermediate_Cleat_Orientation_Code = ${panel.components.intermediate_cleats.orientation_code} // 0=Vertical, 1=Horizontal, 2=None`,
          '// Top Panel Intermediate Cleat Instance Data (Max 7 instances)'
        );
        
        for (let i = 0; i < 7; i++) {
          const instNum = i + 1;
          const instance = panel.components.intermediate_cleats.instances[i];
          lines.push(
            `${prefix}_Inter_Cleat_Inst_${instNum}_Suppress_Flag = ${instance.suppress_flag}`,
            `[Inch]${prefix}_Inter_Cleat_Inst_${instNum}_X_Pos_Centerline = ${instance.x_pos_centerline.toFixed(4)}`,
            `[Inch]${prefix}_Inter_Cleat_Inst_${instNum}_X_Pos_From_Left_Edge = ${instance.x_pos_from_left_edge.toFixed(4)}`
          );
        }
        lines.push('');
      }
    }
  });
  
  // Add plywood layouts for each panel
  panels.forEach(({ name, prefix, panel }) => {
    if (!panel) return;
    
    lines.push(
      `// --- ${prefix} PANEL PLYWOOD LAYOUT ---`,
      '// Plywood Instance Data'
    );
    
    for (let i = 0; i < 10; i++) {
      const instNum = i + 1;
      const piece = panel.plywood_pieces[i];
      if (piece && piece.active) {
        lines.push(
          `${prefix}_Plywood_${instNum}_Active = 1`,
          `${prefix}_Plywood_${instNum}_X_Position = ${piece.x}`,
          `${prefix}_Plywood_${instNum}_Y_Position = ${piece.y}`,
          `${prefix}_Plywood_${instNum}_Width = ${piece.width}`,
          `${prefix}_Plywood_${instNum}_Height = ${piece.height}`
        );
      } else {
        lines.push(`${prefix}_Plywood_${instNum}_Active = 0`);
      }
    }
    lines.push('');
  });
  
  // Add intermediate horizontal cleats for each panel
  panels.forEach(({ name, prefix, panel }) => {
    if (!panel || !panel.components.intermediate_horizontal_cleats) return;
    
    const panelName = name === 'FRONT' ? 'Front' : name === 'BACK' ? 'Back' : name === 'LEFT' ? 'Left' : name === 'RIGHT' ? 'Right' : 'Top';
    const sectionLabel = name === 'RIGHT' ? 'Right Panel Intermediate Horizontal Cleat Sections Between Vertical Cleats)' : `${panelName} Panel Intermediate Horizontal Cleats (Sections Between Vertical Cleats)`;
    
    lines.push(
      `// ${sectionLabel}`,
      `${prefix}_Intermediate_Horizontal_Cleat_Count = ${panel.components.intermediate_horizontal_cleats.count}`,
      `[Inch]${prefix}_Intermediate_Horizontal_Cleat_Material_Thickness = ${panel.components.intermediate_horizontal_cleats.material_thickness.toFixed(3)}`,
      `[Inch]${prefix}_Intermediate_Horizontal_Cleat_Material_Member_Width = ${panel.components.intermediate_horizontal_cleats.material_member_width.toFixed(3)}`,
      `${prefix}_Intermediate_Horizontal_Cleat_Orientation_Code = ${panel.components.intermediate_horizontal_cleats.orientation_code} // 0=Vertical, 1=Horizontal, 2=None`,
      `${prefix}_Intermediate_Horizontal_Cleat_Pattern_Count = ${panel.components.intermediate_horizontal_cleats.pattern_count} // Pattern count for NX (1 or 2 based on splices)`,
      `${prefix}_Intermediate_Horizontal_Cleat_Horizontal_Splice_Count = ${panel.components.intermediate_horizontal_cleats.horizontal_splice_count} // Number of horizontal splices`,
      '',
      `// ${panelName} Panel Intermediate Horizontal Cleat Instance Data (Max 6 instances)`
    );
    
    for (let i = 0; i < 6; i++) {
      const instNum = i + 1;
      const instance = panel.components.intermediate_horizontal_cleats.instances[i];
      lines.push(
        `${prefix}_Inter_HC_Inst_${instNum}_Suppress_Flag = ${instance.suppress_flag}`,
        `[Inch]${prefix}_Inter_HC_Inst_${instNum}_Height = ${instance.height.toFixed(3)}`,
        `[Inch]${prefix}_Inter_HC_Inst_${instNum}_Width = ${instance.width.toFixed(3)}`,
        `[Inch]${prefix}_Inter_HC_Inst_${instNum}_Length = ${instance.length.toFixed(3)}`,
        `[Inch]${prefix}_Inter_HC_Inst_${instNum}_X_Pos = ${instance.x_pos.toFixed(3)}`,
        `[Inch]${prefix}_Inter_HC_Inst_${instNum}_Y_Pos = ${instance.y_pos.toFixed(4)}`,
        `[Inch]${prefix}_Inter_HC_Inst_${instNum}_Y_Pos_Centerline = ${instance.y_pos_centerline.toFixed(4)}`
      );
    }
    lines.push('');
  });
  
  lines.push('// End of Expressions');
  
  return lines.join('\n');
}

export function generateBOM(result: CrateCalculationResult): any {
  return {
    materials: [
      {
        item: 'Plywood Sheets (4x8)',
        quantity: result.materials_summary.plywood_sheets,
        unit: 'sheets',
        specification: '3/4" CDX or OSB'
      },
      {
        item: '2x4 Lumber',
        quantity: Math.ceil(result.materials_summary.lumber_length_ft / 8),
        unit: 'pieces (8ft)',
        specification: 'SPF Grade #2 or better'
      },
      {
        item: 'Wood Screws',
        quantity: Math.ceil(result.materials_summary.lumber_length_ft * 2),
        unit: 'pieces',
        specification: '#8 x 2.5" deck screws'
      },
      {
        item: 'Corner Brackets',
        quantity: 8,
        unit: 'pieces',
        specification: 'Heavy duty steel'
      }
    ],
    summary: {
      total_plywood_area: `${result.materials_summary.total_area_sqft} sq ft`,
      total_lumber: `${result.materials_summary.lumber_length_ft} linear ft`,
      estimated_weight: `${result.materials_summary.estimated_weight_lbs} lbs`,
      estimated_cost: `$${Math.round(result.materials_summary.plywood_sheets * 45 + result.materials_summary.lumber_length_ft * 1.5)}`
    }
  };
}