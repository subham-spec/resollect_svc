from log import logger
from flask import make_response, jsonify
from config_mapping.mapping import SuccessResponse, ErrorResponse
from flask_restx import Namespace, Resource
from services.tag_service import TagService


api = Namespace("resollect/tags")

@api.route("/")
class TagListResource(Resource):
    def get(self):
        """
            List all available tags
        """
        try:
            tag_service = TagService()
            tags = tag_service.get_all_tags()
            
            return make_response(jsonify({"tags": tags}), 200)
            
        except Exception as e:
            logger.error(f"Error while retrieving tags: {e}")
            error_response = ErrorResponse(
                errorCode=500,
                errorResponse=f"Failed to retrieve tags: {str(e)}"
            )
            return make_response(jsonify(error_response.to_dict()), 500) 