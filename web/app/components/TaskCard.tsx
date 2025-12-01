'use client';

import { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Task } from '@/lib/types';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Rocket } from 'lucide-react';
import { ShipCelebration } from './ShipCelebration';

interface TaskCardProps {
  task: Task;
  onShip?: (id: string) => void;
}

export function TaskCard({ task, onShip }: TaskCardProps) {
  const [isShipping, setIsShipping] = useState(false);
  const [showCelebration, setShowCelebration] = useState(false);

  const handleShip = useCallback(async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!onShip || isShipping) return;

    setIsShipping(true);
    setShowCelebration(true);

    // Small delay for animation
    setTimeout(() => {
      onShip(task.id);
    }, 300);
  }, [onShip, task.id, isShipping]);

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{
        opacity: isShipping ? 0 : 1,
        y: 0,
        scale: isShipping ? 0.8 : 1,
        x: isShipping ? 100 : 0,
      }}
      exit={{ opacity: 0, scale: 0.8, x: 100 }}
      transition={{ type: 'spring', stiffness: 300, damping: 25 }}
      whileHover={{ scale: 1.02 }}
      className="cursor-grab active:cursor-grabbing relative"
    >
      <Card className="bg-card hover:bg-accent/50 transition-colors">
        <CardContent className="p-3">
          <div className="flex items-start justify-between gap-2">
            <p className="text-sm font-medium leading-tight">{task.title}</p>
            {task.energy_column !== 'shipped' && onShip && (
              <motion.button
                onClick={handleShip}
                disabled={isShipping}
                whileHover={{ scale: 1.2 }}
                whileTap={{ scale: 0.9 }}
                className="text-muted-foreground hover:text-green-500 transition-colors disabled:opacity-50"
                title="Ship it!"
              >
                <Rocket className="h-4 w-4" />
              </motion.button>
            )}
          </div>
          <div className="mt-2 flex items-center gap-2">
            <Badge variant="outline" className="text-xs">
              {task.id.slice(0, 8)}
            </Badge>
          </div>
        </CardContent>
      </Card>

      <ShipCelebration show={showCelebration} onComplete={() => setShowCelebration(false)} />
    </motion.div>
  );
}
