from shotmanager.scripts.rrs import publish_rrs


def initialize_for_rrs(override_existing=True, verbose=False):
    publish_rrs.initializeForRRS(override_existing, verbose=verbose)


def publishRRS(prodFilePath, take_index=-1, verbose=False, use_cache=False, fileListOnly=False):
    """ Return a dictionary with the rendered and the failed file paths
        The dictionary have the following entries: rendered_files, failed_files, otio_file
    """
    return publish_rrs.publishRRS(
        prodFilePath, takeIndex=take_index, verbose=verbose, useCache=use_cache, fileListOnly=fileListOnly
    )
