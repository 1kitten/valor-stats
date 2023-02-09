import os
import time
from typing import Optional, Callable, Tuple

import rich
from rich.console import Console
from rich.progress import track

from valorant_api import get_current_mmr_data

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

    console.print("[bold][red]Region[/][/] [italic]choose [red]from[/]: eu, na, kr[/]:", end=' ')
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
    if user_input == '4':
        console.print('[bold]Bye-bye :wave: [/]')
        exit(0)
    elif user_input == '1':
        account_data: Tuple = _ask_user_for_account_data()
        nickname, tagline, region = account_data[0], account_data[1], account_data[2]
        result: Tuple = get_current_mmr_data(user_name=nickname, tagline=tagline, region=region)
        if not result:
            show_user_menu()
        else:
            _format_output(mode='current_mmr_data', data=result)


def _format_output(mode: str, data: tuple):
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

    _continue_working_with_cleaned_screen()


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
