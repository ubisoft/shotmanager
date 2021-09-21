.. _general-philosophy:

--- General philosophy -- READ ME ---
=====================================

**Before starting to use Shot Manager it is very important to understand what this add-on is about and
what you will be able to achieve with it.**

Basically it is based around **2 very simple concepts**. Many tools and features have been added around
them to push their logic to something incredibly powerful for storytelling and animation though,
which can make Shot Manager appear complex.


1 - Making the edit in the 3D scene
-----------------------------------

**In order to let the director experiment and concretize his vision in a short amount of time it is crucial to 
iterate fast in the way an action is edited. And is there a better way to so so than directly in the 3D scene?**

So the key idea lies in the analogy with shooting a continuous live action from several real cameras:

    - In a Blender scene we create an action, usualy corresponding to what would be a sequence in terms of narration,
      this with a plausible timing;
    - Next we introduce several cameras and we define from the tool when the cameras are recording and in which order they
      appear in the edit;
    - Then by playing the edit and iterating on the tweaks on the action, the record timings and the order of appartition
      of the point of views we polish it and finalize the way we want the whole sequence to appear on the scene.


Notion of "Shot"
****************

A [Shot]_ is the basic entity manipulated by the Shot Manager user interface. As for a live footage it is made of a
point of view, thanks to a camera, and a "record duration", defined by a start time and an end time.


Notion of "Take"
****************

A [Take]_ is an ordered list of shots. Basicaly **a take is an edit** where shots are played one after the other, in the order
set in the take and independently from the time at which they start in the time of the 3D scene.

In practice - or in a production context - a take would generaly refert to what is commonly called a sequence, that's to say
a small edit of shots that are tied together in the narration.


2 - Playing the edit in real-time
---------------------------------

To view this edit in real-time we introduced a new play mode. When this mode is activated doing a play
in the viewport will play the scene animation from shot to shot, switching the point of view from one
camera to another according to the one associated to the current shot.

With camera binding the time is played linearly, so the point of view simply changes from one specified
camera to another.

**This new play mode goes far beyond that since it allows time jumps (called ellipses) and jumps back into
time, to play the scene action again from another camera. And that's the essence of Shot Managaer!**


.. UX phitlosophy: simple, consistent, predictible
