from flask import Flask
from flask import render_template
from flask import Response, request, jsonify, redirect, url_for
from datetime import datetime
import time
import os
import openai
import requests
import json
import random
import sqlalchemy as db
import pandas as pd
from openai import OpenAI

api_key = '8YQ53Ao5sqOGEq826OfsK3PqOEQBWY36Iv0KJsTx'
base_url = 'https://api.watchmode.com/v1/title/'
gpt_api = ""

def fetch_data(api_key, search_query):
    url = f"{base_url}{search_query}/details/?apiKey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data: {response.status_code}")
        return None
    
def chatGPT_summary(my_api_key, message):
    # Create an OpenAPI client using the key from our environment variable
    client = OpenAI(
        api_key=my_api_key,
    )

    # Specify the model to use and the messages to send
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a movie critic giving an unbiased overview of a specific movie to get someone else to watch it"},
            {"role": "user", "content": message}
        ]
    )
    return completion.choices[0].message.content

def generate(user_input):
    df = pd.read_csv('title_id_map.csv', dtype={'Year': 'string'})
    title = user_input
    results = df[df['Title'] == title]
    id = int(results['Watchmode ID'].iloc[0])

    # Fetch data from Watchmode API
    data = fetch_data(api_key, id)
    print(data)
    similar_movies = []
    for title_id in data['similar_titles']:
        title_result = df[df['Watchmode ID'] == title_id]
        movie = title_result['Title'].iloc[0]
        similar_movies.append(movie)


    if len(similar_movies) > 2:
        random_indices = random.sample(range(0, len(similar_movies) - 1), 3)
        list_here = []
        for index in random_indices:
            #print(f"Summary for {similar_movies[index]}: ")
            #print(chatGPT_summary(gpt_api, f"Explain this movie: {similar_movies[index]}"))
            #print()
            list_here.append(similar_movies[index])
        return list_here
    elif not similar_movies:
        lesser_list = []
        for movie in similar_movies:
            #print(f"Summary for {movie}: ")
            #print(chatGPT_summary(gpt_api, f"Explain this movie: {movie}"))
            #print()
            lesser_list.append(movie)
        return lesser_list
    else:
        return []

def summaries(similar_movies):
    if len(similar_movies) > 2:
        random_indices = random.sample(range(0, len(similar_movies) - 1), 3)
        list_here = []
        for index in random_indices:
            #print(f"Summary for {similar_movies[index]}: ")
            #print(chatGPT_summary(gpt_api, f"Explain this movie: {similar_movies[index]}"))
            #print()
            list_here.append(chatGPT_summary(gpt_api, f"Explain this movie: {similar_movies[index]}"))
        return list_here
    elif not similar_movies:
        lesser_list = []
        for movie in similar_movies:
            #print(f"Summary for {movie}: ")
            #print(chatGPT_summary(gpt_api, f"Explain this movie: {movie}"))
            #print()
            lesser_list.append(chatGPT_summary(gpt_api, f"Explain this movie: {movie}"))
        return lesser_list
    else:
        return []
def convert_to_embedded_link(link):
    video_id = link.split('v=')[1]
    embedded_link = f'https://www.youtube.com/embed/{video_id}'
    return embedded_link
app = Flask(__name__)

start_time = datetime.now()
current_time = start_time

def get_elapsed_time():
    current_time_function = datetime.now()
    elapsed_time = current_time_function - start_time
    return elapsed_time.total_seconds() / 60

current_id = 11 # starts at 11

