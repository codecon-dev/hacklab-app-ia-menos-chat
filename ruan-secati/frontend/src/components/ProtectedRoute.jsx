import { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

function ProtectedRoute({ children }) {
  const { isAuthenticated, isLoading } = useContext(AuthContext);

  if (isLoading) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#f5f5f5'
      }}>
        <div style={{
          fontSize: '1.2rem',
          color: '#666'
        }}>
          Carregando...
        </div>
      </div>
    );
  }

  return isAuthenticated() ? children : <Navigate to="/login" replace />;
}

export default ProtectedRoute;