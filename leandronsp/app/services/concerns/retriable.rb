# frozen_string_literal: true

# Retry logic with exponential backoff
# Usage: include Retriable, then call with_retry { block }
module Retriable
  MAX_RETRIES = 3
  BASE_DELAY = 1 # seconds

  class RetryExhausted < StandardError; end

  def with_retry(max_retries: MAX_RETRIES, &block)
    attempt = 0

    begin
      attempt += 1
      block.call
    rescue StandardError => e
      if attempt < max_retries && retryable_error?(e)
        delay = BASE_DELAY * (2**(attempt - 1)) # Exponential backoff: 1s, 2s, 4s
        Rails.logger.warn("Retry attempt #{attempt}/#{max_retries} after #{delay}s: #{sanitize_error(e)}")
        sleep(delay)
        retry
      else
        Rails.logger.error("Retry exhausted or non-retryable error: #{sanitize_error(e)}")
        raise RetryExhausted, "Failed after #{attempt} attempts: #{e.message}"
      end
    end
  end

  private

  def retryable_error?(error)
    # Retry on network errors, timeouts, rate limits
    error.is_a?(Faraday::TimeoutError) ||
      error.is_a?(Faraday::ConnectionFailed) ||
      (error.respond_to?(:response) && error.response&.dig("error", "type") == "rate_limit_error")
  end

  def sanitize_error(error)
    # Remove API keys from error messages
    error.message.gsub(/sk-ant-[a-zA-Z0-9-]+/, "[API_KEY_REDACTED]")
  end
end
