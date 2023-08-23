# Qt5 version 5.15.2
# PyQt5 version 5.15.2
# python version 3.8

from OwnFrame import *
from PlotFrame_XAS import *
from PlotFrame_RIXS import *
from DataManager import *
import json
import numpy as np

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from edrixs.solvers import *
from edrixs.plot_spectrum import *


class SecondFrame(OwnFrame):
    def __init__(self, parent=None, width=1280, height=840): # parent来自于OwnApplication
        OwnFrame.__init__(self, parent, width, height) # 获得父类中的实例变量
        self.frame = super().getFrame()
        self.frame.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        # self.frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.frame.setMinimumHeight(height - 20)
        self.frame.setMinimumWidth(width - 36)
        self._setupDataVariable()
        self._arrangeUI()
        self._retranslateAll()

        self._textInputRestrict()
        self._arrangeDataInWidgets()

    def _setupDataVariable(self):
        self.dataManager_spectra = DataManager_spectra()
        self.atomdata_present = None
        self.spectra_name_present = None
        # 下面三个是作图时要用的
        self.spectra_data_present = {}
        self.ominc_present = []
        self.eloss_present = []

        self.SpectraDataKeys = ["atomdata", "poltype", "thin", "thout", "phi", "ominc", "eloss", "scattering_axis",
                                "eval_i", "eval_n", "trans_op", "gs_list", "temperature", "spectra"]

    def getFrame(self):  # 属于SecondFrame的getFrame,父类OwnFrame中也含有一个getFrame
        return self.scrollForSecondFrame

