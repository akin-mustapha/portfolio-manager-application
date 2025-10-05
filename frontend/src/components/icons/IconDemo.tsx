import React from 'react';
import { Icon, StatusIcon, TrendIcon, ActionIcon, IconCategories, FinancialIconName } from './index';

export const IconDemo: React.FC = () => {
  return (
    <div className="p-8 space-y-8">
      <div>
        <h2 className="text-2xl font-bold mb-4">Icon System Demo</h2>
        <p className="text-gray-600 mb-6">
          Comprehensive icon system with Lucide React, featuring consistent sizing, animations, and accessibility.
        </p>
      </div>

      {/* Size Variants */}
      <div>
        <h3 className="text-lg font-semibold mb-3">Size Variants</h3>
        <div className="flex items-center gap-4">
          <Icon name="DollarSign" size="xs" />
          <Icon name="DollarSign" size="sm" />
          <Icon name="DollarSign" size="md" />
          <Icon name="DollarSign" size="lg" />
          <Icon name="DollarSign" size="xl" />
          <Icon name="DollarSign" size="2xl" />
        </div>
      </div>

      {/* Animation Variants */}
      <div>
        <h3 className="text-lg font-semibold mb-3">Animation Variants</h3>
        <div className="flex items-center gap-6">
          <div className="text-center">
            <Icon name="Refresh" animation="spin" size="lg" />
            <p className="text-sm mt-1">Spin</p>
          </div>
          <div className="text-center">
            <Icon name="Heart" animation="pulse" size="lg" />
            <p className="text-sm mt-1">Pulse</p>
          </div>
          <div className="text-center">
            <Icon name="ArrowUp" animation="bounce" size="lg" />
            <p className="text-sm mt-1">Bounce</p>
          </div>
          <div className="text-center">
            <Icon name="Settings" animation="rotate" size="lg" />
            <p className="text-sm mt-1">Rotate (hover)</p>
          </div>
          <div className="text-center">
            <Icon name="Star" animation="scale" size="lg" />
            <p className="text-sm mt-1">Scale (hover)</p>
          </div>
          <div className="text-center">
            <Icon name="Eye" animation="fade" size="lg" />
            <p className="text-sm mt-1">Fade</p>
          </div>
        </div>
      </div>

      {/* Convenience Components */}
      <div>
        <h3 className="text-lg font-semibold mb-3">Convenience Components</h3>
        <div className="space-y-4">
          <div>
            <h4 className="font-medium mb-2">Status Icons</h4>
            <div className="flex items-center gap-4">
              <StatusIcon status="success" size="lg" />
              <StatusIcon status="warning" size="lg" />
              <StatusIcon status="error" size="lg" />
              <StatusIcon status="info" size="lg" />
            </div>
          </div>
          
          <div>
            <h4 className="font-medium mb-2">Trend Icons</h4>
            <div className="flex items-center gap-4">
              <TrendIcon trend="up" size="lg" className="text-green-500" />
              <TrendIcon trend="down" size="lg" className="text-red-500" />
              <TrendIcon trend="neutral" size="lg" className="text-gray-500" />
            </div>
          </div>
          
          <div>
            <h4 className="font-medium mb-2">Action Icons</h4>
            <div className="flex items-center gap-4">
              <ActionIcon action="edit" size="lg" />
              <ActionIcon action="delete" size="lg" />
              <ActionIcon action="copy" size="lg" />
              <ActionIcon action="share" size="lg" />
              <ActionIcon action="download" size="lg" />
            </div>
          </div>
        </div>
      </div>

      {/* Icon Categories */}
      <div>
        <h3 className="text-lg font-semibold mb-3">Icon Categories</h3>
        {Object.entries(IconCategories).map(([category, icons]) => (
          <div key={category} className="mb-4">
            <h4 className="font-medium mb-2 capitalize">{category}</h4>
            <div className="flex flex-wrap gap-3">
              {icons.map((iconName) => (
                <div key={iconName} className="text-center">
                  <Icon 
                    name={iconName as FinancialIconName} 
                    size="lg" 
                    animation="scale"
                    className="mx-auto"
                  />
                  <p className="text-xs mt-1 max-w-16 truncate">{iconName}</p>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Interactive Examples */}
      <div>
        <h3 className="text-lg font-semibold mb-3">Interactive Examples</h3>
        <div className="flex gap-4">
          <button className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors">
            <Icon name="Download" size="sm" animation="scale" />
            Download
          </button>
          <button className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded hover:bg-gray-50 transition-colors">
            <Icon name="Share" size="sm" animation="scale" />
            Share
          </button>
          <button className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded hover:bg-gray-50 transition-colors">
            <Icon name="Refresh" size="sm" animation="spin" />
            Refresh
          </button>
        </div>
      </div>

      {/* Accessibility Example */}
      <div>
        <h3 className="text-lg font-semibold mb-3">Accessibility Features</h3>
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <Icon name="CheckCircle" size="sm" ariaLabel="Success: Data loaded successfully" />
            <span>Icon with custom aria-label</span>
          </div>
          <div className="flex items-center gap-2">
            <Icon name="Star" size="sm" ariaHidden={true} />
            <span>Decorative icon (aria-hidden)</span>
          </div>
          <div className="flex items-center gap-2">
            <Icon name="TrendingUp" size="sm" />
            <span>Icon with auto-generated aria-label</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IconDemo;