def get_name(take_instance):
    return take_instance.name


def set_name(take_instance, name):
    """ Set a unique name to the take
    """
    take_instance.name = name


def get_name_path_compliant(take_instance):
    return take_instance.getName_PathCompliant()


def get_shot_list(take_instance, ignore_disabled=False):
    """ Return a filtered copy of the shots associated to this take
    """
    return take_instance.getShotList(ignoreDisabled=ignore_disabled)
