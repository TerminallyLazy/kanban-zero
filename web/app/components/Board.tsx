'use client';

import { useEffect, useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Task, EnergyColumn } from '@/lib/types';
import { api } from '@/lib/api';
import { Column } from './Column';
import { QuickAdd } from './QuickAdd';
import { Loader2 } from 'lucide-react';

const COLUMNS: EnergyColumn[] = ['hyperfocus', 'quick_win', 'low_energy', 'shipped'];

export function Board() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = useCallback(async () => {
    try {
      const data = await api.tasks.list();
      setTasks(data);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load tasks');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const handleTaskAdded = useCallback((task: Task) => {
    setTasks((prev) => [task, ...prev]);
  }, []);

  const handleShipTask = async (id: string) => {
    try {
      const shipped = await api.tasks.ship(id);
      setTasks((prev) =>
        prev.map((t) => (t.id === id ? shipped : t))
      );
    } catch (e) {
      console.error('Failed to ship task:', e);
    }
  };

  const tasksByColumn = COLUMNS.reduce((acc, col) => {
    acc[col] = tasks.filter((t) => t.energy_column === col);
    return acc;
  }, {} as Record<EnergyColumn, Task[]>);

  if (loading) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex flex-col items-center justify-center h-96 gap-4"
      >
        <Loader2 className="h-12 w-12 animate-spin text-primary" />
        <p className="text-muted-foreground text-lg">Loading your tasks...</p>
      </motion.div>
    );
  }

  if (error) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex flex-col items-center justify-center h-96 gap-4"
      >
        <div className="p-6 rounded-xl bg-destructive/10 border border-destructive/20">
          <p className="text-destructive font-semibold">{error}</p>
        </div>
      </motion.div>
    );
  }

  return (
    <div className="space-y-6 pb-8">
      <QuickAdd onTaskAdded={handleTaskAdded} />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 auto-rows-fr"
      >
        {COLUMNS.map((column, index) => (
          <motion.div
            key={column}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 + index * 0.05 }}
          >
            <Column
              column={column}
              tasks={tasksByColumn[column]}
              onShipTask={handleShipTask}
            />
          </motion.div>
        ))}
      </motion.div>
    </div>
  );
}
