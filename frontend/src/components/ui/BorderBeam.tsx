"use client";

import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../utils/ui';

interface BorderBeamProps {
  /** The duration of the border beam. */
  duration?: number;
  /** The delay of the border beam. */
  delay?: number;
  /** The color of the border beam from. */
  colorFrom?: string;
  /** The color of the border beam to. */
  colorTo?: string;
  /** The class name of the border beam. */
  className?: string;
  /** Whether to reverse the animation direction. */
  reverse?: boolean;
  /** The border width of the beam. */
  borderWidth?: number;
}

export const BorderBeam: React.FC<BorderBeamProps> = ({
  duration = 4,
  delay = 0,
  colorFrom = "transparent",
  colorTo = "#3b82f6",
  className,
  reverse = false,
  borderWidth = 1,
}) => {
  // Convert hex color to RGB for box-shadow
  const hexToRgb = (hex: string) => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : { r: 59, g: 130, b: 246 }; // Default blue
  };

  const rgb = hexToRgb(colorTo);
  const shadowColor = `${rgb.r}, ${rgb.g}, ${rgb.b}`;

  return (
    <div className="pointer-events-none absolute inset-0 rounded-[inherit]">
      {/* Rotating glow effect using box-shadow */}
      <motion.div
        className={cn(
          "absolute inset-0 rounded-[inherit]",
          className
        )}
        style={{
          boxShadow: `
            0 0 20px rgba(${shadowColor}, 0.3),
            0 0 40px rgba(${shadowColor}, 0.2),
            0 0 60px rgba(${shadowColor}, 0.1),
            inset 0 0 0 ${borderWidth}px rgba(${shadowColor}, 0.4)
          `,
          background: 'transparent',
        }}
        animate={{
          boxShadow: [
            `0 0 20px rgba(${shadowColor}, 0.3), 0 0 40px rgba(${shadowColor}, 0.2), 0 0 60px rgba(${shadowColor}, 0.1), inset 0 0 0 ${borderWidth}px rgba(${shadowColor}, 0.4)`,
            `0 0 30px rgba(${shadowColor}, 0.5), 0 0 60px rgba(${shadowColor}, 0.3), 0 0 90px rgba(${shadowColor}, 0.2), inset 0 0 0 ${borderWidth}px rgba(${shadowColor}, 0.6)`,
            `0 0 20px rgba(${shadowColor}, 0.3), 0 0 40px rgba(${shadowColor}, 0.2), 0 0 60px rgba(${shadowColor}, 0.1), inset 0 0 0 ${borderWidth}px rgba(${shadowColor}, 0.4)`,
          ],
        }}
        transition={{
          duration,
          delay,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
      

    </div>
  );
};