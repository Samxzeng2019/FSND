import os
import sys
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  # after_request add all headers and methods
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
      return response

  # list all categories
  @app.route('/categories')
  def list_categories():
    try:
      categories = Category.query.order_by(Category.id).all()
      if not categories:
        abort(404)

      return jsonify({
        'success': True,
        'categories': [category.format() for category in categories],
        'total_categories': len(categories)
      })
    except:
      abort(404)

  # paginate questions when questions more than 10, 10 questions per page
  def paginate_questions(request, questions):
    questions_per_page = 10
    page = request.args.get('page', 1, type=int)
    start =  (page - 1) * questions_per_page
    end = start + questions_per_page
    questions_list = [question.format() for question in questions]
    current_questions = questions_list[start:end]
    return current_questions

  # list all questions
  @app.route('/questions', methods=['GET'])
  def list_questions():
    try:
      questions = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, questions)

      categories = Category.query.order_by(Category.id).all()
      return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(questions),
        'categories': [category.format() for category in categories],
        'current_category' : categories[0].format()
      })
    except:
      abort(404)

  # delete quetions based on question id
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()
      if question is None:
        abort(400)

      question.delete()
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)

      return jsonify({
        'success': True,
        'deleted': question_id,
        'questions': current_questions,
        'total_questions': len(selection)
      })

    except:
      abort(422)

  # create a new question
  @app.route('/questions', methods=['POST'])
  def add_question():
    try:
      body = request.get_json()
      new_question = body.get('question', None)
      new_answer = body.get('answer', None)
      difficulty = body.get('difficulty', None)
      category = body.get('category', None)
      question = Question(
        question=new_question,
        answer=new_answer,
        difficulty=difficulty,
        category=category
      )
      try:
        question.insert()
      except Exception as e:
        db.session.rollback()
        abort(400)

      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)

      return jsonify({
        'success': True,
        'created': question.id,
        'questions': current_questions,
        'total_questions': len(selection)
      })

    except:
      print(sys.exc_info(), flush=True)
      abort(422)

  # search questions
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    body = request.get_json()
    if not body:
      abort(400)
    search_text = body.get('searchTerm', None)
    if not search_text:
      abort(400)
    
    try:
      selection = Question.query.filter(Question.question.ilike('%{}%'.format(search_text))).all()
      categories = Category.query.order_by(Category.id).all()

      if selection:
        current_questions = paginate_questions(request, selection)
        return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': len(selection),
          'current_category': categories[0].format()
        })
      else:
        return jsonify({
          'success': False,
          'questions': 'No match question found, please search something else'
        })
    except:
      abort(422)

  # list question by category id
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def list_questions_by_category(category_id):
    try:
      # if use filter, need to specify the Class Question
      questions = Question.query.filter(Question.category == category_id).all()
      if not questions:
        abort(404)
      current_questions = paginate_questions(request, questions)
      categories = Category.query.order_by(Category.id).all()
      return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(questions),
        'current_category' : categories[0].format()
      })
    except:
      abort(404)
    
  # play the quiz for select random questions remaining in the category
  @app.route('/quizzes', methods=['POST'])
  def get_next_question():
    body = request.get_json()
    previous_questions = body.get('previous_questions', None)
    quiz_category = body.get('quiz_category', None)
    try:
      questions = Question.query.filter(Question.category == quiz_category['id']).all()

      if not questions:
        abort(400)
      question_ids = [question.id for question in questions]
      remaining_questions = list(set(question_ids) - set(previous_questions))
      if remaining_questions:
        next_question_id = random.choices(remaining_questions)[0]
        for question in questions:
          if question.id == next_question_id:
            next_question = question.format()
        return jsonify({
          'question': next_question
        })
      else:
        return jsonify({
          'question': None
        })
    except:
      print(sys.exc_info(), flush=True)
      abort(422)
      
  @app.route('/testerror', methods=['GET'])
  def get_error():
    abort(400)

  # 404 not found
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "resource not found"
      }), 404

  # 422 Unprocessable Entity
  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
      }), 422
  
  # 400 bad request
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "bad request"
      }), 400
  

  return app
