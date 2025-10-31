# frozen_string_literal: true

require "base64"
require "json"

module Claude
  # Dish image analyzer using Claude AI vision capabilities
  # Analyzes food images and provides creative pairing suggestions
  class Analyzer
    attr_reader :image_blob

    def initialize(image_blob)
      @image_blob = image_blob
      @client = Client.new
    end

    # Analyze dish image and return structured data
    # @return [Hash] dish information with pairing suggestions
    def analyze
      image_data = encode_image
      prompt = build_prompt

      content = [
        {
          type: "image",
          source: {
            type: "base64",
            media_type: image_blob.content_type,
            data: image_data
          }
        },
        {
          type: "text",
          text: prompt
        }
      ]

      response = @client.messages([ { role: "user", content: content } ])
      parse_response(response)
    rescue JSON::ParserError => e
      Rails.logger.error("Failed to parse Claude response: #{e.message}")
      fallback_response
    rescue StandardError => e
      Rails.logger.error("Dish analysis failed: #{e.message}")
      fallback_response
    end

    private

    def encode_image
      Base64.strict_encode64(@image_blob.download)
    end

    def build_prompt
      base_prompt = <<~PROMPT
        IMPORTANTE: Responda SEMPRE em português brasileiro. Todas as suas respostas devem estar em português.

        Você é um sommelier e especialista em harmonização de alimentos extremamente criativo e conhecedor da cultura brasileira.

        Analise esta imagem de um prato de comida e retorne APENAS um JSON válido em português com a seguinte estrutura:

        {
          "dish_name": "Feijoada Completa",
          "description": "Feijoada tradicional brasileira com feijão preto, carnes variadas e acompanhamentos",
          "dish_type": "Brasileira",
          "cultural_context": "Prato tradicional brasileiro, geralmente servido aos sábados em família",
          "pairing_suggestions": [
            {
              "type": "cocktail",
              "name": "Caipirinha de Limão",
              "description": "A acidez do limão corta a gordura das carnes e realça os sabores",
              "is_easter_egg": true
            }
          ]
        }

        ATENÇÃO: Todos os campos de texto (dish_name, description, cultural_context, name, description) devem estar em português brasileiro.

        REGRAS ESPECIAIS - EASTER EGGS BRASILEIROS:
        - Se for arroz e feijão: inclua "Guaraná Antarctica gelado" como sugestão cultural nostálgica
        - Se for feijoada: inclua "Caipirinha de limão" e "Laranja fatiada"
        - Se for churrasco: inclua "Cerveja bem gelada (Skol, Brahma ou Antarctica)"
        - Se for pão de queijo: inclua "Café preto coado" ou "Suco de laranja natural"
        - Se for coxinha: inclua "Caldo de cana" ou "Refrigerante de guaraná"
        - Se for pastel: inclua "Caldo de cana com limão"
        - Se for açaí: inclua "Complementos como banana, granola e mel"
        - Se for brigadeiro/doce brasileiro: inclua "Café espresso"

        Seja criativo, use linguagem acessível e amigável, e traga sugestões que vão desde opções sofisticadas até nostálgicas e culturais.
      PROMPT

      philosophical_addon = <<~ADDON

        MODO FILOSÓFICO ATIVADO: Adicione reflexões profundas sobre a relação entre comida, memória e identidade cultural.
      ADDON

      Config.philosophical_mode? ? base_prompt + philosophical_addon : base_prompt
    end

    def parse_response(response)
      # Extract JSON from response (handle markdown code blocks if present)
      json_text = response.strip
      json_text = json_text.gsub(/^```json\s*/, "").gsub(/\s*```$/, "")

      data = JSON.parse(json_text)

      {
        dish_name: data["dish_name"],
        description: data["description"],
        dish_type: data["dish_type"],
        cultural_context: data["cultural_context"],
        pairing_suggestions: data["pairing_suggestions"]
      }
    end

    def fallback_response
      {
        dish_name: "Prato Delicioso",
        description: "Não conseguimos analisar este prato no momento, mas parece delicioso!",
        dish_type: "Desconhecido",
        cultural_context: "Análise temporariamente indisponível",
        pairing_suggestions: [
          {
            "type" => "non_alcoholic",
            "name" => "Água gelada",
            "description" => "Sempre uma boa escolha",
            "is_easter_egg" => false
          }
        ]
      }
    end
  end
end
