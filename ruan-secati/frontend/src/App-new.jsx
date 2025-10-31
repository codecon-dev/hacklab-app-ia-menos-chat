import { Routes, Route, Navigate } from 'react-router-dom';
import { useContext } from 'react';
import { AuthContext } from './context/AuthContext';
import Login from './components/Login';
import Register from './components/Register';
import Comparator from './components/Comparator';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  const { user } = useContext(AuthContext);

  return (
    <div style={{ width: '100%', minHeight: '100vh' }}>
      <Routes>
        <Route 
          path="/login" 
          element={user ? <Navigate to="/" replace /> : <Login />} 
        />
        <Route 
          path="/register" 
          element={user ? <Navigate to="/" replace /> : <Register />} 
        />
        <Route 
          path="/" 
          element={
            <ProtectedRoute>
              <Comparator />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="*" 
          element={<Navigate to={user ? "/" : "/login"} replace />} 
        />
      </Routes>
    </div>
  );
}

export default App;