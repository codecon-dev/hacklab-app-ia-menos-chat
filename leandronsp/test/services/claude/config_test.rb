# frozen_string_literal: true

require "test_helper"

module Claude
  class ConfigTest < ActiveSupport::TestCase
    self.use_transactional_tests = false

    def with_env(vars)
      original = {}
      vars.each do |key, value|
        original[key] = ENV[key]
        ENV[key] = value
      end
      yield
    ensure
      original.each { |key, value| ENV[key] = value }
    end

    test 'returns default model when CLAUDE_MODEL not set' do
      with_env('CLAUDE_MODEL' => nil) do
        assert_equal 'claude-sonnet-4-5-20250929', Config.model
      end
    end

    test 'returns custom model when CLAUDE_MODEL set' do
      with_env('CLAUDE_MODEL' => 'claude-opus-4-20250514') do
        assert_equal 'claude-opus-4-20250514', Config.model
      end
    end

    test 'returns default max_tokens when not set' do
      with_env('MAX_TOKENS' => nil) do
        assert_equal 4096, Config.max_tokens
      end
    end

    test 'returns custom max_tokens when set' do
      with_env('MAX_TOKENS' => '2048') do
        assert_equal 2048, Config.max_tokens
      end
    end

    test 'philosophical_mode? returns false by default' do
      with_env('MACEDO_MOOD' => nil) do
        assert_not Config.philosophical_mode?
      end
    end

    test 'philosophical_mode? returns true when MACEDO_MOOD is philosophical' do
      with_env('MACEDO_MOOD' => 'philosophical') do
        assert Config.philosophical_mode?
      end
    end

    test 'validate! raises when ANTHROPIC_API_KEY missing' do
      with_env('ANTHROPIC_API_KEY' => nil) do
        error = assert_raises(RuntimeError) { Config.validate! }
        assert_match(/ANTHROPIC_API_KEY/, error.message)
      end
    end

    test 'validate! raises when MAX_TOKENS is zero' do
      with_env('ANTHROPIC_API_KEY' => 'test-key', 'MAX_TOKENS' => '0') do
        error = assert_raises(RuntimeError) { Config.validate! }
        assert_match(/MAX_TOKENS must be positive/, error.message)
      end
    end

    test 'validate! raises when TEMPERATURE out of range' do
      with_env('ANTHROPIC_API_KEY' => 'test-key', 'TEMPERATURE' => '3.0') do
        error = assert_raises(RuntimeError) { Config.validate! }
        assert_match(/TEMPERATURE must be between/, error.message)
      end
    end
  end
end
