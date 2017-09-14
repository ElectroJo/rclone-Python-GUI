import subprocess
from subprocess import Popen, PIPE, STDOUT
import tkinter
from threading import Thread
import configparser

GUI = tkinter.Tk()
GUI.minsize(width=200, height=200)
ConsoleGUIWin = tkinter.Toplevel()
ConsoleGUIWin.title("Console")
ConsoleGUIWin.deiconify()


#Some code from: https://gist.github.com/zed/42324397516310c86288
class rcloneProcess:
    def __init__(self, GUI, Console):
        self.GUI = GUI
        self.Console = Console
        self.process = Popen([r"rclone\rclone-v1.37-windows-amd64\rclone.exe", "ls","secretC:"], stdout=PIPE, stderr=STDOUT)
        t = Thread(target=self.reader_thread, args=[]).start()
        self.EndButton = tkinter.Button(GUI, text="Stop subprocess")
        self.EndButton = tkinter.Button(GUI, text="Stop subprocess", command = lambda: self.stop(self.EndButton))
        self.EndButton.pack()

    def reader_thread(self):
        for line in iter(self.process.stdout.readline, b''):
            Console.insert(tkinter.END, line)
            Console.see(tkinter.END)
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

def testthis():
    for path in execute([r"rclone\rclone-v1.37-windows-amd64\rclone.exe", "ls","secretC:"]):
        print(path)
        Console.insert(tkinter.END, path)

def RemoveGUI():
    GUI.destroy()

def ConsoleGUI():
    ConsoleFrame = tkinter.Frame(ConsoleGUIWin, width=900, height=500)
    ConsoleFrame.pack(fill="both", expand=True)
    ConsoleFrame.grid_propagate(False)
    Console = tkinter.Text(ConsoleFrame, width=110, height=31)
    Console.grid(row=1)
    ScrollBar = tkinter.Scrollbar(ConsoleFrame, command=Console.yview)
    ScrollBar.grid(row=1, column=1, sticky='ns')
    global Console

def Startapp():
    app = rcloneProcess(GUI, Console)
    GUI.protocol("WM_DELETE_WINDOW", app.stop) # exit subprocess if GUI is closed

def ButtonsGUI():
    ButtonsFrame = tkinter.Frame(GUI, width=6, height=6)
    ButtonsFrame.pack(fill="both", expand=True)
    ButtonsFrame.grid_propagate(False)
    TestCommand = tkinter.Button(ButtonsFrame, text = 'Test',command = lambda: Startapp())
    TestCommand.grid(row=0,column=0)
    CloseButton = tkinter.Button(ButtonsFrame, text = "Close", command = lambda: RemoveGUI())
    CloseButton.grid(row=0,column=2)

def MainWindow():
    ButtonsGUI()
    ConsoleGUI()
    tkinter.mainloop()
MainWindow()
