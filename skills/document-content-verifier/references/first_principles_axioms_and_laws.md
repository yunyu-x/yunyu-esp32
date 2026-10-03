# 第一性原理公理体系与数理定律基准 (Axioms, Physical Laws & Constants)

本手册收录了自然科学、工程技术与数理逻辑中最不可动摇的**第一性原理 (First Principles)**、**公理体系 (Axiomatic Systems)**、**国际物理常数 (CODATA 2022)** 与**极端边界定律**。本技能的所有数理计算、量纲推导与逻辑反驳均以本文档为绝对客观裁判标准。

---

## 一、 国际基本物理常数基准 (CODATA 2022 官方推荐值)

| 常数名称 | 符号 | 精确值 / 推荐值 | 国际单位 (SI) | 量纲 $[M^a L^b T^c \dots]$ |
| :--- | :--- | :--- | :--- | :--- |
| **真空光速** (Speed of Light) | $c$ | $299\,792\,458$ (精确定义) | $\text{m}\cdot\text{s}^{-1}$ | $[L T^{-1}]$ |
| **普朗克常数** (Planck Constant) | $h$ | $6.626\,070\,15 \times 10^{-34}$ (精确定义) | $\text{J}\cdot\text{s} = \text{kg}\cdot\text{m}^2\cdot\text{s}^{-1}$ | $[M L^2 T^{-1}]$ |
| **约化普朗克常数** (Dirac Constant) | $\hbar = h / (2\pi)$ | $1.054\,571\,817 \times 10^{-34}$ | $\text{J}\cdot\text{s}$ | $[M L^2 T^{-1}]$ |
| **基本电荷** (Elementary Charge) | $e$ | $1.602\,176\,634 \times 10^{-19}$ (精确定义) | $\text{C} = \text{A}\cdot\text{s}$ | $[I T]$ |
| **玻尔兹曼常数** (Boltzmann Constant) | $k_B$ | $1.380\,649 \times 10^{-23}$ (精确定义) | $\text{J}\cdot\text{K}^{-1} = \text{kg}\cdot\text{m}^2\cdot\text{s}^{-2}\cdot\text{K}^{-1}$ | $[M L^2 T^{-2} \Theta^{-1}]$ |
| **阿伏伽德罗常数** (Avogadro Constant) | $N_A$ | $6.022\,140\,76 \times 10^{23}$ (精确定义) | $\text{mol}^{-1}$ | $[N^{-1}]$ |
| **万有引力常数** (Gravitational Constant) | $G$ | $6.674\,30(15) \times 10^{-11}$ | $\text{m}^3\cdot\text{kg}^{-1}\cdot\text{s}^{-2}$ | $[M^{-1} L^3 T^{-2}]$ |
| **电子静止质量** (Electron Mass) | $m_e$ | $9.109\,383\,7015(28) \times 10^{-31}$ | $\text{kg}$ | $[M]$ |
| **质子静止质量** (Proton Mass) | $m_p$ | $1.672\,621\,923\,69(51) \times 10^{-27}$ | $\text{kg}$ | $[M]$ |
| **真空介电常数** (Vacuum Permittivity) | $\epsilon_0 = 1 / (\mu_0 c^2)$ | $8.854\,187\,8128(13) \times 10^{-12}$ | $\text{F}\cdot\text{m}^{-1} = \text{s}^4\cdot\text{A}^2\cdot\text{m}^{-3}\cdot\text{kg}^{-1}$ | $[M^{-1} L^{-3} T^4 I^2]$ |
| **真空磁导率** (Vacuum Permeability) | $\mu_0$ | $1.256\,637\,062\,12(19) \times 10^{-6}$ | $\text{N}\cdot\text{A}^{-2} = \text{H}\cdot\text{m}^{-1}$ | $[M L T^{-2} I^{-2}]$ |
| **斯特藩-玻尔兹曼常数** | $\sigma = \frac{\pi^2 k_B^4}{60 \hbar^3 c^2}$ | $5.670\,374\,419 \times 10^{-8}$ | $\text{W}\cdot\text{m}^{-2}\cdot\text{K}^{-4}$ | $[M T^{-3} \Theta^{-4}]$ |
| **理想气体常数** | $R = N_A k_B$ | $8.314\,462\,618$ (精确定义) | $\text{J}\cdot\text{mol}^{-1}\cdot\text{K}^{-1}$ | $[M L^2 T^{-2} \Theta^{-1} N^{-1}]$ |

