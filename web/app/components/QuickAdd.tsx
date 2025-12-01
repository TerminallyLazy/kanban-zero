'use client';

import { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Plus } from 'lucide-react';
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

  if (!isExpanded) {
    return (
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <Button
          onClick={() => setIsExpanded(true)}
          variant="outline"
          className="w-full justify-start gap-2 text-muted-foreground"
        >
          <Plus className="h-4 w-4" />
          Quick add task...
        </Button>
      </motion.div>
    );
  }

  return (
    <motion.form
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      onSubmit={handleSubmit}
      className="flex gap-2"
    >
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="What needs to be done? (AI will parse)"
        autoFocus
        disabled={isAdding}
        className="flex-1 px-3 py-2 text-sm border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50"
      />
      <Button type="submit" disabled={!input.trim() || isAdding}>
        {isAdding ? 'Adding...' : 'Add'}
      </Button>
      <Button
        type="button"
        variant="ghost"
        onClick={() => {
          setIsExpanded(false);
          setInput('');
        }}
      >
        Cancel
      </Button>
    </motion.form>
  );
}
