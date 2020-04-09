"""Shuffle your team for virtual stand-ups!"""

import argparse
import enum
import json
import random
from typing import Dict, Generator, List, Optional


def _assert_members_xor_subteams(members, subteams):
    """Assert that only one of members or subteams is not None.

    Args:
        members: The contents of the 'members' field.
        subteams: The contents of the 'subteams' field.
    Raises:
        ValueError if either both are neither arguments are None.
    """
    no_members = members is None
    no_subteams = subteams is None
    if no_members == no_subteams:
        if no_members:
            raise ValueError('Either members or subteams are required.')
        raise ValueError(
            'Team cannot contain members and subteams at the same level.')


class ShuffleMethod(enum.Enum):
    NONE = 'none'
    GROUPED = 'grouped'
    UNGROUPED = 'ungrouped'


class Team:
    """A team that will present in some order at a meeting.

    The team may contain a list of members or a list of subteams, not both.
    Subteams are Team objects subject to the same constraints.

    Attributes:
        name: The name of this team.
        members: A list of individuals comprising this team.
        subteams: A list of subteams comprising this team.
    """
    def __init__(self,
                 name: str,
                 members: Optional[List[str]] = None,
                 subteams: Optional[List['Team']] = None) -> None:
        _assert_members_xor_subteams(members, subteams)
        self.name = name
        self.members = members
        self.subteams = subteams

    def get_members(self,
                    shuffle_method: ShuffleMethod = ShuffleMethod.GROUPED
                    ) -> List[str]:
        """Get an ordered list of the members of the team.

        This is intended to be used as the order in which each member will
        present at a meeting (e.g. a standup). Each member of the team or any
        subteam will appear exactly once.

        This method returns the members in an order determined by the
        shuffle_method parameter. The shuffle_method can be:
            none: Return team members in the order declared by the team
                object. Do not randomize the list.
            grouped: Shuffle the members of each subteam, but return the
                each subteam in the order declared by the team object.
            ungrouped: Shuffle all members, disregarding subteam, returning
                any permutation of the members of the team.

        Args:
            shuffle_method: The method by which to shuffle the team members.
        Returns:
            A list of all team members, ordered as specified above.
        """
        teams = [self]
        members = []

        while teams:
            team = teams.pop()
            if team.subteams:
                teams.extend(reversed(team.subteams))
            else:
                if shuffle_method == ShuffleMethod.GROUPED:
                    members.extend(random.sample(team.members,
                                                 len(team.members)))
                else:
                    members.extend(team.members)

        if shuffle_method == ShuffleMethod.UNGROUPED:
            random.shuffle(members)

        return members

    def to_dict(self) -> Dict:
        """Write the team out as a dictionary.

        Returns:
            A dictionary with the contents of this team.
        """
        team_dict = {'name': self.name}
        if self.members is None:
            team_dict['subteams'] = [
                subteam.to_dict() for subteam in self.subteams]
        else:
            team_dict['members'] = self.members
        return team_dict


def build_team_from_dict(team_dict: Dict) -> Team:
    """Build a team object based on the contents of a dictionary.

    In the case of subteams, this function will recurse down the dictionary.
    The same constraints on team contents apply here as in the Team
    constructor.

    Args;
        team_dict: A dictionary containing the team structure.
    Returns:
        A Team object.
    """
    _assert_members_xor_subteams(team_dict.get('members'),
                                 team_dict.get('subteams'))
    if 'members' in team_dict:
        return Team(team_dict['name'], members=team_dict['members'])
    return Team(team_dict['name'],
                subteams=[build_team_from_dict(subteam)
                          for subteam in team_dict['subteams']])


def build_team_from_file(filename: str) -> Team:
    """Build a team object based on the contents of a JSON file.

    Args:
        filename: A JSON file containing the team structure.
    Returns:
        A Team object.
    """
    with open(filename) as json_file:
        team_dict = json.load(json_file)
    return build_team_from_dict(team_dict)


def get_answers(limit: int = -1,
                prompt: str = '') -> Generator[str, None, None]:
    """Get answers from input, stopping when an empty input is given.

    Args:
        limit: The maximum number of answers to accept. The default value of
            -1 indicates an indefinite number of answers will be accepted.
        prompt: The prompt when accepting an answer. The default value is the
            empty string.
    Returns:
        A generator which yields the answers until exhausted.
    """
    count = 0
    answer = 'init'
    while (limit < 0 or count < limit) and answer:
        answer = input(prompt)
        count += 1
        if answer:
            yield answer


def prompt_for_team(name: Optional[str] = None) -> Dict:
    """Prompt user to construct a team.

    Args:
        name: The name of the team or subteam. Will prompt for a name if none
            is provided.
    Returns:
        A dictionary representing the team.
    """
    team_dict = {'name': name or input('Team name? ')}
    has_subteams = input('Will there be subteams? Y/N: ')
    if has_subteams.lower().startswith('y'):
        team_dict['subteams'] = [prompt_for_team(name) for name in get_answers(
            prompt='Subteam name? ')]
    else:
        team_dict['members'] = [name for name in get_answers(
            prompt='Team member name: ')]
    return team_dict


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--create', action='store_true',
                        help='Create a team interactively via the command '
                             'line')
    parser.add_argument('--filename',
                        help='Path to JSON file containing team members.')
    parser.add_argument('--shuffle',
                        choices=[c.value for c in ShuffleMethod],
                        default='ungrouped',
                        help='Whether to shuffle subteams by group, shuffle '
                             'the whole list, or return list in order.')

    args = parser.parse_args()

    if not args.create and not args.filename:
        raise RuntimeError('No team file provided and create not specified.')

    if args.create:
        team_dict = prompt_for_team()
        if args.filename:
            with open(args.filename, 'w') as json_file:
                json.dump(team_dict, json_file)
        team = build_team_from_dict(team_dict)
    else:
        team = build_team_from_file(args.filename)

    print('\n'.join(team.get_members(ShuffleMethod(args.shuffle))))


if __name__ == '__main__':
    main()
