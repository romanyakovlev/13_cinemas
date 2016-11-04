import requests
import re
from bs4 import BeautifulSoup
import argparse


def fetch_afisha_page():
    r = requests.get('http://www.afisha.ru/krasnoyarsk/schedule_cinema/')
    return r.content


def parse_afisha_list(raw_html):
    soup =  BeautifulSoup(raw_html, 'html.parser')
    s = soup.find_all(class_ = "object")
    return [[x.find(class_ = "m-disp-table").a.text, len(x.find_all(class_ = "b-td-item"))] for x in s]


def fetch_movie_info(movie_title):
    payload = {'keyword': movie_title}
    js = requests.get("http://api.kinopoisk.cf/searchFilms", params=payload).json()
    rating_and_reviews = js["searchFilms"][0]["rating"]
    rating, reviews_amount = re.compile(r'^([0-9.]+[%]{0,1})[ ]\(([0-9 ]*)\)$').search(rating_and_reviews).groups()
    if "%" in rating: rating = int(rating[:-1])/10
    return [movie_name, cinema_amount, float(rating), int(reviews_amount.replace(' ', ''))]


def output_movies_to_console(movies):
    sorted_arr = sorted(arr,key=lambda x:-x[2])
    for name, cinema_amount, rating, reviews_amount in sorted_arr:
        print('Название: {}, кол-во кинотеатров: {}, рейтинг: {}, кол-во оценок:{}'.format(
        name, cinema_amount, rating, reviews_amount
        ))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('cinema_limit')
    cinema_limit = int(parser.parse_args().cinema_limit)
    arr = []
    print('Программа выполняется...')
    for movie_name, cinema_amount in parse_afisha_list(fetch_afisha_page()):
        if cinema_amount > cinema_limit:
            arr.append(fetch_movie_info(movie_name))
    print('Первый 10 фильмов, идущих в кинотеатрах, отсортированные по рейтингу (фильтр' +
    ' - {} и более кинотеатров)'.format(cinema_limit))
    output_movies_to_console(arr)
