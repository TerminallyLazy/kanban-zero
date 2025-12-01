import { Board } from './components/Board';

export default function Home() {
  return (
    <main className="min-h-screen p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold">Kanban Zero</h1>
        <p className="text-muted-foreground">
          AI-native, energy-aware task management
        </p>
      </header>

      <Board />
    </main>
  );
}
