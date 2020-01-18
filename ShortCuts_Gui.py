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

"""Shortcuts manager for FreeCAD"""


import os
from PySide import QtGui
from PySide import QtCore
import FreeCADGui as Gui
import FreeCAD as App


scheme = {}
actions = {}
defaults = {}
localUser = {}
globalUser = {}
mw = Gui.getMainWindow()
verify = QtGui.QAction(mw)
p = App.ParamGet("User parameter:BaseApp/ShortCutsDev")
path = os.path.dirname(__file__) + "/Resources/icons/"


def wbIcon(i):
    """Create workbench icon."""
    if str(i.find("XPM")) != "-1":
        try:
            icon = []
            for a in ((((i
                         .split('{', 1)[1])
                        .rsplit('}', 1)[0])
                       .strip())
                      .split("\n")):
                icon.append((a
                             .split('"', 1)[1])
                            .rsplit('"', 1)[0])
            icon = QtGui.QIcon(QtGui.QPixmap(icon))
        except:
            icon = QtGui.QIcon(":/icons/freecad")
    else:
        icon = QtGui.QIcon(QtGui.QPixmap(i))
    if icon.isNull():
        icon = QtGui.QIcon(":/icons/freecad")
    return icon


def itemIcon(command):
    """Shortcut item icon indicator."""
    if command in localUser and command in defaults and defaults[command]:
        icon = QtGui.QIcon(path + os.sep + "ShortCuts_LocalGlobal.svg")
    elif command in localUser and command in globalUser:
        icon = QtGui.QIcon(path + os.sep + "ShortCuts_LocalGlobal.svg")
    elif command in localUser:
        icon = QtGui.QIcon(path + os.sep + "ShortCuts_Local.svg")
    else:
        icon = QtGui.QIcon(path + os.sep + "ShortCuts_Global.svg")
    return icon


def updateActions():
    """Create and update a dictionary of unique actions."""
    actions.clear()
    duplicates = []
    for i in mw.findChildren(QtGui.QAction):
        name = i.objectName()
        if name and i.text() and "," not in name:
            if name in actions:
                if name not in duplicates:
                    duplicates.append(name)
            else:
                actions[name] = i
    for d in duplicates:
        del actions[d]


def hasGroup(source=None, workbench=None):
    """Reduce creation of empty database groups."""
    if not all([source, workbench]):
        return False
    if not p.HasGroup(source):
        return False
    if not p.GetGroup(source).HasGroup(workbench):
        return False
    return True


def splitIndex(source=None, workbench=None):
    """Create and return an index list."""
    index = []
    if not all([source, workbench]):
        return index
    if not hasGroup(source, workbench):
        return index
    index = p.GetGroup(source).GetGroup(workbench).GetString("index")
    if index:
        index = index.split(",")
    return index


def resetShortcuts():
    """Reset shortcuts to defaults."""
    for s in scheme:
        if s in defaults and s in actions:
            actions[s].setShortcut(QtGui.QKeySequence(defaults[s]))
        elif s in actions:
            actions[s].setShortcut(QtGui.QKeySequence(""))
        else:
            pass


def applyShortcuts():
    """Save defaults and apply shortcuts from scheme."""
    for a in actions:
        if a not in defaults:
            defaults[a] = actions[a].shortcut().toString()
    for s in scheme:
        if s in actions:
            actions[s].setShortcut(QtGui.QKeySequence(scheme[s]))


def printShortcuts():
    """Print active shortcuts to the report view"""
    for a in mw.findChildren(QtGui.QAction):
        if a.shortcut().toString():
            if a.text():
                text = a.text()
            else:
                text = "N/A"
            App.Console.PrintMessage(text.replace("&", "") +
                                     "\t" +
                                     a.shortcut().toString() +
                                     "\n")


def updateDict(source, wb, d):
    """Update dictionary."""
    if not hasGroup(source, wb):
        return False
    index = splitIndex(source, wb)
    base = p.GetGroup(source).GetGroup(wb)
    for i in index:
        g = base.GetGroup(i)
        command = g.GetString("command")
        # Py2/Py3
        try:
            shortcut = g.GetString("shortcut").decode("UTF-8")
        except AttributeError:
            shortcut = g.GetString("shortcut")
        if command and shortcut:
            d[command] = shortcut
            if command not in scheme:
                scheme[command] = shortcut
    return True


def update(workbench):
    """Update shortcuts and apply them."""
    updateActions()
    resetShortcuts()

    scheme.clear()
    localUser.clear()
    updateDict("User", workbench, localUser)
    globalUser.clear()
    if workbench != "GlobalShortcuts":
        updateDict("User", "GlobalShortcuts", globalUser)

    applyShortcuts()


