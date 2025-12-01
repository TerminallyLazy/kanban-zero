'use client';

import { AnimatePresence } from 'framer-motion';
import { Task, EnergyColumn } from '@/lib/types';
import { TaskCard } from './TaskCard';
import { Flame, Zap, Coffee, Rocket } from 'lucide-react';

const COLUMN_CONFIG: Record<EnergyColumn, { icon: React.ReactNode; color: string; label: string }> = {
  hyperfocus: {
    icon: <Flame className="h-5 w-5" />,
    color: 'text-red-500',
    label: 'Hyperfocus',
  },
  quick_win: {
    icon: <Zap className="h-5 w-5" />,
    color: 'text-yellow-500',
    label: 'Quick Wins',
  },
  low_energy: {
    icon: <Coffee className="h-5 w-5" />,
    color: 'text-blue-500',
    label: 'Low Energy',
  },
  shipped: {
    icon: <Rocket className="h-5 w-5" />,
    color: 'text-green-500',
    label: 'Shipped',
  },
};

interface ColumnProps {
  column: EnergyColumn;
  tasks: Task[];
  onShipTask?: (id: string) => void;
}

export function Column({ column, tasks, onShipTask }: ColumnProps) {
  const config = COLUMN_CONFIG[column];

  return (
    <div className="flex flex-col min-w-[280px] max-w-[320px]">
      <div className={`flex items-center gap-2 mb-3 ${config.color}`}>
        {config.icon}
        <h2 className="font-semibold">{config.label}</h2>
        <span className="text-muted-foreground text-sm">({tasks.length})</span>
      </div>

      <div className="flex flex-col gap-2 min-h-[200px] p-2 bg-muted/30 rounded-lg">
        <AnimatePresence mode="popLayout">
          {tasks.map((task) => (
            <TaskCard key={task.id} task={task} onShip={onShipTask} />
          ))}
        </AnimatePresence>

        {tasks.length === 0 && (
          <p className="text-muted-foreground text-sm text-center py-8">
            No tasks here
          </p>
        )}
      </div>
    </div>
  );
}
