import getPalette from './palette';
import typography from './typography';
import componentsOverride from './componentsOverride';

/**
 * Returns the MUI theme options for the given mode.
 * Usage with ThemeProvider: createTheme(getTheme(mode))
 */
export default function getTheme(mode = 'light') {
  return {
    palette: getPalette(mode),
    typography,
    shape: { borderRadius: 12 },
    components: componentsOverride()
  };
}

// Optional: if you prefer to build the full theme object here
// import { createTheme } from '@mui/material/styles';
// export function buildTheme(mode = 'light') {
//   return createTheme(getTheme(mode));
// }
