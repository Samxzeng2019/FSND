import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('postgres:password@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question = {
            "question": "What is the product of 3 and 4",
            "answer": "The product of 3 and 4 is 12",
            "difficulty": 1,
            "category": "1"
        }

        self.search_term_true = {
            "searchTerm": "What movie earned Tom Hanks his third straight Oscar nomination"
        }

        self.search_term_false = {
            "searchTerm": "abcdefghijklmnopqrstuvwxyz"
        }

        self.quiz = {
            "previous_questions": [2],
            "quiz_category": {"type": "Y", "id": "5"}
        }

        self.quiz_solely = {
            "previous_questions": [24],
            "quiz_category": {"type": "N", "id": "7"}
        }


    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIs(type(data['categories']), list)
        self.assertIs(type(data['total_categories']), int)
    
    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIs(type(data['questions']), list)
        self.assertIs(type(data['total_questions']), int)
        self.assertIs(type(data['categories']), list)
        self.assertIs(type(data['current_category']), dict)
    
    def test_delete_question_by_id(self):
        res = self.client().delete('/questions/5')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 5)
        self.assertIs(type(data['questions']), list)
        self.assertIs(type(data['total_questions']), int)

    def test_post_new_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIs(type(data['created']), int)
        self.assertIs(type(data['questions']), list)
        self.assertIs(type(data['total_questions']), int)
    
    def test_post_search_question_true(self):
        res = self.client().post('/questions/search', json=self.search_term_true)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['questions'][0]['question'], 'What movie earned Tom Hanks his third straight Oscar nomination, in 1996?')
        self.assertIs(type(data['total_questions']), int)
        self.assertIs(type(data['current_category']), dict)

    def test_get_question_by_category_id(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['current_category']['id'], 1)
        self.assertIs(type(data['questions']), list)
        self.assertIs(type(data['total_questions']), int)

    def test_post_quizzes(self):
        res = self.client().post('/quizzes', json=self.quiz)
        data = json.loads(res.data)
        self.assertTrue(data['question'])

    def test_post_quizzes_none(self):
        res = self.client().post('/quizzes', json=self.quiz_solely)
        data = json.loads(res.data)
        self.assertFalse(data['question'])

    def test_400_search_without_content(self):
        res = self.client().post('/questions/search')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')

    def test_404_non_exist_category(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_422_create_question_fail(self):
        res = self.client().post('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()