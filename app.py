from flask import Flask, url_for, redirect, request, render_template, flash, current_app
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import time, json

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'super secret key'

with open('./templates/config.json', 'r') as c:
    params = json.load(c)["params"]
courseName = params['course_name']
courseAbout = params['about']
enterpasskey = params['password']


db = SQLAlchemy(app)
Migrate(app, db)

class Chapters(db.Model):
    __tablename__ = 'chapters'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    slno = db.Column(db.Integer)

    lessons = db.relationship('Lessons', cascade="all,delete", backref='my_chapter', lazy='dynamic')

    def __init__(self, name, slno):
        self.name = name
        self.slno = slno

class Lessons(db.Model):
    __tablename__ = 'lessons'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    slno = db.Column(db.Integer)
    lesson = db.Column(db.Text)

    chapter = db.Column(db.Integer, db.ForeignKey('chapters.id'))
    images = db.relationship('Images', cascade="all,delete", backref='my_lesson', lazy='dynamic')

    def __init__(self, name, chapter, slno, lesson):
        self.name = name
        self.chapter = chapter
        self.slno = slno
        self.lesson = lesson

class Images(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String)

    lesson = db.Column(db.Integer, db.ForeignKey('lessons.id'))

    def __init__(self, image_path, lesson):
        self.image_path = image_path
        self.lesson = lesson

@app.route('/')
def home():
    chapters = Chapters.query.order_by(Chapters.slno).all()
    return render_template('index.html', chapters=chapters, courseName=courseName, courseAbout=courseAbout)

@app.route('/chapter/<int:id>')
def chapter(id):
    lessons = Lessons.query.filter_by(chapter=id).order_by(Lessons.slno).all()
    allImages = {}
    for lesson in lessons:
        images = Images.query.filter_by(lesson=lesson.id)
        if images.count()>0:
            allImages[lesson.id] = images
    chapter = Chapters.query.get(id)
    return render_template('lesson.html', lessons=lessons, allImages=allImages, chapter=id, chapterName=chapter.name, courseName=courseName, courseAbout=courseAbout)

@app.route('/newchapter', methods=['GET', 'POST'])
def newchapter():
    if request.method=='GET':
        chapters = Chapters.query.all()
        newslno = -1
        try:
            for chapter in chapters:
                if int(chapter.slno)>newslno:
                    newslno = chapter.slno
            newslno = newslno + 1
        except:
            newslno = -1
        return render_template('addChapter.html', slno=newslno, courseName=courseName, courseAbout=courseAbout)
    else:
        chapter_name = request.form['chapter_name']
        slno = request.form['slno']
        password = request.form['password']
        if chapter_name is None or chapter_name=='':
            flash('Chapter name can not be blank', 'danger')
            return redirect(url_for('newchapter'))
        if password!=enterpasskey:
            flash('You are not authorized to add a chapter', 'danger')
            return redirect(url_for('newchapter'))
        chapter = Chapters(chapter_name, slno)
        db.session.add(chapter)
        db.session.commit()
        flash(f"Chapter: {chapter_name}, successfully added", 'success')
        return redirect(url_for('home'))

