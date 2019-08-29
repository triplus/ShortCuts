# ShortCuts overlay for FreeCAD
# Copyright (C) 2016, 2017, 2018 triplus @ FreeCAD
#
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA


def shortCuts():
    """
    ShortCuts overlay for FreeCAD.
    """
    import platform
    from PySide import QtGui
    from PySide import QtCore
    import FreeCADGui as Gui
    import FreeCAD as App
    from ShortCutsLocator import delayTimer

    macOS = False

    if platform.system() == "Darwin":
        macOS = True
    else:
        pass

    mw = Gui.getMainWindow()
    mdi = mw.findChild(QtGui.QMdiArea)
    paramGet = App.ParamGet("User parameter:BaseApp/ShortCuts/User")

    iconSvgNone = """<svg
        xmlns="http://www.w3.org/2000/svg" height="64" width="64">
         <rect height="64" width="64" fill="none" />
        </svg>"""

    iconSvgLocal = """<svg
        xmlns="http://www.w3.org/2000/svg" height="64" width="64">
         <circle cx="32" cy="32" r="20"
          stroke="black" stroke-width="2" fill="#008000" />
        </svg>"""

    iconSvgGlobal = """<svg
        xmlns="http://www.w3.org/2000/svg" height="64" width="64">
         <circle cx="32" cy="32" r="20"
          stroke="black" stroke-width="2" fill="#edd400" />
        </svg>"""

    iconSvgLG = """<svg
        xmlns="http://www.w3.org/2000/svg" height="64" width="64">
         <circle cx="44" cy="44" r="18"
          stroke="black" stroke-width="2" fill="#edd400" />
         <circle cx="20" cy="20" r="18"
          stroke="black" stroke-width="2" fill="#008000" />
        </svg>"""

    iconSvgPref = """<svg
        xmlns="http://www.w3.org/2000/svg" height="64" width="64">
         <rect height="7" width="44" y="11" x="10" fill="#888a85" />
         <rect height="7" width="44" y="28.5" x="10" fill="#888a85" />
         <rect height="7" width="44" y="46" x="10" fill="#888a85" />
        </svg>"""

    iconPixNone = QtGui.QPixmap()
    iconPixNone.loadFromData(str.encode(iconSvgNone))

    iconPixLocal = QtGui.QPixmap()
    iconPixLocal.loadFromData(str.encode(iconSvgLocal))

    iconPixGlobal = QtGui.QPixmap()
    iconPixGlobal.loadFromData(str.encode(iconSvgGlobal))

    iconPixLG = QtGui.QPixmap()
    iconPixLG.loadFromData(str.encode(iconSvgLG))

    iconPixPref = QtGui.QPixmap()
    iconPixPref.loadFromData(str.encode(iconSvgPref))

    iconFreeCAD = QtGui.QIcon.fromTheme("freecad")

    if iconFreeCAD.isNull():
        iconFreeCAD = QtGui.QIcon(iconPixNone)
    else:
        pass

    styleEdit = """
        QLineEdit {
            border: 1px outset silver;
        }"""

    styleButtonPref = """
        QToolButton {
            border: 1px solid #1e1e1e;
            background-color: #3c3c3c;
        }"""

    styleContainer = """
        QMenu {
            background: transparent
        }"""

    def xpmParse(i):
        """
        Parse and prepare workbench icon in XPM format.
        """
        icon = []

        for a in ((((i
                     .split('{', 1)[1])
                    .rsplit('}', 1)[0])
                   .strip())
                  .split("\n")):
            icon.append((a
                         .split('"', 1)[1])
                        .rsplit('"', 1)[0])

        return icon

    def wbIcon(i):
        """
        Create and return workbench icon.
        """
        if str(i.find("XPM")) != "-1":
            icon = QtGui.QIcon(QtGui.QPixmap(xpmParse(i)))
        else:
            icon = QtGui.QIcon(QtGui.QPixmap(i))

        if icon.isNull():
            icon = iconFreeCAD
        else:
            pass

        return icon

    def actionList():
        """
        Create a dictionary of unique actions.
        """
        actions = {}
        duplicates = []

        for i in mw.findChildren(QtGui.QAction):
            if i.objectName() and i.text():
                if i.objectName() in actions:
                    if i.objectName() not in duplicates:
                        duplicates.append(i.objectName())
                    else:
                        pass
                else:
                    actions[i.objectName()] = i
            else:
                pass

        for d in duplicates:
            del actions[d]

        return actions

    def keyDelay():
        """
        Set timer interval.
        Start key delay timer.
        """
        timer.stop()

        if paramGet.GetInt("Delay"):
            timer.setInterval(paramGet.GetInt("Delay"))
        else:
            timer.setInterval(1000)

        timer.start()

    def onDelay():
        """
        Run the command on timer timeout.
        """
        action = None
        text = edit.text().upper()

        if text in currentCombinations:
            action = currentCombinations[text]
        else:
            pass

        if action and action.isEnabled():
            setVisibility(mode=1)
            action.trigger()
        else:
            pass

    timer = delayTimer()
    timer.setParent(mw)
    timer.setSingleShot(True)
    timer.timeout.connect(onDelay)

    class ShortCutsEdit(QtGui.QLineEdit):
        """
        ShortCuts main line edit.
        """
        def __init__(self, parent=None):
            super(ShortCutsEdit, self).__init__(parent)

        def focusOutEvent(self, e):
            """
            Hide line edit when focus is lost.
            """
            setVisibility()

        def keyPressEvent(self, e):
            """
            Hide line edit on ESC key.
            Show all available completions on down key.
            """
            if e.key() == QtCore.Qt.Key_Escape:
                setVisibility()
            elif e.key() == QtCore.Qt.Key_Down:
                edit.clear()
                completer.setCompletionPrefix("")
                completer.complete()
            else:
                QtGui.QLineEdit.keyPressEvent(self, e)

    def globalShortcuts():
        """
        Create a dictionary of available global shortcuts.
        """
        currentGlobal.clear()
        index = paramGet.GetGroup("Global shortcuts").GetString("IndexList")
        index = index.split(",")

        for i in index:
            try:
                command = (paramGet
                           .GetGroup("Global shortcuts")
                           .GetGroup(i)
                           .GetString("command")
                           .decode("UTF-8"))
            except AttributeError:
                command = (paramGet
                           .GetGroup("Global shortcuts")
                           .GetGroup(i)
                           .GetString("command"))
            try:
                shortcut = (paramGet
                            .GetGroup("Global shortcuts")
                            .GetGroup(i)
                            .GetString("shortcut")
                            .decode("UTF-8"))
            except AttributeError:
                shortcut = (paramGet
                            .GetGroup("Global shortcuts")
                            .GetGroup(i)
                            .GetString("shortcut"))

            if command and shortcut:
                currentGlobal[command] = shortcut
            else:
                index.remove(i)
                paramGet.GetGroup("Global shortcuts").RemGroup(i)

        string = ",".join(index)
        paramGet.GetGroup("Global shortcuts").SetString("IndexList", string)

    def localShortcuts():
        """
        Create a dictionary of available local shortcuts.
        """
        currentLocal.clear()

        if Gui.activeWorkbench().MenuText:
            activeWB = Gui.activeWorkbench().MenuText
        else:
            activeWB = None

        if activeWB:
            index = paramGet.GetGroup(activeWB).GetString("IndexList")
            index = index.split(",")

            for i in index:
                try:
                    command = (paramGet
                               .GetGroup(activeWB)
                               .GetGroup(i)
                               .GetString("command")
                               .decode("UTF-8"))
                except AttributeError:
                    command = (paramGet
                               .GetGroup(activeWB)
                               .GetGroup(i)
                               .GetString("command"))
                try:
                    shortcut = (paramGet
                                .GetGroup(activeWB)
                                .GetGroup(i)
                                .GetString("shortcut")
                                .decode("UTF-8"))
                except AttributeError:
                    shortcut = (paramGet
                                .GetGroup(activeWB)
                                .GetGroup(i)
                                .GetString("shortcut"))

                if command and shortcut:
                    currentLocal[command] = shortcut
                else:
                    index.remove(i)
                    paramGet.GetGroup(activeWB).RemGroup(i)

            string = ",".join(index)
            paramGet.GetGroup(activeWB).SetString("IndexList", string)
        else:
            pass

    def itemList(activeWB=None):
        """
        Create and return an alphabetically sorted list
        of table widget items.
        """
        items = []
        names = []
        applyShortcuts()
        actions = actionList()

        for i in actions:
            text = actions[i].text()
            text = text.replace("&", "")
            names.append([text, actions[i].objectName()])

        names = sorted(names)

        sort = []

        for i in names:
            sort.append(i[1])

        for i in sort:
            if i in actions:
                command = QtGui.QTableWidgetItem()
                text = actions[i].text()
                text = text.replace("&", "")
                command.setText(text)
                command.setToolTip(actions[i].toolTip())
                command.setFlags(QtCore.Qt.ItemIsEnabled)

                if actions[i].icon():
                    command.setIcon(actions[i].icon())
                else:
                    command.setIcon(QtGui.QIcon(iconPixNone))

                shortcut = QtGui.QTableWidgetItem()

                if (i in currentLocal and
                        i in currentGlobal and
                        activeWB != "Global shortcuts"):
                    shortcut.setText(currentLocal[i])
                    shortcut.setIcon(QtGui.QIcon(iconPixLG))
                    shortcut.setToolTip(activeWB +
                                        ": " +
                                        currentLocal[i] +
                                        "    Global: " +
                                        currentGlobal[i])
                elif i in currentLocal and activeWB != "Global shortcuts":
                    shortcut.setText(currentLocal[i])
                    shortcut.setIcon(QtGui.QIcon(iconPixLocal))
                    shortcut.setToolTip(activeWB + ": " + currentLocal[i])
                elif i in currentGlobal:
                    shortcut.setText(currentGlobal[i])
                    shortcut.setIcon(QtGui.QIcon(iconPixGlobal))
                    shortcut.setToolTip("Global: " + currentGlobal[i])
                else:
                    pass

                shortcut.setData(32, actions[i].objectName())

                items.append([command, shortcut])
            else:
                pass

        return items

    def groupNum(activeWB, command):
        """
        Search for existing command group index number.
        Define new command group index number if one does not exist yet.
        """
        indexNumber = None
        index = paramGet.GetGroup(activeWB).GetString("IndexList")
        index = index.split(",")

        for i in index:
            try:
                if (paramGet
                        .GetGroup(activeWB)
                        .GetGroup(i)
                        .GetString("command")
                        .decode("UTF-8") == command):
                    indexNumber = i
                else:
                    pass
            except AttributeError:
                if (paramGet
                        .GetGroup(activeWB)
                        .GetGroup(i)
                        .GetString("command") == command):
                    indexNumber = i
                else:
                    pass

        if not indexNumber:
            x = 1
            maxNum = 999

            while str(x) in index and x < maxNum:
                x += 1
            else:
                indexNumber = str(x)

            if indexNumber and int(indexNumber) != maxNum:
                index.append(indexNumber)
                (paramGet
                 .GetGroup(activeWB)
                 .SetString("IndexList", ",".join(index)))
            else:
                indexNumber = None
        else:
            pass

        return indexNumber

    def deleteGroup(activeWB, command):
        """
        Delete the command data and corresponding group from the database.
        """
        index = paramGet.GetGroup(activeWB).GetString("IndexList")
        index = index.split(",")

        for i in index:
            try:
                if (paramGet
                        .GetGroup(activeWB)
                        .GetGroup(i)
                        .GetString("command")
                        .decode("UTF-8") == command):
                    index.remove(i)
                    paramGet.GetGroup(activeWB).RemGroup(i)
                    (paramGet
                     .GetGroup(activeWB)
                     .SetString("IndexList", ",".join(index)))
                else:
                    pass
            except AttributeError:
                if (paramGet
                        .GetGroup(activeWB)
                        .GetGroup(i)
                        .GetString("command") == command):
                    index.remove(i)
                    paramGet.GetGroup(activeWB).RemGroup(i)
                    (paramGet
                     .GetGroup(activeWB)
                     .SetString("IndexList", ",".join(index)))
                else:
                    pass

    model = QtGui.QStandardItemModel()
    model.setColumnCount(1)

    def modelData():
        """
        Model data for completer.
        Create a dictionary of unique shortcut combinations.
        """
        duplicates = []
        applyShortcuts()

        actions = actionList()
        currentCombinations.clear()

        if Gui.activeWorkbench().MenuText:
            activeWB = Gui.activeWorkbench().MenuText
        else:
            activeWB = None

        row = 0
        model.clear()

        if activeWB:
            for command in currentLocal:
                if command in actions:
                    item = QtGui.QStandardItem()

                    shortcut = currentLocal[command]

                    text = (shortcut +
                            "  " +
                            (actions[command].text()).replace("&", ""))

                    item.setText(text)

                    if actions[command].icon():
                        item.setIcon(actions[command].icon())
                    else:
                        item.setIcon(QtGui.QIcon(iconPixNone))

                    item.setToolTip(actions[command].toolTip())
                    item.setEnabled(actions[command].isEnabled())
                    item.setData(actions[command].objectName(), 32)

                    model.setItem(row, 0, item)
                    row += 1

                    if shortcut in currentCombinations:
                        if shortcut not in duplicates:
                            duplicates.append(shortcut)
                        else:
                            pass
                    else:
                        currentCombinations[shortcut] = actions[command]

            for command in currentGlobal:
                if command in actions:
                    item = QtGui.QStandardItem()

                    shortcut = currentGlobal[command]

                    text = (shortcut +
                            "  " +
                            (actions[command].text()).replace("&", ""))

                    item.setText(text)

                    if actions[command].icon():
                        item.setIcon(actions[command].icon())
                    else:
                        item.setIcon(QtGui.QIcon(iconPixNone))

                    item.setToolTip(actions[command].toolTip())
                    item.setEnabled(actions[command].isEnabled())
                    item.setData(actions[command].objectName(), 32)

                    model.setItem(row, 0, item)
                    row += 1

                    if shortcut in currentCombinations:
                        if shortcut not in duplicates:
                            duplicates.append(shortcut)
                        else:
                            pass
                    else:
                        currentCombinations[shortcut] = actions[command]

            for d in duplicates:
                del currentCombinations[d]

    completer = QtGui.QCompleter()
    completer.setModel(model)
    completer.setMaxVisibleItems(16)
    completer.popup().setMinimumWidth(220)
    completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)

    def onHighlighted():
        """
        Stop the timer on down key.
        Hide preferences button.
        Increase line edit size.
        """
        timer.stop()
        buttonPref.hide()
        edit.setMinimumWidth(220)

    completer.highlighted.connect(onHighlighted)

    def onCompleter(modelIndex):
        """
        Run selected command on completion.
        Set visibility.
        """
        actions = actionList()

        index = completer.completionModel().mapToSource(modelIndex)
        item = model.itemFromIndex(index)
        data = item.data(32)

        if data in actions:
            actions[data].trigger()
        else:
            pass

        setVisibility(mode=1)

    completer.activated[QtCore.QModelIndex].connect(onCompleter)

    edit = ShortCutsEdit()
    edit.hide()
    edit.setCompleter(completer)
    edit.setStyleSheet(styleEdit)
    edit.setGeometry(10, 10, 40, 24)
    edit.setAlignment(QtCore.Qt.AlignHCenter)
    edit.setContextMenuPolicy(QtCore.Qt.NoContextMenu)

    def onTextEdited(text):
        """
        Start the timer on last key.
        Restore default line edit size.
        """
        if text:
            if paramGet.GetBool("EnableDelay"):
                keyDelay()
            else:
                pass
        else:
            edit.setMinimumWidth(40)
            edit.setGeometry(10, 10, 40, 24)
            buttonPref.show()

    edit.textEdited.connect(onTextEdited)

    def onReturnPressed():
        """
        Clear or hide line edit after enter key is pressed.
        """
        if edit.text():
            edit.clear()
        else:
            setVisibility()

    edit.returnPressed.connect(onReturnPressed)

    buttonPref = QtGui.QToolButton()
    buttonPref.hide()
    buttonPref.setGeometry(60, 10, 24, 24)
    buttonPref.setStyleSheet(styleButtonPref)

    actionPref = QtGui.QAction(buttonPref)
    actionPref.setIcon(QtGui.QIcon(iconPixPref))

    buttonPref.setDefaultAction(actionPref)

    def onPreferences():
        """
        Delete existing preferences dialog if it exists.
        Open new preferences dialog.
        """
        for i in mw.findChildren(QtGui.QDialog):
            if i.objectName() == "ShortCuts":
                i.deleteLater()
            else:
                pass

        dialog = prefDialog()
        dialog.show()

    buttonPref.triggered.connect(onPreferences)

    currentLocal = {}
    currentGlobal = {}
    currentCombinations = {}

    if macOS:
        menu = QtGui.QMenu(mw)
        menu.setParent(mw)
        menu.setMinimumWidth(236)
        menu.setMinimumHeight(36)
        menu.setGeometry(0, 0, 236, 36)
        menu.setStyleSheet(styleContainer)
        menu.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        menu.setWindowFlags(menu.windowFlags() | QtCore.Qt.FramelessWindowHint)

        edit.setParent(menu)
        buttonPref.setParent(menu)
    else:
        edit.setParent(mdi)
        buttonPref.setParent(mdi)

    def setVisibility(mode=0):
        """
        Restore default line edit size.
        Show or hide ShortCuts.
        """
        mdi = mw.findChild(QtGui.QMdiArea)

        edit.setMinimumWidth(40)
        edit.setGeometry(10, 10, 40, 24)

        if macOS:
            if menu.isVisible() or mode == 1:
                timer.stop()
                edit.clear()
                menu.hide()
                completer.popup().hide()
                mdi.setFocus()
            else:
                modelData()
                edit.clear()
                menu.popup(QtCore.QPoint(mw.geometry().x() + mdi.pos().x(),
                                         mw.geometry().y() + mdi.pos().y()))
                edit.setVisible(True)
                buttonPref.setVisible(True)
                edit.setFocus()
        else:
            if edit.isVisible() or mode == 1:
                timer.stop()
                edit.clear()
                edit.hide()
                completer.popup().hide()
                buttonPref.hide()
                mdi.setFocus()
            else:
                modelData()
                edit.show()
                edit.clear()
                buttonPref.show()
                edit.setFocus()

    invokeKey = QtGui.QAction(mw)
    invokeKey.setAutoRepeat(False)
    invokeKey.setText("Invoke shortcuts overlay")
    invokeKey.setObjectName("InvokeShortCutsOverlay")
    invokeKey.setShortcut(QtGui.QKeySequence("Shift+Q"))
    invokeKey.triggered.connect(setVisibility)

    mw.addAction(invokeKey)

    def applyShortcuts():
        """
        Apply global and local shortcuts.
        """
        globalShortcuts()
        localShortcuts()

    def prefDialog():
        """
        Preferences dialog.
        """

        class DelaySpinBox(QtGui.QSpinBox):
            """
            Delay SpinBox focus behaviour.
            """
            def __init__(self, parent=None):
                super(DelaySpinBox, self).__init__(parent)

            def keyPressEvent(self, e):
                """
                Set focus (button Done) on Return key pressed.
                """
                if e.key() == QtCore.Qt.Key_Return:
                    buttonDone.setFocus()
                else:
                    QtGui.QSpinBox.keyPressEvent(self, e)

        def comboBox():
            """
            Workbench selector combo box.
            """
            cBox = QtGui.QComboBox()
            cBox.setMinimumWidth(220)

            listWB = Gui.listWorkbenches()
            listWBSorted = sorted(listWB)
            listWBSorted.reverse()

            for i in listWBSorted:
                if i in listWB:
                    try:
                        icon = wbIcon(Gui.listWorkbenches()[i].Icon)
                    except AttributeError:
                        icon = iconFreeCAD

                    cBox.insertItem(0, icon, listWB[i].MenuText)

            cBox.insertSeparator(0)
            icon = iconFreeCAD
            cBox.insertItem(0, icon, "Global shortcuts")
            cBox.setCurrentIndex(0)

            activeWB = Gui.activeWorkbench().MenuText

            for count in range(cBox.count()):

                if cBox.itemText(count) == activeWB:
                    cBox.setCurrentIndex(count)
                else:
                    pass

            def onCurrentIndexChanged():
                """
                Activate workbench on selection.
                """
                listWB = Gui.listWorkbenches()

                for i in listWB:
                    if listWB[i].MenuText == cBox.currentText():
                        Gui.activateWorkbench(i)
                    else:
                        pass

                updateStats()
                updateTable()

            cBox.currentIndexChanged.connect(onCurrentIndexChanged)

            return cBox

        def tableWidget():
            """
            Table of commands and shortcuts.
            """
            table = QtGui.QTableWidget(0, 2)
            table.verticalHeader().setVisible(False)
            table.setHorizontalHeaderLabels(["Command", "Shortcut"])
            try:
                table.horizontalHeader().setResizeMode(QtGui
                                                       .QHeaderView
                                                       .Stretch)
            except AttributeError:
                table.horizontalHeader().setSectionResizeMode(QtGui
                                                              .QHeaderView
                                                              .Stretch)

            def onItemChanged(item):
                """
                Save shortcut.
                Delete command from database if no shortcut is provided.
                """
                activeWB = cBox.currentText()

                if item.text() and activeWB and item.data(32):
                    try:
                        indexNumber = groupNum(activeWB,
                                               item.data(32).encode("UTF-8"))
                    except TypeError:
                        indexNumber = groupNum(activeWB,
                                               item.data(32))

                    if indexNumber:
                        try:
                            (paramGet
                             .GetGroup(activeWB)
                             .GetGroup(indexNumber)
                             .SetString("command",
                                        item.data(32).encode("UTF-8")))
                        except TypeError:
                            (paramGet
                             .GetGroup(activeWB)
                             .GetGroup(indexNumber)
                             .SetString("command", item.data(32)))
                        try:
                            (paramGet
                             .GetGroup(activeWB)
                             .GetGroup(indexNumber)
                             .SetString("shortcut",
                                        item.text().upper().encode("UTF-8")))
                        except TypeError:
                            (paramGet
                             .GetGroup(activeWB)
                             .GetGroup(indexNumber)
                             .SetString("shortcut",
                                        item.text().upper()))
                    else:
                        print("ShortCuts: " + activeWB + " database is full.")
                elif activeWB and item.data(32):
                    try:
                        deleteGroup(activeWB, item.data(32).encode("UTF-8"))
                    except TypeError:
                        deleteGroup(activeWB, item.data(32))
                else:
                    pass

                applyShortcuts()
                updateTable()
                updateStats()

            table.itemChanged.connect(onItemChanged)

            return table

        def updateTable():
            """
            Update table items.
            """
            items = itemList(cBox.currentText())

            table.blockSignals(True)
            table.setRowCount(len(items))

            row = 0

            for i in items:
                table.setItem(row, 0, i[0])
                table.setItem(row, 1, i[1])
                row += 1

            table.blockSignals(False)

        def updateStats():
            """
            Update statistic information for current number of shortcuts.
            """
            activeWB = cBox.currentText()

            if activeWB == "<none>":
                activeWB = "None"
            else:
                pass

            if activeWB == "Global shortcuts":
                stats.setText("<br>" +
                              "Global: " +
                              "<b>" + str(len(currentGlobal)) + "</b>")
            else:
                stats.setText(activeWB +
                              ": " +
                              "<b>" + str(len(currentLocal)) + "</b>" +
                              "<br>" +
                              "Global: " +
                              "<b>" + str(len(currentGlobal)) + "</b>")

        def onCheckDelay():
            """
            Save enable or disable autorun command state.
            """
            if checkDelay.isChecked():
                paramGet.SetBool("EnableDelay", 1)
                spinDelay.setEnabled(True)
            else:
                paramGet.SetBool("EnableDelay", 0)
                spinDelay.setEnabled(False)

        def onSpinDelay(i):
            """
            Save delay time setting.
            """
            paramGet.SetInt("Delay", i)

        dialog = QtGui.QDialog(mw)
        dialog.resize(800, 450)
        dialog.setWindowTitle("ShortCuts")
        dialog.setObjectName("ShortCuts")

        cBox = comboBox()
        cBox.setParent(dialog)

        table = tableWidget()
        table.setParent(dialog)

        stats = QtGui.QLabel()
        stats.setAlignment(QtCore.Qt.AlignRight)

        home = QtGui.QWidget(dialog)
        layoutHome = QtGui.QVBoxLayout()
        home.setLayout(layoutHome)

        settings = QtGui.QWidget(dialog)
        layoutSettings = QtGui.QVBoxLayout()
        settings.setLayout(layoutSettings)

        stack = QtGui.QStackedWidget(dialog)
        stack.insertWidget(0, home)
        stack.insertWidget(1, settings)

        buttonClose = QtGui.QPushButton("Close", home)
        buttonSettings = QtGui.QPushButton("Settings", home)
        buttonDone = QtGui.QPushButton("Done", settings)

        labelDelay = QtGui.QLabel("Key delay:", dialog)
        checkDelay = QtGui.QCheckBox(dialog)
        checkDelay.stateChanged.connect(onCheckDelay)

        spinDelay = DelaySpinBox()
        spinDelay.setParent(dialog)
        spinDelay.setSingleStep(50)
        spinDelay.setRange(200, 9999)
        spinDelay.setSuffix(" ms")
        spinDelay.valueChanged.connect(onSpinDelay)

        layout = QtGui.QVBoxLayout()
        dialog.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(stack)

        layoutScope = QtGui.QHBoxLayout()
        layoutScope.addWidget(cBox)
        layoutScope.addStretch(1)
        layoutScope.addWidget(stats)

        layoutBottom = QtGui.QHBoxLayout()
        layoutBottom.addWidget(buttonSettings)
        layoutBottom.addStretch(1)
        layoutBottom.addWidget(buttonClose)

        layoutHome.insertLayout(0, layoutScope)
        layoutHome.addWidget(table)
        layoutHome.insertLayout(2, layoutBottom)

        layoutSettingsBottom = QtGui.QHBoxLayout()
        layoutSettingsBottom.addWidget(buttonDone)
        layoutSettingsBottom.addStretch(1)

        layoutDelay = QtGui.QHBoxLayout()
        layoutDelay.insertWidget(0, labelDelay)
        layoutDelay.addStretch(1)
        layoutDelay.insertWidget(2, checkDelay)

        layoutDelaySpin = QtGui.QHBoxLayout()
        layoutDelaySpin.addStretch(1)
        layoutDelaySpin.insertWidget(1, spinDelay)

        groupTrigger = QtGui.QGroupBox("Autorun command")

        layoutTrigger = QtGui.QVBoxLayout()
        groupTrigger.setLayout(layoutTrigger)

        layoutTrigger.insertLayout(0, layoutDelay)
        layoutTrigger.insertLayout(1, layoutDelaySpin)

        layoutSettings.addWidget(groupTrigger)
        layoutSettings.addStretch(1)
        layoutSettings.insertLayout(2, layoutSettingsBottom)

        def onAccepted():
            """
            Close dialog on button close.
            """
            dialog.done(1)

        buttonClose.clicked.connect(onAccepted)

        def onFinished():
            """
            Delete dialog on close.
            """
            dialog.deleteLater()

        dialog.finished.connect(onFinished)

        def onSettings():
            """
            Change to settings on button settings.
            """
            stack.setCurrentIndex(1)

        buttonSettings.clicked.connect(onSettings)

        def onDone():
            """
            Change to home on button done.
            """
            stack.setCurrentIndex(0)
            buttonClose.setFocus()

        buttonDone.clicked.connect(onDone)

        def prefDefaults():
            """
            Set preferences default values.
            """

            if paramGet.GetBool("EnableDelay"):
                checkDelay.setChecked(True)
                spinDelay.setEnabled(True)
            else:
                checkDelay.setChecked(False)
                spinDelay.setEnabled(False)

            if paramGet.GetInt("Delay"):
                spinDelay.setValue(paramGet.GetInt("Delay"))
            else:
                spinDelay.setValue(1000)

            updateTable()
            updateStats()

        prefDefaults()

        return dialog

    def onStart():
        """Start shortcuts."""

        start = False
        try:
            mw.workbenchActivated
            start = True
        except AttributeError:
            pass

        if start:
            startTimer.stop()
            startTimer.deleteLater()
            mw.workbenchActivated.connect(applyShortcuts)
            import ShortCuts_Gui

    def onPreStart():
        """"""
        if App.Version()[1] < "17":
            onStart()
        else:
            if mw.property("eventLoop"):
                onStart()

    startTimer = delayTimer()
    startTimer.timeout.connect(onPreStart)
    startTimer.start(500)


shortCuts()
