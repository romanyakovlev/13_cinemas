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
    html = requests.get("https://www.kinopoisk.ru/index.php?kp_query={}".format(movie_title)).content
    soup = BeautifulSoup(html, "html.parser")
    film_url = soup.find(class_="element most_wanted").find(class_ = "pic").a.attrs["data-url"]
    film_page = requests.get(''.join(["https://www.kinopoisk.ru",film_url])).content
    soup_film = BeautifulSoup(film_page, "html.parser").find(id = "block_rating")
    try:
        kp_rating_count = soup_film.find(class_ = "ratingCount").text
        kp_rating_value = soup_film.find(class_ = "rating_ball").text
    except:
        kp_rating_count = None
        kp_rating_value = 0
    return [kp_rating_count, float(kp_rating_value), movie_name]



def output_movies_to_console(movies):
    sorted_arr = sorted(arr,key=lambda x:-x[1])
    for rating_count, rating_value, film_title, cinema_amount in sorted_arr:
        print('Название: {}, кол-во кинотеатров: {}, рейтинг: {}, кол-во оценок:{}'.format(
            film_title, cinema_amount, rating_value, rating_count
        ))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('cinema_limit')
    cinema_limit = int(parser.parse_args().cinema_limit)
    arr = []
    film_counter = 0
    for movie_name, cinema_amount in parse_afisha_list(fetch_afisha_page()):
        if cinema_amount > cinema_limit:
            arr.append(fetch_movie_info(movie_name)+[cinema_amount])
            film_counter += 1
            print('Программа выполняется...найдено {}/10 фильмов.'.format(film_counter),end="\r")
        if film_counter is 10: break
    print('Первый 10 фильмов, идущих в кинотеатрах, отсортированные по рейтингу (фильтр' +
    ' - {} и более кинотеатров)'.format(cinema_limit))
    output_movies_to_console(arr)
