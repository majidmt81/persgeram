from telethon import TelegramClient, events
from telethon.tl.types import PeerUser
from telethon.tl.functions.users import GetUsersRequest
from telethon import errors
from tkinter import messagebox, filedialog
import tkinter as tk
from tkinter import ttk
import asyncio
import threading
import os

# اطلاعات API تلگرام خود را اینجا وارد کنید
api_id = 'api_id'
api_hash = 'api_hash'
client = TelegramClient('anon', api_id, api_hash)

path_file = ""
user_id = None

# تعریف متغیر global loop
loop = None

# تابع اتصال به تلگرام
async def connect_client():
    try:
        if not client.is_connected():
            await client.connect()
        print("Client connected.")  # اشکال‌زدایی
    except Exception as e:
        root.after(0, lambda: messagebox.showerror("Error", f"Failed to connect to Telegram: {e}"))

# تابع ورود به حساب تلگرام با استفاده از کد تأیید
async def sign_in(phone_number, code):
    await connect_client()  # اتصال به تلگرام
    try:
        await client.sign_in(phone_number, code)  # ورود با استفاده از کد تأیید
        root.after(0, lambda: messagebox.showinfo("Telegram", "Successfully logged in!"))
        root.after(0, root_manage)  # فراخوانی مدیریت رابط کاربری در نخ اصلی
    except errors.SessionPasswordNeededError:
        root.after(0, show_password_input)  # نمایش بخش وارد کردن رمز عبور
        root.after(0, lambda: messagebox.showerror("Error", "Failed to sign in:"))

# نمایش بخش وارد کردن رمز عبور
def show_password_input():
    print('hi')
    global password_entry
    global password_label
    global password_button
    password_label = tk.Label(root, text='Enter your password:',bg = '#4af')
    password_label.pack()
    password_entry = tk.Entry(root, show='*')  # استفاده از show='*' برای مخفی کردن کاراکترهای ورودی
    password_entry.pack()
    password_button = tk.Button(root, text='Submit Password', command=on_password_submit)
    password_button.pack()

# تابع برای ارسال رمز عبور و ورود به تلگرام
def on_password_submit():
    password = password_entry.get()
    asyncio.run_coroutine_threadsafe(send_password(password), loop)

# تابع ارسال رمز عبور برای ورود به حساب
async def send_password(password):
    try:
        await client.sign_in(password=password)  # ورود با استفاده از رمز عبور
        root.after(0, lambda: messagebox.showinfo("Telegram", "Successfully logged in with password!"))
        root.after(0, root_manage)  # فراخوانی مدیریت رابط کاربری در نخ اصلی
    except Exception as e:
        root.after(0, lambda: messagebox.showerror("Error", f"Failed to sign in with password: {e}"))

# فراخوانی ارسال کد از طریق دکمه
def on_send_code():
    phone_number = phone_entry.get()
    asyncio.run_coroutine_threadsafe(send_code(phone_number), loop)

# تابع ارسال کد تأیید به شماره تلفن
async def send_code(phone_number):
    try:
        await connect_client()  # اتصال به تلگرام
        await client.send_code_request(phone_number)
        root.after(0, lambda: messagebox.showinfo("Telegram", "Code sent to your phone number!"))
        root.after(0, show_code_input)  # فراخوانی نمایش کد در نخ اصلی
    except Exception as e:
        root.after(0, lambda: messagebox.showerror("Error", f"Failed to send code: {e}"))

# فراخوانی ورود از طریق دکمه
def on_sign_in():
    phone_number = phone_entry.get()
    code = code_entry.get()
    asyncio.run_coroutine_threadsafe(sign_in(phone_number, code), loop)
    code_entry.pack_forget()
    label_entry.pack_forget()
    bott_entry.pack_forget()

