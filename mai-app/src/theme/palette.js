export const lightPalette = {
  mode: 'light',
  primary: { main: '#1976d2' },
  secondary: { main: '#9c27b0' },
  background: { default: '#fafafa', paper: '#fff' }
};

export const darkPalette = {
  mode: 'dark',
  primary: { main: '#90caf9' },
  secondary: { main: '#ce93d8' },
  background: { default: '#0f1115', paper: '#12151b' }
};

export default function getPalette(mode = 'light') {
  return mode === 'dark' ? darkPalette : lightPalette;
}
