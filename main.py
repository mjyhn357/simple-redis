import sys
import subprocess


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python main.py server    # 启动Redis服务器")
        print("  python main.py client    # 启动Redis客户端")
        return

    mode = sys.argv[1].lower()

    if mode == "server":
        print("Starting Redis Server...")
        subprocess.run([sys.executable, "redis-server.py"])
    elif mode == "client":
        print("Starting Redis Client...")
        subprocess.run([sys.executable, "redis-cli.py"])
    else:
        print("Unknown mode. Use 'server' or 'client'")


if __name__ == "__main__":
    main()