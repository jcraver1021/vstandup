# vstandup

## Files

* `standup.py`

## Usage

`standup.py [-h] [--create] [--filename FILENAME] [--shuffle {none,grouped,ungrouped}]`

`standup.py` has two operations, which can be combined:
1. Constructing a tree that represents an organization.
2. Shuffling the team members to create a random presentation order.

### Constructing a Team

#### Description of Team Structure

The organization consists of two types of entities that are related in a tree
structure:
* Team (or subteam)
* Member

Teams are a dictionary, containing `name`, a string, and either `members`, a
list of strings (member names), or `subteams`, a list of Team objects. An
individual team object cannot contain both `members` and `subteams`.

The root of the tree must be a Team object.

Teams are written and read from the file system as JSON objects.

```json
{
  "name": "Deep Space 9",
  "subteams": [
    {
      "name": "Federation",
      "subteams": [
        {
          "name": "Red",
          "members": [
            "Benjamin Sisko",
            "Worf"
          ]
        },
        {
          "name": "Yellow",
          "members": [
            "Miles O'Brien"
          ]
        },
        {
          "name": "Blue",
          "members": [
            "Jadzia Dax",
            "Julian Bashir"
          ]
        }
      ]
    },
    {
      "name": "Bajor",
      "members": [
        "Kira Nerys",
        "Odo"
      ]
    }
  ]
}
```

#### Building a Team Using the Tool

Rather than building the JSON file by hand, you can use the `--create` option
to construct one during the program execution. This will prompt you to provide
a team name and state whether the team contains subteams or members.

If the team contains members, not subteams, then you will be prompted to enter
the names of the members of that team. When you are finished, simply enter an
empty name.

If the team contains subteams, then you will be prompted to enter the subteam
name. After this, you will create a subteam in the same way you created the
first team; further subteams will be created in much the same way as the
original. When a subteam is completely defined, you will be prompted to enter
the name of the next subteam; as with team members, simply enter an empty name
to complete this list of subteams.

If `--filename` is specified, the team you created will be saved to that file.
Otherwise, the information will be lost after the team members are listed.

### Shuffling the Team Order

The program will always return the team members in some order, whether the team
is created using the `--create` option or read in from the `--filename`
parameter. The `--shuffle` parameter tells the program which order to return
team members. The following options are available:
* `none`: All team members are returned in the order listed.
* `ungrouped`: All team members are aggregated and the entire list is shuffled.
* `grouped`: Each subteam is returned in order, but the members of each subteam
             are ordered randomly.
