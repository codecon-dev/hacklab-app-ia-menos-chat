class CreateDishesFtsTable < ActiveRecord::Migration[8.0]
  def up
    # Create standalone FTS5 virtual table with prefix indexing
    # Note: We use ActiveRecord callbacks instead of SQL triggers
    execute <<~SQL
      CREATE VIRTUAL TABLE dishes_fts USING fts5(
        name,
        description,
        dish_type,
        pairing_text,
        tokenize='unicode61 remove_diacritics 1',
        prefix='2,3,4'
      );
    SQL

    # Populate with existing dishes data
    say_with_time "Indexing existing dishes..." do
      Dish.find_each do |dish|
        pairing_text = dish.pairing_suggestions.to_a.map do |s|
          [s["name"], s["description"]].compact.join(" ")
        end.join(" ")

        execute ActiveRecord::Base.sanitize_sql_array([
          "INSERT INTO dishes_fts(rowid, name, description, dish_type, pairing_text) VALUES (?, ?, ?, ?, ?)",
          dish.id, dish.name || "", dish.description || "", dish.dish_type || "", pairing_text || ""
        ])
      end
    end
  end

  def down
    execute "DROP TABLE IF EXISTS dishes_fts"
  end
end