def onWorkbench():
    """Update shortcuts on workbench activated."""
    workbench = Gui.activeWorkbench().__class__.__name__
    update(workbench)


def comboBox():
    """Workbench selector combo box."""
    cBox = QtGui.QComboBox()
    cBox.setMinimumWidth(220)

    listWB = Gui.listWorkbenches()
    listWBSorted = sorted(listWB)
    listWBSorted.reverse()

    for i in listWBSorted:
        try:
            icon = wbIcon(Gui.listWorkbenches()[i].Icon)
        except AttributeError:
            icon = QtGui.QIcon(":/icons/freecad")
        cBox.insertItem(0,
                        icon,
                        listWB[i].MenuText,
                        listWB[i].__class__.__name__)

    cBox.insertSeparator(0)
    icon = QtGui.QIcon(":/icons/freecad")
    cBox.insertItem(0, icon, "Global shortcuts", "GlobalShortcuts")
    cBox.setCurrentIndex(0)

    activeWB = Gui.activeWorkbench().__class__.__name__
    for count in range(cBox.count()):
        if cBox.itemData(count) == activeWB:
            cBox.setCurrentIndex(count)
    return cBox


def searchLine(table):
    """Search line for preferences."""
    search = QtGui.QLineEdit()

    def onSearch(text):
        """Show or hide commands on search."""
        for n in range(table.rowCount()):
            t = table.item(n, 0).text()
            if t and text and text.lower() in t.lower():
                table.setRowHidden(n, False)
            elif text:
                table.setRowHidden(n, True)
            else:
                table.setRowHidden(n, False)

    search.textEdited.connect(onSearch)
    return search


def tableWidget():
    """Table for commands and shortcuts."""
    table = QtGui.QTableWidget(0, 2)
    table.verticalHeader().setVisible(False)
    table.setHorizontalHeaderLabels(["Command", "Shortcut"])
    # Qt4/Qt5
    try:
        table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
    except AttributeError:
        table.horizontalHeader().setSectionResizeMode(QtGui.
                                                      QHeaderView.
                                                      Stretch)
    return table


def updateTable(cBox, table):
    """Update table widget items."""
    workbench = cBox.itemData(cBox.currentIndex())
    update(workbench)
    names = []
    for i in actions:
        text = actions[i].text()
        text = text.replace("&", "")
        names.append([text, actions[i].objectName()])
    names = sorted(names)
    sort = []
    for i in names:
        sort.append(i[1])
    table.blockSignals(True)
    table.clearContents()
    table.setRowCount(len(actions))
    row = 0
    for i in sort:
        command = QtGui.QTableWidgetItem()
        text = actions[i].text()
        text = text.replace("&", "")
        command.setText(text)
        command.setToolTip(actions[i].toolTip())
        command.setFlags(QtCore.Qt.ItemIsEnabled)
        if actions[i].icon():
            command.setIcon(actions[i].icon())
        else:
            command.setIcon(QtGui.QIcon(":/icons/freecad"))
        shortcut = QtGui.QTableWidgetItem()
        text = actions[i].shortcut().toString()
        if text:
            shortcut.setText(text)
            shortcut.setIcon(QtGui.QIcon(itemIcon(i)))
        shortcut.setData(32, i)
        table.setItem(row, 0, command)
        table.setItem(row, 1, shortcut)
        row += 1
    table.blockSignals(False)


def database(source=None, workbench=None, commands=None):
    """Manage shortcuts database access."""
    current = {}
    index = splitIndex(source, workbench)
    if index:
        base = p.GetGroup(source).GetGroup(workbench)
        for i in index:
            command = base.GetGroup(i).GetString("command")
            # Py2/Py3
            try:
                shortcut = (base
                            .GetGroup(i)
                            .GetString("shortcut")
                            .decode("UTF-8"))
            except AttributeError:
                shortcut = base.GetGroup(i).GetString("shortcut")
            if command and shortcut:
                current[command] = shortcut
        p.GetGroup(source).RemGroup(workbench)
    if commands:
        for cmd in commands:
            if commands[cmd]:
                current[cmd] = commands[cmd]
            elif cmd in current:
                del current[cmd]
            else:
                pass
    n = 1
    index = []
    base = p.GetGroup(source).GetGroup(workbench)
    for i in current:
        index.append(str(n))
        g = base.GetGroup(str(n))
        g.SetString("command", i)
        # Py2/Py3
        try:
            g.SetString("shortcut", current[i].encode("UTF-8"))
        except TypeError:
            g.SetString("shortcut", current[i])
        n += 1
    base.SetString("index", ",".join(index))
    if not splitIndex(source, workbench):
        p.GetGroup(source).RemGroup(workbench)


