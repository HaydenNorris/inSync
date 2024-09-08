from flask import jsonify

class Resource:
    def json(self) -> 'json':
        return jsonify(self.data())