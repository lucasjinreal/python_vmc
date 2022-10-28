#!/usr/bin/env python3

import wx
from vmc import Assistant as VMCAssistant, Bone, Position, Quaternion

class Window(wx.App):
    def __init__(self, vmc: VMCAssistant, 
                 model_root: list[Position, Quaternion],
                 model_t_pose: list[Bone, Position, Quaternion]) -> None:
        self.vmc = vmc
        self.model_root = model_root
        self.model_t_pose = model_t_pose
        super().__init__()

    def OnInit(self) -> bool:
        self.frame = self.Frame(
            vmc = self.vmc,
            parent = None, 
            title = 'VMC Assistant Demo', 
            size = wx.Size(400, 300)
        )
        self.frame.Show(True)
        return True
  
    class Frame(wx.Frame):
        def __init__(self, vmc: VMCAssistant, 
                     parent: wx.App, title: str, size: wx.Size) -> None:
            super().__init__(
                parent, 
                title = title, 
                size = size
            )
            self.panel = self.Panel(self, vmc)

        class Panel(wx.Panel):
                     
            def __init__(self, parent: wx.Frame, vmc: VMCAssistant) -> None:
                self.vmc = vmc
                super().__init__(parent)
                # Controls
                self.test_caption = wx.StaticText(
                    self, label = 'Test', 
                    style = wx.ALIGN_LEFT
                )
                self.test_slider = wx.Slider(
                    self, 
                    value = 0, 
                    minValue = -180, 
                    maxValue = 180, 
                    style = wx.SL_HORIZONTAL | wx.SL_LABELS
                )
                self.Bind(wx.EVT_SLIDER, self.change_test)
                # Log
                self.log = wx.TextCtrl(
                    self, 
                    style = wx.TE_MULTILINE | wx.TE_READONLY
                )
                # Layout
                self.layout = wx.BoxSizer(wx.VERTICAL)
                self.layout.AddMany([
                    (self.test_caption, 0, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5),
                    (self.test_slider, 0, wx.EXPAND | wx.ALL, 5),
                    (self.log, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
                ])
                self.SetSizer(self.layout)
                self.Center()

            def change_test(self, event: wx.Event) -> None:
                value = float(self.test_slider.GetValue())
                quat = Quaternion.from_euler(0.0, 0.0, value, 12)
                self.vmc.send_bones_transform(
                    [
                        [
                            Bone("LeftUpperLeg"),
                            Position(0.0, 0.0, 0.0),
                            quat
                        ]
                    ]
                )
                self.vmc.send_available_states(1)
                self.vmc.send_relative_time()
                self.log.AppendText(
                    str(quat) + "\r\n"
                )
