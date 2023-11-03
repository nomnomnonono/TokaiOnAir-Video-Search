class PageController < ApplicationController
    def index
        @videos = Video.all.order(year: :desc).order(month: :desc).order(day: :desc)
    end
end
