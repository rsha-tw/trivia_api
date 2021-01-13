import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * 10
    end = start + 10

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type,Authorization,true')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    @app.route('/categories')
    def get_all_categories():
        categories = Category.query.all()
        formatted_categories = {
            category.id: category.type for category in categories}

        return jsonify({
            'success': True,
            'categories': formatted_categories
        })

    @app.route('/questions')
    def get_all_questions():
        selection = Question.query.order_by(Question.id).all()
        currernt_questions = paginate_questions(request, selection)

        categories = Category.query.all()
        formatted_categories = {
            category.id: category.type for category in categories}

        return jsonify({
            'success': True,
            'questions': currernt_questions,
            'total_questions': len(Question.query.all()),
            'categories': formatted_categories,
            'current_category': None

        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_questions(question_id):
        body = request.get_json()

        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()
            if question is None:
                abort(404)
            question.delete()
            selection = Question.query.order_by(Question.id).all()
            currernt_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'deleted': question.id,
                'questions': currernt_questions,
                'total_questions': len(Question.query.all())
            })
        except BaseException:
            abort(422)

    @app.route('/questions', methods=['POST'])
    def create_questions():
        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)

        try:
            question = Question(
                question=new_question,
                answer=new_answer,
                category=new_category,
                difficulty=new_difficulty)
            question.insert()

            selection = Question.query.order_by(Question.id).all()
            currernt_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'created': question.id
            })

        except BaseException:
            abort(422)

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()

        if body is None:
            abort(422)

        search = body.get('search')
        search_query = Question.query.order_by('id').filter(
            Question.question.ilike(f'%{search}%')).all()

        formatted_search = [question.format() for question in search_query]

        if len(formatted_search) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': formatted_search
        })

    @app.route('/categories/<category_id>/questions')
    def get_questions_in_category(category_id):

        body = request.get_json()

        selection = Question.query.order_by(
            Question.id).filter(
            Question.category == category_id).all()
        currernt_questions = paginate_questions(request, selection)

        return jsonify({
            'success': True,
            'questions': currernt_questions,
            'total_questions': len(selection)
        })

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        body = request.get_json()
        if body is None:
            abort(422)
        previous_question = body.get('previous_questions')
        quiz_category = body.get('quiz_category')

        if quiz_category['id'] == 0:
            questions = Question.query.all()

        else:
            questions = Question.query.filter(
                Question.category == quiz_category['id']).all()

        question = random.choice(questions).format()

        if question['id'] in previous_question:
            question = random.choice(questions).format()

        if len(previous_question) == len(questions):
            question = None

        return jsonify({
            'success': True,
            'question': question
        })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_requast(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(405)
    def not_fond(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405    

    return app
