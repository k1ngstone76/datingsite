from flask import jsonify
from flask_restful import abort, Resource

from data import db_session
from data.ankets import Anceta
from data.reqparse import parser


def abort_if_anc_not_found(anc_id):  # вместо @app.errorhandler(404)
    session = db_session.create_session()
    anc = session.query(Anceta).get(anc_id)
    if not anc:
        # Функция abort генерирует HTTP-ошибку с нужным кодом и возвращает ответ в формате JSON
        abort(404, message=f"anc {anc_id} not found")


# Для каждого ресурса (единица информации в REST называется ресурсом: новости, пользователи и т. д.) создается
# два класса: для одного объекта и для списка объектов: здесь это NewsResource и NewsListResource соответственно.

class AncResource(Resource):
    def get(self, anc_id):
        abort_if_anc_not_found(anc_id)
        session = db_session.create_session()
        anc = session.query(Anceta).get(anc_id)
        return jsonify({'anketa': anc.to_dict(
            only=('title', 'content', 'user_id'))})

    def delete(self, anc_id):
        abort_if_anc_not_found(anc_id)
        session = db_session.create_session()
        anc = session.query(Anceta).get(anc_id)
        session.delete(anc)
        session.commit()
        return jsonify({'success': 'OK'})

    #     get и post - без аргументов.
    #     Доступ к данным, переданным в теле POST-запроса - парсинг аргументов (reqparse)


class AnkListResource(Resource):
    def get(self):
        session = db_session.create_session()
        anc = session.query(Anceta).all()
        return jsonify({'anketa': [item.to_dict(
            only=('title', 'content', 'user.name')) for item in anc]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        anc = Anceta(
            title=args['title'],
            content=args['content'],
            user_id=args['user_id']
        )
        session.add(anc)
        session.commit()
        return jsonify({'success': 'OK'})
