import subprocess
from subprocess import Popen, PIPE, STDOUT
import tkinter
from threading import Thread
import configparser
import getpass
from tkinter.filedialog import askopenfilename

GUI = tkinter.Tk()
ConfigButtons = []
processlist = []



#Some code from: https://gist.github.com/zed/42324397516310c86288
class rcloneProcess:
    def __init__(self, GUI, *Commands):
        print()
        self.CommandLists = []
        self.CommandLists.append(r"rclone\rclone-v1.37-windows-amd64\rclone.exe")
        for args in Commands:
            self.CommandLists.append(args)
        self.GUI = GUI
        self.process = Popen(self.CommandLists, stdout=PIPE, stderr=STDOUT)
        global processlist
        processlist.append(self.process)
        t = Thread(target=self.reader_thread, args=[]).start()
        self.EndButton = tkinter.Button(GUI, text="Stop subprocess")
        self.EndButton = tkinter.Button(GUI, text="Stop subprocess", command = lambda: self.stop(self.EndButton))
        self.EndButton.grid()
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

    def stop(self,ende):
        self.process.terminate() # tell the subprocess to exit

        # kill subprocess if it hasn't exited after a countdown
        def kill_after(countdown):
            if self.process.poll() is None: # subprocess hasn't exited yet
                countdown -= 1
                if countdown < 0: # do kill
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
    for process in processlist:
        process.terminate()
    GUI.destroy()

def CloseAndStop(app):
    try:
        app.stop
    except:
        pass
    GUI.destroy()

def LoadConfigFromUser(ConFigButtonsFrame, Where=""):
    Columnx = 0
    Rowy = 1
    global ConfigButtons
    User = getpass.getuser()
    for section in ConfigButtons:
        section.destroy()
    ConfigLable = tkinter.Label(ConFigButtonsFrame, text = "Remotes", width = 16)
    ConfigLable.grid()
    ConfigButtons = []
    Config = configparser.ConfigParser()
    if Where == "":
        Config.read("C:\\Users\\" + User +"\\.config\\rclone\\rclone.conf")
    else:
        Config.read(Where)
    for sections in Config.sections():
        ConfigSection = tkinter.Button(ConFigButtonsFrame, width = 16, text = sections)
        if Columnx == 0:
            ConfigSection.grid(column=Columnx, row=Rowy)
            Columnx = 1
        else:
            ConfigSection.grid(column=Columnx, row=Rowy)
            Rowy += 1
            Columnx = 0
        ConfigButtons.append(ConfigSection)

def LoadFile():
    ConfigFile = askopenfilename()
    return ConfigFile

def ButtonsGUI():
    ButtonsFrame = tkinter.Frame(GUI)
    ButtonsFrame.grid()

    MainButtons = tkinter.Frame(ButtonsFrame)
    MainButtons.grid(sticky='w')

    LineCanvas = tkinter.Canvas(ButtonsFrame, height = 1, width = 240)
    LineCanvas.grid()

    ConFigButtonsFrame = tkinter.Frame(GUI)
    ConFigButtonsFrame.grid(sticky='w')

    TestCommand = tkinter.Button(MainButtons, text = 'Test', width = 16,command = lambda: rcloneProcess(MainButtons, *CommandList))
    TestCommand.grid(row=0,column=0)
    CloseButton = tkinter.Button(MainButtons, text = "Close", width = 16, command = lambda: RemoveGUI())
    CloseButton.grid(row=0,column=2)
    LoadConfig = tkinter.Button(MainButtons, text = "Load User Config", width = 16, command = lambda: LoadConfigFromUser(ConFigButtonsFrame))
    LoadConfig.grid()
    LoadCustomConfig = tkinter.Button(MainButtons, text = "Load Custom Config", width = 16, command = lambda: LoadConfigFromUser(ConFigButtonsFrame, LoadFile()))
    LoadCustomConfig.grid()
    LineCanvas.create_line(0,0,250,0,fill='black', width=6)

def MainWindow():
    ButtonsGUI()
    tkinter.mainloop()

MainWindow()
