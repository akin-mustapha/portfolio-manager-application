# Icon System Documentation

A comprehensive icon system built with Lucide React, featuring consistent sizing, animations, and accessibility support for the Trading 212 Portfolio Dashboard.

## Features

- 🎨 **Consistent Design**: Unified sizing, colors, and styling across all icons
- ⚡ **Smooth Animations**: Built-in animation support with Framer Motion
- ♿ **Accessibility First**: Proper ARIA labels and screen reader support
- 🎯 **Type Safe**: Full TypeScript support with intelligent autocomplete
- 📦 **Tree Shakeable**: Only import the icons you need
- 🧩 **Modular**: Organized by categories for easy discovery

## Quick Start

```tsx
import { Icon, StatusIcon, TrendIcon, ActionIcon } from './components/icons';

// Basic usage
<Icon name="DollarSign" size="lg" />

// With animation
<Icon name="Refresh" animation="spin" />

// Convenience components
<StatusIcon status="success" />
<TrendIcon trend="up" className="text-green-500" />
<ActionIcon action="edit" onClick={handleEdit} />
```

## Components

### Icon

The main icon component that renders any icon from the FinancialIcons collection.

```tsx
interface IconProps {
  name: FinancialIconName;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';
  variant?: 'default' | 'hover' | 'active' | 'disabled';
  animation?: 'none' | 'spin' | 'pulse' | 'bounce' | 'rotate' | 'scale' | 'fade';
  className?: string;
  ariaLabel?: string;
  ariaHidden?: boolean;
  onClick?: () => void;
  disabled?: boolean;
}
```

**Examples:**

```tsx
// Basic icon
<Icon name="TrendingUp" />

// Large icon with custom color
<Icon name="DollarSign" size="xl" className="text-green-500" />

// Interactive icon with hover animation
<Icon 
  name="Settings" 
  animation="rotate" 
  onClick={openSettings}
  ariaLabel="Open settings menu"
/>

// Disabled state
<Icon name="Download" disabled />
```

### StatusIcon

Convenience component for status indicators.

```tsx
interface StatusIconProps {
  status: 'success' | 'warning' | 'error' | 'info';
  size?: IconSize;
  className?: string;
}
```

**Examples:**

```tsx
<StatusIcon status="success" />
<StatusIcon status="error" size="lg" />
<StatusIcon status="warning" className="text-yellow-600" />
```

### TrendIcon

Specialized component for showing trends and performance.

```tsx
interface TrendIconProps {
  trend: 'up' | 'down' | 'neutral';
  size?: IconSize;
  className?: string;
}
```

**Examples:**

```tsx
<TrendIcon trend="up" className="text-green-500" />
<TrendIcon trend="down" className="text-red-500" />
<TrendIcon trend="neutral" className="text-gray-500" />
```

### ActionIcon

Interactive icons for common actions with built-in hover effects.

```tsx
interface ActionIconProps {
  action: 'edit' | 'delete' | 'copy' | 'share' | 'download';
  size?: IconSize;
  onClick?: () => void;
  className?: string;
}
```

**Examples:**

```tsx
<ActionIcon action="edit" onClick={handleEdit} />
<ActionIcon action="delete" onClick={handleDelete} />
<ActionIcon action="share" onClick={handleShare} />
```

## Available Icons

### Performance & Trends
- `TrendingUp` - Upward trend indicator
- `TrendingDown` - Downward trend indicator  
- `Activity` - General activity/volatility
- `BarChart` - Bar chart visualization
- `PieChart` - Pie chart visualization
- `LineChart` - Line chart visualization
- `Growth` - Growth indicator

### Financial
- `DollarSign` - Currency symbol
- `Percent` - Percentage symbol
- `Calculator` - Calculations
- `Target` - Goals and targets
- `Coins` - Multiple currencies
- `CreditCard` - Payment methods
- `Banknote` - Cash/money

### UI Controls
- `Play` - Play/start actions
- `X` - Close/cancel
- `Menu` - Navigation menu
- `Settings` - Configuration
- `Refresh` - Refresh/reload
- `Eye` - Show/visible
- `EyeOff` - Hide/invisible
- `ChevronUp/Down/Left/Right` - Directional navigation

### Status & Alerts
- `CheckCircle` - Success states
- `AlertTriangle` - Warning states
- `AlertCircle` - Error states
- `Info` - Information
- `XCircle` - Failed states
- `Clock` - Time/pending states

