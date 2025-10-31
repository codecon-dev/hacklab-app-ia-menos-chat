class AddPairingSuggestionsToDishes < ActiveRecord::Migration[8.0]
  def change
    add_column :dishes, :pairing_suggestions, :json, default: []
  end
end
