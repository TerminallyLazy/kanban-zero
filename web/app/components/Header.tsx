'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Settings as SettingsIcon, Flame, Trophy, TrendingUp } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Settings } from './Settings';
import { Task } from '@/lib/types';

interface HeaderProps {
  tasks: Task[];
}

export function Header({ tasks }: HeaderProps) {
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  // Calculate stats
  const today = new Date().toISOString().split('T')[0];
  const tasksToday = tasks.filter((t) => {
    const taskDate = t.created_at.split('T')[0];
    return taskDate === today;
  }).length;

  const shippedTasks = tasks.filter((t) => t.energy_column === 'shipped').length;

  // Calculate streak (simplified - just count shipped tasks for now)
  const streak = Math.min(shippedTasks, 99);

  return (
    <>
      <header className="sticky top-0 z-30 bg-background/80 backdrop-blur-xl border-b border-border/40 shadow-sm">
        <div className="max-w-[2000px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-3"
            >
              <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-red-500 via-yellow-500 to-green-500 shadow-lg">
                <Flame className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-red-500 via-yellow-500 via-blue-500 to-green-500 bg-clip-text text-transparent">
                  Kanban Zero
                </h1>
                <p className="text-xs text-muted-foreground">
                  AI-native, energy-aware task management
                </p>
              </div>
            </motion.div>

            {/* Stats */}
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="hidden md:flex items-center gap-6"
            >
              {/* Tasks Today */}
              <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-yellow-500/10 border border-yellow-500/20">
                <TrendingUp className="h-4 w-4 text-yellow-500" />
                <div>
                  <p className="text-xs text-muted-foreground">Today</p>
                  <p className="text-lg font-bold text-yellow-500">{tasksToday}</p>
                </div>
              </div>

              {/* Shipped */}
              <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-green-500/10 border border-green-500/20">
                <Trophy className="h-4 w-4 text-green-500" />
                <div>
                  <p className="text-xs text-muted-foreground">Shipped</p>
                  <p className="text-lg font-bold text-green-500">{shippedTasks}</p>
                </div>
              </div>

              {/* Streak */}
              <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-red-500/10 border border-red-500/20">
                <Flame className="h-4 w-4 text-red-500" />
                <div>
                  <p className="text-xs text-muted-foreground">Streak</p>
                  <p className="text-lg font-bold text-red-500">{streak}</p>
                </div>
              </div>
            </motion.div>

            {/* Settings Button */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
            >
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsSettingsOpen(true)}
                className="relative hover:bg-accent transition-all hover:scale-110"
              >
                <SettingsIcon className="h-5 w-5" />
                <motion.span
                  className="absolute -top-1 -right-1 w-2 h-2 bg-green-500 rounded-full"
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ repeat: Infinity, duration: 2 }}
                />
              </Button>
            </motion.div>
          </div>

          {/* Mobile Stats */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="md:hidden flex items-center gap-3 mt-4 pt-4 border-t border-border/40"
          >
            <div className="flex-1 flex items-center gap-2 px-3 py-2 rounded-lg bg-yellow-500/10 border border-yellow-500/20">
              <TrendingUp className="h-3.5 w-3.5 text-yellow-500" />
              <div>
                <p className="text-[10px] text-muted-foreground">Today</p>
                <p className="text-sm font-bold text-yellow-500">{tasksToday}</p>
              </div>
            </div>

            <div className="flex-1 flex items-center gap-2 px-3 py-2 rounded-lg bg-green-500/10 border border-green-500/20">
              <Trophy className="h-3.5 w-3.5 text-green-500" />
              <div>
                <p className="text-[10px] text-muted-foreground">Shipped</p>
                <p className="text-sm font-bold text-green-500">{shippedTasks}</p>
              </div>
            </div>

            <div className="flex-1 flex items-center gap-2 px-3 py-2 rounded-lg bg-red-500/10 border border-red-500/20">
              <Flame className="h-3.5 w-3.5 text-red-500" />
              <div>
                <p className="text-[10px] text-muted-foreground">Streak</p>
                <p className="text-sm font-bold text-red-500">{streak}</p>
              </div>
            </div>
          </motion.div>
        </div>
      </header>

      <Settings isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />
    </>
  );
}