data = [
    {
        "id": 1,
        "title": "The Batman",
        "poster": "https://nairobiwire.com/wp-content/uploads/2021/10/how-many-clubs-are-there-in-a-deck-of-cards.jpg",
        "backdrop": "https://nairobiwire.com/wp-content/uploads/2021/10/how-many-clubs-are-there-in-a-deck-of-cards.jpg",
        "summary": "Once rivals in school, two brilliant doctors reunite by chance - each facing life's worst slump and unexpectedly finding solace in each other.",
        "trailer": "https://nairobiwire.com/wp-content/uploads/2021/10/how-many-clubs-are-there-in-a-deck-of-cards.jpg",
        "runtime_minutes": ["2 minutes"],
        "genre_names": ["2 minutes"],
        "us_rating": "Card Types",
        "user_rating": "Card Types",
        "critic_score": "Card Types",
    },

    {
        "id": 2,
        "title": "Thor: Ragnorak",
        "poster": "https://nairobiwire.com/wp-content/uploads/2021/10/how-many-clubs-are-there-in-a-deck-of-cards.jpg",
        "backdrop": "https://nairobiwire.com/wp-content/uploads/2021/10/how-many-clubs-are-there-in-a-deck-of-cards.jpg",
        "summary": "A lawyer bound by a centuries-old curse becomes entangled with a civil servant who holds the key to his freedom.",
        "trailer": "https://nairobiwire.com/wp-content/uploads/2021/10/how-many-clubs-are-there-in-a-deck-of-cards.jpg",
        "runtime_minutes": ["2 minutes"],
        "genre_names": ["1 minute"],
        "us_rating": "Card Types",
        "user_rating": "Card Types",
        "critic_score": "Card Types",
    },

    {
        "id": 3,
        "title": "Dawn of the Planet of the Apes",
        "poster": "https://nairobiwire.com/wp-content/uploads/2021/10/how-many-clubs-are-there-in-a-deck-of-cards.jpg",
        "backdrop": "https://nairobiwire.com/wp-content/uploads/2021/10/how-many-clubs-are-there-in-a-deck-of-cards.jpg",
        "summary": "The residents of a high-rise apartment fight for their lives against a deadly infectious disease while Sae-bom and Yi-hyun try to find the person because of whom the virus spread.",
        "trailer": "https://nairobiwire.com/wp-content/uploads/2021/10/how-many-clubs-are-there-in-a-deck-of-cards.jpg",
        "runtime_minutes": ["1 minute"],
        "genre_names": ["2 minutes"],
        "us_rating": "Card Types",
        "user_rating": "Card Types",
        "critic_score": "Card Types",
    },
]

# keep track of the user's score (out of five)
score = 0
attempted = dict() # keep track of the problems the user has attempted
# and whether they got it right
# if they got it right and they retry, then deduct 1 from score
# if they got it wrong and retry, do nothing

# key value pair:
# 1: True # for problem 1, either True for success or False for incorrect

@app.route('/')
def start():
    # current_time = datetime.now()
    items = data[:3] # take first 3

    return render_template('input.html', items=items, current_time=current_time) # home page

# @app.route('/home', defaults={'reset': None})
# @app.route('/home/<reset>') # reset in case they go back home after finishing the test
# def welcome(reset):
#     global score
#     global attempted

#     if reset:
#         score = 0
#         attempted = dict()

#     items = data[:3] # take first 3

#     current_time = datetime.now()
#     elapsed_time = get_elapsed_time();

#     return render_template('welcome.html', items=items, current_time=current_time, elapsed_time=elapsed_time) # home page

# @app.route('/search', methods=['POST', 'GET'])
# def search():

#     search_query = request.form['searchQuery']
#     # search_query = request.args.get('query', '')  # Default to an empty string if 'query' parameter is not provided
#     # look for the titles with matching

#     items = []

#     for drama in data: # each drama entry
#         # need to return where exactly it matched

#         # check the title, actors, genre

#         # then, in the return statement, have a field called "title", "actors", or "genre"
#         # to figure out where it matched
#         # and then return the matching text?

#         # may use JS instead
#         # how to account for multiple matches?

#         matchFound = False

#         if search_query.lower() in drama['title'].lower(): # if it's in the title
#             matchFound = True
        
#         for actor in drama['actors']:
#             if search_query.lower() in actor.lower(): # matches the actor name
#                 matchFound = True
#                 break

#         for genre in drama['genres']:
#             if search_query.lower() in genre.lower(): # matches the genre
#                 matchFound = True
#                 break

#         # for each item, edit the corresponding items to be in syntax
#         if matchFound:
#             items.append(drama)

#     # print("hello beautiful")
#     # print(items)

#     return render_template('search_results.html', items=items, query=search_query)

