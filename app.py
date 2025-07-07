from flask import Flask
from log import logger, setup_logger
from flask_cors import CORS
# from healthcheck import HealthCheck
from flask_restx import Api
from controller import register_routes


application = Flask(__name__)

def create_app():    
    setup_logger()
    CORS(application, supports_credentials=True)
    # health = HealthCheck()
    # application.add_url_rule("/resollect_application/healthCheck", view_func=health.run_check)
    return application


def configure_api(application):
    api = Api(
        application,
        version="0.1",
        title="Task Generator System",
        description="Task Generator System",
    )
    register_routes(api)


application = create_app()
configure_api(application)

if __name__ == "__main__":
    logger.info("Starting the app in dev env")
    application.run(
        host="0.0.0.0",
        port=5001,
        load_dotenv=True,
    )
