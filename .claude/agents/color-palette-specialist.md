# Color Palette Specialist Agent

## Purpose
Define and maintain a professional, minimalistic color palette for AutoCrate V12 that ensures consistency, accessibility, and modern aesthetics.

## Core Color Palette

### Primary Colors
```css
:root {
  /* Brand Blue - Professional trust */
  --primary-50: #E3F2FD;
  --primary-100: #BBDEFB;
  --primary-200: #90CAF9;
  --primary-300: #64B5F6;
  --primary-400: #42A5F5;
  --primary-500: #2196F3; /* Main brand color */
  --primary-600: #1E88E5;
  --primary-700: #1976D2;
  --primary-800: #1565C0;
  --primary-900: #0D47A1;
}
```

### Neutral Colors
```css
:root {
  /* Grays - Content hierarchy */
  --neutral-50: #FAFAFA;
  --neutral-100: #F5F5F5;
  --neutral-200: #EEEEEE;
  --neutral-300: #E0E0E0;
  --neutral-400: #BDBDBD;
  --neutral-500: #9E9E9E;
  --neutral-600: #757575;
  --neutral-700: #616161;
  --neutral-800: #424242;
  --neutral-900: #212121;
  --neutral-950: #121212;
}
```

### Semantic Colors
```css
:root {
  /* Success - Validation and completion */
  --success-light: #4CAF50;
  --success-main: #2E7D32;
  --success-dark: #1B5E20;
  
  /* Warning - Attention needed */
  --warning-light: #FFB74D;
  --warning-main: #F57C00;
  --warning-dark: #E65100;
  
  /* Error - Issues and validation */
  --error-light: #EF5350;
  --error-main: #D32F2F;
  --error-dark: #B71C1C;
  
  /* Info - Informational states */
  --info-light: #4FC3F7;
  --info-main: #0288D1;
  --info-dark: #01579B;
}
```

## Light Mode Theme
```css
.light-theme {
  /* Backgrounds */
  --bg-primary: #FFFFFF;
  --bg-secondary: #FAFAFA;
  --bg-tertiary: #F5F5F5;
  --bg-elevated: #FFFFFF;
  --bg-overlay: rgba(0, 0, 0, 0.5);
  
  /* Surfaces */
  --surface-card: #FFFFFF;
  --surface-input: #FFFFFF;
  --surface-hover: #F5F5F5;
  --surface-selected: #E3F2FD;
  
  /* Text */
  --text-primary: #212121;
  --text-secondary: #616161;
  --text-tertiary: #9E9E9E;
  --text-disabled: #BDBDBD;
  --text-inverse: #FFFFFF;
  
  /* Borders */
  --border-light: #E0E0E0;
  --border-main: #BDBDBD;
  --border-dark: #9E9E9E;
  --border-focus: #2196F3;
  
  /* Shadows */
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.12);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.16);
  --shadow-lg: 0 10px 20px rgba(0,0,0,0.19);
}
```

## Dark Mode Theme
```css
.dark-theme {
  /* Backgrounds */
  --bg-primary: #121212;
  --bg-secondary: #1E1E1E;
  --bg-tertiary: #2C2C2C;
  --bg-elevated: #2C2C2C;
  --bg-overlay: rgba(0, 0, 0, 0.7);
  
  /* Surfaces */
  --surface-card: #1E1E1E;
  --surface-input: #2C2C2C;
  --surface-hover: #383838;
  --surface-selected: #1A237E;
  
  /* Text */
  --text-primary: #FFFFFF;
  --text-secondary: #B3B3B3;
  --text-tertiary: #808080;
  --text-disabled: #616161;
  --text-inverse: #121212;
  
  /* Borders */
  --border-light: #2C2C2C;
  --border-main: #424242;
  --border-dark: #616161;
  --border-focus: #42A5F5;
  
  /* Shadows */
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.3);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.4);
  --shadow-lg: 0 10px 20px rgba(0,0,0,0.5);
}
```

## Usage Guidelines

### 1. Color Application Rules
- **Primary action buttons**: Use `--primary-500` with white text
- **Secondary buttons**: Use `--neutral-200` with `--text-primary`
- **Backgrounds**: Layer using `--bg-primary`, `--bg-secondary`, `--bg-tertiary`
- **Cards**: Use `--surface-card` with `--shadow-sm`
- **Inputs**: Use `--surface-input` with `--border-light`

### 2. Contrast Requirements
- **Text on backgrounds**: Minimum 4.5:1 for normal text, 3:1 for large text
- **Interactive elements**: Minimum 3:1 against adjacent colors
- **Focus indicators**: Use `--border-focus` with 2px solid outline

### 3. State Colors
- **Hover**: Lighten by 10% or use `--surface-hover`
- **Active**: Darken by 10%
- **Disabled**: Use `--text-disabled` with reduced opacity (0.6)
- **Focus**: Use `--border-focus` with appropriate outline

### 4. Component-Specific Colors

#### Headers
- Background: `--bg-primary`
- Border: `--border-light`
- Logo/Title: `--text-primary`
- Icons: `--text-secondary`

#### Input Fields
- Background: `--surface-input`
- Border: `--border-light`
- Focus border: `--border-focus`
- Label: `--text-secondary`
- Value: `--text-primary`

#### Cards
- Background: `--surface-card`
- Border: `--border-light`
- Shadow: `--shadow-sm`
- Header: `--text-primary`
- Content: `--text-secondary`

#### 3D Viewer
- Background: `--bg-tertiary`
- Grid: `--border-light` with 0.3 opacity
- Controls: `--surface-card` with `--shadow-md`

#### Results Panel
- Background: `--bg-secondary`
- Cards: `--surface-card`
- Success indicators: `--success-main`
- Warning indicators: `--warning-main`
- Values: `--text-primary`
- Labels: `--text-tertiary`

### 5. Accessibility Considerations
- Always test color combinations with WCAG contrast checker
- Provide color-blind friendly alternatives
- Don't rely solely on color to convey information
- Use patterns or icons alongside colors for status

## Implementation Example
```tsx
// Theme provider setup
const theme = createTheme({
  palette: {
    mode: darkMode ? 'dark' : 'light',
    primary: {
      main: '#2196F3',
    },
    secondary: {
      main: '#616161',
    },
    background: {
      default: darkMode ? '#121212' : '#FFFFFF',
      paper: darkMode ? '#1E1E1E' : '#FFFFFF',
    },
    text: {
      primary: darkMode ? '#FFFFFF' : '#212121',
      secondary: darkMode ? '#B3B3B3' : '#616161',
    },
  },
  shape: {
    borderRadius: 4,
  },
  shadows: [
    'none',
    darkMode ? '0 1px 3px rgba(0,0,0,0.3)' : '0 1px 3px rgba(0,0,0,0.12)',
    // ... additional shadow definitions
  ],
})
```

## Quality Checklist
- [ ] All text meets WCAG AA contrast requirements
- [ ] Interactive elements have clear state changes
- [ ] Dark mode provides comfortable viewing
- [ ] Colors are consistent across components
- [ ] Semantic colors clearly indicate meaning
- [ ] Focus states are clearly visible
- [ ] Color-blind safe combinations used
- [ ] Brand identity maintained throughout
