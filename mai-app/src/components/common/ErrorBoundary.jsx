import React from 'react';
import { Box, Button, Container, Paper, Typography } from '@mui/material';

/**
 * Single class-based component in the app: an error boundary.
 */
export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  componentDidCatch(error, info) {
    // eslint-disable-next-line no-console
    console.error('ErrorBoundary caught error:', error, info);
  }
  handleReload = () => {
    // simple reset; for more advanced you could keep a "reset key" prop
    window.location.reload();
  };
  render() {
    if (!this.state.hasError) return this.props.children;
    return (
      <Container maxWidth="sm" sx={{ py: 8 }}>
        <Paper sx={{ p: 4, borderRadius: 3 }}>
          <Typography variant="h5" gutterBottom>Something went wrong</Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {this.state.error?.message || 'An unexpected error occurred.'}
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button variant="contained" onClick={this.handleReload}>Reload</Button>
          </Box>
        </Paper>
      </Container>
    );
  }
}
