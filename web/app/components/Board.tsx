'use client';

import { useEffect, useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Task, EnergyColumn } from '@/lib/types';
import { api } from '@/lib/api';
import { Column } from './Column';

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
      <div className="flex items-center justify-center h-64">
        <p className="text-muted-foreground">Loading tasks...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-destructive">{error}</p>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex gap-4 overflow-x-auto pb-4"
    >
      {COLUMNS.map((column) => (
        <Column
          key={column}
          column={column}
          tasks={tasksByColumn[column]}
          onShipTask={handleShipTask}
        />
      ))}
    </motion.div>
  );
}
