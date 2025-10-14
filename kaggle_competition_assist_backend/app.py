
import os
from flask import Flask
from flask_cors import CORS
try:
    from .api.health import health_bp
    from .utils.logging_config import setup_logging
except ImportError:
    # Fallback for when running from project root
    from api.health import health_bp
    from utils.logging_config import setup_logging

# Import other blueprints conditionally to avoid import errors
# Temporarily disabled due to import issues
SCRAPING_AVAILABLE = False
print("Warning: Scraping routes temporarily disabled due to import issues")

# Temporarily disabled due to import issues
RAG_AVAILABLE = False
print("Warning: RAG routes temporarily disabled due to import issues")

# Temporarily disabled due to import issues
EVALUATION_AVAILABLE = False
print("Warning: Evaluation routes temporarily disabled due to import issues")

# Temporarily disabled due to import issues
GRAPH_VIZ_AVAILABLE = False
print("Warning: Graph visualization temporarily disabled due to import issues")

try:
    from .api.component_orchestration import component_bp
    COMPONENT_AVAILABLE = True
except ImportError:
    try:
        from api.component_orchestration import component_bp
        COMPONENT_AVAILABLE = True
    except ImportError as e:
        print(f"Warning: Component orchestration not available: {e}")
        COMPONENT_AVAILABLE = False

try:
    from .api.session_management import session_bp
    SESSION_AVAILABLE = True
except ImportError:
    try:
        from api.session_management import session_bp
        SESSION_AVAILABLE = True
    except ImportError as e:
        print(f"Warning: Session management not available: {e}")
        SESSION_AVAILABLE = False
# application facrtory
def create_app(test_config=None):
  # creating flask instance
  app = Flask(__name__, instance_relative_config=True)
  
  # Enable CORS for all routes
  CORS(app)
  
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
  
  # Set up logging
  setup_logging(app)
  
  # register the blueprints for the API routes
  app.register_blueprint(health_bp)  # Health check first
  
  # Register available blueprints
  if SCRAPING_AVAILABLE:
    app.register_blueprint(input_processsing_bp)
    app.register_blueprint(scraping_or_fetching_bp)
    app.logger.info("Scraping blueprints registered")
  
  if RAG_AVAILABLE:
    app.register_blueprint(RAG_pipe_bp)
    app.register_blueprint(multiAgent_bp)
    app.logger.info("RAG blueprints registered")
  
  if EVALUATION_AVAILABLE:
    app.register_blueprint(eval_bp)
    app.logger.info("Evaluation blueprint registered")
  
  if GRAPH_VIZ_AVAILABLE:
    app.register_blueprint(graph_visualization_bp)
    app.logger.info("Graph visualization blueprint registered")
  
  if COMPONENT_AVAILABLE:
    app.register_blueprint(component_bp)
    app.logger.info("Component orchestration blueprint registered")
  
  if SESSION_AVAILABLE:
    app.register_blueprint(session_bp)
    app.logger.info("Session management blueprint registered")
  
  # Log successful startup
  app.logger.info("Available blueprints registered successfully")
  
  return app