# نمایش بخش وارد کردن کد تأیید
def show_code_input():
    global code_entry
    global label_entry
    global bott_entry
    label_entry = tk.Label(root, text='Enter code:',bg = '#4af')
    label_entry.pack()
    code_entry = tk.Entry(root)
    code_entry.pack()
    bott_entry = tk.Button(root, text='Log in', command=on_sign_in)
    bott_entry.pack()

# اجرای حلقه asyncio در یک نخ (thread) جداگانه
def start_async_loop():
    global loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_forever()

# تابع برای اطمینان از اتصال و لاگین شدن کاربر
async def ensure_connected():
    await connect_client()
    if not await client.is_user_authorized():
        root.after(0, lambda: messagebox.showerror("Error", "Client is not logged in. Please log in first."))
        return False
    return True

# تابع ارسال پیام به کاربر با نام کاربری
async def send_message(username, message):
    if await ensure_connected():
        try:
            # دریافت اطلاعات کاربر از نام کاربری
            user = await client.get_entity(username)
            peer = PeerUser(user.id)  # تبدیل به PeerUser با استفاده از شناسه کاربر
            await client.send_message(peer, message)
            fn = user.first_name
            print(f"Message sent to {fn} send!")

            # نمایش پیام ارسالی در سمت راست جعبه چت با نام مخاطب
            def update_chat_box_sent_message():
                chat_box.insert(tk.END, f"{message} :You to {fn}\n", 'sent')
                chat_box.yview(tk.END)
            root.after(0, update_chat_box_sent_message)

        except Exception as e:
            print(f"Error sending message: {e}")

def on_send_button_click():
    global user_id
    user_id = UID.get()
    messagee = msg.get()
    if user_id and messagee:
        print(f"Sending message to {user_id}: {messagee}")  # اشکال‌زدایی
        asyncio.run_coroutine_threadsafe(send_message(user_id, messagee), loop)
        # پاک کردن ورودی پیام
        msg.delete(0, tk.END)
    else:
        root.after(0, lambda: messagebox.showerror("Error", "Please enter both user ID and message."))


# مدیریت واسط کاربری بعد از ورود موفق
async def check_authorization():
    await connect_client()  # اتصال به تلگرام
    if await client.is_user_authorized():
        root.after(0, root_manage)  # فراخوانی مدیریت رابط کاربری در نخ اصلی

def root_manage():
    if os.path.exists(path_file):
        root.withdraw()
        print("hi")
        root2.deiconify()
        chat_box.pack()
        root.after(0, lambda: messagebox.showinfo('File', 'you are logged'))
    else:
        root.deiconify()
        root2.withdraw()
        root.after(0, lambda: messagebox.showinfo('File', 'File is not here!'))

# تابع ارسال فایل
async def send_file(username, file_path):
    if await ensure_connected():
        try:
            # نمایش وضعیت شروع ارسال فایل
            def update_status_sending():
                chat_box.insert(tk.END, "Sending file...\n")
                chat_box.yview(tk.END)
            root.after(0, update_status_sending)

            # دریافت اطلاعات کاربر از نام کاربری
            user = await client.get_entity(username)
            peer = PeerUser(user.id)  # تبدیل به PeerUser با استفاده از شناسه کاربر

            await client.send_file(peer, file_path)

            # نمایش وضعیت ارسال موفق
            def update_status_success():
                chat_box.insert(tk.END, "File sent successfully!\n")
                chat_box.yview(tk.END)
            root.after(0, update_status_success)

            print(f"File sent to {username} successfully!")
        except Exception as e:
            # نمایش وضعیت خطا در ارسال فایل
            def update_status_error():
                chat_box.insert(tk.END, f"Error sending file: {e}\n")
                chat_box.yview(tk.END)
            root.after(0, update_status_error)

            print(f"Error sending file: {e}")

# تابع برای انتخاب فایل و ارسال آن
def on_send_file():
    username = UID.get()
    file_path = filedialog.askopenfilename()
    if username and file_path:
        print(f"Sending file to {username}: {file_path}")  # اشکال‌زدایی
        asyncio.run_coroutine_threadsafe(send_file(username, file_path), loop)
    else:
        root.after(0, lambda: messagebox.showerror("Error", "Please enter a valid username and select a file."))

