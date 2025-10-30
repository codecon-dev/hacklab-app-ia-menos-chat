-- Script de inicialização do banco
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Criar índices para melhorar performance de consultas geográficas
-- (será usado quando criarmos as tabelas)