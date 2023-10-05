class PageController < ApplicationController
    def index
        @videos = Video.all
    end
end
