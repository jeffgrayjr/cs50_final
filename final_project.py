from app import app, db
from app.models import User, Character, Character_Class, Item, Character_Note, Improvement, Move, class_improvements

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Character': Character, 'Item': Item, 'Character_Note': Character_Note, 'Improvement': Improvement, 'Move': Move, 'class_improvements': class_improvements}