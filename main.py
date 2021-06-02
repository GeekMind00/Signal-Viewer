from PyQt5 import QtWidgets , QtCore, QtGui
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  
import os
import main_gui
import pandas as pd
from scipy import signal
import numpy as np
from PyQt5.QtWidgets import QMessageBox , QFileDialog
from PyQt5.Qt import QFileInfo
from PyQt5.QtPrintSupport import QPrinter
class MainWindow(QtWidgets.QMainWindow , main_gui.Ui_MainWindow):
    
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        #########variables######################
        self.i = 0 #counter for (for loob)
        #####timers for plots####
        self.timer1=0
        self.timer2=0
        self.timer3=0
        self.timer=  [

            self.timer1, 
            self.timer2, 
            self.timer3 
        ] 
        ###index for dynamic plot
        self.index1 = 0
        self.index2 = 0
        self.index3 = 0
        self.index = [
        
            self.index1,
            self.index2,
            self.index3
        ]
        ######plot configuration#####
        self.pen = pg.mkPen(color=(255, 0, 0))
        self.widget_configuration(self.widget_1 , "Signal 1")
        self.widget_configuration(self.widget_2, "Signal 2")
        self.widget_configuration(self.widget_3, "Signal 3")
        self.widget_configuration(self.widget_1s , "Spectrogram 1")
        self.widget_configuration(self.widget_2s, "Spectrogram 2")
        self.widget_configuration(self.widget_3s, "Spectrogram 3")

        self.graphs = [

            self.widget_1,
            self.widget_2,
            self.widget_3

        ]
        self.spectros = [

            self.widget_1s,
            self.widget_2s,
            self.widget_3s

        ]

        self.current_widget = self.graphs[0] #idicate the selected widget in groupBox
        self.current_widget_i = 0  ###indicate current widget index
        #####aflag to indicate which is shown signal graph(1) or spectrogram(0) 
        self.shown_1 = 1
        self.shown_2 = 1
        self.shown_3 = 1
        self.shown =[
            
            self.shown_1,
            self.shown_2,
            self.shown_3
        ]
        
        self.signals = [0,0,0] #list to store loaded signals
        self.x = [0,0,0] ### x , y to recieve data for plotting
        self.y = [0,0,0]

        #start the programm with one signal viewed

        self.view_start()

        #########actions triggeration###########
        self.actionOpen.triggered.connect(self.openfile)
        self.actionSave_as_PDF.triggered.connect(self.export_pdf)
        self.actionToolbar.triggered.connect(self.toggle_tool)
        self.actionStatus_bar.triggered.connect(self.toggle_status)
        self.actionPlay.triggered.connect(self.play)
        self.actionPause.triggered.connect(self.pause)
        self.actionStop.triggered.connect(self.stop)
        self.actionClose.triggered.connect(self.close)
        self.actionZoom_in.triggered.connect(self.zoom_in)
        self.actionZoom_out.triggered.connect(self.zoom_out)
        self.actionSpectrogram.triggered.connect(self.spectro) 
        self.actionSignal_graph.triggered.connect(self.graph)
        self.action1_Signal.triggered.connect(self.view_1)
        self.action2_Signals.triggered.connect(self.view_2)
        self.action3_Signals.triggered.connect(self.view_3)
        self.actionAbout.triggered.connect(self.pop_up)
        self.actionExit.triggered.connect(lambda: sys.exit())
        self.rightButton.clicked.connect(self.scroll_right)
        self.leftButton.clicked.connect(self.scroll_left)
        self.upButton.clicked.connect(self.scroll_up)
        self.downButton.clicked.connect(self.scroll_down)
        ####chose the current_widget to control it
        self.radioButton_1.toggled.connect(self.select_1)       
        self.radioButton_2.toggled.connect(self.select_2)
        self.radioButton_3.toggled.connect(self.select_3)
        # radiobutton.toggled.connect
    def select_1(self):
        if self.shown_1 == 1 :
            self.current_widget = self.graphs[0]
        else:
            self.current_widget = self.spectros[0]
        self.current_widget_i = 0
    def select_2(self):
        if self.shown_2 == 1 :
            self.current_widget = self.graphs[1]
        else:
            self.current_widget = self.spectros[1]
        self.current_widget_i = 1
    def select_3(self):
        if self.shown_3 == 1 :
            self.current_widget = self.graphs[2]
        else:
            self.current_widget = self.spectros[2]
        self.current_widget_i = 2
        
       



        
    #####to load and plot signal#######
    def openfile(self):
        self.file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File',"", "Data files (*.csv)")
        if self.file_path:
            df = pd.read_csv(self.file_path)
            self.current_widget.setLabel('bottom', "Time (ms")
            self.reset_widget()
            ####control which widget to plot in
            self.current_widget = self.graphs[self.current_widget_i]
            self.shown[self.current_widget_i] = 1
            self.graphs[self.current_widget_i].show()
            self.spectros[self.current_widget_i].hide()
            self.index[self.current_widget_i] = 0
            self.signals[self.current_widget_i] = self.file_path
            self.file_name = os.path.basename(self.signals[self.current_widget_i])
            self.y[self.current_widget_i] = df.iloc[:,0]
            self.reset_y(self.y[self.current_widget_i])
            self.current_widget.plot(self.y[self.current_widget_i],name = self.file_name ,pen=self.pen)
            self.plot_spectro(self.y[self.current_widget_i] , self.spectros[self.current_widget_i]) #to create spectrogram
            ##### create a timer for widgets#####
           
            if self.current_widget_i == 0:
                self.timer[0] = QtCore.QTimer()
                self.timer[0].setInterval(50)
                self.timer[0].timeout.connect(self.update_plot1)

            elif self.current_widget_i == 1:
                self.timer[1] = QtCore.QTimer()
                self.timer[1].setInterval(50)
                self.timer[1].timeout.connect(self.update_plot2)

            else:
                self.timer[2] = QtCore.QTimer()
                self.timer[2].setInterval(50)
                self.timer[2].timeout.connect(self.update_plot3)

            ######enable tools to control signal#####
            self.actionZoom_in.setEnabled(True)
            self.actionZoom_out.setEnabled(True)
            self.actionPlay.setEnabled(True)
            self.actionPause.setEnabled(True)
            self.actionStop.setEnabled(True)
            self.actionClose.setEnabled(True)
            self.actionSpectrogram.setEnabled(True)
            self.actionSignal_graph.setEnabled(True)
            self.rightButton.setEnabled(True)
            self.leftButton.setEnabled(True)
            self.upButton.setEnabled(True)
            self.downButton.setEnabled(True)
            

    ########upate function to make the plot moving###### 
    def update_plot1(self):

        if self.signals[0] != 0:
            self.index[0] = self.index[0] + 1
            self.graphs[0].setXRange(0 + self.index[0], 1000 + self.index[0], padding=0)

    def update_plot2(self):

        if self.signals[1] != 0:
            self.index[1] = self.index[1] + 1
            self.graphs[1].setXRange(0 + self.index[1], 1000 + self.index[1], padding=0)

    def update_plot3(self):                    
        if self.signals[2] != 0:
            self.index[2] = self.index[2] + 1
            self.graphs[2].setXRange(0 + self.index[2], 1000 + self.index[2], padding=0)
                    
    #######play function to start the movement####
    def play(self):
        
        if self.shown[self.current_widget_i] == 1 and self.timer[self.current_widget_i] != 0 :
            self.timer[self.current_widget_i].start()

    #######pause function to pause the movement####
    def pause(self):
      
        if self.shown[self.current_widget_i] == 1 and self.timer[self.current_widget_i] != 0 :
            self.timer[self.current_widget_i].stop()

    #######stop function to stop the movement and reset the signal plot####
    def stop(self):
    
        if self.shown[self.current_widget_i] == 1 and self.timer[self.current_widget_i] != 0 :
            self.timer[self.current_widget_i].stop()
            self.index[self.current_widget_i] = 0
            self.current_widget.plot(self.y[self.current_widget_i], pen=self.pen)
            self.current_widget.setXRange(0, 1000, padding=0)

    
    #######close function to clear the plot####
    def close(self):
 
        self.timer[self.current_widget_i] = 0
        self.signals[self.current_widget_i] = 0
        self.reset_widget()
        if (self.signals[0] == 0) and (self.signals[1] == 0) and (self.signals[2] == 0):
            self.actionZoom_in.setEnabled(False)
            self.actionZoom_out.setEnabled(False)
            self.actionPlay.setEnabled(False)
            self.actionPause.setEnabled(False)
            self.actionStop.setEnabled(False)
            self.actionClose.setEnabled(False)
            self.actionSpectrogram.setEnabled(False)
            self.rightButton.setEnabled(False)
            self.leftButton.setEnabled(False)
            self.upButton.setEnabled(False)
            self.downButton.setEnabled(False)
            self.actionSignal_graph.setEnabled(False)

     ########function to plot spectrogram####################
    def spectro(self):
        
        if self.signals[self.current_widget_i] != 0:
            self.timer[self.current_widget_i].stop()
            self.shown[self.current_widget_i] = 0
            self.current_widget = self.spectros[self.current_widget_i]
            self.graphs[self.current_widget_i].hide()
            self.spectros[self.current_widget_i].show()



    def plot_spectro(self , values , widget):
        fs = 1000 ####sampling frequency
        f,t,Sxx = signal.spectrogram(values,fs)

        pg.setConfigOptions(imageAxisOrder='row-major')
        self.img= pg.ImageItem()
        widget.addItem(self.img)
        # Add a histogram to control the gradient of the image
        self.hist = pg.HistogramLUTItem()
        # Link the histogram to the image
        self.hist.setImageItem(self.img)
        # Fit the min and max levels of the histogram
        self.hist.setLevels(np.min(Sxx), np.max(Sxx))

        self.hist.gradient.restoreState(
                {'mode': 'rgb',
                'ticks': [(0.5, (0, 182, 188, 255)),
                        (1.0, (246, 111, 0, 255)),
                        (0.0, (75, 0, 113, 255))]})
        self.img.setImage(Sxx)

        self.img.scale(t[-1]/np.size(Sxx, axis=1), f[-1]/np.size(Sxx, axis=0))

        widget.setXRange(0 , t[-1] , padding=0)
        widget.setYRange(0 , f[-1] , padding=0)

        widget.setLimits(xMin=0, xMax=t[-1], yMin=0, yMax=f[-1])
        # Add labels to the axis
        widget.setLabel('bottom', "Time", units='s')
            
        widget.setLabel('left', "Frequency", units='Hz')

    ##################################################################
    def graph(self):

        self.shown[self.current_widget_i] =1
        self.graphs[self.current_widget_i].show()
        self.spectros[self.current_widget_i].hide()
        self.current_widget = self.graphs[self.current_widget_i]



    ###########functions to control the number of shown plots###
    def view_start(self):
    
        self.graphs[1].hide()
        self.graphs[2].hide()
    
        for self.i in self.spectros:
            self.i.hide()

    def view_1(self , action):
        if action:
            self.graphs[0].show()    
            self.radioButton_1.setEnabled(True)
        else:
            self.graphs[0].hide()    
            self.radioButton_1.setEnabled(False)
       
    def view_2(self , action):
        if action:
            self.graphs[1].show()    
            self.radioButton_2.setEnabled(True)
        else:
            self.graphs[1].hide()    
            self.radioButton_2.setEnabled(False)
    def view_3(self,action):
        if action:
            self.graphs[2].show()    
            self.radioButton_3.setEnabled(True)
        else:
            self.graphs[2].hide()    
            self.radioButton_3.setEnabled(False)
    
    ##function to show about in popup message
    def pop_up(self):
        msg = QMessageBox()
        msg.setWindowTitle("About...")
        msg.setText('Signalviewer Version 1.0')
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setInformativeText('Copyright (C) 2021 SBME cairo university')
        x = msg.exec_()

    ########function to show and hide the toolbar#####
    def toggle_tool(self, action):

        if action:
            self.toolBar.show()
        else:
            self.toolBar.hide()

    ########function to show and hide the status bar#####
    def toggle_status(self, action):

        if action:
            self.statusbar.show()
        else:
            self.statusbar.hide()
    ######functionts for zoomig in and out
    def zoom_in(self):
        self.current_widget.plotItem.getViewBox().scaleBy((1 / 1.25, 1 / 1.25))
    def zoom_out(self):
        self.current_widget.plotItem.getViewBox().scaleBy((1.25,1.25))

    ######functionts for scrolling
    def scroll_right(self):
        x_range = self.current_widget.getViewBox().state['viewRange'][0] # the visible range in x axis
        rx = 0.1 * (x_range[1] - x_range[0])
        self.current_widget.setXRange((x_range[0]+rx),(x_range[1]+rx) , padding=0)

    def scroll_left(self):
        x_range = self.current_widget.getViewBox().state['viewRange'][0] # the visible range in x axis
        rx = 0.1 * (x_range[1] - x_range[0])
        self.current_widget.setXRange((x_range[0]-rx),(x_range[1]-rx) , padding=0)

    def scroll_up(self):
        y_range = self.current_widget.getViewBox().state['viewRange'][1] # the visible range in x axis
        ry = 0.1 * (y_range[1] - y_range[0])
        self.current_widget.setYRange((y_range[0]+ry),(y_range[1]+ry) , padding=0)
    
    def scroll_down(self):
        y_range = self.current_widget.getViewBox().state['viewRange'][1] # the visible range in x axis
        ry = 0.1 * (y_range[1] - y_range[0])
        self.current_widget.setYRange((y_range[0]-ry),(y_range[1]-ry) , padding=0)
    ###function to adjust plot widget automatically 

    def reset_widget(self):
        self.graphs[self.current_widget_i].clear()
        self.graphs[self.current_widget_i].setXRange(0 , 1000 , padding=0)
        self.spectros[self.current_widget_i].clear()
            
    #####function to adjust automatically y axis range after zooming , scrolling 
    def reset_y(self , data):

        self.current_widget.setYRange(min(data),max(data) , padding=0)
        

    ########configuration of plot widgets#####    
    def widget_configuration(self,widget,title):
        widget.showGrid(True, True, alpha=0.8)
        widget.setBackground('w') 
        widget.addLegend()
        widget.setTitle(title)
        widget.setXRange(0, 1000, padding=0)
    
    def export_pdf (self):
        
        fn, _ = QFileDialog.getSaveFileName(self, 'Export PDF', None, 'PDF files (.pdf);;All Files()')
        if fn != '':
            if QFileInfo(fn).suffix() == "" :
                fn += '.pdf'
            
            for self.i in range(3):
                self.shown[self.i] = 1
                if self.timer[self.i] != 0 :
                    self.timer[self.i].stop()
                self.spectros[self.i].hide()
                if self.signals[self.i] != 0:
                    self.graphs[self.i].show()
                    self.spectros[self.i].show()
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOrientation(1)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(fn)
            painter = QtGui.QPainter(printer)
            pixmap = QtWidgets.QWidget.grab(self.centralwidget).scaled(
            printer.pageRect(QPrinter.DevicePixel).size().toSize(),
            QtCore.Qt.KeepAspectRatio)
            painter.drawPixmap(0, 0, pixmap)
            painter.end()
            self.view_start()
            if self.action1_Signal.isChecked():
                self.graphs[0].show()
            if self.action2_Signals.isChecked():
                self.graphs[1].show()
            if self.action3_Signals.isChecked():
                self.graphs[2].show()
            
           

        

def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()