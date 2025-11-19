from app import create_app, db
from app.models.user import User
from app.models.task import Task
from app.models.comment import Comment

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Task': Task, 'Comment': Comment}

if __name__ == '__main__':
    seed_data()
    app.run(debug=True, host='0.0.0.0', port=5000)