@app.route('/newlesson/<int:chapter>', methods=['GET', 'POST'])
def newlesson(chapter):
    if request.method=='GET':
        lessons = Lessons.query.filter_by(chapter=chapter)
        newslno = -1
        try:
            for lesson in lessons:
                if int(lesson.slno)>newslno:
                    newslno = lesson.slno
            newslno = newslno + 1
        except:
            newslno = -1
        
        return render_template('addLesson.html', chapter=chapter, slno=newslno, courseName=courseName, courseAbout=courseAbout)
    else:
        lesson_name = request.form['lesson_name']
        slno = request.form['slno']
        lesson = request.form['lesson']
        password = request.form['password']
        if password!=enterpasskey:
            flash('You are not authorized to add a lesson', 'danger')
            return render_template('addLesson.html', name=lesson_name, slno=slno, lesson=lesson, chapter=chapter, courseName=courseName, courseAbout=courseAbout)
        if lesson_name is None or lesson_name=='':
            flash('Lesson Name cannot be blank', 'danger')
            return render_template('addLesson.html', name=lesson_name, slno=slno, lesson=lesson, chapter=chapter, courseName=courseName, courseAbout=courseAbout)
        newLesson = Lessons(lesson_name, chapter, slno, lesson)
        db.session.add(newLesson)
        db.session.commit()
        # name, chapter, slno, lesson

        image = request.files['image']
        lesson_id = Lessons.query.filter_by(name=lesson_name).first().id
        try:
            if image:
                storage_filename = str(time.time()).replace('.','')+'.'+image.filename.split('.')[-1]
                filepath = os.path.join(current_app.root_path,'static', 'img', storage_filename)
                image.save(filepath)
                image = Images(storage_filename, lesson_id)
                db.session.add(image)
                db.session.commit()
                flash('Image added successfully', 'success')
        except Exception as e:
            flash('Image not added due to some error'+str(e), 'danger')

        flash('Lesson added successfully', 'success')
        return redirect(url_for('chapter', id=chapter))

@app.route('/update/chapter/<int:id>', methods=['GET', 'POST'])
def updateChapter(id):
    chapter = Chapters.query.get(id)
    if request.method=='GET':
        return render_template('updateChapter.html', chapter=chapter, courseName=courseName, courseAbout=courseAbout)
    else:
        password = request.form['password']
        if password!=enterpasskey:
            flash('You can not modify the chapter', 'danger')
            return redirect(url_for('chapter', id=id))
        chapter_name = request.form['chapter_name']
        slno = request.form['slno']
        try:
            if chapter_name=='' or slno=='':
                flash('Chapter name or Chapter serial number can not be none', 'danger')
                return redirect(url_for('updateChapter', id=id))
            chapter.name = chapter_name
            chapter.slno = slno
            
            db.session.add(chapter)
            db.session.commit()
            flash('Chapter Updated Successfully', 'success')
            return redirect(url_for('chapter', id=chapter.id))
        except:
            flash(('Chapter cannot be updated due to some error', 'danger'))
            return render_template('updateChapter.html', chapter=chapter, courseName=courseName, courseAbout=courseAbout)

@app.route('/update/lesson/<int:id>', methods=['GET', 'POST'])
def updateLesson(id):
    lesson = Lessons.query.get(id)
    images = Images.query.filter_by(lesson=lesson.id)
    if request.method=='GET':
        return render_template('updateLesson.html', lesson=lesson, images=images, courseName=courseName, courseAbout=courseAbout)
    else:
        password = request.form['password']        
        lesson_name = request.form['lesson_name']
        lesson_body = request.form['lesson']
        lesson_slno = request.form['slno']
        if password!=enterpasskey:
            flash('You can not modify the lesson', 'danger')
            return render_template('updateLesson.html', lesson=lesson, images=images, edited_name=lesson_name, edited_lesson=lesson_body, courseName=courseName, courseAbout=courseAbout)
        if not lesson_name=='' or not lesson=='':
            lesson.name = lesson_name
            lesson.lesson = lesson_body
            lesson.slno = lesson_slno            
            db.session.add(lesson)
            db.session.commit()
            flash('Lesson updated successful', 'success')
        else:
            flash('Lesson Name or Lesson cannot be blank', 'danger')
            return render_template('updateLesson.html', lesson=lesson, images=images, edited_name=lesson_name, edited_lesson=lesson_body, courseName=courseName, courseAbout=courseAbout)
        image = request.files['image']
        try:
            if image:
                storage_filename = str(time.time()).replace('.','')+'.'+image.filename.split('.')[-1]
                filepath = os.path.join(current_app.root_path,'static', 'img', storage_filename)
                image.save(filepath)
                image = Images(storage_filename, lesson.id)
                db.session.add(image)
                db.session.commit()
                flash('Image added successfully', 'success')
        except Exception as e:
            flash('Image not added due to some error'+str(e), 'danger')


        remove_images = request.form.getlist('rmv_imgs')
        remove_images_success_count = 0
        remove_images_fail_count = 0
        for rm_img in remove_images:
            img = Images.query.get(rm_img)
            try:
                filepath = os.path.join(current_app.root_path,'static/img', img.image_path)
                db.session.delete(img)
                db.session.commit()
                os.chmod(filepath, 777)
                os.remove(filepath)
                remove_images_success_count = remove_images_success_count + 1
            except Exception as e:
                flash(str(e), 'danger')
                remove_images_fail_count = remove_images_fail_count + 1

        if remove_images_success_count>0:
            flash(f'{remove_images_success_count} images deleted successfully', 'success')
        if remove_images_fail_count>0:
            flash(f'{remove_images_fail_count} images cannot be deleted due to somee error.', 'danger')

        return redirect(url_for('chapter', id=lesson.chapter))

