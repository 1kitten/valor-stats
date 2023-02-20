from typing import Tuple, Optional
import requests
import logging
from rich.console import Console
import os

logger = logging.getLogger('valorant_api')
logging.basicConfig(
    level='INFO'
)

console = Console()


def _send_request(url):
    try:
        response = requests.get(url, timeout=10).json()
    except Exception as exc:
        logging.error(f'The exception {exc} was raised.')
        return
    else:
        if response.get('data'):
            return response['data']
        os.system('clear')
        console.print("""[bold][red]
                Could not get data from this player.
         Please checkout pasted information and try again.[/][/]
        """)
        return


def get_current_mmr_data(user_name: str, tagline: str, region: str) -> Optional[Tuple]:
    url = f'https://api.henrikdev.xyz/valorant/v1/mmr/{region}/{user_name}/{tagline}'
    result = _send_request(url=url)
    if result:
        try:
            username, tag, rank, ranking_in_tier, last_game = result['name'], result['tag'],\
                result['currenttierpatched'], result['ranking_in_tier'], result['mmr_change_to_last_game']
        except KeyError:
            logger.error('Cannot get all the data from gotten response content.')
        else:
            return username, tag, rank, ranking_in_tier, last_game
    return


def get_mmr_history(user_name: str, tagline: str, region: str):
    url = f'https://api.henrikdev.xyz/valorant/v1/mmr-history/{region}/{user_name}/{tagline}'
    result = _send_request(url)
    if result:
        try:
            mmr_change_per_game = [(i_game['ranking_in_tier'], i_game['mmr_change_to_last_game']) for i_game in result]
        except KeyError:
            logger.error('Cannot get mmr history from games.')
        else:
            return mmr_change_per_game
    return


def get_last_match_statistics(user_name: str, tagline: str, region: str):
    url = f'https://api.henrikdev.xyz/valorant/v3/matches/{region}/{user_name}/{tagline}?filter=competitive'
    result = _send_request(url)[0]
    if result:
        try:
            match_data = {
                "map_played": result['metadata']['map'],
                "server": result['metadata']['cluster'],
                "blue_team": _get_players_from_match(result['players']['all_players'])[0],
                "red_team": _get_players_from_match(result['players']['all_players'])[1]
            }
        except KeyError:
            logger.error('Cannot get data from the last played match')
            return
        else:
            return match_data


def _get_players_from_match(players: dict):
    blue_team = []
    red_team = []
    for i_player in players:
        player_info = {
            "nickname": f"{i_player.get('name')}#{i_player.get('tag')}",
            "agent": i_player.get('character'),
            "rank": i_player.get('currenttier_patched'),
            "kda": f"{i_player.get('stats').get('kills')}"
                   f"/{i_player.get('stats').get('deaths')}/{i_player.get('stats').get('assists')}"
        }
        if i_player.get('team') == 'Blue':
            blue_team.append(player_info)
        else:
            red_team.append(player_info)

    return blue_team, red_team


if __name__ == '__main__':
    get_last_match_statistics('aftrr', '000', 'eu')