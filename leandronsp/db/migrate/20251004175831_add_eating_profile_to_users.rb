class AddEatingProfileToUsers < ActiveRecord::Migration[8.0]
  def change
    add_column :users, :eating_profile, :text
  end
end
