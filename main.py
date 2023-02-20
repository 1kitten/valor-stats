import os
import time
from typing import Optional, Callable, Tuple, List, Union, Dict

import rich
from rich.console import Console
from rich.progress import track
from rich.table import Table

from valorant_api import (
    get_current_mmr_data,
    get_mmr_history,
    get_last_match_statistics
)

console: rich.console.Console = Console()


def show_user_menu() -> None:
    """ Print user interface in console. """
    console.print(
        """
        [bold]
        [red]1)[/] Current MMR data.
        [red]2)[/] MMR history.
        [red]3)[/] Last match overall statistics.
        [blink]4) Exit.[/]
        [/] 
        """
    )
    _ask_user_for_menu_input()


def _ask_user_for_menu_input() -> Optional[Callable]:
    """ Asking user to choose an option from menu"""
    console.print("[bold]Choose the option from [red]menu[/]:[/]", end=' ')
    user_menu_choice = str(input())
    if user_menu_choice not in ('1', '2', '3', '4'):
        os.system('clear')
        console.print('Please choose only the option from menu :clown_face:')
        show_user_menu()
    return _check_user_input(user_menu_choice)


def _ask_user_for_account_data() -> Tuple[str, str, str]:
    """ Asking user for valorant player data. Such as nickname, tagline etc. """
    console.print("[bold][red]Nickname[/][/]:", end=' ')
    user_nickname: str = str(input())
    while not user_nickname:
        console.print("[bold]You [red]need[/] to paste nickname![/]:", end=' ')
        user_nickname = str(input())

    console.print("[bold][red]Tagline[/][/] [italic](ex. #[white]000[/])[/]:", end=' ')
    user_tagline: str = str(input())
    while not user_tagline:
        console.print("[bold]You [red]need[/] to paste tagline![/]:", end=' ')
        user_tagline = str(input())

    console.print("[bold][red]Region[/][/] [italic]choose [red]from[/] (eu, na, kr)[/]:", end=' ')
    user_region: str = str(input())
    while user_region not in ('eu', 'na', 'kr'):
        console.print("[bold]Please choose region [red]from[/] (eu, na, kr):[/]", end=' ')
        user_region = str(input())

    return user_nickname, user_tagline, user_region


def _check_user_input(user_input: str):
    """
    Checking user input from console
    :param: user_input. The one option from console menu.
    """
    account_data: Tuple = _ask_user_for_account_data()
    nickname, tagline, region = account_data[0], account_data[1], account_data[2]

    if user_input == '4':
        console.print('[bold]Bye-bye :wave: [/]')
        exit(0)
    elif user_input == '1':
        curr_mmr: Tuple = get_current_mmr_data(user_name=nickname, tagline=tagline, region=region)
        if not curr_mmr:
            show_user_menu()
        else:
            _format_output(mode='current_mmr_data', data=curr_mmr)
    elif user_input == '2':
        mmr_hist: List = get_mmr_history(user_name=nickname, tagline=tagline, region=region)
        if not mmr_hist:
            show_user_menu()
        else:
            _format_output(mode='mmr_history', data=mmr_hist)
    else:
        match_data = get_last_match_statistics(user_name=nickname, tagline=tagline, region=region)
        if not match_data:
            show_user_menu()
        else:
            _format_output(mode='match_data', data=match_data)


def _format_output(mode: str, data: Union[List, Tuple, Dict]):
    """
    Printing formatted information for user in console
    :param: mode. The mode for output format in console.
    :param: data. User in game data.
    """
    if mode == 'current_mmr_data':
        nickname, tag, rank, mmr, last_game = data[0], data[1], data[2], data[3], data[4]

        console.print()
        for _ in track(range(10), description='Loading data...'):
            time.sleep(0.1)

        if str(last_game).startswith('-'):
            _last_game_result_for_output = f"[red]{last_game} :disappointed_relieved:[/]"
        else:
            _last_game_result_for_output = f"[green]{last_game} :grinning:[/]"

        console.print(
            f"""
            [bold]
            [red]Nickname[/]: [red on white]{nickname}#{tag}[/]
            [red]Rank[/]: [red on white]{rank}[/] ([cyan]{mmr}[/])
            [red]Last game result[/]: {_last_game_result_for_output}
            [/]
            """
        )
    elif mode == 'mmr_history':
        console.print()
        won_games: int = 0
        for _ in track(data, description='Loading data...'):
            time.sleep(0.1)

        for i_game in data:
            if str(i_game[1]).startswith('-'):
                console.print(f"[red]{i_game[0]}[/] | [red]{i_game[1]}[/]")
            else:
                won_games += 1
                console.print(f"[green]{i_game[0]}[/] | [green][bold]+[/]{i_game[1]}[/]")
            time.sleep(0.1)

        user_winrate = _get_winrate(total_games_played=len(data), games_won=won_games)
        _create_table_for_match_history(winrate=user_winrate, total_games=len(data), won_games=won_games)
    else:
        console.print(
            f"""
            [bold][green]Map played:[/] {data.get('map_played')}
            [yellow]Server:[/] {data.get('server')}[/]
            """
        )

        console.print("[bold][blue]Blue Team:[/][/]")

        for i_plr in data.get('blue_team'):
            console.print(f"[bold][white]Nickname: {i_plr.get('nickname')}\n[/]"
                          f"Agent: {i_plr.get('agent')}\n"
                          f"Rank: {i_plr.get('rank')}\n"
                          f"[violet]K/D/A: {i_plr.get('kda')}[/][/]\n")

        console.print("[bold][red]Red Team:[/][/]")

        for i_plr in data.get('red_team'):
            console.print(f"[bold][white]Nickname: {i_plr.get('nickname')}\n[/]"
                          f"Agent: {i_plr.get('agent')}\n"
                          f"Rank: {i_plr.get('rank')}\n"
                          f"[violet]K/D/A: {i_plr.get('kda')}[/][/]\n")

    _continue_working_with_cleaned_screen()


def _create_table_for_match_history(winrate: float, won_games: int, total_games: int) -> None:
    """
    Printing overall stats from player games
    :param winrate: (float) winrate of player
    :param won_games: (int) total games won
    :param total_games: (int) total games played
    """
    table = Table(title='Overall stats', style='bold')
    table.add_column('Winrate %', style='bold')
    table.add_column('Games [green]WON[/]')
    table.add_column('Games [red]LOST[/]')
    table.add_row(f"[bold][magenta]{winrate}%[/]", f"[bold][green]{won_games}[/]",
                  f"[bold][red]{total_games - won_games}[/]")
    console.print(table)


def _get_winrate(total_games_played: int, games_won: int) -> float:
    return round(100 * games_won / total_games_played)


def _continue_working_with_cleaned_screen() -> None:
    """ Asking user for enter key before next interact """
    console.print('[bold]Press enter to [green]continue[/][/]', end=' ')
    input()
    os.system('clear')
    show_user_menu()


def main():
    show_user_menu()


if __name__ == '__main__':
    os.system('clear')
    console.print("[bold]Welcome to [red]VALORANT[/] stats checker![/]")
    main()
