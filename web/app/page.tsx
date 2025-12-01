'use client';

import { useState, useEffect } from 'react';
import { Board } from './components/Board';
import { Header } from './components/Header';
import { api } from '@/lib/api';
import { Task } from '@/lib/types';

export default function Home() {
  const [tasks, setTasks] = useState<Task[]>([]);

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const data = await api.tasks.list();
        setTasks(data);
      } catch (e) {
        console.error('Failed to load tasks for header:', e);
      }
    };
    fetchTasks();

    // Refresh tasks every 30 seconds to keep stats updated
    const interval = setInterval(fetchTasks, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen">
      <Header tasks={tasks} />
      <main className="max-w-[2000px] mx-auto p-6">
        <Board />
      </main>
    </div>
  );
}
