// ===== LOGIN SYSTEM - TURISMO INTELIGENTE ===== //

class LoginSystem {
    constructor() {
        this.API_BASE = 'http://localhost:8000';
        this.TOKEN_KEY = 'turismo_token';
        this.USER_KEY = 'turismo_user';
        
        this.init();
    }

    // ===== INITIALIZATION ===== //
    init() {
        this.setupEventListeners();
        this.checkExistingLogin();
        console.log('Sistema de login inicializado');
    }

    // ===== EVENT LISTENERS ===== //
    setupEventListeners() {
        // Form submissions
        $('#formLogin').on('submit', (e) => {
            e.preventDefault();
            this.fazerLogin();
        });

        $('#formCadastro').on('submit', (e) => {
            e.preventDefault();
            this.fazerCadastro();
        });

        // Toggle between login and register
        $('#btnMostrarCadastro').on('click', () => {
            this.mostrarFormulario('cadastro');
        });

        $('#btnMostrarLogin').on('click', () => {
            this.mostrarFormulario('login');
        });

        // Continue button
        $('#btnContinuar').on('click', () => {
            this.redirecionarParaApp();
        });

        // Close modals on escape
        $(document).on('keydown', (e) => {
            if (e.key === 'Escape') {
                this.fecharModals();
            }
        });
    }

    // ===== FORM MANAGEMENT ===== //
    mostrarFormulario(tipo) {
        if (tipo === 'cadastro') {
            $('#loginForm').addClass('hidden');
            $('#registerForm').removeClass('hidden');
            $('#cadastroNome').focus();
        } else {
            $('#registerForm').addClass('hidden');
            $('#loginForm').removeClass('hidden');
            $('#loginEmail').focus();
        }
    }

    // ===== LOGIN FUNCTIONALITY ===== //
    async fazerLogin() {
        const email = $('#loginEmail').val().trim();
        const senha = $('#loginSenha').val();

        if (!this.validarEmail(email)) {
            this.mostrarErro('Por favor, insira um email válido.');
            return;
        }

        if (!senha) {
            this.mostrarErro('Por favor, insira a senha.');
            return;
        }

        this.mostrarLoading('Realizando login...');

        try {
            const response = await $.ajax({
                url: `${this.API_BASE}/api/v1/auth/login`,
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    email: email,
                    senha: senha
                }),
                timeout: 10000
            });

            this.esconderLoading();

