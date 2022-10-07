# GPLv3 License
#
# Copyright (C) 2021 Ubisoft
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Utils markers
"""


def sceneContainsCameraBinding(scene):
    for m in scene.timeline_markers:
        if m.camera is not None:
            return True
    return False


def clearMarkersFromCameraBinding(scene):
    for m in scene.timeline_markers:
        if m.camera is not None:
            m.name = m.camera.name
            m.camera = None


def getMarkerbyName(scene, markerName, filter=""):
    for m in scene.timeline_markers:
        if filter in m.name and markerName == m.name:
            return m
    return None


def sortMarkers(markers, filter=""):
    sortedMarkers = [m for m in sorted(markers, key=lambda x: x.frame, reverse=False) if filter in m.name]
    return sortedMarkers


def getFirstMarker(scene, frame, filter=""):
    markers = sortMarkers(scene.timeline_markers, filter)
    return markers[0] if len(markers) else None


def getMarkerBeforeFrame(scene, frame, filter=""):
    markers = sortMarkers(scene.timeline_markers, filter)
    previousMarker = None
    for m in markers:
        if frame > m.frame:
            previousMarker = m
        else:
            return previousMarker
    return previousMarker


def getMarkerAtFrame(scene, frame, filter=""):
    markers = sortMarkers(scene.timeline_markers, filter)
    for m in markers:
        # for m in scene.timeline_markers:
        if frame == m.frame:
            return m
    return None


def getMarkerAfterFrame(scene, frame, filter=""):
    markers = sortMarkers(scene.timeline_markers, filter)
    for m in markers:
        if frame < m.frame:
            return m
    return None


def getLastMarker(scene, frame, filter=""):
    markers = sortMarkers(scene.timeline_markers, filter)
    return markers[len(markers) - 1] if len(markers) else None


def clearMarkersSelection(markers):
    for m in markers:
        m.select = False


def addMarkerAtFrame(scene, frame, name):
    marker = getMarkerAtFrame(scene, frame)
    if marker is not None:
        marker = getMarkerAtFrame(scene, frame)
        marker.name = name
    else:
        if "" == name:
            name = f"F_{scene.frame_current}"
        marker = scene.timeline_markers.new(name, frame=frame)
    return marker


def deleteMarkerAtFrame(scene, frame):
    marker = getMarkerAtFrame(scene, frame)
    if marker is not None:
        scene.timeline_markers.remove(marker)
