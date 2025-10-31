class Dish < ApplicationRecord
  include Searchable

  belongs_to :user, optional: true
  has_one_attached :image

  validate :image_presence
  validate :image_format
  validate :image_size

  after_save :update_search_index
  after_destroy :remove_from_search_index

  private

  def remove_from_search_index
    self.class.connection.execute(
      "DELETE FROM dishes_fts WHERE rowid = #{id}"
    )
  end

  # Updates the FTS index for this dish
  def update_search_index
    pairing_text = extract_pairing_text

    sql = <<~SQL.squish
      INSERT OR REPLACE INTO dishes_fts(rowid, name, description, dish_type, pairing_text)
      VALUES (?, ?, ?, ?, ?)
    SQL

    self.class.connection.execute(
      self.class.sanitize_sql_array([
        sql,
        id,
        name || '',
        description || '',
        dish_type || '',
        pairing_text || ''
      ])
    )
  end

  # Extracts text from pairing_suggestions JSON for indexing
  def extract_pairing_text
    return '' if pairing_suggestions.blank?

    pairing_suggestions.map do |suggestion|
      [
        suggestion['name'],
        suggestion['description']
      ].compact.join(' ')
    end.join(' ')
  end

  def image_presence
    errors.add(:image, "must be present") unless image.attached?
  end

  def image_format
    return unless image.attached?

    acceptable_types = %w[image/png image/jpg image/jpeg image/webp]
    unless acceptable_types.include?(image.content_type)
      errors.add(:image, "must be PNG, JPG or WEBP")
    end
  end

  def image_size
    return unless image.attached?

    if image.byte_size > 5.megabytes
      errors.add(:image, "must be less than 5MB")
    end
  end
end