@app.route('/delete/lesson/<int:id>', methods=['POST'])
def deleteLesson(id):
    if request.method=='POST':
        try:
            password = request.form['password']
            lesson = Lessons.query.get(id)
            images = Images.query.filter_by(lesson=id)
            if password!=enterpasskey:
                flash('You can not delete the lesson', 'danger')
                return redirect(url_for('chapter', id=lesson.chapter))
            for img in images:
                filepath = os.path.join(current_app.root_path,'static/img', img.image_path)
                os.chmod(filepath, 777)
                os.remove(filepath)

            db.session.delete(lesson)
            db.session.commit()
            flash('Lesson deleted successful', 'success')
        except:
            flash('Lesson can not be deleted due to some error', 'danger')
        return redirect(url_for('chapter', id=lesson.chapter))

@app.route('/delete/chapter/<int:id>', methods=['POST'])
def deleteChapter(id):
    if request.method=='POST':
        try:
            password = request.form['password']
            if password!=enterpasskey:
                flash('You can not delete the chapter', 'danger')
                return redirect(url_for('chapter', id=id))
            chapter = Chapters.query.get(id)
            lessons = Lessons.query.filter_by(chapter=id)
            for lesson in lessons:
                images = Images.query.filter_by(lesson=lesson.id)
                for image in images:
                    filepath = os.path.join(current_app.root_path,'static/img', image.image_path)
                    os.chmod(filepath, 777)
                    os.remove(filepath)
            db.session.delete(chapter)
            db.session.commit()
            flash('Chapter deleted successful', 'success')
        except:
            flash('Chapter can not be deleted due to some error', 'danger')
        return redirect(url_for('home'))

@app.route('/search')
def search():
    lessons = Lessons.query.all()
    chapters = Chapters.query.all()
    search_term = request.args.get('search')

    terms = request.args.get('search').split()
    search_results_lessons = set()
    search_results_chapters = set()
    for chapter in chapters:
        for term in terms:
            if str(chapter.name.lower()).find(term.lower())>-1:
                search_results_chapters.add(chapter)
    for lesson in lessons:
        for term in terms:
            if lesson.name.lower().find(term.lower())>-1 or lesson.lesson.lower().find(term.lower())>-1:
                search_results_lessons.add(lesson)

    lessons = list(search_results_lessons)
    temp = []
    for lesson in lessons:
        chapter_name = Chapters.query.get(lesson.chapter).name
        temp.append([lesson.id, lesson.chapter, lesson.name, chapter_name])
        
    chapters = list(search_results_chapters)
    lessons = temp
    noOfResult = len(lessons)+len(chapters)
    return render_template('search.html', noOfResult=noOfResult, lessons=lessons, chapters=chapters, search_term = search_term, courseName=courseName, courseAbout=courseAbout)

@app.route('/about')
def about():
    return render_template('about.html', courseName=courseName, courseAbout=courseAbout)

# if __name__ == "__main__":
#     app.run(debug=True)
