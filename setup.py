import os
import re
import subprocess
import logging

# Konfigurasi logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def print_log(message, level="info"):
    """Mencetak pesan ke terminal dan mencatat log."""
    if level == "info":
        print(f"✅ {message}")
        logging.info(message)
    elif level == "warning":
        print(f"⚠️ {message}")
        logging.warning(message)
    elif level == "error":
        print(f"❌ {message}")
        logging.error(message)

def run_command(command):
    """Menjalankan perintah shell dengan subprocess dan menangani error."""
    try:
        subprocess.run(command, check=True, shell=True)
        print_log(f"Berhasil menjalankan: {command}")
    except subprocess.CalledProcessError as e:
        print_log(f"Gagal menjalankan: {command}\nError: {e}", "error")

def install_dependencies():
    """Menginstal semua dependensi yang dibutuhkan."""
    print_log("📦 Menginstal dependensi...")
    dependencies = [
        "sudo apt update && sudo apt upgrade -y",
        "sudo apt install python3-pip -y",
        "sudo pip3 install flask requests --break-system-packages",
        "sudo pip3 install psutil flask_cors --break-system-packages",
        "sudo apt install -y ufw",
        "sudo systemctl start pigpiod",
        "sudo systemctl enable pigpiod",
        "sudo apt-get install -y pptp-linux"
    ]
    for dep in dependencies:
        run_command(dep)
    print_log("✅ Semua dependensi telah terinstal.")

def replace_line_in_file(filename, pattern, replacement):
    """Mengganti baris dalam file berdasarkan pola tertentu."""
    try:
        with open(filename, "r") as file:
            lines = file.readlines()
        
        with open(filename, "w") as file:
            for line in lines:
                if re.search(pattern, line):
                    file.write(replacement + "\n")
                else:
                    file.write(line)
        print_log(f"✅ Berhasil mengedit file: {filename}")
    except FileNotFoundError:
        print_log(f"❌ File tidak ditemukan: {filename}", "error")

def configure_files(python_path, log_dir, flask_port, vpn_gateway, vpn_user, vpn_pass):
    """Mengedit file konfigurasi dengan parameter yang diberikan."""
    print_log("🛠️ Mengonfigurasi file...")

    replace_line_in_file("billacceptor.py", r'LOG_DIR = .*', f'LOG_DIR = "{log_dir}"')
    replace_line_in_file("billacceptor.py", r'app.run\(host="0.0.0.0", port=.*', f'app.run(host="0.0.0.0", port={flask_port}, debug=True)')
    replace_line_in_file("billacceptor.service", r'ExecStart=.*', f'ExecStart=/usr/bin/python3 {python_path}/billacceptor.py')
    replace_line_in_file("vpn", r'pty "pptp .*', f'pty "pptp {vpn_gateway} --nolaunchpppd --debug"')
    replace_line_in_file("vpn", r'name .*', f'name {vpn_user}')
    replace_line_in_file("vpn", r'password .*', f'password {vpn_pass}')

def move_files(python_path, rollback_path):
    """Memindahkan file ke lokasi yang sesuai."""
    print_log("📂 Memindahkan file konfigurasi...")
    run_command("sudo mv billacceptor.service /etc/systemd/system/")
    run_command("sudo mv vpn /etc/ppp/peers/")
    run_command("sudo chmod 777 /etc/ppp/peers")
    run_command(f"sudo mv billacceptor.py {python_path}")
    run_command(f"sudo mv rollback.py {rollback_path}")

def configure_ufw(flask_port):
    """Mengonfigurasi firewall UFW."""
    print_log("🔐 Mengonfigurasi UFW...")
    run_command(f"sudo ufw allow {flask_port}")
    run_command("sudo ufw enable")

def enable_service():
    """Mengaktifkan service billacceptor."""
    print_log("🚀 Mengaktifkan service Bill Acceptor...")
    run_command("sudo systemctl enable billacceptor.service")
    run_command("sudo systemctl start billacceptor.service")

def configure_vpn(log_path):
    """Mengonfigurasi VPN agar otomatis terhubung saat boot dengan membersihkan rc.local dan menambahkan crontab."""
    print_log("🔧 Mengonfigurasi VPN agar otomatis terhubung saat boot...")

    rc_local_path = "/etc/rc.local"

    # Hapus isi bawaan dan buat ulang rc.local
    print_log("📝 Menghapus isi rc.local dan menambahkan konfigurasi baru...")
    with open(rc_local_path, "w") as rc_local:
        rc_local.write("#!/bin/bash\n")
        rc_local.write('vpn="0"\n')
        rc_local.write("exit 0\n")

    run_command(f"sudo chmod +x {rc_local_path}")

    # Konfigurasi crontab
    print_log("🕒 Menambahkan konfigurasi crontab untuk VPN...")
    cron_command = f'@reboot sudo pon vpn updetach >> {log_path} 2>&1'

    # Tambahkan crontab tanpa membuka editor
    run_command(f'(crontab -l 2>/dev/null; echo "{cron_command}") | crontab -')

    print_log("✅ Konfigurasi VPN berhasil diperbarui.")

if __name__ == "__main__":
    print("\n🔧 **Setup Bill Acceptor**\n")

    # **Input dari pengguna**
    python_path = input("Masukkan path penyimpanan billacceptor.py: ")  
    log_dir = input("Masukkan path LOG_DIR: ")  
    flask_port = input("Masukkan port Flask: ")  
    vpn_gateway = input("Masukkan IP Gateway VPN: ")  
    vpn_user = input("Masukkan Username VPN: ")  
    vpn_pass = input("Masukkan Password VPN: ")  
    log_path = input("Masukkan path untuk log VPN: ")
    rollback_path = input("Masukkan path penyimpanan rollback.py: ")

    # **Jalankan semua fungsi**
    install_dependencies()
    configure_files(python_path, log_dir, flask_port, vpn_gateway, vpn_user, vpn_pass)
    move_files(python_path, rollback_path)
    configure_ufw(flask_port)
    enable_service()
    configure_vpn(log_path)

    print("\n🎉 **Setup selesai! Bill Acceptor sudah terinstal dan berjalan.** 🎉")
    print_log("🎉 Setup selesai! Bill Acceptor sudah terinstal dan berjalan.")