def preferences():
    """ShortCuts preferences dialog."""
    def onAccepted():
        """Close dialog on button close."""
        dia.done(1)

    def onFinished():
        """Delete dialog on close."""
        dia.deleteLater()
        onWorkbench()

    # Dialog
    dia = QtGui.QDialog(mw)
    dia.setModal(True)
    dia.resize(900, 500)
    dia.setWindowTitle("Shortcuts preferences")
    dia.finished.connect(onFinished)
    layout = QtGui.QVBoxLayout()
    dia.setLayout(layout)

    # Button close
    btnClose = QtGui.QPushButton("Close")
    btnClose.setToolTip("Close the preferences dialog")
    btnClose.clicked.connect(onAccepted)

    # Button print
    btnPrint = QtGui.QPushButton("Print")
    btnPrint.setToolTip("Print active shortcuts to the report view")
    btnPrint.clicked.connect(printShortcuts)

    loBtn = QtGui.QHBoxLayout()
    loBtn.addWidget(btnPrint)
    loBtn.addStretch()
    loBtn.addWidget(btnClose)

    # Combo
    cBox = comboBox()

    # Table widget
    table = tableWidget()

    # Search
    search = searchLine(table)

    # Functions and connections
    def onItemChanged(item):
        """Save shortcut."""
        workbench = cBox.itemData(cBox.currentIndex())
        command = item.data(32)
        shortcut = item.text()
        verify.setShortcut(QtGui.QKeySequence(shortcut))
        shortcut = verify.shortcut().toString()
        verify.setShortcut(QtGui.QKeySequence(""))
        database("User", workbench, commands={command: shortcut})
        update(workbench)
        table.blockSignals(True)
        if shortcut:
            item.setText(shortcut)
            item.setIcon(itemIcon(command))
        elif command in scheme and scheme[command]:
            item.setText(scheme[command])
            item.setIcon(itemIcon(command))
        elif command in defaults and defaults[command]:
            item.setText(defaults[command])
            item.setIcon(itemIcon(command))
        else:
            item.setText("")
            item.setIcon(QtGui.QIcon())
        table.blockSignals(False)

    table.itemChanged.connect(onItemChanged)

    def onCurrentIndexChanged():
        """Activate workbench on selection."""
        workbench = cBox.itemData(cBox.currentIndex())
        wbList = Gui.listWorkbenches()
        for i in wbList:
            if wbList[i].__class__.__name__ == workbench:
                Gui.activateWorkbench(workbench)
        updateTable(cBox, table)

    cBox.currentIndexChanged.connect(onCurrentIndexChanged)

    updateTable(cBox, table)

    # Layout
    loTop = QtGui.QHBoxLayout()
    loTop.addWidget(cBox)
    loTop.addWidget(search)

    layout.insertLayout(0, loTop)
    layout.addWidget(table)
    layout.insertLayout(2, loBtn)

    btnClose.setDefault(True)
    btnClose.setFocus()

    return dia


def onPreferences():
    """Open the preferences dialog."""
    dia = preferences()
    dia.show()


def accessoriesMenu():
    """Add ShortCuts preferences to accessories menu."""
    pref = QtGui.QAction(mw)
    pref.setText("Shortcuts")
    pref.setObjectName("ShortCuts")
    pref.triggered.connect(onPreferences)
    try:
        import AccessoriesMenu
        AccessoriesMenu.addItem("ShortCuts")
    except ImportError:
        a = mw.findChild(QtGui.QAction, "AccessoriesMenu")
        if a:
            a.menu().addAction(pref)
        else:
            mb = mw.menuBar()
            action = QtGui.QAction(mw)
            action.setObjectName("AccessoriesMenu")
            action.setIconText("Accessories")
            m = QtGui.QMenu()
            action.setMenu(m)
            m.addAction(pref)

            def addMenu():
                """Add accessories menu to the menu bar."""
                mb.addAction(action)
                action.setVisible(True)

            addMenu()
            mw.workbenchActivated.connect(addMenu)


def onStart():
    """Start shortcuts."""
    start = False
    try:
        mw.workbenchActivated
        start = True
    except AttributeError:
        pass

    if start:
        timer.stop()
        timer.deleteLater()
        onWorkbench()
        accessoriesMenu()
        mw.workbenchActivated.connect(onWorkbench)


def onPreStart():
    """Improve start reliability and maintain FreeCAD 0.16 support."""
    if App.Version()[1] < "17":
        onStart()
    else:
        if mw.property("eventLoop"):
            onStart()


timer = QtCore.QTimer()
timer.timeout.connect(onPreStart)
timer.start(500)
