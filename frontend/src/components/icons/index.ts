// Main components
export { default as Icon, StatusIcon, TrendIcon, ActionIcon } from './Icon';
export { default as IconWrapper } from './IconWrapper';

// Icon mapping and utilities
export {
  FinancialIcons,
  IconCategories,
  getFinancialIcon,
  hasFinancialIcon,
  type FinancialIconName,
  type FinancialIconType,
} from './FinancialIcons';

// Types
export type {
  IconSize,
  IconVariant,
  IconAnimation,
} from './IconWrapper';

// Re-export commonly used icons for convenience
export {
  TrendingUp,
  TrendingDown,
  DollarSign,
  PieChart,
  BarChart,
  Activity,
  AlertTriangle,
  CheckCircle,
  X,
  Menu,
  Settings,
  RefreshCw as Refresh,
  Eye,
  EyeOff,
} from 'lucide-react';