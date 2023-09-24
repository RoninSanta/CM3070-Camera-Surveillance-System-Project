# CM3070-Final-Year-Project
Camera Surveillance System
## Object Tracking and Identification using OpenCV and YOLO framework 

## Installation - READ FIRST! ##
### The necessary modules and packages are stored in the requirements.txt ###
Install the text file FIRST!! before running any of the scripts or else it won't work! 
- TYPE py -m pip install -r requirements.txt in your python environment terminal to execute text file
- For MAC USERS use python -m pip install -r requirements.txt

#### The Webcam Script  #######
- It will track any movement from the video footage
- Identify the object that is on screen and display a label
- The script attached will seek permission from camera and identify any object from the footage

#### Dashbaord Script ####
- The Dashboard is the user interface where I control can control the review and edit the slips stored
- Every script run is stored under the 'output_videos' folder, this GUI will list all the files in that folder
- The user can watch the clips, Rewind, Fastforward, and Delete clips at will
- Deleted clips are permanently deleted from the file system as well

#### Surveillance Script ####
- This script will play stored video clips from different scenarios and apply AI algorithm to identify objects
- The objects in the clips will be catergorised and tracked showcasing the capabilities of the OpenCV & YOLO framework
- The objective is to showcase the different scenarios which it works like example:

#### sentGmail script ###
- When a person is detected, it captures a screenshot
- Sends an email alert with the screenshot attached
- It helps to identify house pets i.e cats and dogs
- It works in low light conditiosn like at night

#### Size Issue ####
- The yolov3.weights is currently over 200MB therefore, you might have an issue trying to download it
- However, it is very crucial since it contains the pre-trained model for the classifier
