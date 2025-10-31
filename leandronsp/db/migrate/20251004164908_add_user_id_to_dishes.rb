class AddUserIdToDishes < ActiveRecord::Migration[8.0]
  def change
    add_reference :dishes, :user, null: true, foreign_key: true
  end
end
