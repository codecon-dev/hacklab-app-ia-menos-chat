# frozen_string_literal: true

namespace :db do
  namespace :queue do
    desc "Load queue schema for development and test"
    task load_schema: :environment do
      ["development", "test"].each do |env|
        database = "storage/#{env}_queue.sqlite3"
        next unless File.exist?(database)

        ActiveRecord::Base.establish_connection(
          adapter: "sqlite3",
          database: database
        )

        load Rails.root.join("db/queue_schema.rb")
        puts "✅ Queue schema loaded for #{env}"
      end

      # Reconnect to default database
      ActiveRecord::Base.establish_connection(Rails.env.to_sym)
    end
  end

  # Hook into db:reset and db:setup to load queue schema
  Rake::Task["db:reset"].enhance do
    Rake::Task["db:queue:load_schema"].invoke
  end

  Rake::Task["db:setup"].enhance do
    Rake::Task["db:queue:load_schema"].invoke
  end
end
