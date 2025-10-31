# frozen_string_literal: true

# Background job to update user eating profiles using AI analysis
# Runs periodically via Solid Queue recurring tasks
class UpdateUserProfilesJob < ApplicationJob
  include Retriable

  queue_as :default

  # Process all users with dishes and update their eating profiles
  def perform
    User.joins(:dishes).distinct.find_each do |user|
      with_retry do
        analyzer = Claude::ProfileAnalyzer.new(user)
        profile = analyzer.analyze

        user.update!(eating_profile: profile)
        Rails.logger.info("Updated eating profile for user #{user.id}: #{profile}")
      end
    rescue StandardError => e
      Rails.logger.error("Failed to update profile for user #{user.id}: #{e.message}")
      # Continue processing other users
    end

    Rails.logger.info("Completed user profile updates")
  end
end
