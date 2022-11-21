""" Manages profiles

"""

import json
import argparse
import os

# Keys
PROFILES = 'profiles'
NAME = 'name'
DESCRIPTION = 'description'
BANDWIDTH = 'bandwidth'
TOPOLOGY = 'topology'


def get_profiles(file_name):
    """ Read the profile.json file and loads profiles as objects
    Args:
        file_name (string): pathname of the profile.json file
    """
    if len(profiles) == 0:
        with (open(file_name)) as topo_file:
            doc = json.load(topo_file)
            for profile in doc[PROFILES]:
                profiles[profile[NAME]] = profile
            return profiles
    else:
        return profiles


def get_profile(profile_name):
    """ Returns the profile object providing a profile name
    Args:
        profile_name (string): name of the profile
    Returns:
        dict: key/values pairs of attributes of the profile.
    """
    if profile_name in profiles:
        return profiles[profile_name]
    return None


def display_profile(profile):
    """ Prints the provided profile
    Args:
        profile (dict): profile
    """
    print (profile[NAME])
    print ("\t", profile[DESCRIPTION])
    print ("\t Bandwidth: ", profile[BANDWIDTH])


def do_cli():
    """ Executes the CLI
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("--show", nargs=1, help="display profile.")
    parser.add_argument("--list", nargs='*', help="Displays all profiles.")

    args = parser.parse_args()

    if args.show is not None:
        profile_name = args.resolve[0]
        if profile_name in profiles:
            display_profile(profiles[profile_name])
        else:
            print ("unknown profile", profile_name)


def init():
    """ Intiializes the module
    """
    global profiles
    profiles = {}
    this_dir = os.path.split(__file__)[0]
    profile_file_path = os.path.join(this_dir, "profiles.json")
    profiles = get_profiles(profile_file_path)

if __name__ == "__main__":
    init()

do_cli()
