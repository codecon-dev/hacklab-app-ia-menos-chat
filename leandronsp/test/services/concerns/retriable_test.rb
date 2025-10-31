# frozen_string_literal: true

require "test_helper"

class RetriableTest < ActiveSupport::TestCase
  self.use_transactional_tests = false

  class DummyService
    include Retriable

    attr_accessor :attempts, :should_succeed_after

    def initialize
      @attempts = 0
      @should_succeed_after = nil
    end

    def flaky_operation
      with_retry do
        @attempts += 1
        raise Faraday::TimeoutError, 'Timeout!' unless @should_succeed_after && @attempts >= @should_succeed_after
        'success'
      end
    end
  end

  setup do
    @service = DummyService.new
  end

  test 'succeeds on first attempt when no errors' do
    @service.should_succeed_after = 1
    result = @service.flaky_operation

    assert_equal 'success', result
    assert_equal 1, @service.attempts
  end

  test 'retries on retryable errors' do
    @service.should_succeed_after = 3
    result = @service.flaky_operation

    assert_equal 'success', result
    assert_equal 3, @service.attempts
  end

  test 'raises RetryExhausted after max retries' do
    @service.should_succeed_after = 10 # Will never succeed within retry limit

    error = assert_raises(Retriable::RetryExhausted) do
      @service.flaky_operation
    end

    assert_match(/Failed after 3 attempts/, error.message)
  end

  test 'sanitizes API keys in error messages' do
    service = DummyService.new

    error = StandardError.new('Error with key: sk-ant-secret123')
    sanitized = service.send(:sanitize_error, error)

    assert_match(/API_KEY_REDACTED/, sanitized)
    assert_no_match(/sk-ant-secret123/, sanitized)
  end
end