## Sizes

| Size | Dimensions | Use Case |
|------|------------|----------|
| `xs` | 12px × 12px | Small inline icons |
| `sm` | 16px × 16px | Button icons, form elements |
| `md` | 20px × 20px | Default size, general use |
| `lg` | 24px × 24px | Prominent icons, headers |
| `xl` | 32px × 32px | Large feature icons |
| `2xl` | 40px × 40px | Hero icons, empty states |

## Animations

### Built-in Animations

- `none` - No animation (default)
- `spin` - Continuous rotation (loading states)
- `pulse` - Scale pulsing effect
- `bounce` - Vertical bouncing
- `rotate` - Hover rotation effect
- `scale` - Hover scale effect
- `fade` - Fade in animation

### Animation Examples

```tsx
// Loading spinner
<Icon name="Refresh" animation="spin" />

// Attention-grabbing pulse
<Icon name="Bell" animation="pulse" />

// Interactive hover effects
<Icon name="Star" animation="scale" />
<Icon name="Settings" animation="rotate" />
```

## Accessibility

The icon system includes comprehensive accessibility features:

### Automatic ARIA Labels
Icons automatically generate ARIA labels from their names:
```tsx
<Icon name="TrendingUp" />
// Generates: aria-label="trending up"
```

### Custom ARIA Labels
```tsx
<Icon name="Settings" ariaLabel="Open user preferences" />
```

### Decorative Icons
```tsx
<Icon name="Star" ariaHidden={true} />
```

### Screen Reader Support
All icons include proper semantic markup and can be hidden from screen readers when used decoratively.

## Styling

### CSS Classes
Icons inherit text color by default and can be styled with Tailwind classes:

```tsx
<Icon name="DollarSign" className="text-green-500 hover:text-green-600" />
```

### Size Classes
Each size applies consistent width and height classes:
- `xs`: `w-3 h-3`
- `sm`: `w-4 h-4`
- `md`: `w-5 h-5`
- `lg`: `w-6 h-6`
- `xl`: `w-8 h-8`
- `2xl`: `w-10 h-10`

### Variants
- `default`: Standard appearance
- `hover`: Includes hover state transitions
- `active`: Active/selected state
- `disabled`: Disabled appearance with reduced opacity

## Performance

### Tree Shaking
Only imported icons are included in the bundle:

```tsx
// ✅ Good - only imports needed icons
import { TrendingUp, DollarSign } from 'lucide-react';

// ❌ Avoid - imports entire icon library
import * as Icons from 'lucide-react';
```

### Animation Performance
- Animations use CSS transforms for optimal performance
- Respects `prefers-reduced-motion` for accessibility
- Animations are disabled in test environments

## Testing

The icon system includes comprehensive tests covering:
- Component rendering
- Prop handling
- Accessibility features
- Animation states
- Error handling

Run tests with:
```bash
npm test -- --testPathPattern=Icon.test.tsx
```

## Migration Guide

### From Raw Lucide Icons

**Before:**
```tsx
import { TrendingUp } from 'lucide-react';

<TrendingUp className="w-5 h-5 text-green-500" />
```

**After:**
```tsx
import { Icon } from './components/icons';

<Icon name="TrendingUp" className="text-green-500" />
```

### Benefits of Migration
- Consistent sizing across the application
- Built-in accessibility features
- Animation support
- Type safety with icon names
- Better testing support

## Best Practices

### Do's ✅
- Use semantic icon names that match their purpose
- Provide custom `ariaLabel` for complex actions
- Use appropriate sizes for context
- Leverage convenience components when available
- Test with screen readers

### Don'ts ❌
- Don't use icons without proper labels for interactive elements
- Don't override size classes manually
- Don't use animations excessively
- Don't forget to handle loading states
- Don't ignore accessibility warnings

## Contributing

When adding new icons:

1. Add the icon to `FinancialIcons.ts`
2. Update the appropriate category in `IconCategories`
3. Add TypeScript types
4. Include in tests
5. Update documentation

## Browser Support

- Modern browsers with ES6+ support
- Graceful degradation for older browsers
- Respects user motion preferences
- Works with screen readers

## Dependencies

- `lucide-react`: Icon library
- `framer-motion`: Animation support
- `clsx`: Utility for conditional classes
- `react`: React framework