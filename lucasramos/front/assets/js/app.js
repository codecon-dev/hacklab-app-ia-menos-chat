
class TurismoApp {
    constructor() {
        this.map = null;
        this.heroMap = null;
        this.currentRoute = null;
        this.markers = [];
        this.routeMarkers = []; // Marcadores da rota no mapa do Brasil
        this.routeLine = null;   // Linha da rota no mapa do Brasil
        this.routeLayer = null;
        this.rotaAtual = null; // Para armazenar os dados da rota atual
        this.API_BASE = 'http://localhost:8000';
        this.currentRequest = null;
        this.TOKEN_KEY = 'turismo_token';
        this.USER_KEY = 'turismo_user';
        
        this.init();
    }

    // ===== INITIALIZATION ===== //
    init() {
        this.checkAuthentication();
        this.setupEventListeners();
        this.initMap();
        this.initHeroMap();
        this.initAutocomplete();
        this.setupUserInterface();
        this.setupScrollAnimations();
        this.initHeroBanner(); // Inicializar banner Slick
        
        // Carregar roteiros salvos após autenticação
        setTimeout(() => {
            if (this.getToken()) {
                this.carregarRoteirosSalvos();
            }
        }, 1000);
        console.log('Turismo Inteligente App iniciado com sucesso!');
    }

    // ===== AUTHENTICATION ===== //
    checkAuthentication() {
        const token = this.getToken();
        const user = this.getUser();

        if (token && user) {
            console.log(`Usuário autenticado: ${user.nome}`);
            this.updateUserInterface(user);
            this.showAuthenticatedFeatures();
        } else {
            console.log('Modo público - algumas funcionalidades restritas');
            this.showPublicMode();
        }
    }

    updateUserInterface(user) {
        const $userNameElement = $('.user-name');
        const $userEmailElement = $('.user-email');
        
        if ($userNameElement.length) $userNameElement.text(user.nome || 'Usuário');
        if ($userEmailElement.length) $userEmailElement.text(user.email || 'email@exemplo.com');
    }

    showAuthenticatedFeatures() {
        // Mostrar funcionalidades para usuários logados
        this.toggleElement('btnSalvarRoteiro', true);
        this.toggleElement('roteirosSalvosSection', true);
        this.toggleElement('loginButton', false);
        this.toggleElement('logoutButton', true);
        
        // Remover mensagens de acesso público
        this.removePublicMessages();
    }

    showPublicMode() {
        // Ocultar funcionalidades para usuários não logados
        this.toggleElement('btnSalvarRoteiro', false);
        this.toggleElement('roteirosSalvosSection', false);
        this.toggleElement('loginButton', true);
        this.toggleElement('logoutButton', false);
        
        // Adicionar mensagens informativas
        this.addPublicMessages();
    }

    toggleElement(elementId, show) {
        const $element = $('#' + elementId);
        if ($element.length) {
            $element.toggle(show);
        }
    }

    addPublicMessages() {
        // Adicionar mensagem no botão de salvar (caso esteja visível)
        const $saveButton = $('#btnSalvarRoteiro');
        if ($saveButton.length) {
            $saveButton.hide();
        }
        
        // Adicionar banner informativo
        // this.addPublicBanner();
    }

    removePublicMessages() {
        const $banner = $('#publicModeBanner');
        if ($banner.length) {
            $banner.remove();
        }
    }

    addPublicBanner() {
        // Verificar se o banner já existe
        if ($('#publicModeBanner').length) return;
        
        const bannerHtml = `
            <div id="publicModeBanner" class="alert alert-info shadow-lg mb-4">
                <div>
                    <i class="fas fa-info-circle"></i>
                    <div>
                        <h3 class="font-bold">Modo Público</h3>
                        <div class="text-xs">Faça login para salvar roteiros e acessar funcionalidades exclusivas!</div>
                    </div>
                </div>
                <div class="flex-none">
                    <button class="btn btn-sm btn-primary" onclick="window.location.href='login.html'">
                        <i class="fas fa-sign-in-alt mr-1"></i>
                        Fazer Login
                    </button>
                </div>
            </div>
        `;
        
        // Inserir no início da seção de planejamento
        const $planningSection = $('#planningSection');
        if ($planningSection.length) {
            $planningSection.prepend(bannerHtml);
        }
    }

    getToken() {
        return localStorage.getItem(this.TOKEN_KEY);
    }

    getUser() {
        const userData = localStorage.getItem(this.USER_KEY);
        return userData ? JSON.parse(userData) : null;
    }

    logout() {
        localStorage.removeItem(this.TOKEN_KEY);
        localStorage.removeItem(this.USER_KEY);
        console.log('Logout realizado');
        window.location.href = 'login.html';
    }

    // ===== HERO MAP INITIALIZATION ===== //
    initHeroMap() {
        try {
            const $heroMapContainer = $('#brazilMap');
            if (!$heroMapContainer.length) return;

            this.heroMap = L.map('brazilMap', {
                center: [-14.2350, -51.9253],
                zoom: 4,
                minZoom: 3,
                maxZoom: 18,
                zoomControl: true,
                scrollWheelZoom: true,
                doubleClickZoom: true,
                dragging: true,
                attributionControl: false,
                zoomAnimation: true,
                fadeAnimation: true,
                markerZoomAnimation: true
            });

            // Add tile layer with Brazil focus
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                opacity: 0.8,
                attribution: false
            }).addTo(this.heroMap);
            
            // Adicionar controles customizados
            this.addMapControls();

            // Add decorative markers for major Brazilian cities
            const majorCities = [
                { name: 'São Paulo', lat: -23.5505, lng: -46.6333 },
                { name: 'Rio de Janeiro', lat: -22.9068, lng: -43.1729 },
                { name: 'Brasília', lat: -15.8267, lng: -47.9218 },
                { name: 'Salvador', lat: -12.9714, lng: -38.5014 },
                { name: 'Fortaleza', lat: -3.7172, lng: -38.5433 },
                { name: 'Manaus', lat: -3.1190, lng: -60.0217 }
            ];

            majorCities.forEach(city => {
                L.circleMarker([city.lat, city.lng], {
                    radius: 4,
                    fillColor: '#ff6b6b',
                    color: '#fff',
                    weight: 2,
                    opacity: 0.8,
                    fillOpacity: 0.8
                }).addTo(this.heroMap);
            });

