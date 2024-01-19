import PySimpleGUI as sg
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import pandas as pd
#from sklearn.metrics import r2_score
import scipy.stats

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

def scatterPlotToUI(windowX,windowY,chem="NA"):
    _x=verifyNumbers(window[windowX].get().splitlines())
    _y=verifyNumbers(window[windowY].get().splitlines())
    
    _newFig = matplotlib.figure.Figure(figsize=(4.5, 4.5), dpi=100)
    _sub1 = _newFig.add_subplot(111)
    try:
        scatterPlot(_x,_y,_sub1)
    except ValueError:
        print("x and y must be the same size")
    return FigOnCanvas(window['-CANVAS-'].TKCanvas,_newFig)

def addRegressionUI(windowX,windowY,chem="NA",regression='linear'):
    inputX=verifyNumbers(window[windowX].get().splitlines())
    inputY=verifyNumbers(window[windowY].get().splitlines())

    _updatedFig = matplotlib.figure.Figure(figsize=(4.5, 4.5), dpi=100)
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
    print('Plotting regression line')
    try:
        scatterPlot(_x,_y,_sub1)
        slope, yint, temp = linearRegression(_x,_y,_sub1,chem='NA')
    except ValueError:
        print("x and y must be the same size")  
    _sub1.autoscale()
    _sub1.set_xlabel(_xlabel)
    _sub1.set_ylabel(_ylabel)
        
    return FigOnCanvas(window['-CANVAS-'].TKCanvas,_updatedFig), slope, yint

dataCol1 =[
    [   sg.Text("Column 1")],
        [sg.Multiline(size=(5,20), key="Multiline1",expand_x=True, expand_y=True, justification='left', horizontal_scroll=True)
        ]
    ]

dataCol2 =[
    [   sg.Text("Column 2")],
        [sg.Multiline(size=(5,20), key="Multiline2",expand_x=True, expand_y=True, justification='left',horizontal_scroll=True)
        ]
    ]

graphCol3 =[
    [
        sg.Text("Column 3")
        ],[sg.Button("Clear"),sg.Button("Rescale")],[sg.Canvas(key='-CANVAS-')],
    [sg.Button("Linear Regression"),sg.Button("Log Regression")],
    
]

layout = [ 
    [sg.Text('Please enter data')],
    [sg.Column(dataCol1),sg.VSeperator(),sg.Column(dataCol2),sg.VSeperator(),sg.Column(graphCol3)],
    [sg.Button("Plot")],
    [sg.Submit(), sg.Cancel()]
]
window = sg.Window('Simple data entry window', layout,margins=(100, 100)) 

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event=="Exit":
        break
    if event=="Linear Regression" :
        if 'drawnCanvas' in globals():
            delete_figure_agg(drawnCanvas)
            del(drawnCanvas)
        drawnCanvas,slope,yint= addRegressionUI('Multiline1','Multiline2',chem="NA",regression='linear')
    if event=="Log Regression":
        if 'drawnCanvas' in globals():
            delete_figure_agg(drawnCanvas)
            del(drawnCanvas)
        drawnCanvas,slope,yint= addRegressionUI('Multiline1','Multiline2',chem="NA",regression='log')
    if event =="Rescale":
        print("plot will be rescaled")
    if event=="Clear" and ('drawnCanvas' in globals()):
        delete_figure_agg(drawnCanvas)
        del(drawnCanvas)
    if event =="Plot":
        if 'drawnCanvas' in globals():
            delete_figure_agg(drawnCanvas)
            del(drawnCanvas)
        drawnCanvas = scatterPlotToUI('Multiline1','Multiline2')
window.close() 
