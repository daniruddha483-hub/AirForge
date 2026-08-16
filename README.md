AirForge

AirForge is a Python-based touchless CAD sketching application that uses hand gestures to create and manipulate basic geometric designs through a webcam.

Overview:

The project uses computer webcam and hand tracking to turn hand movements into CAD-style drawing actions. The main goal is to experiment with a more natural way of interacting with geometric design software without relying entirely on a mouse and keyboard.

Features:

* Real-time hand tracking
* Gesture-based drawing
* Geometric shape creation
* You can move objects
* Gesture-based erasing
* CAD-style grid

Technologies

I Used :
* Python
* OpenCV
* MediaPipe
* NumPy

How It Works:

The webcam in the laptop/PC captures the user's hand movements and MediaPipe detects the hand landmark points. AirForge processes these landmarks to identify simple gestures (ex:pointer up or index and poiter up gestures) and converts them into drawing or editing actions on the black workspace.

How to use:

pointer up - free hand drawing 

pointer + middle finger - straight line drawing

pointer + pinky - draw rectangle/square

thumb - erase parts

pinch - to move or throw it around

fist - clear cavnas

Project Status

The AirForge is still a work in progress. The current version does 2D gesture-based drawing, And i'm planning on improving it more by adding new features.
