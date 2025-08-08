
import os
from flask import Flask
from .api.scraping_routes import input_processsing_bp, scraping_or_fetching_bp
from api.RAG_and_MultiAgent import RAG_pipe_bp, multiAgent_bp
from api.evaluation_bp import eval_bp
from api.graph_visualization import graph_visualization_bp
# application facrtory
def create_app(test_config=None):
  # creating flask instance
  app = Flask(__name__, instance_relative_config=True)
  # load the config from the config.py file
  app.config.from_object('kaggle_competition_assist_backend.config.Config')
  # if test_config is provided, override the default config
  if test_config is not None:
    app.config.update(test_config)
  else:
    # load the instance config, if it exists, when not testing
    app.config.from_pyfile('config.py', silent=True)
  
  try:
    os.makedirs(app.instance_path)
  except OSError:
    pass
  # register the blueprints for the API routes
  app.register_blueprint(input_processsing_bp)
  app.register_blueprint(scraping_or_fetching_bp)
  app.register_blueprint(RAG_pipe_bp)
  app.register_blueprint(multiAgent_bp)
  app.register_blueprint(eval_bp)
  app.register_blueprint(graph_visualization_bp)
  
  


