Use voice commands to store mouse positions and then click on them. This is an abandoned project that has not been thoroughly tested yet.

# Commands
storage new (dictate text here):

Stores the current mouse position with the name given by the text dictated after storage new unless a mouse position has already been stored with the same name within the active context.

storage update (dictate text here):

The mouse position best matching the active context that has the name given through the dictated text is updated to receive the current mouse position.

storage delete (dictate text here): 

The mouse position best matching the active context that has the name given through the dictated text is deleted.

walk (dictate text here): 
The cursor is moved to the mouse position best matching the active context that has the name given through the dictated text.

# Settings
user.mouse_position_storage_application_specific

When set to 1, mouse positions are stored as application specific. When set to 0, stored positions are not specific to any application.

user.mouse_position_storage_title

If given a string value and positions are being stored as application specific, mouse positions are stored requiring the current window to have that string in the title. If multiple stored positions' titles match the current title, which position is chosen between them is undefined.

user.mouse_position_storage_relativity

Determines what mouse positions are stored relative to. If this is ABSOLUTE, then mouse positions get stored relative to the upper left position of the main monitor. If this is WINDOW, mouse positions are stored relative to the upper left corner of the current window.
