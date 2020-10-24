from app import db, Chapters, Lessons, Images

all_data = Chapters.query.all()
for data in all_data:
    print(data.id, data.name)

all_data = Lessons.query.all()
for data in all_data:
    print(data.id, data.name, data.chapter)

all_data = Images.query.all()
for data in all_data:
    print(data.id, data.image_path, data.lesson)