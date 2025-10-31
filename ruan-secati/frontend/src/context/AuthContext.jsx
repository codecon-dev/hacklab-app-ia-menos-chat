import { createContext, useState, useEffect } from 'react';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Verificar se há dados de autenticação salvos no localStorage
    const savedToken = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');

    if (savedToken && savedUser) {
      setToken(savedToken);
      setUser(JSON.parse(savedUser));
    }
    
    setIsLoading(false);
  }, []);

  const login = (userToken, userData) => {
    setToken(userToken);
    setUser(userData);
    
    // Salvar no localStorage
    localStorage.setItem('token', userToken);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    
    // Remover do localStorage
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  };

  const isAuthenticated = () => {
    // Verificar também o localStorage como fallback
    const storedToken = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');
    
    // Se há token e user em memória, está autenticado
    if (token && user) return true;
    
    // Se não há em memória mas há no localStorage, pode ser um problema de sincronização
    if (storedToken && storedUser && (!token || !user)) {
      // Recarregar do localStorage
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
      return true;
    }
    
    return false;
  };

  const value = {
    user,
    token,
    isLoading,
    login,
    logout,
    isAuthenticated
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};