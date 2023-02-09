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


if __name__ == '__main__':
    ...
