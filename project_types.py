import enum
import os
from talon import ctrl, actions


class MousePosition:
    STRING_START = '('
    STRING_ENDING = ')'
    COORDINATE_SEPARATOR = ', '
    def __init__(self, horizontal: int, vertical: int):
        self.horizontal = horizontal
        self.vertical = vertical
   
    def get_horizontal(self):
        return self.horizontal
    def get_vertical(self):
        return self.vertical
   
    def __add__(self, other):
        result = MousePosition(0, 0)
        result += self
        result += other
        return result
    def __iadd__(self, other):
        self.horizontal += other.horizontal
        self.vertical += other.vertical
        return self
    def __sub__(self, other):
        result = MousePosition(0, 0)
        result += self
        result -= other
        return result
    def __isub__(self, other):
        self.horizontal -= other.horizontal
        self.vertical -= other.vertical
        return self

    def go(self):
        actions.mouse_move(self.horizontal, self.vertical)

    def __str__(self) -> str:
        return MousePosition.STRING_START + str(self.horizontal) + MousePosition.COORDINATE_SEPARATOR \
        + str(self.vertical) + MousePosition.STRING_ENDING

    #assumes that the text properly represents a mouse position object
    @staticmethod
    def from_text(text: str):
        horizontal_start = text.index(MousePosition.STRING_START) + 1
        horizontal_ending = text.index(MousePosition.COORDINATE_SEPARATOR)
        horizontal = int(text[horizontal_start : horizontal_ending])
        vertical_start = horizontal_ending + 1
        vertical_ending = text.index(MousePosition.STRING_ENDING)
        vertical = int(text[vertical_start : vertical_ending])
        return MousePosition(horizontal, vertical)

class MousePositionFile:
    def __init__(self, folder: str, name: str):
        self.folder = folder
        self.name = name
        self._initialize_file_if_nonexistent()
        self._retrieve_position()
       
    def get(self):
        return self.position
       
    def set(self, position: MousePosition):
        self.position = position
        self._store_position()
   
    def set_to_current_mouse_position(self):
        horizontal, vertical = ctrl.mouse_pos()
        position = MousePosition(horizontal, vertical)
        self.set(position)
   
    def _store_position(self):
        with open(self.get_path(), 'w') as position_file:
            position_text = str(self.position)
            position_file.write(position_text)
   
    def _retrieve_position(self):
        with open(self.get_path(), 'r') as position_file:
            position_text = position_file.readline().rstrip('\n\r')
            self.position = MousePosition.from_text(position_text)
   
    def get_path(self):
        return os.path.join(self.folder, self.name)
   
    def _initialize_file_if_nonexistent(self):
        if not os.path.exists(self.get_path()):
            self._make_directory_if_nonexistent()
            self.set(MousePosition(0, 0))
   
    def _make_directory_if_nonexistent(self):
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

class ContextDataNotFound(Exception):
    pass

#Determines when a stored mouse position can be used
class PositionContext:
    APP_START = 'app:'
    TITLE_PART_START = 'title:'
    MOUSE_POSITION_MODE_START = 'mouse position mode:'
    def __init__(self, app = '', title_part = '', mouse_position_mode = ''):
        self.app = app
        self.title_part = title_part
        self.mouse_position_mode = mouse_position_mode

    def receive_field_from_line(self, text):
        if text.startswith(PositionContext.APP_START):
            self.app = text_from_string_after_substring(text, PositionContext.APP_START)
        elif text.startswith(PositionContext.TITLE_PART_START):
            self.title_part = text_from_string_after_substring(text, PositionContext.TITLE_PART_START)
        elif text.startswith(PositionContext.MOUSE_POSITION_MODE_START):
            self.mouse_position_mode = text_from_string_after_substring(text, PositionContext.MOUSE_POSITION_MODE_START)
        else:
            raise ContextDataNotFound('Context data not found within the following text: ' + text)

    def matches_title(self, title):
        return self.title_part in title

    def matches_app(self, app):
        return app == self.app or self.app == ''

    def matches_mouse_position_mode(self, mode):
        return mode == self.mouse_position_mode

    def matches_position_context(self, other):
        return self.matches_app(other.app) \
            and self.matches_title(other.title_part) \
            and self.matches_mouse_position_mode(other.mouse_position_mode)

    def compute_specificity(self):
        result = 0
        if self.app:
            result += 1
        if self.title_part:
            result += 1
        if self.mouse_position_mode: #mode beats application and title part matching
            result += 3
        return result

    def __eq__(self, other):
        return self.app == other.app and self.title_part == other.title_part and self.mouse_position_mode == other.mouse_position_mode
   
    def __str__(self) -> str:
        result = ''
        if self.app:
            result += PositionContext.APP_START + self.app + '\n'
        if self.title_part:
            result += PositionContext.TITLE_PART_START + self.title_part + '\n'
        if self.mouse_position_mode:
            result += PositionContext.MOUSE_POSITION_MODE_START + self.mouse_position_mode + '\n'
        return result

def text_from_string_after_substring(text, substring):
    return text[len(substring) : ]

class PositionRelativity(enum.Enum):
    ABSOLUTE = enum.auto()
    WINDOW = enum.auto()
    MOUSE = enum.auto()

STORED_POSITION_RELATIVITY_START = 'PositionRelativity.'

class PositionFileData:
    def __init__(self, path):
        self.position = None
        self.context = PositionContext()
        self.relativity = PositionRelativity.ABSOLUTE
        self._get_data_from_file(path)
       
    def _get_data_from_file(self, path):
        with open(path, 'r') as position_file:
            for line in position_file:
                line_without_trailing_new_line_character = line.rstrip('\n\r')
                self._get_data_from_line(line_without_trailing_new_line_character)
    def _get_data_from_line(self, line):
        try:
            self.context.receive_field_from_line(line)
            return
        except ContextDataNotFound:
            pass
        if line.startswith(STORED_POSITION_RELATIVITY_START):
            self.relativity = PositionRelativity[text_from_string_after_substring(line, STORED_POSITION_RELATIVITY_START)]
            return
        if line:
            self.position = MousePosition.from_text(line)
    def get_position(self):
        return self.position
    def get_context(self):
        return self.context
    def get_relativity(self):
        return self.relativity
    def __str__(self) -> str:
        result = f'position: {self.position}'
        result += 'context:' + str(self.context)
        result += 'relativity:' + str(self.relativity)
        return result
        return result
