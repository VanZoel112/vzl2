#!/usr/bin/env python3
"""
VzoelFox Userbot 24/7 Daemon Runner
Founder Userbot: Vzoel Fox's Lutpan
Version: 1.0.0 - Production Grade 24/7 Runner
"""

import asyncio
import sys
import os
import signal
import logging
import traceback
from datetime import datetime
from pathlib import Path
import json
import time
import subprocess
import psutil

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'vzoel_daemon.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('VzoelFox-Daemon')

# Runtime stats
STATS_FILE = Path("daemon_stats.json")
runtime_stats = {
    "daemon_start_time": None,
    "restart_count": 0,
    "total_uptime": 0,
    "last_restart": None,
    "crashes": 0,
    "process_restarts": 0,
    "memory_usage": 0,
    "cpu_usage": 0
}

# Global process handle
main_process = None
shutdown_requested = False

def load_stats():
    """Load daemon runtime statistics"""
    global runtime_stats
    try:
        if STATS_FILE.exists():
            with open(STATS_FILE, 'r') as f:
                loaded_stats = json.load(f)
                runtime_stats.update(loaded_stats)
    except Exception as e:
        logger.warning(f"Failed to load daemon stats: {e}")

def save_stats():
    """Save daemon runtime statistics"""
    try:
        # Update current resource usage
        process = psutil.Process()
        runtime_stats["memory_usage"] = process.memory_info().rss / 1024 / 1024  # MB
        runtime_stats["cpu_usage"] = process.cpu_percent()
        
        with open(STATS_FILE, 'w') as f:
            json.dump(runtime_stats, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save daemon stats: {e}")

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global shutdown_requested, main_process
    
    logger.info(f"🛑 Received signal {signum}, shutting down daemon gracefully...")
    shutdown_requested = True
    
    # Stop main process if running
    if main_process and main_process.poll() is None:
        logger.info("🔌 Stopping main process...")
        main_process.terminate()
        try:
            main_process.wait(timeout=10)  # Wait up to 10 seconds
        except subprocess.TimeoutExpired:
            logger.warning("⚠️ Main process didn't stop gracefully, force killing...")
            main_process.kill()
    
    # Update stats
    if runtime_stats["daemon_start_time"]:
        uptime = time.time() - runtime_stats["daemon_start_time"]
        runtime_stats["total_uptime"] += uptime
    
    save_stats()
    logger.info("🦊 VzoelFox Daemon shutdown complete")
    sys.exit(0)

def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown"""
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Termination signal
    if hasattr(signal, 'SIGHUP'):
        signal.signal(signal.SIGHUP, signal_handler)   # Hangup signal

def check_dependencies():
    """Check if all required dependencies are available"""
    required_files = [
        "main.py",
        "client.py", 
        "config.py",
        "emoji_handler.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        logger.error(f"❌ Missing required files: {missing_files}")
        return False
    
    logger.info("✅ All dependencies found")
    return True

def get_system_info():
    """Get system resource information"""
    try:
        memory = psutil.virtual_memory()
        cpu_count = psutil.cpu_count()
        disk = psutil.disk_usage('/')
        
        return {
            "memory_total": round(memory.total / 1024 / 1024 / 1024, 2),  # GB
            "memory_available": round(memory.available / 1024 / 1024 / 1024, 2),  # GB
            "memory_percent": memory.percent,
            "cpu_count": cpu_count,
            "cpu_percent": psutil.cpu_percent(interval=1),
            "disk_total": round(disk.total / 1024 / 1024 / 1024, 2),  # GB
            "disk_free": round(disk.free / 1024 / 1024 / 1024, 2),  # GB
        }
    except Exception as e:
        logger.error(f"Failed to get system info: {e}")
        return {}

async def monitor_process():
    """Monitor the main process and system resources"""
    global main_process
    
    while not shutdown_requested:
        try:
            await asyncio.sleep(30)  # Monitor every 30 seconds
            
            if main_process and main_process.poll() is None:
                # Process is running, get resource usage
                try:
                    proc = psutil.Process(main_process.pid)
                    memory_mb = proc.memory_info().rss / 1024 / 1024
                    cpu_percent = proc.cpu_percent()
                    
                    # Log resource usage every 5 minutes
                    if time.time() % 300 < 30:  # Approximately every 5 minutes
                        logger.info(f"📊 Process stats: Memory: {memory_mb:.1f}MB, CPU: {cpu_percent:.1f}%")
                    
                    # Check for memory leaks (restart if using too much memory)
                    if memory_mb > 1024:  # More than 1GB
                        logger.warning(f"⚠️ High memory usage detected: {memory_mb:.1f}MB")
                        
                except psutil.NoSuchProcess:
                    logger.warning("⚠️ Main process not found in system")
            
        except Exception as e:
            logger.error(f"Monitor error: {e}")

def start_main_process():
    """Start the main VzoelFox process"""
    global main_process
    
    try:
        logger.info("🚀 Starting main VzoelFox process...")
        
        # Start main.py as subprocess
        main_process = subprocess.Popen([
            sys.executable, "main.py"
        ], 
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
        )
        
        runtime_stats["process_restarts"] += 1
        logger.info(f"✅ Main process started with PID: {main_process.pid}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to start main process: {e}")
        return False

def wait_for_process():
    """Wait for main process to finish and handle output"""
    global main_process
    
    try:
        # Read output in real-time
        for line in iter(main_process.stdout.readline, ''):
            if line:
                # Forward main process output to daemon log
                logger.info(f"[MAIN] {line.strip()}")
            if shutdown_requested:
                break
        
        # Wait for process to finish
        return_code = main_process.wait()
        logger.info(f"🔄 Main process exited with code: {return_code}")
        
        return return_code
        
    except Exception as e:
        logger.error(f"Error waiting for process: {e}")
        return -1

async def run_daemon():
    """Main daemon loop with auto-restart functionality"""
    global main_process, shutdown_requested
    
    max_restarts = 100  # Maximum restart attempts
    restart_delay = 10  # Base delay between restarts
    consecutive_failures = 0
    
    # Start monitoring task
    monitor_task = asyncio.create_task(monitor_process())
    
    while runtime_stats["restart_count"] < max_restarts and not shutdown_requested:
        try:
            # Start main process
            if start_main_process():
                consecutive_failures = 0  # Reset failure counter
                
                # Wait for process in a separate thread to avoid blocking
                loop = asyncio.get_event_loop()
                return_code = await loop.run_in_executor(None, wait_for_process)
                
                if shutdown_requested:
                    break
                
                # Check return code
                if return_code == 0:
                    logger.info("✅ Main process stopped gracefully")
                    break
                else:
                    logger.warning(f"⚠️ Main process crashed with code: {return_code}")
                    runtime_stats["crashes"] += 1
                    consecutive_failures += 1
            else:
                consecutive_failures += 1
            
            # Don't restart if shutdown was requested
            if shutdown_requested:
                break
            
            runtime_stats["restart_count"] += 1
            runtime_stats["last_restart"] = datetime.now().isoformat()
            
            if runtime_stats["restart_count"] >= max_restarts:
                logger.error(f"❌ Maximum restart attempts ({max_restarts}) reached")
                break
            
            # Calculate delay with exponential backoff for consecutive failures
            if consecutive_failures > 3:
                delay = min(restart_delay * (consecutive_failures ** 0.5), 300)  # Max 5 minutes
            else:
                delay = restart_delay
            
            logger.info(f"⏳ Restarting in {delay:.1f} seconds... (Attempt {runtime_stats['restart_count']}/{max_restarts})")
            
            # Wait with periodic status updates
            for i in range(int(delay)):
                if shutdown_requested:
                    break
                await asyncio.sleep(1)
                if i % 30 == 29:  # Every 30 seconds
                    remaining = delay - i - 1
                    logger.info(f"⏳ Restart in {remaining:.0f} seconds...")
            
        except Exception as e:
            logger.error(f"💥 Critical error in daemon loop: {e}")
            logger.error(f"📋 Traceback:\n{traceback.format_exc()}")
            runtime_stats["crashes"] += 1
            await asyncio.sleep(restart_delay)
    
    # Cancel monitoring task
    monitor_task.cancel()

def print_banner():
    """Print VzoelFox daemon banner"""
    banner = """
╔══════════════════════════════════════════════════════╗
║             🦊 VzoelFox 24/7 Daemon                 ║
║           Production Grade Process Manager           ║
║                                                      ║
║     Founder: Vzoel Fox's Lutpan                      ║
║     Version: 1.0.0 - Daemon Edition                 ║
║     Features: Auto-restart, Monitoring, Logging     ║
╚══════════════════════════════════════════════════════╝
"""
    print(banner)

def print_system_info():
    """Print system information"""
    sys_info = get_system_info()
    if sys_info:
        print(f"""
🖥️  System Information:
├── Memory: {sys_info.get('memory_available', 0):.1f}GB free / {sys_info.get('memory_total', 0):.1f}GB total ({sys_info.get('memory_percent', 0):.1f}% used)
├── CPU: {sys_info.get('cpu_count', 0)} cores, {sys_info.get('cpu_percent', 0):.1f}% usage
├── Disk: {sys_info.get('disk_free', 0):.1f}GB free / {sys_info.get('disk_total', 0):.1f}GB total
└── Platform: {sys.platform}
""")

def print_daemon_stats():
    """Print daemon runtime statistics"""
    print(f"""
📊 Daemon Statistics:
├── Total Restarts: {runtime_stats['restart_count']}
├── Process Restarts: {runtime_stats['process_restarts']}
├── Crashes: {runtime_stats['crashes']}
├── Last Restart: {runtime_stats['last_restart'] or 'Never'}
├── Memory Usage: {runtime_stats['memory_usage']:.1f}MB
├── CPU Usage: {runtime_stats['cpu_usage']:.1f}%
└── Log Directory: {LOG_DIR.absolute()}
""")

async def main():
    """Main daemon entry point"""
    load_stats()
    setup_signal_handlers()
    print_banner()
    print_system_info()
    print_daemon_stats()
    
    # Check dependencies
    if not check_dependencies():
        logger.error("❌ Dependency check failed, exiting...")
        sys.exit(1)
    
    # Update daemon start time
    runtime_stats["daemon_start_time"] = time.time()
    save_stats()
    
    logger.info("🦊 VzoelFox 24/7 Daemon starting...")
    logger.info("🔍 Monitoring: System resources every 30 seconds")
    logger.info("📊 Stats: Auto-saved continuously")
    logger.info("🛑 Shutdown: Use Ctrl+C for graceful stop")
    
    try:
        await run_daemon()
    except KeyboardInterrupt:
        logger.info("🛑 Received keyboard interrupt")
    except Exception as e:
        logger.error(f"💥 Fatal daemon error: {e}")
        logger.error(f"📋 Traceback:\n{traceback.format_exc()}")
    
    # Final stats update
    if runtime_stats["daemon_start_time"]:
        uptime = time.time() - runtime_stats["daemon_start_time"]
        runtime_stats["total_uptime"] += uptime
    
    save_stats()
    logger.info("🦊 VzoelFox Daemon has stopped")

if __name__ == "__main__":
    try:
        # Check Python version
        if sys.version_info < (3, 8):
            print("❌ Python 3.8 or higher is required")
            sys.exit(1)
        
        # Check for help argument
        if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h", "help"]:
            print("""
🦊 VzoelFox 24/7 Daemon Usage:

Commands:
  python daemon.py           - Start 24/7 daemon
  python daemon.py --help    - Show this help

Features:
  • Auto-restart on crashes
  • Resource monitoring
  • Process management
  • Graceful shutdown handling
  • Comprehensive logging
  • Statistics tracking

The daemon will automatically manage the main.py process and 
restart it if it crashes or stops unexpectedly.

Founder: Vzoel Fox's Lutpan
            """)
            sys.exit(0)
        
        # Install signal handlers early
        setup_signal_handlers()
        
        # Run the daemon
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("\n🛑 Daemon interrupted by user")
    except Exception as e:
        print(f"💥 Fatal daemon error: {e}")
        sys.exit(1)