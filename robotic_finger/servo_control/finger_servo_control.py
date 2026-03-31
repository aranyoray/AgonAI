"""
Robotic Finger Servo Control - Python (Raspberry Pi / Serial)
==============================================================
Control the robotic finger via:
  1. Direct GPIO servo control (Raspberry Pi)
  2. Serial communication to Arduino

Usage:
  python finger_servo_control.py --mode gpio     # Direct Raspberry Pi GPIO
  python finger_servo_control.py --mode serial   # Arduino via USB serial
  python finger_servo_control.py --mode serial --port /dev/ttyUSB0
"""

import argparse
import time
import sys
import math

# --- Configuration ---
SERVO_PIN = 18           # GPIO pin for Raspberry Pi PWM
FINGER_OPEN = 10         # Open angle (degrees)
FINGER_CLOSED = 160      # Closed/grip angle (degrees)
THREAD_HOLD = 120        # Thread holding angle (degrees)
FINGER_REST = 45         # Rest position (degrees)
SWEEP_DELAY = 0.015      # Delay between angle steps (seconds)
SERIAL_BAUD = 9600


class ServoController:
    """Base class for servo control."""

    def __init__(self):
        self.current_angle = FINGER_REST
        self.is_gripping = False

    def set_angle(self, angle):
        """Set servo to exact angle."""
        raise NotImplementedError

    def smooth_move(self, target_angle):
        """Smoothly move servo to target angle."""
        target_angle = max(0, min(180, target_angle))
        step = 1 if target_angle > self.current_angle else -1

        while self.current_angle != target_angle:
            self.current_angle += step
            self.set_angle(self.current_angle)
            time.sleep(SWEEP_DELAY)

        print(f"  Moved to {self.current_angle}°")

    def open_finger(self):
        """Fully open the finger."""
        print("Opening finger...")
        self.smooth_move(FINGER_OPEN)
        self.is_gripping = False

    def close_finger(self):
        """Fully close/grip the finger."""
        print("Closing finger...")
        self.smooth_move(FINGER_CLOSED)
        self.is_gripping = True

    def thread_hold(self):
        """Move to thread holding position."""
        print("Thread hold position...")
        self.smooth_move(THREAD_HOLD)
        self.is_gripping = True

    def rest_position(self):
        """Move to rest position."""
        print("Rest position...")
        self.smooth_move(FINGER_REST)
        self.is_gripping = False

    def thread_keep_sequence(self):
        """
        Automated thread keeping sequence:
        1. Open finger wide
        2. Position for thread catch
        3. Close slowly to grip
        4. Hold with gentle oscillation
        """
        print("Starting thread keep sequence...")

        # Step 1: Open
        print("  [1/4] Opening...")
        self.smooth_move(FINGER_OPEN)
        time.sleep(1.0)

        # Step 2: Position
        print("  [2/4] Positioning for thread...")
        self.smooth_move(FINGER_REST)
        time.sleep(0.8)

        # Step 3: Grip
        print("  [3/4] Gripping thread...")
        self.smooth_move(THREAD_HOLD)
        time.sleep(0.5)

        # Step 4: Hold with micro-oscillation
        print("  [4/4] Securing thread (oscillating)...")
        start = time.time()
        while time.time() - start < 3.0:
            oscillation = int(3 * math.sin(time.time() * 2))
            self.set_angle(THREAD_HOLD + oscillation)
            time.sleep(0.05)

        # Settle
        self.set_angle(THREAD_HOLD)
        self.is_gripping = True
        print("  Thread secured and held.")

    def cleanup(self):
        """Release resources."""
        pass


class GPIOServoController(ServoController):
    """Direct Raspberry Pi GPIO servo control using hardware PWM."""

    def __init__(self):
        super().__init__()
        try:
            import RPi.GPIO as GPIO
            self.GPIO = GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(SERVO_PIN, GPIO.OUT)
            self.pwm = GPIO.PWM(SERVO_PIN, 50)  # 50Hz for servo
            self.pwm.start(self._angle_to_duty(FINGER_REST))
            print(f"GPIO servo initialized on pin {SERVO_PIN}")
        except ImportError:
            print("ERROR: RPi.GPIO not available. Use --mode serial instead.")
            sys.exit(1)

    @staticmethod
    def _angle_to_duty(angle):
        """Convert angle (0-180) to duty cycle (2.5-12.5%)."""
        return 2.5 + (angle / 180.0) * 10.0

    def set_angle(self, angle):
        angle = max(0, min(180, angle))
        self.current_angle = angle
        self.pwm.ChangeDutyCycle(self._angle_to_duty(angle))

    def cleanup(self):
        self.pwm.stop()
        self.GPIO.cleanup()
        print("GPIO cleaned up.")


