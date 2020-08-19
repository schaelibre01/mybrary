from pymongo import MongoClient
from flask import Flask, render_template, jsonify, request
import requests
import json
from konlpy.tag import Kkma
from re import match
from collections import Counter


app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.dbsparta


# HTML 화면 보여주기
@app.route('/')
def home():
    return render_template('index.html')


# GET 요청 예시
@app.route('/search', methods=['GET'])
def show_stars():
    # 1. db에서 mystar 목록 전체를 검색합니다. ID는 제외하고 like 가 많은 순으로 정렬합니다.
    # 참고) find({},{'_id':False}), sort()를 활용하면 굿!
    # 2. 성공하면 success 메시지와 함께 stars_list 목록을 클라이언트에 전달합니다.
    return jsonify({'result': 'success', 'msg': 'list 연결되었습니다!'})


# POST 요청 예시
@app.route('/search', methods=['POST'])
def search_keyword():
    url = 'https://openapi.naver.com/v1/search/book.json?'
    client_id = "QpvvkiISGC1mn16KVb3d"
    client_secret = "ukKNKa8DVk"
    keyword = request.form.get('keyword')
    query_string = "query=" + keyword + "&display=10&start=1&sort=count"
    header = {
        "X-Naver-Client-ID": client_id,
        "X-Naver-Client-secret": client_secret
    }
    r = requests.get(url + query_string, headers=header)
    books = json.loads(r.text)['items']
    all_text = ''
    for book in books:
        all_text += book['description']
    kkma = Kkma()
    ex_sent = kkma.sentences(all_text)
    nouns = []
    for sent in ex_sent :
        for noun in kkma.nouns(sent):
            if len(str(noun)) > 2 and not(match('^[0-9]', noun)):
                nouns.append(noun)
    nouns_count = Counter(nouns)
    chart_index = sorted(nouns_count, reverse=True, key=lambda item: item[1])
    chart_values = list(nouns_count.values())

    return jsonify({'result': 'success', 'books': books, 'chart_index': chart_index, 'chart_values' : chart_values})


if __name__ == '__main__':
    app.run('localhost', port=5000, debug=True)
