import os
from flask import Flask, request, abort, jsonify, json
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def add_pagination(request, selection):
    cur_page = request.args.get('page', 1, type=int)
    start = (cur_page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    cur_questions = questions[start:end]
    return cur_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
    Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    '''
    cors = CORS(app)

    @app.after_request
    def after_request(areq):
        areq.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        areq.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return areq

    @app.route("/categories")
    def categories():
        selection = Category.query.order_by(Category.type).all()

        if len(categories) == 0:
            abort(404)
        return jsonify({
             'success': True,
             'categories': {category.id: category.type for category in selection}
        })

    @app.route('/questions')
    def questions():
        selection = Question.query.order_by(Question.id).all()
        cur_questions = add_pagination(request, selection)
        categories = Category.query.order_by(Category.type).all()

        if len(cur_questions) == 0:
           abort(404)

        return jsonify({
            'success': True,
            'categories':  {category.id: category.type for category in categories},
            'questions': cur_questions,
            'total_questions': Question.query.count(),
            'current_category': None,
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_questions(question_id):
       
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()
            if question is None:
                abort(404)
            question.delete()
            selection = Question.query.order_by(Question.id).all()
            cur_questions = add_pagination(request, selection)

            return jsonify({
                    'success': True,
                    'deleted': question_id,
                    'questions': cur_questions,
                    'total_questions':len(Question.query.all())
                })

        except:
            abort(422)

    @app.route("/questions", methods=['POST'])
    def post_questions():
        body = request.get_json()
       
        question = body.get('question', None)
        answer = body.get('answer', None)
        category = body.get('category', None)
        difficulty = body.get('difficulty', None)

        try:   
            
                all_questions = Question.query.all()

                selection = Question.query.order_by(Question.id).all()

                current_questions = add_pagination(request, selection)
                question = Question(question=question, answer=answer, category=category, difficulty=difficulty)
                question.insert()

                return jsonify({
                                    'success': True,
                                    'created': question.id,
                                    'question': current_questions,
                                    'total_quetions': len(all_questions)
                                 })
              
        except:
                abort(422)

    @app.route("/questions/search", methods=['POST'])
    def searchQuestions():
        body = request.get_json()

        search = body.get('searchNew',None)

        if search:
            results =  Question.query.filter(
                        Question.question.ilike(f'%{search}%')).all()

            return jsonify({
                'success': True,
                'questions': [question.format() for question in results],
                'total_questions': len(results),
                'current_category': None})
        else:
            abort(404)

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_question_by_category(category_id):
                try:
                    questions = Question.query.filter(Question.category == str(category_id)).all()
                    return jsonify({
                                'success': True,
                                'questions': [question.format() for question in questions],
                                'total_questions': len(questions),
                                'current_category': category_id
                                })
                except:
                    abort(404)

    @app.route("/quizzes", methods=['POST'])
    def quizzes():

        try:
            body = request.get_json()
            if not ('quiz_category' in body and 'previous_questions' in body):
                    abort(422)

            category = body.get('quiz_category')
            previous_questions = body.get('previous_questions')

            if category['type'] == 'click':
                present_question = Question.query.filter(Question.id.notin_(previous_questions)).all()

            else:
                    new_questions = Question.query.filter_by(category=category['id']).filter(Question.id.notin_(previous_questions)).all()

            new_question = new_questions[random.randrange(0,
                                                          len(new_questions))].format() if len(new_questions) > 0 else None

            return jsonify({
                    'success': True,
                    'question': present_question
                        })
        except:
                abort(422)


    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            'error': 400,
            "message": "Bad request sent"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            'error': 404,
            "message": "Data could not be found"
        }), 404

    @app.errorhandler(422)
    def not_processed(error):
        return jsonify({
            "success": False,
            'error': 422,
            "message": "Could not be processed"
        }), 422

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            'error': 500,
            "message": "Internal server error"
        }), 500

    return app
