import React from 'react';
import { Box, Divider, Drawer, List, ListItemButton, ListItemText, Toolbar, Typography } from '@mui/material';
import { useAuth } from '../../providers/AuthProvider';
import { MANAGER_TABS, SALESMAN_TABS, ROUTES } from '../../routing/routePaths';
import { useLocation, useNavigate, useSearchParams } from 'react-router-dom';

function buildItems(role) {
  const tabs = role === 'manager' ? MANAGER_TABS : SALESMAN_TABS;
  return tabs.map(key => ({ key, label: key.charAt(0).toUpperCase() + key.slice(1) }));
}

export default function AppSideNav({ open, onClose, width = 240, variant = 'temporary' }) {
  const { role } = useAuth() || {};
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const location = useLocation();

  const basePath = role === 'manager' ? ROUTES.MANAGER : ROUTES.SALES;
  const currentTab = params.get('tab') || (role === 'manager' ? MANAGER_TABS[0] : SALESMAN_TABS[0]);
  const items = buildItems(role);

  const go = (tabKey) => {
    const search = new URLSearchParams({ tab: tabKey });
    navigate(`${basePath}?${search.toString()}`, { replace: location.pathname.startsWith(basePath) });
    onClose?.();
  };

  const content = (
    <Box sx={{ width }}>
      <Toolbar>
        <Typography variant="subtitle2" color="text.secondary">
          {role === 'manager' ? 'Manager' : 'Sales'} Panels
        </Typography>
      </Toolbar>
      <Divider />
      <List>
        {items.map(it => (
          <ListItemButton key={it.key} selected={currentTab === it.key} onClick={() => go(it.key)}>
            <ListItemText primary={it.label} />
          </ListItemButton>
        ))}
      </List>
    </Box>
  );

  return (
    <Drawer
      variant={variant}
      open={variant === 'temporary' ? open : true}
      onClose={onClose}
      ModalProps={{ keepMounted: true }}
    >
      {content}
    </Drawer>
  );
}
