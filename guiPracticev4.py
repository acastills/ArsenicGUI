import PySimpleGUI as sg
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import pandas as pd
import scipy.stats
import tkinter as tk

plotSize=4
canvasSize=100
windowSizeX=200
windowSizeY=150
def verifyNumbers(inputArray):
    _temp=[]
    for i in inputArray:
        if(i != '\n'):
            try:
                _temp.append(float(i))
            except ValueError:
               print('{} is not recognized as a number'.format(i))
    return _temp

def delete_figure_agg(figure_agg):
    figure_agg.get_tk_widget().forget()
    try:
        FigOnCanvas.canvas_packed.pop(figure_agg.get_tk_widget())
    except Exception as e:
        print(f'Error removing {figure_agg} from list', e)
    plt.close('all')
    
def logPrep(inputArray):
    _temp=[]
    for i in inputArray:
        if(i > 0):
            _temp.append(float(i))
    return _temp

chem_to_color={'As(V)':'purple','PO4':'orange','As(III)':'green'}

def scatterPlot(x,y,ax,chem='NA'):
    _color=chem_to_color.get(chem,'black')
    try:
        ax.scatter(x,y,color=_color)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
    except ValueError:
        print("x and y must be the same size")
    return ax
    
def linearRegression(x,y,ax,chem='NA'):
    #slope, yint = np.polyfit(x, y, deg=1)
    slope, yint, r_squared, p_value, std_err = scipy.stats.linregress(x, y)
    _color=chem_to_color.get(chem,'black')
    # Create sequence of 100 numbers from 0 to 100 
    xseq = np.linspace(min(x), max(x), num=100)
    if yint <0:
        #ax.legend([("y=%.2fx(%.2f) , $R^2$=%.2f"%(slope,yint, r_squared))],loc='best')
        ax.legend([("y=%.2fx%.2f , $R^2$=%.2f"%(slope,yint, r_squared))],draggable=True,loc='best')

    else:
        ax.legend([("y=%.2fx+%.2f , $R^2$=%.2f"%(slope,yint, r_squared))],draggable=True, loc='best')
    ax.plot(xseq, yint + slope * xseq, color=_color, lw=2.5);
    return slope, yint, ax

def FigOnCanvas(canvas, figure):
    if not hasattr(FigOnCanvas, 'canvas_packed'):
        FigOnCanvas.canvas_packed = {}
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    widget = figure_canvas_agg.get_tk_widget()
    if widget not in FigOnCanvas.canvas_packed:
        FigOnCanvas.canvas_packed[widget] = figure
        widget.pack(side='top', fill='both', expand=1.25)
    return figure_canvas_agg

def scatterPlotToUI(windowX,windowY,canvas,chem="NA"):
    print('made it here')
    _x=verifyNumbers(window[windowX].get().splitlines())
    _y=verifyNumbers(window[windowY].get().splitlines())
    
    print(_x)
    _newFig = matplotlib.figure.Figure(figsize=(plotSize, plotSize), dpi=100)
    _sub1 = _newFig.add_subplot(111)
    try:
        scatterPlot(_x,_y,_sub1)
    except ValueError:
        print("x and y must be the same size")
    return FigOnCanvas(canvas.TKCanvas,_newFig)

 ## based on answer from geeksForGeeks 
def isVariablePresent(variable):
    for name, value in globals().items():
        if value is variable:
            return True

def addRegressionUI(windowX,windowY,canvas,regression='linear',chem="NA"):
    inputX=verifyNumbers(window[windowX].get().splitlines())
    inputY=verifyNumbers(window[windowY].get().splitlines())

    _updatedFig = matplotlib.figure.Figure(figsize=(plotSize, plotSize), dpi=100)
    _sub1 = _updatedFig.add_subplot(111)
    
    if regression=="log":
        prepX=logPrep(inputX)
        prepY=logPrep(inputY)
        try:
            # x is the dataframe index
            _checkedDF=pd.DataFrame(inputY,inputX)
        except ValueError:
            print("x and y must be the same size")
        #Removing paired x and y values if they are not fit for log
        for i in _checkedDF.index:
            if i not in prepX:
                _checkedDF=_checkedDF.drop(i)
        for j in _checkedDF[0]:
            if j not in prepY:
                _checkedDF=_checkedDF[_checkedDF[0] != j]
        _x=np.log(np.array(_checkedDF.index))
        _y=np.log(np.array(_checkedDF[0]))
        _xlabel="log(x)"
        _ylabel="log(y)"
    else:
        _x=inputX
        _y=inputY
        _xlabel="x"
        _ylabel="y"
    ######
    try:
        scatterPlot(_x,_y,_sub1)
        slope, yint, temp = linearRegression(_x,_y,_sub1,chem)
    except ValueError:
        print("x and y must be the same size")  
    _sub1.autoscale()
    _sub1.set_xlabel(_xlabel)
    _sub1.set_ylabel(_ylabel)
        
    return FigOnCanvas(canvas.TKCanvas,_updatedFig), slope, yint

l1=sg.Text("Choose method:")
r11=sg.Radio('PVA','chemMethod',key='pva',default=True)
r12=sg.Radio('SDS','chemMethod',key='sds')

class myIndicatorButton():
    def __init__(self,inputText,myOpt1,myOpt2,myGroup):
        self.myText=sg.Text(inputText)
        self.option1=sg.Radio(myOpt1,myGroup,default=True)
        self.option2=sg.Radio(myOpt2,myGroup,key=myGroup+'_'+myOpt2.lower())

