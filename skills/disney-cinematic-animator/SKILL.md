---
name: disney-cinematic-animator
description: >-
  Professional Disney & Pixar 12 Principles of Animation character design, volumetric procedural kinematics,
  and cinema-grade expressive motion styling for embedded & micro-screen character avatars. Enforces volume
  preservation (squash & stretch), anticipation wind-ups, overlapping action/secondary follow-through, arc trajectories,
  and baby schema appeal.
---

# Disney Cinematic Animator Skill

This skill provides an authoritative, industry-grade framework for designing, evaluating, and implementing
cinema-grade character aesthetics and expressive motion for embedded digital companions (such as M5Stack StickS3
LingBuddy Jollybot).

---

## 1. The 12 Disney Principles of Animation for Embedded Character Kinematics

Based on the canonical masterpiece *"The Illusion of Life: Disney Animation"* by Frank Thomas and Ollie Johnston,
embedded procedural character animation must strictly enforce these 12 foundational laws:

### 1. Squash and Stretch (挤压与拉伸与体积守恒)
* **The Iron Law of Volume Preservation**: An organic character is never made of rigid plastic. When moving, jumping, or landing, the character compresses along the impact axis while expanding along the transverse axis such that:
  $$\text{Volume} \approx W \times H = \text{Constant}$$
* **Mathematical Model**:
  $$\text{scale}_x(t) = 1.0 + A \cdot \cos(\omega t), \quad \text{scale}_y(t) = \frac{1.0}{\text{scale}_x(t)}$$
* **Impact Cushioning**: Upon landing from a jump, vertical compression drops to $0.82\times$ while width expands to $1.22\times$ for $120\text{ms}$ before springing back.

### 2. Anticipation (预备蓄力动作)
* **Visual Forewarning**: Real organisms do not initiate high-energy movements instantaneously. Before a jump, punch, or leap, the character must perform an inverse wind-up:
  - Jump: Deep crouch (Squat downwards $-12\text{px}$) for $15\%$ of action duration before explosive upward launch.
  - Punch / Wave: Pull arm backwards and compress chest before swinging forward.

### 3. Staging (鲜明清晰的舞台构图与剪影度)
* On a constrained micro-screen ($135 \times 240\text{px}$), visual noise destroys immersion.
* **Silhouette Readability**: Poses must be distinctly identifiable purely from their outer silhouette (Negative space between limbs and torso, head tilted at dynamic angle).

### 4. Straight Ahead Action & Pose to Pose (关键帧姿态与平滑补间)
* Break down each motion into 3 primary keyframe phases:
  1. **Anticipation (蓄力前摇, 0% ~ 18%)**
  2. **Action Climax / Stroke (招式高潮爆发, 18% ~ 65%)**
  3. **Recovery / Settle (回弹定势收招, 65% ~ 100%)**

### 5. Follow Through & Overlapping Action (多重惯性重叠与跟随)
* Different anatomical structures possess different mass and inertia. They never stop simultaneously:
  - **Ear Flopping Delay**: Ears lag torso roll by $\Delta t \approx 65\text{ms}$ with spring-damper overshoot:
    $$\theta_{ear}(t) = \theta_{head}(t - \tau) + A_{flop} \cdot \sin(2\pi f t) e^{-\zeta t}$$
  - **Tail Sway Inertia**: Tail oscillates in a trailing harmonic wave behind body translation.
  - **Soft Belly Jiggle**: Chubby pear belly compresses and bounces independently of the ribcage.

### 6. Slow In and Slow Out (缓入缓出 / S 曲线平滑过渡)
* Never use linear interpolation ($\text{lerp}$) for character limbs.
* Enforce **Cubic Hermite Spline / Smoothstep / Quintic Ease**:
  $$S(t) = 3t^2 - 2t^3 \quad \text{or} \quad \text{EaseInOutCubic}(t) = \begin{cases} 4t^3 & t < 0.5 \\ 1 - \frac{(-2t + 2)^3}{2} & t \ge 0.5 \end{cases}$$

### 7. Arcs (圆弧自然轨迹)
* Biological skeletal joints are hinged levers. Every wrist, paw, knee, and ear moves along **circular and parabolic arcs**, never straight Euclidean vectors:
  $$x_{paw}(t) = x_{shoulder} - L \cdot \sin(\theta(t)), \quad y_{paw}(t) = y_{shoulder} + L \cdot \cos(\theta(t))$$

### 8. Secondary Action (次级微动态与情绪同理心)
* When executing a primary action (e.g. Kungfu palm strike), secondary micro-dynamics breathe life into the character:
  - Synchronous eye pupil micro-saccades ($1\sim 2\text{px}$ gaze tracking).
  - Chest breathing expansion cycle ($f = 0.4\text{Hz}$).
  - Rosy blush pulsing upon victory/cheering.

### 9. Timing (节奏律动与轻重拍)
* Animation is pacing. Fast punch ($80\text{ms}$) followed by prolonged power-hold pose ($400\text{ms}$) produces explosive weight.

### 10. Exaggeration (适度戏剧化夸张)
* Exaggerate limb extension by $+15\%\sim 25\%$ at stroke apex to convey strength, vitality, and Disney appeal without breaking anatomy.

### 11. Solid Drawing (三维体积感、光影与遮挡)
* Cel-shading with 3 explicit light levels:
  - **Keylight (受光暖金)**: Top-rim incident light highlight.
  - **Midtone (主皮毛焦糖暖棕)**: Body base color.
  - **Shadow / Ambient Occlusion (深可可遮蔽)**: Contact shadows, under-belly occlusion.
  - **Z-Depth Sorting**: Painter's algorithm ordering far limbs $\to$ torso $\to$ near limbs.

### 12. Appeal (亲和力与幼儿图式 Baby Schema)
* Enforce Konrad Lorenz's *Kindchenschema*:
  - Head-to-body ratio $\approx 1:1.1$.
  - Large rounded doe eyes with primary white star highlights and secondary catchlights.
  - Plump pear-shaped tummy with sweet cream patch and cute belly button.
  - Classic cat-like "$\omega$" lip smile arcs.

---

## 2. Robust Embedded Geometry Safety Rules

To guarantee **zero memory corruption, zero division by zero, and zero FreeRTOS CPU panics**:
1. **Radius Strict Positivity**: Every radius passed to `fillCircle`, `drawCircle`, `fillEllipse`, `drawEllipse`, `drawArc` MUST be clamped:
   $$r \ge 1, \quad r_x \ge 1, \quad r_y \ge 1$$
2. **Arc Radius Invariance**: For `drawArc(x, y, r_0, r_1, a_0, a_1)`:
   $$r_0 \ge 1, \quad r_1 \ge r_0 + 1$$
3. **Polygon Coincidence Protection**: For tapered capsules connecting $(x_1, y_1)$ to $(x_2, y_2)$, if $\text{distance} < 1.0\text{px}$, fall back to drawing single circular paw.
4. **Finite Coordinates**: All trigonometric calculations must be bounded within screen bounds $[-30, 270]$.
