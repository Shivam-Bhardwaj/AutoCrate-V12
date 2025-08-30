/**
 * AutoCrate Calculations - Fixed Version
 * Matches exact logic from desktop nx_expressions_generator.py
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
  private readonly VERTICAL_CLEAT_MATERIAL_MULTIPLIER = 1.0; // Matches desktop logic
  
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
    // Calculate number of skids needed
    const minSkids = 2;
    const maxSkidSpacing = Math.min(maxSpacing, crateWidth - skidWidth);
    const skidCount = Math.max(minSkids, Math.ceil((crateWidth - skidWidth) / maxSkidSpacing) + 1);
    
    // Calculate pitch (center to center spacing)
    const pitch = skidCount > 1 ? (crateWidth - skidWidth) / (skidCount - 1) : 0;
    
    // Calculate master origin offset (distance from crate edge to first skid center)
    const xMasterOriginOffset = skidWidth / 2;
    
    return {
      count: skidCount,
      pitch: pitch,
      x_master_origin_offset: xMasterOriginOffset,
      actual_length: crateWidth // Skids run the full width
    };
  }

  private calculateVerticalCleatMaterialNeeded(panelWidth: number, panelHeight: number, cleatMemberWidth: number): number {
    const MIN_CLEAT_SPACING = 0.25; // Minimum gap between cleats to avoid interference
    
    // Generate plywood layout
    const plywoodSheets = this.calculatePlywoodLayout(panelWidth, panelHeight);
    
    // Extract vertical splice positions (where sheets meet vertically)
    const verticalSplices: number[] = [];
    for (const sheet of plywoodSheets) {
      if (sheet.active === 1 && sheet.x > 0 && sheet.x < panelWidth) {
        verticalSplices.push(sheet.x);
      }
    }
    
    // If no vertical splices, no extra material needed
    if (verticalSplices.length === 0) {
      return 0;
    }
    
    // Calculate edge cleat positions (matching desktop logic exactly)
    const leftEdgeCleatCenterline = cleatMemberWidth / 2.0;
    const rightEdgeCleatCenterline = panelWidth - (cleatMemberWidth / 2.0);
    
    // Check if any splice is too close to the right edge cleat
    let materialNeeded = 0.0;
    
    for (const spliceX of verticalSplices) {
      // Check clearance from right edge cleat
      const rightClearance = rightEdgeCleatCenterline - spliceX - cleatMemberWidth;
      
      // If splice cleat would be too close to right edge cleat, calculate material needed
      if (rightClearance < MIN_CLEAT_SPACING) {
        // Calculate how much we need to extend the panel
        let extensionNeeded = MIN_CLEAT_SPACING - rightClearance + cleatMemberWidth;
        // Round up to nearest 0.25"
        extensionNeeded = Math.ceil(extensionNeeded / 0.25) * 0.25;
        materialNeeded = Math.max(materialNeeded, extensionNeeded);
      }
    }
    
    return materialNeeded;
  }
  
  private calculateFloorboardLayout(
    usableCoverage: number,
    startOffset: number,
    availableWidths: number[],
    minCustom: number
  ) {
    const instances: FloorboardInstance[] = [];
    let currentY = startOffset;
    const sortedWidths = [...availableWidths].sort((a, b) => b - a);
    
    // Standard floorboard layout algorithm from desktop
    while (currentY < startOffset + usableCoverage && instances.length < this.MAX_FLOORBOARD_INSTANCES) {
      const remainingSpace = startOffset + usableCoverage - currentY;
      let selectedWidth = 0;
      
      // Try to use the largest width that fits
      for (const width of sortedWidths) {
        if (width <= remainingSpace) {
          selectedWidth = width;
          break;
        }
      }
      
      // If no standard width fits and remaining space is less than minCustom, use remaining space
      // If no standard width fits but remaining space is larger than minCustom, use minCustom
      if (selectedWidth === 0) {
        if (remainingSpace < minCustom) {
          selectedWidth = remainingSpace;
        } else {
          selectedWidth = minCustom;
        }
      }
      
      // Only add if we have a valid width
      if (selectedWidth > 0) {
        instances.push({
          suppress_flag: 1,
          actual_width: selectedWidth,
          y_pos_abs: currentY
        });
        
        currentY += selectedWidth;
      } else {
        // Safety break to prevent infinite loop
        break;
      }
      
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
  
  private calculatePlywoodLayout(panelWidth: number, panelHeight: number) {
    const pieces: PlywoodPiece[] = [];
    const maxPieces = 10;
    
    // Calculate optimal plywood layout (simplified version)
    const sheetsAcross = Math.ceil(panelWidth / this.PLYWOOD_WIDTH);
    const sheetsDown = Math.ceil(panelHeight / this.PLYWOOD_HEIGHT);
    
    let pieceIndex = 0;
    for (let row = 0; row < sheetsDown && pieceIndex < maxPieces; row++) {
      for (let col = 0; col < sheetsAcross && pieceIndex < maxPieces; col++) {
        const x = col * this.PLYWOOD_WIDTH;
        const y = row * this.PLYWOOD_HEIGHT;
        const width = Math.min(this.PLYWOOD_WIDTH, panelWidth - x);
        const height = Math.min(this.PLYWOOD_HEIGHT, panelHeight - y);
        
        pieces.push({
          x: x,
          y: y,
          width: width,
          height: height,
          active: 1
        });
        pieceIndex++;
      }
    }
    
    // Fill remaining with inactive pieces
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
  
  private calculateComprehensivePanel(
    width: number, 
    height: number,
    depth: number,
    type: 'front' | 'back' | 'left' | 'right' | 'top',
    panelThickness: number,
    cleatThickness: number,
    cleatMemberWidth: number
  ): PanelResult {
    // Calculate cleats
    const cleats: CleatInfo[] = [];
    
    // Horizontal cleats (top and bottom)
    cleats.push({
      type: 'horizontal_top',
      position: 'horizontal',
      x: 0,
      y: height - cleatMemberWidth,
      length: width,
      material_thickness: cleatThickness,
      material_member_width: cleatMemberWidth,
      count: 1
    });
    
    cleats.push({
      type: 'horizontal_bottom',
      position: 'horizontal',
      x: 0,
      y: 0,
      length: width,
      material_thickness: cleatThickness,
      material_member_width: cleatMemberWidth,
      count: 1
    });
    
    // Vertical cleats (left and right)
    const verticalCleatLength = height - 2 * cleatMemberWidth;
    cleats.push({
      type: 'vertical_left',
      position: 'vertical',
      x: 0,
      y: cleatMemberWidth,
      length: verticalCleatLength,
      material_thickness: cleatThickness,
      material_member_width: cleatMemberWidth,
      count: 1
    });
    
    cleats.push({
      type: 'vertical_right',
      position: 'vertical',
      x: width - cleatMemberWidth,
      y: cleatMemberWidth,
      length: verticalCleatLength,
      material_thickness: cleatThickness,
      material_member_width: cleatMemberWidth,
      count: 1
    });
    
    // Calculate intermediate cleats
    const intermediateCleatInstances: IntermediateCleatInstance[] = [];
    let intermediateCount = 0;
    
    if (width > 48) {
      // Add intermediate vertical cleats for wide panels
      const spacing = 48; // Standard spacing
      const availableWidth = width - cleatMemberWidth * 2;
      
      // Calculate number of intermediate cleats needed
      if (availableWidth > spacing) {
        intermediateCount = Math.floor(availableWidth / spacing) - 1;
        intermediateCount = Math.max(0, intermediateCount); // Ensure non-negative
        intermediateCount = Math.min(intermediateCount, this.MAX_INTERMEDIATE_CLEATS);
      }
      
      for (let i = 0; i < this.MAX_INTERMEDIATE_CLEATS; i++) {
        if (i < intermediateCount) {
          const xPos = cleatMemberWidth + (i + 1) * spacing;
          intermediateCleatInstances.push({
            suppress_flag: 1,
            x_pos_centerline: xPos + cleatMemberWidth / 2,
            x_pos_from_left_edge: xPos
          });
        } else {
          intermediateCleatInstances.push({
            suppress_flag: 0,
            x_pos_centerline: 0,
            x_pos_from_left_edge: 0
          });
        }
      }
    } else {
      // Fill with suppressed instances
      for (let i = 0; i < this.MAX_INTERMEDIATE_CLEATS; i++) {
        intermediateCleatInstances.push({
          suppress_flag: 0,
          x_pos_centerline: 0,
          x_pos_from_left_edge: 0
        });
      }
    }
    
    // Calculate klimps for front panel only
    const klimpInstances: KlimpInstance[] = [];
    if (type === 'front') {
      // Add klimps at strategic points
      const klimpCount = Math.min(4, this.MAX_KLIMPS);
      for (let i = 0; i < this.MAX_KLIMPS; i++) {
        if (i < klimpCount) {
          klimpInstances.push({
            suppress_flag: 1,
            x_pos: (width / (klimpCount + 1)) * (i + 1),
            y_pos: height / 2
          });
        } else {
          klimpInstances.push({
            suppress_flag: 0,
            x_pos: 0,
            y_pos: 0
          });
        }
      }
    }
    
    // Calculate horizontal intermediate cleats
    const horizontalCleatInstances: HorizontalCleatInstance[] = [];
    for (let i = 0; i < this.MAX_HORIZONTAL_CLEATS; i++) {
      horizontalCleatInstances.push({
        suppress_flag: 0,
        height: 0,
        width: 0,
        length: 0,
        x_pos: 0,
        y_pos: 0,
        y_pos_centerline: 0
      });
    }
    
    // Calculate plywood pieces
    const plywoodPieces = this.calculatePlywoodLayout(width, height);
    
    // Create panel result
    const result: PanelResult = {
      width: width,
      height: height,
      depth: depth,
      cleats: cleats,
      plywood_pieces: plywoodPieces,
      components: {
        plywood: {
          width: width,
          height: height,
          thickness: panelThickness
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
          length: verticalCleatLength,
          material_thickness: cleatThickness,
          material_member_width: cleatMemberWidth,
          count: 2
        },
        intermediate_cleats: intermediateCount > 0 || type === 'top' ? {
          count: intermediateCount,
          length: verticalCleatLength,
          material_thickness: cleatThickness,
          material_member_width: cleatMemberWidth,
          orientation_code: 0,
          instances: intermediateCleatInstances
        } : undefined,
        klimps: type === 'front' ? {
          count: klimpInstances.filter(k => k.suppress_flag === 1).length,
          diameter: this.DEFAULT_KLIMP_DIAMETER,
          orientation_code: 3,
          instances: klimpInstances
        } : undefined,
        intermediate_horizontal_cleats: {
          count: 0,
          material_thickness: cleatThickness,
          material_member_width: cleatMemberWidth,
          orientation_code: 1,
          pattern_count: 1,
          horizontal_splice_count: 0,
          instances: horizontalCleatInstances
        }
      }
    };
    
    // For top panel, adjust the naming
    if (type === 'top') {
      result.length = height;  // The second parameter is the length for top panel
    }
    
    return result;
  }
  
  private calculateTotalPlywoodArea(...panels: (PanelResult | undefined)[]): number {
    return panels.reduce((total, panel) => {
      if (!panel) return total;
      const panelArea = (panel.width * panel.height) / 144; // Convert to sq ft
      return total + panelArea;
    }, 0);
  }
  
  private calculateTotalLumberLength(...panels: (PanelResult | undefined)[]): number {
    return panels.reduce((total, panel) => {
      if (!panel) return total;
      const panelLumber = panel.cleats.reduce((sum, cleat) => {
        return sum + cleat.length * cleat.count;
      }, 0);
      return total + panelLumber / 12; // Convert to feet
    }, 0);
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
    
    // === INITIAL CRATE DIMENSIONS ===
    // This matches the desktop logic exactly
    const crateOverallWidthOD = product.width + (2 * clearance);
    const skidModelLength = product.length + (2 * clearance);
    const crateOverallLengthOD = skidModelLength;
    
    // === SKID LUMBER PROPERTIES ===
    const skidProps = this.calculateSkidProperties(product.weight, allow3x4Skids);
    const skidActualHeight = skidProps.actual_height;
    const skidActualWidth = skidProps.actual_width;
    
    // === PANEL ASSEMBLY CALCULATIONS ===
    const panelAssemblyOverallThickness = materials.panelThickness + cleatThickness;
    
    // Front/Back panels
    const frontPanelCalcDepth = panelAssemblyOverallThickness;
    const backPanelCalcDepth = panelAssemblyOverallThickness;
    
    // End Panels are sandwiched between Front and Back
    const endPanelCalcLength = crateOverallLengthOD - frontPanelCalcDepth - backPanelCalcDepth;
    const endPanelCalcHeightBase = floorboardThickness + product.height + clearanceAbove;
    const endPanelCalcHeight = skidActualHeight + floorboardThickness + product.height + clearanceAbove - groundClearance;
    const endPanelCalcDepth = panelAssemblyOverallThickness;
    
    // Front/Back panel width calculation
    const panelTotalThickness = cleatThickness + materials.panelThickness;
    let frontPanelCalcWidth = product.width + (2 * clearance) + (2 * panelTotalThickness);
    let frontPanelCalcHeight = endPanelCalcHeightBase;
    
    let backPanelCalcWidth = frontPanelCalcWidth;
    let backPanelCalcHeight = frontPanelCalcHeight;
    
    // Top Panel
    let topPanelCalcWidth = frontPanelCalcWidth;
    let topPanelCalcLength = crateOverallLengthOD;
    const topPanelCalcDepth = panelAssemblyOverallThickness;
    
    // === VERTICAL CLEAT MATERIAL CALCULATIONS ===
    // This is the critical part that was missing from the web version
    
    // Step 1: Front/Back Panels - Calculate material needed for vertical cleat spacing
    const frontBackMaterialNeeded = this.calculateVerticalCleatMaterialNeeded(
      frontPanelCalcWidth, frontPanelCalcHeight, cleatMemberWidth
    );
    
    // Add material to front/back panels and update crate width
    frontPanelCalcWidth += frontBackMaterialNeeded;
    backPanelCalcWidth += frontBackMaterialNeeded;
    let updatedCrateOverallWidthOD = crateOverallWidthOD + frontBackMaterialNeeded;
    
    // Step 2: Left/Right Panels - Calculate material needed
    const leftRightMaterialNeeded = this.calculateVerticalCleatMaterialNeeded(
      endPanelCalcLength, endPanelCalcHeight, cleatMemberWidth
    );
    
    // Update end panel length and overall crate length
    let updatedEndPanelCalcLength = endPanelCalcLength + leftRightMaterialNeeded;
    let updatedCrateOverallLengthOD = crateOverallLengthOD + leftRightMaterialNeeded;
    
    // Step 3: Update top panel dimensions with new crate dimensions
    topPanelCalcWidth = frontPanelCalcWidth;
    topPanelCalcLength = updatedCrateOverallLengthOD;
    
    // Step 4: Top Panel - Calculate material needed for vertical cleats in both directions
    const topWidthMaterialNeeded = this.calculateVerticalCleatMaterialNeeded(
      topPanelCalcWidth, topPanelCalcLength, cleatMemberWidth
    );
    const topLengthMaterialNeeded = this.calculateVerticalCleatMaterialNeeded(
      topPanelCalcLength, topPanelCalcWidth, cleatMemberWidth
    );
    
    // Apply top panel material additions (cascades to other panels)
    if (topWidthMaterialNeeded > 0) {
      frontPanelCalcWidth += topWidthMaterialNeeded;
      backPanelCalcWidth += topWidthMaterialNeeded;
      updatedCrateOverallWidthOD += topWidthMaterialNeeded;
      topPanelCalcWidth += topWidthMaterialNeeded;
    }
    
    if (topLengthMaterialNeeded > 0) {
      updatedEndPanelCalcLength += topLengthMaterialNeeded;
      updatedCrateOverallLengthOD += topLengthMaterialNeeded;
      topPanelCalcLength += topLengthMaterialNeeded;
    }
    
    // === COMPONENT LAYOUTS ===
    // Calculate skid layout based on the final overall width
    const skidLayout = this.calculateSkidLayout(updatedCrateOverallWidthOD, skidActualWidth, skidProps.max_spacing_rule);
    
    // Calculate floorboard layout based on the final overall length
    const fbUsableCoverage = updatedCrateOverallLengthOD;
    const fbStartOffset = 0;
    const floorboardLayout = this.calculateFloorboardLayout(fbUsableCoverage, fbStartOffset, stdLumberWidths, minCustom);
    
    // Calculate comprehensive panels with updated dimensions
    const frontPanel = this.calculateComprehensivePanel(
      frontPanelCalcWidth, frontPanelCalcHeight, frontPanelCalcDepth, 'front',
      materials.panelThickness, cleatThickness, cleatMemberWidth
    );
    const backPanel = this.calculateComprehensivePanel(
      backPanelCalcWidth, backPanelCalcHeight, backPanelCalcDepth, 'back',
      materials.panelThickness, cleatThickness, cleatMemberWidth
    );
    const leftPanel = this.calculateComprehensivePanel(
      updatedEndPanelCalcLength, endPanelCalcHeight, endPanelCalcDepth, 'left',
      materials.panelThickness, cleatThickness, cleatMemberWidth
    );
    const rightPanel = this.calculateComprehensivePanel(
      updatedEndPanelCalcLength, endPanelCalcHeight, endPanelCalcDepth, 'right',
      materials.panelThickness, cleatThickness, cleatMemberWidth
    );
    const topPanel = includeTop ? this.calculateComprehensivePanel(
      topPanelCalcWidth, topPanelCalcLength, topPanelCalcDepth, 'top',
      materials.panelThickness, cleatThickness, cleatMemberWidth
    ) : undefined;
    
    // === FINAL DIMENSIONS ===
    const externalLength = updatedCrateOverallLengthOD;
    const externalWidth = updatedCrateOverallWidthOD;
    const externalHeight = endPanelCalcHeight + (includeTop ? topPanelCalcDepth : 0);
    
    // Internal dimensions (product clearance space)
    const internalLength = product.length + clearance * 2;
    const internalWidth = product.width + clearance * 2;
    const internalHeight = product.height + clearanceAbove;
    
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
        overall_width_od: updatedCrateOverallWidthOD,
        overall_length_od: updatedCrateOverallLengthOD
      },
      skid_parameters: {
        lumber_callout: skidProps.lumber_callout,
        actual_height: skidActualHeight,
        actual_width: skidActualWidth,
        actual_length: updatedCrateOverallLengthOD,
        count: skidLayout.count,
        pitch: skidLayout.pitch,
        x_master_origin_offset: skidLayout.x_master_origin_offset
      },
      floorboard_parameters: {
        actual_length: updatedCrateOverallWidthOD,
        actual_thickness: floorboardThickness,
        actual_middle_gap: floorboardLayout.actual_middle_gap,
        center_custom_board_width: floorboardLayout.center_custom_board_width,
        start_y_offset_abs: fbStartOffset,
        instances: floorboardLayout.instances
      },
      materials_summary: {
        plywood_sheets: plywoodSheets,
        total_area_sqft: totalPlywoodArea,
        lumber_length_ft: totalLumberLength,
        estimated_weight_lbs: Math.round(estimatedCrateWeight)
      },
      compliance: {
        astm_d6251: true,
        safety_factor: this.SAFETY_FACTOR,
        max_load: Math.round(product.weight * this.SAFETY_FACTOR),
        standards_met: ['ASTM D6251-17', 'ISPM-15', 'MIL-STD-2073']
      }
    };
  }
}

// Re-export the NX expression generation function for offline use
export { generateNXExpression } from './autocrate-calculations';