import React, { createContext, useContext, useMemo, useState } from 'react';
import { ThemeProvider as MuiThemeProvider, createTheme, CssBaseline, GlobalStyles } from '@mui/material';
import getTheme from '../theme';

const ColorModeContext = createContext({ mode: 'light', toggleColorMode: () => {} });

/**
 * App-level Theme provider (MUI)
 * - fără fișiere CSS: reset + globale prin CssBaseline/GlobalStyles
 * - dark/light toggle prin context
 * - folosește sursa unică de adevăr din folderul `theme/`
 */
export function ThemeProvider({ children }) {
  const [mode, setMode] = useState('light');
  const toggleColorMode = () => setMode(m => (m === 'light' ? 'dark' : 'light'));

  const theme = useMemo(() => createTheme(getTheme(mode)), [mode]);

  return (
    <ColorModeContext.Provider value={{ mode, toggleColorMode }}>
      <MuiThemeProvider theme={theme}>
        <CssBaseline />
        <GlobalStyles
          styles={{
            'html, body, #root': { height: '100%' },
            '*, *::before, *::after': { boxSizing: 'border-box' },
            img: { maxWidth: '100%', display: 'block' }
          }}
        />
        {children}
      </MuiThemeProvider>
    </ColorModeContext.Provider>
  );
}

export const useColorMode = () => useContext(ColorModeContext);
