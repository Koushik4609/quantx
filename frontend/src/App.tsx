import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { AuthPage } from './pages/AuthPage';
import { DashboardPage } from './pages/DashboardPage';
import { TradePage } from './pages/TradePage';
import { TransactionsPage } from './pages/TransactionsPage';
import { AssistantPage } from './pages/AssistantPage';
import { NewsPage } from './pages/NewsPage';
import { AcademyPage } from './pages/AcademyPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { StrategyPage } from './pages/StrategyPage';
import { PortfolioAIPage } from './pages/PortfolioAIPage';
import { AlertsPage } from './pages/AlertsPage';
import { BrokerPage } from './pages/BrokerPage';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { token } = useAuth();
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
};

const AppRouter = () => {
  const { token } = useAuth();
  
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={token ? <Navigate to="/dashboard" replace /> : <AuthPage />} />
        
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="/trade" 
          element={
            <ProtectedRoute>
              <TradePage />
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="/transactions" 
          element={
            <ProtectedRoute>
              <TransactionsPage />
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="/assistant" 
          element={
            <ProtectedRoute>
              <AssistantPage />
            </ProtectedRoute>
          } 
        />

        <Route 
          path="/news" 
          element={
            <ProtectedRoute>
              <NewsPage />
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="/academy" 
          element={
            <ProtectedRoute>
              <AcademyPage />
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="/analytics" 
          element={
            <ProtectedRoute>
              <AnalyticsPage />
            </ProtectedRoute>
          } 
        />

        <Route 
          path="/strategies" 
          element={
            <ProtectedRoute>
              <StrategyPage />
            </ProtectedRoute>
          } 
        />

        <Route 
          path="/portfolio-ai" 
          element={
            <ProtectedRoute>
              <PortfolioAIPage />
            </ProtectedRoute>
          } 
        />

        <Route 
          path="/alerts" 
          element={
            <ProtectedRoute>
              <AlertsPage />
            </ProtectedRoute>
          } 
        />

        <Route 
          path="/broker" 
          element={
            <ProtectedRoute>
              <BrokerPage />
            </ProtectedRoute>
          } 
        />

        <Route path="*" element={<Navigate to={token ? "/dashboard" : "/login"} replace />} />
      </Routes>
    </BrowserRouter>
  );
};

function App() {
  return (
    <AuthProvider>
      <AppRouter />
    </AuthProvider>
  );
}

export default App;
