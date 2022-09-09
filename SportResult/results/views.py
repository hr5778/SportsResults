from django.shortcuts import render
import requests
from django.core.paginator import Paginator
from dateutil import parser
from .models import SportLeague, Sport
from django.http import HttpResponse


def home(request):
    """Initial home page allowing user to choose their sports league
    """
   # If initial load, store sports league information in models
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
    """
    Parse results from nba api and retrieve scores for each game
    :param url_nba_results: Json from the NBA API
    :return: List of dictionaries, where each dictionary contains the results of a game
    """
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
    """
    Parse results from Premier league api and retrieve scores for each game
    :param url_pl_results: Json results from Premier league api
    :param season: season the api was queried with
    :return: List of dictionaries, where each dictionary contains the results of a game
    """
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
    """
    Gets the results for the 2020 season for the selected sports league
    :param league: NBA or PL
    :return: results of all games to be rendered in the template
    """
    match_date = None

    league_object = SportLeague.objects.get(key=league)
    api = league_object.api

    if request.method == "GET" and "match_date" in request.GET:
        match_date = request.GET["match_date"]

    all_games = []
    if ('all_results_' + league not in request.session) or match_date is not None:
        if league == "PL":

            # Query PL API and parse results
            headers = {'X-Auth-Token': league_object.header, 'Accept-Encoding': ''}
            request_url = api
            if match_date is not None:
                request_url = request_url + "&dateTo=" + match_date + "&dateFrom=" + match_date
            try:
                response = requests.get(request_url, headers=headers)
                initial_results = response.json()
            except requests.exceptions.RequestException as e:
                return HttpResponse("Error retrieving data. Please contact admin")

            all_games.extend(parse_pl_url_results(initial_results, 2020))

        elif league == "NBA":
            # Query NBA API and parse results
            request_url = api + "1"

            if match_date is not None:
                request_url = request_url + "&dates[]=" + match_date

            try:
                response = requests.get(request_url)
                initial_results = response.json()
                all_games.extend(parse_nba_url_results(initial_results))
                total_pages = initial_results["meta"]["total_pages"]
                page_range = range(2, total_pages + 1)

                # Return all results from the API
                for x in page_range:
                    request_url = api + str(x)
                    if match_date is not None:
                        request_url = request_url + "&dates[]=" + match_date
                    response = requests.get(request_url)
                    all_games.extend(parse_nba_url_results(response.json()))
            except requests.exceptions.RequestException as e:
                return HttpResponse("Error retrieving data. Please contact admin")

        # Add all results to session
        if match_date is None:
            request.session["all_results_" + league] = sorted(all_games, key=lambda d: d['game_date'])

    # Get results from session if a date has not been set
    if match_date is None:
        ordered_games = request.session["all_results_" + league]
    else:
        ordered_games = sorted(all_games, key=lambda d: d['game_date'])

    # Paginate the results
    paginator = Paginator(ordered_games, 40)
    page_number = request.GET.get('page')
    all_pages = paginator.get_page(page_number)
    return render(request, 'results/displayresults.html', {"results": all_pages, "league": league_object, "match_date": match_date})
