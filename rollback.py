import os
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

def uninstall_dependencies():
    """Menghapus semua dependensi yang telah diinstal."""
    print_log("📦 Menghapus dependensi yang telah diinstal...")
    dependencies = [
        "sudo apt remove --purge -y python3-pip pptp-linux ufw",
        "sudo apt autoremove -y",
        "sudo pip3 uninstall -y flask requests psutil flask_cors"
    ]
    for dep in dependencies:
        run_command(dep)
    print_log("✅ Semua dependensi telah dihapus.")

def remove_files(python_path, log_dir):
    """Menghapus file konfigurasi, logs, dan service."""
    print_log("🗑️ Menghapus file konfigurasi dan logs...")

    files_to_remove = [
        f"{python_path}/billacceptor.py",
        "/etc/systemd/system/billacceptor.service",
        "/etc/ppp/peers/vpn",
    ]
    
    for file in files_to_remove:
        if os.path.exists(file):
            run_command(f"sudo rm -f {file}")
        else:
            print_log(f"File {file} tidak ditemukan, mungkin sudah dihapus.", "warning")

    # Hapus direktori log jika ada
    if os.path.exists(log_dir):
        run_command(f"sudo rm -rf {log_dir}")

def disable_service():
    """Menonaktifkan dan menghapus service billacceptor."""
    print_log("🚫 Menonaktifkan dan menghapus service Bill Acceptor...")
    run_command("sudo systemctl stop billacceptor.service")
    run_command("sudo systemctl disable billacceptor.service")
    run_command("sudo rm -f /etc/systemd/system/billacceptor.service")
    run_command("sudo systemctl daemon-reload")

def reset_firewall(flask_port):
    """Menghapus aturan firewall UFW yang telah ditambahkan."""
    print_log("🔐 Menghapus aturan firewall UFW...")
    run_command(f"sudo ufw deny {flask_port}")
    run_command("sudo ufw disable")

def clear_crontab():
    """Mengosongkan crontab pengguna."""
    print_log("🗑️ Mengosongkan crontab...")
    run_command("crontab -r")

def clear_rc_local():
    """Mengosongkan isi rc.local dan mengembalikannya ke default."""
    print_log("🗑️ Mengosongkan rc.local...")
    rc_local_path = "/etc/rc.local"

    with open(rc_local_path, "w") as rc_local:
        rc_local.write("#!/bin/bash\n")
        rc_local.write("exit 0\n")

    run_command(f"sudo chmod +x {rc_local_path}")

def clone_repository(clone_dir):
    """Meng-clone repository ke direktori yang ditentukan."""
    repo_url = "https://github.com/GTT008/billacceptor_beta"
    print_log(f"🔄 Meng-clone repository ke {clone_dir}...")

    # Buat direktori jika tidak ada
    if not os.path.exists(clone_dir):
        print_log(f"📂 Direktori {clone_dir} tidak ditemukan, membuatnya terlebih dahulu...")
        os.makedirs(clone_dir)

    run_command(f"git clone {repo_url} {clone_dir}")

if __name__ == "__main__":
    print("\n🔧 **Uninstall Bill Acceptor**\n")

    # **Konfirmasi sebelum menghapus**
    confirm = input("⚠️ Apakah Anda yakin ingin menghapus Bill Acceptor dan semua konfigurasinya? (y/n): ").strip().lower()
    if confirm != "y":
        print("🚫 Uninstall dibatalkan.")
        exit()

    # **Input lokasi dari file konfigurasi**
    python_path = input("Masukkan path penyimpanan billacceptor.py: ")  
    log_dir = input("Masukkan path LOG_DIR: ")  
    flask_port = input("Masukkan port Flask yang digunakan: ")  

    # **Jalankan semua fungsi uninstall**
    uninstall_dependencies()
    remove_files(python_path, log_dir)
    disable_service()
    reset_firewall(flask_port)
    clear_crontab()
    clear_rc_local()

    # **Konfirmasi untuk clone ulang repository**
    clone_choice = input("🔄 Apakah Anda ingin meng-clone ulang repository Bill Acceptor? (y/n): ").strip().lower()
    if clone_choice == "y":
        clone_dir = input("""Masukkan direktori tujuan untuk clone repository 
                          dan nama foldernya (ex : /home/yusuf/namafolder): """).strip()
        clone_repository(clone_dir)

    print("\n🎉 **Uninstall selesai! Semua konfigurasi telah dihapus.** 🎉")
    if clone_choice == "y":
        print_log(f"✅ Repository telah di-clone ke {clone_dir}.")
    else:
        print_log("✅ Uninstall selesai tanpa cloning repository.")
