import os
import json
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''

  @app.after_request   
  def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''

  @app.route('/categories')
  def get_all_categories():
        categories = Category.query.all()
        if categories is None:
            abort(404)
       
        else:
            formated_categories = [category.format() for category in categories]
            result = {
              'success': True,
              'categories': formated_categories,
            }
            return jsonify(result)
           


  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start =  (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

  @app.route('/questions')
  def get_paginated_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        formated_categories = [category.format() for category in  Category.query.all()]

        if len(current_questions) == 0:
            abort(404)

        result = {
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection),
            'current_category': None,
            'categories': formated_categories,
         }    

        return jsonify(result)

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            question.delete()
            result = {
                'success': True,
             }
            return jsonify(result)

        except:
            abort(422)
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  @app.route('/questions', methods=['POST'])
  def add_new_question():
      if not request.data:
        abort(422)
        
      new_question_data = json.loads(request.data)        
      new_question = new_question_data['question']
      new_answer = new_question_data['answer']
      new_difficulty = new_question_data['difficulty']
      new_category = new_question_data['category']
      if not new_question or not new_answer or not new_difficulty or not new_category:
        abort(404)

      try:
        added_question = Question(question=new_question, answer=new_answer, difficulty=new_difficulty, category=new_category)
        added_question.insert()

        result = {
            'success': True,
        }
        return jsonify(result)

      except:
            abort(405)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  @app.route('/searchQuestions', methods=['POST'])
  def search_questions():
        if not request.data:
            abort(422)
        new_search_data = json.loads(request.data)
        new_search = new_search_data['searchTerm']
        if not new_search:
            abort(404)
        try:
            selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(new_search)))
            current_questions = paginate_questions(request, selection)
            result = {
                'success': True,
                'questions': current_questions,
                'total_questions': len(selection.all()),
            }
            return jsonify(result)
        except:
            abort(405)



  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

  @app.route('/categories/<int:category_id>/questions')
  def get_questions_by_category(category_id):
        questions_by_category = Question.query.filter(Question.category == category_id).all()
        current_questions = paginate_questions(request, questions_by_category)

        if len(current_questions) == 0:
            abort(404)

        result = {
            'success': True,
            'questions': current_questions,
            'total_questions': len(questions_by_category),
            'current_category': category_id,
         }    
        return jsonify(result)
           



  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
        if not request.data:
            abort(422)

        quiz_data = json.loads(request.data)
        selected_category = quiz_data['quiz_category']
        previous_questions_array = quiz_data['previous_questions']

        if not selected_category:
            abort(404)        
        
        try:
            if selected_category['id'] not in [1, 2, 3, 4, 5, 6]:
                all_available_questions = Question.query.filter(Question.id.notin_(previous_questions_array)).all()   # for ALL category
            else:
                all_available_questions = Question.query.filter_by(category = selected_category['id']).filter(Question.id.notin_(previous_questions_array)).all()
               
            if len(all_available_questions) > 0:
                random_question = all_available_questions[random.randrange(0, len(all_available_questions))]
                result = {
                    'success': True,
                    'question': Question.format(random_question)
                }
            else:
                result = {
                    'success': True,
                    'question': None
                }    
            return jsonify(result)

        except:
            abort(405)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(400)
  def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad request'
        }), 400

  @app.errorhandler(404)
  def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource not found'
        }), 404        

  @app.errorhandler(405)
  def not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'Method not allowed'
        }), 405

  @app.errorhandler(422)
  def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable entity'
        }), 422 

  @app.errorhandler(500)
  def internal_server(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal Server Error'
        }), 500         

  
  return app

    