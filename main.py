from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class VideoModel(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), nullable=False)
	views = db.Column(db.Integer, nullable=False)
	likes = db.Column(db.Integer, nullable=False)

post_video = reqparse.RequestParser()
post_video.add_argument("name", type=str, help="Name of the video is required", required=True)
post_video.add_argument("views", type=int, help="Views of the video", required=True)
post_video.add_argument("likes", type=int, help="Likes on the video", required=True)

update_video = reqparse.RequestParser()
update_video.add_argument("name", type=str, help="Name of the video is required")
update_video.add_argument("views", type=int, help="Views of the video")
update_video.add_argument("likes", type=int, help="Likes on the video")

resource_fields = {
	'id': fields.Integer,
	'name': fields.String,
	'views': fields.Integer,
	'likes': fields.Integer
}

class Video(Resource):
	@marshal_with(resource_fields)
	def get(self, video_id):
		result = VideoModel.query.filter_by(id=video_id).first()
		if not result:
			abort(404, message="Could not find video with that id")
		return result

	@marshal_with(resource_fields)
	def post(self, video_id):
		args = post_video.parse_args()
		result = VideoModel.query.filter_by(id=video_id).first()
		if result:
			abort(409, message="Video id taken...")

		video = VideoModel(id=video_id, name=args['name'], views=args['views'], likes=args['likes'])
		db.session.add(video)
		db.session.commit()
		return video, 201

	@marshal_with(resource_fields)
	def patch(self, video_id):
		args = update_video.parse_args()
		result = VideoModel.query.filter_by(id=video_id).first()
		if not result:
			abort(404, message="Video doesn't exist, cannot update")

		if args['name']:
			result.name = args['name']
		if args['views']:
			result.views = args['views']
		if args['likes']:
			result.likes = args['likes']

		db.session.commit()

		return result

	@marshal_with(resource_fields)
	def delete(self, video_id):
		result = VideoModel.query.filter_by(id=video_id).first()
		if not result:
			abort(404, message="Video doesn't exist, cannot delete")
		db.session.delete(result)
		db.session.commit()
		return '', 204


api.add_resource(Video, "/video/<int:video_id>")

if __name__ == "__main__":
	app.run(debug=True)