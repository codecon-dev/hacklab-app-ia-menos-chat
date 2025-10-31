require 'anthropic'
require 'base64'

client = Anthropic::Client.new(
  access_token: ENV['ANTHROPIC_API_KEY']
)

image_path = 'image.jpg'
image_data = Base64.strict_encode64(File.binread(image_path))

response = client.messages(
  parameters: {
    model: 'claude-sonnet-4-5-20250929',
    max_tokens: 1024,
    messages: [
      {
        role: 'user',
        content: [
          {
            type: 'image',
            source: {
              type: 'base64',
              media_type: 'image/jpeg', # ou 'image/png' dependendo do tipo de imagem
              data: image_data
            }
          },
          {
            type: 'text',
            text: 'Qual tipo de vinho acompanha este prato? Seja conciso e direto.'
          }
        ]
      }
    ]
  }
)

puts response.dig('content', 0, 'text')
