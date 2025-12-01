'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { Task, EnergyColumn } from '@/lib/types';
import { TaskCard } from './TaskCard';
import { Flame, Zap, Coffee, Rocket } from 'lucide-react';

const COLUMN_CONFIG: Record<
  EnergyColumn,
  {
    icon: React.ReactNode;
    color: string;
    bgColor: string;
    borderColor: string;
    label: string;
    description: string;
    gradient: string;
  }
> = {
  hyperfocus: {
    icon: <Flame className="h-5 w-5" />,
    color: 'text-red-500',
    bgColor: 'bg-red-500/10',
    borderColor: 'border-red-500/30',
    label: 'Hyperfocus',
    description: 'Deep work, high impact',
    gradient: 'from-red-500/20 to-transparent',
  },
  quick_win: {
    icon: <Zap className="h-5 w-5" />,
    color: 'text-yellow-500',
    bgColor: 'bg-yellow-500/10',
    borderColor: 'border-yellow-500/30',
    label: 'Quick Wins',
    description: 'Fast, easy victories',
    gradient: 'from-yellow-500/20 to-transparent',
  },
  low_energy: {
    icon: <Coffee className="h-5 w-5" />,
    color: 'text-blue-500',
    bgColor: 'bg-blue-500/10',
    borderColor: 'border-blue-500/30',
    label: 'Low Energy',
    description: 'Chill mode tasks',
    gradient: 'from-blue-500/20 to-transparent',
  },
  shipped: {
    icon: <Rocket className="h-5 w-5" />,
    color: 'text-green-500',
    bgColor: 'bg-green-500/10',
    borderColor: 'border-green-500/30',
    label: 'Shipped',
    description: 'Done and deployed',
    gradient: 'from-green-500/20 to-transparent',
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
    <div className="flex flex-col h-full">
      {/* Column Header */}
      <motion.div
        className={`flex items-center justify-between p-4 rounded-t-xl bg-gradient-to-br ${config.gradient} border-2 ${config.borderColor} ${config.bgColor} backdrop-blur-sm`}
        whileHover={{ scale: 1.02 }}
        transition={{ type: 'spring', stiffness: 300, damping: 20 }}
      >
        <div className="flex items-center gap-3">
          <div className={`${config.color} p-2 rounded-lg ${config.bgColor}`}>
            {config.icon}
          </div>
          <div>
            <h2 className={`font-bold text-lg ${config.color}`}>
              {config.label}
            </h2>
            <p className="text-xs text-muted-foreground">{config.description}</p>
          </div>
        </div>
        <div className={`flex items-center justify-center min-w-[2rem] h-8 px-2 rounded-full ${config.bgColor} ${config.color} font-bold text-sm border ${config.borderColor}`}>
          {tasks.length}
        </div>
      </motion.div>

      {/* Column Content */}
      <div className={`flex-1 flex flex-col gap-3 p-4 rounded-b-xl border-2 border-t-0 ${config.borderColor} bg-card/50 backdrop-blur-sm min-h-[400px]`}>
        <AnimatePresence mode="popLayout">
          {tasks.map((task) => (
            <TaskCard key={task.id} task={task} onShip={onShipTask} />
          ))}
        </AnimatePresence>

        {tasks.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex-1 flex flex-col items-center justify-center text-center py-12"
          >
            <div className={`${config.color} opacity-20 mb-3`}>
              {config.icon}
            </div>
            <p className="text-muted-foreground text-sm">
              No tasks yet
            </p>
            <p className="text-muted-foreground text-xs mt-1">
              Drag tasks here or add new ones
            </p>
          </motion.div>
        )}
      </div>
    </div>
  );
}
