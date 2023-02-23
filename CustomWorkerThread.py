import sys
import traceback

from PySide2.QtCore import QRunnable, Slot, Signal, QObject
import sys
import traceback

from PySide2.QtCore import QRunnable, Slot, Signal, QObject


class WorkerSignals(QObject):
    finished = Signal()
    error = Signal(tuple)
    progress = Signal(int)
    result = Signal(object)


class Worker(QRunnable, QObject):
    def __init__(self, function, *args, **kwargs):
        super(Worker, self).__init__()
        self.running_function = function
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        self.kwargs['progress'] = self.signals.progress

    @Slot()
    def run(self):
        try:
            print("Try")
            result = self.running_function(*self.args, **self.kwargs)
        except NotImplementedError:
            print("error")
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            print("else")
            self.signals.result.emit(result)
        finally:
            print("Finally")
            self.signals.finished.emit()