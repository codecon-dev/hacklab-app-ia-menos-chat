import { useState, useContext, useEffect } from "react";
import { AuthContext } from "../context/AuthContext";
import jsPDF from "jspdf";

function Comparator() {
  // URL base da API - pode ser alterada para debug
  const API_BASE_URL = "http://localhost:8000";
  // Alternativa para debug: "http://127.0.0.1:8000"
  
  const [product1, setProduct1] = useState("");
  const [product2, setProduct2] = useState("");
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);
  const [history, setHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [historyError, setHistoryError] = useState("");

  const { user, token, logout } = useContext(AuthContext);

  // Debug: Log mudanças no estado do histórico
  useEffect(() => {
    console.log("📊 Estado do histórico mudou:", {
      length: history.length,
      items: history.map((item, idx) => ({
        index: idx,
        product1: item.product1,
        product2: item.product2,
        created_at: item.created_at
      }))
    });
  }, [history]);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    // Carregar histórico ao montar o componente, mas com um pequeno delay
    // para garantir que o token esteja completamente inicializado
    const timeoutId = setTimeout(() => {
      if (token) {
        fetchHistory();
      }
    }, 100);

    return () => clearTimeout(timeoutId);
  }, [token]);

  // Função para buscar histórico de comparações
  const fetchHistory = async () => {
    if (!token) {
      console.log("❌ fetchHistory: Token não disponível");
      return;
    }
    
    console.log("🔍 fetchHistory: Iniciando busca do histórico...");
    console.log("🔗 URL:", `${API_BASE_URL}/history`);
    console.log("🔑 Token:", token ? `Bearer ${token.substring(0, 20)}...` : 'Não definido');
    
    setLoadingHistory(true);
    setHistoryError("");
    try {
      const response = await fetch(`${API_BASE_URL}/history`, {
        method: "GET",
        headers: { 
          "Authorization": `Bearer ${token}`
        }
      });

      console.log("📡 fetchHistory: Status da resposta:", response.status);
      console.log("📡 fetchHistory: Headers da resposta:", Object.fromEntries(response.headers));

      if (!response.ok) {
        if (response.status === 401) {
          console.warn("⚠️ fetchHistory: Token pode estar expirado durante busca do histórico");
          setHistoryError("Sessão expirada. Faça login novamente para ver o histórico.");
          return;
        }
        const errorText = await response.text();
        console.error("❌ fetchHistory: Erro na resposta:", errorText);
        setHistoryError(`Erro ao buscar histórico: ${response.status} - ${errorText}`);
        throw new Error(`Erro ao buscar histórico: ${response.status} - ${errorText}`);
      }

      const data = await response.json();
      console.log("✅ fetchHistory: Dados recebidos:", data);
      console.log("📊 fetchHistory: Tipo dos dados:", typeof data);
      console.log("📊 fetchHistory: É array?", Array.isArray(data));
      console.log("📊 fetchHistory: Quantidade de itens:", Array.isArray(data) ? data.length : 'N/A');
      
      // Validar se os dados são um array válido
      if (!Array.isArray(data)) {
        console.error("❌ fetchHistory: Dados recebidos não são um array:", data);
        setHistoryError("Formato de dados inválido recebido da API.");
        setHistory([]);
        return;
      }
      
              if (Array.isArray(data)) {
                data.forEach((item, index) => {
                  console.log(`📄 fetchHistory: Item ${index}:`, {
                    product1: item.product1,
                    product2: item.product2,
                    created_at: item.created_at,
                    tem_comparison_result: !!item.comparison_result,
                    tem_resumo: !!(item.comparison_result && item.comparison_result.resumo),
                    keys: Object.keys(item)
                  });
                });
              }      setHistory(data);
      setHistoryError("");
      console.log("💾 fetchHistory: Estado do histórico atualizado");
    } catch (err) {
      console.error("❌ fetchHistory: Erro capturado:", err);
      console.error("❌ fetchHistory: Stack trace:", err.stack);
      setHistoryError(`Erro de conexão: ${err.message}`);
    } finally {
      setLoadingHistory(false);
      console.log("🏁 fetchHistory: Processo finalizado");
    }
  };

  // Função para extrair nome do site do URL
  const extractSiteName = (url) => {
    try {
      const hostname = new URL(url).hostname;
      // Remove www. se existir
      const siteName = hostname.replace(/^www\./, '');
      // Pega apenas o nome principal (antes do primeiro ponto)
      const mainName = siteName.split('.')[0];
      // Capitaliza a primeira letra
      return mainName.charAt(0).toUpperCase() + mainName.slice(1);
    } catch {
      return 'Link';
    }
  };

  const handleCompare = async () => {
    setLoading(true);
    setError("");
    setReport(null);

    // Validar se o token existe
    if (!token) {
      setError("Você precisa estar logado para fazer comparações.");
      setLoading(false);
      return;
    }

    // Validar campos de entrada
    if (!product1.trim() || !product2.trim()) {
      setError("Por favor, preencha ambos os produtos para comparação.");
      setLoading(false);
      return;
    }

    try {
      // Debug: Log da requisição
      console.log('Enviando requisição para:', `${API_BASE_URL}/compare`);
      console.log('Token:', token ? `Bearer ${token.substring(0, 20)}...` : 'Não definido');
      console.log('Payload:', { product1, product2 });
      
      const response = await fetch(`${API_BASE_URL}/compare`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ product1, product2 }),
      });

      if (!response.ok) {
        if (response.status === 401) {
          // Token expirado ou inválido - fazer logout
          logout();
          setError("Sua sessão expirou. Por favor, faça login novamente.");
          return;
        }
        
        // Outros erros HTTP
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Erro do servidor: ${response.status}`);
      }

      const data = await response.json();
      setReport(data);
      // Atualizar histórico após nova comparação
      fetchHistory();
    } catch (err) {
      // Melhorar mensagens de erro de rede
      if (err.name === 'TypeError' && err.message.includes('fetch')) {
        setError("Erro de conexão. Verifique sua internet e tente novamente.");
      } else {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleExportPDF = (reportData = null, prod1 = null, prod2 = null) => {
    console.log('🖨️ handleExportPDF chamado com parâmetros:', {
      reportData,
      prod1,
      prod2,
      currentReport: report
    });
    
    // Se não foram passados parâmetros, usa o report atual
    const rawData = reportData || report;
    const product1Name = prod1 || product1;
    const product2Name = prod2 || product2;
    
    // Normalizar dados - verificar se há aninhamento (comparison_result)
    let dataToExport = rawData;
    if (rawData && rawData.comparison_result) {
      console.log('🔄 Detectado objeto aninhado, extraindo comparison_result');
      dataToExport = rawData.comparison_result;
    }
    
    console.log('🖨️ Dados para exportação após normalização:', {
      dataToExport,
      product1Name,
      product2Name,
      resumo: dataToExport?.resumo,
      conclusao: dataToExport?.conclusao,
      pros_produto1: dataToExport?.pros_produto1,
      contras_produto1: dataToExport?.contras_produto1,
      pros_produto2: dataToExport?.pros_produto2,
      contras_produto2: dataToExport?.contras_produto2
    });
    
    if (!dataToExport) {
      console.log('❌ Nenhum dado para exportar');
      return;
    }

    const doc = new jsPDF();
    
    // Configuração da fonte e título
    doc.setFontSize(20);
    doc.setFont(undefined, 'bold');
    doc.text('Compara.ai', 20, 20);
    
    // Data da comparação
    doc.setFontSize(10);
    doc.setFont(undefined, 'normal');
    const today = new Date().toLocaleDateString('pt-BR');
    doc.text(`Gerado em: ${today}`, 20, 30);
    
    // Produtos comparados
    doc.setFontSize(14);
    doc.setFont(undefined, 'bold');
    doc.text('Produtos Comparados:', 20, 45);
    
    doc.setFontSize(12);
    doc.setFont(undefined, 'normal');
    doc.text(`• ${product1Name}`, 20, 55);
    doc.text(`• ${product2Name}`, 20, 65);
    
    // Resumo
    let yPosition = 80;
    doc.setFontSize(14);
    doc.setFont(undefined, 'bold');
    doc.text('Resumo:', 20, yPosition);
    
    yPosition += 10;
    doc.setFontSize(11);
    doc.setFont(undefined, 'normal');
    
    // Quebrar texto do resumo em linhas com validação
    const resumoText = dataToExport.resumo && dataToExport.resumo.trim() !== '' ? dataToExport.resumo : "Resumo não disponível";
    console.log('📝 Texto do resumo para PDF:', resumoText);
    const resumoLines = doc.splitTextToSize(resumoText, 170);
    doc.text(resumoLines, 20, yPosition);
    yPosition += resumoLines.length * 6;
    
    // Conclusão (se existir)
    if (dataToExport.conclusao && dataToExport.conclusao.trim() !== '') {
      yPosition += 15;
      doc.setFontSize(14);
      doc.setFont(undefined, 'bold');
      doc.text('Conclusão:', 20, yPosition);
      
      yPosition += 10;
      doc.setFontSize(11);
      doc.setFont(undefined, 'normal');
      
      // Quebrar texto da conclusão em linhas
      console.log('📝 Texto da conclusão para PDF:', dataToExport.conclusao);
      const conclusaoLines = doc.splitTextToSize(dataToExport.conclusao, 170);
      doc.text(conclusaoLines, 20, yPosition);
      yPosition += conclusaoLines.length * 6;
    }
    
    // Produto 1
    yPosition += 15;
    doc.setFontSize(14);
    doc.setFont(undefined, 'bold');
    doc.text(`${product1Name}:`, 20, yPosition);
    
    yPosition += 10;
    doc.setFontSize(12);
    doc.setFont(undefined, 'bold');
    doc.setTextColor(40, 167, 69); // Verde
    doc.text('Prós:', 20, yPosition);
    
    yPosition += 8;
    doc.setFontSize(10);
    doc.setFont(undefined, 'normal');
    doc.setTextColor(0, 0, 0); // Preto
    
    if (dataToExport.pros_produto1 && dataToExport.pros_produto1.length > 0) {
      dataToExport.pros_produto1.forEach((pro, index) => {
        const proText = `• ${pro}`;
        const proLines = doc.splitTextToSize(proText, 170);
        doc.text(proLines, 20, yPosition);
        yPosition += proLines.length * 5;
      });
    } else {
      doc.text("—", 20, yPosition);
      yPosition += 5;
    }
    
    yPosition += 5;
    doc.setFontSize(12);
    doc.setFont(undefined, 'bold');
    doc.setTextColor(220, 53, 69); // Vermelho
    doc.text('Contras:', 20, yPosition);
    
    yPosition += 8;
    doc.setFontSize(10);
    doc.setFont(undefined, 'normal');
    doc.setTextColor(0, 0, 0); // Preto
    
    if (dataToExport.contras_produto1 && dataToExport.contras_produto1.length > 0) {
      dataToExport.contras_produto1.forEach((contra, index) => {
        const contraText = `• ${contra}`;
        const contraLines = doc.splitTextToSize(contraText, 170);
        doc.text(contraLines, 20, yPosition);
        yPosition += contraLines.length * 5;
      });
    } else {
      doc.text("—", 20, yPosition);
      yPosition += 5;
    }
    
    // Verificar se precisa de nova página
    if (yPosition > 250) {
      doc.addPage();
      yPosition = 20;
    }
    
    // Produto 2
    yPosition += 15;
    doc.setFontSize(14);
    doc.setFont(undefined, 'bold');
    doc.text(`${product2Name}:`, 20, yPosition);
    
    yPosition += 10;
    doc.setFontSize(12);
    doc.setFont(undefined, 'bold');
    doc.setTextColor(40, 167, 69); // Verde
    doc.text('Prós:', 20, yPosition);
    
    yPosition += 8;
    doc.setFontSize(10);
    doc.setFont(undefined, 'normal');
    doc.setTextColor(0, 0, 0); // Preto
    
    if (dataToExport.pros_produto2 && dataToExport.pros_produto2.length > 0) {
      dataToExport.pros_produto2.forEach((pro, index) => {
        const proText = `• ${pro}`;
        const proLines = doc.splitTextToSize(proText, 170);
        doc.text(proLines, 20, yPosition);
        yPosition += proLines.length * 5;
      });
    } else {
      doc.text("—", 20, yPosition);
      yPosition += 5;
    }
    
    yPosition += 5;
    doc.setFontSize(12);
    doc.setFont(undefined, 'bold');
    doc.setTextColor(220, 53, 69); // Vermelho
    doc.text('Contras:', 20, yPosition);
    
    yPosition += 8;
    doc.setFontSize(10);
    doc.setFont(undefined, 'normal');
    doc.setTextColor(0, 0, 0); // Preto
    
    if (dataToExport.contras_produto2 && dataToExport.contras_produto2.length > 0) {
      dataToExport.contras_produto2.forEach((contra, index) => {
        const contraText = `• ${contra}`;
        const contraLines = doc.splitTextToSize(contraText, 170);
        doc.text(contraLines, 20, yPosition);
        yPosition += contraLines.length * 5;
      });
    } else {
      doc.text("—", 20, yPosition);
      yPosition += 5;
    }
    
    // Salvar o PDF
    doc.save(`comparacao-${product1Name}-vs-${product2Name}.pdf`);
  };

  return (
    <div style={{
      fontFamily: "Arial, sans-serif",
      width: "100%",
      padding: isMobile ? "20px" : "20px 40px",
      backgroundColor: "#f9f9f9",
      minHeight: "100vh",
      boxSizing: "border-box",
      overflowX: "hidden"
    }}>
      {/* Header com informações do usuário */}
      <div style={{
        display: 'flex',
        flexDirection: isMobile ? 'column' : 'row',
        justifyContent: 'space-between',
        alignItems: isMobile ? 'stretch' : 'center',
        marginBottom: '2rem',
        padding: '1rem',
        backgroundColor: 'white',
        borderRadius: '8px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        gap: isMobile ? '1rem' : '0'
      }}>
        <div>
          <h1 style={{
            margin: 0,
            color: "#333",
            fontSize: "1.8rem"
          }}>
            Comparador de Produtos
          </h1>
          <p style={{
            margin: '0.5rem 0 0 0',
            color: '#666',
            fontSize: '0.9rem'
          }}>
            Bem-vindo, {user?.username}!
          </p>
        </div>
        <div style={{
          display: 'flex',
          gap: '1rem',
          alignItems: 'center'
        }}>
          <button
            onClick={() => setShowHistory(!showHistory)}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: showHistory ? '#28a745' : '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '0.9rem'
            }}
          >
            {showHistory ? 'Ocultar Histórico' : 'Ver Histórico'}
          </button>
          <button
            onClick={logout}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#dc3545',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '0.9rem'
            }}
          >
            Sair
          </button>
        </div>
      </div>

      {/* Seção do Histórico */}
      {showHistory && (
        <div style={{
          backgroundColor: "white",
          padding: isMobile ? "20px" : "30px",
          borderRadius: "10px",
          boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
          maxWidth: "1200px",
          margin: "0 auto 20px auto",
          boxSizing: "border-box",
          width: "100%"
        }}>
          <div style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "20px"
          }}>
            <h3 style={{
              margin: "0",
              color: "#333",
              fontSize: "1.4rem"
            }}>
              📈 Histórico de Comparações
            </h3>
            <button
              onClick={fetchHistory}
              disabled={loadingHistory}
              style={{
                padding: "8px 16px",
                backgroundColor: loadingHistory ? "#6c757d" : "#007bff",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: loadingHistory ? "not-allowed" : "pointer",
                fontSize: "14px"
              }}
            >
              {loadingHistory ? "Carregando..." : "🔄 Atualizar"}
            </button>
          </div>

          {loadingHistory ? (
            <div style={{
              textAlign: "center",
              padding: "40px",
              color: "#6c757d"
            }}>
              Carregando histórico...
            </div>
          ) : historyError ? (
            <div style={{
              backgroundColor: "#f8d7da",
              color: "#721c24",
              padding: "15px",
              borderRadius: "6px",
              margin: "20px 0",
              border: "1px solid #f5c6cb"
            }}>
              <strong>Erro no histórico:</strong> {historyError}
              <br />
              <button
                onClick={fetchHistory}
                style={{
                  marginTop: "10px",
                  padding: "5px 10px",
                  backgroundColor: "#dc3545",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                  fontSize: "12px"
                }}
              >
                Tentar novamente
              </button>
            </div>
          ) : history.length === 0 ? (
            <div style={{
              textAlign: "center",
              padding: "40px",
              color: "#6c757d",
              fontStyle: "italic"
            }}>
              Nenhuma comparação encontrada no histórico.
            </div>
          ) : (
            <div style={{
              display: "grid",
              gap: "15px",
              maxHeight: "400px",
              overflowY: "auto",
              padding: "5px"
            }}>
              {history.map((item, index) => {
                // Verificações de segurança para evitar erros de renderização
                const product1 = item?.product1 || `Produto 1 #${index + 1}`;
                const product2 = item?.product2 || `Produto 2 #${index + 1}`;
                const createdAt = item?.created_at ? 
                  new Date(item.created_at).toLocaleDateString('pt-BR') : 
                  'Data não disponível';
                const resumo = item?.comparison_result?.resumo || "Resumo não disponível";

                return (
                  <div key={item.id || index} style={{
                    backgroundColor: "#f8f9fa",
                    padding: "15px",
                    borderRadius: "6px",
                    border: "1px solid #dee2e6",
                    transition: "all 0.2s"
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.backgroundColor = "#e9ecef";
                    e.currentTarget.style.borderColor = "#007bff";
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.backgroundColor = "#f8f9fa";
                    e.currentTarget.style.borderColor = "#dee2e6";
                  }}>
                    <div style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "flex-start",
                      marginBottom: "8px"
                    }}>
                      <div style={{ flex: 1, cursor: "pointer" }}
                        onClick={() => {
                          console.log("🖱️ Clicando no item do histórico:", item);
                          // Mapear os dados do histórico para o formato esperado pelo report
                          const mappedReport = item.comparison_result ? {
                            resumo: item.comparison_result.resumo,
                            conclusao: item.comparison_result.conclusao,
                            pros_produto1: item.comparison_result.pros_produto1,
                            pros_produto2: item.comparison_result.pros_produto2,
                            contras_produto1: item.comparison_result.contras_produto1,
                            contras_produto2: item.comparison_result.contras_produto2,
                            links_recomendados: item.comparison_result.links_recomendados
                          } : null;
                          
                          setReport(mappedReport);
                          setProduct1(product1);
                          setProduct2(product2);
                          setShowHistory(false);
                        }}>
                        <strong style={{ color: "#007bff" }}>
                          {product1} vs {product2}
                        </strong>
                      </div>
                      <div style={{ 
                        display: "flex", 
                        alignItems: "center", 
                        gap: "10px",
                        flexShrink: 0 
                      }}>
                        <small style={{ color: "#6c757d" }}>
                          {createdAt}
                        </small>
                        <button
                          onClick={(e) => {
                            e.stopPropagation(); // Evita que o clique no botão ative o clique do item
                            const mappedReport = item.comparison_result ? {
                              resumo: item.comparison_result.resumo,
                              conclusao: item.comparison_result.conclusao,
                              pros_produto1: item.comparison_result.pros_produto1,
                              pros_produto2: item.comparison_result.pros_produto2,
                              contras_produto1: item.comparison_result.contras_produto1,
                              contras_produto2: item.comparison_result.contras_produto2,
                              links_recomendados: item.comparison_result.links_recomendados
                            } : null;
                            handleExportPDF(mappedReport, product1, product2);
                          }}
                          style={{
                            padding: "4px 8px",
                            backgroundColor: "#28a745",
                            color: "white",
                            border: "none",
                            borderRadius: "4px",
                            cursor: "pointer",
                            fontSize: "12px",
                            fontWeight: "bold",
                            display: "flex",
                            alignItems: "center",
                            gap: "4px",
                            transition: "background-color 0.2s"
                          }}
                          onMouseOver={(e) => {
                            e.target.style.backgroundColor = "#218838";
                          }}
                          onMouseOut={(e) => {
                            e.target.style.backgroundColor = "#28a745";
                          }}
                          title="Exportar PDF desta comparação"
                        >
                          📄 PDF
                        </button>
                      </div>
                    </div>
                    <p style={{
                      margin: "0",
                      color: "#6c757d",
                      fontSize: "14px",
                      lineHeight: "1.4",
                      display: "-webkit-box",
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: "vertical",
                      overflow: "hidden",
                      cursor: "pointer"
                    }}
                    onClick={() => {
                      console.log("🖱️ Clicando no item do histórico:", item);
                      // Mapear os dados do histórico para o formato esperado pelo report
                      const mappedReport = item.comparison_result ? {
                        resumo: item.comparison_result.resumo,
                        conclusao: item.comparison_result.conclusao,
                        pros_produto1: item.comparison_result.pros_produto1,
                        pros_produto2: item.comparison_result.pros_produto2,
                        contras_produto1: item.comparison_result.contras_produto1,
                        contras_produto2: item.comparison_result.contras_produto2,
                        links_recomendados: item.comparison_result.links_recomendados
                      } : null;
                      
                      setReport(mappedReport);
                      setProduct1(product1);
                      setProduct2(product2);
                      setShowHistory(false);
                    }}>
                      {resumo}
                    </p>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      <div style={{
        backgroundColor: "white",
        padding: isMobile ? "20px" : "40px",
        borderRadius: "10px",
        boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
        maxWidth: "1200px",
        margin: "0 auto",
        boxSizing: "border-box",
        width: "100%"
      }}>
        <div style={{
          display: "grid",
          gridTemplateColumns: isMobile ? "1fr" : "1fr 1fr",
          gap: isMobile ? "20px" : "30px",
          marginBottom: "30px",
          maxWidth: "100%",
          margin: "0 auto 30px auto",
          boxSizing: "border-box"
        }}>
          <div>
            <label style={{
              display: "block",
              marginBottom: "8px",
              fontWeight: "bold",
              color: "#555"
            }}>
              Produto 1:
            </label>
            <input
              type="text"
              value={product1}
              onChange={(e) => setProduct1(e.target.value)}
              placeholder="Ex: iPhone 15 Pro"
              style={{
                width: "100%",
                padding: "12px",
                border: "2px solid #ddd",
                borderRadius: "6px",
                fontSize: "16px",
                transition: "border-color 0.3s",
                boxSizing: "border-box"
              }}
              onFocus={(e) => e.target.style.borderColor = "#007bff"}
              onBlur={(e) => e.target.style.borderColor = "#ddd"}
            />
          </div>

          <div>
            <label style={{
              display: "block",
              marginBottom: "8px",
              fontWeight: "bold",
              color: "#555"
            }}>
              Produto 2:
            </label>
            <input
              type="text"
              value={product2}
              onChange={(e) => setProduct2(e.target.value)}
              placeholder="Ex: Samsung Galaxy S24 Ultra"
              style={{
                width: "100%",
                padding: "12px",
                border: "2px solid #ddd",
                borderRadius: "6px",
                fontSize: "16px",
                transition: "border-color 0.3s",
                boxSizing: "border-box"
              }}
              onFocus={(e) => e.target.style.borderColor = "#007bff"}
              onBlur={(e) => e.target.style.borderColor = "#ddd"}
            />
          </div>
        </div>

        <button
          onClick={handleCompare}
          disabled={loading || !product1.trim() || !product2.trim()}
          style={{
            width: "100%",
            padding: "15px",
            backgroundColor: loading ? "#6c757d" : "#007bff",
            color: "white",
            border: "none",
            borderRadius: "6px",
            fontSize: "18px",
            fontWeight: "bold",
            cursor: loading || !product1.trim() || !product2.trim() ? "not-allowed" : "pointer",
            transition: "background-color 0.3s",
            marginBottom: "20px"
          }}
        >
          {loading ? "Comparando..." : "Comparar Produtos"}
        </button>

        {error && (
          <div style={{
            backgroundColor: "#f8d7da",
            color: "#721c24",
            padding: "15px",
            borderRadius: "6px",
            marginBottom: "20px",
            border: "1px solid #f5c6cb"
          }}>
            <strong>Erro:</strong> {error}
          </div>
        )}

        {report && (
          <div style={{
            backgroundColor: "#f8f9fa",
            padding: "30px",
            borderRadius: "8px",
            border: "1px solid #e9ecef"
          }}>
            <div style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "20px"
            }}>
              <h3 style={{
                margin: "0",
                color: "#333",
                fontSize: "1.4rem"
              }}>
                Resultado da Comparação
              </h3>
              <button
                onClick={handleExportPDF}
                style={{
                  padding: "8px 16px",
                  backgroundColor: "#28a745",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                  fontSize: "14px",
                  fontWeight: "bold"
                }}
              >
                📄 Exportar PDF
              </button>
            </div>

            {/* Resumo */}
            <div style={{
              backgroundColor: "white",
              padding: "15px",
              borderRadius: "6px",
              marginBottom: "20px",
              border: "1px solid #dee2e6"
            }}>
              <h4 style={{
                margin: "0 0 10px 0",
                color: "#495057",
                fontSize: "1.1rem"
              }}>
                📝 Resumo
              </h4>
              <p style={{
                margin: "0",
                lineHeight: "1.6",
                color: "#6c757d"
              }}>
                {report.resumo || "—"}
              </p>
            </div>

            {/* Conclusão */}
            {report.conclusao && (
              <div style={{
                backgroundColor: "white",
                padding: "15px",
                borderRadius: "6px",
                marginBottom: "20px",
                border: "1px solid #dee2e6"
              }}>
                <h4 style={{
                  margin: "0 0 10px 0",
                  color: "#495057",
                  fontSize: "1.1rem"
                }}>
                  🎯 Conclusão
                </h4>
                <p style={{
                  margin: "0",
                  lineHeight: "1.6",
                  color: "#6c757d",
                  fontWeight: "500"
                }}>
                  {report.conclusao}
                </p>
              </div>
            )}

            <div style={{
              display: "grid",
              gridTemplateColumns: isMobile ? "1fr" : "1fr 1fr",
              gap: "30px",
              maxWidth: "100%",
              margin: "0 auto",
              boxSizing: "border-box"
            }}>
              {/* Produto 1 */}
              <div style={{
                backgroundColor: "white",
                padding: "20px",
                borderRadius: "8px",
                border: "1px solid #dee2e6"
              }}>
                <h4 style={{
                  margin: "0 0 15px 0",
                  color: "#495057",
                  fontSize: "1.2rem",
                  borderBottom: "2px solid #007bff",
                  paddingBottom: "8px"
                }}>
                  {product1}
                </h4>

                {/* Prós */}
                <div style={{ marginBottom: "20px" }}>
                  <h5 style={{
                    margin: "0 0 10px 0",
                    color: "#28a745",
                    fontSize: "1rem",
                    display: "flex",
                    alignItems: "center",
                    gap: "5px"
                  }}>
                    ✅ Prós
                  </h5>
                  {report.pros_produto1 && report.pros_produto1.length > 0 ? (
                    <ul style={{
                      listStyle: "none",
                      padding: "0",
                      margin: "0"
                    }}>
                      {report.pros_produto1.map((pro, index) => (
                        <li key={index} style={{
                          backgroundColor: "#d4edda",
                          padding: "8px 12px",
                          margin: "5px 0",
                          borderRadius: "4px",
                          borderLeft: "4px solid #28a745",
                          fontSize: "14px",
                          color: "#000"
                        }}>
                          {pro}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p style={{
                      color: "#6c757d",
                      fontSize: "14px",
                      fontStyle: "italic",
                      margin: "0"
                    }}>
                      Nenhum pró identificado
                    </p>
                  )}
                </div>

                {/* Contras */}
                <div>
                  <h5 style={{
                    margin: "0 0 10px 0",
                    color: "#dc3545",
                    fontSize: "1rem",
                    display: "flex",
                    alignItems: "center",
                    gap: "5px"
                  }}>
                    ❌ Contras
                  </h5>
                  {report.contras_produto1 && report.contras_produto1.length > 0 ? (
                    <ul style={{
                      listStyle: "none",
                      padding: "0",
                      margin: "0"
                    }}>
                      {report.contras_produto1.map((contra, index) => (
                        <li key={index} style={{
                          backgroundColor: "#f8d7da",
                          padding: "8px 12px",
                          margin: "5px 0",
                          borderRadius: "4px",
                          borderLeft: "4px solid #dc3545",
                          fontSize: "14px",
                          color: "#000"
                        }}>
                          {contra}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p style={{
                      color: "#6c757d",
                      fontSize: "14px",
                      fontStyle: "italic",
                      margin: "0"
                    }}>
                      Nenhum contra identificado
                    </p>
                  )}
                </div>
              </div>

              {/* Produto 2 */}
              <div style={{
                backgroundColor: "white",
                padding: "20px",
                borderRadius: "8px",
                border: "1px solid #dee2e6"
              }}>
                <h4 style={{
                  margin: "0 0 15px 0",
                  color: "#495057",
                  fontSize: "1.2rem",
                  borderBottom: "2px solid #ffc107",
                  paddingBottom: "8px"
                }}>
                  {product2}
                </h4>

                {/* Prós */}
                <div style={{ marginBottom: "20px" }}>
                  <h5 style={{
                    margin: "0 0 10px 0",
                    color: "#28a745",
                    fontSize: "1rem",
                    display: "flex",
                    alignItems: "center",
                    gap: "5px"
                  }}>
                    ✅ Prós
                  </h5>
                  {report.pros_produto2 && report.pros_produto2.length > 0 ? (
                    <ul style={{
                      listStyle: "none",
                      padding: "0",
                      margin: "0"
                    }}>
                      {report.pros_produto2.map((pro, index) => (
                        <li key={index} style={{
                          backgroundColor: "#d4edda",
                          padding: "8px 12px",
                          margin: "5px 0",
                          borderRadius: "4px",
                          borderLeft: "4px solid #28a745",
                          fontSize: "14px",
                          color: "#000"
                        }}>
                          {pro}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p style={{
                      color: "#6c757d",
                      fontSize: "14px",
                      fontStyle: "italic",
                      margin: "0"
                    }}>
                      Nenhum pró identificado
                    </p>
                  )}
                </div>

                {/* Contras */}
                <div>
                  <h5 style={{
                    margin: "0 0 10px 0",
                    color: "#dc3545",
                    fontSize: "1rem",
                    display: "flex",
                    alignItems: "center",
                    gap: "5px"
                  }}>
                    ❌ Contras
                  </h5>
                  {report.contras_produto2 && report.contras_produto2.length > 0 ? (
                    <ul style={{
                      listStyle: "none",
                      padding: "0",
                      margin: "0"
                    }}>
                      {report.contras_produto2.map((contra, index) => (
                        <li key={index} style={{
                          backgroundColor: "#f8d7da",
                          padding: "8px 12px",
                          margin: "5px 0",
                          borderRadius: "4px",
                          borderLeft: "4px solid #dc3545",
                          fontSize: "14px",
                          color: "#000"
                        }}>
                          {contra}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p style={{
                      color: "#6c757d",
                      fontSize: "14px",
                      fontStyle: "italic",
                      margin: "0"
                    }}>
                      Nenhum contra identificado
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* Links Recomendados */}
            <div style={{
              backgroundColor: "white",
              padding: "15px",
              borderRadius: "6px",
              marginTop: "20px",
              border: "1px solid #dee2e6"
            }}>
              <h4 style={{
                margin: "0 0 15px 0",
                color: "#495057",
                fontSize: "1.1rem"
              }}>
                🔗 Links Recomendados
              </h4>

              <div style={{
                display: "grid",
                gridTemplateColumns: isMobile ? "1fr" : "1fr 1fr",
                gap: "30px",
                maxWidth: "100%",
                margin: "0 auto"
              }}>
                <div>
                  <h5 style={{
                    margin: "0 0 10px 0",
                    color: "#6c757d",
                    fontSize: "0.9rem"
                  }}>
                    {product1}
                  </h5>
                  {report.links_recomendados?.produto1 && report.links_recomendados.produto1.length > 0 ? (
                    <ul style={{
                      listStyle: "none",
                      padding: "0",
                      margin: "0"
                    }}>
                      {report.links_recomendados.produto1.map((link, index) => (
                        <li key={index} style={{ marginBottom: "8px" }}>
                          <a
                            href={link}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{
                              color: "#007bff",
                              textDecoration: "none",
                              fontSize: "14px",
                              padding: "6px 12px",
                              border: "1px solid #007bff",
                              borderRadius: "4px",
                              display: "inline-block",
                              transition: "all 0.2s"
                            }}
                            onMouseOver={(e) => {
                              e.target.style.backgroundColor = "#007bff";
                              e.target.style.color = "white";
                            }}
                            onMouseOut={(e) => {
                              e.target.style.backgroundColor = "transparent";
                              e.target.style.color = "#007bff";
                            }}
                          >
                            🔗 {extractSiteName(link)}
                          </a>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p style={{
                      color: "#666",
                      fontSize: "14px",
                      fontStyle: "italic"
                    }}>
                      Nenhum link disponível
                    </p>
                  )}
                </div>

                <div>
                  <h5 style={{
                    margin: "0 0 10px 0",
                    color: "#6c757d",
                    fontSize: "0.9rem"
                  }}>
                    {product2}
                  </h5>
                  {report.links_recomendados?.produto2 && report.links_recomendados.produto2.length > 0 ? (
                    <ul style={{
                      listStyle: "none",
                      padding: "0",
                      margin: "0"
                    }}>
                      {report.links_recomendados.produto2.map((link, index) => (
                        <li key={index} style={{ marginBottom: "8px" }}>
                          <a
                            href={link}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{
                              color: "#007bff",
                              textDecoration: "none",
                              fontSize: "14px",
                              padding: "6px 12px",
                              border: "1px solid #007bff",
                              borderRadius: "4px",
                              display: "inline-block",
                              transition: "all 0.2s"
                            }}
                            onMouseOver={(e) => {
                              e.target.style.backgroundColor = "#007bff";
                              e.target.style.color = "white";
                            }}
                            onMouseOut={(e) => {
                              e.target.style.backgroundColor = "transparent";
                              e.target.style.color = "#007bff";
                            }}
                          >
                            🔗 {extractSiteName(link)}
                          </a>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p style={{
                      color: "#666",
                      fontSize: "14px",
                      fontStyle: "italic"
                    }}>
                      Nenhum link disponível
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Comparator;