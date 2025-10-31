# frozen_string_literal: true

# Claude API Configuration Initializer
# Validates required environment variables on boot
Rails.application.config.to_prepare do
  Claude::Config.validate! unless Rails.env.test?
end
