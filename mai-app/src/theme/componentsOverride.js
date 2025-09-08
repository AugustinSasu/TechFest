/**
 * Static component overrides that don't depend on the runtime theme object.
 * If later you need theme-aware overrides, export a function (theme) => ({...})
 */
export default function componentsOverride() {
  return {
    MuiButton: {
      styleOverrides: {
        root: { textTransform: 'none', fontWeight: 600, borderRadius: 12 }
      }
    },
    MuiPaper: {
      defaultProps: { elevation: 0 },
      styleOverrides: { root: { borderRadius: 12 } }
    }
  };
}