# '''
# View a particular kdrama
# '''
@app.route('/movie/<string:title>', methods=['GET']) # GET request because just requesting info from server
def learn(title):
    item = None
    df = pd.read_csv('title_id_map.csv', dtype={'Year': 'string'})
    current_time = datetime.now()
    elapsed_time = get_elapsed_time();
    
    suggested_titles = generate(title)
    titles_data = []
    for movie in suggested_titles:
        title_result = df[df['Title'] == movie]
        id = int(title_result['Watchmode ID'].iloc[0])
        titles_data.append(id)

    complete_data = []
    for inner_id in titles_data:
        complete_data.append(fetch_data(api_key, inner_id))
    print(complete_data)
    # print(item)
    # print(item)

    return render_template('movie.html', item=item, current_time=current_time, elapsed_time=elapsed_time, title=title, items=complete_data)

@app.route('/overview/<string:title>', methods=['GET']) # GET request because just requesting info from server
def learn2(title):
    item = None
    df = pd.read_csv('title_id_map.csv', dtype={'Year': 'string'})
    current_time = datetime.now()
    elapsed_time = get_elapsed_time();
    better_summary = chatGPT_summary(gpt_api, f"Explain this movie: {title}")

    title_result = df[df['Title'] == title]
    id = int(title_result['Watchmode ID'].iloc[0])
    data = fetch_data(api_key, id)
    print(data)
    standard_link = data['trailer']
    embedded_link = convert_to_embedded_link(standard_link)
    
    # print(item)
    # print(item)

    return render_template('main.html', item=item, current_time=current_time, elapsed_time=elapsed_time, title=title, movie=data, trailer=embedded_link, sum=better_summary)


@app.route('/readme', methods=['GET']) # GET request because just requesting info from server
def learn3():
    current_time = datetime.now()
    elapsed_time = get_elapsed_time();
    return render_template('readme.html', current_time=current_time, elapsed_time=elapsed_time)

# '''
# Access Types
# '''

# @app.route('/type/<int:id>', methods=['GET']) # GET request because just requesting info from server
# def type(id):
#     item = None
#     number = 0
#     current_time = datetime.now()
#     elapsed_time = get_elapsed_time();
#     print(data)

#     for drama in data:
#         if drama['id'] == int(id): # str by default
#             item = drama
#             break
    
#     # matching item by actor
#     itemActor = None
#     itemGenre = None

#     if item: # item exists
#         actors = item['actors']
#         genres = item['genres']

#         for actor in actors: # for each actor in this particular kdrama
#             for drama in data: # check if existing match in data
#                 if drama['id'] != int(id):
#                     for actor2 in drama['actors']: # (BUT CANNOT BE THE SAME ITEM)
#                         if actor.lower() == actor2.lower():
#                             itemActor = drama
#                             break

#         for genre in genres: # for each actor in this particular kdrama
#             for drama in data: # check if existing match in data
#                 if drama['id'] != int(id) and genre in drama['genres']: # (BUT CANNOT BE THE SAME ITEM)
#                     itemGenre = drama
#                     break

#     # print(item)
#     # print(item)
#     number = id

#     return render_template('types.html', item=item, itemActor=itemActor, itemGenre=itemGenre, number=number, current_time=current_time, elapsed_time=elapsed_time)

# @app.route('/overview/<int:id>', methods=['GET']) # GET request because just requesting info from server
# def overview(id):
#     item = None
#     number = 0
#     current_time = datetime.now()
#     elapsed_time = get_elapsed_time();
#     print(data)

#     for drama in data:
#         if drama['id'] == int(id): # str by default
#             item = drama
#             break
    
#     # matching item by actor
#     itemActor = None
#     itemGenre = None

#     if item: # item exists
#         actors = item['actors']
#         genres = item['genres']

#         for actor in actors: # for each actor in this particular kdrama
#             for drama in data: # check if existing match in data
#                 if drama['id'] != int(id):
#                     for actor2 in drama['actors']: # (BUT CANNOT BE THE SAME ITEM)
#                         if actor.lower() == actor2.lower():
#                             itemActor = drama
#                             break

#         for genre in genres: # for each actor in this particular kdrama
#             for drama in data: # check if existing match in data
#                 if drama['id'] != int(id) and genre in drama['genres']: # (BUT CANNOT BE THE SAME ITEM)
#                     itemGenre = drama
#                     break

#     # print(item)
#     # print(item)
#     number = id

