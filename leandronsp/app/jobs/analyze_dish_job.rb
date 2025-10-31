# frozen_string_literal: true

# Background job to analyze dish images using Claude AI
# Enqueued after dish creation to avoid blocking HTTP requests
class AnalyzeDishJob < ApplicationJob
  include Retriable

  queue_as :default

  # Analyze dish image and update attributes with AI results
  # @param dish_id [Integer] ID of the dish to analyze
  def perform(dish_id)
    dish = Dish.find(dish_id)

    Rails.logger.info("Starting analysis for dish #{dish_id}")

    with_retry do
      analyzer = Claude::Analyzer.new(dish.image)
      result = analyzer.analyze

      dish.update!(
        name: result[:dish_name] || dish.name,
        description: result[:description],
        pairing_suggestions: result[:pairing_suggestions],
        dish_type: result[:dish_type]
      )

      Rails.logger.info("Successfully analyzed dish #{dish_id}")
    end
  rescue ActiveRecord::RecordNotFound
    Rails.logger.warn("Dish #{dish_id} not found, skipping analysis")
  rescue StandardError => e
    Rails.logger.error("Failed to analyze dish #{dish_id}: #{e.message}")
    dish&.update(
      description: I18n.t("ai.analysis_unavailable"),
      pairing_suggestions: []
    )
  end
end
