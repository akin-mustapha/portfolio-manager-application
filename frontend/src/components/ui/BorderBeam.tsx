import React from 'react';
import { cn } from '../../utils/ui';

interface BorderBeamProps {
  className?: string;
  size?: number;
  duration?: number;
  delay?: number;
  borderWidth?: number;
  anchor?: number;
  colorFrom?: string;
  colorVia?: string;
  colorTo?: string;
  reverse?: boolean;
}

export const BorderBeam: React.FC<BorderBeamProps> = ({
  className,
  size = 200,
  duration = 15,
  anchor = 90,
  borderWidth = 1.5,
  colorFrom = "transparent",
  colorVia = "rgb(34, 197, 94)",
  colorTo = "transparent",
  delay = 0,
  reverse = false,
}) => {
  return (
    <div
      className={cn(
        "pointer-events-none absolute inset-0 rounded-[inherit] [border:calc(var(--border-width)*1px)_solid_transparent]",
        className
      )}
      style={
        {
          "--border-width": borderWidth,
          "--border-radius": "inherit",
        } as React.CSSProperties
      }
    >
      <div
        className="absolute inset-0 rounded-[inherit] [border:inherit] [mask:linear-gradient(transparent,transparent),conic-gradient(from_calc(var(--border-angle)*1deg),transparent_0,var(--color-from)_12.5%,var(--color-via)_25%,var(--color-to)_37.5%,transparent_50%)] [mask-composite:intersect]"
        style={
          {
            "--color-from": colorFrom,
            "--color-via": colorVia,
            "--color-to": colorTo,
            "--border-angle": "0deg",
            animation: `border-beam ${duration}s linear infinite ${delay}s ${
              reverse ? "reverse" : ""
            }`,
          } as React.CSSProperties
        }
      />
      <style jsx>{`
        @keyframes border-beam {
          to {
            --border-angle: 360deg;
          }
        }
      `}</style>
    </div>
  );
};