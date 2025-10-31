# app/models/concerns/searchable.rb
module Searchable
  extend ActiveSupport::Concern

  included do
    # Main full-text search scope
    scope :full_text_search, ->(query) {
      return all if query.blank?

      sanitized_query = sanitize_search_query(query)
      fts = fts_table_name

      joins("INNER JOIN #{fts} ON #{table_name}.id = #{fts}.rowid")
        .where("#{fts} MATCH ?", sanitized_query)
        .select("#{table_name}.*, bm25(#{fts}) AS rank")
        .order("rank ASC")  # Lower BM25 score is better
    }

    # Class method to rebuild the entire search index
    def self.rebuild_search_index
      connection.execute("DELETE FROM #{fts_table_name}")

      find_each do |record|
        record.send(:update_search_index)
      end

      count
    end
  end

  # Updates FTS index for this record
  # Must be implemented in each model
  def update_search_index
    raise NotImplementedError, "#{self.class} must implement #update_search_index"
  end

  class_methods do
    # FTS table name (convention: table_fts)
    def fts_table_name
      "#{table_name}_fts"
    end

    # Sanitizes search query and adds automatic wildcards
    def sanitize_search_query(query)
      cleaned = query.to_s
                     .strip
                     .gsub(/[^\w\s\*"&|!()-]/, ' ')  # Remove dangerous chars
                     .squeeze(' ')                     # Remove double spaces

      return '*' if cleaned.blank?

      # If no special operators, add * to each word
      # for automatic prefix search (e.g., "fish" becomes "fish*")
      if !cleaned.match?(/["&|!*()]/)
        cleaned.split.map { |word| "#{word}*" }.join(' ')
      else
        # With operators, add * only to words, not to operators
        cleaned.split.map do |word|
          if word.match?(/^(AND|OR|NOT)$/i)
            word  # Keep operators without wildcard
          elsif word.end_with?('*')
            word  # Already has wildcard
          elsif !word.match?(/["|!()]/)
            "#{word}*"  # Add wildcard
          else
            word  # Keep special characters
          end
        end.join(' ')
      end
    end
  end
end