# 与所有控件都相关的函数
    def _arrangeUI(self):

        needToSaveStyleSheet = 'color:rgb(160,60,60)'
        if "boxSpectraPara":
            self.boxSpectraPara = QGroupBox(self.frame)
            self.boxSpectraPara.setFixedSize(1020, 605)

            self.rixs_check_box = QCheckBox("rixs", self.boxSpectraPara)
            self.rixs_check_box.setFixedSize(100,32)
            self.rixs_check_box.setChecked(True)
            self.rixs_check_box.stateChanged.connect(self._handleOnCheckChanged_rixs)

            self.xas_check_box = QCheckBox("xas", self.boxSpectraPara)
            self.xas_check_box.setFixedSize(100,32)
            self.xas_check_box.setChecked(False)
            self.xas_check_box.stateChanged.connect(self._handleOnCheckChanged_xas)

            self.poltype_label = QLabel(self.boxSpectraPara)
            self.poltype_label.setAlignment(QtCore.Qt.AlignCenter)
            self.poltype_label.setFixedSize(145,32)

            self.combo_in = QComboBox(self.boxSpectraPara)
            self.combo_in.addItem("linear")  # 当选用某些频道但没有实现进行精确对角化则会报错,让用户先去进行相应的精确对角化
            self.combo_in.addItem("left")
            self.combo_in.addItem("right")
            self.combo_in.addItem("isotropic")
            self.combo_in.setCurrentText("linear")
            self.combo_in.setFixedSize(125, 32)
            self.alpha_label = QLabel(self.boxSpectraPara)
            self.alpha_label.setAlignment(QtCore.Qt.AlignCenter)
            self.alpha_label.setFixedSize(80,32)
            self.alpha_text = QLineEdit(self.boxSpectraPara)  # str
            self.alpha_text.setFixedSize(62, 32)
            self.combo_out = QComboBox(self.boxSpectraPara)
            self.combo_out.addItem("linear")  # 当选用某些频道但没有实现进行精确对角化则会报错,让用户先去进行相应的精确对角化
            self.combo_out.addItem("left")
            self.combo_out.addItem("right")
            self.combo_out.addItem("isotropic")
            self.combo_out.setCurrentText("linear")
            self.combo_out.setFixedSize(125, 32)
            self.beta_label = QLabel(self.boxSpectraPara)
            self.beta_label.setAlignment(QtCore.Qt.AlignCenter)
            self.beta_label.setFixedSize(80,32)
            self.beta_text = QLineEdit(self.boxSpectraPara)  # str
            self.beta_text.setFixedSize(62, 32)

            self.thin_label = QLabel(self.boxSpectraPara)
            self.thin_label.setAlignment(QtCore.Qt.AlignCenter)
            self.thin_label.setFixedSize(145,32)

            self.thin_text = QLineEdit(self.boxSpectraPara)  # str
            self.thin_text.setFixedSize(62, 32)

            self.thout_label = QLabel(self.boxSpectraPara)
            self.thout_label.setAlignment(QtCore.Qt.AlignCenter)
            self.thout_label.setFixedSize(145,32)

            self.thout_text = QLineEdit(self.boxSpectraPara)  # str
            self.thout_text.setFixedSize(62, 32)

            self.phi_label = QLabel(self.boxSpectraPara)
            self.phi_label.setAlignment(QtCore.Qt.AlignCenter)
            self.phi_label.setFixedHeight(32)

            self.phi_text = QLineEdit(self.boxSpectraPara)  # str
            self.phi_text.setFixedSize(62, 32)

            self.photon_energy_ref_label = QLabel(self.boxSpectraPara)
            self.photon_energy_ref_label.setFixedSize(750, 32)

            self.ominc_label = QLabel(self.boxSpectraPara)
            self.ominc_label.setAlignment(QtCore.Qt.AlignCenter)
            self.ominc_label.setStyleSheet(needToSaveStyleSheet)
            self.ominc_label.setFixedSize(145,32)
            self.ominc_texts = [QLineEdit(self.boxSpectraPara),
                                   QLineEdit(self.boxSpectraPara),
                                   QLineEdit(self.boxSpectraPara)]
            ominc_layout = QHBoxLayout()
            ominc_layout.addWidget(self.ominc_label)
            for text in self.ominc_texts:
                text.setFixedSize(70, 32)
                text.setStyleSheet(needToSaveStyleSheet)
                ominc_layout.addWidget(text)

            self.eloss_label = QLabel(self.boxSpectraPara)
            self.eloss_label.setAlignment(QtCore.Qt.AlignCenter)
            self.eloss_label.setStyleSheet(needToSaveStyleSheet)
            self.eloss_label.setFixedSize(145,32)
            self.eloss_texts = [QLineEdit(self.boxSpectraPara),
                                QLineEdit(self.boxSpectraPara),
                                QLineEdit(self.boxSpectraPara)]
            eloss_layout = QHBoxLayout()
            eloss_layout.addWidget(self.eloss_label)
            for text in self.eloss_texts:
                text.setFixedSize(70, 32)
                text.setStyleSheet(needToSaveStyleSheet)
                eloss_layout.addWidget(text)

            self.temperature_label = QLabel(self.boxSpectraPara)
            self.temperature_label.setAlignment(QtCore.Qt.AlignCenter)
            self.temperature_label.setFixedSize(126,32)
            self.temperature_text = QLineEdit(self.boxSpectraPara)
            self.temperature_text.setFixedSize(62, 32)

            self.gamma_f_label = QLabel(self.boxSpectraPara)
            self.gamma_f_label.setAlignment(QtCore.Qt.AlignCenter)
            self.gamma_f_label.setFixedSize(126,32)

            self.gamma_f_text = QLineEdit(self.boxSpectraPara)
            self.gamma_f_text.setFixedSize(62, 32)

            if "scattering_axis_box":
                self.scattering_axis_box = QGroupBox(self.boxSpectraPara)
                self.scattering_axis_box.setFixedSize(240,140)
                # 3*3的矩阵
                self.scattering_axis_texts = [[QLineEdit(self.scattering_axis_box) for _ in range(3)] for _ in range(3)]
                for row in self.scattering_axis_texts:
                    for LineEdit in row:
                        LineEdit.setFixedSize(62, 32)

                scattering_axis_box_layout = QGridLayout(self.scattering_axis_box)
                scattering_axis_box_layout.setAlignment(QtCore.Qt.AlignTop)
                def arrange_matrix_on_box(grid_layout, widgets):
                    for row_i in range(len(widgets)):
                        one_row = widgets[row_i]
                        for col_j in range(len(one_row)):
                            grid_layout.addWidget(one_row[col_j], row_i, col_j, QtCore.Qt.AlignTop)

                arrange_matrix_on_box(scattering_axis_box_layout, self.scattering_axis_texts)
                self.scattering_axis_box.setLayout(scattering_axis_box_layout)

                self.image_label = QLabel(self.boxSpectraPara)
                self.image_label.setFixedSize(450,320)
                im = QPixmap('./images/rixs-geometry.png')
                self.image_label.setScaledContents(True)
                self.image_label.setPixmap(im)

            if "Para_Layout":
                poltype_layout = QHBoxLayout()
                poltype_layout.addWidget(self.poltype_label)
                poltype_layout.addWidget(self.combo_in)
                poltype_layout.addWidget(self.alpha_label)
                poltype_layout.addWidget(self.alpha_text)
                poltype_layout.addWidget(self.combo_out)
                poltype_layout.addWidget(self.beta_label)
                poltype_layout.addWidget(self.beta_text)

                ParaLayout_top = QGridLayout()
                ParaLayout_top.setAlignment(QtCore.Qt.AlignTop)
                ParaLayout_top.addWidget(self.rixs_check_box, 0, 0, 1, 1, QtCore.Qt.AlignTop)
                ParaLayout_top.addWidget(self.xas_check_box, 0, 1, 1, 1, QtCore.Qt.AlignTop)
                ParaLayout_top.addLayout(poltype_layout,1,0,1,4, QtCore.Qt.AlignTop)

                ParaLayout = QGridLayout()
                ParaLayout.setAlignment(QtCore.Qt.AlignTop)
                ParaLayout.addWidget(self.thin_label, 2, 0, 1, 1, QtCore.Qt.AlignTop)
                ParaLayout.addWidget(self.thin_text, 2, 1, 1, 1, QtCore.Qt.AlignTop)
                ParaLayout.addWidget(self.thout_label, 3, 0, 1, 1, QtCore.Qt.AlignTop)
                ParaLayout.addWidget(self.thout_text, 3, 1, 1, 1, QtCore.Qt.AlignTop)
                ParaLayout.addWidget(self.phi_label, 4, 0, 1, 1, QtCore.Qt.AlignTop)
                ParaLayout.addWidget(self.phi_text, 4, 1, 1, 1, QtCore.Qt.AlignTop)
                ParaLayout.addWidget(self.photon_energy_ref_label, 5, 0, 1, 3, QtCore.Qt.AlignTop)

                ParaLayout2 = QGridLayout()
                ParaLayout2.addLayout(ominc_layout, 0, 0, 1, 4, QtCore.Qt.AlignTop)
                ParaLayout2.addLayout(eloss_layout, 1, 0, 1, 4, QtCore.Qt.AlignTop)
                ParaLayout2.addWidget(self.temperature_label, 2, 0, 1, 1, QtCore.Qt.AlignTop)
                ParaLayout2.addWidget(self.temperature_text, 2, 1, 1, 1, QtCore.Qt.AlignTop)
                ParaLayout2.addWidget(self.gamma_f_label, 3, 0, 1, 1, QtCore.Qt.AlignTop)
                ParaLayout2.addWidget(self.gamma_f_text, 3, 1, 1, 1, QtCore.Qt.AlignTop)
                ParaLayout2.addWidget(self.scattering_axis_box, 4, 0, 1, 1, QtCore.Qt.AlignTop)
                HBox2 = QHBoxLayout()
                HBox2.addLayout(ParaLayout2)
                HBox2.addWidget(self.image_label)

                boxSpectraParaLayout = QVBoxLayout(self.boxSpectraPara)
                boxSpectraParaLayout.addLayout(ParaLayout_top)
                boxSpectraParaLayout.addLayout(ParaLayout)
                boxSpectraParaLayout.addLayout(HBox2)
                # boxSpectraParaLayout.addWidget(self.image_label)
                self.boxSpectraPara.setLayout(boxSpectraParaLayout)

        if "boxSpectraList":
            self.boxSpectraList = QGroupBox(self.frame)
            self.boxSpectraList.setGeometry(0, 170, 200, 605)
            self.boxSpectraList.setFixedSize(200, 605)

            self.buttonAddToSpectraList = QPushButton(self.boxSpectraList)
            self.buttonAddToSpectraList.setStyleSheet(needToSaveStyleSheet)
            self.buttonAddToSpectraList.setFixedSize(80, 32)
            self.buttonAddToSpectraList.clicked.connect(self._handleOnAddToSpectraList)

            self.buttonCheckInput = QPushButton(self.boxSpectraList)
            self.buttonCheckInput.setStyleSheet(needToSaveStyleSheet)
            self.buttonCheckInput.setFixedSize(80, 32)
            self.buttonCheckInput.clicked.connect(self._handleOnCheckInput)

            self.spectra_list = QListWidget(self.boxSpectraList)
            self.spectra_list.setFixedSize(180,480)
            self.spectra_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            def spectra_list_menu_show():
                if self.spectra_list.currentItem() is None:
                    return
                self.spectra_list_menu.exec_(QtGui.QCursor.pos())

            self.spectra_list.customContextMenuRequested.connect(spectra_list_menu_show)
            self.spectra_list.itemDoubleClicked.connect(self._handleOnImportSpectraFromList)

            self.spectra_list_menu = QMenu(self.spectra_list)

            def spectra_list_import_action():
                print("why does not work")
                self._handleOnImportSpectraFromList(self.spectra_list.currentItem())

            self.spectra_list_menu_import_action = QAction(self.spectra_list_menu)
            self.spectra_list_menu_import_action.triggered.connect(spectra_list_import_action)
            self.spectra_list_menu_delete_action = QAction(self.spectra_list_menu)
            self.spectra_list_menu_delete_action.triggered.connect(self._handleOnDeleteFromSpectraList)
            self.spectra_list_menu.addAction(self.spectra_list_menu_import_action)
            self.spectra_list_menu.addAction(self.spectra_list_menu_delete_action)

            self.spectra_list_save_button = QPushButton(self.spectra_list)
            self.spectra_list_save_button.setFixedSize(80, 32)
            self.spectra_list_save_button.clicked.connect(self._handleOnSaveSpectraList)

            self.spectra_list_load_button = QPushButton(self.spectra_list)
            self.spectra_list_load_button.setFixedSize(80, 32)
            self.spectra_list_load_button.clicked.connect(self._handleOnLoadSpectraList)

            boxSpectraListLayout = QGridLayout(self.boxSpectraList)
            boxSpectraListLayout.setAlignment(QtCore.Qt.AlignTop)
            boxSpectraListLayout.addWidget(self.buttonAddToSpectraList, 0, 0, 1, 1, QtCore.Qt.AlignTop)
            boxSpectraListLayout.addWidget(self.buttonCheckInput, 0, 1, 1, 1, QtCore.Qt.AlignTop)
            boxSpectraListLayout.addWidget(self.spectra_list, 1, 0, 2, 2, QtCore.Qt.AlignTop)
            boxSpectraListLayout.addWidget(self.spectra_list_save_button, 3, 0, 1, 1, QtCore.Qt.AlignTop)
            boxSpectraListLayout.addWidget(self.spectra_list_load_button, 3, 1, 1, 1, QtCore.Qt.AlignTop)

            self.boxSpectraList.setLayout(boxSpectraListLayout)

        if "channel_box":
            self.channel_box = QGroupBox(self.frame)
            self.channel_box.setFixedSize(955,200)

            self.combo_xas = QComboBox(self.channel_box)
            self.combo_xas.addItem("xas_1v1c_python_ed")  # 当选用某些频道但没有实现进行精确对角化则会报错,让用户先去进行相应的精确对角化
            self.combo_xas.addItem("xas_1v1c_fortran_ed")
            self.combo_xas.addItem("xas_2v1c_fortran_ed")
            self.combo_xas.setCurrentText("xas_1v1c_python_ed")
            self.combo_xas.setFixedSize(225, 42)

            self.combo_rixs = QComboBox(self.channel_box)
            self.combo_rixs.addItem("rixs_1v1c_python_ed")
            self.combo_rixs.addItem("rixs_1v1c_fortran_ed")
            self.combo_rixs.addItem("rixs_2v1c_fortran_ed")
            self.combo_rixs.setFixedSize(225, 42)

            self.spectrum_calculation_button = QPushButton(self.channel_box)
            self.spectrum_calculation_button.clicked.connect(self._handleOnSpectrumCalculation)
            self.spectrum_calculation_button.setFixedSize(200, 42)

            self.plot_button = QPushButton(self.channel_box)
            self.plot_button.setFixedSize(200, 42)
            self.plot_button.clicked.connect(self._handleOnPlotSpectrum)

            # self.plotframe_xas_label = QLabel(self.channel_box)
            # self.plotframe_xas_label.setAlignment(QtCore.Qt.AlignCenter)
            # self.plotframe_xas_label.setFixedHeight(32)
            # self.plotframe_xas_combo = QComboBox(self.channel_box)
            # self.plotframe_xas_combo.setFixedSize(62, 32)
            # self.plotframe_rixs_label = QLabel(self.channel_box)
            # self.plotframe_rixs_label.setAlignment(QtCore.Qt.AlignCenter)
            # self.plotframe_rixs_label.setFixedHeight(32)
            # self.plotframe_rixs_combo = QComboBox(self.channel_box)
            # self.plotframe_rixs_combo.setFixedSize(62, 32)
            # plotframe_combo_layout = QHBoxLayout()
            # plotframe_combo_layout.addWidget(self.plotframe_xas_label)
            # plotframe_combo_layout.addWidget(self.plotframe_xas_combo)
            # plotframe_combo_layout.addWidget(self.plotframe_rixs_label)
            # plotframe_combo_layout.addWidget(self.plotframe_rixs_combo)

            channel_box_layout = QGridLayout()
            channel_box_layout.setAlignment(QtCore.Qt.AlignTop)
            channel_box_layout.addWidget(self.combo_xas,0,1,QtCore.Qt.AlignTop)
            channel_box_layout.addWidget(self.combo_rixs,0,3,QtCore.Qt.AlignTop)
            channel_box_layout.addWidget(self.spectrum_calculation_button,1,2,QtCore.Qt.AlignTop)
            channel_box_layout.addWidget(self.plot_button,2,2,QtCore.Qt.AlignTop)
            self.channel_box.setLayout(channel_box_layout)

        if "mainLayout":
            HBOX = QHBoxLayout()
            HBOX.addWidget(self.boxSpectraList)
            HBOX.addWidget(self.boxSpectraPara)
            mainLayout = QVBoxLayout(self.frame)
            mainLayout.setAlignment(QtCore.Qt.AlignTop)
            # mainLayout中的布局
            mainLayout.setSpacing(2)
            mainLayout.addLayout(HBOX)
            mainLayout.addWidget(self.channel_box)
            self.frame.setLayout(mainLayout)
            self.scrollForSecondFrame = QScrollArea(self.frame.parent())
            self.scrollForSecondFrame.setWidget(self.frame)

    def _retranslateAll(self):
        self._retranslateTips()
        self._retranslateNames()

    def _retranslateTips(self):
        _translate = QtCore.QCoreApplication.translate
        if "boxSpectraPara":
            self.thin_text.setToolTip(
                _translate("SecondFrame_thin_text_tip","光子入射??"))
            self.thin_text.setPlaceholderText(
                _translate("SecondFrame_thin_text_sample","0.0"))
            self.thin_text.setText(
                _translate("SecondFrame_thin_text_text",""))
            self.thout_text.setToolTip(
                _translate("SecondFrame_thout_text_tip","光子出射??"))
            self.thout_text.setPlaceholderText(
                _translate("SecondFrame_thin_text_sample","0.0"))
            self.thout_text.setText(
                _translate("SecondFrame_thin_text_text",""))
            self.phi_text.setToolTip(
                _translate("SecondFrame_thout_text_tip","光子入射??"))
            self.phi_text.setPlaceholderText(
                _translate("SecondFrame_thin_text_sample","0.0"))
            self.phi_text.setText(
                _translate("SecondFrame_thin_text_text",""))
            self.photon_energy_ref_label.setToolTip(
                _translate("SecondFrame_photon_energy_ref_label_tip","从精确对角化结果得到的入射光子能量参考:"
                                                 "[min(eval_n)-min(eval_i), max(eval_n)-min(eval_i)]"))
            self.ominc_texts[0].setToolTip(
                _translate("SecondFrame_ominc_texts[1]_tip","start"))
            self.ominc_texts[1].setToolTip(
                _translate("SecondFrame_ominc_texts[1]_tip","end"))
            self.ominc_texts[2].setToolTip(
                _translate("SecondFrame_ominc_texts[2]_tip","# of steps"))
            for text in self.ominc_texts:
                text.setText(_translate("SecondFrame_ominc_text_text",""))
            self.eloss_texts[0].setToolTip(
                _translate("SecondFrame_eloss_texts[1]_tip","start"))
            self.eloss_texts[1].setToolTip(
                _translate("SecondFrame_eloss_texts[1]_tip","end"))
            self.eloss_texts[2].setToolTip(
                _translate("SecondFrame_eloss_texts[2]_tip","# of steps"))
            for text in self.eloss_texts:
                text.setText(_translate("SecondFrame_eloss_text_text",""))

            self.temperature_text.setToolTip(
                _translate("SecondFrame_temperature_text_tip","温度"))
            self.temperature_text.setPlaceholderText(
                _translate("SecondFrame_temperature_text_sample","1.0"))
            self.temperature_text.setText(
                _translate("SecondFrame_temperature_text_sample",""))
            self.gamma_f_text.setToolTip(
                _translate("SecondFrame_temperature_gamma_f_tip","gamma_f:用于rixs的计算"))
            self.gamma_f_text.setPlaceholderText(
                _translate("SecondFrame_temperature_gamma_f_sample","0.01"))
            self.gamma_f_text.setText(
                _translate("SecondFrame_temperature_gamma_f_sample",""))

        if "boxSpectraList":
            self.buttonAddToSpectraList.setToolTip(
                _translate("SecondFrame_add_to_spectra_list_button_tip", "添加到列表中"))

            self.spectra_list_menu_import_action.setToolTip(  # 这个好像没用
                _translate("SecondFrame_spectra_list_menu_import_action_tip", "导入选中元素"))
            self.spectra_list_menu_delete_action.setToolTip(  # 这个好像没用
                _translate("SecondFrame_spectra_list_menu_import_action_tip", "删除选中元素"))

            self.spectra_list_save_button.setToolTip(
                _translate("SecondFrame_spectra_list_save_button_tip", "保存列表"))
            self.spectra_list_load_button.setToolTip(
                _translate("SecondFrame_spectra_list_load_button_tip", "加载列表"))

        if "scattering_axis_box":
            for row in self.scattering_axis_texts:
                for lineEdit in row:
                    lineEdit.setToolTip(_translate("SecondFrame_scattering_axis_texts_tip",""))
                    lineEdit.setPlaceholderText(_translate("SecondFrame_scattering_axis_texts_sample","例:1.0"))
                    lineEdit.setText(_translate("SecondFrame_scattering_axis_texts_text",""))

        if "channel_box":
            self.combo_xas.setToolTip(_translate("SecondFrame_combo_tip","请选择一个XAS频道"))
            self.combo_rixs.setToolTip(_translate("SecondFrame_combo_tip","请选择一个RIXS频道"))
            self.spectrum_calculation_button.setToolTip(_translate("SecondFrame_spectrum_calculation_button_tip","计算谱型"))
            self.plot_button.setToolTip(_translate("SecondFrame_plot_button_tip","显示谱线"))

    def _retranslateNames(self):
        _translate = QtCore.QCoreApplication.translate
        if "Parameters":
            self.boxSpectraPara.setTitle(
                _translate("SecondFrame_boxSpectraPara", "Parameters"))
            self.poltype_label.setText(
                _translate("SecondFrame_poltype_label_text", "poltype"))
            self.alpha_label.setText(
                _translate("SecondFrame_alpha_label_text", "alpha:"))
            self.beta_label.setText(
                _translate("SecondFrame_alpha_label_text", "beta:"))
            self.thin_label.setText(
                _translate("SecondFrame_thin_label_label", "thin"))
            self.thout_label.setText(
                _translate("SecondFrame_thout_label_label", "thout"))
            self.phi_label.setText(
                _translate("SecondFrame_phi_label_label", "phi"))
            self.photon_energy_ref_label.setText(
                _translate("SecondFrame_photon_energy_ref_label", "incident_photon_energy_reference:"))
            self.ominc_label.setText(
                _translate("SecondFrame_ominc_label_label", "ominc_linspace"))
            self.eloss_label.setText(
                _translate("SecondFrame_eloss_label_label", "eloss_linspace"))
            self.temperature_label.setText(_translate("SecondFrame_temperature_label", "temperature"))
            self.gamma_f_label.setText(_translate("SecondFrame_gamma_f_label", "gamma_f"))

        if "boxSpectraList":
            self.boxSpectraList.setTitle(
                _translate("secondFrame_spectra_list_title", "spectra_list"))
            self.buttonAddToSpectraList.setText(
                _translate("SecondFrame_add_to_spectra_list_button_label", "ADD"))
            self.buttonCheckInput.setText(
                _translate("SecondFrame_buttonCheckInput_label", "CHECK"))

            self.spectra_list_menu_import_action.setText(  # 这个好像没用
                _translate("SecondFrame_spectra_list_menu_import_action_label", "import"))
            self.spectra_list_menu_delete_action.setText(  # 这个好像没用
                _translate("SecondFrame_spectra_list_menu_delete_action_label", "delete"))

            self.spectra_list_save_button.setText(
                _translate("SecondFrame_spectra_list_save_button_label", "SAVE"))
            self.spectra_list_load_button.setText(
                _translate("SecondFrame_spectra_list_load_button_label", "LOAD"))

        if "channel_box":
            self.channel_box.setTitle(_translate("SecondFrame_channel_box", "channel_box"))
            self.spectrum_calculation_button.setText(_translate("SecondFrame_spectrum_calculation_button_label", "spectrum_calculation"))
            self.plot_button.setText(_translate("SecondFrame_plot_button_label", "plot spectrum"))

        self.scattering_axis_box.setTitle(_translate("SecondFrame_scattering_axis_title", "scattering_axis"))

    def _textInputRestrict(self):
        self.alpha_text.setValidator(self.floatRegxValidator)
        self.beta_text.setValidator(self.floatRegxValidator)
        self.thout_text.setValidator(self.floatRegxValidator)
        self.thout_text.setValidator(self.floatRegxValidator)
        self.phi_text.setValidator(self.floatRegxValidator)
        self.ominc_texts[0].setValidator(self.floatRegxValidator)
        self.ominc_texts[1].setValidator(self.floatRegxValidator)
        self.ominc_texts[2].setValidator(self.npRegxValidator)
        self.eloss_texts[0].setValidator(self.floatRegxValidator)
        self.eloss_texts[1].setValidator(self.floatRegxValidator)
        self.eloss_texts[2].setValidator(self.npRegxValidator)

        self.temperature_text.setValidator(self.floatRegxValidator)
        self.gamma_f_text.setValidator(self.floatRegxValidator)
        for row in self.scattering_axis_texts:
            for lineEdit in row:
                lineEdit.setValidator(self.floatRegxValidator)

    def _arrangeDataInWidgets(self):
        super()._bindDataWithWidgets("alpha", self.alpha_text, self._toFloatFromText)
        super()._bindDataWithWidgets("beta", self.beta_text, self._toFloatFromText)
        super()._bindDataWithWidgets("thin", self.thin_text, self._toFloatFromText)
        super()._bindDataWithWidgets("thout", self.thout_text, self._toFloatFromText)
        super()._bindDataWithWidgets("phi", self.phi_text, self._toFloatFromText)
        super()._bindDataWithWidgets("ominc_start", self.ominc_texts[0], self._toFloatFromText)
        super()._bindDataWithWidgets("ominc_end", self.ominc_texts[1], self._toFloatFromText)
        super()._bindDataWithWidgets("ominc_steps", self.ominc_texts[2], self._toIntFromText)
        super()._bindDataWithWidgets("eloss_start", self.eloss_texts[0], self._toFloatFromText)
        super()._bindDataWithWidgets("eloss_end", self.eloss_texts[1], self._toFloatFromText)
        super()._bindDataWithWidgets("eloss_steps", self.eloss_texts[2], self._toIntFromText)

        super()._bindDataWithWidgets("temperature", self.temperature_text, self._toFloatFromText)
        super()._bindDataWithWidgets("gamma_f", self.gamma_f_text, self._toFloatFromText)
        super()._bindDataWithWidgets("scattering_axis", self.scattering_axis_texts, self._toFloatListByWidgets_2DFromText)

