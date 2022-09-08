from django.shortcuts import render
import requests
from django.core.paginator import Paginator
from dateutil import parser


def home(request):

   return render(request, 'results/home.html', {"message": "hello"})


def parse_nba_url_results(url_nba_results):
    games = []
    for game in url_nba_results['data']:
        result = {
            "home_team": game["home_team"]["full_name"],
            "home_team_score": game["home_team_score"],
            "visitor_team": game["visitor_team"]["full_name"],
            "visitor_team_score": game["visitor_team_score"],
            "game_date": parser.parse(game["date"]).strftime('%Y-%m-%d'),
            "season": game["season"]
        }
        games.append(result)
    return games


def parse_pl_url_results(url_pl_results, season):
    games = []
    for game in url_pl_results['matches']:
        result = {
            "home_team": game["homeTeam"]["name"],
            "home_team_score": game["score"]["fullTime"]["home"],
            "visitor_team": game["awayTeam"]["name"],
            "visitor_team_score": game["score"]["fullTime"]["away"],
            "game_date": parser.parse(game["utcDate"]).strftime('%Y-%m-%d'),
            "season": season
        }
        games.append(result)

    return games


def nba_results(request):

    request_url = 'https://www.balldontlie.io/api/v1/games?seasons[]=2020&per_page=100&page='
    response = requests.get(request_url + "1")
    initial_results = response.json()

    all_games = parse_nba_url_results(initial_results)
    total_pages = initial_results["meta"]["total_pages"]
    page_range = range(2, total_pages + 1)

    for x in page_range:
        response = requests.get(request_url + "1")
        all_games.extend(parse_nba_url_results(response.json()))

    ordered_games = sorted(all_games, key=lambda d: d['game_date'])

    paginator = Paginator(ordered_games, 40)
    page_number = request.GET.get('page')
    all_pages = paginator.get_page(page_number)

    return render(request, 'results/displayresults.html', {"results": all_pages, "league": "NBA"})


def pl_results(request):

    request_url = 'http://api.football-data.org/v4/competitions/PL/matches?season=2020'
    headers = {'X-Auth-Token': '23ce8b7c3bdc4c3fb6a15b0f82e84246', 'Accept-Encoding': ''}

    response = requests.get(request_url, headers=headers)
    initial_results = response.json()

    all_games = parse_pl_url_results(initial_results, 2020)
    ordered_games = sorted(all_games, key=lambda d: d['game_date'])

    paginator = Paginator(ordered_games, 40)
    page_number = request.GET.get('page')
    all_pages = paginator.get_page(page_number)

    return render(request, 'results/displayresults.html', {"results": all_pages, "league": 'PL'})