#     return render_template('overviews.html', item=item, itemActor=itemActor, itemGenre=itemGenre, number=number, current_time=current_time, elapsed_time=elapsed_time)

# @app.route('/example/<int:id>', methods=['GET']) # GET request because just requesting info from server
# def example(id):
#     item = None
#     number = 0
#     current_time = datetime.now()
#     elapsed_time = get_elapsed_time();
#     print(data)

#     for drama in data:
#         if drama['id'] == int(id): # str by default
#             item = drama
#             break
    
#     # matching item by actor
#     itemActor = None
#     itemGenre = None

#     if item: # item exists
#         actors = item['actors']
#         genres = item['genres']

#         for actor in actors: # for each actor in this particular kdrama
#             for drama in data: # check if existing match in data
#                 if drama['id'] != int(id):
#                     for actor2 in drama['actors']: # (BUT CANNOT BE THE SAME ITEM)
#                         if actor.lower() == actor2.lower():
#                             itemActor = drama
#                             break

#         for genre in genres: # for each actor in this particular kdrama
#             for drama in data: # check if existing match in data
#                 if drama['id'] != int(id) and genre in drama['genres']: # (BUT CANNOT BE THE SAME ITEM)
#                     itemGenre = drama
#                     break

#     # print(item)
#     # print(item)
#     number = id

#     return render_template('examples.html', item=item, itemActor=itemActor, itemGenre=itemGenre, number=number, current_time=current_time, elapsed_time=elapsed_time)

# @app.route('/mechanic/<int:id>', methods=['GET']) # GET request because just requesting info from server
# def mechanic(id):
#     item = None
#     number = 0
#     current_time = datetime.now()
#     elapsed_time = get_elapsed_time();
#     print(data)

#     for drama in data:
#         if drama['id'] == int(id): # str by default
#             item = drama
#             break
    
#     # matching item by actor
#     itemActor = None
#     itemGenre = None

#     if item: # item exists
#         actors = item['actors']
#         genres = item['genres']

#         for actor in actors: # for each actor in this particular kdrama
#             for drama in data: # check if existing match in data
#                 if drama['id'] != int(id):
#                     for actor2 in drama['actors']: # (BUT CANNOT BE THE SAME ITEM)
#                         if actor.lower() == actor2.lower():
#                             itemActor = drama
#                             break

#         for genre in genres: # for each actor in this particular kdrama
#             for drama in data: # check if existing match in data
#                 if drama['id'] != int(id) and genre in drama['genres']: # (BUT CANNOT BE THE SAME ITEM)
#                     itemGenre = drama
#                     break

#     # print(item)
#     # print(item)
#     number = id

#     return render_template('mechanics.html', item=item, itemActor=itemActor, itemGenre=itemGenre, number=number, current_time=current_time, elapsed_time=elapsed_time)

# @app.route('/recognition/<int:id>', methods=['GET']) # GET request because just requesting info from server
# def recognition(id):
#     item = None
#     number = 0
#     current_time = datetime.now()
#     elapsed_time = get_elapsed_time();
#     print(data)

#     for drama in data:
#         if drama['id'] == int(id): # str by default
#             item = drama
#             break
    
#     # matching item by actor
#     itemActor = None
#     itemGenre = None

#     if item: # item exists
#         actors = item['actors']
#         genres = item['genres']

#         for actor in actors: # for each actor in this particular kdrama
#             for drama in data: # check if existing match in data
#                 if drama['id'] != int(id):
#                     for actor2 in drama['actors']: # (BUT CANNOT BE THE SAME ITEM)
#                         if actor.lower() == actor2.lower():
#                             itemActor = drama
#                             break

#         for genre in genres: # for each actor in this particular kdrama
#             for drama in data: # check if existing match in data
#                 if drama['id'] != int(id) and genre in drama['genres']: # (BUT CANNOT BE THE SAME ITEM)
#                     itemGenre = drama
#                     break

#     # print(item)
#     # print(item)
#     number = id

#     return render_template('recognitions.html', item=item, itemActor=itemActor, itemGenre=itemGenre, number=number, current_time=current_time, elapsed_time=elapsed_time)


# '''
# Access the add a new kdrama page OR add a new kdrama
# '''
# @app.route('/add', methods=['POST', 'GET']) # GET request because just requesting info from server
# def add_drama():
#     global current_id
#     global data
    
