'use client';

import { motion } from 'framer-motion';
import { Task } from '@/lib/types';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Rocket } from 'lucide-react';

interface TaskCardProps {
  task: Task;
  onShip?: (id: string) => void;
}

export function TaskCard({ task, onShip }: TaskCardProps) {
  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.8 }}
      whileHover={{ scale: 1.02 }}
      className="cursor-grab active:cursor-grabbing"
    >
      <Card className="bg-card hover:bg-accent/50 transition-colors">
        <CardContent className="p-3">
          <div className="flex items-start justify-between gap-2">
            <p className="text-sm font-medium leading-tight">{task.title}</p>
            {task.energy_column !== 'shipped' && onShip && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onShip(task.id);
                }}
                className="text-muted-foreground hover:text-green-500 transition-colors"
                title="Ship it!"
              >
                <Rocket className="h-4 w-4" />
              </button>
            )}
          </div>
          <div className="mt-2 flex items-center gap-2">
            <Badge variant="outline" className="text-xs">
              {task.id.slice(0, 8)}
            </Badge>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
