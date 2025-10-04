import React from 'react';

const Dashboard: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Portfolio Overview
        </h2>
        <p className="text-gray-600">
          Welcome to your Trading 212 Portfolio Dashboard. 
          Connect your Trading 212 API to get started.
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Total Value
          </h3>
          <p className="text-3xl font-bold text-gray-900">--</p>
          <p className="text-sm text-gray-500">Connect API to view data</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Total Return
          </h3>
          <p className="text-3xl font-bold text-gray-900">--</p>
          <p className="text-sm text-gray-500">Connect API to view data</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Active Pies
          </h3>
          <p className="text-3xl font-bold text-gray-900">--</p>
          <p className="text-sm text-gray-500">Connect API to view data</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;