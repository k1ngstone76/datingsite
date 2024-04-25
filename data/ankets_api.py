import flask
# Согласно архитектуре REST, обмен данными между клиентом и сервером осуществляется в формате JSON (реже — XML).
# Поэтому формат ответа сервера flask изменён с помощью метода jsonify, который преобразует наши данные в JSON.
from flask import request, jsonify

from . import db_session
from .ankets import Anceta

# Механизм разделения приложения Flask на независимые модули
# Как правило, blueprint — логически выделяемый набор обработчиков адресов.
# Blueprint работает аналогично объекту приложения Flask, но в действительности он не является приложением.
blueprint = flask.Blueprint('news_api', __name__, template_folder='templates')


@blueprint.route('/api/anc')
def get_news():
    db_sess = db_session.create_session()
    anc = db_sess.query(Anceta).all()
    # Можно явно указать, какие именно поля оставить в получившемся словаре.
    return jsonify(
        {'anc': [item.to_dict(only=('title', 'content', 'user.name')) for item in anc]})


@blueprint.route('/api/anc/<int:anc_id>', methods=['GET'])
def get_one_news(anc_id):
    db_sess = db_session.create_session()
    # Согласно REST, далее нужно реализовать получение информации об одной новости. Фактически, мы уже получили из списка
    # всю информацию о каждой новости. При проектировании приложений по архитектуре REST обычно поступают таким образом:
    # когда возвращается список объектов, он содержит только краткую информацию (например, только id и заголовок)...
    ank = db_sess.query(Anceta).get(anc_id)
    if not ank:
        return jsonify({'error': 'Not found'})
    # ...а полную информацию (текст и автора) можно посмотреть с помощью запроса, который мы обработаем далее.
    # Можно явно указать, какие именно поля оставить в получившемся словаре.
    return jsonify({'news': ank.to_dict(only=('title', 'content', 'user_id'))})


@blueprint.route('/api/anc', methods=['POST'])
def create_anc():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['title', 'content', 'user_id']):
        return jsonify({'error': 'Bad request'})
    # Проверив, что запрос содержит все требуемые поля, мы заносим новую запись в базу данных.
    # request.json содержит тело запроса, с ним можно работать, как со словарем.
    db_sess = db_session.create_session()

    anc = Anceta(
        title=request.json['title'],
        content=request.json['content'],
        user_id=request.json['user_id']
    )
    db_sess.add(anc)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/ank/<int:ank_id>', methods=['DELETE'])
def delete_ank(ank_id):
    db_sess = db_session.create_session()
    ank = db_sess.query(Anceta).get(ank_id)
    if not ank:
        return jsonify({'error': 'Not found'})
    db_sess.delete(ank)
    db_sess.commit()
    return jsonify({'success': 'OK'})