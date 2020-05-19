#-*- coding: utf-8 -*-

import os
import json

import bpy
from ..operators import renderProps


def publishRRS( prodFilePath ):
    print(" -- * publishRRS * --")
    
    cacheFilePath = "c:\\tmp\\"
    
    ### batch render to generate the files
    ### To do: specify the take?

    renderProps.launchRender( 'PROJECT', renderRootFilePath = cacheFilePath )


    ### generate the otio file
    
    # projProp_fps = json.loads( os.environ['UAS_PROJECT_FRAMERATE'] )
    renderProps.exportOtio( renderRootFilePath = cacheFilePath )

    ### copy files to the network
    from distutils.dir_util import copy_tree
    # Wkip to do: exclude .png
    copy_tree ( cacheFilePath, prodFilePath, update = 1 )
    




