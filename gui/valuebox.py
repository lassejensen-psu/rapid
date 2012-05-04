from PyQt4.QtCore import Qt, pyqtSignal
from PyQt4.QtGui import QGroupBox, QDoubleSpinBox, QComboBox, QLabel, \
                        QHBoxLayout, QVBoxLayout, QStandardItem
from PyQt4.Qwt5 import QwtSlider
from numpy.testing import assert_approx_equal

class ValueBox(QGroupBox):
    '''A box that sets values'''

    def __init__(self, parent, title, boxID, model):
        '''Initiallize the box and what is inside it'''
        super(QGroupBox, self).__init__(parent)
        self.setTitle(title)
        self._boxID = boxID
        self._createWidgets(model)
        self._makeConnections()
        self._initUI()
        self.paramIndx = self._boxID

    def _createWidgets(self, model):
        '''Create the widgets contained in this box'''

        # Min range spin box
        self.valueMinSpinBox = QDoubleSpinBox(self)
        self.valueMinSpinBox.setDecimals(2)

        # Max range spin box
        self.valueMaxSpinBox = QDoubleSpinBox(self)
        self.valueMaxSpinBox.setDecimals(2)

        # Set up the spin box that allows the user to choose a value manually
        self.valueSpinBox = QDoubleSpinBox(self)
        self.valueSpinBox.setDecimals(4)

        # Set up the slider that allows the user to choose a value visually
        self.valueSlider = QwtSlider(self, Qt.Horizontal)
        self.valueSlider.setMinimumWidth(500)

        # Store the underlying model
        self.model = model

        # Add the parameter chooser
        self.paramChooser = QComboBox(self)
        self.paramChooser.setModel(self.model)
        self.paramChooser.setSizeAdjustPolicy(QComboBox.AdjustToContents)

    def _makeConnections(self):
        'Connect the contained widgets to each other and set initial values'

        # If the value spinbox changes, check the bounds of the slider range
        self.valueSpinBox.valueChanged.connect(self.changeSliderVal)

        # If the slider moves, change the spinbox
        self.valueSlider.valueChanged.connect(self.valueSpinBox.setValue)

        # Change the slider range bounds if the bounds spinboxes change
        self.valueMinSpinBox.valueChanged.connect(self.changeValueMin)
        self.valueMaxSpinBox.valueChanged.connect(self.changeValueMax)

        # If the underlying model's data changes, reflect this in the sliders
        # and spin boxes
        self.model.valueChanged.connect(self.updateValue)
        self.model.maxValueChanged.connect(self.updateMax)
        self.model.minValueChanged.connect(self.updateMin)

        # If the combo box is changed, send out a signal
        self.paramChooser.currentIndexChanged.connect(self.changeParameter)

    def _initUI(self):
        '''Place the widgets in the proper locations in the box'''

        # Set up the location of all the contained widgets
        rangeLayout = QHBoxLayout()
        rangeLayout.addWidget(QLabel('Parameters'))
        rangeLayout.addWidget(self.paramChooser)
        rangeLayout.addStretch()
        rangeLayout.addWidget(QLabel('Min Value'))
        rangeLayout.addWidget(self.valueMinSpinBox)
        rangeLayout.addWidget(QLabel('Max Value'))
        rangeLayout.addWidget(self.valueMaxSpinBox)
        pickerLayout = QHBoxLayout()
        pickerLayout.addWidget(QLabel('Variable Value'))
        pickerLayout.addWidget(self.valueSpinBox)
        pickerLayout.addWidget(self.valueSlider)

        # Lay out these layouts
        valuePickerLayout = QVBoxLayout()
        valuePickerLayout.addLayout(rangeLayout)
        valuePickerLayout.addLayout(pickerLayout)
        self.setLayout(valuePickerLayout)

    #######
    # SLOTS
    #######

    def changeValueMin(self, min):
        '''If the slider minimum value changes, adjust the slider range
        and store the value in the model'''
        try:
            assert_approx_equal(self.valueMinSpinBox.value(), min)
        except AssertionError:
            self.valueMinSpinBox.setValue(min)
        self.valueSlider.setRange(min, self.valueMaxSpinBox.value())
        try:
            assert_approx_equal(self.model.getMinValue(self.paramIndx), min)
        except AssertionError:
            self.model.setMinValue(self.paramIndx, min)

    def changeValueMax(self, max):
        '''If the slider minimum value changes, adjust the slider range
        and store the value in the model'''
        try:
            assert_approx_equal(self.valueMaxSpinBox.value(), max)
        except AssertionError:
            self.valueMaxSpinBox.setValue(max)
        self.valueSlider.setRange(self.valueMinSpinBox.value(), max)
        try:
            assert_approx_equal(self.model.getMaxValue(self.paramIndx), max)
        except AssertionError:
            self.model.setMaxValue(self.paramIndx, max)

    def changeSliderVal(self, val):
        '''If the spinbox value is chosen outside the slider range,
        extend range, and store the value in the model'''
        if val > self.valueMaxSpinBox.value():
            self.valueMaxSpinBox.setValue(val)
        elif val < self.valueMinSpinBox.value():
            self.valueMinSpinBox.setValue(val)

        try:
            assert_approx_equal(self.valueSlider.value(), val)
        except AssertionError:
            self.valueSlider.setValue(val)

        # Change the spin box as well
        try:
            assert_approx_equal(self.valueSpinBox.value(), val)
        except AssertionError:
            self.valueSpinBox.setValue(val)

        # Change the underlying model's value
        try:
            assert_approx_equal(self.model.getValue(self.paramIndx), val)
        except AssertionError:
            self.model.setValue(self.paramIndx, val)

    def updateMin(self, paramIndx, min):
        '''Update the parameter's min when the model changes'''
        if self.paramIndx == paramIndx:
            self.changeValueMin(min)

    def updateMax(self, paramIndx, max):
        '''Update the parameter's max when the model changes'''
        if self.paramIndx == paramIndx:
            self.changeValueMax(max)

    def updateValue(self, paramIndx, val):
        '''Update the parameter's value when the model changes'''
        if self.paramIndx == paramIndx:
            self.changeSliderVal(val)

    def changeParameter(self, paramIndx):
        '''Affect changes in the parameter'''

        self.paramIndx = paramIndx
        # Read the old values of the 
        self.changeSliderVal(self.model.getValue(self.paramIndx))
        self.changeValueMin(self.model.getMinValue(self.paramIndx))
        self.changeValueMax(self.model.getMaxValue(self.paramIndx))
        self.paramChooser.setCurrentIndex(self.paramIndx)