# 以下是与数据处理/传递相关的函数
    def _verifyValid_and_getSpectraDataFromInput(self) -> SpectraBasicData or None:
        # 如果验证通过，可以加入到列表中
        if "get parameters from input and check":
            if self.rixs_check_box.isChecked() == True:
                spectra_type = "rixs"
                poltype_in = self.combo_in.currentText()
                if poltype_in == 'isotropic':
                    self.informMsg("RIXS现无法计算isotropic类型,请选择其他类型")
                    return
                alpha = super()._getDataFromInupt("alpha")
                poltype_out = self.combo_out.currentText()
                if poltype_out == 'isotropic':
                    self.informMsg("RIXS现无法计算isotropic类型,请选择其他类型")
                    return None
                beta = super()._getDataFromInupt("beta")
                poltype = [(poltype_in, alpha/180*np.pi, poltype_out, beta/180*np.pi)]
                print(beta/180*np.pi)
                eloss_start = super()._getDataFromInupt("eloss_start")
                eloss_end = super()._getDataFromInupt("eloss_end")
                eloss_steps = super()._getDataFromInupt("eloss_steps")
                try:
                    eloss = np.linspace(eloss_start, eloss_end, eloss_steps)
                    if len(eloss) == 0:  # 往往是steps的个数设置为0
                        self.informMsg("请输入规范格式的eloss: # of steps应为正整数")
                        return None
                    if eloss[1] == eloss[0]:  # 判断eloss中的元素是否全部都相等
                        self.informMsg("请输入规范格式的eloss: start和end相同")
                        return None
                except Exception as e:
                    print(e)
                    self.informMsg("请输入规范格式的eloss")
                    return None
                gamma_f = super()._getDataFromInupt("gamma_f")
            else:
                spectra_type = "xas"
                poltype_in = self.combo_in.currentText()
                alpha = super()._getDataFromInupt("alpha")
                poltype = [(poltype_in, alpha)]
                eloss = None
                gamma_f = 0.0

            thin = super()._getDataFromInupt("thin")
            thout = super()._getDataFromInupt("thout")
            phi = super()._getDataFromInupt("phi")
            temperature = super()._getDataFromInupt("temperature")
            if temperature == 0.0:
                temperature = 0.00001  # 0是算不了的,不能当分母
            ominc_start = super()._getDataFromInupt("ominc_start")
            ominc_end = super()._getDataFromInupt("ominc_end")
            ominc_steps = super()._getDataFromInupt("ominc_steps")
            print(ominc_start, ominc_end, ominc_steps)
            try:
                ominc = np.linspace(ominc_start,ominc_end,ominc_steps)
                print(ominc)
                if len(ominc) == 0:  # 往往是steps的个数设置为0
                    self.informMsg("请输入规范格式的ominc")
                    return None
                if np.all(ominc/ominc[0]-np.zeros(len(ominc))) == 0:  # 判断ominc中的元素是否都相等
                    self.informMsg("请输入规范格式的ominc")
                    return None
            except Exception as e:
                print(e)
                self.informMsg("请输入规范格式的ominc")
                return None

            atomdata = self.atomdata_present
            if atomdata is None:
                self.informMsg("没有原子信息")
                return None
            eval_i = atomdata.ed["eval_i"]
            if eval_i is []:
                self.informMsg("eval_i not exist")
                return None
            eval_n = atomdata.ed["eval_n"]
            if eval_n is []:
                self.informMsg("eval_n not exist")
                return None
            trans_op = atomdata.ed["trans_op"]
            if trans_op is [[]]:
                self.informMsg("trans_op not exist")
                return None
            scattering_axis = super()._getDataFromInupt("scattering_axis")
            if scattering_axis == [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]:
                scattering_axis = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
            mat = np.array(scattering_axis)
            if np.all(np.dot(mat.T, mat) - np.diag([1] * 3)) != 0:
                self.informMsg("请输入实幺正矩阵scattering_axis")
                return None

        if "get SpectraBasicData":
            spectra_data = SpectraBasicData(atomdata=atomdata,
                                            spectra_type=spectra_type,
                                            poltype=poltype,
                                            thin=thin,
                                            thout=thout,
                                            phi=phi,
                                            ominc=ominc,
                                            eloss=eloss,
                                            scattering_axis=scattering_axis,
                                            temperature=temperature,
                                            gamma_f=gamma_f,
                                            spectra=self.spectra_data_present)
            print("success create an SpectraBasicData-class")

        return spectra_data

    def _getItemFromSpectraData(self, parent, spectraData:SpectraBasicData) -> QListWidgetItem:
        item = QListWidgetItem(parent)
        itemName = DataManager_spectra.getNameFromSpectraData(spectraData)
        item.setText(itemName)
        return item

    def _handleOnCheckChanged_rixs(self):
        if self.rixs_check_box.isChecked() == True:
            self.xas_check_box.setChecked(False)
            return
        else:
            self.xas_check_box.setChecked(True)

    def _handleOnCheckChanged_xas(self):
        if self.xas_check_box.isChecked() == True:
            self.rixs_check_box.setChecked(False)
            return
        else:
            self.rixs_check_box.setChecked(True)

    def _handleOnCheckInput(self):
        self._verifyValid_and_getSpectraDataFromInput()

    def _handleOnImportSpectraFromList(self, item:QListWidgetItem):
        print(item.text())
        spectra_data = self.dataManager_spectra.getSpectraDataByName(item.text())  # 能够存放在dataManager_spectra中的都是合法的数据
        print("数据获取成功")
        # 根据数据设置界面
        self.spectra_name_present = item.text()
        self.atomdata_present = spectra_data.atomdata
        self.spectra_data_present = spectra_data.spectra
        self._setInterfaceBySpectraData(spectra_data)

    def _setInterfaceBySpectraData(self, data:SpectraBasicData):  # data类型到时候需注明
        self._retranslateNames() # 先把当前界面清空一下
        spectra_type = data.spectra_type
        poltype = data.poltype
        # print(data.thin[0])
        # print(str(data.thin[0]))
        # print(data.thout)
        # print(str(data.thout))
        # print(data.phi)
        self.thin_text.setText(str(data.thin[0]))
        self.thout_text.setText(str(data.thout[0]))
        self.phi_text.setText(str(data.phi[0]))       # 打开文件发现保存的thin/thout/phi都是以元组的形式保存,如(thin,)
        print("asda")
        self.photon_energy_ref_label.setText("incident_photon_energy_reference: " + "[" + \
                                             str(min(self.atomdata_present.ed["eval_n"])-min(self.atomdata_present.ed["eval_i"])) \
                                             + ', ' + \
                                             str(max(self.atomdata_present.ed["eval_n"])-min(self.atomdata_present.ed["eval_i"])) \
                                             + ']')
        self.ominc_texts[0].setText(str(data.ominc[0]))
        self.ominc_texts[1].setText(str(data.ominc[-1]))
        self.ominc_texts[2].setText(str(len(data.ominc)))
        self.temperature_text.setText("" if data.temperature is None else str(data.temperature))
        print("so true")
        if data.scattering_axis is not None:
            for i in range(3):
                for j in range(3):
                    self.scattering_axis_texts[i][j].setText(str(data.scattering_axis[i][j]))
        print("asas")
        if spectra_type == "rixs":
            self.rixs_check_box.setChecked(True)
            self.combo_in.setCurrentText(poltype[0][0])
            self.alpha_text.setText(str(poltype[0][1]))
            self.combo_out.setCurrentText(poltype[0][2])
            self.beta_text.setText(str(poltype[0][3]))
            self.eloss_texts[0].setText(str(data.eloss[0]))
            self.eloss_texts[1].setText(str(data.eloss[-1]))
            self.eloss_texts[2].setText(str(len(data.eloss)))
            self.gamma_f_text.setText(str(data.gamma_f))
        else:
            self.xas_check_box.setChecked(True)
            self.combo_in.setCurrentText(poltype[0][0])
            self.alpha_text.setText(str(poltype[0][1]))
            self.eloss_texts[0].setText("")
            self.eloss_texts[1].setText("")
            self.eloss_texts[2].setText("")
            self.gamma_f_text.setText(str(data.gamma_f))

    def _handleOnAddToSpectraList(self):
        spectraData = self._verifyValid_and_getSpectraDataFromInput()
        if spectraData is None:
            return
        spectra_name = DataManager_spectra.getNameFromSpectraData(spectraData)
        if spectraData.spectra == {}:
            self.informMsg("请先进行谱型计算再添加到list")
            return
        if spectra_name in self.dataManager_spectra.spectraBasicDataList.keys():
            reply = self.questionMsg("已存在同名item,请问是否覆盖")
            if reply == False:
                return
        if self.dataManager_spectra.addSpectraData(spectraData) is False:
            self.informMsg("信息不完整或有误,请检查")
            return
        item = self._getItemFromSpectraData(self.spectra_list, spectraData)
        row = 0
        while row < self.spectra_list.count():
            if self.spectra_list.item(row).text() == item.text():
                break
            row += 1
        if row != self.spectra_list.count():
            self.spectra_list.takeItem(row)
            self.spectra_list.addItem(item)
            self.spectra_list.sortItems()
            self.spectra_list.setCurrentItem(item)

        self.spectra_name_present = DataManager_spectra.getNameFromSpectraData(spectraData)