---

## 二、 量纲齐次性与白金汉 $\pi$ 定理 (Dimensional Homogeneity)

### 1. 7 个 SI 基本量纲代数
- 质量 $[M]$ (kg)
- 长度 $[L]$ (m)
- 时间 $[T]$ (s)
- 电流 $[I]$ (A)
- 热力学温度 $[\Theta]$ (K)
- 物质的量 $[N]$ (mol)
- 发光强度 $[J]$ (cd)

### 2. 量纲齐次性公理 (Fourier 公理)
任何表征真实物理规律的方程 $A + B = C$ 必须满足：
$$[A] \equiv [B] \equiv [C]$$
**违背判据**：若符号展开后方程两侧或项之间量纲指数向量不完全一致，则该方程**在数学和物理上必然虚假**。

### 3. 指数与对数函数的无量纲公理
对于任何先验物理量 $X$：
- 若存在 $\exp(X)$、$\ln(X)$、$\sin(X)$，则 $X$ 必须为**绝对无量纲量**：
  $$[X] = [M^0 L^0 T^0 I^0 \Theta^0 N^0 J^0] = 1$$
- 任何试图对有量纲量（如 $\ln(\text{10 kg})$）直接求值的 AI 推导，均属量纲概念混淆。

---

## 三、 不可违背的物理守恒律与极限壁垒

### 1. 守恒公理 (Conservation Axioms / 诺特定理)
- **时间平移不变性 $\iff$ 能量守恒定律**：孤立系统总能量不变，永动机（第一类）不存在。
- **空间平移不变性 $\iff$ 动量守恒定律**：合外力为零时，系统总动量严格守恒，工质推进必须满足动量反冲。
- **空间旋转不变性 $\iff$ 角动量守恒定律**：合外力矩为零时，总角动量守恒。
- **规范对称性 $\iff$ 电荷守恒定律**：封闭系统代数净电荷严格守恒。

### 2. 热力学与能量耗散极限
- **热力学第二定律 (开尔文-克劳修斯表述)**：不可能制造出从单一热源吸热并完全转化为有用功而不产生其他影响的循环机械。
- **卡诺循环效率极限**：任何工作在温度 $T_H$（高温热源）与 $T_C$（低温热源）之间的热机，其实际效率 $\eta$ 必须满足：
  $$\eta \le \eta_{\text{Carnot}} = 1 - \frac{T_C}{T_H} < 100\%$$
