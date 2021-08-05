from datetime import datetime

try:
    from mako.template import Template

    HAS_MAKO = True
except ImportError:
    HAS_MAKO = False
try:
    from pygments import highlight
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import PythonLexer

    HAS_PYGMENTS = True
except ImportError:
    HAS_PYGMENTS = False
from utils.functions import print_error, read_file

__all__ = ("TextFormatter", "HTMLFormatter")


class TextFormatter:
    max_depth = 5
    frames_quantity = 0
    frames_without_locals = []
    locals_formatted = False

    @staticmethod
    def is_valid_to_display(varname: str, obj):
        if not (
            varname in ("self", "e")
            or varname.startswith("__")
            or "method" in varname
            or "function" in varname
            or "module" in str(type(obj))
            or "Report" in str(type(obj))
        ):
            return True

    @staticmethod
    def extract_attributes(obj):
        result = {}
        for k in dir(obj):
            if (
                hasattr(obj, k)
                and not k.startswith("__")
                and not k.endswith("__")
                and not hasattr(k, "hidden")
                and not type(getattr(obj, k)).__name__.endswith("method")
            ):
                result[k] = getattr(obj, k)

        return result

    def format_traceback_frame(self, frame):
        if self.locals_formatted:
            self.frames_quantity += 1
            self.locals_formatted = False

        lines, current_line = frame.code
        code = "‖   |"
        code += "‖   |".join(
            ((">>> " if lines.index(line) == frame.line - current_line else "    ") + line) for line in lines
        )

        return f"@ {frame.file}, line {frame.line} (frame #{self.frames_quantity}):\n" f"{code}‖\n" "\n"

    def format_locals(self, frame):
        i = int()
        locals_text = f"@ frame #{self.frames_quantity}:\n"

        for varname, value in frame.locals.items():
            if self.is_valid_to_display(varname, value):
                if isinstance(value, dict):
                    locals_text += f"""‖   |    {varname} ({type(value).__name__}):\n‖   |   |"""
                    for k, v in value.items():
                        if self.is_valid_to_display(k, v):
                            locals_text += f""""{k}": {v}\n‖   |   |"""
                    locals_text += "‖   |\n"
                    i += 1

                elif hasattr(value, "__dict__") and ("class" in str(type(value))):
                    locals_text += f"""‖   |   {varname} (object of type {str(type(value))[7:-1]}):\n"""

                    d = self.extract_attributes(value)
                    for k, v in d.items():
                        locals_text += f"""‖   |   |   attribute '{k}' ({type(v).__name__}): {v}\n"""
                    locals_text += "‖   |\n"
                    i += 1

                else:
                    locals_text += f"""‖   |   {varname} ({type(value).__name__}): {repr(value)}\n"""
                    i += 1

        self.locals_formatted = True
        if i:
            return locals_text
        else:
            return ""

    def format(self, report):
        traceback_as_list, locals_as_list = [], []
        empty_locals_message = ""

        for frame in report.traceback:
            traceback_as_list.append(self.format_traceback_frame(frame))

            locals_for_frame = self.format_locals(frame)
            if locals_for_frame:
                locals_as_list.append(locals_for_frame)
            else:
                self.frames_without_locals.append(frame)

        if self.frames_without_locals:
            message_part = ""
            for frame_num in range(len(self.frames_without_locals)):
                message_part += f"{frame_num}, "
            message_part = message_part[:-2]
            empty_locals_message = f"\n‖   Frames {message_part} don`t have locals"

        return (
            "Error report"
            "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
            "Exception has been ocurred at {timestamp} and indices the following:\n"
            "‖   {exception_name}: {exception_description}\n"
            "Traceback:\n"
            "‖   {traceback}\n"
            "Locals:{empty_locals}\n"
            "‖   {locals}\n"
        ).format(
            timestamp=datetime.fromtimestamp(int(report.timestamp)),
            traceback="‖   ".join(traceback_as_list),
            locals="‖   ".join(locals_as_list),
            empty_locals=empty_locals_message,
            exception_name=type(report.exception).__name__,
            exception_description=str(report.exception),
        )


class HTMLFormatter:
    def __init__(self):
        if not HAS_MAKO:
            print_error("Mako is not installed. please install all requirements")
            return
        if not HAS_PYGMENTS:
            print_error("pygments is not installed. please install all requirements")
            return
        self._template = Template(
            read_file("assets/error/error_template.html"),
            default_filters=["decode.utf8"],
            input_encoding="utf-8",
            output_encoding="utf-8",
        )

    def highlight(self, code):
        return highlight(code, PythonLexer(), HtmlFormatter())

    def format(self, report, maxdepth=5):
        return self._template.render(
            maxdepth=maxdepth,
            report=report,
            datetime=datetime,
            highlight=self.highlight,
        )
