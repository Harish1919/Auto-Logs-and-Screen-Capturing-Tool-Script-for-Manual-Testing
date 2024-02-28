import os
import sys
import cv2
import wave
import time
import pyaudio
import datetime
import keyboard
import pyautogui
import importlib
import subprocess
import numpy as np
import pygetwindow
from moviepy.editor import VideoFileClip, AudioFileClip


class Constants:
    requiredPackages = ['pip', 'opencv-python', 'opencv-python-headless', 'numpy', 'pyaudio', 'keyboard', 'pyautogui','moviepy']
    pythonInstallCommand = ['winget', 'install', 'Python']
    pythonVersionCheck = ['python', '--version']
    pythonInstallMessage = 'Python is already installed'
    pythonUpgradeMessage = 'Python is not installed. Installing Python using winget...'
    pythonUpdateCommand = ['winget', 'upgrade', 'Python']
    pipUpgradeCommand = ['python', '-m', 'pip', 'install', '--upgrade', '--user']
    adbConnectCommand = ['adb', 'connect', '127.0.0.1:58526']
    adbLogsClearCommand = ['adb', '-s', '127.0.0.1:58526', 'logcat', '-c']
    adbLogcatCommand = ['adb', '-s', '127.0.0.1:58526', 'logcat']
    dateAndTimeFormat = 'Time_%H-%M-%S_Date_%Y-%m-%d'
    audioSelection = 'Do you want to record audio? (y/n) and hit ENTER: '
    defaultDeepLink = 'amzn://apps/android?asin='
    inputAppASIN = 'Enter the "LIVE/TEST_ASIN" to download the app and hit "ENTER" for further recording: '
    deepLinkAndroidIntent = ['adb', 'shell', 'am', 'start', '-W', '-a', 'android.intent.action.VIEW', '-d']
    logFileFormat = '.log'
    videoData = 'mp4v'
    waveFileMode = 'wb'
    outputFileFormat = '.mp4'
    inbuiltAudioFormat = '.wav'
    defaultVideoEncoder = 'libx264'
    exitKey = ']'
    audioSelectionKey = 'y'
    bufferVideoKey = '['
    screenShotKey = '='
    introductionMessage = ("\033[94m===== The following would happen once the input 'ASIN' was provided and the 'ENTER' key was pressed: ===== \033[0m\n"
        "-> \033[91m Command Prompt will minimize automatically \033[0m.\n\n"
        "-> \033[91m The video and logs will be auto captured when the command prompt is minimized \033[0m.\n\n"
        "-> \033[91m Hit '=' key to capture screenshots while performing app testing \033[0m.\n\n"
        "-> \033[91m Shortcuts: hit '[' key for failure clips & logs; hit ']' key after completing the app testing \033[0m.\n\n"
        "-> \033[91m After hitting ']' key the folder where captured logs and videos will open automatically \033[0m.\n")


class PackageManager:
    def __init__(self):
        self.libraries = Constants.requiredPackages

    def runSubprocess(self, args, stdout=None, stderr=None):
        try:
            subprocess.run(args, check=True, stdout=stdout, stderr=stderr)
        except (subprocess.CalledProcessError, OSError):
            pass
        if sys.stdin.isatty():
            return

    def checkPythonInstalled(self):
        try:
            output = subprocess.check_output(Constants.pythonVersionCheck, stderr=subprocess.STDOUT, text=True)
            print(output.strip())
            return True
        except subprocess.CalledProcessError:
            return False

    def installOrUpgradePython(self):
        message = Constants.pythonInstallMessage if not self.checkPythonInstalled() else Constants.pythonUpgradeMessage
        args = Constants.pythonInstallCommand if not self.checkPythonInstalled() else Constants.pythonUpdateCommand
        self.runSubprocess(args)
        print(f"\033[92m{message}\033[0m" if not self.checkPythonInstalled() else "")

    def checkLibrariesInstalled(self):
        notInstalled = []
        for library in self.libraries:
            try:
                importlib.import_module(library)
            except ImportError:
                notInstalled.append(library)
        return notInstalled

    def upgradeLibraries(self):
        for library in self.checkLibrariesInstalled():
            args = Constants.pipUpgradeCommand + [library]
            with open(os.devnull, 'w') as null_file:
                self.runSubprocess(args, stdout=null_file, stderr=null_file)
            print('\033[92m' + f"Upgraded library: {library}" + '\033[0m')

    def installLibraries(self):
        notInstalled = self.checkLibrariesInstalled()
        if notInstalled:
            print('\033[92m' + "Installing/upgrading libraries..." + '\033[0m')
            args = Constants.pipUpgradeCommand + notInstalled
            with open(os.devnull, 'w') as null_file:
                self.runSubprocess(args, stdout=null_file, stderr=null_file)
            print('\033[92m' + "Successfully installed/upgraded libraries!" + '\033[0m')
        else:
            print("All libraries are already installed")
        if sys.stdin.isatty():
            return

    def clearSystemLogs(self):
        args = Constants.adbConnectCommand
        self.runSubprocess(args)
        args = Constants.adbLogsClearCommand
        self.runSubprocess(args)
        print("Cleared previous logs.")