- **朗道尔极限 (Landauer's Principle)**：室温 $T$ 下，擦除 1 比特信息所耗散的最小能量下界为：
  $$E_{\min} \ge k_B T \ln 2 \approx 2.87 \times 10^{-21}\ \text{J}\ (T = 300\text{ K})$$
  任何号称计算耗能低于此下界的微纳芯片方案均为伪科学。

### 3. 相对论与因果律极限
- **相对论因果律**：任何具有非零静止质量的物体 $m > 0$，其运动速度 $v < c$；信息传递速度严格不超过 $c$。
- **质能等价关系**：
  $$E^2 = (m_0 c^2)^2 + (p c)^2$$
- **洛伦兹因子发散**：当 $v \to c$ 时，$\gamma = \frac{1}{\sqrt{1 - v^2/c^2}} \to \infty$。

### 4. 量子力学基本下界
- **海森堡不确定性原理**：
  $$\Delta x \cdot \Delta p \ge \frac{\hbar}{2}$$
  $$\Delta E \cdot \Delta t \ge \frac{\hbar}{2}$$
- **光子能量与动量量子化**：$E = h \nu = \hbar \omega$，$p = h / \lambda$。

### 5. 信息论与通信极限
- **香农-哈特利信道容量定理** (Shannon-Hartley Theorem)：在带宽 $B$ (Hz) 与信噪比 $S/N$ 下，连续无失真信道最高传输速率 $C$ (bps) 满足：
  $$C = B \log_2\left(1 + \frac{S}{N}\right)$$
  任何宣称超越该容量上限的编码压缩算法必不成立。
- **奈奎斯特采样定理**：为无失真重构有限带宽连续信号，采样频率 $f_s$ 必须满足：
  $$f_s \ge 2 f_{\max}$$

---

## 四、 数理逻辑公理与常见 AI 逻辑谬误表

### 1. 经典逻辑基本公理 (Aristotle)
1. **同一律 (Law of Identity)**：$A \equiv A$。概念与命题必须自始至终具有确定内涵。
2. **不矛盾律 (Law of Non-Contradiction)**：$\neg (A \wedge \neg A)$。一个命题不能同时既为真又为假。
3. **排中律 (Law of Excluded Middle)**：$A \vee \neg A$。对于任何命题，要么为真，要么为假，不存在第三种独立真值。
4. **充足理由律 (Principle of Sufficient Reason)**：任何真命题必须有其得以成立的充分必要前提。

### 2. 常见 AI 生成逻辑谬误与反驳模板

| 谬误类型 | 形式化结构 | 典型 AI 幻觉案例 | 第一性原理反驳方法 |
| :--- | :--- | :--- | :--- |
| **肯定后件** (Affirming the Consequent) | $(P \implies Q) \wedge Q \vdash P$ | “模型参数越大在 GSM8K 上得分越高。因此由于模型在 GSM8K 上得分高，其参数必定大于 70B。” | 证明存在其他充分原因（如数据微调、蒸馏）亦可导致 $Q$，推导非充要。 |
| **否定前件** (Denying the Antecedent) | $(P \implies Q) \wedge \neg P \vdash \neg Q$ | “如果物体受到外力，速度会改变。因为该卫星不受外力，所以其速度为零。” | 惯性定律：$\neg P \implies$ 保持匀速直线运动，而非静止。 |
| **混淆因果与相关** (Cum Hoc Ergo Propter Hoc) | $\text{Corr}(A, B) > 0 \vdash A \implies B$ | “研究表明代码注释率高的软件崩溃率低，因此增加注释能直接防止内存泄漏。” | 共同隐变量（如开发者工程经验），变量因果图存在混淆因子。 |
| **合成谬误** (Fallacy of Composition) | $\forall x (P(x)) \vdash P(\sum x)$ | “单台服务器的平均响应延迟为 5ms，因此由 10000 台服务器组成的集群总吞吐延迟依然是 5ms。” | 排队论 $M/M/1$ 延迟随拥塞率非线性发散，忽略了网络拓扑与仲裁开销。 |
| **尺度缩放谬误** (Square-Cube Scaling Error) | $L \to k L \vdash \text{Volume} \to k \text{Volume}$ | “将机械臂长由 1m 放大为 10m，其自重和惯量仅增大 10 倍。” | 平方-立方定律：截面积 $\propto L^2$，体积与自重 $\propto L^3$，惯量 $\propto L^5$。 |

---

## 五、 计算机科学与算法下界公理

1. **基于比较的排序下界**：任何基于键比较的排序算法在最坏情况下的时间复杂度下界为：
   $$\Omega(n \log n)$$
   声称发明了 $O(n)$ 时间复杂度的通用比较排序算法必定存在逻辑破绽。
2. **主定理 (Master Theorem)**：对于递归式 $T(n) = a T(n/b) + f(n)$：
   - 若 $f(n) = O(n^c)$ 且 $c < \log_b a$，则 $T(n) = \Theta(n^{\log_b a})$；
   - 若 $c = \log_b a$，则 $T(n) = \Theta(n^{\log_b a} \lg n)$；
   - 若 $c > \log_b a$，则 $T(n) = \Theta(f(n))$。
3. **CAP 定理 (Brewer)**：在分布式数据存储中，一致性 (Consistency)、可用性 (Availability) 和分区容错性 (Partition Tolerance) 三者不可兼得，最多同时满足其二。
4. **阿姆达尔定律 (Amdahl's Law)**：若某任务中可并行化的比例为 $p$，即使采用无限并行核心数，其最大加速比为：
   $$S_{\max} = \lim_{s \to \infty} \frac{1}{(1 - p) + \frac{p}{s}} = \frac{1}{1 - p}$$
