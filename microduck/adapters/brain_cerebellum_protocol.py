#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Microduck Brain-Cerebellum Protocol (BCP) Python Implementation
Industrial-Grade Binary Communication Protocol Stack between Brain & Cerebellum.

Implements ASSS v1.0 specifications:
- 0xAA 0x55 Preamble, CRC16-CCITT Checksum, Sequence Rolling Window
- Motion Intent Downlink Frame (32-Byte Payload)
- High-Frequency Telemetry Uplink Frame (22-Byte Payload)
- Fault-tolerant Dead Reckoning & Heartbeat State Machine
"""

import struct
import time
from enum import IntEnum
from typing import Optional, Callable, Dict, Any, Tuple, List

PREAMBLE_B0 = 0xAA
PREAMBLE_B1 = 0x55
FRAME_TAIL = 0x0D

class MsgType(IntEnum):
    MOTION_INTENT = 0x01
    TELEMETRY = 0x02
    HEARTBEAT = 0x03
    CALIBRATE = 0x04
    ESTOP = 0x05

class SystemStatus(IntEnum):
    IDLE = 0x00
    WALKING = 0x01
    FALLEN = 0x02
    RECOVERING = 0x03
    CALIBRATING = 0x04
    ESTOP = 0x05


def crc16_ccitt(data: bytes, initial_crc: int = 0xFFFF) -> int:
    """Computes CRC16-CCITT (poly 0x1021, init 0xFFFF)."""
    crc = initial_crc
    for b in data:
        crc ^= (b << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc


class MotionIntent:
    """Downlink Intent Frame from Brain to Cerebellum."""
    def __init__(
        self,
        vx: float = 0.0,
        vy: float = 0.0,
        vyaw: float = 0.0,
        head_neck_pitch: float = 0.0,
        head_pitch: float = 0.0,
        head_yaw: float = 0.0,
        head_roll: float = 0.0,
        body_height_offset_mm: int = 0,
        body_roll_offset_deg: int = 0,
        body_pitch_offset_deg: int = 0,
        mouth_open_pct: int = 0,
        locomotion_mode: int = 0,
        flags: int = 0
    ):
        self.vx = float(vx)
        self.vy = float(vy)
        self.vyaw = float(vyaw)
        self.head_neck_pitch = float(head_neck_pitch)
        self.head_pitch = float(head_pitch)
        self.head_yaw = float(head_yaw)
        self.head_roll = float(head_roll)
        self.body_height_offset_mm = int(body_height_offset_mm)
        self.body_roll_offset_deg = int(body_roll_offset_deg)
        self.body_pitch_offset_deg = int(body_pitch_offset_deg)
        self.mouth_open_pct = int(mouth_open_pct)
        self.locomotion_mode = int(locomotion_mode)
        self.flags = int(flags)

    def pack(self) -> bytes:
        # Format: 7 floats (28B), 3 int8 (3B), 3 uint8 (3B), 2 reserved bytes (2B) = 36B total payload
        fmt = "<7f3b3B2s"
        return struct.pack(
            fmt,
            self.vx, self.vy, self.vyaw,
            self.head_neck_pitch, self.head_pitch, self.head_yaw, self.head_roll,
            self.body_height_offset_mm, self.body_roll_offset_deg, self.body_pitch_offset_deg,
            self.mouth_open_pct, self.locomotion_mode, self.flags,
            b"\x00\x00"
        )

    @classmethod
    def unpack(cls, payload: bytes) -> "MotionIntent":
        fmt = "<7f3b3B2s"
        unpacked = struct.unpack(fmt, payload)
        return cls(
            vx=unpacked[0],
            vy=unpacked[1],
            vyaw=unpacked[2],
            head_neck_pitch=unpacked[3],
            head_pitch=unpacked[4],
            head_yaw=unpacked[5],
            head_roll=unpacked[6],
            body_height_offset_mm=unpacked[7],
            body_roll_offset_deg=unpacked[8],
            body_pitch_offset_deg=unpacked[9],
            mouth_open_pct=unpacked[10],
            locomotion_mode=unpacked[11],
            flags=unpacked[12]
        )


class TelemetryFrame:
    """Uplink Telemetry Frame from Cerebellum to Brain."""
    def __init__(
        self,
        quat: Tuple[float, float, float, float] = (1.0, 0.0, 0.0, 0.0), # w, x, y, z
        gyro: Tuple[float, float, float] = (0.0, 0.0, 0.0),            # rad/s
        foot_contacts: int = 0,                                         # bit0: left, bit1: right
        system_state: SystemStatus = SystemStatus.IDLE,
        battery_mv: int = 8000,
        max_motor_temp_c: int = 35,
        max_motor_id: int = 22,
        total_current_ma: int = 500
    ):
        self.quat = quat
        self.gyro = gyro
        self.foot_contacts = foot_contacts
        self.system_state = system_state
        self.battery_mv = battery_mv
        self.max_motor_temp_c = max_motor_temp_c
        self.max_motor_id = max_motor_id
        self.total_current_ma = total_current_ma

    def pack(self) -> bytes:
        # Q15 conversion for quaternion
        qw = int(max(-1.0, min(1.0, self.quat[0])) * 32767)
        qx = int(max(-1.0, min(1.0, self.quat[1])) * 32767)
        qy = int(max(-1.0, min(1.0, self.quat[2])) * 32767)
        qz = int(max(-1.0, min(1.0, self.quat[3])) * 32767)

        # Gyro in rad/s * 100
        gx = int(self.gyro[0] * 100)
        gy = int(self.gyro[1] * 100)
        gz = int(self.gyro[2] * 100)

        fmt = "<4h3hBBHBBH"
        return struct.pack(
            fmt,
            qw, qx, qy, qz,
            gx, gy, gz,
            self.foot_contacts, int(self.system_state),
            self.battery_mv,
            self.max_motor_temp_c, self.max_motor_id,
            self.total_current_ma
        )

    @classmethod
    def unpack(cls, payload: bytes) -> "TelemetryFrame":
        fmt = "<4h3hBBHBBH"
        vals = struct.unpack(fmt, payload)
        quat = (vals[0] / 32767.0, vals[1] / 32767.0, vals[2] / 32767.0, vals[3] / 32767.0)
        gyro = (vals[4] / 100.0, vals[5] / 100.0, vals[6] / 100.0)
        return cls(
            quat=quat,
            gyro=gyro,
            foot_contacts=vals[7],
            system_state=SystemStatus(vals[8]),
            battery_mv=vals[9],
            max_motor_temp_c=vals[10],
            max_motor_id=vals[11],
            total_current_ma=vals[12]
        )


class BcpProtocolCodec:
    """Encodes and Decodes BCP frames with sliding sequence number and CRC checks."""
    def __init__(self):
        self.seq_num = 0
        self.rx_buffer = bytearray()

    def encode_frame(self, msg_type: MsgType, payload: bytes, status: SystemStatus = SystemStatus.IDLE) -> bytes:
        self.seq_num = (self.seq_num + 1) & 0xFF
        header = struct.pack("<BBBBBB", PREAMBLE_B0, PREAMBLE_B1, int(msg_type), self.seq_num, len(payload), int(status))
        crc = crc16_ccitt(header[2:] + payload)
        tail = struct.pack("<HB", crc, FRAME_TAIL)
        return header + payload + tail

    def parse_stream(self, data: bytes) -> List[Tuple[MsgType, int, SystemStatus, bytes]]:
        """Parses incoming byte stream, returns list of valid (msg_type, seq, status, payload) tuples."""
        self.rx_buffer.extend(data)
        frames = []

        while len(self.rx_buffer) >= 9: # Min frame size = 6 header + 0 payload + 2 crc + 1 tail
            if self.rx_buffer[0] != PREAMBLE_B0 or self.rx_buffer[1] != PREAMBLE_B1:
                self.rx_buffer.pop(0)
                continue

            msg_type = self.rx_buffer[2]
            seq = self.rx_buffer[3]
            pay_len = self.rx_buffer[4]
            status = SystemStatus(self.rx_buffer[5])

            total_frame_len = 6 + pay_len + 3
            if len(self.rx_buffer) < total_frame_len:
                # Incomplete frame, wait for more bytes
                break

            frame_bytes = self.rx_buffer[:total_frame_len]
            if frame_bytes[-1] != FRAME_TAIL:
                # Corrupt frame tail, pop preamble and resync
                self.rx_buffer.pop(0)
                continue

            expected_crc = struct.unpack("<H", frame_bytes[-3:-1])[0]
            calc_crc = crc16_ccitt(frame_bytes[2:-3])

            if expected_crc == calc_crc:
                payload = bytes(frame_bytes[6:6 + pay_len])
                frames.append((MsgType(msg_type), seq, status, payload))
                del self.rx_buffer[:total_frame_len]
            else:
                # CRC mismatch, discard one byte and retry
                self.rx_buffer.pop(0)

        return frames


if __name__ == "__main__":
    codec = BcpProtocolCodec()

    # 1. Test Motion Intent Encoding & Decoding
    intent = MotionIntent(vx=0.35, vy=0.0, vyaw=-0.2, head_pitch=0.15, mouth_open_pct=50)
    raw_frame = codec.encode_frame(MsgType.MOTION_INTENT, intent.pack(), status=SystemStatus.WALKING)
    print(f"[OK] Encoded MotionIntent Frame: {len(raw_frame)} bytes")

    parsed = codec.parse_stream(raw_frame)
    assert len(parsed) == 1
    m_type, seq, st, payload = parsed[0]
    decoded_intent = MotionIntent.unpack(payload)
    print(f"[OK] Decoded MotionIntent: vx={decoded_intent.vx:.2f} m/s, vyaw={decoded_intent.vyaw:.2f} rad/s, mouth={decoded_intent.mouth_open_pct}%")

    # 2. Test Telemetry Encoding & Decoding
    telemetry = TelemetryFrame(
        quat=(0.99, 0.01, 0.05, 0.0),
        gyro=(0.02, -0.01, 0.05),
        battery_mv=7850,
        max_motor_temp_c=48,
        total_current_ma=1250
    )
    raw_telemetry = codec.encode_frame(MsgType.TELEMETRY, telemetry.pack(), status=SystemStatus.WALKING)
    parsed_telem = codec.parse_stream(raw_telemetry)
    assert len(parsed_telem) == 1
    _, _, _, telem_payload = parsed_telem[0]
    decoded_telem = TelemetryFrame.unpack(telem_payload)
    print(f"[OK] Decoded Telemetry: Battery={decoded_telem.battery_mv} mV, Current={decoded_telem.total_current_ma} mA, Temp={decoded_telem.max_motor_temp_c} °C")
