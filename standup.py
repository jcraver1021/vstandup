"""Shuffle your team for virtual stand-ups!

Team should be stored as a .json file with the following format:
{
  "team": [
    <list of non-managers>
  ],
  "managers": [
    <list of managers>
  ]
}
"""

import argparse
import enum
import json
import random


class ManagerSettings(enum.Enum):
    FIRST = 'first'
    LAST = 'last'
    THROUGHOUT = 'throughout'


def shuffle_team(filename, manager_setting=ManagerSettings.THROUGHOUT):
    """Shuffle the team members found in this file.

    Args:
        filename: Path to JSON file containing the team.
            Exclusively looks at "team" and "managers" keys, expecting a list
            of strings (team member names).
        manager_setting: Where the managers should go during the ordering.
            Options are:
                "first": Managers go first.
                "last": Managers go last.
                "throughout": Managers are lumped in with everyone else.
            "throughout" is the default behavior.
    Returns:
        A list representing the ordering of the team.
    """
    with open(filename) as f:
        team = json.load(f)

    if manager_setting == ManagerSettings.FIRST:
        sources = [team['managers'], team['team']]
    elif manager_setting == ManagerSettings.LAST:
        sources = [team['team'], team['managers']]
    else:
        sources = [team['team'] + team['managers']]

    standup_order = []
    for source in sources:
        standup_order.extend(random.sample(source, len(source)))

    return standup_order


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('filename',
                        help='Path to JSON file containing team members.')
    parser.add_argument('--managers',
                        choices=[c.value for c in ManagerSettings],
                        default='throughout',
                        help='Where managers should go in the ordering.')

    args = parser.parse_args()

    print('\n'.join(shuffle_team(args.filename,
                                 ManagerSettings(args.managers))))


if __name__ == '__main__':
    main()
