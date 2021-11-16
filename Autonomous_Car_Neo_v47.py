

import os
import time
import datetime
import threading
from bluetooth import *
import RPi.GPIO as GPIO


class genel():

    arac_hareket_halinde_mi                     = False
    aracin_yonu                                 = None
    otomatik_mesafe_olcum_thread_calissin_mi    = True
    isik_olcum_thread_calissin_mi               = True
    mesafe_sensoru_tek_seferde_olcum_sayisi     = 10
    mesafe_sensorleri_adlari                    = ["sol", "ön-sol", "ön-orta", "ön-sağ", "sağ", "arka-sağ", "arka-orta", "arka-sol"]
    aracin_cevredeki_nesnelerle_mesafeleri      = {"sol": 0, "ön-sol":0, "ön-orta":0, "ön-sağ":0, "sağ":0, "arka-sağ":0, "arka-orta":0, "arka-sol":0}
    arac_dururken_mesafe_olcumu_kritik_deger    = 25   # cm cinsinden
    arac_hareket_halindeyken_mesafe_olcumu_kritik_deger = 40    # cm cinsinde
    arac_dururken_kritik_mesafede_nesne_olan_yonler = []
    arac_hareket_halindeyken_kritik_mesafede_nesne_olan_yonler = []
    surekli_mod                                 = "OFF"
    aracin_durdugu_an                           = datetime.datetime.now()

    def arac_durdu():
        genel.sag_motorlar_pwm.ChangeDutyCycle(0)
        genel.sol_motorlar_pwm.ChangeDutyCycle(0)
        GPIO.output(genel.sag_motorlar_one_hareket_pini, False)
        GPIO.output(genel.sol_motorlar_one_hareket_pini, False)
        GPIO.output(genel.sag_motorlar_arkaya_hareket_pini, False)
        GPIO.output(genel.sol_motorlar_arkaya_hareket_pini, False)
        genel.arka_geri_vites_lambasini_sondur()
        genel.arac_hareket_halinde_mi   = False
        genel.aracin_yonu               = None
        genel.aracin_durdugu_an         = datetime.datetime.now()

    def arac_duz_ileri_gidiyor():
        if (not genel.arac_hareket_halinde_mi and "ön-orta" not in genel.arac_dururken_kritik_mesafede_nesne_olan_yonler and \
            "ön-sol" not in genel.arac_dururken_kritik_mesafede_nesne_olan_yonler and \
            "ön-sağ" not in genel.arac_dururken_kritik_mesafede_nesne_olan_yonler) or \
        (genel.arac_hareket_halinde_mi and "ön-orta" not in genel.arac_hareket_halindeyken_kritik_mesafede_nesne_olan_yonler):
            genel.sag_motorlar_pwm.ChangeDutyCycle(100)
            genel.sol_motorlar_pwm.ChangeDutyCycle(100)
            GPIO.output(genel.sag_motorlar_one_hareket_pini, True)
            GPIO.output(genel.sol_motorlar_one_hareket_pini, True)
            GPIO.output(genel.sag_motorlar_arkaya_hareket_pini, False)
            GPIO.output(genel.sol_motorlar_arkaya_hareket_pini, False)
            genel.arka_fren_lambalarini_sondur()
            genel.arka_geri_vites_lambasini_sondur()
            genel.arac_hareket_halinde_mi   = True
            genel.aracin_yonu               = "Düz İleri"
        else:
            genel.arka_fren_lambalarini_yak_sondur_yak()
            print("\n****** ARACIN HAREKET EDECEĞİ YÖNDE KRİTİK MESAFEDE NESNE ALGILANDI, ARAÇ HAREKET ETTİRİLMEDİ\n")

    def arac_duz_geri_gidiyor():
        if (not genel.arac_hareket_halinde_mi and "arka-orta" not in genel.arac_dururken_kritik_mesafede_nesne_olan_yonler and \
            "arka-sağ" not in genel.arac_dururken_kritik_mesafede_nesne_olan_yonler and \
            "arka-sol" not in genel.arac_dururken_kritik_mesafede_nesne_olan_yonler) or \
        (genel.arac_hareket_halinde_mi and "arka-orta" not in genel.arac_hareket_halindeyken_kritik_mesafede_nesne_olan_yonler):
            genel.sag_motorlar_pwm.ChangeDutyCycle(100)
            genel.sol_motorlar_pwm.ChangeDutyCycle(100)        
            GPIO.output(genel.sag_motorlar_one_hareket_pini, False)
            GPIO.output(genel.sol_motorlar_one_hareket_pini, False)
            GPIO.output(genel.sag_motorlar_arkaya_hareket_pini, True)
            GPIO.output(genel.sol_motorlar_arkaya_hareket_pini, True)
            genel.arka_fren_lambalarini_sondur()
            genel.arka_geri_vites_lambasini_yak()
            genel.arac_hareket_halinde_mi   = True
            genel.aracin_yonu               = "Düz Geri"
        else:
            genel.arka_fren_lambalarini_yak_sondur_yak()
            print("\n****** ARACIN HAREKET EDECEĞİ YÖNDE KRİTİK MESAFEDE NESNE ALGILANDI, ARAÇ HAREKET ETTİRİLMEDİ\n")

    def arac_ileri_sola_donuyor():
        if (not genel.arac_hareket_halinde_mi and "ön-orta" not in genel.arac_dururken_kritik_mesafede_nesne_olan_yonler and \
            "ön-sol" not in genel.arac_dururken_kritik_mesafede_nesne_olan_yonler) or (genel.arac_hareket_halinde_mi and \
            "ön-orta" not in genel.arac_hareket_halindeyken_kritik_mesafede_nesne_olan_yonler and \
            "ön-sol" not in genel.arac_hareket_halindeyken_kritik_mesafede_nesne_olan_yonler):
            genel.sag_motorlar_pwm.ChangeDutyCycle(100)
            genel.sol_motorlar_pwm.ChangeDutyCycle(25)        
            GPIO.output(genel.sag_motorlar_one_hareket_pini, True)
            GPIO.output(genel.sol_motorlar_one_hareket_pini, True)
            GPIO.output(genel.sag_motorlar_arkaya_hareket_pini, False)
            GPIO.output(genel.sol_motorlar_arkaya_hareket_pini, False)
            genel.arka_fren_lambalarini_sondur()
            genel.arka_geri_vites_lambasini_sondur()        
            genel.arac_hareket_halinde_mi   = True
            genel.aracin_yonu               = "İleri Sol"
        else:
            genel.arka_fren_lambalarini_yak_sondur_yak()
            print("\n****** ARACIN HAREKET EDECEĞİ YÖNDE KRİTİK MESAFEDE NESNE ALGILANDI, ARAÇ HAREKET ETTİRİLMEDİ\n")

    def arac_ileri_saga_donuyor():
        if (not genel.arac_hareket_halinde_mi and "ön-orta" not in genel.arac_dururken_kritik_mesafede_nesne_olan_yonler and \
            "ön-sağ" not in genel.arac_dururken_kritik_mesafede_nesne_olan_yonler) or (genel.arac_hareket_halinde_mi and \
            "ön-orta" not in genel.arac_hareket_halindeyken_kritik_mesafede_nesne_olan_yonler and \
            "ön-sağ" not in genel.arac_hareket_halindeyken_kritik_mesafede_nesne_olan_yonler):
            genel.sag_motorlar_pwm.ChangeDutyCycle(25)
            genel.sol_motorlar_pwm.ChangeDutyCycle(100)        
            GPIO.output(genel.sag_motorlar_one_hareket_pini, True)
            GPIO.output(genel.sol_motorlar_one_hareket_pini, True)
            GPIO.output(genel.sag_motorlar_arkaya_hareket_pini, False)
            GPIO.output(genel.sol_motorlar_arkaya_hareket_pini, False)
            genel.arka_fren_lambalarini_sondur()
            genel.arka_geri_vites_lambasini_sondur()        
            genel.arac_hareket_halinde_mi   = True
            genel.aracin_yonu               = "İleri Sağ"
        else:
            genel.arka_fren_lambalarini_yak_sondur_yak()
            print("\n****** ARACIN HAREKET EDECEĞİ YÖNDE KRİTİK MESAFEDE NESNE ALGILANDI, ARAÇ HAREKET ETTİRİLMEDİ\n")

    def arac_geri_sola_donuyor():
        if (not genel.arac_hareket_halinde_mi and "arka-orta" not in genel.arac_dururken_kritik_mesafede_nesne_olan_yonler and \
            "arka-sol" not in genel.arac_dururken_kritik_mesafede_nesne_olan_yonler) or (genel.arac_hareket_halinde_mi and \
            "arka-orta" not in genel.arac_hareket_halindeyken_kritik_mesafede_nesne_olan_yonler and \
            "arka-sol" not in genel.arac_hareket_halindeyken_kritik_mesafede_nesne_olan_yonler):
            genel.sag_motorlar_pwm.ChangeDutyCycle(100)
            genel.sol_motorlar_pwm.ChangeDutyCycle(25)        
            GPIO.output(genel.sag_motorlar_one_hareket_pini, False)
            GPIO.output(genel.sol_motorlar_one_hareket_pini, False)
            GPIO.output(genel.sag_motorlar_arkaya_hareket_pini, True)
            GPIO.output(genel.sol_motorlar_arkaya_hareket_pini, True)
            genel.arka_fren_lambalarini_sondur()
            genel.arka_geri_vites_lambasini_yak()        
            genel.arac_hareket_halinde_mi   = True
            genel.aracin_yonu               = "Geri Sol"
        else:
            genel.arka_fren_lambalarini_yak_sondur_yak()
            print("\n****** ARACIN HAREKET EDECEĞİ YÖNDE KRİTİK MESAFEDE NESNE ALGILANDI, ARAÇ HAREKET ETTİRİLMEDİ\n")

    def arac_geri_saga_donuyor():
        if (not genel.arac_hareket_halinde_mi and "arka-orta" not in genel.arac_dururken_kritik_mesafede_nesne_olan_yonler and \
            "arka-sağ" not in genel.arac_dururken_kritik_mesafede_nesne_olan_yonler) or (genel.arac_hareket_halinde_mi and \
            "arka-orta" not in genel.arac_hareket_halindeyken_kritik_mesafede_nesne_olan_yonler and \
            "arka-sağ" not in genel.arac_hareket_halindeyken_kritik_mesafede_nesne_olan_yonler):
            genel.sag_motorlar_pwm.ChangeDutyCycle(25)
            genel.sol_motorlar_pwm.ChangeDutyCycle(100)        
            GPIO.output(genel.sag_motorlar_one_hareket_pini, False)
            GPIO.output(genel.sol_motorlar_one_hareket_pini, False)
            GPIO.output(genel.sag_motorlar_arkaya_hareket_pini, True)
            GPIO.output(genel.sol_motorlar_arkaya_hareket_pini, True)
            genel.arka_fren_lambalarini_sondur()
            genel.arka_geri_vites_lambasini_yak()        
            genel.arac_hareket_halinde_mi   = True
            genel.aracin_yonu               = "Geri Sağ"
        else:
            genel.arka_fren_lambalarini_yak_sondur_yak()
            print("\n****** ARACIN HAREKET EDECEĞİ YÖNDE KRİTİK MESAFEDE NESNE ALGILANDI, ARAÇ HAREKET ETTİRİLMEDİ\n")

    def arac_saga_360_donuyor():
        if (not genel.arac_hareket_halinde_mi and "sağ" not in genel.arac_dururken_kritik_mesafede_nesne_olan_yonler) or \
        (genel.arac_hareket_halinde_mi and "sağ" not in genel.arac_hareket_halindeyken_kritik_mesafede_nesne_olan_yonler):
            genel.sag_motorlar_pwm.ChangeDutyCycle(100)
            genel.sol_motorlar_pwm.ChangeDutyCycle(100)        
            GPIO.output(genel.sag_motorlar_one_hareket_pini, False)
            GPIO.output(genel.sol_motorlar_one_hareket_pini, True)
            GPIO.output(genel.sag_motorlar_arkaya_hareket_pini, True)
            GPIO.output(genel.sol_motorlar_arkaya_hareket_pini, False)
            genel.arka_fren_lambalarini_sondur()
            genel.arka_geri_vites_lambasini_sondur()
            genel.arac_hareket_halinde_mi   = True
            genel.aracin_yonu               = "Sağa 360"
        else:
            genel.arka_fren_lambalarini_yak_sondur_yak()
            print("\n****** ARACIN HAREKET EDECEĞİ YÖNDE KRİTİK MESAFEDE NESNE ALGILANDI, ARAÇ HAREKET ETTİRİLMEDİ\n")

    def arac_sola_360_donuyor():
        if (not genel.arac_hareket_halinde_mi and "sol" not in genel.arac_dururken_kritik_mesafede_nesne_olan_yonler) or \
        (genel.arac_hareket_halinde_mi and "sol" not in genel.arac_hareket_halindeyken_kritik_mesafede_nesne_olan_yonler):
            genel.sag_motorlar_pwm.ChangeDutyCycle(100)
            genel.sol_motorlar_pwm.ChangeDutyCycle(100)        
            GPIO.output(genel.sag_motorlar_one_hareket_pini, True)
            GPIO.output(genel.sol_motorlar_one_hareket_pini, False)
            GPIO.output(genel.sag_motorlar_arkaya_hareket_pini, False)
            GPIO.output(genel.sol_motorlar_arkaya_hareket_pini, True)
            genel.arka_fren_lambalarini_sondur()
            genel.arka_geri_vites_lambasini_sondur()
            genel.arac_hareket_halinde_mi   = True
            genel.aracin_yonu               = "Sola 360"
        else:
            genel.arka_fren_lambalarini_yak_sondur_yak()
            print("\n****** ARACIN HAREKET EDECEĞİ YÖNDE KRİTİK MESAFEDE NESNE ALGILANDI, ARAÇ HAREKET ETTİRİLMEDİ\n")

    def arka_fren_lambalarini_yak():
        GPIO.output(genel.arka_alt_fren_lambalari_kontrol_pini, True)

    def arka_fren_lambalarini_sondur():
        GPIO.output(genel.arka_alt_fren_lambalari_kontrol_pini, False)

    def arka_fren_lambalarini_yak_sondur_yak():
        genel.arka_fren_lambalarini_yak()
        time.sleep(0.2)
        genel.arka_fren_lambalarini_sondur()
        time.sleep(0.2)
        genel.arka_fren_lambalarini_yak()
        time.sleep(0.2)
        genel.arka_fren_lambalarini_sondur()
        time.sleep(0.2)
        genel.arka_fren_lambalarini_yak()

    def on_alt_farlari_yak():
        GPIO.output(genel.on_alt_farlar_kontrol_pini, True)

    def on_alt_farlari_sondur():
        GPIO.output(genel.on_alt_farlar_kontrol_pini, False)

    def on_ust_farlari_yak():
        GPIO.output(genel.on_ust_farlar_kontrol_pini, True)

    def on_ust_farlari_sondur():
        GPIO.output(genel.on_ust_farlar_kontrol_pini, False)

    def arka_geri_vites_lambasini_yak():
        GPIO.output(genel.arka_ust_geri_vites_lambasi_kontrol_pini, True)

    def arka_geri_vites_lambasini_sondur():
        GPIO.output(genel.arka_ust_geri_vites_lambasi_kontrol_pini, False)

    def tum_farlari_yak():
        genel.on_alt_farlari_yak()
        genel.on_ust_farlari_yak()
        genel.arka_fren_lambalarini_yak()
        genel.arka_geri_vites_lambasini_yak()

    def tum_farlari_sondur():
        genel.on_alt_farlari_sondur()
        genel.on_ust_farlari_sondur()
        genel.arka_fren_lambalarini_sondur()
        genel.arka_geri_vites_lambasini_sondur()

    def multiplexer_channel_and_value_set_function(pin, durum):
        if pin == "C0":
            GPIO.output(genel.multiplexer_SO_kontrol_pini, False)
            GPIO.output(genel.multiplexer_S1_kontrol_pini, False)
            GPIO.output(genel.multiplexer_S2_kontrol_pini, False)
            GPIO.output(genel.multiplexer_S3_kontrol_pini, False)
        elif pin == "C1":
            GPIO.output(genel.multiplexer_SO_kontrol_pini, True)
            GPIO.output(genel.multiplexer_S1_kontrol_pini, False)
            GPIO.output(genel.multiplexer_S2_kontrol_pini, False)
            GPIO.output(genel.multiplexer_S3_kontrol_pini, False)
        elif pin == "C2":
            GPIO.output(genel.multiplexer_SO_kontrol_pini, False)
            GPIO.output(genel.multiplexer_S1_kontrol_pini, True)
            GPIO.output(genel.multiplexer_S2_kontrol_pini, False)
            GPIO.output(genel.multiplexer_S3_kontrol_pini, False)
        elif pin == "C3":
            GPIO.output(genel.multiplexer_SO_kontrol_pini, True)
            GPIO.output(genel.multiplexer_S1_kontrol_pini, True)
            GPIO.output(genel.multiplexer_S2_kontrol_pini, False)
            GPIO.output(genel.multiplexer_S3_kontrol_pini, False)
        elif pin == "C4":
            GPIO.output(genel.multiplexer_SO_kontrol_pini, False)
            GPIO.output(genel.multiplexer_S1_kontrol_pini, False)
            GPIO.output(genel.multiplexer_S2_kontrol_pini, True)
            GPIO.output(genel.multiplexer_S3_kontrol_pini, False)
        elif pin == "C5":
            GPIO.output(genel.multiplexer_SO_kontrol_pini, True)
            GPIO.output(genel.multiplexer_S1_kontrol_pini, False)
            GPIO.output(genel.multiplexer_S2_kontrol_pini, True)
            GPIO.output(genel.multiplexer_S3_kontrol_pini, False)
        elif pin == "C6":
            GPIO.output(genel.multiplexer_SO_kontrol_pini, False)
            GPIO.output(genel.multiplexer_S1_kontrol_pini, True)
            GPIO.output(genel.multiplexer_S2_kontrol_pini, True)
            GPIO.output(genel.multiplexer_S3_kontrol_pini, False)
        elif pin == "C7":
            GPIO.output(genel.multiplexer_SO_kontrol_pini, True)
            GPIO.output(genel.multiplexer_S1_kontrol_pini, True)
            GPIO.output(genel.multiplexer_S2_kontrol_pini, True)
            GPIO.output(genel.multiplexer_S3_kontrol_pini, False)
        elif pin == "C8":
            GPIO.output(genel.multiplexer_SO_kontrol_pini, False)
            GPIO.output(genel.multiplexer_S1_kontrol_pini, False)
            GPIO.output(genel.multiplexer_S2_kontrol_pini, False)
            GPIO.output(genel.multiplexer_S3_kontrol_pini, True)
        elif pin == "C9":
            GPIO.output(genel.multiplexer_SO_kontrol_pini, True)
            GPIO.output(genel.multiplexer_S1_kontrol_pini, False)
            GPIO.output(genel.multiplexer_S2_kontrol_pini, False)
            GPIO.output(genel.multiplexer_S3_kontrol_pini, True)
        elif pin == "C10":
            GPIO.output(genel.multiplexer_SO_kontrol_pini, False)
            GPIO.output(genel.multiplexer_S1_kontrol_pini, True)
            GPIO.output(genel.multiplexer_S2_kontrol_pini, False)
            GPIO.output(genel.multiplexer_S3_kontrol_pini, True)
        elif pin == "C11":
            GPIO.output(genel.multiplexer_SO_kontrol_pini, True)
            GPIO.output(genel.multiplexer_S1_kontrol_pini, True)
            GPIO.output(genel.multiplexer_S2_kontrol_pini, False)
            GPIO.output(genel.multiplexer_S3_kontrol_pini, True)
        elif pin == "C12":
            GPIO.output(genel.multiplexer_SO_kontrol_pini, False)
            GPIO.output(genel.multiplexer_S1_kontrol_pini, False)
            GPIO.output(genel.multiplexer_S2_kontrol_pini, True)
            GPIO.output(genel.multiplexer_S3_kontrol_pini, True)
        elif pin == "C13":
            GPIO.output(genel.multiplexer_SO_kontrol_pini, True)
            GPIO.output(genel.multiplexer_S1_kontrol_pini, False)
            GPIO.output(genel.multiplexer_S2_kontrol_pini, True)
            GPIO.output(genel.multiplexer_S3_kontrol_pini, True)
        elif pin == "C14":
            GPIO.output(genel.multiplexer_SO_kontrol_pini, False)
            GPIO.output(genel.multiplexer_S1_kontrol_pini, True)
            GPIO.output(genel.multiplexer_S2_kontrol_pini, True)
            GPIO.output(genel.multiplexer_S3_kontrol_pini, True)                                                                        
        elif pin == "C15":
            GPIO.output(genel.multiplexer_SO_kontrol_pini, True)
            GPIO.output(genel.multiplexer_S1_kontrol_pini, True)
            GPIO.output(genel.multiplexer_S2_kontrol_pini, True)
            GPIO.output(genel.multiplexer_S3_kontrol_pini, True)

        if durum:
            GPIO.output(genel.multiplexer_SIG_kontrol_pini, True)
        else:
            GPIO.output(genel.multiplexer_SIG_kontrol_pini, False)

    def otomatik_mesafe_olcum():
        while genel.otomatik_mesafe_olcum_thread_calissin_mi:
            for sira in range(len(genel.mesafe_sensorleri_adlari)):
                # önce tüm mesafe sensörleri trigger pin'lerini low yapıyoruz
                for k in genel.mesafe_sensorleri_trigger_pinleri:
                    genel.multiplexer_channel_and_value_set_function(k, False)

                sensor_tek_seferde_olcum_degerleri = []

                for i in range(genel.mesafe_sensoru_tek_seferde_olcum_sayisi):
                    pulse_start_time    = None
                    pulse_end_time      = None
                    pulse_duration      = None
                    distance            = None
                    pulse_start_i_beklemeye_baslama_zamani = None
                    pulse_end_i_beklemeye_baslama_zamani = None
                    # ölçüm yapacağımız mesafe sensörünün trigger pinini 10 mikro saniye süreyle high yapıyoruz\
                    # yani 10 mikro saniye sinyal gönderiyoruz, sonra tekrar low yapıyoruz
                    genel.multiplexer_channel_and_value_set_function(genel.mesafe_sensorleri_trigger_pinleri[sira], True)
                    time.sleep(0.00001)
                    genel.multiplexer_channel_and_value_set_function(genel.mesafe_sensorleri_trigger_pinleri[sira], False)

                    # mesafe sensörünün echo pininin sinyali almaya başlamasını bekliyoruz, sinyali aldığı andan önceki anı\
                    # sinyali alışın başlangıç zamanı olarak keydediyoruz
                    pulse_start_i_beklemeye_baslama_zamani = datetime.datetime.now()
                    while GPIO.input(genel.mesafe_sensorleri_echo_pinleri[sira]) == 0:
                        pulse_start_time = datetime.datetime.now()
                        if datetime.datetime.now() - pulse_start_i_beklemeye_baslama_zamani >= datetime.timedelta(milliseconds=5):
                            break

                    # sinyali almaya başladıktan sonra bitirmesini bekliyor ve bitirdiği anı kaydediyoruz
                    if pulse_start_time is not None:
                        pulse_end_i_beklemeye_baslama_zamani = datetime.datetime.now()
                        while GPIO.input(genel.mesafe_sensorleri_echo_pinleri[sira]) == 1:
                            pulse_end_time = datetime.datetime.now()
                            if datetime.datetime.now() - pulse_end_i_beklemeye_baslama_zamani >= datetime.timedelta(milliseconds=5):
                                break

                    if pulse_start_time is not None and pulse_end_time is not None:
                        distance = round((pulse_end_time - pulse_start_time).total_seconds() * 17150, 2)
                        sensor_tek_seferde_olcum_degerleri.append(distance)
                    
                    sensor_tek_seferde_olcum_degerleri = sorted(sensor_tek_seferde_olcum_degerleri)

                    if sensor_tek_seferde_olcum_degerleri == []:
                        genel.aracin_cevredeki_nesnelerle_mesafeleri[genel.mesafe_sensorleri_adlari[sira]] = 0
                    else:
                        genel.aracin_cevredeki_nesnelerle_mesafeleri[genel.mesafe_sensorleri_adlari[sira]] = int(sum(sensor_tek_seferde_olcum_degerleri)/len(sensor_tek_seferde_olcum_degerleri))

                if 0 < genel.aracin_cevredeki_nesnelerle_mesafeleri[genel.mesafe_sensorleri_adlari[sira]] <= genel.arac_dururken_mesafe_olcumu_kritik_deger:
                    if genel.mesafe_sensorleri_adlari[sira] not in genel.arac_dururken_kritik_mesafede_nesne_olan_yonler:
                        genel.arac_dururken_kritik_mesafede_nesne_olan_yonler.append(genel.mesafe_sensorleri_adlari[sira])
                    if genel.mesafe_sensorleri_adlari[sira] not in genel.arac_hareket_halindeyken_kritik_mesafede_nesne_olan_yonler:
                        genel.arac_hareket_halindeyken_kritik_mesafede_nesne_olan_yonler.append(genel.mesafe_sensorleri_adlari[sira])
                elif genel.arac_dururken_mesafe_olcumu_kritik_deger < genel.aracin_cevredeki_nesnelerle_mesafeleri[genel.mesafe_sensorleri_adlari[sira]] <= \
                genel.arac_hareket_halindeyken_mesafe_olcumu_kritik_deger:
                    if genel.mesafe_sensorleri_adlari[sira] in genel.arac_dururken_kritik_mesafede_nesne_olan_yonler:
                        genel.arac_dururken_kritik_mesafede_nesne_olan_yonler.remove(genel.mesafe_sensorleri_adlari[sira])
                    if genel.mesafe_sensorleri_adlari[sira] not in genel.arac_hareket_halindeyken_kritik_mesafede_nesne_olan_yonler:
                        genel.arac_hareket_halindeyken_kritik_mesafede_nesne_olan_yonler.append(genel.mesafe_sensorleri_adlari[sira])
                elif genel.aracin_cevredeki_nesnelerle_mesafeleri[genel.mesafe_sensorleri_adlari[sira]] > genel.arac_hareket_halindeyken_mesafe_olcumu_kritik_deger:
                    if genel.mesafe_sensorleri_adlari[sira] in genel.arac_dururken_kritik_mesafede_nesne_olan_yonler:
                        genel.arac_dururken_kritik_mesafede_nesne_olan_yonler.remove(genel.mesafe_sensorleri_adlari[sira])
                    if genel.mesafe_sensorleri_adlari[sira] in genel.arac_hareket_halindeyken_kritik_mesafede_nesne_olan_yonler:
                        genel.arac_hareket_halindeyken_kritik_mesafede_nesne_olan_yonler.remove(genel.mesafe_sensorleri_adlari[sira])

                if genel.arac_hareket_halinde_mi:
                    if (genel.aracin_yonu == "Düz İleri" and "ön-orta" in genel.arac_hareket_halindeyken_kritik_mesafede_nesne_olan_yonler) or \
                    (genel.aracin_yonu == "Düz Geri" and "arka-orta" in genel.arac_hareket_halindeyken_kritik_mesafede_nesne_olan_yonler) or \
                    (genel.aracin_yonu == "İleri Sol" and ("ön-orta" in genel.arac_hareket_halindeyken_kritik_mesafede_nesne_olan_yonler or \
                        "ön-sol" in genel.arac_hareket_halindeyken_kritik_mesafede_nesne_olan_yonler)) or \
                    (genel.aracin_yonu == "İleri Sağ" and ("ön-orta" in genel.arac_hareket_halindeyken_kritik_mesafede_nesne_olan_yonler or \
                        "ön-sağ" in genel.arac_hareket_halindeyken_kritik_mesafede_nesne_olan_yonler)) or \
                    (genel.aracin_yonu == "Geri Sol" and ("arka-orta" in genel.arac_hareket_halindeyken_kritik_mesafede_nesne_olan_yonler or \
                        "arka-sol" in genel.arac_hareket_halindeyken_kritik_mesafede_nesne_olan_yonler)) or \
                    (genel.aracin_yonu == "Geri Sağ" and ("arka-orta" in genel.arac_hareket_halindeyken_kritik_mesafede_nesne_olan_yonler or \
                        "arka-sağ" in genel.arac_hareket_halindeyken_kritik_mesafede_nesne_olan_yonler)) or \
                    (genel.aracin_yonu == "Sağa 360" and "sağ" in genel.arac_hareket_halindeyken_kritik_mesafede_nesne_olan_yonler) or \
                    (genel.aracin_yonu == "Sola 360" and "sol" in genel.arac_hareket_halindeyken_kritik_mesafede_nesne_olan_yonler):
                        genel.arac_durdu()
                        genel.arka_fren_lambalarini_yak()
                        print("\n****** ARACIN HAREKET ETTİĞİ YÖNDE KRİTİK MESAFEDE NESNE ALGILANDI ARAÇ DURDURULDU")
                        #genel.arka_fren_lambalarini_yak_sondur_yak()

            time.sleep(0.1)
            
            #print("Mesafe Ölçümü :", genel.aracin_cevredeki_nesnelerle_mesafeleri)

    def ldr_kontrol():
        while genel.isik_olcum_thread_calissin_mi:
            genel.ldr_say = 0
      
            #Output on the pin for 
            GPIO.setup(genel.ldr_sensor_pini, GPIO.OUT)
            GPIO.output(genel.ldr_sensor_pini, GPIO.LOW)
            time.sleep(1)

            #Change the pin back to input
            GPIO.setup(genel.ldr_sensor_pini, GPIO.IN)
          
            #Count until the pin goes high
            while (GPIO.input(genel.ldr_sensor_pini) == GPIO.LOW):
                genel.ldr_say += 1

            if genel.ldr_say > 80 and GPIO.input(genel.on_alt_farlar_kontrol_pini) == GPIO.LOW:
                genel.ldr_durum = "Karanlık"
                print("\nKARANLIK oldu farlar yakıldı\n")
                genel.on_alt_farlari_yak()
            else:
                genel.ldr_durum = "Aydınlık"

            time.sleep(1)

            #print("\nLDR : ", genel.ldr_say, genel.ldr_durum, "\n")

    def ses_duyuldu(*args):
        if not genel.arac_hareket_halinde_mi and datetime.datetime.now() > genel.aracin_durdugu_an + datetime.timedelta(seconds=3):
            genel.ses_geldi_mi = True
            print("\nSES SENSÖRÜ ses algıladı\n")

            ses_on_alt_lambalarin_durumu            = GPIO.input(genel.on_alt_farlar_kontrol_pini)
            ses_on_ust_lambalarin_durumu            = GPIO.input(genel.on_ust_farlar_kontrol_pini)
            ses_arka_fren_lambalarinin_durumu       = GPIO.input(genel.arka_alt_fren_lambalari_kontrol_pini)
            ses_arka_geri_vites_lambasinin_durumu   = GPIO.input(genel.arka_ust_geri_vites_lambasi_kontrol_pini)

            genel.tum_farlari_sondur()
            time.sleep(0.2)
            genel.tum_farlari_yak()
            time.sleep(0.3)
            genel.tum_farlari_sondur()
            time.sleep(0.3)
            genel.tum_farlari_yak()
            time.sleep(0.3)
            genel.tum_farlari_sondur()

            if ses_on_alt_lambalarin_durumu: genel.on_alt_farlari_yak()
            if ses_on_ust_lambalarin_durumu: genel.on_ust_farlari_yak()
            if ses_arka_fren_lambalarinin_durumu: genel.arka_fren_lambalarini_yak()
            if ses_arka_geri_vites_lambasinin_durumu: genel.arka_geri_vites_lambasini_yak()

            del ses_on_alt_lambalarin_durumu, ses_on_ust_lambalarin_durumu, ses_arka_fren_lambalarinin_durumu, ses_arka_geri_vites_lambasinin_durumu

            genel.ses_geldi_mi = False

    def hareket_algilandi(*args):
        if not genel.arac_hareket_halinde_mi and datetime.datetime.now() > genel.aracin_durdugu_an + datetime.timedelta(seconds=3):
            print("\n***************** PIR SENSOR hareket algıladı ******************\n")
            genel.hareket_algilandi_mi = True

            hareket_on_alt_lambalarin_durumu            = GPIO.input(genel.on_alt_farlar_kontrol_pini)
            hareket_on_ust_lambalarin_durumu            = GPIO.input(genel.on_ust_farlar_kontrol_pini)
            hareket_arka_fren_lambalarinin_durumu       = GPIO.input(genel.arka_alt_fren_lambalari_kontrol_pini)
            hareket_arka_geri_vites_lambasinin_durumu   = GPIO.input(genel.arka_ust_geri_vites_lambasi_kontrol_pini)

            genel.tum_farlari_sondur()
            time.sleep(0.2)
            genel.on_alt_farlari_yak()
            genel.arka_fren_lambalarini_yak()
            time.sleep(0.3)
            genel.on_alt_farlari_sondur()
            genel.arka_fren_lambalarini_sondur()
            genel.on_ust_farlari_yak()
            genel.arka_geri_vites_lambasini_yak()
            time.sleep(0.3)
            genel.on_ust_farlari_sondur()
            genel.arka_geri_vites_lambasini_sondur()
            genel.on_alt_farlari_yak()
            genel.arka_fren_lambalarini_yak()
            time.sleep(0.3)
            genel.on_alt_farlari_sondur()
            genel.arka_fren_lambalarini_sondur()
            genel.on_ust_farlari_yak()
            genel.arka_geri_vites_lambasini_yak()
            time.sleep(0.3)
            genel.on_ust_farlari_sondur()
            genel.arka_geri_vites_lambasini_sondur()
            genel.on_alt_farlari_yak()
            genel.arka_fren_lambalarini_yak()
            time.sleep(0.3)
            genel.on_alt_farlari_sondur()
            genel.arka_fren_lambalarini_sondur()
            genel.on_ust_farlari_yak()
            genel.arka_geri_vites_lambasini_yak()
            time.sleep(0.3)
            genel.tum_farlari_sondur()

            if hareket_on_alt_lambalarin_durumu: genel.on_alt_farlari_yak()
            if hareket_on_ust_lambalarin_durumu: genel.on_ust_farlari_yak()
            if hareket_arka_fren_lambalarinin_durumu: genel.arka_fren_lambalarini_yak()
            if hareket_arka_geri_vites_lambasinin_durumu: genel.arka_geri_vites_lambasini_yak()

            del hareket_on_alt_lambalarin_durumu, hareket_on_ust_lambalarin_durumu, hareket_arka_fren_lambalarinin_durumu, hareket_arka_geri_vites_lambasinin_durumu

            while 1:
                if not GPIO.input(genel.pir_sensor_pini):
                    print("\n************** algılanan hareket sona erdi hareket_algilandi fonksiyonundan çıkılıyor ***************\n")
                    genel.hareket_algilandi_mi = False        
                    break

    def selektor_yap():
        selektor_on_alt_lambalarin_durumu            = GPIO.input(genel.on_alt_farlar_kontrol_pini)
        selektor_on_ust_lambalarin_durumu            = GPIO.input(genel.on_ust_farlar_kontrol_pini)

        for i in range(2):
            genel.on_alt_farlari_yak()
            genel.on_ust_farlari_yak()
            time.sleep(0.2)
            genel.on_alt_farlari_sondur()
            genel.on_ust_farlari_sondur()
            time.sleep(0.1)
            
        if selektor_on_alt_lambalarin_durumu: genel.on_alt_farlari_yak()
        if selektor_on_ust_lambalarin_durumu: genel.on_ust_farlari_yak()

        del selektor_on_alt_lambalarin_durumu, selektor_on_ust_lambalarin_durumu

    def bt_baglanti_isik_hareketi():
        print("Bluetooth bağlantı yapıldı, BT ışık hareketi yapılıyor")
        genel.tum_farlari_sondur()
        for i in range(3):
            genel.on_alt_farlari_yak()
            genel.on_ust_farlari_sondur()
            time.sleep(0.2)
            genel.on_ust_farlari_yak()
            genel.on_alt_farlari_sondur()
            time.sleep(0.2)
        genel.on_ust_farlari_sondur()


    # Multiplexer kontrol pinleri
    multiplexer_SO_kontrol_pini                 = 27        # Board Pin #13 output
    multiplexer_S1_kontrol_pini                 = 17        # Board Pin #11 output
    multiplexer_S2_kontrol_pini                 = 4         # Board Pin #7 output
    multiplexer_S3_kontrol_pini                 = 3         # Board Pin #5 output
    multiplexer_SIG_kontrol_pini                = 2         # Board Pin #3 output

    # C ile başlayanlar Multiplexer pinleri
    # motor kontrol pin değişkenleri
    sag_motorlar_one_hareket_pini               = 22        # Board Pin #15 output
    sag_motorlar_arkaya_hareket_pini            = 11        # Board Pin #23 output
    sol_motorlar_one_hareket_pini               = 9         # Board Pin #21 output
    sol_motorlar_arkaya_hareket_pini            = 10        # Board Pin #19 output
    sag_motorlar_pwm_pini                       = 12        # Board Pin #32 output
    sol_motorlar_pwm_pini                       = 13        # Board Pin #33 output
    sag_motorlar_pwm                            = None
    sol_motorlar_pwm                            = None

    # lamba kontrol pin değişkenleri
    on_alt_farlar_kontrol_pini                  = 26        # Board Pin #37 output
    on_ust_farlar_kontrol_pini                  = 6         # Board Pin #31 output
    arka_alt_fren_lambalari_kontrol_pini        = 21        # Board Pin #40 output
    arka_ust_geri_vites_lambasi_kontrol_pini    = 1         # Board Pin #28 output

    # mesafe sensörleri değişkenleri ve içinde tutuldukları listeler
    on_orta_mesafe_sensoru_trigger_pini         = "C1"
    on_orta_mesafe_sensoru_echo_pini            = 5         # Board Pin #29 input
    on_sag_mesafe_sensoru_trigger_pini          = "C2"
    on_sag_mesafe_sensoru_echo_pini             = 0         # Board Pin #27 input
    on_sol_mesafe_sensoru_trigger_pini          = "C0"
    on_sol_mesafe_sensoru_echo_pini             = 19        # Board Pin #35 input
    sag_mesafe_sensoru_trigger_pini             = "C6"
    sag_mesafe_sensoru_echo_pini                = 18        # Board Pin #12 input
    sol_mesafe_sensoru_trigger_pini             = "C7"
    sol_mesafe_sensoru_echo_pini                = 23        # Board Pin #16 input
    arka_orta_mesafe_sensoru_trigger_pini       = "C4"
    arka_orta_mesafe_sensoru_echo_pini          = 20        # Board Pin #38 input
    arka_sag_mesafe_sensoru_trigger_pini        = "C3"
    arka_sag_mesafe_sensoru_echo_pini           = 16        # Board Pin #36 input
    arka_sol_mesafe_sensoru_trigger_pini        = "C5"
    arka_sol_mesafe_sensoru_echo_pini           = 15        # Board Pin #10 input

    mesafe_sensorleri_trigger_pinleri = []
    mesafe_sensorleri_trigger_pinleri.extend((sol_mesafe_sensoru_trigger_pini, on_sol_mesafe_sensoru_trigger_pini, \
    on_orta_mesafe_sensoru_trigger_pini, on_sag_mesafe_sensoru_trigger_pini, sag_mesafe_sensoru_trigger_pini,\
    arka_sag_mesafe_sensoru_trigger_pini, arka_orta_mesafe_sensoru_trigger_pini, arka_sol_mesafe_sensoru_trigger_pini))

    mesafe_sensorleri_echo_pinleri = []
    mesafe_sensorleri_echo_pinleri.extend((sol_mesafe_sensoru_echo_pini, on_sol_mesafe_sensoru_echo_pini, \
    on_orta_mesafe_sensoru_echo_pini, on_sag_mesafe_sensoru_echo_pini, sag_mesafe_sensoru_echo_pini,\
    arka_sag_mesafe_sensoru_echo_pini, arka_orta_mesafe_sensoru_echo_pini, arka_sol_mesafe_sensoru_echo_pini))

    # üst kattaki sensörlerin pinleri ve değişkenleri
    pir_sensor_pini                             = 24        # Board Pin #18 input
    hareket_algilandi_mi                        = False
    ldr_sensor_pini                             = 25        # Board Pin #22 input
    ldr_say                                     = 0
    ldr_durum                                   = None    
    sound_sensor_pini                           = 7         # Board Pin #26 input
    ses_geldi_mi                                = False

    # Bluetooth Communication Settings
    bt_socket                                   = None
    bt_socket_hazir_mi                          = False
    baglanti_timeout                            = 30
    ic_version                                  = "43_b"

