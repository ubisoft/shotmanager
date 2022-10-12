


What happens during...
----------------------

Note: Separators in file names can be different in practice according to the settings or Project settings


A Take rendering:
=================

    - if Stamp Info is activated:

        - for each enabled shot of the current take:
            - the shot is rendered as PNG file in its own temp directory named:
                <take name>\<shot name>_intermediate\<shot name>_<frame>.png
            - the Stamp Info frame files are rendered in the same temp directory:
                <take name>\<shot name>_intermediate\_tmp_StampInfo_<shot name>_<frame>.png
            - currently a wav file is also rendered

            - in the VSE of a temp scene named Tmp_VSE_RenderScene<shot name> those 3 renderings are composited and rendered as a .mp4 file in:
                <take name>\<sequence name>_<shot name>.mp4
              
              This temp scene is then deleted


        - for the sequence:
            - in the VSE of a temp scene named VSE_SequenceRenderScene:
                - the video part of the .mp4 of each shot is added to the edit
                - the sound part of the .mp4 of each shot is added to the track above
                - a video is rendered in:
                    <take name>\<sequence name>_<take name>.mp4

    - if Stamp Info is NOT activated:



A Playblast rendering:
======================

    **Playblast mode is NOT related to the use of Project Settings**

    - if Stamp Info is activated:
        - each enabled shot of the current take is rendered as PNG file in its own temp directory
        - for each enabled shot the SI files are rendered in the directory of each shot

        - each shot is rendered as a sequence of images, with the file format specified in the prefs for playblast (playblastImagesOutputFormat), in jpg by default
        the seq ed is called on the basis of the rendered images sequences
        - **Note that at the moment the playblast overrides the content of the rendering**

    - if Stamp Info is NOT activated:
        - 

