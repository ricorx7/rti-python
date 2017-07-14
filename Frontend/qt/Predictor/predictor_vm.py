import datetime
from predictor_view import Ui_RoweTechPredictor
from subsystem_view import Ui_Subsystem
from subsystem_vm import SubsystemVM
from PyQt5.QtWidgets import QWidget

import ADCP.Predictor.DataStorage as DS
import ADCP.AdcpCommands as Commands

class PredictorVM(Ui_RoweTechPredictor):
    """
    ADCP Terminal using WAMP.
    """

    def __init__(self, parent):
        Ui_RoweTechPredictor.__init__(self)
        self.setupUi(parent)
        self.parent = parent

        # Calculated results
        self.calc_power = 0.0
        self.calc_data = 0.0
        self.calc_num_batt = 0.0

        # Connect the buttons
        self.addSubsystemButton.clicked.connect(self.add_subsystem)

        self.tabSubsystem.setTabsClosable(True)
        self.tabSubsystem.clear()
        self.tabSubsystem.tabCloseRequested.connect(self.tab_close_requested)
        #self.calculateButton.clicked.connect(self.calculate)
        self.saveCommandsButton.clicked.connect(self.save_to_file)

        # Recalculate when value changes
        self.deploymentDurationSpinBox.valueChanged.connect(self.valueChanged)
        self.ceiDoubleSpinBox.valueChanged.connect(self.valueChanged)

        # Create the list of subsystems
        self.init_list()

        # Command file
        self.cepo_list = []
        self.command_file = []

        # Run initial Calculate
        self.calculate()

    def init_list(self):
        # Add item to combobox.  Set the userData to subsystem code
        self.subsystemComboBox.addItem("2 - 1200kHz", "2")
        self.subsystemComboBox.addItem("3 - 600kHz", "3")
        self.subsystemComboBox.addItem("4 - 300kHz", "4")
        self.subsystemComboBox.addItem("6 - 1200kHz 45 degree offset", "6")
        self.subsystemComboBox.addItem("7 - 600kHz 45 degree offset", "7")
        self.subsystemComboBox.addItem("8 - 300kHz 45 degree offset", "8")
        self.subsystemComboBox.addItem("A - 1200kHz Vertical", "A")
        self.subsystemComboBox.addItem("B - 600kHz Vertical", "B")
        self.subsystemComboBox.addItem("C - 300kHz Vertical", "C")
        self.subsystemComboBox.addItem("D - 150kHz Vertical", "D")
        self.subsystemComboBox.addItem("E - 75kHz Vertical", "E")

    def add_subsystem(self):
        """
        Add a tab for the given subsystem.
        :return:
        """
        ss = self.subsystemComboBox.itemData(self.subsystemComboBox.currentIndex())

        # Create the subsystem view
        # Add it to the Tab
        ssUI = Ui_Subsystem()
        ssVM = SubsystemVM(self.tabSubsystem, self, ss)
        self.tabSubsystem.addTab(ssVM, ss)

        # Add subsystem to CEPO
        self.cepo_list.append(ss)

        # Recalculate
        self.calculate()


    def tab_close_requested(self, index):
        """
        Remove the tab.
        :param index: Index of the tab.
        :return:
        """
        self.tabSubsystem.removeTab(index)

        # Remove from the CEPO list
        del self.cepo_list[index]

        # Recalculate
        self.calculate()

    def valueChanged(self, value):
        """
        Use this to handle a value changed.
        :param value: New value.
        :return:
        """
        self.calculate()

    def calculate(self):
        """
        Calculate the new prediction results.
        :return:
        """
        # Clear the results
        self.calc_power = 0.0
        self.calc_data = 0.0
        self.calc_num_batt = 0.0

        for tab in range(self.tabSubsystem.count()):
            self.tabSubsystem.widget(tab).calculate()
            # print(self.tabSubsystem.widget(tab).cwpblDoubleSpinBox.value())

            # Accuulate the values
            self.calc_data += self.tabSubsystem.widget(tab).calc_data
            self.calc_num_batt += self.tabSubsystem.widget(tab).calc_num_batt
            self.calc_power += self.tabSubsystem.widget(tab).calc_power


        # Update the display
        self.powerLabel.setText(str(round(self.calc_power, 2)) + " watts")
        self.powerLabel.setStyleSheet("font-weight: bold; color: blue")
        self.numBatteriesLabel.setText(str(round(self.calc_num_batt, 2)) + " batteries")
        self.numBatteriesLabel.setStyleSheet("font-weight: bold; color: blue")
        self.dataUsageLabel.setText(str(DS.bytes_2_human_readable(self.calc_data)))
        self.dataUsageLabel.setStyleSheet("font-weight: bold; color: blue")

        # Update the command file
        self.update_command_file()


    def update_command_file(self):
        self.commandFileTextBrowser.clear()

        self.commandFileTextBrowser.append("CDEFAULT")

        # CEPO List
        cepo = "CEPO "
        for ss in self.cepo_list:
            cepo += ss
        self.commandFileTextBrowser.append(cepo)

        self.commandFileTextBrowser.append("CEI " + Commands.sec_to_hmss(self.ceiDoubleSpinBox.value()))

        for tab in range(self.tabSubsystem.count()):
            ss_cmd_list = self.tabSubsystem.widget(tab).get_cmd_list()
            for ss_cmd in ss_cmd_list:
                self.commandFileTextBrowser.append(ss_cmd.to_str(tab))

        self.commandFileTextBrowser.append("CSAVE")
        self.commandFileTextBrowser.append("START")

    def save_to_file(self):

        # Create a new file name based off date and time
        file_name = datetime.datetime.now().strftime("%Y%m%d%H%M%S_RTI_CFG.txt")

        file = open(file_name, 'w')
        file.write(self.commandFileTextBrowser.toPlainText())
        file.close()