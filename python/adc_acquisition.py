
import serial
import time
import csv
import numpy as np
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from pathlib import Path
from tkinter import Tk, filedialog


# ==========================
# 1. 基础参数
# ==========================

SERIAL_PORT = "COM6"
BAUD_RATE = 115200
CAPTURE_SECONDS = 60

timestamps = []
adc_values = []


# ==========================
# 2. 串口数据采集
# ==========================

print("开始连接 ESP32...")

with serial.Serial(
    SERIAL_PORT,
    BAUD_RATE,
    timeout=2
) as ser:

    time.sleep(2)
    ser.reset_input_buffer()

    start_time = time.monotonic()

    while time.monotonic() - start_time < CAPTURE_SECONDS:

        line = ser.readline().decode(
            "utf-8",
            errors="replace"
        ).strip()

        if not line:
            continue

        parts = line.split(",")

        if len(parts) != 2:
            continue

        try:
            timestamp_ms = int(parts[0])
            adc_raw = int(parts[1])

        except ValueError:
            continue

        # 同时保存时间戳和ADC数据
        timestamps.append(timestamp_ms)
        adc_values.append(adc_raw)


# ==========================
# 3. 数据检查
# ==========================

print("\n=== 数据采集结果 ===")

print("采集数量：", len(adc_values))
print("时间戳数量：", len(timestamps))

assert len(timestamps) == len(adc_values)

if len(adc_values) == 0:
    raise RuntimeError("没有采集到有效数据")

timestamps_array = np.array(timestamps)
adc_array = np.array(adc_values)

adc_min = np.min(adc_array)
adc_max = np.max(adc_array)

adc_span = adc_max - adc_min
coverage = adc_span / 4095 * 100

print("ADC最小值：", adc_min)
print("ADC最大值：", adc_max)
print("ADC覆盖跨度：", adc_span)
print("量程覆盖率：", round(coverage, 2), "%")


# ==========================
# 4. 采样间隔分析
# ==========================

time_diff = np.diff(timestamps_array)

if len(time_diff) > 0:

    print("\n=== 采样间隔检查 ===")

    print("平均采样间隔：",
          np.mean(time_diff), "ms")

    print("最小采样间隔：",
          np.min(time_diff), "ms")

    print("最大采样间隔：",
          np.max(time_diff), "ms")

    print("时间戳严格递增：",
          np.all(time_diff > 0))

    print("实际平均采样频率：",
          round(1000 / np.mean(time_diff), 3), "Hz")


# ==========================
# 5. 保存CSV
# ==========================

root = Tk()
root.withdraw()
root.attributes("-topmost", True)

save_path = filedialog.asksaveasfilename(
    initialfile="adc_60s.csv",
    defaultextension=".csv",
    filetypes=[("CSV文件", "*.csv")]
)

root.destroy()

if not save_path:
    raise RuntimeError("已取消CSV保存")

save_dir = Path(save_path).parent

with open(
    save_path,
    "w",
    newline="",
    encoding="utf-8-sig"
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "timestamp_ms",
        "adc_raw"
    ])

    writer.writerows(
        zip(timestamps, adc_values)
    )

print("\nCSV保存成功：", save_path)


# ==========================
# 6. 生成ADC动态曲线
# ==========================

elapsed_time = (
    timestamps_array - timestamps_array[0]
) / 1000

plt.figure(figsize=(10, 5))

plt.plot(elapsed_time, adc_array)

plt.title("ESP32 ADC Acquisition")
plt.xlabel("Time (s)")
plt.ylabel("ADC Raw Value")

plt.ylim(-100, 4200)
plt.grid(True)
plt.tight_layout()

plt.savefig(
    save_dir / "adc_60s_curve.png",
    dpi=200
)

plt.close()


# ==========================
# 7. 生成ADC分布直方图
# ==========================

plt.figure(figsize=(10, 5))

plt.hist(adc_array, bins=30)

plt.title("ADC Value Distribution")
plt.xlabel("ADC Raw Value")
plt.ylabel("Frequency")

plt.grid(True)
plt.tight_layout()

plt.savefig(
    save_dir / "adc_distribution.png",
    dpi=200
)

plt.close()

print("\n两张图表生成成功！")
print("保存目录：", save_dir)