class acilis():

    print("\n\n***************************  LEO ÇALIŞMAYA BAŞLADI  ******************************\n")

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.cleanup()

    # Led kontrol pinleri
    GPIO.setup(genel.on_alt_farlar_kontrol_pini, GPIO.OUT, initial=0)
    GPIO.setup(genel.on_ust_farlar_kontrol_pini, GPIO.OUT, initial=0)
    GPIO.setup(genel.arka_alt_fren_lambalari_kontrol_pini, GPIO.OUT, initial=0)
    GPIO.setup(genel.arka_ust_geri_vites_lambasi_kontrol_pini, GPIO.OUT, initial=0)
    print("\n------------ Açılışta led pinleri ayarlandı ----------------")

    # motor pinleri
    GPIO.setup(genel.sag_motorlar_one_hareket_pini, GPIO.OUT, initial=0)
    GPIO.setup(genel.sag_motorlar_arkaya_hareket_pini, GPIO.OUT, initial=0)    
    GPIO.setup(genel.sol_motorlar_one_hareket_pini, GPIO.OUT, initial=0)
    GPIO.setup(genel.sol_motorlar_arkaya_hareket_pini, GPIO.OUT, initial=0)
    GPIO.setup(genel.sag_motorlar_pwm_pini, GPIO.OUT, initial=0)
    GPIO.setup(genel.sol_motorlar_pwm_pini, GPIO.OUT, initial=0)
    genel.sag_motorlar_pwm = GPIO.PWM(genel.sag_motorlar_pwm_pini, 100)
    genel.sag_motorlar_pwm.start(0)
    genel.sol_motorlar_pwm = GPIO.PWM(genel.sol_motorlar_pwm_pini, 100)
    genel.sol_motorlar_pwm.start(0)
    print("------------ Açılışta motor pinleri ayarlandı ----------------")

    # Mesafe Sensörleri TRIG pinleri Multiplexer'a takılı, Multiplexer kontrol pinleri
    GPIO.setup(genel.multiplexer_SO_kontrol_pini, GPIO.OUT, initial=0)
    GPIO.setup(genel.multiplexer_S1_kontrol_pini, GPIO.OUT, initial=0)
    GPIO.setup(genel.multiplexer_S2_kontrol_pini, GPIO.OUT, initial=0)
    GPIO.setup(genel.multiplexer_S3_kontrol_pini, GPIO.OUT, initial=0)
    GPIO.setup(genel.multiplexer_SIG_kontrol_pini, GPIO.OUT, initial=0)
    # mesafe sensörleri Echo pinleri (Trig pinleri multiplexer üzerinde)
    GPIO.setup(genel.on_orta_mesafe_sensoru_echo_pini, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(genel.on_sag_mesafe_sensoru_echo_pini, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(genel.on_sol_mesafe_sensoru_echo_pini, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(genel.sag_mesafe_sensoru_echo_pini, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(genel.sol_mesafe_sensoru_echo_pini, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(genel.arka_orta_mesafe_sensoru_echo_pini, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(genel.arka_sag_mesafe_sensoru_echo_pini, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(genel.arka_sol_mesafe_sensoru_echo_pini, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    print("------------ Açılışta mesafe sensörü pinleri ayarlandı ----------------")

  
    # Bluetooth socketi tanımlanıyor ve dinlemeye geçiyor
    try:
        genel.bt_socket=BluetoothSocket( RFCOMM )
        genel.bt_socket.bind(("", PORT_ANY))
        genel.bt_socket.listen(1)
        print("------------ Açılışta bluetooth portu hazırlandı ----------------")
        genel.bt_socket_hazir_mi = True
    except Exception as e:
        print("Açılışta bt_socket oluşturulurken hata :", str(e))
        genel.bt_socket_hazir_mi = False

    # üst kattaki sensörlerin pinleri
    # ses geliyor mu diye sürekli kontrol yapıyor
    GPIO.setup(genel.sound_sensor_pini, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(genel.sound_sensor_pini, GPIO.RISING, genel.ses_duyuldu, bouncetime=100)
    # hareket oldu mu diye sürekli kontrol yapıyor
    GPIO.setup(genel.pir_sensor_pini, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(genel.pir_sensor_pini, GPIO.RISING, genel.hareket_algilandi, bouncetime=1000)
    # 8 sensörü çalıştırıp aracın etrafındaki nesnelerle arasındaki mesafeleri ölçen thread, 0.5 saniyede bir güncelliyor
    mesafe_olcumu_thread = threading.Thread(target=genel.otomatik_mesafe_olcum)
    mesafe_olcumu_thread.start()
    # Aydınlık ve karanlık durumunu tespit etmek için 0.5 sn. de bir thread ile ldr ölçümü yapıyoruz
    isik_olcumu_thread = threading.Thread(target=genel.ldr_kontrol)
    isik_olcumu_thread.start()

    print("------Açılışta GPIO event_detect'ler ve thread'ler çalıştırıldı --------")

class ana_program():
    print("\n--------------************ ANA PROGRAM ***********-----------------\n")
    if genel.bt_socket_hazir_mi is True:
        while True:
            print("\n.....Bluetooth üzerinden Client bağlantısı bekleniyor.....")
            bt_baglanti_portu, bt_adresi = genel.bt_socket.accept()
            bt_baglanti_portu.settimeout(genel.baglanti_timeout)
            print("\nBağlanan Bluetooth Client Adresi : ", bt_adresi[0], "    Portu: ", bt_adresi[1])
            genel.bt_baglanti_isik_hareketi()
            print("Bağlanan Bluetooth Client'ından mesaj alinmasi bekleniyor...")
            while True:
                try:
                    bt_client_tan_gelen_mesaj = bt_baglanti_portu.recv(1024).decode("utf-8")
                    print("Leo Araç Uygulaması versiyon : ", genel.ic_version, "   Bağlanan Bluetooth Client'ından gelen bilgi :", bt_client_tan_gelen_mesaj)
                    if bt_client_tan_gelen_mesaj == "cikis basildi"  or not bt_client_tan_gelen_mesaj:
                        print("BT client'tan çıkış komutu geldi, aktif BT socket bağlantısı kapatılıyor")
                        genel.surekli_mod = "OFF"
                        genel.arac_durdu()
                        bt_baglanti_portu.close()
                        break
                    
                    elif genel.surekli_mod == "OFF" and (bt_client_tan_gelen_mesaj == "sola ileri donus birakildi" or \
                        bt_client_tan_gelen_mesaj == "ileri birakildi" or bt_client_tan_gelen_mesaj == "saga ileri donus birakildi" or \
                        bt_client_tan_gelen_mesaj == "geri sola donus birakildi" or bt_client_tan_gelen_mesaj == "geri birakildi" or \
                        bt_client_tan_gelen_mesaj == "geri saga donus birakildi" or bt_client_tan_gelen_mesaj == "sola 360 donus birakildi" or \
                        bt_client_tan_gelen_mesaj == "saga 360 donus birakildi"):
                        genel.arac_durdu()

                    elif bt_client_tan_gelen_mesaj == "sola ileri donus basildi":
                        genel.arac_ileri_sola_donuyor()

                    elif bt_client_tan_gelen_mesaj == "ileri basildi":
                        genel.arac_duz_ileri_gidiyor()

                    elif bt_client_tan_gelen_mesaj == "saga ileri donus basildi":
                        genel.arac_ileri_saga_donuyor()

                    elif bt_client_tan_gelen_mesaj == "dur basildi":
                        genel.arac_durdu()
                        genel.arka_fren_lambalarini_yak()

                    elif bt_client_tan_gelen_mesaj == "geri sola donus basildi":
                        genel.arac_geri_sola_donuyor()

                    elif bt_client_tan_gelen_mesaj == "geri basildi":
                        genel.arac_duz_geri_gidiyor()

                    elif bt_client_tan_gelen_mesaj == "geri saga donus basildi":
                        genel.arac_geri_saga_donuyor()                    

                    elif bt_client_tan_gelen_mesaj == "sola 360 donus basildi":
                        genel.arac_sola_360_donuyor()                    

                    elif bt_client_tan_gelen_mesaj == "saga 360 donus basildi":
                        genel.arac_saga_360_donuyor()                    

                    elif bt_client_tan_gelen_mesaj == "tum farlari yak basildi":
                        genel.tum_farlari_yak()

                    elif bt_client_tan_gelen_mesaj == "selektor yap basildi":
                        genel.selektor_yap()

                    elif bt_client_tan_gelen_mesaj == "tum farlari sondur basildi":
                        genel.tum_farlari_sondur()

                    elif bt_client_tan_gelen_mesaj == "SM ON":
                        genel.surekli_mod = "ONN"

                    elif bt_client_tan_gelen_mesaj == "SM OFF":
                        genel.surekli_mod = "OFF"
                        genel.arac_durdu()

                except Exception as e:
                    print("Bluetooth bağlantısında hata :", str(e))
                    bt_baglanti_portu.close()
                    break
            bt_baglanti_portu.close()
    else:
        print("Bluetooth Socket'i hazır değil, Bluetooth bağlantısı sağlanamayacak!")