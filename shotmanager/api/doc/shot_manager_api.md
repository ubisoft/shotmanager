# Shot Manager Python API

In order to communicate with its data from another script, Shot Manager provides its own API.
It is located here: [https://github.com/ubisoft/shotmanager/tree/main/shotmanager/api/doc/shot_manager_api.md](https://github.com/ubisoft/shotmanager/tree/main/shotmanager/api/doc/shot_manager_api.md).

The use of the API is highly recommended in such cases because the role of the functions is easier to understand - only the most important ones
are exposed - and because you can rely on the stability of those functions. Indeed their behavior will not change in future releases, whereas
the ones in the code may be modified during refactoring operations.


## Main concepts

### Shot Manager

The **Shot Manager** is the main property class. Basically it contains a set of takes (CollectionProperty) and each take has a set of shots (CollectionProperty).

The functions available in the API are spread in several files, in a logical and object-oriented approach, according to the manipulated entities. They are not classes though, just C-like functions.

In Shot Manager the UI and functionnal part are - as much as possible - separated. 2 properties are a bit inbetween though: the current shot and the selected shot (they are indices, not pointers to the shot instances). The current shot is more than a UI information since the concerned shot has a special behavior (its camera is the one used by the scene for example). The selected shot refers to the highlighted item in the shots list (which is also the take). Many actions are based on it so it has also to be considered as a functional information. In spite of that the add-on can be completely manipulated without the use of the interface, and takes that are not set as the current one can be changed in exaclty the same way as the current one.


## Examples

Several step-by-step samples and use-case coverages are provided in the "api_code_samples" folder.
