from shotmanager.scripts.rrs import publish_rrs


def initialize_for_rrs(override_existing=True, verbose=False):
    publish_rrs.initializeForRRS(override_existing, verbose=verbose)


def publishRRS(prodFilePath, take_index=-1, verbose=False, use_cache=False, fileListOnly=False):
    """ Return a dictionary with the rendered and the failed file paths
        The dictionary have the following entries:
            - rendered_files_in_cache: rendered files when cache is used
            - failed_files_in_cache: failed files when cache is used
            - rendered_files: rendered files (either from direct rendering or from copy from cache)
            - failed_files: failed files (either from direct rendering or from copy from cache)
            - edl_files: edl files
            - other_files: json dumped file list
    """
    return publish_rrs.publishRRS(
        prodFilePath, takeIndex=take_index, verbose=verbose, useCache=use_cache, fileListOnly=fileListOnly
    )
