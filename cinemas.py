import requests
import argparse
import re
from bs4 import BeautifulSoup


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('cinema_limit')
    cinema_limit = int(parser.parse_args().cinema_limit)
    return cinema_limit


def fetch_afisha_page():
    request = requests.get('http://www.afisha.ru/krasnoyarsk/schedule_cinema/')
    return request.content


def parse_afisha_list(raw_html):
    soup =  BeautifulSoup(raw_html, 'html.parser')
    movies_list = soup.find_all(class_="object")
    return [[movie.find(class_="m-disp-table").a.text,
               len(movie.find_all(class_ = "b-td-item"))] for movie in movies_list]


def fetch_movie_info(movie_title):
    request_params = {"text": movie_title}
    data = requests.get("https://plus.kinopoisk.ru/search/films/", params=request_params).content
    soup = BeautifulSoup(data, "html.parser")
    html_film = soup.find(class_="link  film-snippet__media-content").attrs['href']
    film_page = requests.get(html_film).content
    film_soup = BeautifulSoup(film_page, "html.parser")
    film_rating = film_soup.find(class_="rating-button__rating").text
    film_reviews_amount = film_soup.find(class_="film-header__rating-comment").text
    try:
        converted_film_rating = float(film_rating)
    except ValueError:
        converted_film_rating = 0
    return converted_film_rating, film_reviews_amount


def output_movies_to_console(movies):
    sorted_arr = sorted(movies, key=lambda x: -x[2])
    if not sorted_arr:
        print("По вашему запросу ничего не найдено.")
        return None
    for name, cinema_amount, rating, reviews_amount in sorted_arr:
        print('Название: {}, кол-во кинотеатров: {}, рейтинг: {}, кол-во оценок: {}\n'.format(
                name, cinema_amount, rating, reviews_amount))


def parse_kiopoisk_and_filter_by_cinemas(movies_info, cinema_limit):
    movies_list = []
    for movie_name, cinema_amount in movies_info:
        if cinema_amount > cinema_limit:
            film_rating, film_reviews = fetch_movie_info(movie_name)
            movies_list.append([movie_name, cinema_amount, film_rating, film_reviews])
    return movies_list


if __name__ == '__main__':
    cinema_limit = parse_args()
    print('Программа выполняется...')
    movies_list =parse_kiopoisk_and_filter_by_cinemas(parse_afisha_list(fetch_afisha_page()),
                                                                                         cinema_limit)
    print('Первый 10 фильмов, идущих в кинотеатрах, отсортированные по рейтингу (фильтр' +
    ' - {} и более кинотеатров):\n'.format(cinema_limit))
    output_movies_to_console(movies_list)
