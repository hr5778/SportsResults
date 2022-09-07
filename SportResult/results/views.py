from django.shortcuts import render
import requests


def home(request):
   return render(request, 'results/home.html', {"message": "hello"})


def nba_results(request, page_number):
    response = requests.get('https://www.balldontlie.io/api/v1/games?per_page=40&page=' + str(page_number))
    nba_results = response.json()

    meta = {
        "current_page": nba_results["meta"]["current_page"],
        "next_page": nba_results["meta"]["next_page"],
        "previous_page": nba_results["meta"]["current_page"] - 1

    }


    all_games = []
    for game in nba_results['data']:
        result = {
            "home_team": game["home_team"]["full_name"],
            "home_team_score": game["home_team_score"],
            "visitor_team": game["visitor_team"]["full_name"],
            "visitor_team_score": game["visitor_team_score"],
            "game_date": game["date"],
            "season": game["season"]
        }

        all_games.append(result)
    print(len(all_games))
    return render(request, 'results/displayresults.html', {"results": all_games, "page_info": meta})

