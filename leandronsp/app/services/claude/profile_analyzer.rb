# frozen_string_literal: true

module Claude
  # Analyzes user eating patterns and generates personalized profile descriptions
  # Uses Claude AI to create creative descriptions based on dish preferences
  class ProfileAnalyzer
    attr_reader :user

    def initialize(user)
      @user = user
      @client = Client.new
    end

    # Analyze user's dishes and generate a profile description
    # @return [String] personalized profile description
    def analyze
      return default_profile if user.dishes.empty?

      dishes_summary = build_dishes_summary
      prompt = build_prompt(dishes_summary)

      @client.chat(prompt)
    rescue StandardError => e
      Rails.logger.error("Profile analysis failed for user #{user.id}: #{e.message}")
      default_profile
    end

    private

    def build_dishes_summary
      dishes = user.dishes.includes(:image_attachment).limit(20)

      summary = {
        total_dishes: user.dishes.count,
        dish_types: dishes.group(:dish_type).count,
        favorite_dishes: dishes.where(favorite: true).pluck(:name, :dish_type),
        recent_dishes: dishes.order(created_at: :desc).limit(5).pluck(:name, :dish_type)
      }

      summary
    end

    def build_prompt(summary)
      <<~PROMPT
        IMPORTANTE: Responda SEMPRE em português brasileiro.

        Você é um crítico gastronômico criativo e bem-humorado que analisa perfis de pessoas baseado no que elas comem.

        Analise o perfil alimentar desta pessoa e crie UMA ÚNICA FRASE curta (máximo 15 palavras) e criativa que descreva o estilo gastronômico dela.

        Dados do perfil:
        - Total de pratos: #{summary[:total_dishes]}
        - Tipos de comida preferidos: #{summary[:dish_types].to_json}
        - Pratos favoritos: #{summary[:favorite_dishes].map { |name, type| "#{name} (#{type})" }.join(", ")}
        - Pratos recentes: #{summary[:recent_dishes].map { |name, type| "#{name} (#{type})" }.join(", ")}

        EXEMPLOS de frases que você deve criar (NÃO copie estes exemplos, crie algo único):
        - "Uma pessoa clássica que sabe bem o sabor brasileiro"
        - "Aventureiro gastronômico que não tem medo de experimentar"
        - "Alma brasileira com pitadas de curiosidade internacional"
        - "Tradicional no coração, moderno no paladar"
        - "Explorador de sabores que respeita as raízes"

        REGRAS:
        1. Seja criativo e único
        2. Use linguagem brasileira informal e acessível
        3. Máximo 15 palavras
        4. Capture a essência do perfil alimentar
        5. Se houver muita comida brasileira (arroz e feijão, feijoada, churrasco), enfatize isso
        6. Se houver variedade internacional, mencione o lado explorador

        Retorne APENAS a frase, sem aspas, sem explicações.
      PROMPT
    end

    def default_profile
      "Começando a jornada gastronômica"
    end
  end
end
