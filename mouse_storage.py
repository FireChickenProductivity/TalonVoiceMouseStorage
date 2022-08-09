import os

from talon import Module, actions, ui, ctrl

from .project_types import *



MOUSE_STORAGE_FOLDER_NAME = 'positions'
PROJECT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
MOUSE_STORAGE_DIRECTORY = os.path.join(PROJECT_DIRECTORY, MOUSE_STORAGE_FOLDER_NAME)
DATA_DIRECTORY = os.path.join(PROJECT_DIRECTORY, "data")

module = Module()

application_specific = module.setting(
    'mouse_position_storage_application_specific',
    type = bool,
    default = True,
    desc = 'Whether or not stored mouse positions should be stored as application specific',
)

require_title_contains = module.setting(
    'mouse_position_storage_title',
    type = str,
    default = '',
    desc = 'If not empty, mouse positions are stored requiring this string present in the application title.'
)

default_mouse_position_mode = module.setting(
    'mouse_position_storage_default_mode',
    type = str,
    default = '',
    desc = 'Mouse positions can be mode specific. This setting is used as the mode when none is set manually.',
)

require_mode = module.setting(
    'mouse_position_storage_required_mode',
    type = str,
    default = '',
    desc = 'Stored mouse positions require this mouse position storage mode',
)

relativity = module.setting(
    'mouse_position_storage_relativity',
    type = str,
    default = 'ABSOLUTE',
    desc = 'Describes what mouse positions are stored relative to. The default is relative to the upper left corner of the main monitor',
)

manually_set_mouse_position_mode = ''

def get_mouse_position_mode():
    if not manually_set_mouse_position_mode:
        return default_mouse_position_mode.get()
    return manually_set_mouse_position_mode

def get_required_mode():
    if require_mode.get():
        return require_mode.get()
    return default_mouse_position_mode.get()

@module.action_class
class Actions:
    def mouse_position_storage_current_application_name() -> str:
        '''Returns the current application name'''
        window = ui.active_window()
        return window.app.name
    def mouse_position_storage_current_window_title() -> str:
        '''Returns the current window title'''
        return ui.active_window().title
    def mouse_position_storage_current_window_position() -> MousePosition:
        '''Returns the upper left hand corner of the active window'''
        window = ui.active_window()
        rectangle = window.rect
        horizontal = rectangle.left
        vertical = rectangle.top
        return MousePosition(horizontal, vertical)

    def mouse_position_storage_update_manually_set_mode(new_mode: str):
        '''Updates the mouse position storage manually set mode, which overrides the default mode'''
        global manually_set_mouse_position_mode
        manually_set_mouse_position_mode  = new_mode

    def mouse_position_storage_store_position_with_name(name: str):
        '''Stores a mouse position with the specified name assuming a position with the same context does not already exist'''
        store_current_mouse_position_with_name(name)
    def mouse_positions_storage_update_position_with_name(name: str):
        '''If a mouse position with the same name exists for the active context, the action updates it'''
        update_mouse_position_with_name(name)
    def mouse_positions_storage_remove_position_with_name(name: str):
        '''If a mouse position with the same name exists for the active context, the action updates it'''
        remove_mouse_position_with_name(name)
    def mouse_positions_storage_go_to_position(name: str):
        '''Goes to the mouse position stored with the specified name with the most specific matching context'''
        go_to_mouse_position(name)
    def mouse_positions_storage_update_reference_position():
        '''Updates the mouse stored reference position with current mouse location'''
        position = get_reference_point()
        position.set_to_current_mouse_position()
   

