#--coding:utf-8--#
_author_='hcy'
from flask import Blueprint,jsonify,abort,render_template,request,json

firstdemo_api = Blueprint('firstdemo_api', __name__, template_folder='templates')

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]


@firstdemo_api.route('/fm/merchant/api/v1.0/tasks', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': tasks})


@firstdemo_api.route('/fm/merchant/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = filter(lambda t: t['id'] == task_id, tasks)
    if len(task) == 0:
        abort(404)
    return jsonify({'task': task[0]})


@firstdemo_api.route('/fm/merchant/api/v1.0/tasks1', methods=['POST'])
def create_task():
    print request.data
    jsonstr = eval(request.data)
    print jsonstr['title']
    if not jsonstr or not 'title' in jsonstr:
        abort(400)
    task = {
        'id':  1,
        'title': jsonstr['title'],
        'description': 1,
        'done': False
    }
    tasks.append(task)
    print tasks
    return jsonify(task)


@firstdemo_api.route('/fm/merchant/api/v1.0/tasks/<int:task_id>',methods=['PUT'])
def update_task(task_id):
    task = filter(lambda t:t['id'] == task_id,tasks)
    print request.json
    print request.data
    if len(task)==0:
        abort(404)
    if not request.data:
        abort(400)
    if 'title' in request.json and type(request.json['title']) != unicode:
        abort(400)
    if 'description' in request.json and type(request.json['description']) is not unicode:
        abort(400)
    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)
    task[0]['title'] = request.json.get('title', task[0]['title'])
    task[0]['description'] = request.json.get('description', task[0]['description'])
    task[0]['done'] = request.json.get('done', task[0]['done'])
    return  jsonify({'task':task[0]})




@firstdemo_api.route('/aaa')
def aaa():
    return render_template("/test/posttest.html")
