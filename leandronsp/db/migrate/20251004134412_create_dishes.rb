class CreateDishes < ActiveRecord::Migration[8.0]
  def change
    create_table :dishes do |t|
      t.string :name
      t.text :description
      t.string :dish_type
      t.boolean :favorite
      t.text :user_notes

      t.timestamps
    end
  end
end
