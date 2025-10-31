json.extract! dish, :id, :name, :description, :dish_type, :favorite, :user_notes, :created_at, :updated_at
json.url dish_url(dish, format: :json)
