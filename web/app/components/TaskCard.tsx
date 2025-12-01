'use client';

import { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Task } from '@/lib/types';
import { Badge } from '@/components/ui/badge';
import { Rocket, Calendar, Sparkles } from 'lucide-react';
import { ShipCelebration } from './ShipCelebration';

interface TaskCardProps {
  task: Task;
  onShip?: (id: string) => void;
}

export function TaskCard({ task, onShip }: TaskCardProps) {
  const [isShipping, setIsShipping] = useState(false);
  const [showCelebration, setShowCelebration] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

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

  // Format date nicely
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

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
      whileHover={{ scale: 1.02, y: -4 }}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      className="cursor-grab active:cursor-grabbing relative group"
    >
      <div className="relative bg-card border-2 border-border hover:border-primary/30 rounded-xl p-4 shadow-sm hover:shadow-xl transition-all duration-200 backdrop-blur-sm">
        {/* Gradient overlay on hover */}
        <motion.div
          className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent rounded-xl opacity-0 pointer-events-none"
          animate={{ opacity: isHovered ? 1 : 0 }}
          transition={{ duration: 0.2 }}
        />

        {/* Content */}
        <div className="relative z-10">
          <div className="flex items-start justify-between gap-3">
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold leading-snug text-foreground mb-2 break-words">
                {task.title}
              </p>
              {task.body && (
                <p className="text-xs text-muted-foreground line-clamp-2 mb-2">
                  {task.body}
                </p>
              )}
            </div>

            {/* Ship Button */}
            {task.energy_column !== 'shipped' && onShip && (
              <motion.button
                onClick={handleShip}
                disabled={isShipping}
                whileHover={{ scale: 1.15, rotate: 15 }}
                whileTap={{ scale: 0.9 }}
                className="flex-shrink-0 text-muted-foreground hover:text-green-500 transition-colors disabled:opacity-50 p-1.5 rounded-lg hover:bg-green-500/10"
                title="Ship it!"
              >
                <Rocket className="h-4 w-4" />
              </motion.button>
            )}
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between gap-2 mt-3 pt-3 border-t border-border/50">
            <div className="flex items-center gap-2 flex-wrap">
              <Badge
                variant="outline"
                className="text-[10px] px-1.5 py-0 h-5 font-mono"
              >
                {task.id.slice(0, 8)}
              </Badge>
              {task.created_via !== 'web' && (
                <Badge
                  variant="secondary"
                  className="text-[10px] px-1.5 py-0 h-5 capitalize"
                >
                  <Sparkles className="h-2.5 w-2.5 mr-0.5" />
                  {task.created_via}
                </Badge>
              )}
            </div>

            <div className="flex items-center gap-1 text-[10px] text-muted-foreground">
              <Calendar className="h-3 w-3" />
              <span>{formatDate(task.created_at)}</span>
            </div>
          </div>
        </div>

        {/* Shimmer effect on hover */}
        <motion.div
          className="absolute inset-0 rounded-xl overflow-hidden pointer-events-none"
          initial={false}
        >
          <motion.div
            className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent"
            animate={{
              x: isHovered ? ['100%', '-100%'] : '100%',
            }}
            transition={{
              duration: 0.8,
              ease: 'easeInOut',
            }}
          />
        </motion.div>
      </div>

      <ShipCelebration show={showCelebration} onComplete={() => setShowCelebration(false)} />
    </motion.div>
  );
}
