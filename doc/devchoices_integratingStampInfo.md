# Dev Choices: Integrating Stamp Info

[Ubisoft Stamp Info](https://github.com/ubisoft/stampinfo) is another add-on developed by our team for the production needs.
It allows the writing of metadata and various other scene or sequence information
onto the output images.

While designing it we though it could be interesting to be able to use it in some contexts
where Shot Manager is not required.

Now, arriving at Shot Manager v 2.0, it appears that installing another add-on in addition
to this one, is often complex for the user: the reason and purpose for this is often not
well understood, the process of installing, especially in administrator mode, is laborious.

So the idea is now to have Stamp Info integrated into Shot Manager so that the user just
have one add-on to install or to update. The question is: How?


## Separated add-on Vs integrated module

Back to the initial decision, what were the pros and cons we saw for a separated add-on when it comes to
code and functionalities that are not directly related to the main add-on?

### Integrated module

#### Benefits:
- Easy to share, install, track and update
- Shared code or libraries are easy to handle since they are part of the same package

#### Drawbacks:
- The code of the main add-on becomes more complex and heavier due to the amount of files and dependencies
- When just the side feature is required the user has to go through the whole add-on, which may be overkill


### Separated add-on

#### Benefits:
- Can be used as a standalone tool
- Easier to maintain and to improve

#### Drawbacks:
- More documentation, especially regarding the installation
- Required additional installation steps when this add-on is used as part of the main add-on (Shot Manager in
our case)


## How to integrate Stamp Info back?

In order to simplify the installation of Stamp Info, in other words to have it installed or updated
at the same time than Shot Manager, we have 2 possible approaches:
- either keep it as an add-on and just install its package during the installation of Shot Manager,
- or take the code out of Stamp Info and make it a module

What is the amount of work for each approach?

### Keeping Stamp Info as an add-on

#### Work
- Take StampInfo.zip and put it into Shot Manager package
- Call the add-on installation instructions when Shot Manager is being installed

#### Pros
- No change in the current code of Shot Manager

#### Cons
- Be sure to remove and reinstall Stamp Info correctly
- Increase of the weight of Shot Manager


### Integrating Stamp Info inside Shot Manager add-on

#### Work
- Refactor how Stamp Info properties instance is get
- Recreate the set of preference properties inside Stamp Info, with possible renaming to 
make things clean
- Inform the user in the documentation that Stamp Info add-on is not required anymore

#### Pros
- One single add-on to maintain and deploy

#### Cons
- Many changes required in Shot Manager (to get the Stamp Info properties instance, to have
a dedicated set of preferences...)


## Adopted approach

In terms of development times and refactors, maintenance and perspectives for future changes we will keep
the add-on structure of Stamp Info and integrate it into the package of Shot Manager. This way we can
still do a more in-depth integration later on or even step back.
Beside, by integrating the add-on directly inside Shot Manager (and not downloading it) we allow Shot Manager
to be installed off-line (being in Administrator mode is still required though).



