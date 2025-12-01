'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useEffect, useState } from 'react';

interface ShipCelebrationProps {
  show: boolean;
  onComplete?: () => void;
}

export function ShipCelebration({ show, onComplete }: ShipCelebrationProps) {
  const [particles, setParticles] = useState<{ id: number; x: number; y: number }[]>([]);

  useEffect(() => {
    if (show) {
      // Generate particles
      const newParticles = Array.from({ length: 12 }, (_, i) => ({
        id: i,
        x: Math.random() * 100 - 50,
        y: Math.random() * -100 - 50,
      }));
      setParticles(newParticles);

      // Clear after animation
      const timer = setTimeout(() => {
        setParticles([]);
        onComplete?.();
      }, 1000);

      return () => clearTimeout(timer);
    }
  }, [show, onComplete]);

  return (
    <AnimatePresence>
      {particles.map((particle) => (
        <motion.div
          key={particle.id}
          initial={{ opacity: 1, scale: 1, x: 0, y: 0 }}
          animate={{
            opacity: 0,
            scale: 0,
            x: particle.x,
            y: particle.y,
          }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          className="absolute w-2 h-2 rounded-full bg-green-500 pointer-events-none"
          style={{ left: '50%', top: '50%' }}
        />
      ))}
    </AnimatePresence>
  );
}
