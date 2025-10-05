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
  /** The size of the beam glow. */
  size?: number;
}

export const BorderBeam: React.FC<BorderBeamProps> = ({
  duration = 4,
  delay = 0,
  colorFrom = "transparent",
  colorTo = "#3b82f6",
  className,
  reverse = false,
  borderWidth = 2,
  size = 100,
}) => {
  // Convert hex color to RGB for gradients
  const hexToRgb = (hex: string) => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : { r: 59, g: 130, b: 246 }; // Default blue
  };

  const rgb = hexToRgb(colorTo);
  const beamColor = `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.8)`;
  const beamColorFade = `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0)`;

  return (
    <div className="pointer-events-none absolute inset-0 rounded-[inherit] overflow-hidden">
      {/* Four separate beams for each edge - cleaner approach */}
      <div className="absolute inset-0">
        {/* Top beam */}
        <motion.div
          className="absolute top-0 left-0"
          style={{
            width: '100%',
            height: `${borderWidth}px`,
            background: `linear-gradient(90deg, ${beamColorFade}, ${beamColor}, ${beamColorFade})`,
            borderRadius: '1px',
          }}
          initial={{ scaleX: 0, x: '-100%' }}
          animate={{
            scaleX: [0, 1, 1, 0],
            x: ['-100%', '-100%', '100%', '100%'],
          }}
          transition={{
            duration,
            delay: reverse ? delay + (duration * 3) / 4 : delay,
            repeat: Infinity,
            ease: "easeInOut",
            times: [0, 0.2, 0.8, 1],
          }}
        />

        {/* Right beam */}
        <motion.div
          className="absolute top-0 right-0"
          style={{
            width: `${borderWidth}px`,
            height: '100%',
            background: `linear-gradient(180deg, ${beamColorFade}, ${beamColor}, ${beamColorFade})`,
            borderRadius: '1px',
          }}
          initial={{ scaleY: 0, y: '-100%' }}
          animate={{
            scaleY: [0, 1, 1, 0],
            y: ['-100%', '-100%', '100%', '100%'],
          }}
          transition={{
            duration,
            delay: reverse ? delay + (duration * 2) / 4 : delay + duration / 4,
            repeat: Infinity,
            ease: "easeInOut",
            times: [0, 0.2, 0.8, 1],
          }}
        />

        {/* Bottom beam */}
        <motion.div
          className="absolute bottom-0 right-0"
          style={{
            width: '100%',
            height: `${borderWidth}px`,
            background: `linear-gradient(270deg, ${beamColorFade}, ${beamColor}, ${beamColorFade})`,
            borderRadius: '1px',
          }}
          initial={{ scaleX: 0, x: '100%' }}
          animate={{
            scaleX: [0, 1, 1, 0],
            x: ['100%', '100%', '-100%', '-100%'],
          }}
          transition={{
            duration,
            delay: reverse ? delay + duration / 4 : delay + (duration * 2) / 4,
            repeat: Infinity,
            ease: "easeInOut",
            times: [0, 0.2, 0.8, 1],
          }}
        />

        {/* Left beam */}
        <motion.div
          className="absolute bottom-0 left-0"
          style={{
            width: `${borderWidth}px`,
            height: '100%',
            background: `linear-gradient(0deg, ${beamColorFade}, ${beamColor}, ${beamColorFade})`,
            borderRadius: '1px',
          }}
          initial={{ scaleY: 0, y: '100%' }}
          animate={{
            scaleY: [0, 1, 1, 0],
            y: ['100%', '100%', '-100%', '-100%'],
          }}
          transition={{
            duration,
            delay: reverse ? delay : delay + (duration * 3) / 4,
            repeat: Infinity,
            ease: "easeInOut",
            times: [0, 0.2, 0.8, 1],
          }}
        />
      </div>

      {/* Subtle glow effect */}
      <motion.div
        className="absolute inset-0 rounded-[inherit]"
        style={{
          boxShadow: `0 0 10px rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.2)`,
        }}
        animate={{
          boxShadow: [
            `0 0 10px rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.1)`,
            `0 0 20px rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.3)`,
            `0 0 10px rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.1)`,
          ],
        }}
        transition={{
          duration: duration / 2,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
    </div>
  );
};