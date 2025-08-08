from flask import Blueprint, jsonify, request
from evaluation.guideline_evaluator import Evaluator

eval_bp = Blueprint("evaluation", __name__, url_prefix="/evaluate")
@eval_bp.route("/", methods=["POST"])
def evaluate():
    data = request.get_json()
    response = data.get("response", "")
    task = data.get("task", "")
    guideline_json_path = data.get("guideline_json_path", "data/evaluation/kaggle_expert_tips.json")

    evaluator = Evaluator(guideline_json_path)
    evaluation_result = evaluator.evaluate_response(response, task)

    return jsonify(evaluation_result), 200