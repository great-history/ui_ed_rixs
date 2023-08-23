# Qt5 version 5.15.2
# PyQt5 version 5.15.2
# python version 3.8

from FirstFrame import *
from SecondFrame import *
import sys


class OwnApplication:
    def __init__(self):
        self.data = {} # 存放ed的计算结果,方便第一个页面调用到第二个页面
        self.widgetsWithData = {}  # 以一个名字(str)为key，value为(控件,解析方式)，可以从控件中获取输入
        self.mainWindow = QMainWindow()
        self.mainWidget = QWidget(self.mainWindow)  # main window
        self.frames = []  # 存放各个页面
        self.curFrameIndex = 0  # 当前页面索引
        QtGui.QFontDatabase.addApplicationFont("./resource/*.otf")
        self._setFont()
        self._arrangeUI()

    def _setupMainWidget(self):
        self.mainWidget.setMinimumHeight(960)
        self.mainWidget.setFixedWidth(1280)

        self.frames.append(FirstFrame(parent= None, width=1280, height=840))
        self.frames.append(SecondFrame(parent = None, width=1280, height=840))

        self.goToNextFrameBtn = QPushButton(self.mainWidget)
        self.goToNextFrameBtn.setStyleSheet(  # test
            '''
            QPushButton{
                height: 64px;
                width: 64px;
                border-width: 0px;
                border-radius: 10px;
                color: #57579C;
                background-color: #E9EBAE;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F1B99A;
            }
            QPushButton:pressed {
                background-color: #79CDEB;
            }
            QPushButton#cancel{
                background-color: gray ;
            }
            ''')
        self.goToNextFrameBtn.clicked.connect(self._handleOnGotoNextPage)

        self.goToPreviousFrameBtn = QPushButton(self.mainWidget)
        self.goToPreviousFrameBtn.setStyleSheet(  # test
            '''
            QPushButton{
                height: 81px;
                width: 81px;
                border-width: 0px;
                border-radius: 10px;
                color: #57579C;
                background-color: #E9EBAE;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F1B99A;
            }
            QPushButton:pressed {
                background-color: #79CDEB;
            }
            QPushButton#cancel{
                background-color: gray ;
            }
            ''')
        self.goToPreviousFrameBtn.clicked.connect(self._handleOnGotoPreviousPage)

    def _setFont(self):
        self.mainWidget.setFont(QtGui.QFont("SourceHanSansSC-Medium"))

    def _retranslateAll(self):
        self._retranslateTips()
        self._retranslateNames()

    def _retranslateTips(self):
        _translate = QtCore.QCoreApplication.translate

        self.goToNextFrameBtn.setToolTip(
            _translate("FirstFrame_goToNextFrameBtn_tip", "next page"))
        self.goToPreviousFrameBtn.setToolTip(
            _translate("SecondFrame_goToPreviousFrameBtn_tip", "previous page"))

    def _retranslateNames(self):
        _translate = QtCore.QCoreApplication.translate
        self.mainWidget.setWindowTitle(
            _translate("MainWindow_title", "RIXS/XAS_Simulation"))  # title
        self.goToNextFrameBtn.setText(
            _translate("FirstFrame_goToNextFrameBtn_label", "NEXT"))
        self.goToPreviousFrameBtn.setText(
            _translate("SecondFrame_goToPreviousFrameBtn_label", "PREVIOUS"))

    def _arrangeUI(self):
        self._setupMainWidget()
        self._retranslateAll()

        if "mainWidget":
            self.topLayout = QGridLayout(self.mainWidget)
            self.topLayout.setAlignment(QtCore.Qt.AlignTop)

            self.frameContain = QHBoxLayout()  # 存放一个页面
            self.topLayout.addLayout(self.frameContain, 0, 0, 1, 20)
            self.topLayout.addWidget(self.goToNextFrameBtn, 1, 0, 1, 10, QtCore.Qt.AlignCenter)
            self.topLayout.addWidget(self.goToPreviousFrameBtn, 1, 10, 1, 10, QtCore.Qt.AlignCenter)
            self.topLayout.setRowStretch(0, 10)
            self.topLayout.setRowStretch(1, 1)

            self.mainWidget.setLayout(self.topLayout)
            self.curFrameIndex = 0  # 当前页面是第一页
            self._addFrameToMainWindow()

        if "mainWindow":
            self._setupMainWindow()

    def _setupMainWindow(self):
        self.mainWindow.setMinimumHeight(960)
        self.mainWindow.setFixedWidth(1280)
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

        file_menu = self.mainWindow.menuBar().addMenu("File")  # 在menuBar上添加File菜单
        quit_action = create_action("Quit", slot=self.mainWindow.close, shortcut="Ctrl+Q", tip="Close the application")
        add_actions(file_menu, (quit_action,None))

        def on_about_firstpage():
            msg = """ 
                            Perform ED for the case of two atomic shells, one valence plus one Core
                shell with pure Python solver.
                For example, for Ni-:math:`L_3` edge RIXS, they are 3d valence and 2p core shells.
                 It will use scipy.linalag.eigh to exactly diagonalize both the initial and intermediate
                Hamiltonians to get all the eigenvalues and eigenvectors, and the transition operators
                will be built in the many-body eigenvector basis.
                The outputs are:
                eval_i: 1d float array ———— The eigenvalues of the initial Hamiltonian.
                eval_n: 1d float array ———— The eigenvalues of the intermediate Hamiltonian.
                trans_op: 3d complex array ———— The transition operators in the eigenstates basis.
                they will be used in the second page calculation.
                """
            QMessageBox.about(self.mainWindow, "About the FirstPage", msg.strip())  # #

        def on_about_firstpage_atom_basic_info():  # help_menu中的功能,用来介绍该界面已经实现的功能
            msg = """ 
        shell_name: tuple of two strings
        Names of valence and core shells. The 1st (2nd) string in the tuple is for the
        valence (core) shell.
        - The 1st string can only be 's', 'p', 't2g', 'd', 'f',
        - The 2nd string can be 's', 'p', 'p12', 'p32', 'd', 'd32', 'd52',
          'f', 'f52', 'f72'.
        For example: shell_name=('d', 'p32') indicates a :math:`L_3` edge transition from
        core :math:`p_{3/2}` shell to valence :math:`d` shell.
        shell_level: tuple of two float numbers
        Energy level of valence (1st element) and core (2nd element) shells.
        They will be set to zero if not provided.
        v_soc: tuple of two float numbers
        Spin-orbit coupling strength of valence electrons, for the initial (1st element)
        and intermediate (2nd element) Hamiltonians.
        They will be set to zero if not provided.
        c_soc: a float number
        Spin-orbit coupling strength of core electrons.
        v_noccu: int number
        Number of electrons in valence shell.
               """
            QMessageBox.about(self.mainWindow, "About the FirstPage Parameters", msg.strip())  # #

        def on_about_firstpage_slater_parameters():  # help_menu中的功能,用来介绍该界面已经实现的功能
                msg = """ 
            slater: tuple of two lists
            Slater integrals for initial (1st list) and intermediate (2nd list) Hamiltonians.
            The order of the elements in each list should be like this:
             [FX_vv, FX_vc, GX_vc, FX_cc],
            where X are integers with ascending order, it can be X=0, 2, 4, 6 or X=1, 3, 5.
            One can ignore all the continuous zeros at the end of the list.
            For example, if the full list is: [F0_dd, F2_dd, F4_dd, 0, F2_dp, 0, 0, 0, 0], one can
            just provide [F0_dd, F2_dd, F4_dd, 0, F2_dp]
            All the Slater integrals will be set to zero if slater=None.
                   """
                QMessageBox.about(self.mainWindow, "About the FirstPage Parameters", msg.strip())  # #

        def on_about_firstpage_other_parameters():
            msg = """
            ext_B: tuple of three float numbers
            Vector of external magnetic field with respect to global :math:`xyz`-axis.
            They will be set to zero if not provided.
        on_which: string
            Apply Zeeman exchange field on which sector. Options are 'spin', 'orbital' or 'both'.
        v_cfmat: 2d complex array
            Crystal field splitting Hamiltonian of valence electrons. The dimension and the orbital
            order should be consistent with the type of valence shell.
            They will be zeros if not provided.
        v_othermat: 2d complex array
            Other possible Hamiltonian of valence electrons. The dimension and the orbital order
            should be consistent with the type of valence shell.
            They will be zeros if not provided.
        loc_axis: 3*3 float array
            The local axis with respect to which local orbitals are defined.
            - x: local_axis[:,0],
            - y: local_axis[:,1],
            - z: local_axis[:,2].
            It will be an identity matrix if not provided.
        verbose: int
            Level of writting data to files. Hopping matrices, Coulomb tensors, eigvenvalues
            will be written if verbose > 0."""
            QMessageBox.about(self.mainWindow, "About the FirstPage Parameters", msg.strip())  # #

        def on_about_secondpage():  # help_menu中的功能,用来介绍该界面已经实现的功能
            msg = """ 
                Calculate XAS for the case of one valence shell plus one core shell with Python solver.
                This solver is only suitable for small size of Hamiltonian, typically the dimension of 
                both initial and intermediate Hamiltonian are smaller than 10,000.
               """
            QMessageBox.about(self.mainWindow, "About the FirstPage Parameters", msg.strip())  # #

        def on_about_secondpage_parameters():  # help_menu中的功能,用来介绍该界面已经实现的功能
            msg = """ 
                ominc: 1d float array
                    Incident energy of photon.
                gamma_c: a float number or a 1d float array with the same shape as ominc.
                    The core-hole life-time broadening factor. It can be a constant value
                    or incident energy dependent.
                thin: float number
                    The incident angle of photon (in radian).
                phi: float number
                    Azimuthal angle (in radian), defined with respect to the
                    :math:`x`-axis of the scattering axis: scatter_axis[:,0].
                pol_type: list of tuples
                    Type of polarization, options can be:
                    - ('linear', alpha), linear polarization, where alpha is the angle between the
                      polarization vector and the scattering plane.
                    - ('left', 0), left circular polarization.
                    - ('right', 0), right circular polarization.
                    - ('isotropic', 0). isotropic polarization.
                    It will set pol_type=[('isotropic', 0)] if not provided.
                gs_list: 1d list of ints
                    The indices of initial states which will be used in XAS calculations.
                    It will set gs_list=[0] if not provided.
                temperature: float number
                    Temperature (in K) for boltzmann distribution.
                scatter_axis: 3*3 float array
                    The local axis defining the scattering plane. The scattering plane is defined in
                    the local :math:`zx`-plane.
                    local :math:`x`-axis: scatter_axis[:,0]
                    local :math:`y`-axis: scatter_axis[:,1]
                    local :math:`z`-axis: scatter_axis[:,2]
                    It will be set to an identity matrix if not provided.
                    """
            QMessageBox.about(self.mainWindow, "About the FirstPage Parameters", msg.strip())  # #

        help_menu = self.mainWindow.menuBar().addMenu("Help")
        about_action_firstpage = create_action("About_FirstPage", slot = on_about_firstpage,
                                                shortcut = 'F2', tip = 'About the demo')

        about_action_firstpage_atom_basic_info = create_action("About_FirstPage_Atom_Basic_Info",
                                                               slot=on_about_firstpage_atom_basic_info,
                                                               shortcut='F2', tip='About the demo')
        about_action_firstpage_slater_parameters = create_action("About_FirstPage_Slater_Parameters",
                                                                 slot=on_about_firstpage_slater_parameters,
                                                                 shortcut='F3', tip='About the demo')
        about_action_firstpage_other_parameters = create_action("About_FirstPage_Other_Parameters",
                                                                slot=on_about_firstpage_other_parameters,
                                                                shortcut='F4', tip='About the demo')
        about_action_secondpage = create_action("About_SecondPage", slot=on_about_secondpage, shortcut='F5', tip='About the demo')
        about_action_secondpage_parameters = create_action("About_SecondPage_Parameters", slot=on_about_secondpage_parameters,
                                                           shortcut='F6', tip='About the demo')
        add_actions(help_menu, (about_action_firstpage,None,
                                about_action_firstpage_atom_basic_info, None,
                                about_action_firstpage_slater_parameters, None,
                                about_action_firstpage_other_parameters, None,
                                about_action_secondpage, None,
                                about_action_secondpage_parameters))

        # mainWindow的status Bar的设定
        self.mainWindow.statusBar().showMessage("")

    def _addFrameToMainWindow(self):
        self.frameContain.addWidget(self.frames[self.curFrameIndex].getFrame())  # 在主界面加入一个页面

    def _removeFrameFromMainWindow(self):
        self.frameContain.removeWidget(self.frames[self.curFrameIndex].getFrame())
        self.frames[self.curFrameIndex].getFrame().setParent(None) # 这句话必须加上,否则不能previous

    # 为什么这里的return似乎不起作用？？非常奇怪
    def _handleOnGotoNextPage(self):
        next_p = self.curFrameIndex+1
        if next_p >= len(self.frames):  # 没有下一页了,这里len(self.frame) = 2,此时self.curFrameIndex = 1
            self.informMsg("已经是最后一页了")
            return

        if self.frames[self.curFrameIndex]._verifyValid_and_getAtomDataFromInput() == None:
            if self.questionMsg("数据不完整,是否继续跳到下一页？？") == False:
                return
        if self.frames[self.curFrameIndex].eval_i_present is None or \
                self.frames[self.curFrameIndex].eval_n_present is None or \
                self.frames[self.curFrameIndex].trans_op_present is None:
            if self.questionMsg("尚未进行精确对角化,是否仍要继续跳到下一页？？") == False:
                return
        self._removeFrameFromMainWindow()
        self.curFrameIndex += 1
        self._addFrameToMainWindow()
        try:
            self.frames[self.curFrameIndex].atomdata_present = self.frames[self.curFrameIndex-1].\
                                            dataManager.atomBasicDataList[self.frames[self.curFrameIndex-1].atom_name_present]
        except Exception as e:
            print(e)
        reply = self.questionMsg("是否刷新之前的界面？？")
        if reply == True:
            try:
                self.frames[self.curFrameIndex]._retranslateTips()  # 刷新第二个页面
                self.frames[self.curFrameIndex].photon_energy_ref_label.setText("incident_photon_energy_reference: " + "[" + \
                                                 str(min(self.frames[self.curFrameIndex].atomdata_present.ed["eval_n"])-
                                                     min(self.frames[self.curFrameIndex].atomdata_present.ed["eval_i"])) \
                                                 + ', ' + \
                                                 str(max(self.frames[self.curFrameIndex].atomdata_present.ed["eval_n"])
                                                     -min(self.frames[self.curFrameIndex].atomdata_present.ed["eval_i"])) \
                                                 + ']')
            except Exception as e:
                print(e)

    def _handleOnGotoPreviousPage(self):
        next_p = self.curFrameIndex-1
        if next_p <= -1:  # 没有下一页了
            self.informMsg("已经是第一页了")
            return
        self._removeFrameFromMainWindow()
        self.curFrameIndex -= 1
        self._addFrameToMainWindow()

    def informMsg(self, msg: str):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("inform")
        msgBox.setText(msg)
        msgBox.exec_()  # 模态

    def questionMsg(self, msg: str):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("确认框")
        reply = QMessageBox.information(msgBox,  # 使用infomation信息框
                                        "标题",
                                        msg,
                                        QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            return True
        if reply == QMessageBox.No:
            return False
        msgBox.exec_()  # 模态


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # app.setStyleSheet(open('./custom/styleSheet.qss', encoding='utf-8').read())
    myapp = OwnApplication()
    myapp.mainWindow.show()
    app.exec_()