# spectra数据相关
# self.boxSpectraList的某个调用函数
    def _handleOnDeleteFromSpectraList(self) -> bool:
        item = self.spectra_list.currentItem()
        if item is None:
            return False
        row = self.spectra_list.row(item)
        if item.text() == self.spectra_name_present: # 恰好删除的是当前的item,即在界面上显示的那个
            self.spectra_list.takeItem(row)
            self.spectra_list.sortItems()
            self.atomdata_present = None
            self.spectra_name_present = None
            self.spectra_data_present = {}
            self._retranslateTips()  # 再将界面上的数据抹去
        else: # 删除的不是当前的item
            self.spectra_list.takeItem(row)

        # 把dataManager中的也删了吧
        del self.dataManager_spectra.spectraBasicDataList[item.text()]
        return True

    def _handleOnLoadSpectraList(self):
        fileName, fileType = QFileDialog.getOpenFileName(self.frame, r'Load json',
                                               r'D:\Users\yg\PycharmProjects\spectra_data',
                                               r'json Files(*.json)')  # 打开程序文件所在目录是将路径换为.即可
        if fileName == "":
            self.informMsg("未选择文件")
            return
        SpectraData = DataManager_spectra.getSpectraDataFromJsonFile(fileName)
        if SpectraData == None:
            return
        spectra_name = DataManager_spectra.getNameFromSpectraData(SpectraData)
        if spectra_name in self.dataManager_spectra.spectraBasicDataList.keys():
            reply = self.questionMsg("List中已经存在相同名称,是否进行覆盖？")
            if reply == False:
                return None
        print(fileName)
        self.dataManager_spectra.addSpectraData(SpectraData)
        item = self._getItemFromSpectraData(self.spectra_list, SpectraData)
        row = 0
        while row < self.spectra_list.count():
            if self.spectra_list.item(row).text() == item.text():
                break
            row += 1
        if row != self.spectra_list.count():
            self.spectra_list.takeItem(row)
        print("here")
        self.spectra_list.addItem(item)
        self.spectra_list.sortItems()
        self.spectra_list.setCurrentItem(item)
        self.informMsg("文件成功导入到spectra_list")

    def _handleOnSaveSpectraList(self):
        item = self.spectra_list.currentItem()
        if item is None:
            self.informMsg("未选中atom_list中的item")
            return False

        fileName = item.text() + ".json"
        SpectraData = self.dataManager_spectra.spectraBasicDataList[item.text()]
        fileName_choose, filetype = QFileDialog.getSaveFileName(self.frame,
                                                                "文件保存",
                                                                "./" + fileName,  # 起始路径
                                                                "Json Files (.json)")

        spectra_data_dict = DataManager_spectra.saveSpectraDatatoJsonFile(SpectraData)
        with open(fileName_choose, 'w') as f:
            try:
                json.dump(spectra_data_dict, f, indent=4)  # 若已存在该文件,就覆盖之前
            except Exception as e:
                print(e)
                self.informMsg("保存失败")
                return
        self.informMsg("已经保存")