class SerialServoController(ServoController):
    """Control servo via Arduino over serial."""

    def __init__(self, port="/dev/ttyUSB0", baud=SERIAL_BAUD):
        super().__init__()
        try:
            import serial
            self.ser = serial.Serial(port, baud, timeout=2)
            time.sleep(2)  # Wait for Arduino reset
            # Read startup message
            while self.ser.in_waiting:
                print(f"  Arduino: {self.ser.readline().decode().strip()}")
            print(f"Serial connected on {port} @ {baud}")
        except ImportError:
            print("ERROR: pyserial not installed. Run: pip install pyserial")
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: Could not open serial port {port}: {e}")
            sys.exit(1)

    def _send_command(self, cmd):
        """Send command to Arduino and read response."""
        self.ser.write(f"{cmd}\n".encode())
        time.sleep(0.1)
        while self.ser.in_waiting:
            line = self.ser.readline().decode().strip()
            if line:
                print(f"  Arduino: {line}")

    def set_angle(self, angle):
        angle = max(0, min(180, angle))
        self.current_angle = angle
        self._send_command(str(angle))

    def smooth_move(self, target_angle):
        """For serial mode, let Arduino handle smooth movement."""
        self._send_command(str(target_angle))
        self.current_angle = target_angle

    def open_finger(self):
        print("Opening finger...")
        self._send_command("o")
        self.is_gripping = False

    def close_finger(self):
        print("Closing finger...")
        self._send_command("c")
        self.is_gripping = True

    def thread_hold(self):
        print("Thread hold position...")
        self._send_command("t")
        self.is_gripping = True

    def rest_position(self):
        print("Rest position...")
        self._send_command("r")
        self.is_gripping = False

    def thread_keep_sequence(self):
        print("Starting thread keep sequence...")
        self._send_command("k")
        # Wait for sequence to complete
        time.sleep(8)
        while self.ser.in_waiting:
            line = self.ser.readline().decode().strip()
            if line:
                print(f"  Arduino: {line}")
        self.is_gripping = True

    def cleanup(self):
        if hasattr(self, 'ser') and self.ser.is_open:
            self.ser.close()
            print("Serial connection closed.")


def interactive_control(controller):
    """Interactive command loop."""
    print("\n=== Robotic Finger Control ===")
    print("Commands:")
    print("  o       - Open finger")
    print("  c       - Close/grip")
    print("  t       - Thread hold position")
    print("  r       - Rest position")
    print("  k       - Thread keeping sequence")
    print("  0-180   - Set exact angle")
    print("  q       - Quit")
    print("==============================\n")

    while True:
        try:
            cmd = input("finger> ").strip().lower()

            if not cmd:
                continue
            elif cmd == 'q':
                print("Returning to rest position...")
                controller.rest_position()
                break
            elif cmd == 'o':
                controller.open_finger()
            elif cmd == 'c':
                controller.close_finger()
            elif cmd == 't':
                controller.thread_hold()
            elif cmd == 'r':
                controller.rest_position()
            elif cmd == 'k':
                controller.thread_keep_sequence()
            else:
                try:
                    angle = int(cmd)
                    if 0 <= angle <= 180:
                        controller.smooth_move(angle)
                    else:
                        print("Angle must be 0-180")
                except ValueError:
                    print(f"Unknown command: {cmd}")

        except KeyboardInterrupt:
            print("\nInterrupted. Returning to rest...")
            controller.rest_position()
            break
        except EOFError:
            break

    controller.cleanup()


def main():
    parser = argparse.ArgumentParser(
        description="Robotic Finger Servo Controller"
    )
    parser.add_argument(
        "--mode", choices=["gpio", "serial"], default="serial",
        help="Control mode: gpio (Raspberry Pi) or serial (Arduino)"
    )
    parser.add_argument(
        "--port", default="/dev/ttyUSB0",
        help="Serial port for Arduino (default: /dev/ttyUSB0)"
    )
    parser.add_argument(
        "--baud", type=int, default=SERIAL_BAUD,
        help=f"Serial baud rate (default: {SERIAL_BAUD})"
    )

    args = parser.parse_args()

    if args.mode == "gpio":
        controller = GPIOServoController()
    else:
        controller = SerialServoController(port=args.port, baud=args.baud)

    interactive_control(controller)


if __name__ == "__main__":
    main()
