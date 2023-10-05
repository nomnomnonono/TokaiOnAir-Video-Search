class CreateVideos < ActiveRecord::Migration[7.0]
  def change
    create_table :videos, id: false do |t|
      t.string :id, limit: 50, null: false, primary_key: true
      t.text :title
      t.text :description
      t.text :thumbnail
      t.integer :year
      t.integer :month
      t.integer :day
      t.integer :viewcount
      t.integer :likecount

      t.timestamps
    end
  end
end