# self.spectrum_calculation_button的调用函数(only)
    def _handleOnSpectrumCalculation(self) -> bool:
        SpectraData = self._verifyValid_and_getSpectraDataFromInput()
        if SpectraData == None:
            return False
        self.eloss_present = SpectraData.eloss
        self.ominc_present = SpectraData.ominc
        if self.xas_check_box.isChecked() == True:
            if self.combo_xas.currentText() == "xas_1v1c_python_ed":
                ominc = np.array(SpectraData.ominc)
                gamma_c = SpectraData.atomdata.gamma_c
                thin = (SpectraData.thin)*np.pi/180  # 角度转弧度
                phi = (SpectraData.phi)*np.pi/180
                poltype = SpectraData.poltype # poltype是一个列表[],这里列表只有一个元素,是一个tuple(str,float,str,float)
                print(poltype)
                print(poltype[0][0])
                print(poltype[0][1])
                poltype = [(poltype[0][0],poltype[0][1])]
                temperature = SpectraData.temperature
                scattering_axis = SpectraData.scattering_axis
                if 'xas_1v1c_python_ed' in SpectraData.spectra.keys():
                    reply = self.questionMsg("当前数据类中已经含有xas_1v1c_python_ed spectra,是否进行覆盖")
                    if reply == False:
                        return False
                xas_1v1c_spectra = xas_1v1c_py(eval_i=SpectraData.atomdata.ed["eval_i"],
                                               eval_n=SpectraData.atomdata.ed["eval_n"],
                                               trans_op=SpectraData.atomdata.ed["trans_op"],
                                               ominc=ominc, gamma_c=gamma_c,
                                               thin=thin, phi=phi, pol_type=poltype,
                                               gs_list=SpectraData.atomdata.ed["gs_list"],
                                               temperature=temperature, scatter_axis=scattering_axis)
                SpectraData.spectra['xas_1v1c_python_ed'] = xas_1v1c_spectra
                print(xas_1v1c_spectra)
                self.spectra_data_present['xas_1v1c_python_ed'] = xas_1v1c_spectra
                print("谱型计算完成")
            return True

        else:
            if self.combo_rixs.currentText() == "rixs_1v1c_python_ed":
                ominc = np.array(SpectraData.ominc)
                eloss = np.array(SpectraData.eloss)
                gamma_c = SpectraData.atomdata.gamma_c
                gamma_f = SpectraData.gamma_f
                thin = (SpectraData.thin)*np.pi/180
                thout = (SpectraData.thout)*np.pi/180
                phi = (SpectraData.phi)*np.pi/180
                poltype = SpectraData.poltype
                temperature = SpectraData.temperature
                scatter_axis = SpectraData.scattering_axis
                print(SpectraData.atomdata.ed["trans_op"].shape)
                if 'rixs_1v1c_python_ed' in SpectraData.spectra.keys():
                    reply = self.questionMsg("当前数据类中已经含有rixs_1v1c_python_ed spectra,是否进行覆盖")
                    if reply == False:
                        return False
                try:
                    spectra = rixs_1v1c_py(eval_i=SpectraData.atomdata.ed["eval_i"],
                                           eval_n=SpectraData.atomdata.ed["eval_n"],
                                           trans_op=SpectraData.atomdata.ed["trans_op"],
                                           ominc=ominc, eloss=eloss, gamma_c=gamma_c, gamma_f=gamma_f,
                                           thin=thin, thout=thout, phi=phi, pol_type=poltype,
                                           gs_list=SpectraData.atomdata.ed["gs_list"],
                                           temperature=temperature, scatter_axis=scatter_axis)
                    self.spectra_data_present[self.combo_rixs.currentText()] = spectra
                    return True
                except Exception as e:
                    print(e)
                    self.informMsg("RIXS谱计算失败")
                    return False

