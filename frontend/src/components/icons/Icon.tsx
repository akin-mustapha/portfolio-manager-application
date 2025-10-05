import React from 'react';
import { IconWrapper, IconSize, IconVariant, IconAnimation } from './IconWrapper';
import { FinancialIcons, FinancialIconName, getFinancialIcon } from './FinancialIcons';

interface IconProps {
  name: FinancialIconName;
  size?: IconSize;
  variant?: IconVariant;
  animation?: IconAnimation;
  className?: string;
  ariaLabel?: string;
  ariaHidden?: boolean;
  onClick?: () => void;
  disabled?: boolean;
}

export const Icon: React.FC<IconProps> = ({
  name,
  ariaLabel,
  ariaHidden,
  ...props
}) => {
  const IconComponent = getFinancialIcon(name);
  
  // Generate default aria-label if not provided and not hidden
  const defaultAriaLabel = !ariaHidden && !ariaLabel 
    ? name.replace(/([A-Z])/g, ' $1').trim().toLowerCase()
    : ariaLabel;

  return (
    <IconWrapper
      icon={IconComponent}
      ariaLabel={defaultAriaLabel}
      ariaHidden={ariaHidden}
      {...props}
    />
  );
};

// Convenience components for common icon patterns
export const StatusIcon: React.FC<Omit<IconProps, 'name'> & { status: 'success' | 'warning' | 'error' | 'info' }> = ({
  status,
  ...props
}) => {
  const iconMap = {
    success: 'CheckCircle' as const,
    warning: 'AlertTriangle' as const,
    error: 'XCircle' as const,
    info: 'Info' as const,
  };

  const variantMap = {
    success: 'default' as const,
    warning: 'default' as const,
    error: 'default' as const,
    info: 'default' as const,
  };

  return (
    <Icon
      name={iconMap[status]}
      variant={variantMap[status]}
      {...props}
    />
  );
};

export const TrendIcon: React.FC<Omit<IconProps, 'name'> & { trend: 'up' | 'down' | 'neutral' }> = ({
  trend,
  ...props
}) => {
  const iconMap = {
    up: 'TrendingUp' as const,
    down: 'TrendingDown' as const,
    neutral: 'Activity' as const,
  };

  return (
    <Icon
      name={iconMap[trend]}
      {...props}
    />
  );
};

export const ActionIcon: React.FC<Omit<IconProps, 'name'> & { action: 'edit' | 'delete' | 'copy' | 'share' | 'download' }> = ({
  action,
  ...props
}) => {
  const iconMap = {
    edit: 'Edit' as const,
    delete: 'Delete' as const,
    copy: 'Copy' as const,
    share: 'Share' as const,
    download: 'Download' as const,
  };

  return (
    <Icon
      name={iconMap[action]}
      variant="hover"
      animation="scale"
      {...props}
    />
  );
};

export default Icon;