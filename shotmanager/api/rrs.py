from shotmanager.scripts.rrs import publish_rrs


def initialize_for_rrs(override_existing=True, verbose=False):
    publish_rrs.initializeForRRS(override_existing, verbose=verbose)


def publishRRS(prodFilePath, take_index=-1, verbose=False):
    publish_rrs.publishRRS(prodFilePath, takeIndex=take_index, verbose=verbose)