# self.plot_button的调用函数(only)
    def _handleOnPlotSpectrum(self):
        if self.spectra_data_present.keys() == []:
            self.informMsg("请先计算谱型")
            return

        if self.xas_check_box.isChecked() == True:
            which = self.combo_xas.currentText()
            print(which)
            if which not in self.spectra_data_present.keys():
                self.informMsg("没有spectra data,请先进行计算")
            else:
                try:
                    ax2 = plt.subplot(1, 1, 1)
                    plt.grid()
                    plt.plot(self.ominc_present, self.spectra_data_present[which], '-')
                    plt.xlabel(r'Incident Energy (eV)')
                    plt.ylabel(r'XAS Intensity (a.u.)')
                    plt.title(r'(b) map of XAS')
                    plt.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9, wspace=0.2, hspace=0.3)
                    plt.show()
                except Exception as e:
                    print(e)
                    self.informMsg("作图失败")
        else:
            which = self.combo_rixs.currentText()
            if which not in self.spectra_data_present.keys():
                self.informMsg("没有spectra data,请先进行计算")
            else:
                try:
                    print((self.spectra_data_present[which]).shape)
                    plt.subplot(1, 1, 1)
                    plt.imshow(np.sum(self.spectra_data_present[which], axis=2),
                               extent=[min(self.eloss_present), max(self.eloss_present), min(self.ominc_present), max(self.ominc_present)],
                               origin='lower', aspect='auto', cmap='rainbow', interpolation='gaussian')
                    plt.xlabel(r'Energy loss (eV)')
                    plt.ylabel(r'Incident Energy (eV)')
                    plt.title(r'(c) map of RIXS')
                    plt.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9, wspace=0.2, hspace=0.3)
                    plt.show()
                except Exception as e:
                    print(e)
                    self.informMsg("作图失败")

if __name__ == '__main__':
    app=QApplication(sys.argv)
    demo=SecondFrame()
    demo.scrollForSecondFrame.show()
    sys.exit(app.exec_())

                
                


