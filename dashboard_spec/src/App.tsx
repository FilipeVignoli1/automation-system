// App.tsx
import React from 'react';
import { Dashboard } from '../components/Dashboard';
import rawData from '../data/solicitacoes.json';

const App: React.FC = () => {
  return <Dashboard data={rawData} />;
};

export default App;