#     if request.method == 'POST':
#         # Access the form data
#         title = request.form.get('title')
#         image_url = request.form.get('image')
#         summary = request.form.get('summary')
#         actors = request.form.get('actors')
#         genres = request.form.get('genres')

#         # Optional: Process the comma-separated actors and genres into lists
#         actors_list = [actor.strip() for actor in actors.split(',')]
#         genres_list = [genre.strip() for genre in genres.split(',')]

#         # Parse the form data
#         new_item = {
#             "id": current_id,
#             "title": title,
#             "image": image_url,
#             "summary": summary,
#             "actors": actors_list,
#             "genres": genres_list
#         }

#         current_id += 1

#         data.append(new_item)

#         return jsonify({"id": new_item["id"]}) # item id of the new item
#     else:
#         return render_template('add_drama.html')
    
# '''
# Edit a kdrama
# '''
# @app.route('/edit/<int:id>', methods=['GET', 'POST'])
# def edit_kdrama(id):
#     item = next((drama for drama in data if drama['id'] == id), None) # shorthand to find the drama by id

#     if not item:
#         return "Item not found", 404
    
#     if request.method == 'POST':
#         # Process the form data and update the item
#         item['title'] = request.form['title']
#         item['image'] = request.form['image']
#         item['summary'] = request.form['summary']
#         item['actors'] = request.form['actors'].split(',')
#         item['genres'] = request.form['genres'].split(',')
#         # Redirect to the view page to see changes
#         return redirect(url_for('view', id=id)) # redirect them to the view/id URL
    
#     else:# For a GET request, render the edit form with the item data
#         return render_template('edit_drama.html', item=item)


# # BRANDON'S CODE FOR LEARNING / QUIZ
# @app.route('/quiz1/<int:state>', methods=['GET'])  # GET request because just requesting info from server
# def quiz1(state):  # Now function takes both 'id' and 'state' as arguments
#     quiz_state = state  # You can now use the 'state' variable inside your function
#     # result = "" # only for the correct/incorrect part

#     return render_template('quiz1.html', state=quiz_state)

# @app.route('/quiz2/<int:state>', methods=['GET'])  # GET request because just requesting info from server
# def quiz2(state):  # Now function takes both 'id' and 'state' as arguments
#     quiz_state = state  # You can now use the 'state' variable inside your function
#     # result = "" # only for the correct/incorrect part

#     return render_template('quiz2.html', state=quiz_state)

# @app.route('/quiz3/<int:state>', methods=['GET'])  # GET request because just requesting info from server
# def quiz3(state):  # Now function takes both 'id' and 'state' as arguments
#     quiz_state = state  # You can now use the 'state' variable inside your function
#     # result = "" # only for the correct/incorrect part

#     return render_template('quiz3.html', state=quiz_state)

# @app.route('/test/<int:state>', methods=['GET'])  # GET request because just requesting info from server
# def test(state):  # Now function takes both 'id' and 'state' as arguments
#     quiz_state = state  # You can now use the 'state' variable inside your function
#     # result = "" # only for the correct/incorrect part

#     return render_template('test.html', state=quiz_state)

# @app.route('/submit/<int:problem_number>', methods=['POST'])
# def submit(problem_number):
#     global score

#     number = request.form['number']
#     print(number)

#     correct_ans = None
#     correct = False

#     problem_number = int(problem_number)

#     if problem_number in attempted: # if they tried this problem already
#         if attempted[problem_number]: # only if they got it correct, then deduct the point
#             score -= 1
    
#     if problem_number == 1:
#         correct_ans = 0
#     elif problem_number == 2:
#         correct_ans = 0
#     elif problem_number == 3:
#         correct_ans = 3
#     elif problem_number == 4:
#         correct_ans = -5
#     elif problem_number == 5:
#         correct_ans = -1
    
#     if int(number) == int(correct_ans): # show at the end
#         score += 1
#         correct = True
    
#     # return redirect(url_for('index'))  # Redirect back to the form page, or wherever you need.
#     return render_template('test_result.html', problem_number=problem_number, your_ans=number, correct_ans=correct_ans, correct=correct, score=score)

if __name__ == '__main__':
   app.run(debug = True)