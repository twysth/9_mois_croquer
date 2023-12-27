import meilisearch
from sqlalchemy import create_engine, MetaData, Table
from flask import Flask, jsonify


client = meilisearch.Client('http://localhost:7700', 'KJxAqdceVtDDr5vzvC5LlAvv6NOVlS3cZ9eA4n_Q2fc')

db_url = "mysql+pymysql://root:BabouDiDou+182406@127.0.0.1:3306/9_croquer"
engine = create_engine(db_url)
metadata = MetaData()

def meilei_add(table, list_col):
    '''table is a string with the name of the table to add, list_col is a list of string representing selected columns to index'''
    table_obj = Table(table, metadata, autoload_with=engine)
    with engine.connect() as connection :
        result_set = connection.execute(table_obj.select()).fetchall()
        #Fetching all the table is convenient in developpement but inefficient, should be fixed later
    documents = []
    for row in result_set:
        document = {column.name: getattr(row, column.name) for column in table_obj.columns if column.name in list_col}
        documents.append(document)
    #workaround for the food table
    if table == 'food':
        client.index(table).update(primary_key='code')
    client.index(table).add_documents(documents) 

    #list of retrieved columns
list_recipes = ['id', 'name', 'budget', 'difficulty', 'food']
list_articles = ['id', 'title', 'content' ]
list_food = [ 'code', 'name']
list_questions = [ 'id', 'question', 'answer', 'url_article']
#adding table to meili
meilei_add('recipes', list_recipes)
meilei_add('articles', list_articles)
meilei_add('food', list_food)
meilei_add('questions', list_questions)



app = Flask(__name__)



search = 'kiwi'


if search :
    @app.route("/search")
    def search_engine() :
        results = client.multi_search(
            [
            {'indexUid': 'food', 'q': search, 'limit' : 10},
            {'indexUid': 'recipes', 'q': search, 'limit' : 10},
            {'indexUid': 'articles', 'q': search, 'limit' : 10},
            {'indexUid': 'questions', 'q': search, 'limit' : 10}
            ])
        response = jsonify(results)
        response.headers.add('Content-Type', 'application/json')
        return response
        