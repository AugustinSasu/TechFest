// Re-export role & tabs from routing to avoid duplication/inconsistencies.
export { ROLES, MANAGER_TABS, SALESMAN_TABS } from '../routing/routePaths';

export const ACHIEVEMENT_TIERS = [
  { id: 'bronze', min: 10000 },
  { id: 'silver', min: 25000 },
  { id: 'gold',   min: 50000 }
];

export const DEFAULT_PAGE_SIZE = 10;

export const CHAT_AUTHORS = {
  USER: 'user',
  AI: 'ai'
};
