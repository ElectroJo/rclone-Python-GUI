import subprocess
from subprocess import Popen, PIPE, STDOUT
import tkinter
from threading import Thread
import configparser
import getpass
from tkinter.filedialog import askopenfilename

GUI = tkinter.Tk()
GUI.minsize(width=200, height=200)
ConfigButtons = []



#Some code from: https://gist.github.com/zed/42324397516310c86288
class rcloneProcess:
    def __init__(self, GUI):
        self.GUI = GUI
        self.process = Popen([r"rclone\rclone-v1.37-windows-amd64\rclone.exe", "ls","secretC:"], stdout=PIPE, stderr=STDOUT)
        t = Thread(target=self.reader_thread, args=[]).start()
        self.EndButton = tkinter.Button(GUI, text="Stop subprocess")
        self.EndButton = tkinter.Button(GUI, text="Stop subprocess", command = lambda: self.stop(self.EndButton))
        self.EndButton.pack()
        self.ConsoleGUIWin = tkinter.Toplevel()
        self.ConsoleGUIWin.title("Console")
        self.ConsoleFrame = tkinter.Frame(self.ConsoleGUIWin, width=900, height=500)
        self.ConsoleFrame.pack(fill="both", expand=True)
        self.ConsoleFrame.grid_propagate(False)
        self.Console = tkinter.Text(self.ConsoleFrame, width=110, height=31)
        self.Console.grid(row=1)
        self.ScrollBar = tkinter.Scrollbar(self.ConsoleFrame, command=self.Console.yview)
        self.ScrollBar.grid(row=1, column=1, sticky='ns')

    def reader_thread(self):
        for line in iter(self.process.stdout.readline, b''):
            try:
                self.Console.insert(tkinter.END, line)
            except:
                pass
            try:
                self.Console.see(tkinter.END)
            except:
                pass
        print('done reading')

    def stop(self,ende):
        print('stoping')
        self.process.terminate() # tell the subprocess to exit

        # kill subprocess if it hasn't exited after a countdown
        def kill_after(countdown):
            if self.process.poll() is None: # subprocess hasn't exited yet
                countdown -= 1
                if countdown < 0: # do kill
                    print('killing')
                    self.process.kill() # more likely to kill on *nix
                else:
                    self.GUI.after(1000, kill_after, countdown)
                    return # continue countdown in a second
            # clean up
            self.process.stdout.close()  # close fd
            self.process.wait()
            ende.destroy()       # wait for the subprocess' exit
        kill_after(countdown=5)


def RemoveGUI():
    GUI.destroy()


def Startapp():
    app = rcloneProcess(GUI)
    GUI.protocol("WM_DELETE_WINDOW", lambda app=app:CloseAndStop(app)) # exit subprocess if GUI is closed

def CloseAndStop(app):
    app.stop
    GUI.destroy()

def LoadConfigFromUser(ButtonsFrame, Where=""):
    global ConfigButtons
    User = getpass.getuser()
    for section in ConfigButtons:
        section.destroy()
    ConfigButtons = []
    Config = configparser.ConfigParser()
    if Where == "":
        Config.read("C:\\Users\\" + User +"\\.config\\rclone\\rclone.conf")
    else:
        Config.read(Where)
    for sections in Config.sections():
        ConfigSection = tkinter.Button(ButtonsFrame, text = sections)
        ConfigSection.grid()
        ConfigButtons.append(ConfigSection)

def LoadFile():
    ConfigFile = askopenfilename()
    return ConfigFile

def ButtonsGUI():
    ButtonsFrame = tkinter.Frame(GUI, width=6, height=6)
    ButtonsFrame.pack(fill="both", expand=True)
    ButtonsFrame.grid_propagate(False)
    TestCommand = tkinter.Button(ButtonsFrame, text = 'Test',command = lambda: Startapp())
    TestCommand.grid(row=0,column=0)
    CloseButton = tkinter.Button(ButtonsFrame, text = "Close", command = lambda: RemoveGUI())
    CloseButton.grid(row=0,column=2)
    LoadConfig = tkinter.Button(ButtonsFrame, text = "Load User Config", command = lambda: LoadConfigFromUser(ButtonsFrame))
    LoadConfig.grid()
    LoadCustomConfig = tkinter.Button(ButtonsFrame, text = "Load Custom Config", command = lambda: LoadConfigFromUser(ButtonsFrame, LoadFile()))
    LoadCustomConfig.grid()

def MainWindow():
    ButtonsGUI()
    tkinter.mainloop()

MainWindow()
