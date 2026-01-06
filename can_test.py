import time
import can
from functions import initialize_canbus_connection


def test_can_connection():
    """CAN 버스 연결 및 패킷 수신 테스트"""

    print("="*50)
    print("CAN Bus Connection Test")
    print("="*50)

    # CAN 버스 초기화
    print("\n[1] Initializing CAN bus connection...")
    try:
        initialize_canbus_connection()
        print("    ✓ CAN bus initialization completed")
    except Exception as e:
        print(f"    ✗ Initialization failed: {e}")
        return

    # CAN 버스 연결
    print("\n[2] Connecting to CAN bus (can0)...")
    try:
        can_bus = can.interface.Bus(channel='can0', interface='socketcan')
        print("    ✓ Successfully connected to can0")
    except Exception as e:
        print(f"    ✗ Connection failed: {e}")
        return

    # 패킷 수신 테스트
    print("\n[3] Starting packet reception test...")
    print("    (Listening for CAN messages... Press Ctrl+C to stop)\n")

    packet_count = 0
    last_recv_time = time.time()
    received_addresses = set()

    try:
        while True:
            current_time = time.time()

            # 타임아웃 체크 (10초 동안 메시지가 없으면 경고)
            if current_time - last_recv_time >= 10:
                print(f"\n⚠ Warning: No messages received for 10 seconds")
                last_recv_time = current_time

            # 메시지 수신 (1초 타임아웃)
            try:
                recv_message = can_bus.recv(1)
            except Exception as e:
                print(f"\n✗ Message reception error: {e}")
                continue

            # 수신된 메시지 처리
            if recv_message is not None:
                last_recv_time = current_time
                packet_count += 1
                address = recv_message.arbitration_id
                signal = recv_message.data

                # 새로운 주소 발견 시 출력
                if address not in received_addresses:
                    received_addresses.add(address)
                    print(f"\n[New Address] 0x{address:03x}")

                # 패킷 정보 출력
                data_hex = ' '.join([f'{b:02x}' for b in signal])
                timestamp = time.strftime('%H:%M:%S', time.localtime(current_time))

                print(f"[{timestamp}] ID: 0x{address:03x} | Data: [{data_hex}] | DLC: {len(signal)}")

                # 주요 주소 체크 (jupiter.py에서 사용하는 중요 주소들)
                if address == 0x528:
                    print("    → UnixTime packet detected")
                elif address == 0x118:
                    print("    → DriveSystemStatus packet detected")
                elif address == 0x273:
                    print("    → Wiper status packet detected")
                elif address == 0x3c2:
                    print("    → Seatbelt/Autopilot packet detected")

                # 100개마다 통계 출력
                if packet_count % 100 == 0:
                    print(f"\n--- Statistics: {packet_count} packets received, {len(received_addresses)} unique addresses ---\n")

    except KeyboardInterrupt:
        print("\n\n[4] Test stopped by user")
        print(f"\n{'='*50}")
        print("Test Summary")
        print(f"{'='*50}")
        print(f"Total packets received: {packet_count}")
        print(f"Unique addresses: {len(received_addresses)}")
        print(f"Addresses found: {sorted([f'0x{addr:03x}' for addr in received_addresses])}")
        print(f"{'='*50}\n")

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")

    finally:
        # CAN 버스 종료
        try:
            can_bus.shutdown()
            print("CAN bus connection closed")
        except:
            pass


def simple_monitor():
    """간단한 CAN 모니터 - 특정 주소만 출력"""

    # 모니터링할 주소 정의 (jupiter.py에서 중요한 주소들)
    monitor_addresses = {
        0x118: 'DriveSystemStatus',
        0x528: 'UnixTime',
        0x273: 'WiperStatus',
        0x3c2: 'Seatbelt/AP',
        0x334: 'Accelerator',
        0x39d: 'Brake',
        0x1f9: 'ParkingButton',
        0x3e2: 'MapLamp',
        0x229: 'GearStalk',
        0x2f3: 'HVAC',
        0x249: 'TurnSignal'
    }

    print("="*60)
    print("Simple CAN Monitor - Filtered View")
    print("="*60)
    print(f"Monitoring addresses: {list(monitor_addresses.keys())}")
    print("Press Ctrl+C to stop\n")

    initialize_canbus_connection()
    can_bus = can.interface.Bus(channel='can0', interface='socketcan')

    try:
        while True:
            recv_message = can_bus.recv(1)

            if recv_message is not None:
                address = recv_message.arbitration_id

                # 모니터링 대상 주소만 출력
                if address in monitor_addresses:
                    signal = recv_message.data
                    data_hex = ' '.join([f'{b:02x}' for b in signal])
                    timestamp = time.strftime('%H:%M:%S', time.localtime())
                    name = monitor_addresses[address]

                    print(f"[{timestamp}] {name:20s} (0x{address:03x}): [{data_hex}]")

    except KeyboardInterrupt:
        print("\n\nMonitoring stopped")
    finally:
        can_bus.shutdown()


if __name__ == '__main__':
    import sys

    print("\nCAN Bus Test Tool")
    print("-" * 50)
    print("1. Full test (all packets)")
    print("2. Simple monitor (filtered view)")
    print("-" * 50)

    if len(sys.argv) > 1 and sys.argv[1] == '2':
        simple_monitor()
    else:
        choice = input("Select mode (1 or 2, default=1): ").strip()

        if choice == '2':
            simple_monitor()
        else:
            test_can_connection()
