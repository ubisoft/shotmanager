

UAS Shot Manager
-------------------------------------------------------------

# Purpose:
--------

	Manages the shots of a Blender scene. It offers a realtime editing directly on
	the data of a 3D scene.
	Shot Manager is very versatile and can be useful in many cases.
	The main usecase is this: A continuous action is set in a scene, then some cameras
	are put at the appropriate places in the world and a shot is created for each one of
	them in order to record the right segment of time.
	This is very convenient for previz and 3D layout.


# Important points:
-------------------



3D:
	- Camera markers are NOT compatible with Shot Manager. They prevent the shot play to work correctlt.
	Shot Manager will then not allow their use by freezint its user interface.

	- Negative frames are not supported. When starting the action prepare a sate time zone between 0 and the
	start of the first shot (including the lenght of the handles).

	- The end frame of a shot is included in the shot and rendered.
	The duration of a shot (ie the total number of frames) is then equal to end - start + 1

3D Edit:
	- By default first frame of the edit is 0, as most edititng applications, but this is a preference and it can
	be set to 1, or event to an arbitrary (positive) number (so that the sequence and exported xml can be added
	at the end of another one)

Media:
	- First frame of the exported videos gets the number 0 (and not 1)
	- Hence the last frame of a media is equal to duration - 1
	- Rendered media and exports are done in the specified Root directory. Path relative to the current project are
	supported.



Naming:
	- Shot: Association of a period of time in the 3D scene, given by a start and a end, and a point of view, given
	by the camera held by the shot.


	- Takes: A take is a given set of shots
# Features:
---------

# Retime
---------

## Insert Time:
	Insert a range of time between the frame Start and the frame Start + 1.
	- From (or Start): Frame at which the time is inserted. wkip frame inserted there?
	Keyframes at this frame are not affected by the time change
	- To (or End): Defines the frame at which the frame Start + 1 will be after the insertion time.
	Keyframes at thisframe Start + 1 and above will then be added to an offset given by Duration (End - Start).
	Hence End - Start is the duration of the time insered right after the frame Start.

## Remove Time:
	Remove the time included between Start frame and End Frame.


[History](./CHANGELOG.md)
