import { Task, CreateTaskInput, UpdateTaskInput, EnergyColumn } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class APIError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'APIError';
  }
}

async function fetchAPI<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    throw new APIError(response.status, await response.text());
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

export const api = {
  tasks: {
    list: (column?: EnergyColumn): Promise<Task[]> => {
      const params = column ? `?column=${column}` : '';
      return fetchAPI<Task[]>(`/api/tasks${params}`);
    },

    get: (id: string): Promise<Task> => {
      return fetchAPI<Task>(`/api/tasks/${id}`);
    },

    create: (data: CreateTaskInput): Promise<Task> => {
      return fetchAPI<Task>('/api/tasks', {
        method: 'POST',
        body: JSON.stringify({ ...data, created_via: 'web' }),
      });
    },

    update: (id: string, data: UpdateTaskInput): Promise<Task> => {
      return fetchAPI<Task>(`/api/tasks/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      });
    },

    delete: (id: string): Promise<void> => {
      return fetchAPI<void>(`/api/tasks/${id}`, {
        method: 'DELETE',
      });
    },

    ship: (id: string): Promise<Task> => {
      return fetchAPI<Task>(`/api/tasks/${id}/ship`, {
        method: 'POST',
      });
    },
  },
};