class ScreenRecorder:
    def __init__(self, outputFps=15, codec=Constants.videoData):
        self.outputFps = outputFps
        self.codec = codec
        self.outputSize = pyautogui.size()
        self.recordBuffer = []
        self.recordBufferSize = self.outputFps * 20
        self.lastKeyPressed = None
        self.logProcess = None
        self.audioBuffer = []
        self.audioBufferSize = self.outputFps * 20
        self.outputVideo = None
        self.bugCounter = None
        self.screenshot_counter = 1


    def generateOutputFilename(self, extension=Constants.outputFileFormat):
        if self.bugCounter is None:
            bug_number = "Full Testing Video"
        else:
            bug_number = f"Bug{self.bugCounter}"
        filename = os.path.join(
            self.outputFolder,
            f"{self.appAsin}_{bug_number}_{datetime.datetime.now().strftime(Constants.dateAndTimeFormat)}{extension}"
        )
        return filename

    def startRecording(self, recordAudio=True):
        if recordAudio:
            channels = 2
            audioSampleRate = 44100
            audioBufferSize = int(audioSampleRate / self.outputFps)
            audio = pyaudio.PyAudio()

            def audioCallback(inData, frameCount, timeInfo, status):
                self.audioBuffer.append(np.frombuffer(inData, dtype=np.int16))
                if len(self.audioBuffer) > self.audioBufferSize:
                    self.audioBuffer = self.audioBuffer[-self.audioBufferSize:]
                return None, pyaudio.paContinue

            def startAudioStream():
                stream = audio.open(
                    format=pyaudio.paInt16,
                    channels=channels,
                    rate=audioSampleRate,
                    input=True,
                    frames_per_buffer=audioBufferSize,
                    stream_callback=audioCallback,
                )
                return audio, stream

            def stopAudioStream(audio, stream):
                stream.stop_stream()
                stream.close()
                audio.terminate()
            audio, audioStream = startAudioStream()
        window = pygetwindow.getActiveWindow()
        window.minimize()
        startTime = time.monotonic()
        self.startLogging()
        fourcc = cv2.VideoWriter_fourcc(*self.codec)
        self.outputVideo = cv2.VideoWriter(self.outputFilename, fourcc, self.outputFps, self.outputSize)

        while True:
            try:
                img = pyautogui.screenshot()
                frame = np.array(img)
                cursorPos = pyautogui.position()
                cv2.circle(frame, tuple(cursorPos), 12, (0, 0, 255), -1)
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                if keyboard.is_pressed(Constants.screenShotKey) and self.lastKeyPressed != Constants.screenShotKey:
                    screenshot_filename = os.path.join(self.outputFolder, f'screenshot_{self.screenshot_counter}.png')
                    cv2.imwrite(screenshot_filename, frame)
                    print(f'Saved screenshot: {screenshot_filename}')
                    self.screenshot_counter += 1
                if keyboard.is_pressed(Constants.screenShotKey):
                    self.lastKeyPressed = Constants.screenShotKey
                else:
                    self.lastKeyPressed = None
                self.outputVideo.write(frame)
                self.recordBuffer.append(frame)
                elapsedTime = time.monotonic() - startTime
                waitTime = 1.0 / self.outputFps - elapsedTime
                if waitTime > 0:
                    time.sleep(waitTime)
                if keyboard.is_pressed(Constants.exitKey) or keyboard.is_pressed(Constants.exitKey):
                    break
                elif (keyboard.is_pressed(Constants.bufferVideoKey) or keyboard.is_pressed(Constants.bufferVideoKey)) and self.lastKeyPressed != Constants.bufferVideoKey:
                    self.save()
                    self.lastKeyPressed = Constants.bufferVideoKey
                elif not keyboard.is_pressed(Constants.bufferVideoKey):
                    self.lastKeyPressed = None

                if len(self.recordBuffer) > self.recordBufferSize:
                    self.recordBuffer = self.recordBuffer[-self.recordBufferSize:]
            except Exception as e:
                print(f"Error while recording: {e}")
                break

        if recordAudio:
            stopAudioStream(audio, audioStream)
        else:
            self.audioBuffer = []
        self.stopLogging()
        print("Recording stopped.")

    def save(self):
        if self.bugCounter is None:
            self.bugCounter = 1
        numFrames = len(self.recordBuffer)
        if numFrames == 0:
            print("No frames recorded yet.")
            return
        elif numFrames < self.recordBufferSize:
            self.recordBufferSize = numFrames
        saveFrames = self.recordBuffer[-self.recordBufferSize:]
        saveFilename = self.generateOutputFilename()
        fourcc = cv2.VideoWriter_fourcc(*self.codec)
        saveVideo = cv2.VideoWriter(saveFilename, fourcc, self.outputFps, self.outputSize)
        for frame in saveFrames:
            saveVideo.write(frame)
        saveVideo.release()

        if self.audioBuffer:
            audioData = np.concatenate(self.audioBuffer)
            audioFilename = self.generateOutputFilename(Constants.inbuiltAudioFormat)
            audioSampleWidth = 2
            audioSampleRate = 44100

            waveFile = wave.open(audioFilename, Constants.waveFileMode)
            waveFile.setnchannels(2)
            waveFile.setsampwidth(audioSampleWidth)
            waveFile.setframerate(audioSampleRate)
            waveFile.writeframes(audioData.tobytes())
            waveFile.close()

            videoClip = VideoFileClip(saveFilename)
            audioClip = AudioFileClip(audioFilename)
            mergedClip = videoClip.set_audio(audioClip)
            mergedFilename = self.generateOutputFilename(Constants.outputFileFormat)
            mergedClip.write_videofile(mergedFilename, codec=Constants.defaultVideoEncoder)
            os.remove(saveFilename)
            os.remove(audioFilename)
            print(f"Video saved as {mergedFilename}")
        else:
            print(f"Video file saved as {saveFilename}")
        self.recordBuffer = []
        self.bugCounter += 1

    def startLogging(self):
        logFilePath = os.path.join(
            self.outputFolder,
            f'{self.appAsin}_logs_{datetime.datetime.now().strftime(Constants.dateAndTimeFormat)}{Constants.logFileFormat}',
        )
        args = Constants.adbConnectCommand
        subprocess.Popen(args)
        try:
            with open(logFilePath, "a") as f:
                adb = Constants.adbLogcatCommand
                self.logProcess = subprocess.Popen(adb, stdout=f)
            print("Started capturing new logs.")
        except FileNotFoundError:
            print("Error: adb command not found. Make sure the Android SDK is installed and adb is in your PATH.")
        except subprocess.CalledProcessError as e:
            print("Error: ", e)

    def stopLogging(self):
        if self.logProcess is not None:
            self.logProcess.kill()

    def record(self):
        try:
            print(Constants.introductionMessage)
            recordAudioInput = input(Constants.audioSelection)
            recordAudio = recordAudioInput.lower() == Constants.audioSelectionKey
            appAsin = input(Constants.inputAppASIN)
            deepLink = f'{Constants.defaultDeepLink}{appAsin}'
            deepLinkArgs = Constants.adbConnectCommand
            subprocess.Popen(deepLinkArgs)
            AndroidIntentArgs = Constants.deepLinkAndroidIntent + [deepLink]
            subprocess.Popen(AndroidIntentArgs)
            self.appAsin = appAsin
            self.outputFolder = os.path.join(os.path.expanduser("~"), "Downloads", f"{self.appAsin}_{datetime.datetime.now().strftime(Constants.dateAndTimeFormat)}")
            os.makedirs(self.outputFolder, exist_ok=True)
            self.outputFilename = self.generateOutputFilename()
            fourcc = cv2.VideoWriter_fourcc(*self.codec)
            self.outputVideo = cv2.VideoWriter(self.outputFilename, fourcc, self.outputFps, self.outputSize)
            self.startRecording(recordAudio=recordAudio)
        except Exception as e:
            print(f"Error while recording: {e}")
        finally:
            if self.outputVideo is not None:
                self.outputVideo.release()

            if os.path.exists(self.outputFilename):
                print(f"Output video file saved as {self.outputFilename}")
            else:
                print("Output video file could not be found.")
            saveLocation = os.path.dirname(self.outputFilename)
            subprocess.Popen(['explorer', saveLocation])


if __name__ == "__main__":
    packageInstallation = PackageManager()
    if not packageInstallation.checkPythonInstalled():
        print("Python is not installed. Installing...")
        packageInstallation.installOrUpgradePython()
    else:
        print("Python is already installed and updated...!")
    packageInstallation.installLibraries()
    packageInstallation.clearSystemLogs()
    recorder = ScreenRecorder()
    recorder.record()
