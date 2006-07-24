#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-
# generated by wxGlade 0.4 on Thu Dec 15 22:45:56 2005

import wx

class ValSlider(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: ValSlider.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.label = wx.StaticText(self, -1, "name:", style=wx.ALIGN_RIGHT)
        self.text = wx.TextCtrl(self, -1, "0")
        self.slider_1 = wx.Slider(self, -1, 0, 0, 10000)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_TEXT_ENTER, self.do_text, self.text)
        self.Bind(wx.EVT_COMMAND_SCROLL, self.do_scroll, self.slider_1)
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: ValSlider.__set_properties
        self.SetTitle("frame_1")
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: ValSlider.__do_layout
        sizer = wx.FlexGridSizer(1, 3, 0, 0)
        sizer.Add(self.label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer.Add(self.text, 0, wx.ADJUST_MINSIZE, 0)
        sizer.Add(self.slider_1, 0, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        sizer.Fit(self)
        sizer.SetSizeHints(self)
        sizer.AddGrowableCol(2)
        self.Layout()
        # end wxGlade

    def do_text(self, event): # wxGlade: ValSlider.<event_handler>
        print "Event handler `do_text' not implemented!"
        event.Skip()

    def do_scroll(self, event): # wxGlade: ValSlider.<event_handler>
        print "Event handler `do_scroll' not implemented!"
        event.Skip()

# end of class ValSlider


