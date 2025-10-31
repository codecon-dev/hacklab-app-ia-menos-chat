namespace :search do
  desc "Rebuild full-text search index for Dish model"
  task rebuild_dishes: :environment do
    puts "🔨 Rebuilding search index for Dish..."

    count = Dish.rebuild_search_index

    puts "✅ Done! Indexed #{count} dishes."
  end

  desc "Rebuild all full-text search indexes"
  task rebuild_all: [:rebuild_dishes] do
    puts "✅ All search indexes rebuilt successfully!"
  end

  desc "Verify FTS5 extension is available"
  task check_fts5: :environment do
    result = ActiveRecord::Base.connection.execute(
      "SELECT * FROM pragma_compile_options WHERE compile_options LIKE '%FTS5%'"
    ).first

    if result
      puts "✅ FTS5 extension is available and enabled"
    else
      puts "❌ FTS5 extension is NOT available"
      puts "   Please ensure SQLite is compiled with FTS5 support"
    end
  end
end
