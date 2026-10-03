# SPICE 电路级物理建模与微分方程体系

---

## 1. 锂动力电芯低温内阻倍增模型 (Arrhenius Kinetics)

### 1.1 电化学活化能方程
在严寒低温工况下，锂离子穿透固态电解质界面膜（SEI）与在有机电解液中的扩散离子迁移率遵循阿伦尼乌斯动力学规律：
$$R_{\text{cell}}(T) = R_0 \cdot \exp\left[ \frac{E_a}{R_g} \left( \frac{1}{T} - \frac{1}{T_0} \right) \right]$$
其中：
- $E_a \approx 58.5\text{ kJ/mol}$（典型 15C 软包动力电芯活化能）
- $R_g = 8.314\text{ J/(mol}\cdot\text{K)}$（摩尔气体常数）
- $T_0 = 298.15\text{ K}$（常温 25°C，标称 $R_0 = 80\text{ m}\Omega$）
- $T = 253.15\text{ K}$（极端低温 -20°C，内阻暴增至 $450\text{ m}\Omega$）

### 1.2 POSCAP 独立蓄能维持计算
当主回路发生大电流脉冲放电时，肖特基隔离二极管反向截止，POSCAP 独立承担主控稳压供电：
$$\Delta V_{\text{sag}} = \frac{I_{\text{load}} \cdot \Delta t}{C_{\text{poscap}}}$$
为确保在 $2.0\text{ms}$ 内供电轨跌落 $\le 0.60\text{V}$，所需最小储能容值为：
$$C_{\text{poscap}} \ge \frac{0.14\text{A} \times 2.0\times 10^{-3}\text{s}}{0.60\text{V}} = 466.7\ \mu\text{F} \implies \text{选型 } 470\ \mu\text{F POSCAP}$$

---

## 2. EPM 感性关断二阶振荡与临界阻尼缓冲网络 (Snubber)

### 2.1 二阶微分方程
当开关管 Q1 关断时，线圈电感 $L$、结电容 $C_7$ 与缓冲电阻 $R_5$ 构成标准二阶 RLC 谐振回路：
$$L \frac{d^2 i}{dt^2} + R_5 \frac{di}{dt} + \frac{1}{C_7} i = 0$$
特征多项式根为：
$$s_{1,2} = -\alpha \pm \sqrt{\alpha^2 - \omega_0^2}$$
其中衰减常数 $\alpha = \frac{R_5}{2L}$，无阻尼自振角频率 $\omega_0 = \frac{1}{\sqrt{LC_7}}$。

### 2.2 阻尼比 $\zeta$ 设计判据
二阶系统无量纲阻尼比定义为：
$$\zeta = \frac{\alpha}{\omega_0} = \frac{R_5}{2} \sqrt{\frac{C_7}{L}}$$
- **欠阻尼 ($\zeta < 0.1$)**：电压产生剧烈高频欠阻尼振铃，高次谐波去敏射频接收机；
- **过阻尼 ($\zeta > 1.0$)**：关断时间过长，开关管持续承受大功耗；
- **临界/准临界阻尼 ($0.4 \le \zeta \le 0.7$)**：振荡波形在半个周期内迅速衰减平息。
选定 $L = 42.8\ \mu\text{H}, C_7 = 10\text{ nF}$，取 $R_5 = 56\ \Omega$：
$$\zeta = \frac{56}{2} \sqrt{\frac{10\times 10^{-9}}{42.8\times 10^{-6}}} = 0.428 \implies \text{最优准临界阻尼}$$

---

## 3. 硬件 RC 单稳态脉宽限幅看门狗 (微分电路)

### 3.1 时域阶跃响应
当输入端发生阶跃输入 $V_{\text{in}}(t) = V_{\text{dd}} \cdot u(t)$ 时，微分电容 $C_8$ 与下拉电阻 $R_6$ 的节点电压瞬态响应为：
$$V_{\text{gate}}(t) = V_{\text{dd}} \cdot e^{-\frac{t}{R_6 C_8}}$$
设 MOSFET 导通阈值电压为 $V_{\text{th}}$，当 $V_{\text{gate}}(t) \le V_{\text{th}}$ 时，MOSFET 自动关断，硬切断主回路电流。

### 3.2 自动截止时间理论解
$$t_{\text{cutoff}} = R_6 C_8 \cdot \ln\left(\frac{V_{\text{dd}}}{V_{\text{th}}}\right)$$
对于 $V_{\text{dd}} = 3.3\text{V}, V_{\text{th}} = 1.05\text{V}, R_6 = 47\text{ k}\Omega, C_8 = 100\text{ nF}$：
$$t_{\text{cutoff}} = (47\times 10^3 \cdot 100\times 10^{-9}) \cdot \ln\left(\frac{3.3}{1.05}\right) = 4.7\text{ms} \times 1.145 = 5.38\text{ ms}$$

---

## 4. Littelfuse PPTC 自恢复保险丝电热相变宏模型

### 4.1 焦耳热与散热平衡方程
$$C_{\text{th}} \frac{dT}{dt} = I^2(t) \cdot R(T) - \frac{T - T_{\text{amb}}}{R_{\text{th}}}$$
当局部温度达到聚合物居里相变温度 $T_{\text{curie}} \approx 125^\circ\text{C}$ 时，导电炭黑链结断裂，阻抗呈非线性指数阶跃：
$$R(T) = R_{\text{cold}} + \frac{R_{\text{hot}}}{1 + \exp\left[-\gamma (T - T_{\text{curie}})\right]}$$
其中：
- $R_{\text{cold}} = 0.060\ \Omega$（常温导通电阻）
- $R_{\text{hot}} \ge 15\text{ k}\Omega$（动作后高阻态）
- $\gamma$ 为相变陡度系数

---

## 5. 地回路寄生电感地弹 (Ground Bounce) 与 RC 滤波

### 5.1 地弹电压生成
双电机急刹大电流脉冲在 PCB 接地回路寄生电感 $L_{\text{gnd}}$ 上诱发的瞬态电位差为：
$$V_{\text{bounce}}(t) = L_{\text{gnd}} \cdot \frac{di}{dt}$$
对于 $L_{\text{gnd}} = 6\text{ nH}, \frac{di}{dt} = \frac{12\text{A}}{50\text{ ns}} = 2.4 \times 10^8\text{ A/s}$：
$$V_{\text{bounce}} = 6\times 10^{-9} \times 2.4\times 10^8 = 1.44\text{ V}$$

### 5.2 低通滤波器衰减比
设脉冲持续时间为 $t_p = 50\text{ ns}$，低通滤波器时间常数 $\tau = R_{23} C_{13} = 1\text{k}\Omega \times 100\text{nF} = 100\ \mu\text{s}$：
$$V_{\text{cs\_peak}} \approx V_{\text{bounce}} \cdot \left(1 - e^{-\frac{t_p}{\tau}}\right) \approx V_{\text{bounce}} \cdot \frac{t_p}{\tau} = 1.44\text{V} \times \frac{50\times 10^{-9}}{100\times 10^{-6}} \approx 0.72\text{ mV}$$
从而将地弹残余电压牢牢压制在 DW01A 过流触发门限（150mV）的 $0.48\%$，安全抗扰裕度超 $200\times$。
