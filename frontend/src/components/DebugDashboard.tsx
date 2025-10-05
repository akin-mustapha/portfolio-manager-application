import React from 'react';
import { useAppContext } from '../contexts/AppContext';

const DebugDashboard: React.FC = () => {
  const { auth } = useAppContext();

  console.log('DebugDashboard render:', {
    isAuthenticated: auth.isAuthenticated,
    hasTrading212Connection: auth.hasTrading212Connection,
  });

  return (
    <div className="p-8 bg-red-100 min-h-screen">
      <h1 className="text-4xl font-bold text-red-800 mb-4">DEBUG DASHBOARD</h1>
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-2xl font-bold mb-4">Authentication Status</h2>
        <p>Is Authenticated: {auth.isAuthenticated ? 'YES' : 'NO'}</p>
        <p>Has Trading212 Connection: {auth.hasTrading212Connection ? 'YES' : 'NO'}</p>
        
        <div className="mt-6 p-4 bg-blue-100 rounded">
          <h3 className="font-bold">Sample Portfolio Data</h3>
          <p>Total Value: £125,430.50</p>
          <p>Total Return: 25.43%</p>
          <p>This should be visible!</p>
        </div>
      </div>
    </div>
  );
};

export default DebugDashboard;