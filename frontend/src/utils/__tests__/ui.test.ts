import {
  cn,
  createCardStyles,
  createButtonStyles,
  createSkeletonStyles,
  getMotionPreference,
} from '../ui';

// Mock window.matchMedia for testing
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

describe('UI Utilities', () => {
  describe('cn function', () => {
    it('should combine class names correctly', () => {
      const result = cn('class1', 'class2', 'class3');
      expect(result).toBe('class1 class2 class3');
    });

    it('should handle conditional classes', () => {
      const result = cn('base', true && 'conditional', false && 'hidden');
      expect(result).toBe('base conditional');
    });

    it('should handle undefined and null values', () => {
      const result = cn('base', undefined, null, 'valid');
      expect(result).toBe('base valid');
    });
  });

  describe('createCardStyles', () => {
    it('should create glass card styles by default', () => {
      const styles = createCardStyles();
      expect(styles).toContain('rounded-xl');
      expect(styles).toContain('p-6');
      expect(styles).toContain('transition-all');
      expect(styles).toContain('backdrop-blur');
    });

    it('should create solid card styles', () => {
      const styles = createCardStyles('solid');
      expect(styles).toContain('bg-white');
      expect(styles).toContain('dark:bg-gray-800');
      expect(styles).toContain('shadow-medium');
    });

    it('should create gradient card styles', () => {
      const styles = createCardStyles('gradient');
      expect(styles).toContain('bg-glass-gradient');
      expect(styles).toContain('shadow-glass');
    });
  });

  describe('createButtonStyles', () => {
    it('should create primary button styles by default', () => {
      const styles = createButtonStyles();
      expect(styles).toContain('bg-primary-600');
      expect(styles).toContain('text-white');
      expect(styles).toContain('px-4');
      expect(styles).toContain('py-2');
    });

    it('should create secondary button styles', () => {
      const styles = createButtonStyles('secondary');
      expect(styles).toContain('bg-white/10');
      expect(styles).toContain('border');
    });

    it('should create small button styles', () => {
      const styles = createButtonStyles('primary', 'sm');
      expect(styles).toContain('px-3');
      expect(styles).toContain('py-1.5');
      expect(styles).toContain('text-sm');
    });

    it('should create large button styles', () => {
      const styles = createButtonStyles('primary', 'lg');
      expect(styles).toContain('px-6');
      expect(styles).toContain('py-3');
      expect(styles).toContain('text-lg');
    });
  });

  describe('createSkeletonStyles', () => {
    it('should create skeleton styles with shimmer animation', () => {
      const styles = createSkeletonStyles();
      expect(styles).toContain('animate-shimmer');
      expect(styles).toContain('bg-gray-200');
      expect(styles).toContain('dark:bg-gray-700');
    });

    it('should accept custom className', () => {
      const styles = createSkeletonStyles('custom-class');
      expect(styles).toContain('custom-class');
      expect(styles).toContain('animate-shimmer');
    });
  });

  describe('getMotionPreference', () => {
    it('should return false when prefers-reduced-motion is not set', () => {
      // Reset the mock to return false
      (window.matchMedia as jest.Mock).mockImplementation(query => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: jest.fn(),
        removeListener: jest.fn(),
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        dispatchEvent: jest.fn(),
      }));

      const result = getMotionPreference();
      expect(result).toBe(false);
    });

    it('should return true when prefers-reduced-motion is set', () => {
      // Mock matchMedia to return true for reduced motion
      (window.matchMedia as jest.Mock).mockImplementation(query => ({
        matches: query === '(prefers-reduced-motion: reduce)',
        media: query,
        onchange: null,
        addListener: jest.fn(),
        removeListener: jest.fn(),
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        dispatchEvent: jest.fn(),
      }));

      const result = getMotionPreference();
      expect(result).toBe(true);
    });
  });
});