import sys
import json
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5 import QtGui
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import re

class PlotFrame_XAS:

    def __init__(self):
        self.filename_present = None
        self.listwidgetitemflags = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | \
                                   QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsUserCheckable
        self.SpectraDataKeys = ["atomdata", "poltype", "thin", "thout", "phi", "ominc", "eloss", "scattering_axis",
                                "eval_i", "eval_n", "trans_op", "gs_list", "temperature", "spectra"]
        self.setup_mainFrame()
        self.retranslateUi()
        self.setup_mainwindow()

    def setup_mainFrame(self):
        self.mainWindow = QMainWindow()
        self.mainWindow.setMinimumSize(1180, 850)
        self.mainWindow.setWindowTitle('XAS-PLOT-SHOW')
        self.main_frame = QWidget(self.mainWindow)
        font = QtGui.QFont()
        font.setFamily("Consola")
        font.setPointSize(9)
        if "groupBox_Load_Files":
            self.groupBox_Load_Files = QGroupBox(self.main_frame)
            self.groupBox_Load_Files.setFixedSize(250, 700)
            self.groupBox_Load_Files.setObjectName("groupBox_Single_Pixel")  # 不是界面上显示的
            self.Load_File_btn = QPushButton(self.main_frame)
            self.Load_File_btn.clicked.connect(self._handleOn_LoadFile)
            self.Load_File_btn.setFixedSize(115, 40)
            self.import_all_btn = QPushButton("import_all",self.main_frame)
            self.import_all_btn.clicked.connect(self._handleOn_ImportAllFiguresFromDataList)
            self.import_all_btn.setFixedSize(115, 40)
            self.delete_all_btn = QPushButton("delete_all",self.main_frame)
            self.delete_all_btn.clicked.connect(self._handleOn_DeleteAllFromDataList)
            self.delete_all_btn.setFixedSize(115, 40)
            HBox1 = QHBoxLayout()
            HBox2 = QHBoxLayout()
            HBox1.addWidget(self.Load_File_btn)
            HBox1.addWidget(self.delete_all_btn)
            HBox2.addWidget(self.import_all_btn)

            self.data_QList = QListWidget(self.main_frame)
            self.data_QList.setFixedSize(230, 550)
            self.data_QList.itemDoubleClicked.connect(self._handleOnImportFigureFromDataList)
            self.data_QList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            data_QList_menu = QMenu(self.data_QList)
            self.data_QList_menu_import_figure_action = QAction(data_QList_menu)
            self.data_QList_menu_delete_data_action = QAction(data_QList_menu)
            self.data_QList_menu_import_figure_action.triggered.connect(self._handleOnImportFigureFromDataList)
            self.data_QList_menu_delete_data_action.triggered.connect(self._handleOnDeleteDataFromDataList)
            data_QList_menu.addAction(self.data_QList_menu_import_figure_action)
            data_QList_menu.addAction(self.data_QList_menu_delete_data_action)
            self.data_QList_menu_import_figure_action.setText("import figure")
            self.data_QList_menu_delete_data_action.setText("delete item")
            def data_QList_menu_show():
                if self.data_QList.currentItem() is None:
                    return
                data_QList_menu.exec_(QtGui.QCursor.pos())

            self.data_QList.customContextMenuRequested.connect(data_QList_menu_show)

            groupBox_Load_Files_Layout = QVBoxLayout(self.groupBox_Load_Files)
            groupBox_Load_Files_Layout.addLayout(HBox1, QtCore.Qt.AlignCenter)
            groupBox_Load_Files_Layout.addLayout(HBox2, QtCore.Qt.AlignCenter)
            groupBox_Load_Files_Layout.addWidget(self.data_QList)

        if "groupBox_Single_Pixel":
            self.groupBox_Single_Pixel = QGroupBox(self.main_frame)
            self.groupBox_Single_Pixel.setFixedSize(1150, 900)
            self.groupBox_Single_Pixel.setObjectName("groupBox_Single_Pixel")

            self.button_remove_all = QPushButton("REMOVE ALL", self.groupBox_Single_Pixel)
            self.button_remove_all.setFixedSize(120, 32)
            self.button_remove_all.clicked.connect(self._handleOn_Remove_All)

            self.combo_which = QComboBox(self.groupBox_Single_Pixel)
            self.combo_which.setFixedSize(190,32)
            self.combo_which.addItem("xas_1v1c_python_ed")
            self.combo_which.addItem("xas_1v1c_fortran_ed")
            self.combo_which.addItem("xas_2v1c_fortran_ed")

            self.fig = plt.figure(figsize=(16, 10), dpi=100)
            self.axes = plt.axes([0.10, 0.15, 0.80, 0.75])
            self.canvas = FigureCanvas(self.fig)
            self.canvas.setParent(self.groupBox_Single_Pixel)
            self.mpl_toolbar_origin = NavigationToolbar(self.canvas, self.groupBox_Single_Pixel)

            HBox = QHBoxLayout()
            HBox.addWidget(self.mpl_toolbar_origin)
            HBox.addWidget(self.combo_which)
            HBox.addWidget(self.button_remove_all)
            groupBox_Single_Pixel_Layout = QVBoxLayout(self.groupBox_Single_Pixel)
            groupBox_Single_Pixel_Layout.addLayout(HBox)
            groupBox_Single_Pixel_Layout.addWidget(self.canvas)

        if "slider":
            self.para_slider = QSlider(self.main_frame)
            self.para_slider.setFixedSize(45, 275)
            self.para_slider.setOrientation(QtCore.Qt.Vertical)
            self.para_slider.setMinimum(0)  # 设置最小值
            self.para_slider.setMaximum(1000)  # 设置最大值
            self.para_slider.setSingleStep(1)  # 设置步长值
            self.para_slider.setValue(0)  # 设置当前值
            self.para_slider.valueChanged.connect(lambda :self._handleOn_value_change(self.para_slider.value()))
            self.para_min = QLineEdit(self.main_frame)
            self.para_min.setFixedSize(50, 35)
            self.para_max = QLineEdit(self.main_frame)
            self.para_max.setFixedSize(50, 35)
            VBOX_Slider = QVBoxLayout()
            VBOX_Slider.addWidget(self.para_min)
            VBOX_Slider.addWidget(self.para_slider)
            VBOX_Slider.addWidget(self.para_max)

        if "mainlayout":
            VBOX_1 = QVBoxLayout()
            VBOX_1.addWidget(self.groupBox_Load_Files)
            VBOX_2 = QVBoxLayout()
            main_frame_layout = QGridLayout(self.main_frame)
            main_frame_layout.setAlignment(QtCore.Qt.AlignTop)
            main_frame_layout.addLayout(VBOX_1, 0, 0, 2, 1, QtCore.Qt.AlignTop)
            main_frame_layout.addWidget(self.groupBox_Single_Pixel, 0, 1, 2, 2)
            main_frame_layout.addLayout(VBOX_2, 0, 3, 2, 1, QtCore.Qt.AlignTop)
            main_frame_layout.addLayout(VBOX_Slider, 0, 4, 2, 1, QtCore.Qt.AlignTop)
            self.main_frame.setLayout(main_frame_layout)

            self.scroll_area = QScrollArea(self.mainWindow)
            self.scroll_area.setWidget(self.main_frame)
            self.mainWindow.setCentralWidget(self.scroll_area)

    def setup_mainwindow(self):
        # mainWindow的menuBar的设置
        def create_action(text, slot=None, shortcut=None,
                          icon=None, tip=None, checkable=False,
                          signal="triggered()"):  # 创建一个动作,
            action = QAction(text, self.mainWindow)
            if icon is not None:
                action.setIcon(QIcon(":/%s.png" % icon))
            if shortcut is not None:
                action.setShortcut(shortcut)
            if tip is not None:
                action.setToolTip(tip)
                action.setStatusTip(tip)
            if slot is not None:
                action.triggered.connect(slot)
            if checkable:
                action.setCheckable(True)
            return action

        def add_actions(target, actions):
            for action in actions:
                if action is None:
                    target.addSeparator()  # 两个动作之间画一条横线
                else:
                    target.addAction(action)

        def save_plot():  # file_menu的功能之一,用来保存当前的图像,并在statusBar中显示保存的路径
            file_choices = "PNG (*.png)|*.png"

            path, filetype = QFileDialog.getSaveFileName(self.mainWindow,
                                                         'Save file', '',
                                                         file_choices)
            if path:
                self.canvas.print_figure(path, dpi=100)
                self.mainWindow.statusBar().showMessage('Saved to %s' % path, 8000)  # 8000是指message显示的时间长度为8000毫秒

        file_menu = self.mainWindow.menuBar().addMenu("File")  # 在menuBar上添加File菜单
        save_file_action = create_action("Save plot", slot=save_plot, shortcut="Ctrl+S", tip="Save the plot")
        quit_action = create_action("Quit", slot=self.mainWindow.close, shortcut="Ctrl+Q", tip="Close the application")
        add_actions(file_menu, (save_file_action, None, quit_action))

        def on_about():  # help_menu中的功能,用来介绍该界面已经实现的功能
            msg = """ A SC_gap Fitting GUI of using PyQt with matplotlib:

                * Use the matplotlib navigation bar
                * Add values to the text box and press Enter (or click "Draw")
                * Show or hide the grid
                * Drag the slider to modify the width of the bars
                * Save the plot to a file using the File menu
                * Click on a bar to receive an informative message
               """
            QMessageBox.about(self.mainWindow, "About the demo", msg.strip())  # #

        help_menu = self.mainWindow.menuBar().addMenu("Help")
        about_action = create_action("About", slot=on_about, shortcut='F1', tip='About the demo')
        add_actions(help_menu, (about_action,))

        # mainWindow的status Bar的设定
        self.mainWindow.statusBar().showMessage("")

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        if "groupBox_Load_Files":
            self.groupBox_Load_Files.setTitle(
                _translate("PlotFrame_groupBox_Load_Files_title", "Load_Files"))
            self.Load_File_btn.setText(_translate("PlotFrame_groupBox_Load_Files_text", "LOAD"))

        if "groupBox_Single_Pixel":
            self.groupBox_Single_Pixel.setTitle(
                _translate("PlotFrame_groupBox_Single_Pixel_title", "Single_Pixel"))

    def _handleOn_value_change(self, value:float):
        try:
            item = self._getItemFromName(self.data_QList, self.filename_present)
            spectra_data = item.data(-1)[2]
            data_max = max(spectra_data)
            data_min = min(spectra_data)
            delta = (data_max-data_min)/500
        except Exception as e:
            self.informMsg(str(e)+":目前无数据")
            return
        row = self.data_QList.count()
        diff = delta * value
        try:
            self._handleOn_Remove_All()
            for i in range(row):
                item = self.data_QList.item(i)
                spectra_data = item.data(-1)[2] + diff*(i-1)
                self.canvas_plot_from_data(item.data(-1)[1], spectra_data, item)
        except Exception as e:
            self.informMsg(str(e))

    def _getItemFromName(self, parent:QListWidget, name) -> QListWidgetItem:
        row = parent.count()
        for i in range(row):
            if parent.item(i).text() == name:
                return parent.item(i)
        item = QListWidgetItem(parent)
        item.setText(name)
        return item

    def _handleOn_LoadFile(self):
        fileNames_List, fileType = QFileDialog.getOpenFileNames(self.main_frame, r'Load json',
                                                         r'D:\Users\yg\PycharmProjects\spectra_data', r'json Files(*.json)')

        for fileName in fileNames_List:
            try:
                with open(fileName, 'r') as f:
                    temp = json.loads(f.read())
                fileName_list = fileName.split('/')
                which = self.combo_which.currentText()
                try:
                    ominc = [float(c_num) for c_num in temp["ominc"]]
                    ominc = (np.array(ominc)).flatten()
                    spectra_xas = [float(str) for str in temp["spectra"][which]]
                    spectra_xas = np.array(spectra_xas)
                    data = [temp['poltype'], ominc, spectra_xas]
                    self.filename_present = fileName_list[-1]
                    row = 0
                    while row < self.data_QList.count():
                        if self.data_QList.item(row).text() == self.filename_present:
                            reply = self.questionMsg("List中已经存在相同名称,是否进行覆盖？")
                            if reply == False:
                                return
                            else:
                                break
                        row += 1
                    if row != self.data_QList.count():  # 前面已经问过相同的问题了,因此这里直接删除
                        self.data_QList.takeItem(row)

                    item = self._getItemFromName(parent=self.data_QList, name=self.filename_present)
                    item.setData(-1, data)
                    item.setFlags(self.listwidgetitemflags)
                    self.data_QList.addItem(item)
                    self.data_QList.sortItems()
                    self.data_QList.setCurrentItem(item)
                except Exception as e:
                    self.informMsg(str(e) + ":data_QList存放出錯")
                    return
            except Exception as e:
                self.informMsg(str(e) + "文件錯誤")
                return

    def _handleOn_ImportAllFiguresFromDataList(self):
        row = self.data_QList.count()
        if row == 0:
            self.informMsg("data_list中無item")
            return
        for i in range(row):
            item = self.data_QList.item(i)
            try:
                item.data(4).remove()
            except Exception as e:
                self.informMsg(str(e))
            try:
                ominc = item.data(-1)[1]
                xas = item.data(-1)[2]
                self.canvas_plot_from_data(ominc, xas, item)
            except Exception as e:
                self.informMsg(str(e) + ":import失败")

    def _handleOnImportFigureFromDataList(self):  # 用来作原始曲线
        item = self.data_QList.currentItem()
        try:
            item.data(4).remove()
        except Exception as e:
            self.informMsg(str(e) + ":first time")
        try:
            self.filename_present = item.text()
            ominc = item.data(-1)[1]
            xas = item.data(-1)[2]
            self.canvas_plot_from_data(ominc, xas, item)
        except Exception as e:
            self.informMsg(str(e) + ":import失败")

    def canvas_plot_from_data(self, bias, data, item:QListWidgetItem):
        try:
            row = self.data_QList.count()
            for i in range(row):
                if item == self.data_QList.item(i):
                    line = self.axes.plot(bias, data, linestyle='-', linewidth=2)[0]
                    item.setData(4, line)
                    self.canvas.draw()
        except Exception as e:
            self.informMsg(str(e) + ":作曲綫失敗")

    def _handleOnDeleteDataFromDataList(self):  # 图像连同数据全部销毁 # 如果该函数被调用,则一定是选中对象了,这说明List中至少有一个item
        item = self.data_QList.currentItem()
        filename = item.text()

        if filename == self.filename_present:
            item.data(4).remove()
            self.canvas.draw()
            self.filename_present = None

        row = self.data_QList.row(item)
        self.data_QList.takeItem(row)

    def _handleOn_DeleteAllFromDataList(self):
        reply = self.questionMsg("是否要全部刪除")
        if reply == True:
            row = self.data_QList.count()
            for i in range(row):
                self._handleOnDeleteDataFromDataList()
        self.filename_present = None

    def _handleOn_Remove_All(self):  # self.button_remove_all的调用函数
        try:
            row = self.data_QList.count()
            for i in range(row):
                self.data_QList.item(i).data(4).remove()
        except Exception as e:
            self.informMsg(str(e) + ":實驗數據抹除失败")
        try:
            self.axes.cla()
            self.canvas.draw()
        except Exception as e:
            self.informMsg(str(e) + ":something wrong")
            return

    def check(self) -> bool:
        try:
            if self.filename_present == None:
                self.informMsg("目前无数据")
                return False
        except:
            return True

    # 两个信息提示框
    def informMsg(self, msg: str):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("inform")
        msgBox.setText(msg)
        msgBox.exec_()

    def questionMsg(cls, msg: str):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("确认框")
        reply = QMessageBox.information(msgBox,"标题",msg,QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            return True
        if reply == QMessageBox.No:
            return False
        msgBox.exec_()

# to do list:如何鼠标触碰后显示QWidgetList中的item的名称？？
if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = PlotFrame_XAS()
    form.mainWindow.show()
    app.exec_()


