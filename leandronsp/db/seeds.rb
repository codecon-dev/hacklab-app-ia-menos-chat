# db/seeds.rb

puts "🌱 Cleaning old data..."
Dish.destroy_all
User.destroy_all

puts "👥 Creating test users..."

users_data = [
  { email: "alice@macedo.com", password: "senha123" },
  { email: "bob@macedo.com", password: "senha123" },
  { email: "carol@macedo.com", password: "senha123" }
]

users = users_data.map do |data|
  user = User.create!(data)
  puts "✅ User created: #{user.email}"
  user
end

puts "\n📸 Creating dishes with images for each user..."

# Each user gets 3 dishes
dishes_per_user = [
  [
    { name: "Feijoada Completa", image: "feijoada.jpg", favorite: true },
    { name: "Pão de Queijo", image: "pao_de_queijo.jpg", favorite: true },
    { name: "Churrasco Brasileiro", image: "churrasco.jpg", favorite: false }
  ],
  [
    { name: "Pizza Margherita", image: "pizza_margherita.jpg", favorite: true },
    { name: "Sushi Roll", image: "sushi_platter.jpg", favorite: false },
    { name: "Burger Artesanal", image: "burger.jpg", favorite: true }
  ],
  [
    { name: "Pasta Carbonara", image: "pasta_carbonara.jpg", favorite: true },
    { name: "Ramen Japonês", image: "ramen.jpg", favorite: false },
    { name: "Tacos Mexicanos", image: "tacos.jpg", favorite: true }
  ]
]

users.each_with_index do |user, index|
  puts "\n🍽️  Creating dishes for #{user.email}..."

  dishes_per_user[index].each do |data|
    image_path = Rails.root.join("storage", "seed_images", data[:image])

    unless File.exist?(image_path)
      puts "❌ Image not found: #{data[:image]}"
      next
    end

    dish = user.dishes.build(
      name: I18n.t("ai.placeholder"),
      favorite: data[:favorite],
      description: I18n.t("ai.placeholder"),
      pairing_suggestions: []
    )

    dish.image.attach(
      io: File.open(image_path),
      filename: data[:image],
      content_type: "image/jpeg"
    )

    if dish.save
      # Enqueue background job for AI analysis
      AnalyzeDishJob.perform_later(dish.id)
      puts "   ✅ #{data[:name]} created, analysis queued"
    else
      puts "   ❌ Error creating #{data[:name]}: #{dish.errors.full_messages.join(', ')}"
    end
  end
end

puts "\n🎉 Seed complete!"
puts "   📊 #{User.count} users created"
puts "   🍽️  #{Dish.count} dishes created"
puts "\n📝 Test credentials:"
users_data.each do |data|
  puts "   Email: #{data[:email]} | Password: #{data[:password]}"
end
