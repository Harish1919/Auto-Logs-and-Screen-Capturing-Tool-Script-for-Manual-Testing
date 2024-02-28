The Auto evidence capturing tool offers the below features.

* Screen recording: The Screen Recorder class in the tool provides functionality for capturing screen activity during the testing. It utilizes the OpenCV library to record the screen at a specified frame rate (through a click of a key), ensuring smooth and high-quality video output.
* Audio capture: The tool captures audio during the recording process, synchronizing it with the screen video. This feature helps in documenting any relevant audio-related issues that may be encountered during bug reproduction. The audio capturing can be turned ON/OFF as per the need.
* Clearing previous system logs: The tool clears previous system logs to provide a clean environment for capturing new logs during bug recording sessions. This ensures accurate and focused bug analysis.
* Logging: The tool captures system logs concurrently with the screen recording. This allows for a comprehensive analysis of bugs by correlating system events with recorded visuals and audio.
* Library Management: The tool checks for the required libraries and installs or upgrades them automatically as necessary. This ensures that the tool operates smoothly and utilizes the latest features and enhancements.
* Auto Output File Management: The tool automatically names the recorded evidences, manages the storage and organises them in one folder per app. Also opens the respective folder for testers when the testing ends. This ensuring easy access and retrieval of recorded evidences.

How to Use:


1. A one time download on the tool is necessary. Version 1 - Link . Version 2 enhanced tool - Link
2. Double click the .EXE FILE file in testing device (Amazon Appstore should be kept open before running this Tool)
3. Wait for it to auto update and auto install if required libraries are not present in the system.  (~2 seconds)
4. Tool will prompt a message for your permission to record with audio / without audio (y/n). Provide Y/N.
5. It will prompt to enter ASIN, input the ASIN and hit enter, This action will do 3 things automatically at once. 
    i) Starts screen recording. ii) Opens the Amazon AppStore to install the app. ii) Minimises the Appstore automatically to window taskbar once the installed app launches. iv) Creates a folder with ASIN name in Downloads.
6. During the recording session, the screen activity is automatically captured along with system logs and video.
7. Press ' [ ' once a bug was identified on an app. This will save last 10 seconds of the recorded buffer clip and names the clip automatically.
8. Press ' ] ' once the full testing completed on the app. This action will do the below things automatically 
    i) Stops the recording. ii) Names the full video and the log. iii) Opens the evidences folder 

