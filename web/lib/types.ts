export type EnergyColumn = 'hyperfocus' | 'quick_win' | 'low_energy' | 'shipped';

export interface Task {
  id: string;
  title: string;
  body: string | null;
  raw_input: string;
  energy_column: EnergyColumn;
  position: number;
  created_at: string;
  updated_at: string;
  shipped_at: string | null;
  created_via: 'cli' | 'slack' | 'web' | 'api';
}

export interface CreateTaskInput {
  raw_input: string;
  energy_column?: EnergyColumn;
  created_via?: 'web';
}

export interface UpdateTaskInput {
  title?: string;
  body?: string;
  energy_column?: EnergyColumn;
  position?: number;
}
