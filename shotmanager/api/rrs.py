from shotmanager.scripts.rrs import publish_rrs


def initialize_for_rrs(override_existing=True, verbose=False):
    publish_rrs.initializeForRRS(override_existing, verbose=verbose)


def publishRRS(prodFilePath, take_index=-1, verbose=False):
    """ Return a dictionary with the rendered and the failed file paths
        filesDict = {"rendered_files": newMediaFiles, "failed_files": failedFiles}
    """
    return publish_rrs.publishRRS(prodFilePath, takeIndex=take_index, verbose=verbose)
