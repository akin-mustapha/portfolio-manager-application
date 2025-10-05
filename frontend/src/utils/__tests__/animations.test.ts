import {
  getAnimationVariants,
  getTransition,
  createStaggerContainer,
  springTransition,
  smoothTransition,
  bounceTransition,
} from '../animations';

describe('Animation Utilities', () => {
  describe('getAnimationVariants', () => {
    it('should return fade variants for fade style', () => {
      const variants = getAnimationVariants('fade');
      expect(variants.initial).toEqual({ opacity: 0 });
      expect(variants.animate).toEqual({ opacity: 1 });
      expect(variants.exit).toEqual({ opacity: 0 });
    });

    it('should return slide up variants for from-bottom style', () => {
      const variants = getAnimationVariants('from-bottom');
      expect(variants.initial).toEqual({ opacity: 0, y: 20 });
      expect(variants.animate).toEqual({ opacity: 1, y: 0 });
      expect(variants.exit).toEqual({ opacity: 0, y: -20 });
    });

    it('should return scale variants for scale style', () => {
      const variants = getAnimationVariants('scale');
      expect(variants.initial).toEqual({ opacity: 0, scale: 0.9 });
      expect(variants.animate).toEqual({ opacity: 1, scale: 1 });
      expect(variants.exit).toEqual({ opacity: 0, scale: 0.95 });
    });
  });

  describe('getTransition', () => {
    it('should return bounce transition for bounce style', () => {
      const transition = getTransition('bounce');
      expect(transition).toEqual(bounceTransition);
    });

    it('should return spring transition for scale style', () => {
      const transition = getTransition('scale');
      expect(transition).toEqual(springTransition);
    });

    it('should return smooth transition for default styles', () => {
      const transition = getTransition('fade');
      expect(transition).toEqual(smoothTransition);
    });
  });

  describe('createStaggerContainer', () => {
    it('should create stagger container with default values', () => {
      const container = createStaggerContainer();
      expect(container.animate.transition.staggerChildren).toBe(0.1);
      expect(container.animate.transition.delayChildren).toBe(0.1);
    });

    it('should create stagger container with custom values', () => {
      const container = createStaggerContainer(0.2, 0.3);
      expect(container.animate.transition.staggerChildren).toBe(0.2);
      expect(container.animate.transition.delayChildren).toBe(0.3);
    });
  });

  describe('transition configurations', () => {
    it('should have correct spring transition properties', () => {
      expect(springTransition.type).toBe('spring');
      expect(springTransition.damping).toBe(25);
      expect(springTransition.stiffness).toBe(300);
    });

    it('should have correct smooth transition properties', () => {
      expect(smoothTransition.type).toBe('tween');
      expect(smoothTransition.duration).toBe(0.3);
    });

    it('should have correct bounce transition properties', () => {
      expect(bounceTransition.type).toBe('spring');
      expect(bounceTransition.damping).toBe(15);
      expect(bounceTransition.stiffness).toBe(400);
    });
  });
});