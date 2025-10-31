require 'anthropic'

client = Anthropic::Client.new(access_token: ENV.fetch('ANTHROPIC_API_KEY'))

response = client.messages(
  parameters: {
    model: 'claude-sonnet-4-20250514',
    max_tokens: 1024,
    messages: [
      { role: 'user', content: 'Olá, Claude! Me diga uma curiosidade interessante.' }
    ]
  }
)

puts response.dig('content', 0, 'text')
