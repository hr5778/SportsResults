from django.shortcuts import render
import requests
from django.core.paginator import Paginator
from dateutil import parser
from .models import SportLeague, Sport


def home(request):

    # If no Sports Leagues exist then add the leagues
    if not SportLeague.objects.all().exists():
        football = Sport(name="Football")
        football.save()
        basketball = Sport(name="Basketball")
        basketball.save()

        pl = SportLeague(key="PL", name="Premier League", country="UK", sport=football, header='23ce8b7c3bdc4c3fb6a15b0f82e84246', api='http://api.football-data.org/v4/competitions/PL/matches?season=2020')
        pl.save()
        nba = SportLeague(key="NBA", name="NBA", country="USA", sport=basketball, header="", api='https://www.balldontlie.io/api/v1/games?seasons[]=2020&per_page=100&page=')
        nba.save()

    all_leagues = SportLeague.objects.all()

    return render(request, 'results/home.html', {"leagues": all_leagues})


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


def display_results(request, league):
    league_object = SportLeague.objects.get(key=league)
    api = league_object.api

    all_games = []
    if league == "PL":
        request_url = api
        headers = {'X-Auth-Token': league_object.header, 'Accept-Encoding': ''}
        response = requests.get(request_url, headers=headers)
        initial_results = response.json()
        all_games.extend(parse_pl_url_results(initial_results, 2020))
        print(initial_results)

    elif league == "NBA":
        request_url = api + "1"
        response = requests.get(request_url)
        initial_results = response.json()

        all_games.extend(parse_nba_url_results(initial_results))
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
