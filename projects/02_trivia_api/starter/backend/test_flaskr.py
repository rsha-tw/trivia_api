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
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass


    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))
    
    def test_404_invalid_categories(self):
        res = self.client().get('/categories/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
    
    def test_404_invaild_question(self):
        res = self.client().get('/questions/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "method not allowed")
    

    def test_200_delete_question(self):
        res = self.client().delete(f'/questions/10')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted'],10)

    def test_404_delete_question(self):
        res = self.client().delete('/questions/100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['message'], "unprocessable")
        self.assertFalse(data['success'])
    
       
    def test_create_new_questions(self):
        res = self.client().post('/questions',json={"question":"The Taj Mahal is located in which Indian city?","answer":"Agra","category":3,"difficulty":2})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
       

    def test_405_if_creation_not_allowed(self):
        res = self.client().post('/questions/create', json={"question":"The Taj Mahal is located in which Indian city?","answer":"Agra","category":3,"difficulty":2})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_post_questions_search_with_results(self):
        res = self.client().post('/questions/search', json={'search': 'The Taj'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))

    def test_post_questions_search_without_results(self):
        res = self.client().post('/questions/search', json={'search': 'anything'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'], "resource not found")
    
    def test_get_categories_by_id(self):
        res = self.client().get('/categories/4/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['questions'])
    
    def test_404_sent_requesting_if_invalid(self):
        res = self.client().get('/categories/100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
    
    def test_create_new_quizzes(self):
        res = self.client().post('/quizzes', json={"previous_questions": [1, 2],"quiz_category": {"type": "click", "id": 0}})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_400_if_quizzis_not_allowed(self):
        res = self.client().post('/quizzes')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()