chemMethodButton=myIndicatorButton('Choose method:','PVA','SDS','chemMethod')
plotButton1=myIndicatorButton('','Linear','Log','reg1')
plotButton2=myIndicatorButton('','Linear','Log','reg2')
plotButton3=myIndicatorButton('','Linear','Log','reg3')

inputOrganization={
    'Plot1':{'inWindowX':'Multiline1',
    'inWindowY':'Multiline2',
    'inCanvas':'-CANVAS1-',
    'button':plotButton1,
    'drawnCanvas':'drawnCanvas1',
    'chem':'PO4'
    },
    'Plot2':{'inWindowX':'Multiline3',
    'inWindowY':'Multiline4',
    'inCanvas':'-CANVAS2-',
    'button':plotButton2,
    'drawnCanvas':'drawnCanvas2',
    'chem':'As(V)'
    } ,
    'Plot3':{'inWindowX':'Multiline5',
    'inWindowY':'Multiline6',
    'inCanvas':'-CANVAS3-',
    'button':plotButton3,
    'drawnCanvas':'drawnCanvas3',
    'chem':'As(III)'
    }
}
class myDrawnCanvas():
    def __init__(self,inputEvent):
        global window
        global values
        global inputOrganization
        _isLogRegression=values[inputOrganization[inputEvent]['button'].option2.key]
        self._regression = 'log' if _isLogRegression else 'linear'
        self._xInput=inputOrganization[inputEvent]['inWindowX']
        self._yInput=inputOrganization[inputEvent]['inWindowY']
        self._canvas=window[inputOrganization[inputEvent]['inCanvas']]
        self._chem=inputOrganization[inputEvent]['chem']
    
    def makeCompletePlot(self):
        print('in super class!')
        _drawnCanvas,slope,yint= addRegressionUI(self._xInput,self._yInput,self._canvas,self._regression,self._chem)
        #_drawnCanvas = scatterPlotToUI(self._xInput,self._yInput,self._canvas)
        return _drawnCanvas

dataCol1 =[
    [   sg.Text("Concentration (micromol)")],
        [sg.Multiline(size=(5,5), key="Multiline1",expand_x=True, expand_y=True, justification='left', horizontal_scroll=True)],
         [sg.Multiline(size=(5,5), key="Multiline3",expand_x=True, expand_y=True, justification='left', horizontal_scroll=True)],
          [sg.Multiline(size=(5,5), key="Multiline5",expand_x=True, expand_y=True, justification='left', horizontal_scroll=True)]
        
    ]

dataCol2 =[
    [   sg.Text("Absorbance")],
        [sg.Multiline(size=(5,5), key="Multiline2",expand_x=True, expand_y=True, justification='left',horizontal_scroll=True)],
         [sg.Multiline(size=(5,5), key="Multiline4",expand_x=True, expand_y=True, justification='left',horizontal_scroll=True)],
          [sg.Multiline(size=(5,5), key="Multiline6",expand_x=True, expand_y=True, justification='left',horizontal_scroll=True)],
        
    ]

graphCol3 =[
    [sg.Text("Calibration")],
    [sg.Button("Plot1"),sg.Button("Clear1"),plotButton1.myText,plotButton1.option1,plotButton1.option2],[sg.Canvas(key=inputOrganization['Plot1']['inCanvas'])],
    [sg.Button("Plot2"),sg.Button("Clear2"),plotButton2.myText,plotButton2.option1,plotButton2.option2],[sg.Canvas(key=inputOrganization['Plot2']['inCanvas'])],
    [sg.Button("Plot3"),sg.Button("Clear3"),plotButton3.myText,plotButton3.option1,plotButton3.option2],[sg.Canvas(key=inputOrganization['Plot3']['inCanvas'])]
]

layout = [ 
    [sg.Text('Please enter data')],[chemMethodButton.myText,chemMethodButton.option1,chemMethodButton.option2],
    [sg.Column(dataCol1),sg.VSeperator(),sg.Column(dataCol2),sg.VSeperator(),sg.Column(graphCol3)],
    [sg.Submit(), sg.Cancel()]
]
window = sg.Window('Simple data entry window', layout,margins=(windowSizeX, windowSizeY)) 

canvases=['drawnCanvas1','drawnCanvas2','drawnCanvas3']

def clearPlot(figName):
   if figName in globals():
       for i in globals().keys():
            delete_figure_agg(globals()[i])
            del(fig1)
while True:
    event, values = window.read()
    
    if event == sg.WIN_CLOSED or event=="Exit":
        break
    if event=="Clear1" and ('fig1' in globals()):
        delete_figure_agg(fig1)
        #fig1.get_tk_widget().forget()
        del(fig1)
    if event =="Plot1":
        if 'fig1' in globals():
            delete_figure_agg(fig1)
            del(fig1)
        fig1=myDrawnCanvas(event).makeCompletePlot()
    if event =="Plot2":
        if 'fig2' in globals():
            delete_figure_agg(fig2)
            del(fig2)
        fig2=myDrawnCanvas(event).makeCompletePlot()
    if event =="Plot3":
        if 'fig3' in globals():
            delete_figure_agg(fig3)
            del(fig3)
        fig3=myDrawnCanvas(event).makeCompletePlot()

window.close() 
