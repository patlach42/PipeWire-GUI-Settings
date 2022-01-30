import os
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import re
import functools


program_dir = os.path.dirname(os.path.realpath(__file__))


class PwMetadataSettings:
    AVAILABLE_SAMPLES_VALUES = ['0', '32', '64', '128', '256', '512', '1024', '2048', '4096']

    def __init__(self):
        self.clock_quantum = None

    def query_metadata(self):
        raw_data = os.popen("pw-metadata -n settings 0").read()
        prepared_data = raw_data.strip().split('\n')[1:]
        settings = {}
        for _string in prepared_data:
            parsed_settings_string = {
                e[0]: e[1].strip('\'')
                for e in map(lambda x: x.split(':'), re.split(r"\s(?=([^\']*\'[^\']*\')*[^\']*$)", _string))
                if len(e) == 2 and e[0]
            }
            if parsed_settings_string.get('key') is not None and parsed_settings_string.get('value') is not None:
                settings[parsed_settings_string['key']] = parsed_settings_string['value']
        self.clock_quantum = settings.get('clock.quantum')

    def set_sample_rate(self, sample_rate, options, style):
        os.popen("pw-metadata -n settings 0 clock.quantum %s" % sample_rate)
        for k, v in options.items():
            if k == sample_rate:
                v.setIcon(style.standardIcon(QStyle.SP_DialogApplyButton))
            else:
                v.setIcon(QIcon())


def main():
    pw_metadata_settings = PwMetadataSettings()
    pw_metadata_settings.query_metadata()

    app = QApplication([])
    style = app.style()
    app.setQuitOnLastWindowClosed(False)

    # Adding an icon
    icon = QIcon(os.path.join(program_dir, 'icon.png'))

    # Adding item on the menu bar
    tray = QSystemTrayIcon()
    tray.setIcon(icon)
    tray.setVisible(True)
    # Creating the options
    menu = QMenu()
    options = {}
    menu.addSection('Sample Rate')
    for sample_rate in pw_metadata_settings.AVAILABLE_SAMPLES_VALUES:
        options[sample_rate] = QAction("%s Samples" % sample_rate)

        if sample_rate == pw_metadata_settings.clock_quantum:
            options[sample_rate].setIcon(style.standardIcon(QStyle.SP_DialogApplyButton))

        options[sample_rate].triggered.connect(
            functools.partial(pw_metadata_settings.set_sample_rate, sample_rate, options, style)
        )
        menu.addAction(options[sample_rate])
    menu.addSeparator()

    # To quit the app
    quit = QAction("Quit")
    quit.triggered.connect(app.quit)
    menu.addAction(quit)

    # Adding options to the System Tray
    tray.setContextMenu(menu)
    app.exec_()


if __name__ == '__main__':
    main()
