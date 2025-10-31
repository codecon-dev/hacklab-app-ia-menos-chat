class DishesController < ApplicationController
  before_action :authenticate_user!
  before_action :set_dish, only: %i[ show edit update destroy toggle_favorite ]

  # GET /dishes or /dishes.json
  def index
    @dishes = current_user.dishes

    # Full-text search if query is present
    if params[:search].present?
      @dishes = @dishes.full_text_search(params[:search])
    end

    # Favorites filter (maintains existing functionality)
    @dishes = @dishes.where(favorite: true) if params[:favorites].present?

    # Ordering: if search is present, use ranking; otherwise, use date
    @dishes = if params[:search].present?
                @dishes # Already sorted by relevance (search_rank)
              else
                @dishes.order(created_at: :desc)
              end
  end

  # GET /dishes/1 or /dishes/1.json
  def show
  end

  # GET /dishes/new
  def new
    @dish = current_user.dishes.build
  end

  # GET /dishes/1/edit
  def edit
  end

  # POST /dishes or /dishes.json
  def create
    @dish = current_user.dishes.build(dish_params)

    # Set placeholders for AI-generated fields
    @dish.name ||= I18n.t("ai.placeholder")
    @dish.description = I18n.t("ai.placeholder")

    respond_to do |format|
      if @dish.save
        # Enqueue background job for AI analysis
        AnalyzeDishJob.perform_later(@dish.id)

        format.html { redirect_to @dish, notice: I18n.t("flash.dishes.created_analyzing") }
        format.json { render :show, status: :created, location: @dish }
      else
        format.html { render :new, status: :unprocessable_entity }
        format.json { render json: @dish.errors, status: :unprocessable_entity }
      end
    end
  end

  # PATCH/PUT /dishes/1 or /dishes/1.json
  def update
    respond_to do |format|
      if @dish.update(dish_params)
        format.html { redirect_to @dish, notice: "Dish was successfully updated.", status: :see_other }
        format.json { render :show, status: :ok, location: @dish }
      else
        format.html { render :edit, status: :unprocessable_entity }
        format.json { render json: @dish.errors, status: :unprocessable_entity }
      end
    end
  end

  # DELETE /dishes/1 or /dishes/1.json
  def destroy
    @dish.destroy!

    respond_to do |format|
      format.html { redirect_to dishes_path, notice: I18n.t("flash.dishes.destroyed"), status: :see_other }
      format.json { head :no_content }
    end
  end

  # POST /dishes/1/toggle_favorite
  def toggle_favorite
    @dish.update(favorite: !@dish.favorite)
    notice_key = @dish.favorite ? "flash.dishes.favorite_added" : "flash.dishes.favorite_removed"
    redirect_to @dish, notice: I18n.t(notice_key)
  end

  private
    # Use callbacks to share common setup or constraints between actions.
    def set_dish
      @dish = current_user.dishes.find(params.expect(:id))
    end

    # Only allow a list of trusted parameters through.
    def dish_params
      params.expect(dish: [ :name, :description, :dish_type, :favorite, :user_notes, :image ])
    end
end
