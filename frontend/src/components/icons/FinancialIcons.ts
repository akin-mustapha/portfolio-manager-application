import {
  // Performance & Trends
  TrendingUp,
  TrendingDown,
  Activity,
  BarChart,
  PieChart,
  LineChart,
  
  // Financial
  DollarSign,
  Percent,
  Calculator,
  Target,
  Coins,
  CreditCard,
  Banknote,
  
  // UI Controls
  Play,
  X,
  Menu,
  Settings,
  RefreshCw,
  Eye,
  EyeOff,
  ChevronUp,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  MoreHorizontal,
  MoreVertical,
  
  // Status & Alerts
  CheckCircle,
  AlertTriangle,
  Info,
  AlertCircle,
  XCircle,
  Clock,
  
  // Navigation & Actions
  Home,
  Search,
  Filter,
  Download,
  Upload,
  Share,
  Copy,
  Edit,
  Trash2,
  Plus,
  Minus,
  
  // Data & Analytics
  Database,
  BarChart3,
  BarChart4,
  TrendingUp as Growth,
  Calendar,
  Clock as Time,
  
  // User & Account
  User,
  Users,
  UserCheck,
  Shield,
  Lock,
  Unlock,
  Key,
  
  // Communication
  Mail,
  Bell,
  MessageSquare,
  Phone,
  
  // System
  Wifi,
  WifiOff,
  Power,
  Zap,
  Globe,
  Server,
  
  // Arrows & Directions
  ArrowUp,
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  ArrowUpRight,
  ArrowDownRight,
  
  // Shapes & Symbols
  Circle,
  Square,
  Triangle,
  Star,
  Heart,
  Bookmark,
  
  type LucideIcon,
} from 'lucide-react';

// Financial Dashboard Icon Mapping
export const FinancialIcons = {
  // Performance & Trends
  TrendingUp,
  TrendingDown,
  Activity,
  BarChart,
  PieChart,
  LineChart,
  Growth,
  
  // Financial
  DollarSign,
  Percent,
  Calculator,
  Target,
  Coins,
  CreditCard,
  Banknote,
  
  // UI Controls (matching design system)
  Play,
  X,
  Menu,
  Settings,
  Refresh: RefreshCw,
  Eye,
  EyeOff,
  ChevronUp,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  MoreHorizontal,
  MoreVertical,
  
  // Status & Alerts
  CheckCircle,
  AlertTriangle,
  Info,
  AlertCircle,
  XCircle,
  Clock,
  
  // Navigation & Actions
  Home,
  Search,
  Filter,
  Download,
  Upload,
  Share,
  Copy,
  Edit,
  Delete: Trash2,
  Plus,
  Minus,
  
  // Data & Analytics
  Database,
  BarChart3,
  BarChart4,
  Calendar,
  Time,
  
  // User & Account
  User,
  Users,
  UserCheck,
  Shield,
  Lock,
  Unlock,
  Key,
  
  // Communication
  Mail,
  Bell,
  MessageSquare,
  Phone,
  
  // System
  Wifi,
  WifiOff,
  Power,
  Zap,
  Globe,
  Server,
  
  // Arrows & Directions
  ArrowUp,
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  ArrowUpRight,
  ArrowDownRight,
  
  // Shapes & Symbols
  Circle,
  Square,
  Triangle,
  Star,
  Heart,
  Bookmark,
} as const;

export type FinancialIconName = keyof typeof FinancialIcons;
export type FinancialIconType = LucideIcon;

// Icon categories for easier organization
export const IconCategories = {
  performance: [
    'TrendingUp',
    'TrendingDown',
    'Activity',
    'BarChart',
    'PieChart',
    'LineChart',
    'Growth',
  ] as FinancialIconName[],
  
  financial: [
    'DollarSign',
    'Percent',
    'Calculator',
    'Target',
    'Coins',
    'CreditCard',
    'Banknote',
  ] as FinancialIconName[],
  
  controls: [
    'Play',
    'X',
    'Menu',
    'Settings',
    'Refresh',
    'Eye',
    'EyeOff',
  ] as FinancialIconName[],
  
  status: [
    'CheckCircle',
    'AlertTriangle',
    'Info',
    'AlertCircle',
    'XCircle',
    'Clock',
  ] as FinancialIconName[],
  
  navigation: [
    'Home',
    'Search',
    'Filter',
    'ChevronUp',
    'ChevronDown',
    'ChevronLeft',
    'ChevronRight',
  ] as FinancialIconName[],
  
  actions: [
    'Download',
    'Upload',
    'Share',
    'Copy',
    'Edit',
    'Delete',
    'Plus',
    'Minus',
  ] as FinancialIconName[],
};

// Helper function to get icon by name
export const getFinancialIcon = (name: FinancialIconName): LucideIcon => {
  return FinancialIcons[name];
};

// Helper function to check if icon exists
export const hasFinancialIcon = (name: string): name is FinancialIconName => {
  return name in FinancialIcons;
};

export default FinancialIcons;