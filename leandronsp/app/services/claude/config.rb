# frozen_string_literal: true

module Claude
  # Configuration loader for Claude API
  # Loads settings from environment variables with sensible defaults
  class Config
    class << self
      def api_key
        ENV["ANTHROPIC_API_KEY"]
      end

      def model
        ENV.fetch("CLAUDE_MODEL", "claude-sonnet-4-5-20250929")
      end

      def max_tokens
        ENV.fetch("MAX_TOKENS", "4096").to_i
      end

      def temperature
        ENV.fetch("TEMPERATURE", "1.0").to_f
      end

      def timeout
        ENV.fetch("CLAUDE_TIMEOUT", "60").to_i
      end

      def philosophical_mode?
        ENV["MACEDO_MOOD"] == "philosophical"
      end

      def validate!
        raise "ANTHROPIC_API_KEY environment variable is required" if api_key.nil? || api_key.empty?
        raise "MAX_TOKENS must be positive" if max_tokens <= 0
        raise "TEMPERATURE must be between 0 and 2" unless (0..2).cover?(temperature)
      end
    end
  end
end
