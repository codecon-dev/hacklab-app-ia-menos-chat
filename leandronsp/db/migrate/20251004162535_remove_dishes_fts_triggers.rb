class RemoveDishesFtsTriggers < ActiveRecord::Migration[8.0]
  def up
    execute "DROP TRIGGER IF EXISTS dishes_fts_insert"
    execute "DROP TRIGGER IF EXISTS dishes_fts_update"
    execute "DROP TRIGGER IF EXISTS dishes_fts_delete"
  end

  def down
    # Triggers will not be recreated - we'll use ActiveRecord callbacks instead
  end
end
