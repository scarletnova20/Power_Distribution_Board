from pathlib import Path
import wx
import wx.svg
app=wx.App(False)
source=Path('engineering/schematic_preview/Swayatt_PCB.svg')
im=wx.svg.SVGimage.CreateFromFile(str(source))
bmp=im.ConvertToBitmap(width=2376,height=1680)
bmp.SaveFile('engineering/schematic_preview/Swayatt_PCB.png',wx.BITMAP_TYPE_PNG)
print('Rendered schematic preview')
