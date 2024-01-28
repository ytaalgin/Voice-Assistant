import random
from gtts import gTTS
from playsound import playsound
import pywhatkit as kit
import speech_recognition as sr
import os
import tkinter as tk
from tkinter import messagebox, simpledialog
from tkhtmlview import HTMLLabel
import serial
import time

arduino_port = 'COM4'  # Arduino'nun bağlı olduğu portu değiştirin

# Seri portu başlatın
ser = serial.Serial(arduino_port, baudrate=9600, timeout=1)


def communicate_with_arduino(command):
    ser.write(command.encode())  # Arduino'ya komutu gönder
    time.sleep(1)  # Arduino'nun yanıtını beklemek için bir süre bekle
    response = ser.readline().decode('utf-8').strip()  # Arduino'dan yanıtı al
    return response


r = sr.Recognizer()


def get_emergency_number():
    # Daha önce girilen numarayı kontrol et
    try:
        with open("emergency_number.txt", "r") as file:
            number = file.read()
    except FileNotFoundError:
        number = None

    if not number:
        number = simpledialog.askstring("Acil Durum Numarası", "Lütfen acil durum numarasını girin:")
        if number:
            # Numarayı dosyaya kaydet
            with open("emergency_number.txt", "w") as file:
                file.write(number)
            messagebox.showinfo("Acil Durum Numarası", f"Girilen Acil Durum Numarası: {number}")
    else:
        messagebox.showinfo("Acil Durum Numarası", f"Kaydedilmiş Acil Durum Numarası: {number}")


def reset_emergency_number():
    # Kaydedilmiş numarayı sıfırla
    try:
        with open("emergency_number.txt", "r") as file:
            number = file.read()
        if number:
            with open("emergency_number.txt", "w") as file:
                file.write("")
            messagebox.showinfo("Numara Sıfırlandı", "Kaydedilmiş Acil Durum Numarası Sıfırlandı.")
    except FileNotFoundError:
        messagebox.showinfo("Hata", "Kaydedilmiş bir Acil Durum Numarası bulunamadı.")


# Ana pencereyi oluştur
root = tk.Tk()
root.geometry("500x550")
root.title("Viper Assist")

# Merhaba mesajını ekleyin
hello_label = tk.Label(root, text="Sistemi kullanmak için acil durum numarası girin."
                                  "\nArdından çıkan ekranda istenen bilgiyi yazın. "
                                  "\nDaha sonra bütün ekranlardan çıkış yapın. Asistan"
                                  "\nHey diye seslenerek uyandırılabilir. Kullanım"
                                  "\nkılavuzundaki talimatlara uyunuz. Numara sadece bir "
                                  "\nkez girilmelidir. Daha sonra isterseniz sıfırlaya-"
                                  "\nbilirsiniz.", font=("Helvetica", 12))
hello_label.pack(pady=10)

# Etiket (Label) ekleyin
label = tk.Label(root, text="Viper Assist", font=("Helvetica", 16))
label.pack(pady=20)

# Logo ekleyin
logo = tk.PhotoImage(file="logo.png")  # Logo resminizin yolunu belirtin
logo_label = tk.Label(root, image=logo)
logo_label.pack()

# Butonları içerecek bir çerçeve (frame) oluşturun
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# Başlat düğmesini oluşturun ve bazı özellikleri ayarlayın
start_button = tk.Button(button_frame, text="Numara Gir", command=get_emergency_number,
                         bg="green", fg="white", relief=tk.RIDGE, borderwidth=3)
start_button.config(width=15, height=2)  # Butonun boyutunu ayarlayın
start_button.grid(row=0, column=0, padx=10)  # Çerçeve içindeki konumunu ayarlayın

# Numarayı Sıfırla düğmesini oluşturun
reset_button = tk.Button(button_frame, text="Numarayı Sıfırla", command=reset_emergency_number,
                         bg="green", fg="white", relief=tk.RIDGE, borderwidth=3)
reset_button.config(width=15, height=2)  # Butonun boyutunu ayarlayın
reset_button.grid(row=0, column=1, padx=10)  # Çerçeve içindeki konumunu ayarlayın

# Ana döngüyü başlatın
root.mainloop()


class SesliAsistan:
    @staticmethod
    def seslendirme(metin):
        xtts = gTTS(text=metin, lang="tr")
        dosya = "dosya" + str(random.randint(0, 1242312412312)) + ".mp3"
        xtts.save(dosya)
        playsound(dosya)
        os.remove(dosya)

    def mikrofon(self):
        with sr.Microphone() as kaynak:
            print("Sizi dinliyorum...")
            listen = r.listen(kaynak)
            voice = ""
            try:
                voice = r.recognize_google(listen, language="tr-TR")
            except sr.UnknownValueError:
                self.seslendirme("ne dediğinizi anlayamadım")
            return voice

    def ses_karslik(self, gelen_ses):
        if gelen_ses in "merhaba":
            self.seslendirme("size de merhabalar")
        elif gelen_ses in "selam":
            self.seslendirme("size de selamlar")
        elif gelen_ses in "nasılsın":
            self.seslendirme("iyiyim sizler nasılsınız efendim")

        elif gelen_ses in "imdat" or "yardım edin":
            self.seslendirme("hemen bir yakınınıza haber veriyorum")

            try:
                with open("emergency_number.txt", "r") as file:
                    number = file.read()
                kit.sendwhatmsg_instantly(f"{number}", "Yardıma ihtiyacım var. Bu mesaj cankurtaran "
                                                       "asistan Moli tarafından gönderilmiştir.", 30, tab_close=True)

            except (SystemExit, KeyboardInterrupt, OSError, StopIteration):
                self.seslendirme("bir hata meydana geldi lütfen daha sonra tekrar deneyiniz")


asistan = SesliAsistan()


def acil_durum():
    arduino_response = communicate_with_arduino("REPORT_FALL\n")
    if arduino_response == "REAL_FALL" or arduino_response == "SUSPECTED_FALL":
        asistan.seslendirme("İyi misiniz?")
        yanit = asistan.mikrofon()
        if yanit in "evet":
            asistan.ses_karslik("Lütfen dikkatli olun...")
        elif yanit in "hayır":
            asistan.ses_karslik("Hemen size ulaşmaları için bildirim gönderiyorum...")
            with open("emergency_number.txt", "r") as file:
                number = file.read()
            kit.sendwhatmsg_instantly(f"{number}", "Yardıma ihtiyacım var. "
                                      "Bu mesaj cankurtaran asistan Moli tarafından"
                                      "gönderilmiştir.", 30, tab_close=True)

            def countdown(time_sec):
                while time_sec:
                    mins, secs = divmod(time_sec, 60)
                    timeformat = '{:02d}:{:02d}'.format(mins, secs)
                    print(timeformat, end='\r')
                    time.sleep(1)
                    time_sec -= 1

                kit.sendwhatmsg_instantly(f"{number}", "Yardıma ihtiyacım var. "
                                          "Bu mesaj cankurtaran asistan Moli tarafından "
                                          "gönderilmiştir.", 30, tab_close=True)
            countdown(60)


def uyanma_fonksiyonu(metin):
    if metin == "yardım" or metin == "hey" or metin == "imdat":
        asistan.seslendirme("dinliyorum...")
        cevap = asistan.mikrofon()
        if cevap != "":
            asistan.ses_karslik(cevap)


while True:
    ses = asistan.mikrofon()
    if ses != " ":
        ses = ses.lower()
        print(ses)
        uyanma_fonksiyonu(ses)
        acil_durum()
