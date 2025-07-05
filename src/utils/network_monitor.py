import psutil
import time
import platform
import subprocess
import re
from typing import Dict, Any, Optional

def get_network_usage() -> Dict[str, Any]:
    """
    Returns current network usage statistics.
    """
    net_io = psutil.net_io_counters()
    return {
        "bytes_sent": net_io.bytes_sent,
        "bytes_recv": net_io.bytes_recv,
        "packets_sent": net_io.packets_sent,
        "packets_recv": net_io.packets_recv,
    }

def ping_host(host: str, count: int = 1) -> Optional[float]:
    """
    Pings a host and returns the average latency in milliseconds.
    Returns None if the host is unreachable or ping fails.
    """
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, str(count), host]
    try:
        output = subprocess.check_output(command, timeout=5).decode()
        # Extract average time from ping output
        if platform.system().lower() == 'windows':
            # Example: Minimum = 1ms, Maximum = 1ms, Average = 1ms
            match = re.search(r'Average = (\d+)ms', output)
        else:
            # Example: round-trip min/avg/max/stddev = 0.040/0.040/0.040/0.000 ms
            match = re.search(r'min/avg/max/stddev = [^/]+/(\d+\.\d+)/', output)
        
        if match:
            return float(match.group(1))
        return None
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return None
    except Exception as e:
        print(f"Error pinging host {host}: {e}")
        return None

# Example Usage
if __name__ == "__main__":
    print("--- Network Usage ---")
    usage = get_network_usage()
    print(f"Bytes Sent: {usage['bytes_sent']}")
    print(f"Bytes Received: {usage['bytes_recv']}")

    print("\n--- Ping Test ---")
    host_to_ping = "google.com"
    latency = ping_host(host_to_ping)
    if latency is not None:
        print(f"Average latency to {host_to_ping}: {latency} ms")
    else:
        print(f"Could not ping {host_to_ping}")

    host_to_ping_local = "localhost"
    latency_local = ping_host(host_to_ping_local)
    if latency_local is not None:
        print(f"Average latency to {host_to_ping_local}: {latency_local} ms")
    else:
        print(f"Could not ping {host_to_ping_local}")