            console.log('Mapa do Brasil no hero section inicializado');
        } catch (error) {
            console.error('Erro ao inicializar mapa do hero:', error);
        }
    }
    
    // ===== MAP CONTROLS ===== //
    addMapControls() {
        if (!this.heroMap) return;
        
        // Botão para resetar vista do mapa
        const resetViewControl = L.control({ position: 'topright' });
        resetViewControl.onAdd = () => {
            const div = L.DomUtil.create('div', 'leaflet-bar leaflet-control');
            div.innerHTML = `
                <a href="#" title="Resetar Vista" style="
                    display: block;
                    width: 30px;
                    height: 30px;
                    line-height: 30px;
                    text-align: center;
                    text-decoration: none;
                    color: #333;
                    background: white;
                    border-radius: 4px;
                    font-size: 14px;
                    font-weight: bold;
                "><i class="fas fa-home"></i></a>
            `;
            div.onclick = (e) => {
                e.preventDefault();
                this.resetMapView();
            };
            return div;
        };
        resetViewControl.addTo(this.heroMap);
        
        // Botão para mostrar rota completa
        const showRouteControl = L.control({ position: 'topright' });
        showRouteControl.onAdd = () => {
            const div = L.DomUtil.create('div', 'leaflet-bar leaflet-control');
            div.innerHTML = `
                <a href="#" title="Ver Rota Completa" style="
                    display: block;
                    width: 30px;
                    height: 30px;
                    line-height: 30px;
                    text-align: center;
                    text-decoration: none;
                    color: #333;
                    background: white;
                    border-radius: 4px;
                    font-size: 14px;
                "><i class="fas fa-route"></i></a>
            `;
            div.onclick = (e) => {
                e.preventDefault();
                this.showFullRoute();
            };
            return div;
        };
        showRouteControl.addTo(this.heroMap);
    }
    
    resetMapView() {
        if (!this.heroMap) return;
        
        this.heroMap.setView([-14.2350, -51.9253], 4, {
            animate: true,
            duration: 1.5
        });
        console.log('Vista do mapa resetada');
    }
    
    showFullRoute() {
        if (!this.heroMap || !this.routeMarkers || this.routeMarkers.length === 0) {
            console.warn('Nenhuma rota disponível para mostrar');
            return;
        }
        
        // Calcular bounds de todos os marcadores
        const bounds = [];
        this.routeMarkers.forEach(marker => {
            if (marker.getLatLng) {
                bounds.push(marker.getLatLng());
            }
        });
        
        if (bounds.length > 0) {
            this.heroMap.fitBounds(bounds, { 
                padding: [50, 50],
                animate: true,
                duration: 1.5
            });
            console.log('Mostrando rota completa');
        }
    }

        // ===== HERO BANNER INITIALIZATION ===== //
    initHeroBanner() {
        try {
            // Banner estático - sem necessidade de Slick Carousel
            console.log('Banner estático inicializado com codecon.png');
            
            // Opcional: Adicionar alguma animação ou efeito se necessário
            const $bannerSlide = $('.banner-slide');
            if ($bannerSlide.length) {
                $bannerSlide.css('opacity', '0');
                setTimeout(() => {
                    $bannerSlide.css({
                        'transition': 'opacity 0.8s ease',
                        'opacity': '1'
                    });
                }, 100);
            }
        } catch (error) {
            console.error('Erro ao inicializar banner:', error);
        }
    }

    // ===== SCROLL ANIMATIONS ===== //
    setupScrollAnimations() {
        // Scroll to planning section
        window.scrollToPlanning = () => {
            const $planningSection = $('#planningSection');
            if ($planningSection.length) {
                $planningSection[0].scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        };

        // Parallax effect for hero section
        $(window).on('scroll', () => {
            const scrolled = $(window).scrollTop();
            const $heroSection = $('.hero-section');
            
            if ($heroSection.length) {
                const rate = scrolled * -0.3;
                $heroSection.css('transform', `translate3d(0, ${rate}px, 0)`);
            }
        });

        // Animate elements on scroll
        this.setupScrollObserver();
    }

    setupScrollObserver() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    $(entry.target).css({
                        'opacity': '1',
                        'transform': 'translateY(0)'
                    });
                }
            });
        }, observerOptions);

        // Observe cards for animation
        $('.card').each(function() {
            $(this).css({
                'opacity': '0',
                'transform': 'translateY(30px)',
                'transition': 'opacity 0.6s ease, transform 0.6s ease'
            });
            observer.observe(this);
        });
    }

    setupUserInterface() {
        const user = this.getUser();
        if (user) {
            this.updateUserInterface(user);
        }
    }

    // ===== EVENT LISTENERS ===== //
    setupEventListeners() {
        // Form submission
        $('#routeForm').on('submit', (e) => {
            e.preventDefault();
            this.buscarRota();
        });

        // Clear button
        $('#btnLimpar').on('click', () => this.limparFormulario());

        // Logout button - usando delegação de eventos
        $(document).on('click', '[onclick*="app.logout"]', (e) => {
            e.preventDefault();
            this.logout();
        });
    }

    // ===== MAP INITIALIZATION ===== //
    initMap() {
        try {
            const $mapContainer = $('#map');
            if (!$mapContainer.length) return;

            this.map = L.map('map').setView([-14.2350, -51.9253], 4);
            
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(this.map);

            console.log('Mapa principal inicializado');
        } catch (error) {
            console.error('Erro ao inicializar mapa:', error);
        }
    }

    // ===== AUTOCOMPLETE ===== //
    initAutocomplete() {
        this.setupCityAutocomplete('origemInput', 'origemSugestoes');
        this.setupCityAutocomplete('destinoInput', 'destinoSugestoes');
    }

    setupCityAutocomplete(inputId, suggestionsId) {
        const $input = $('#' + inputId);
        const $suggestions = $('#' + suggestionsId);
        
        if (!$input.length || !$suggestions.length) return;

        let timeout;
        
        $input.on('input', (e) => {
            clearTimeout(timeout);
            const query = $(e.target).val().trim();
            
            if (query.length < 2) {
                $suggestions.hide();
                return;
            }
            
            timeout = setTimeout(() => {
                this.buscarCidadesAutocomplete(query, $suggestions, $input);
            }, 300);
        });

        $input.on('blur', () => {
            setTimeout(() => {
                $suggestions.hide();
            }, 200);
        });

        $input.on('focus', (e) => {
            if ($(e.target).val().length >= 2) {
                this.buscarCidadesAutocomplete($(e.target).val().trim(), $suggestions, $input);
            }
        });
    }

    async buscarCidadesAutocomplete(termo, $suggestionsContainer, $inputElement) {
        try {
            // Usar o endpoint correto da API
            const url = `${this.API_BASE}/api/v1/cities/search?q=${encodeURIComponent(termo)}&limit=8`;
            
            const response = await $.ajax({
                url: url,
                method: 'GET',
                contentType: 'application/json'
            });

            // A resposta vem com formato { cidades: [...] }
            const cities = response.cidades || [];
            this.renderSuggestions(cities, $suggestionsContainer, $inputElement);
        } catch (error) {
            console.error('Erro ao buscar cidades:', error);
            $suggestionsContainer.hide();
        }
    }

    renderSuggestions(cities, $container, $input) {
        if (!cities || cities.length === 0) {
            $container.hide();
            return;
        }

        const inputId = $input.attr('id');
        const containerId = $container.attr('id');
        
        $container.html(cities.map(city => 
            `<div class="sugestao-item" onclick="app.selectCity('${city.nome}', '${city.uf}', '${inputId}', '${containerId}')">
                <div class="cidade-info">
                    <span class="cidade-nome">${city.nome}</span>
                    <span class="cidade-uf">${city.uf}</span>
                </div>
            </div>`
        ).join(''));
        
        $container.show();
    }

    selectCity(nome, uf, inputId, containerId) {
        const $input = $('#' + inputId);
        const $container = $('#' + containerId);
        
        $input.val(`${nome}, ${uf}`);
        $container.hide();
    }

    // ===== ROUTE SEARCH ===== //
    async buscarRota() {
        const origem = $('#origemInput').val().trim();
        const destino = $('#destinoInput').val().trim();
        
        // Campo de preferências foi removido no design flat
        const $preferenciasElement = $('#preferenciasInput');
        const preferencias = $preferenciasElement.length ? $preferenciasElement.val().trim() : '';

        if (!origem || !destino) {
            alert('Por favor, preencha as cidades de origem e destino.');
            return;
        }

        this.showLoading(true);
        this.hideResults();

        try {
            const headers = {
                'Content-Type': 'application/json'
            };
            
            // Adicionar token apenas se o usuário estiver logado
            const token = this.getToken();
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }
            
            const response = await $.ajax({
                url: `${this.API_BASE}/api/v1/tourism/route`,
                method: 'POST',
                headers: headers,
                data: JSON.stringify({
                    cidade_origem: origem,
                    cidade_destino: destino,
                    preferencias: preferencias || null
                }),
                contentType: 'application/json'
            });

            // Salvar dados da rota atual para possível salvamento
            this.rotaAtual = {
                cidade_origem: origem,
                cidade_destino: destino,
                preferencias: preferencias || null,
                resposta_ai: response.conteudo,
                coordenadas_origem: response.coordenadas_origem || null,
                coordenadas_destino: response.coordenadas_destino || null
            };
            
            this.displayResults(response);
            
        } catch (error) {
            console.error('Erro:', error);
            const errorMessage = error.responseJSON?.detail || error.statusText || 'Erro ao buscar rota';
            alert('Erro ao buscar rota: ' + errorMessage);
        } finally {
            this.showLoading(false);
        }
    }

    // ===== RESULTS DISPLAY ===== //
    displayResults(data) {
        console.log('Exibindo resultados:', data);
        
        // Verificar se temos dados válidos
        if (!data.sucesso || !data.rota) {
            console.error('Dados de rota inválidos:', data);
            return;
        }
        
        const { rota } = data;
        
        // Atualizar header da rota (principal)
        this.updateRouteHeader(rota);
        
        // Atualizar sidebar recolhível com pontos turísticos
        this.updateRouteSidebar(rota.pontos_turisticos || []);
        
        // Adicionar pontos turísticos ao mapa do Brasil existente
        this.addPointsToBrazilMap(rota.pontos_turisticos || []);
        
        // Salvar dados da rota atual
        this.rotaAtual = {
            cidade_origem: rota.cidade_origem,
            cidade_destino: rota.cidade_destino,
            preferencias: this.rotaAtual?.preferencias || null,
            resposta_ai: JSON.stringify(rota),
            coordenadas_origem: rota.pontos_turisticos?.[0]?.coordenadas || null,
            coordenadas_destino: rota.pontos_turisticos?.[rota.pontos_turisticos.length - 1]?.coordenadas || null,
            pontos_turisticos: rota.pontos_turisticos || []
        };

        // Mostrar sidebar e botão de abertura
        this.showRouteSidebar();
        this.showResults();
    }

    updateRouteHeader(rota) {
        // Atualizar no sidebar (nova localização)
        const $routeTitle = $('#routeTitle');
        const $routeSubtitle = $('#routeSubtitle');
        const $routeDistance = $('#routeDistance');
        const $routeTime = $('#routeTime');
        
        if ($routeTitle.length) {
            $routeTitle.text(`${rota.cidade_origem} → ${rota.cidade_destino}`);
        }
        
        if ($routeSubtitle.length) {
            const subtitle = rota.recomendacoes_gerais ? 
                rota.recomendacoes_gerais.substring(0, 100) + '...' : 
                'Descubra pontos incríveis pelo caminho';
            $routeSubtitle.text(subtitle);
        }
        
        if ($routeDistance.length) {
            $routeDistance.html('<i class="fas fa-route"></i> ' + (rota.distancia_aproximada || 'Calculando...'));
        }
        
        if ($routeTime.length) {
            $routeTime.html('<i class="fas fa-clock"></i> ' + (rota.tempo_viagem_estimado || 'Calculando...'));
        }
    }

    getCategoryIcon(categoria) {
        const iconMap = {
            'natural': 'fas fa-leaf',
            'histórico': 'fas fa-landmark',
            'cultural': 'fas fa-theater-masks',
            'religioso': 'fas fa-pray',
            'gastronômico': 'fas fa-utensils',
            'aventura': 'fas fa-mountain',
            'praia': 'fas fa-umbrella-beach',
            'default': 'fas fa-map-marker-alt'
        };
        
        for (const [key, icon] of Object.entries(iconMap)) {
            if (categoria && categoria.toLowerCase().includes(key)) {
                return icon;
            }
        }
        
        return iconMap.default;
    }

    selectPoint(index) {
        // Remover seleção anterior
        $('.point-item').removeClass('active expanded');
        
        // Selecionar novo ponto
        const $selectedItem = $(`[data-point-index="${index}"]`);
        if ($selectedItem.length) {
            $selectedItem.addClass('active expanded');
            
            // Scroll para o ponto na sidebar
            $selectedItem[0].scrollIntoView({ 
                behavior: 'smooth', 
                block: 'nearest' 
            });
        }
        
        // Highlight no mapa do Brasil
        this.highlightRouteMarker(index);
    }

    highlightRouteMarker(index) {
        // Reset all route markers to default
        if (this.routeMarkers) {
            this.routeMarkers.forEach((marker, i) => {
                // Só resetar marcadores de círculo (ímpares no array, pois temos círculo + número)
                if (i % 2 === 0) {
                    const pontoIndex = Math.floor(i / 2);
                    const ponto = this.rotaAtual?.pontos_turisticos?.[pontoIndex];
                    if (ponto && marker.setStyle) {
                        marker.setStyle({
                            radius: 10,
                            fillColor: this.getMarkerColor(ponto.categoria),
                            weight: 3,
                            opacity: 1,
                            fillOpacity: 0.9
                        });
                    }
                }
            });
        }
        
        // Highlight selected marker
        const markerIndex = index * 2; // Cada ponto tem 2 marcadores (círculo + número)
        if (this.routeMarkers && this.routeMarkers[markerIndex]) {
            const selectedMarker = this.routeMarkers[markerIndex];
            const ponto = this.rotaAtual?.pontos_turisticos?.[index];
            
            if (selectedMarker.setStyle) {
                selectedMarker.setStyle({
                    radius: 15,
                    fillColor: this.getMarkerColor(ponto?.categoria),
                    weight: 4,
                    opacity: 1,
                    fillOpacity: 1
                });
            }
            
            // Center map on selected marker
            this.heroMap.setView(selectedMarker.getLatLng(), Math.max(this.heroMap.getZoom(), 8), {
                animate: true,
                duration: 0.5
            });
        }
    }

    highlightMarker(index) {
        // Reset all markers to default
        this.markers.forEach((marker, i) => {
            const ponto = this.rotaAtual?.pontos_turisticos?.[i];
            if (ponto) {
                const defaultIcon = this.createCustomMarkerIcon(i, ponto.categoria);
                marker.setIcon(defaultIcon);
            }
        });
        
        // Highlight selected marker
        if (this.markers[index]) {
            const ponto = this.rotaAtual?.pontos_turisticos?.[index];
            if (ponto) {
                const highlightIcon = this.createHighlightMarkerIcon(index, ponto.categoria);
                this.markers[index].setIcon(highlightIcon);
            }
            
            // Center map on selected marker with smooth animation
            this.map.setView(this.markers[index].getLatLng(), 15, {
                animate: true,
                duration: 0.5
            });
        }
    }

    formatTourismContent(content) {
        return content
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>')
            .replace(/^\s*/, '<p>')
            .replace(/\s*$/, '</p>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>');
    }

    updateMap() {
        if (!this.map) {
            this.initMap();
        }
        
        // Clear existing markers
        this.clearMarkers();
    }

    addMarkersToMap(pontos) {
        if (!this.map) return;

        this.clearMarkers();
        const bounds = [];

        pontos.forEach((ponto, index) => {
            if (ponto.lat && ponto.lng) {
                const marker = L.marker([ponto.lat, ponto.lng])
                    .bindPopup(`<strong>${ponto.nome}</strong><br>${ponto.descricao || 'Ponto turístico'}`);
                
                this.markers.push(marker);
                marker.addTo(this.map);
                bounds.push([ponto.lat, ponto.lng]);
            }
        });

        if (bounds.length > 0) {
            this.map.fitBounds(bounds, { padding: [20, 20] });
        }
    }

    clearMarkers() {
        this.markers.forEach(marker => {
            this.map.removeLayer(marker);
        });
        this.markers = [];
    }

    // ===== UI UTILITIES ===== //
    showLoading(show) {
        // Novo overlay CodeCon PRO
        const $loadingOverlay = $('#loadingOverlay');
        if ($loadingOverlay.length) {
            if (show) {
                $loadingOverlay.removeClass('hidden');
                // Bloquear scroll do body
                $('body').css('overflow', 'hidden');
            } else {
                $loadingOverlay.addClass('hidden');
                // Restaurar scroll do body
                $('body').css('overflow', '');
            }
        }
        
        // Manter compatibilidade com loading antigo se existir
        const $loading = $('#loading');
        if ($loading.length) {
            $loading.toggleClass('hidden', !show);
        }
    }

    showResults() {
        const $results = $('#resultSection');
        if ($results.length) {
            $results.removeClass('hidden');
            $results[0].scrollIntoView({ behavior: 'smooth' });
        }
    }

    hideResults() {
        const $results = $('#resultSection');
        if ($results.length) {
            $results.addClass('hidden');
        }
    }

    limparFormulario() {
        $('#origemInput').val('');
        $('#destinoInput').val('');
        
        // Campo de preferências foi removido - verificar se existe antes de limpar
        const $preferenciasElement = $('#preferenciasInput');
        if ($preferenciasElement.length) {
            $preferenciasElement.val('');
        }
        
        this.hideResults();
        this.clearMarkers();
    }

    // ===== ROTEIROS SALVOS ===== //
    mostrarModalSalvarRoteiro() {
        // Verificar se usuário está logado
        if (!this.getToken()) {
            alert('Você precisa fazer login para salvar roteiros. Clique no botão "Entrar" no menu.');
            return;
        }
        
        if (!this.rotaAtual) {
            alert('Nenhuma rota foi gerada ainda. Faça uma busca primeiro.');
            return;
        }

        // Preencher resumo no modal
        $('#resumoOrigem').text(this.rotaAtual.cidade_origem);
        $('#resumoDestino').text(this.rotaAtual.cidade_destino);
        $('#resumoPreferencias').text(this.rotaAtual.preferencias || 'Nenhuma especificada');
        
        // Mostrar modal
        $('#modalSalvarRoteiro').prop('checked', true);
    }

    fecharModalSalvarRoteiro() {
        $('#modalSalvarRoteiro').prop('checked', false);
        $('#tituloRoteiro').val('');
    }

    async salvarRoteiro() {
        const titulo = $('#tituloRoteiro').val().trim();
        
        if (!titulo) {
            alert('Por favor, insira um título para o roteiro.');
            return;
        }

        if (!this.rotaAtual) {
            alert('Nenhuma rota disponível para salvar.');
            return;
        }

        try {
            const response = await $.ajax({
                url: `${this.API_BASE}/roteiros/`,
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getToken()}`
                },
                data: JSON.stringify({
                    titulo: titulo,
                    cidade_origem: this.rotaAtual.cidade_origem,
                    cidade_destino: this.rotaAtual.cidade_destino,
                    preferencias: this.rotaAtual.preferencias,
                    resposta_ai: this.rotaAtual.resposta_ai,
                    coordenadas_origem: this.rotaAtual.coordenadas_origem,
                    coordenadas_destino: this.rotaAtual.coordenadas_destino
                }),
                contentType: 'application/json'
            });

            this.fecharModalSalvarRoteiro();
            this.showNotification('Roteiro salvo com sucesso!', 'success');
            
            // Recarregar lista de roteiros salvos
            this.carregarRoteirosSalvos();
            
        } catch (error) {
            console.error('Erro ao salvar roteiro:', error);
            const errorMessage = error.responseJSON?.detail || error.statusText || 'Erro ao salvar roteiro';
            alert('Erro ao salvar roteiro: ' + errorMessage);
        }
    }

    async carregarRoteirosSalvos() {
        try {
            const response = await $.ajax({
                url: `${this.API_BASE}/roteiros/`,
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${this.getToken()}`
                }
            });

            this.exibirRoteirosSalvos(response);
            
        } catch (error) {
            console.error('Erro ao carregar roteiros:', error);
        }
    }

    exibirRoteirosSalvos(roteiros) {
        const $container = $('#listaRoteirosSalvos');
        
        if (roteiros.length === 0) {
            $container.html(`
                <div class="col-span-full text-center py-8 text-gray-500">
                    <i class="fas fa-bookmark text-4xl mb-4"></i>
                    <p>Nenhum roteiro salvo ainda.</p>
                    <p class="text-sm">Gere uma rota e clique em "Salvar Roteiro"</p>
                </div>
            `);
            return;
        }

        const roteirosHtml = roteiros.map(roteiro => `
            <div class="card bg-base-100 shadow-lg hover:shadow-xl transition-shadow">
                <div class="card-body p-4">
                    <h4 class="card-title text-lg">${roteiro.titulo}</h4>
                    <div class="text-sm space-y-1">
                        <div><strong>De:</strong> ${roteiro.cidade_origem}</div>
                        <div><strong>Para:</strong> ${roteiro.cidade_destino}</div>
                        <div class="text-xs text-gray-500">
                            Salvo em: ${new Date(roteiro.created_at).toLocaleDateString('pt-BR')}
                        </div>
                    </div>
                    <div class="card-actions justify-end mt-3">
                        <button class="btn btn-sm btn-outline" onclick="app.carregarRoteiro(${roteiro.id})">
                            <i class="fas fa-eye mr-1"></i>
                            Ver
                        </button>
                        <button class="btn btn-sm btn-error btn-outline" onclick="app.excluirRoteiro(${roteiro.id})">
                            <i class="fas fa-trash mr-1"></i>
                            Excluir
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
        
        $container.html(roteirosHtml);
    }

    async carregarRoteiro(id) {
        try {
            const response = await $.ajax({
                url: `${this.API_BASE}/roteiros/${id}`,
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${this.getToken()}`
                }
            });

            // Preencher formulário com dados do roteiro
            $('#origemInput').val(response.cidade_origem);
            $('#destinoInput').val(response.cidade_destino);
            
            // Campo de preferências foi removido - verificar se existe antes de preencher
            const $preferenciasElement = $('#preferenciasInput');
            if ($preferenciasElement.length) {
                $preferenciasElement.val(response.preferencias || '');
            }
            
            // Simular dados para exibição
            const data = {
                conteudo: response.resposta_ai,
                coordenadas_origem: response.coordenadas_origem,
                coordenadas_destino: response.coordenadas_destino,
                pontos: []
            };
            
            this.displayResults(data);
            this.showNotification('Roteiro carregado!', 'success');
            
        } catch (error) {
            console.error('Erro ao carregar roteiro:', error);
            const errorMessage = error.responseJSON?.detail || error.statusText || 'Erro ao carregar roteiro';
            alert('Erro ao carregar roteiro: ' + errorMessage);
        }
    }

    async excluirRoteiro(id) {
        if (!confirm('Tem certeza que deseja excluir este roteiro?')) {
            return;
        }

        try {
            await $.ajax({
                url: `${this.API_BASE}/roteiros/${id}`,
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${this.getToken()}`
                }
            });

            this.showNotification('Roteiro excluído com sucesso!', 'success');
            this.carregarRoteirosSalvos();
            
        } catch (error) {
            console.error('Erro ao excluir roteiro:', error);
            const errorMessage = error.responseJSON?.detail || error.statusText || 'Erro ao excluir roteiro';
            alert('Erro ao excluir roteiro: ' + errorMessage);
        }
    }

    showNotification(message, type = 'info') {
        // Implementar notificação toast se necessário
        console.log(`[${type.toUpperCase()}] ${message}`);
    }

    // ===== COLLAPSIBLE ROUTE SIDEBAR ===== //
    updateRouteSidebar(pontos) {
        // Atualizar informações da rota na sidebar
        this.updateRouteSidebarInfo();
        
        // Atualizar lista de pontos na sidebar
        const $pointsList = $('#pointsList');
        if (!$pointsList.length) return;
        
        if (!pontos || pontos.length === 0) {
            $pointsList.html(`
                <div class="no-points-message">
                    <p>Nenhum ponto turístico encontrado</p>
                </div>
            `);
            return;
        }
        
        const pontosHtml = pontos.map((ponto, index) => {
            const iconClass = this.getCategoryIcon(ponto.categoria);
            return `
                <div class="point-item" data-point-index="${index}" onclick="app.selectPoint(${index})">
                    <div class="point-header">
                        <h4 class="point-name">${ponto.nome}</h4>
                        <span class="point-category">
                            <i class="${iconClass}"></i>
                            ${ponto.categoria}
                        </span>
                    </div>
                    
                    <p class="point-description">${ponto.descricao}</p>
                    
                    <div class="point-info">
                        <span class="point-info-item">
                            <i class="fas fa-clock"></i>
                            <span>${ponto.tempo_visita_estimado}</span>
                        </span>
                        ${ponto.valor_entrada ? `
                            <span class="point-info-item">
                                <i class="fas fa-dollar-sign"></i>
                                <span>${ponto.valor_entrada}</span>
                            </span>
                        ` : ''}
                    </div>
                    
                    <div class="point-details">
                        ${ponto.endereco ? `
                            <div class="detail-row">
                                <span class="detail-label">
                                    <i class="fas fa-map-marker-alt"></i>
                                    Local:
                                </span>
                                <span class="detail-value">${ponto.endereco}</span>
                            </div>
                        ` : ''}
                        ${ponto.horario_funcionamento ? `
                            <div class="detail-row">
                                <span class="detail-label">
                                    <i class="fas fa-clock"></i>
                                    Horário:
                                </span>
                                <span class="detail-value">${ponto.horario_funcionamento}</span>
                            </div>
                        ` : ''}
                        ${ponto.dicas_importantes ? `
                            <div class="detail-row">
                                <span class="detail-label">
                                    <i class="fas fa-lightbulb"></i>
                                    Dicas:
                                </span>
                                <span class="detail-value">${ponto.dicas_importantes}</span>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
        }).join('');
        
        $pointsList.html(pontosHtml);
    }

    updateRouteSidebarInfo() {
        const $routeTitleMini = $('#routeTitleMini');
        const $routeDistanceMini = $('#routeDistanceMini');
        const $routeTimeMini = $('#routeTimeMini');
        
        if (this.rotaAtual && $routeTitleMini.length) {
            $routeTitleMini.text(`${this.rotaAtual.cidade_origem} → ${this.rotaAtual.cidade_destino}`);
        }
        
        if ($routeDistanceMini.length) {
            $routeDistanceMini.text('📏 Calculando...');
        }
        
        if ($routeTimeMini.length) {
            $routeTimeMini.text('⏱️ Calculando...');
        }
    }

    toggleRouteSidebar() {
        console.log('toggleRouteSidebar chamada');
        
        const $sidebar = $('#routeSidebar');
        const $openBtn = $('#sidebarOpenBtn');
        const $body = $('body');
        const $overlay = $('#sidebar-overlay');
        
        if (!$sidebar.length) {
            console.log('Sidebar não encontrada');
            return;
        }
        
        const isOpen = $sidebar.hasClass('open');
        console.log('Sidebar está aberta:', isOpen);
        
        if (isOpen) {
            // Fechar sidebar
            $sidebar.removeClass('open');
            $body.removeClass('sidebar-open');
            $overlay.removeClass('active');
            $openBtn.removeClass('hidden');
            console.log('Sidebar fechada');
        } else {
            // Abrir sidebar
            // Criar overlay se não existir
            if (!$overlay.length) {
                $('<div id="sidebar-overlay" class="sidebar-overlay"></div>')
                    .appendTo('body')
                    .on('click', () => this.toggleRouteSidebar());
            }
            
            $sidebar.addClass('open');
            $body.addClass('sidebar-open');
            $('#sidebar-overlay').addClass('active');
            $openBtn.addClass('hidden');
            console.log('Sidebar aberta');
        }
    }

    showRouteSidebar() {
        console.log('showRouteSidebar chamada');
        
        const $sidebar = $('#routeSidebar');
        const $openBtn = $('#sidebarOpenBtn');
        const $body = $('body');
        
        console.log('Elementos encontrados:', {
            sidebar: $sidebar.length,
            openBtn: $openBtn.length,
            body: $body.length
        });
        
        if ($sidebar.length) {
            $sidebar.removeClass('hidden');
            console.log('Hidden removido da sidebar');
            
            // Criar overlay se não existir
            if (!$('#sidebar-overlay').length) {
                $('<div id="sidebar-overlay" class="sidebar-overlay"></div>')
                    .appendTo('body')
                    .on('click', () => this.toggleRouteSidebar());
            }
            
            // Abrir automaticamente na primeira vez
            setTimeout(() => {
                $sidebar.addClass('open');
                $body.addClass('sidebar-open');
                $('#sidebar-overlay').addClass('active');
                console.log('Classes "open" e "sidebar-open" adicionadas');
            }, 100);
        }
        
        if ($openBtn.length) {
            $openBtn.removeClass('hidden');
            console.log('Hidden removido do botão abrir');
        }
    }

    hideRouteSidebar() {
        const $sidebar = $('#routeSidebar');
        const $openBtn = $('#sidebarOpenBtn');
        const $body = $('body');
        
        if ($sidebar.length) {
            $sidebar.removeClass('open').addClass('hidden');
            $body.removeClass('sidebar-open');
        }
        
        if ($openBtn.length) {
            $openBtn.addClass('hidden');
        }
    }

    // ===== BRAZIL MAP ROUTE VISUALIZATION ===== //
    addPointsToBrazilMap(pontos) {
        console.log('Adicionando pontos ao mapa do Brasil:', pontos);
        
        if (!this.heroMap || !pontos || pontos.length === 0) {
            console.warn('Mapa do Brasil não disponível ou sem pontos');
            return;
        }

        // Limpar marcadores de rotas anteriores
        this.clearBrazilMapRoute();

        const bounds = [];
        const routeCoordinates = [];

        // Adicionar marcadores para cada ponto turístico
        pontos.forEach((ponto, index) => {
            console.log(`Processando ponto ${index}:`, ponto);
            
            if (ponto.coordenadas) {
                let lat, lng;
                
                // Verificar diferentes formatos de coordenadas
                if (typeof ponto.coordenadas === 'string') {
                    const coords = ponto.coordenadas.split(',').map(c => parseFloat(c.trim()));
                    lat = coords[0];
                    lng = coords[1];
                } else if (ponto.coordenadas.lat && ponto.coordenadas.lng) {
                    lat = ponto.coordenadas.lat;
                    lng = ponto.coordenadas.lng;
                } else if (Array.isArray(ponto.coordenadas)) {
                    lat = ponto.coordenadas[0];
                    lng = ponto.coordenadas[1];
                }

                console.log(`Coordenadas do ponto ${index}: lat=${lat}, lng=${lng}`);

                if (lat && lng && !isNaN(lat) && !isNaN(lng)) {
                    // Criar marcador para ponto turístico
                    const routeMarker = L.circleMarker([lat, lng], {
                        radius: 10,
                        fillColor: this.getMarkerColor(ponto.categoria),
                        color: '#fff',
                        weight: 3,
                        opacity: 1,
                        fillOpacity: 0.9
                    })
                    .bindPopup(this.createRoutePopupContent(ponto, index))
                    .on('click', () => this.selectPoint(index));
                    
                    // Adicionar número do ponto
                    const numberMarker = L.marker([lat, lng], {
                        icon: L.divIcon({
                            className: 'route-number-marker',
                            html: `<div class="route-number">${index + 1}</div>`,
                            iconSize: [24, 24],
                            iconAnchor: [12, 12]
                        })
                    });
                    
                    // Adicionar ao array de marcadores da rota
                    if (!this.routeMarkers) this.routeMarkers = [];
                    this.routeMarkers.push(routeMarker);
                    this.routeMarkers.push(numberMarker);
                    
                    routeMarker.addTo(this.heroMap);
                    numberMarker.addTo(this.heroMap);
                    bounds.push([lat, lng]);
                    routeCoordinates.push([lat, lng]);
                    
                    console.log(`Marcador ${index} adicionado ao mapa`);
                } else {
                    console.warn(`Coordenadas inválidas para ponto ${index}:`, ponto.coordenadas);
                }
            } else {
                console.warn(`Ponto ${index} sem coordenadas:`, ponto);
            }
        });

        console.log('Coordenadas da rota:', routeCoordinates);

        // Desenhar rota mais realista se possível
        if (routeCoordinates.length > 1) {
            console.log('Tentando desenhar rota com OSRM...');
            this.drawRouteWithOSRM(routeCoordinates);
            
            // Dar zoom inicial na origem (primeiro ponto)
            const origem = routeCoordinates[0];
            setTimeout(() => {
                console.log('Focando na origem:', origem);
                this.heroMap.setView(origem, 12, {
                    animate: true,
                    duration: 1.5
                });
                
                // Depois de 3 segundos, mostrar a rota completa
                setTimeout(() => {
                    console.log('Mostrando rota completa');
                    this.heroMap.fitBounds(bounds, { 
                        padding: [50, 50],
                        animate: true,
                        duration: 1.5
                    });
                }, 3000);
            }, 1000);
            
        } else if (routeCoordinates.length === 1) {
            console.log('Apenas um ponto, centralizando mapa');
            this.heroMap.setView(routeCoordinates[0], 12, {
                animate: true,
                duration: 1.5
            });
        }
        
        console.log('Pontos adicionados com sucesso!');
    }

    async drawRouteWithOSRM(coordinates) {
        console.log('Desenho de rota OSRM iniciado com coordenadas:', coordinates);
        
        try {
            // Usar OSRM para desenhar rota mais realista
            const waypoints = coordinates.map(coord => `${coord[1]},${coord[0]}`).join(';');
            const osrmUrl = `https://router.project-osrm.org/route/v1/driving/${waypoints}?overview=full&geometries=geojson`;
            
            console.log('URL OSRM:', osrmUrl);
            
            const data = await $.ajax({
                url: osrmUrl,
                method: 'GET',
                dataType: 'json'
            });
            
            console.log('Resposta OSRM:', data);
            
            if (data.routes && data.routes[0]) {
                const route = data.routes[0];
                const routeCoords = route.geometry.coordinates.map(coord => [coord[1], coord[0]]);
                
                console.log('Coordenadas da rota OSRM:', routeCoords.length, 'pontos');
                
                // Desenhar rota realista com efeito visual melhorado
                this.routeLine = L.polyline(routeCoords, {
                    color: '#3B82F6',
                    weight: 5,
                    opacity: 0.8,
                    smoothFactor: 1,
                    dashArray: null // Linha sólida para rotas OSRM
                }).addTo(this.heroMap);
                
                // Adicionar uma linha de sombra para melhor visualização
                const shadowLine = L.polyline(routeCoords, {
                    color: '#1E40AF',
                    weight: 7,
                    opacity: 0.3,
                    smoothFactor: 1
                }).addTo(this.heroMap);
                
                // Adicionar à lista de elementos da rota para limpeza posterior
                if (!this.routeElements) this.routeElements = [];
                this.routeElements.push(shadowLine);
                
                console.log('Rota OSRM adicionada ao mapa com sombra');
                
                // Adicionar distância e tempo estimado se disponível
                if (route.distance && route.duration) {
                    const distance = (route.distance / 1000).toFixed(1) + ' km';
                    const duration = Math.round(route.duration / 60) + ' min';
                    
                    console.log('Distância e tempo calculados:', distance, duration);
                    
                    // Atualizar informações da rota
                    this.updateRouteDistance(distance, duration);
                }
            } else {
                console.warn('OSRM não retornou rotas válidas, usando linha simples');
                // Fallback: linha simples
                this.drawSimpleRoute(coordinates);
            }
        } catch (error) {
            console.warn('Erro ao obter rota OSRM, usando linha simples:', error);
            this.drawSimpleRoute(coordinates);
        }
    }

    drawSimpleRoute(coordinates) {
        console.log('Desenhando rota simples com coordenadas:', coordinates);
        
        // Desenhar linha de sombra primeiro (mais grossa e mais escura)
        const shadowLine = L.polyline(coordinates, {
            color: '#1E40AF',
            weight: 7,
            opacity: 0.3,
            smoothFactor: 1,
            dashArray: '12, 7'
        }).addTo(this.heroMap);
        
        // Desenhar linha principal por cima
        this.routeLine = L.polyline(coordinates, {
            color: '#3B82F6',
            weight: 5,
            opacity: 0.9,
            smoothFactor: 1,
            dashArray: '10, 5'
        }).addTo(this.heroMap);
        
        // Adicionar à lista de elementos da rota para limpeza posterior
        if (!this.routeElements) this.routeElements = [];
        this.routeElements.push(shadowLine);
        
        console.log('Rota simples adicionada ao mapa com efeito visual');
    }

    updateRouteDistance(distance, duration) {
        console.log('Atualizando distância da rota:', distance, duration);
        
        // Atualizar elementos na sidebar
        const $routeDistance = $('#routeDistance');
        const $routeTime = $('#routeTime');
        
        console.log('Elementos encontrados:', {
            routeDistance: $routeDistance.length ? 'SIM' : 'NÃO',
            routeTime: $routeTime.length ? 'SIM' : 'NÃO'
        });
        
        if ($routeDistance.length) {
            $routeDistance.html(`<i class="fas fa-route"></i> ${distance}`);
            console.log('Distância atualizada');
        }
        
        if ($routeTime.length) {
            $routeTime.html(`<i class="fas fa-clock"></i> ${duration}`);
            console.log('Tempo atualizado');
        }
    }

    createRoutePopupContent(ponto, index) {
        const iconClass = this.getCategoryIcon(ponto.categoria);
        const number = index + 1;
        return `
            <div class="route-popup">
                <div class="popup-header">
                    <span class="popup-number">${number}</span>
                    <h4 class="popup-title">${ponto.nome}</h4>
                </div>
                <p class="popup-category">
                    <i class="${iconClass}"></i> 
                    ${ponto.categoria}
                </p>
                <p class="popup-description">${ponto.descricao}</p>
                ${ponto.tempo_visita_estimado ? `
                    <p class="popup-time">
                        <i class="fas fa-clock"></i> 
                        ${ponto.tempo_visita_estimado}
                    </p>
                ` : ''}
                ${ponto.valor_entrada ? `
                    <p class="popup-price">
                        <i class="fas fa-dollar-sign"></i> 
                        ${ponto.valor_entrada}
                    </p>
                ` : ''}
            </div>
        `;
    }

    clearBrazilMapRoute() {
        // Limpar marcadores de rota anterior
        if (this.routeMarkers) {
            this.routeMarkers.forEach(marker => {
                this.heroMap.removeLayer(marker);
            });
            this.routeMarkers = [];
        }

        // Limpar linha da rota anterior
        if (this.routeLine) {
            this.heroMap.removeLayer(this.routeLine);
            this.routeLine = null;
        }
        
        // Limpar elementos visuais extras (sombras, etc.)
        if (this.routeElements) {
            this.routeElements.forEach(element => {
                this.heroMap.removeLayer(element);
            });
            this.routeElements = [];
        }
    }

    // ===== MAP ROUTE VISUALIZATION ===== //
    addRouteToMap(pontos) {
        if (!this.map || !pontos || pontos.length === 0) return;

        // Limpar marcadores e rotas existentes
        this.clearMarkers();
        this.clearRoute();

        const bounds = [];
        const routeCoordinates = [];

        // Adicionar marcadores para cada ponto
        pontos.forEach((ponto, index) => {
            if (ponto.coordenadas) {
                let lat, lng;
                
                // Verificar diferentes formatos de coordenadas
                if (typeof ponto.coordenadas === 'string') {
                    const coords = ponto.coordenadas.split(',').map(c => parseFloat(c.trim()));
                    lat = coords[0];
                    lng = coords[1];
                } else if (ponto.coordenadas.lat && ponto.coordenadas.lng) {
                    lat = ponto.coordenadas.lat;
                    lng = ponto.coordenadas.lng;
                } else if (Array.isArray(ponto.coordenadas)) {
                    lat = ponto.coordenadas[0];
                    lng = ponto.coordenadas[1];
                }

                if (lat && lng && !isNaN(lat) && !isNaN(lng)) {
                    // Criar marcador personalizado
                    const customIcon = this.createCustomMarkerIcon(index, ponto.categoria);
                    
                    const marker = L.marker([lat, lng], { icon: customIcon })
                        .bindPopup(this.createPopupContent(ponto))
                        .on('click', () => this.selectPoint(index));
                    
                    this.markers.push(marker);
                    marker.addTo(this.map);
                    bounds.push([lat, lng]);
                    routeCoordinates.push([lat, lng]);
                }
            }
        });

        // Desenhar linha da rota conectando os pontos
        if (routeCoordinates.length > 1) {
            this.currentRoute = L.polyline(routeCoordinates, {
                color: '#3B82F6',
                weight: 4,
                opacity: 0.7,
                smoothFactor: 1
            }).addTo(this.map);
        }

        // Ajustar visualização para mostrar todos os pontos
        if (bounds.length > 0) {
            this.map.fitBounds(bounds, { padding: [30, 30] });
        }
    }

    createCustomMarkerIcon(index, categoria) {
        const color = this.getMarkerColor(categoria);
        const number = index + 1;
        
        return L.divIcon({
            className: 'custom-marker',
            html: `
                <div class="marker-pin" style="background-color: ${color};">
                    <span class="marker-number">${number}</span>
                </div>
                <div class="marker-shadow"></div>
            `,
            iconSize: [30, 42],
            iconAnchor: [15, 42],
            popupAnchor: [0, -42]
        });
    }

    createHighlightMarkerIcon(index, categoria) {
        const color = this.getMarkerColor(categoria);
        const number = index + 1;
        
        return L.divIcon({
            className: 'custom-marker highlight',
            html: `
                <div class="marker-pin highlight" style="background-color: ${color}; transform: scale(1.2);">
                    <span class="marker-number">${number}</span>
                </div>
                <div class="marker-shadow"></div>
            `,
            iconSize: [36, 50],
            iconAnchor: [18, 50],
            popupAnchor: [0, -50]
        });
    }

    getMarkerColor(categoria) {
        const colorMap = {
            'natural': '#22C55E',     // Verde
            'histórico': '#8B5CF6',   // Roxo
            'cultural': '#F59E0B',    // Amarelo
            'religioso': '#3B82F6',   // Azul
            'gastronômico': '#EF4444', // Vermelho
            'aventura': '#F97316',    // Laranja
            'praia': '#06B6D4',       // Ciano
            'default': '#6B7280'      // Cinza
        };
        
        for (const [key, color] of Object.entries(colorMap)) {
            if (categoria && categoria.toLowerCase().includes(key)) {
                return color;
            }
        }
        
        return colorMap.default;
    }

    createPopupContent(ponto) {
        const categoria = this.getCategoryIcon(ponto.categoria);
        return `
            <div class="map-popup">
                <h4 class="popup-title">${ponto.nome}</h4>
                <p class="popup-category">${categoria} ${ponto.categoria}</p>
                <p class="popup-description">${ponto.descricao}</p>
                ${ponto.tempo_visita_estimado ? `
                    <p class="popup-time">⏱️ ${ponto.tempo_visita_estimado}</p>
                ` : ''}
                ${ponto.valor_entrada ? `
                    <p class="popup-price">💰 ${ponto.valor_entrada}</p>
                ` : ''}
            </div>
        `;
    }

    getDefaultMarkerIcon() {
        return L.icon({
            iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
            shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        });
    }

    getHighlightMarkerIcon() {
        return L.icon({
            iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
            shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
            iconSize: [30, 49],
            iconAnchor: [15, 49],
            popupAnchor: [1, -41],
            shadowSize: [49, 49]
        });
    }

    clearRoute() {
        if (this.currentRoute) {
            this.map.removeLayer(this.currentRoute);
            this.currentRoute = null;
        }
    }
}

// Initialize app when DOM is loaded
$(document).ready(() => {
    window.app = new TurismoApp();
});

// Global functions for compatibility
window.scrollToPlanning = () => {
    const $planningSection = $('#planningSection');
    if ($planningSection.length) {
        $planningSection[0].scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
};