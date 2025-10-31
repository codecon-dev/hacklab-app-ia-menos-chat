class LocaleController < ApplicationController
  def change
    locale = params[:locale].to_s.strip.to_sym

    if I18n.available_locales.include?(locale)
      session[:locale] = locale
    end

    redirect_to request.referer || root_path, allow_other_host: false
  end
end
