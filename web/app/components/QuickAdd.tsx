'use client';

import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, Sparkles, Loader2, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { api } from '@/lib/api';
import { Task } from '@/lib/types';

interface QuickAddProps {
  onTaskAdded: (task: Task) => void;
}

export function QuickAdd({ onTaskAdded }: QuickAddProps) {
  const [input, setInput] = useState('');
  const [isAdding, setIsAdding] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isAdding) return;

    setIsAdding(true);
    try {
      const task = await api.tasks.create({ raw_input: input.trim() });
      onTaskAdded(task);
      setInput('');
      setIsExpanded(false);
    } catch (error) {
      console.error('Failed to add task:', error);
    } finally {
      setIsAdding(false);
    }
  }, [input, isAdding, onTaskAdded]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      setIsExpanded(false);
      setInput('');
    }
  }, []);

  return (
    <div className="relative">
      <AnimatePresence mode="wait">
        {!isExpanded ? (
          <motion.div
            key="collapsed"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >
            <button
              onClick={() => setIsExpanded(true)}
              className="w-full group relative overflow-hidden rounded-xl border-2 border-dashed border-border hover:border-primary/50 bg-card/50 backdrop-blur-sm p-4 transition-all duration-200 hover:shadow-lg"
            >
              <div className="flex items-center justify-center gap-3">
                <div className="p-2 rounded-lg bg-primary/10 text-primary group-hover:bg-primary/20 transition-colors">
                  <Plus className="h-5 w-5" />
                </div>
                <div className="text-left">
                  <p className="font-semibold text-foreground group-hover:text-primary transition-colors">
                    Quick Add Task
                  </p>
                  <p className="text-xs text-muted-foreground flex items-center gap-1">
                    <Sparkles className="h-3 w-3" />
                    AI will route it to the right energy level
                  </p>
                </div>
              </div>

              {/* Shimmer effect */}
              <motion.div
                className="absolute inset-0 bg-gradient-to-r from-transparent via-primary/10 to-transparent"
                animate={{
                  x: ['-100%', '100%'],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  repeatDelay: 1,
                }}
              />
            </button>
          </motion.div>
        ) : (
          <motion.form
            key="expanded"
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            onSubmit={handleSubmit}
            className="relative rounded-xl border-2 border-primary/30 bg-card/90 backdrop-blur-sm p-4 shadow-xl"
          >
            <div className="flex gap-3">
              <div className="flex-1">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="What needs to be done? (e.g., 'Fix the login bug' or 'Review PRs')"
                  autoFocus
                  disabled={isAdding}
                  className="w-full px-4 py-3 text-sm font-medium bg-background border-2 border-border focus:border-primary rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 disabled:opacity-50 transition-all"
                />
                <div className="flex items-center gap-1 mt-2 text-xs text-muted-foreground">
                  <Sparkles className="h-3 w-3 text-primary" />
                  <span>AI will automatically categorize and route your task</span>
                </div>
              </div>

              <div className="flex flex-col gap-2">
                <Button
                  type="submit"
                  disabled={!input.trim() || isAdding}
                  className="px-6 font-semibold shadow-lg hover:shadow-xl transition-all"
                  size="lg"
                >
                  {isAdding ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Adding...
                    </>
                  ) : (
                    <>
                      <Plus className="h-4 w-4 mr-2" />
                      Add
                    </>
                  )}
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => {
                    setIsExpanded(false);
                    setInput('');
                  }}
                  className="px-6"
                  size="lg"
                >
                  <X className="h-4 w-4 mr-2" />
                  Cancel
                </Button>
              </div>
            </div>
          </motion.form>
        )}
      </AnimatePresence>
    </div>
  );
}