            if (response.success) {
                // Salvar dados do usuário
                this.salvarLogin(response.token, response.usuario);
                
                // Mostrar sucesso
                this.mostrarSucesso(response.message);
            } else {
                this.mostrarErro(response.message || 'Erro no login');
            }

        } catch (error) {
            this.esconderLoading();
            console.error('Erro no login:', error);
            
            if (error.responseJSON) {
                this.mostrarErro(error.responseJSON.detail || 'Erro no servidor');
            } else if (error.statusText === 'timeout') {
                this.mostrarErro('Tempo limite excedido. Tente novamente.');
            } else {
                this.mostrarErro('Erro de conexão. Verifique se a API está rodando.');
            }
        }
    }

    // ===== REGISTER FUNCTIONALITY ===== //
    async fazerCadastro() {
        const nome = $('#cadastroNome').val().trim();
        const email = $('#cadastroEmail').val().trim();
        const senha = $('#cadastroSenha').val();

        if (!nome || nome.length < 2) {
            this.mostrarErro('Por favor, insira um nome válido (mínimo 2 caracteres).');
            return;
        }

        if (!this.validarEmail(email)) {
            this.mostrarErro('Por favor, insira um email válido.');
            return;
        }

        if (senha !== 'sejapro') {
            this.mostrarErro('A senha deve ser "sejapro".');
            return;
        }

        this.mostrarLoading('Criando conta...');

        try {
            const response = await $.ajax({
                url: `${this.API_BASE}/api/v1/auth/cadastro`,
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    nome: nome,
                    email: email,
                    senha: senha
                }),
                timeout: 10000
            });

            this.esconderLoading();

            if (response.success) {
                // Mostrar sucesso e volta para login
                this.mostrarSucesso(response.message + ' Agora faça login.');
                
                // Preencher email no formulário de login
                $('#loginEmail').val(email);
                
                // Voltar para login após 2 segundos
                setTimeout(() => {
                    this.fecharModals();
                    this.mostrarFormulario('login');
                }, 2000);
            } else {
                this.mostrarErro(response.message || 'Erro no cadastro');
            }

        } catch (error) {
            this.esconderLoading();
            console.error('Erro no cadastro:', error);
            
            if (error.responseJSON) {
                this.mostrarErro(error.responseJSON.detail || 'Erro no servidor');
            } else if (error.statusText === 'timeout') {
                this.mostrarErro('Tempo limite excedido. Tente novamente.');
            } else {
                this.mostrarErro('Erro de conexão. Verifique se a API está rodando.');
            }
        }
    }

    // ===== STORAGE MANAGEMENT ===== //
    salvarLogin(token, usuario) {
        localStorage.setItem(this.TOKEN_KEY, token);
        localStorage.setItem(this.USER_KEY, JSON.stringify(usuario));
        console.log('Login salvo:', usuario.nome);
    }

    obterToken() {
        return localStorage.getItem(this.TOKEN_KEY);
    }

    obterUsuario() {
        const userData = localStorage.getItem(this.USER_KEY);
        return userData ? JSON.parse(userData) : null;
    }

    limparLogin() {
        localStorage.removeItem(this.TOKEN_KEY);
        localStorage.removeItem(this.USER_KEY);
        console.log('Login limpo');
    }

    // ===== LOGIN VERIFICATION ===== //
    async checkExistingLogin() {
        const token = this.obterToken();
        const usuario = this.obterUsuario();

        if (token && usuario) {
            console.log('Token encontrado, verificando validade...');
            
            try {
                const response = await $.ajax({
                    url: `${this.API_BASE}/api/v1/auth/verificar-token`,
                    method: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({ token: token }),
                    timeout: 5000
                });

                if (response.valid) {
                    console.log('Token válido, redirecionando...');
                    this.redirecionarParaApp();
                } else {
                    this.limparLogin();
                }
            } catch (error) {
                console.log('Token inválido, limpando...');
                this.limparLogin();
            }
        }
    }

    // ===== NAVIGATION ===== //
    redirecionarParaApp() {
        window.location.href = 'index.html';
    }

    // ===== UI FEEDBACK ===== //
    mostrarLoading(texto) {
        $('#loadingText').text(texto);
        $('#loadingModal').addClass('modal-open');
    }

    esconderLoading() {
        $('#loadingModal').removeClass('modal-open');
    }

    mostrarSucesso(texto) {
        $('#successText').text(texto);
        $('#successModal').addClass('modal-open');
    }

    mostrarErro(mensagem) {
        $('#errorMessage').text(mensagem);
        $('#errorAlert').removeClass('hidden').addClass('slide-up');
        
        // Auto-hide após 5 segundos
        setTimeout(() => {
            this.fecharErro();
        }, 5000);
    }

    fecharErro() {
        $('#errorAlert').addClass('hidden').removeClass('slide-up');
    }

    fecharModals() {
        $('#loadingModal').removeClass('modal-open');
        $('#successModal').removeClass('modal-open');
    }

    // ===== VALIDATION ===== //
    validarEmail(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    }
}

// ===== GLOBAL FUNCTIONS ===== //
function fecharErro() {
    if (window.loginSystem) {
        window.loginSystem.fecharErro();
    }
}

// ===== DOCUMENT READY ===== //
$(document).ready(() => {
    console.log('Iniciando sistema de login...');
    window.loginSystem = new LoginSystem();
    
    // Focus no primeiro campo
    $('#loginEmail').focus();
    
    // Console welcome message
    console.log(`
    ======================================
       SISTEMA DE LOGIN - TURISMO INTELIGENTE
    ======================================
    
    Senha padrão: sejapro
    API Base: ${window.loginSystem?.API_BASE || 'localhost:8000'}
    Debug: Digite 'loginSystem' no console
    
    ======================================
    `);
});