import time
import random
import paho.mqtt.client as mqtt

# ==========================================
# KONFIGURASI MQTT
# ==========================================

BROKER = "localhost"
PORT = 1883

TOPIC_SUHU = "iot/2510020148/sensor/suhu"
TOPIC_RELAY = "iot/2510020148/aktuator/relay"
TOPIC_PWM = "iot/2510020148/aktuator/pwm"

# ==========================================
# KONDISI SIMULASI PERANGKAT
# ==========================================

relay_status = "OFF"
pwm_value = 0
temperature = 28.0


# ==========================================
# KETIKA TERHUBUNG KE MQTT
# ==========================================

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Berhasil terhubung ke MQTT Broker!")

        client.subscribe(TOPIC_RELAY)
        client.subscribe(TOPIC_PWM)

        print("Berlangganan topic Relay dan PWM.")
    else:
        print("Koneksi MQTT gagal:", reason_code)


# ==========================================
# MENERIMA PERINTAH DARI NODE-RED
# ==========================================

def on_message(client, userdata, message):
    global relay_status, pwm_value

    payload = message.payload.decode().strip()

    # Kontrol Relay
    if message.topic == TOPIC_RELAY:
        if payload == "ON":
            relay_status = "ON"
            print("Relay: ON")

        elif payload == "OFF":
            relay_status = "OFF"
            print("Relay: OFF")

    # Kontrol PWM LED
    elif message.topic == TOPIC_PWM:
        try:
            value = int(float(payload))

            if 0 <= value <= 255:
                pwm_value = value
                brightness = (pwm_value / 255) * 100

                print(
                    f"PWM LED: {pwm_value} "
                    f"({brightness:.1f}%)"
                )
            else:
                print("Nilai PWM harus 0 sampai 255.")

        except ValueError:
            print("Perintah PWM tidak valid:", payload)


# ==========================================
# MEMBUAT MQTT CLIENT
# ==========================================

client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    client_id="Python_Simulator_2510020148"
)

client.on_connect = on_connect
client.on_message = on_message


# ==========================================
# MENJALANKAN SIMULATOR
# ==========================================

try:
    print("Menghubungkan ke MQTT Broker...")

    client.connect(BROKER, PORT, 60)
    client.loop_start()

    time.sleep(2)

    print("===================================")
    print(" SIMULATOR PERANGKAT IoT AKTIF")
    print("===================================")
    print("Monitoring suhu setiap 3 detik.")
    print("Relay dan PWM siap menerima perintah.")
    print("Tekan CTRL + C untuk menghentikan.")
    print("===================================")

    while True:
        # Simulasi pembacaan suhu DHT22
        temperature += random.uniform(-0.5, 0.5)
        temperature = max(25.0, min(35.0, temperature))

        # Mengirim suhu melalui MQTT
        result = client.publish(
            TOPIC_SUHU,
            payload=round(temperature, 2),
            qos=0
        )

        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"Suhu terkirim: {temperature:.2f} °C")
        else:
            print("Gagal mengirim data suhu.")

        time.sleep(3)

except KeyboardInterrupt:
    print("\nSimulator dihentikan.")

except Exception as error:
    print("Terjadi kesalahan:", error)

finally:
    client.loop_stop()
    client.disconnect()
    print("Koneksi MQTT ditutup.")
