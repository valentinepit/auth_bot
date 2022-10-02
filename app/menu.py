from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

btn_main = KeyboardButton("Main menu")
btn_del_submit = KeyboardButton("DEL")
btn_add_submit = KeyboardButton("ADD")


# Main menu
btn_list = KeyboardButton("User list")
btn_add = KeyboardButton("Add User")
btn_del = KeyboardButton("Delete User")


main_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_list, btn_add, btn_del)

del_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_del_submit, btn_main)
add_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_add_submit, btn_main)

btn_list = InlineKeyboardButton('List', callback_data='list')
btn_add = InlineKeyboardButton('Add User', callback_data='add')
btn_del = InlineKeyboardButton('Delete User', callback_data='del')
inline_kb = InlineKeyboardMarkup(row_width=3).add(btn_list, btn_add, btn_del)

btn_next = InlineKeyboardButton('Next', callback_data="next")
btn_prev = InlineKeyboardButton('Prev', callback_data="prev")
btn_main = InlineKeyboardButton("Main menu", callback_data="main")
sub_menu = InlineKeyboardMarkup(row_width=3).add(btn_prev, btn_main, btn_next)