def create_directory_if_nonexistent(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def store_current_mouse_position_with_name(name):
    position = get_mouse_position()
    directory = get_mouse_position_directory_from_name(name)
    create_directory_if_nonexistent(directory)
    if no_position_in_directory_with_same_context(directory):
        store_mouse_position_at_directory(position, directory)
    else:
        tell_user_must_use_update_commands_to_overwrite_position(name)

def tell_user_must_use_update_commands_to_overwrite_position(name):
    actions.app.notify(f'Cannot overwrite position {name} with this command. Instead use storage update {name}')

def get_mouse_position():
    horizontal, vertical = ctrl.mouse_pos()
    position = MousePosition(horizontal, vertical)
    return position

def get_mouse_position_directory_from_name(name):
    return os.path.join(MOUSE_STORAGE_DIRECTORY, name)

def update_mouse_position_with_name(name):
    directory = get_mouse_position_directory_from_name(name)
    path = get_directory_path_with_active_storage_context_if_exists(directory)
    if path:
        position = get_mouse_position()
        store_mouse_position_at_path(position, path)
    else:
        tell_user_position_unavailable_with_name(name)
def tell_user_position_unavailable_with_name(name):
    actions.app.notify(f'The position {name} does not exist in an active context!')
   

def store_mouse_position_at_directory(position, directory):
    path = get_mouse_position_storage_path_from_directory(directory)
    store_mouse_position_at_path(position, path)

def get_mouse_position_storage_path_from_directory(directory):
    path = get_directory_path_with_active_storage_context_if_exists(directory)
    if not path:
        return get_new_mouse_position_storage_path_for(directory)
    return path

def get_new_mouse_position_storage_path_for(directory):
    existing_paths = os.listdir(directory)
    path = ''
    for i in range(len(existing_paths) + 1):
        filename = str(i) + '.txt'
        path = os.path.join(directory, filename)
        if not os.path.exists(path):
            return path
    return path

def no_position_in_directory_with_same_context(directory):
    return get_directory_path_with_active_storage_context_if_exists(directory) == ''

def get_directory_path_with_active_storage_context_if_exists(directory):
    if not os.path.isdir(directory):
        return ''
    existing_paths = os.listdir(directory)
    active_context = get_active_storage_context()
    for path in existing_paths:
        data = PositionFileData(os.path.join(directory, path))
        context = data.get_context()
        if context == active_context:
            return os.path.join(directory, path)
    return ''

def store_mouse_position_at_path(position, path):
    with open(path, 'w') as position_file:
        context = get_active_storage_context()
        context_string = str(context)
        print(f'Storing mouse position at path {path} with context {context_string}')
        position_file.write(context_string)
        if relativity.get() == 'WINDOW':
            position = get_position_relative_to_active_window(position)
        elif relativity.get() == 'MOUSE':
            position = get_position_relative_to_reference_point(position)
        position_file.write(str(position) + '\n')
        position_relativity = get_active_storage_relativity()
        position_file.write(str(position_relativity))

def get_active_storage_relativity():
    return PositionRelativity[relativity.get()]

def get_active_storage_context():
    application = ''
    if stored_position_should_be_application_specific():
        application = actions.user.mouse_position_storage_current_application_name()
    required_title_part = ''
    if stored_position_should_be_title_specific():
        required_title_part = require_title_contains.get()
    required_mode = get_required_mode()
    context = PositionContext(application, required_title_part, required_mode)
    return context

def stored_position_should_be_application_specific():
    return application_specific.get()
def stored_position_should_be_title_specific():
    return stored_position_should_be_application_specific() and require_title_contains.get()

def go_to_mouse_position(name):
    active_context = get_active_context()
    position, position_relativity = get_position_and_relativity_with_specified_name_best_matching_context(name, active_context)
    if position_relativity == PositionRelativity.WINDOW:
        position = make_position_relative_to_window_absolute(position)
    elif position_relativity == PositionRelativity.MOUSE:
        position = make_position_relative_to_reference_point_absolute(position)
    horizontal = position.get_horizontal()
    vertical = position.get_vertical()
    actions.mouse_move(horizontal, vertical)

def remove_mouse_position_with_name(name):
    active_context = get_active_context()
    path = get_path_with_specified_name_best_matching_context(name, active_context)
    if path:
        try:
            remove_position_at_path(path)
        except:
            actions.app.notify(f'Error! Could not remove position with name {name}!')
    else:
        tell_user_position_unavailable_with_name(name)
    actions.app.notify(f'Removed position with name {name} from the act of context!')

def remove_position_at_path(path):
    if mouse_position_filepath_in_correct_directory(path):
        os.remove(path)
    else:
        actions.app.notify('Warning! The mouse position storage position removal code was used to try to remove a file outside the mouse position storage!')
        print(f'Warning! The mouse position storage position removal code was used to try to remove a file outside the mouse position storage at path: {path}')


def mouse_position_filepath_in_correct_directory(path):
    current_folder = os.path.dirname(path)
    folder_of_current_folder = os.path.dirname(current_folder)
    return folder_of_current_folder == MOUSE_STORAGE_DIRECTORY

def get_active_context():
    application = actions.user.mouse_position_storage_current_application_name()
    title = actions.user.mouse_position_storage_current_window_title()
    mode = get_mouse_position_mode()
    context = PositionContext(application, title, mode)
    return context

def get_path_with_specified_name_best_matching_context(name, context):
    directory = get_mouse_position_directory_from_name(name)
    best_match_path = ''
    best_match_specificity = 0
    for filename in os.listdir(directory):
        data = get_data_from_directory_and_filename(directory, filename)
        data_context = data.get_context()
        if data_context.matches_position_context(context):
            specificity = data_context.compute_specificity()
            if specificity >= best_match_specificity:
                best_match_specificity = specificity
                best_match_path = os.path.join(directory, filename)
    return best_match_path

def get_position_with_specified_name_best_matching_context(name, context):
    data = get_data_with_specified_name_best_matching_context(name, context)
    return data.get_position()

def get_data_with_specified_name_best_matching_context(name, context):
    best_match_path = get_path_with_specified_name_best_matching_context(name, context)
    data = PositionFileData(best_match_path)
    return data

def get_position_and_relativity_with_specified_name_best_matching_context(name, context):
    data = get_data_with_specified_name_best_matching_context(name, context)
    return data.get_position(), data.get_relativity()
       
def get_data_from_directory_and_filename(directory, filename):
    path = os.path.join(directory, filename)
    data = PositionFileData(path)
    return data


def get_position_relative_to_active_window(position):
    window_position = actions.user.mouse_position_storage_current_window_position()
    relative_position = position - window_position
    return relative_position

def get_position_relative_to_reference_point(position):
    reference_point_file = get_reference_point()
    reference_point = reference_point_file.get()
    return position - reference_point

def make_position_relative_to_window_absolute(position):
    window_position = actions.user.mouse_position_storage_current_window_position()
    absolute_position = position + window_position
    return absolute_position
   
def make_position_relative_to_reference_point_absolute(position):
    current_position = get_mouse_position()
    return position + current_position

def get_reference_point():
   return MousePositionFile(DATA_DIRECTORY, "reference point")
