# frozen_string_literal: true

require "anthropic"

module Claude
  # Thin wrapper around ruby-anthropic gem
  # Handles API communication with timeout and error normalization
  class Client
    include Retriable

    def initialize
      @client = Anthropic::Client.new(
        access_token: Config.api_key,
        request_timeout: Config.timeout
      )
    end

    # Send a simple text message to Claude
    # @param message [String] the message text
    # @param system [String, nil] optional system prompt
    # @return [String] Claude's response text
    def chat(message, system: nil)
      with_retry do
        params = build_params(
          messages: [ { role: "user", content: message } ],
          system: system
        )

        response = @client.messages(parameters: params)
        extract_text(response)
      end
    end

    # Send messages with optional image support
    # @param messages [Array<Hash>] array of message hashes with role and content
    # @param system [String, nil] optional system prompt
    # @return [String] Claude's response text
    def messages(messages, system: nil)
      with_retry do
        params = build_params(messages: messages, system: system)
        response = @client.messages(parameters: params)
        extract_text(response)
      end
    end

    private

    def build_params(messages:, system: nil)
      params = {
        model: Config.model,
        max_tokens: Config.max_tokens,
        temperature: Config.temperature,
        messages: messages
      }
      params[:system] = system if system.present?
      params
    end

    def extract_text(response)
      response.dig("content", 0, "text") || ""
    end
  end
end
