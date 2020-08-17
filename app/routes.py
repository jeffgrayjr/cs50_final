from flask import render_template, flash, redirect, url_for, request, jsonify
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, CreateCharacter, ViewCharacter, AddItem, AddImprovement, AddCharacterNote, AddMove, LevelUp
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app.models import User, Character, Character_Class, Item, Improvement, class_improvements, character_improvements, Character_Note, Move, character_moves
from datetime import datetime
import random

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/')
@app.route('/index')
@login_required
def index():
    user = User.query.filter_by(username=current_user.username).first_or_404()
    characters = Character.query.filter_by(user_id=user.id)
    
    return render_template('index.html', title="Home", characters=characters)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Succesfully registered!')
        return redirect(url_for('login'))
    return render_template('register.html', title="Register", form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    characters = Character.query.filter_by(user_id=user.id)
    
    return render_template('user.html', user=user, characters=characters)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@app.route('/character/<char_id>', methods=['GET', 'POST'])
@login_required
def view_character(char_id):
    form = ViewCharacter()
    add_item = AddItem()
    add_note = AddCharacterNote()
    add_improvement = AddImprovement()
    character = Character.query.filter_by(id=char_id).first_or_404()
    char_class = Character_Class.query.filter_by(id=character.char_class).first()
    char_items = Item.query.filter_by(owner=char_id).all()
    char_notes = Character_Note.query.filter_by(owner=char_id).all()
    improvements_for_class = Character_Class.query.join(class_improvements).join(Improvement).filter(class_improvements.c.character_class==char_class.id).first()
    add_improvement.improvement.choices = [(d.id, d.description) for d in improvements_for_class.improvements]
    current_char_improvements = Character.query.join(character_improvements).join(Improvement).filter(character_improvements.c.character_id==character.id).first()
    current_char_moves = Character.query.join(character_moves).join(Move).filter(character_moves.c.character_id==character.id).first()
    try:
        current_char_improvements = current_char_improvements.char_improvements
    except:
        current_char_improvements = ['None']
    try:
        current_char_moves = current_char_moves.char_moves
    except:
        current_char_moves = ['None']

    if form.validate_on_submit():
        character.harm = form.harm_radio.data
        character.luck = form.luck_radio.data
        character.experience = form.experience.data
        db.session.commit()
        flash('Changes saved')
        return redirect(url_for('view_character', char_id=character.id))
    elif request.method == 'GET':
        form.harm_radio.data = character.harm
        form.luck_radio.data = character.luck
        form.experience.data = character.experience
    return render_template('character.html', character=character, character_class=char_class, char_items=char_items, form=form, add_item=add_item, add_improvement=add_improvement, current_char_improvements=current_char_improvements, add_note=add_note, char_notes=char_notes, current_char_moves=current_char_moves)

@app.route('/character/create', methods=['GET', 'POST'])
@login_required
def create_character():
    classes = Character_Class.query.all()
    form = CreateCharacter()
    form.character_class.choices = [(c.id, c.class_name) for c in Character_Class.query.all()]
    if form.validate_on_submit():
        character = Character(user_id=current_user.id, name=form.character_name.data, char_class=form.character_class.data, charm=form.charm.data, cool=form.cool.data, sharp=form.sharp.data, tough=form.tough.data, weird=form.weird.data)
        db.session.add(character)
        db.session.commit()
        flash('Success!')
        #return redirect(url_for('index'))
        return redirect(url_for('add_move', char_id = character.id))
    #url_for('add_move', char_id=char_id)
    return render_template('create_character.html', title="New Character", form=form, form_title="New Chracter")

@app.route('/edit/<char_id>/', methods=['GET', 'POST'])
@login_required
def edit_character(char_id):
    classes = Character_Class.query.all()
    form = CreateCharacter()
    form.character_class.choices = [(c.id, c.class_name) for c in Character_Class.query.all()]
    character = Character.query.filter_by(id=char_id).first_or_404()
    char_class = Character_Class.query.filter_by(id=character.char_class).first()

    if form.validate_on_submit():
        character.name = form.character_name.data
        character.char_class = form.character_class.data
        #character.level = form.level.data
        character.charm = form.charm.data
        character.cool = form.cool.data
        character.sharp = form.sharp.data
        character.tough = form.tough.data
        character.weird = form.weird.data
        db.session.commit()
        flash('Changes have been saved')
        if request.args.get('source') == 'char_view':
            return redirect(url_for('view_character', char_id=character.id))
        else:
            return redirect(url_for('index'))
    elif request.method == 'GET':
        form.character_name.data = character.name
        form.character_class.data = character.char_class
        #form.level.data = character.level
        form.charm.data = character.charm
        form.cool.data = character.cool
        form.sharp.data = character.sharp
        form.tough.data = character.tough
        form.weird.data = character.weird
    
    return render_template('edit_character.html', title='Edit Character', form=form, form_title="Edit Chracter", char_id=char_id)


@app.route('/add_item/<char_id>', methods=['GET', 'POST'])
@login_required
def add_item(char_id):
    form = AddItem()
    if form.validate_on_submit():
        item = Item(owner=char_id, name=form.name.data, description = form.description.data, tags = form.tags.data)
        db.session.add(item)
        db.session.commit()
    else:
        flash('Invalid item')
    return redirect(url_for('view_character', _anchor='inventory', char_id=char_id))

@app.route('/remove_item/<char_id>/<item_id>', methods=['GET', 'POST'])
@login_required
def remove_item(item_id, char_id):
    item_to_delete = Item.query.filter_by(id=int(item_id)).first()
    db.session.delete(item_to_delete)
    db.session.commit()
    return redirect(url_for('view_character', _anchor='inventory', char_id=char_id))

@app.route('/remove_note/<char_id>/<note_id>', methods=['GET', 'POST'])
@login_required
def remove_note(note_id, char_id):
    note_to_delete = Character_Note.query.filter_by(id=int(note_id)).first()
    db.session.delete(note_to_delete)
    db.session.commit()
    return redirect(url_for('view_character', char_id=char_id))

@app.route('/add_improvement/<char_id>', methods=['POST'])
@login_required
def add_improvement(char_id):
    add_improvement = AddImprovement()
    character = Character.query.filter_by(id=char_id).first_or_404()
    char_class = Character_Class.query.filter_by(id=character.char_class).first()
    test_improvements = Character_Class.query.join(class_improvements).join(Improvement).filter(class_improvements.c.character_class==char_class.id).first()
    add_improvement.improvement.choices = [(c.id, c.description) for c in test_improvements.improvements]
    if add_improvement.validate_on_submit():
        character = Character.query.filter_by(id=char_id).first_or_404()
        improvement = Improvement.query.filter_by(id=add_improvement.improvement.data).first()
        character.char_improvements.append(improvement)
        db.session.commit()
        flash('Success!')
    else:
        flash('Error')
    return redirect(url_for('view_character', char_id=char_id))

@app.route('/add_note/<char_id>', methods=['POST'])
@login_required
def add_note(char_id):
    add_note = AddCharacterNote()
    if add_note.validate_on_submit():
        note = Character_Note(note=add_note.note.data, owner=char_id)
        db.session.add(note)
        db.session.commit()
    else:
        flash('Invalid input')
    return redirect(url_for('view_character', char_id=char_id))

@app.route('/add_move/<char_id>', methods=['GET', 'POST'])
@login_required
def add_move(char_id):
    add_move = AddMove()
    character = Character.query.filter_by(id=char_id).first_or_404()
    char_class = Character_Class.query.filter_by(id=character.char_class).first()
    moves_for_class = Move.query.filter_by(move_class=char_class.id).all()
    add_move.new_move.choices = [(c.id, c.name) for c in moves_for_class]
    if add_move.validate_on_submit():
        character = Character.query.filter_by(id=char_id).first_or_404()
        moves = add_move.new_move.data
        for i in range(len(moves)):
            move = Move.query.filter_by(id=moves[i]).first()
            character.char_moves.append(move)
        db.session.commit()
        flash('Success!')
    elif request.method == 'GET':
        return render_template('add_move.html', title='Add Move', add_move = add_move, form_title="Add Moves", char_id=char_id)
    else:
        flash('Invalid input')
    return redirect(url_for('view_character', char_id=char_id))

@app.route('/roll', methods=['POST'])
@login_required
def roll_dice():
    rating = request.form['rating']
    d6_1 = random.randint(1, 6)
    d6_2 = random.randint(1, 6)
    total_roll = d6_1 + d6_2 + int(rating)
    return jsonify({'rating': request.form['rating'], 'roll_1': d6_1, 'roll_2': d6_2, 'total': total_roll})

@app.route('/level_up/<char_id>', methods=['GET', 'POST'])
@login_required
def level_up(char_id):
    level_up = LevelUp()
    character = Character.query.filter_by(id=char_id).first_or_404()
    char_class = Character_Class.query.filter_by(id=character.char_class).first()
    improvements_for_class = Character_Class.query.join(class_improvements).join(Improvement).filter(class_improvements.c.character_class==char_class.id).first()
    moves_for_class = Move.query.filter_by(move_class=character.char_class).all()
    #improvement choice
    level_up.improvement.choices = [(d.id, d.description) for d in improvements_for_class.improvements]
    level_up.improvement.choices.insert(0, (0, "Add Improvement"))
    #new move choices for current class, can do different classes via ajax request
    level_up.new_move.choices = [(c.id, c.name) for c in moves_for_class]
    level_up.new_move.choices.insert(0, (0, 'Add Move'))
    if level_up.validate_on_submit():
        character = Character.query.filter_by(id=char_id).first_or_404()
        improvement = Improvement.query.filter_by(id=level_up.improvement.data).first()
        character.char_improvements.append(improvement)
        if level_up.new_move.data != 0:
            move = Move.query.filter_by(id=level_up.new_move.data).first()
            character.char_moves.append(move)
            flash("Move added")
        character.level += 1
        character.experience = 0
        db.session.commit()
        return redirect(url_for('view_character', char_id=char_id))
    elif request.method == 'GET':
        pass
    else:
        flash('Error')
    return render_template('level_up.html', title='Level Up', level_up=level_up, form_title="Level Up")

@app.route('/save_changes', methods=['POST'])
@login_required
def save_changes():
    character = Character.query.filter_by(id=int(request.form['char_id'])).first_or_404()
    character.harm = int(request.form['harm'])
    character.luck = int(request.form['luck'])
    character.experience = int(request.form['exp'])
    db.session.commit()
    return ('', 204)

@app.route('/delete_character', methods=['POST'])
@login_required
def delete_character():
    #pass
    char_id = request.form['char_id']
    character = Character.query.filter_by(id=char_id).first_or_404()
    char_items = Item.query.filter_by(owner=char_id).all()
    for i in range(len(char_items)):
        db.session.delete(char_items[i])
    char_notes = Character_Note.query.filter_by(owner=char_id).all()
    for j in range(len(char_notes)):
        db.session.delete(char_notes[j])
    db.session.delete(character)
    db.session.commit()
    return jsonify({"redirect": url_for('index')})