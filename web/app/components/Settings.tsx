'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useTheme } from 'next-themes';
import { X, Sun, Moon, Laptop, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface SettingsProps {
  isOpen: boolean;
  onClose: () => void;
}

export function Settings({ isOpen, onClose }: SettingsProps) {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  const [animationsEnabled, setAnimationsEnabled] = useState(true);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
          />

          {/* Settings Panel */}
          <motion.div
            initial={{ opacity: 0, x: 300 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 300 }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed right-0 top-0 bottom-0 w-full max-w-md bg-background border-l border-border shadow-2xl z-50 overflow-y-auto"
          >
            <div className="p-6 space-y-6">
              {/* Header */}
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold">Settings</h2>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={onClose}
                  className="hover:bg-accent"
                >
                  <X className="h-5 w-5" />
                </Button>
              </div>

              {/* Theme Selection */}
              <div className="space-y-3">
                <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
                  Appearance
                </h3>
                <div className="grid grid-cols-3 gap-3">
                  <button
                    onClick={() => setTheme('light')}
                    className={`flex flex-col items-center gap-2 p-4 rounded-lg border-2 transition-all ${
                      theme === 'light'
                        ? 'border-primary bg-primary/10'
                        : 'border-border hover:border-primary/50 hover:bg-accent'
                    }`}
                  >
                    <Sun className="h-5 w-5" />
                    <span className="text-xs font-medium">Light</span>
                  </button>

                  <button
                    onClick={() => setTheme('dark')}
                    className={`flex flex-col items-center gap-2 p-4 rounded-lg border-2 transition-all ${
                      theme === 'dark'
                        ? 'border-primary bg-primary/10'
                        : 'border-border hover:border-primary/50 hover:bg-accent'
                    }`}
                  >
                    <Moon className="h-5 w-5" />
                    <span className="text-xs font-medium">Dark</span>
                  </button>

                  <button
                    onClick={() => setTheme('system')}
                    className={`flex flex-col items-center gap-2 p-4 rounded-lg border-2 transition-all ${
                      theme === 'system'
                        ? 'border-primary bg-primary/10'
                        : 'border-border hover:border-primary/50 hover:bg-accent'
                    }`}
                  >
                    <Laptop className="h-5 w-5" />
                    <span className="text-xs font-medium">System</span>
                  </button>
                </div>
              </div>

              {/* Animation Toggle */}
              <div className="space-y-3">
                <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
                  Preferences
                </h3>
                <button
                  onClick={() => setAnimationsEnabled(!animationsEnabled)}
                  className="w-full flex items-center justify-between p-4 rounded-lg border-2 border-border hover:border-primary/50 hover:bg-accent transition-all"
                >
                  <div className="flex items-center gap-3">
                    <Sparkles className="h-5 w-5 text-primary" />
                    <div className="text-left">
                      <p className="font-medium">Animations</p>
                      <p className="text-xs text-muted-foreground">
                        Smooth transitions and effects
                      </p>
                    </div>
                  </div>
                  <div
                    className={`w-11 h-6 rounded-full transition-colors ${
                      animationsEnabled ? 'bg-primary' : 'bg-muted'
                    }`}
                  >
                    <motion.div
                      animate={{ x: animationsEnabled ? 20 : 2 }}
                      transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                      className="w-5 h-5 bg-white rounded-full mt-0.5"
                    />
                  </div>
                </button>
              </div>

              {/* About */}
              <div className="pt-6 border-t border-border">
                <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-3">
                  About
                </h3>
                <div className="space-y-2 text-sm text-muted-foreground">
                  <p>
                    <strong className="text-foreground">Kanban Zero</strong> v1.0.0
                  </p>
                  <p>AI-native, energy-aware task management for ADHD brains</p>
                  <p className="text-xs pt-2">
                    Built with Next.js, Tailwind CSS, and Framer Motion
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