@client.on(events.NewMessage)
async def handler(event):
    # دریافت اطلاعات فرستنده
    sender = await event.get_sender()

    # بررسی اینکه پیام از کانال نباشد
    if event.is_channel:
        return  # اگر پیام از کانال باشد، آن را نادیده بگیر

    # دریافت نام فرستنده
    sender_name = getattr(sender, 'first_name', 'Unknown')  # اگر نام وجود ندارد، 'Unknown' نمایش داده شود

    # دریافت متن پیام
    message = event.message.text

    # چاپ پیام دریافتی برای اشکال‌زدایی
    print(f"Received message from {sender_name}: {message}")

    # نمایش پیام دریافتی در جعبه چت
    def update_chat_box_received_message():
        chat_box.insert(tk.END, f"{sender_name}: {message}\n", 'received')
        chat_box.yview(tk.END)
    root.after(0, update_chat_box_received_message)

# تابع logout برای خروج از حساب کاربری و بازنشانی TelegramClient
async def logout():
    global client
    try:
        await client.log_out()  
        print("Logged out successfully!")
        
        # تغییرات در رابط کاربری را در نخ اصلی انجام دهید
        root.after(0, lambda: root2.withdraw())  # مخفی کردن پنجره چت
        root.after(0, lambda: root.deiconify())  # نمایش پنجره ورود
        root.after(0, lambda: phone_entry.delete(0, tk.END)) 
        root.after(0, lambda: UID.delete(0, tk.END)) 
        root.after(0, lambda: chat_box.delete(1.0, tk.END)) 

        root.after(0, lambda: messagebox.showinfo("Logout", "You have been logged out successfully!"))

        await client.disconnect()

        # ساخت یک نمونه جدید از TelegramClient
        client = TelegramClient('anon', api_id, api_hash)
        await client.connect()

    except Exception as e:
        root.after(0, lambda: messagebox.showerror("Error", f"Failed to log out: {e}"))

root = tk.Tk()
root.minsize(400, 300)
root.configure(bg= '#5af')
root.title('Login to Telegram')
ttk.Label(root, text='Your phone:', background = '#4af').pack()
phone_entry = ttk.Entry(root)
phone_entry.pack()

ttk.Button(root, text='Send code', command=on_send_code).pack()

async_thread = threading.Thread(target=start_async_loop, daemon=True)
async_thread.start()

root2 = tk.Tk()
root2.minsize(400, 550)
root2.title('persgram2')
root2.configure(bg= '#5af')

chat_box = tk.Text(root2, wrap=tk.WORD,bg='#abc')
chat_box.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

chat_box.tag_configure('sent', justify='right', background='lightblue')
chat_box.tag_configure('received', justify='left', background='lightgray')

ttk.Label(root2, text='Username:',background='#8af').pack()
UID = ttk.Entry(root2)
UID.pack()

logout_button = ttk.Button(root2, text="Logout", command=lambda: asyncio.run_coroutine_threadsafe(logout(), loop))
logout_button.pack(side=tk.BOTTOM, pady=10)

# ایجاد یک frame در پایین صفحه برای نگهداری دکمه‌ها و ورودی پیام
bottom_frame = tk.Frame(root2,bg='#2af')
bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

send_file_button = ttk.Button(bottom_frame, text='Send file', command=on_send_file)
send_file_button.pack(side=tk.LEFT, padx=5)

msg = ttk.Entry(bottom_frame)
msg.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

send_message_button = ttk.Button(bottom_frame, text='Send message', command=on_send_button_click)
send_message_button.pack(side=tk.RIGHT, padx=5)

root2.withdraw()

# چک کردن وضعیت ورود کاربر
asyncio.run_coroutine_threadsafe(check_authorization(), loop)

root.mainloop()
    