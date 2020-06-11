import wx.adv
import wx

import requests
import json
import sched
import time
from _thread import start_new_thread
from config import key

TRAY_TOOLTIP = 'HueTray'
TRAY_ICON = 'on.png'
TRAY_ICON2 = 'off.png'

ip = requests.get("https://discovery.meethue.com/").json()[0]["internalipaddress"]

def create_menu_item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.Append(item)
    return item


class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, frame):
        self.frame = frame
        super(TaskBarIcon, self).__init__()
        self.set_icon(TRAY_ICON)
        s = sched.scheduler(time.time, time.sleep)
        def do_something(sc): 
            self.state = self.get_state()
            s.enter(5, 1, do_something, (sc,))
        s.enter(5, 1, do_something, (s,))
        start_new_thread(s.run, ())
        self.state = self.get_state()
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)

    def get_state(self):
        r = requests.get("http://{}/api/{}/{}".format(ip, key, "lights/1"))
        parsed = json.loads(r.text)
        if parsed["state"]["on"]:
            self.set_icon(TRAY_ICON)
        else:
            self.set_icon(TRAY_ICON2)
        return parsed["state"]["on"]

    def CreatePopupMenu(self):
        menu = wx.Menu()
        create_menu_item(menu, 'Exit', self.on_exit)
        return menu

    def set_icon(self, path):
        icon = wx.Icon(path)
        self.SetIcon(icon, TRAY_TOOLTIP)

    def on_left_down(self, event):
        self.state = self.get_state()
        if not self.state:
            self.set_icon(TRAY_ICON)
        else:
            self.set_icon(TRAY_ICON2)
        requests.put("http://{}/api/{}/{}".format(ip, key, "lights/1/state"), json.dumps({"on": not self.state}))

    def on_exit(self, event):
        wx.CallAfter(self.Destroy)
        self.frame.Close()

class App(wx.App):
    def OnInit(self):
        frame=wx.Frame(None)
        self.SetTopWindow(frame)
        TaskBarIcon(frame)
        return True

def main():
    app = App(False)
    app.MainLoop()


if __name__ == '__main__':
    main()