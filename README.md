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

free hand drawing - pointer finger up and all others should be down 

straight line drawing- pointer and middle finger up

rectangle/square drawing- pointer and pinky up all other should be down drag for the size and put all other fingers up to release the brush 

clear canvas - fist

erase parts- thumb up and drag it over the parts you want to erase

move/throw the strokes - pinch and move or pinch and throw it around the canvas


Installation:

Clone the repository:
git clone https://github.com/daniruddha483-hub/AirForge.git
cd AirForge


Install the required libraries:
pip install opencv-python mediapipe numpy


Run the application:
python AirCAD.py

A working webcam is required.

Project Status

The AirForge is still a work in progress. The current version does 2D gesture-based drawing, And i'm planning on improving it more by adding new features.
