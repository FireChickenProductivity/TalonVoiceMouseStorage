storage new <user.prose>: user.mouse_position_storage_store_position_with_name(prose)
storage update <user.prose>: user.mouse_positions_storage_update_position_with_name(prose)
storage delete <user.prose>: user.mouse_positions_storage_remove_position_with_name(prose)
walk <user.prose>: user.mouse_positions_storage_go_to_position(prose)
settings()
    user.mouse_position_storage_title = ''
    user.mouse_position_storage_application_specific = 1
    user.mouse_position_storage_relativity = 'WINDOW'
