"""
tests/test_cadet_motion_studio.py
-----------------------------------
Comprehensive Unit Tests for Cadet Ren Local Motion Studio, 14-DOF Parametric
Kinematics, Disney 12 Principles Interpolator, and Asset Exporters.
Ensures 100% compliance with Constitutional Axiom 5 (Non-Regression Law).
"""

import os
import sys
import tempfile
import pytest
from PIL import Image

# Add scripts directory to sys.path
SCRIPTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts"))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from cadet_motion_studio import (
    CadetPoseState,
    POSE_LIBRARY,
    quintic_ease_in_out,
    interpolate_pose,
    render_pose_frame,
    generate_transition_frames,
    save_transition_gif,
    export_character_dna_sheet,
    load_authentic_sample_data,
    generate_authentic_sample_transition_frames,
    compare_and_audit_sample_consistency,
    POSE_SCALE_ADAPTATION,
    CHARACTER_DNA_SPEC,
    C_FUR_AMBER,
    C_VEST_NAVY,
    C_VEST_GOLD,
    C_FUR_WHITE
)


def test_pose_library_integrity():
    """验证标准姿态库中的所有 10 套招式完整性与解剖学有界性"""
    expected_poses = [
        "idle", "bow", "kungfu", "taichi", "dragon_punch",
        "wave", "wingchun", "cheer", "defend", "sit"
    ]
    for pose_name in expected_poses:
        assert pose_name in POSE_LIBRARY, f"缺少核心姿态: {pose_name}"
        pose = POSE_LIBRARY[pose_name]
        assert isinstance(pose, CadetPoseState)
        # 解剖学坐标安全有界性防护 (Safe Clamping)
        assert -35.0 <= pose.body_y_offset <= 35.0, f"{pose_name} body_y_offset 越界"
        assert 0.70 <= pose.body_squash <= 1.40, f"{pose_name} body_squash 越界"
        assert -20.0 <= pose.body_tilt_deg <= 20.0, f"{pose_name} body_tilt_deg 越界"
        assert 10.0 <= pose.leg_spread <= 35.0, f"{pose_name} leg_spread 越界"
        assert -1.5 <= pose.ear_flop <= 1.5, f"{pose_name} ear_flop 越界"
        assert -2.0 <= pose.tail_sway <= 2.0, f"{pose_name} tail_sway 越界"
        assert len(pose.description) > 0, f"{pose_name} 必须提供描述"


def test_quintic_ease_in_out_properties():
    """验证五次 Hermite 缓入缓出平滑曲线数学性质"""
    # 边界条件 f(0) = 0, f(1) = 1
    assert quintic_ease_in_out(0.0) == pytest.approx(0.0)
    assert quintic_ease_in_out(1.0) == pytest.approx(1.0)
    # 对称中点 f(0.5) = 0.5
    assert quintic_ease_in_out(0.5) == pytest.approx(0.5)
    # 单调递增性
    for t_step in range(10):
        t1 = t_step / 10.0
        t2 = (t_step + 1) / 10.0
        assert quintic_ease_in_out(t1) <= quintic_ease_in_out(t2)
    # 饱和截断保护
    assert quintic_ease_in_out(-0.5) == pytest.approx(0.0)
    assert quintic_ease_in_out(1.5) == pytest.approx(1.0)


def test_interpolation_boundary_conditions():
    """验证插值器两端严格对齐 Pose A 与 Pose B 端点状态"""
    pose_a = POSE_LIBRARY["bow"]
    pose_b = POSE_LIBRARY["kungfu"]

    # t = 0.0 时，必须精确还原 Pose A
    p_start = interpolate_pose(pose_a, pose_b, 0.0, enable_anticipation=False, enable_overshoot=False)
    assert p_start.body_y_offset == pytest.approx(pose_a.body_y_offset, abs=1e-4)
    assert p_start.body_squash == pytest.approx(pose_a.body_squash, abs=1e-4)
    assert p_start.leg_spread == pytest.approx(pose_a.leg_spread, abs=1e-4)

    # t = 1.0 时，必须精确还原 Pose B
    p_end = interpolate_pose(pose_a, pose_b, 1.0, enable_anticipation=False, enable_overshoot=False)
    assert p_end.body_y_offset == pytest.approx(pose_b.body_y_offset, abs=1e-4)
    assert p_end.body_squash == pytest.approx(pose_b.body_squash, abs=1e-4)
    assert p_end.leg_spread == pytest.approx(pose_b.leg_spread, abs=1e-4)


def test_disney_anticipation_and_squash():
    """验证迪士尼第一原则：前摇蓄力 (Anticipation) 会产生反向下蹲与弹性压缩"""
    pose_a = POSE_LIBRARY["idle"]
    pose_b = POSE_LIBRARY["dragon_punch"]

    # 在 t = 0.10 (前摇蓄力中点)，应发生明显的下沉与压缩
    interp_ant = interpolate_pose(pose_a, pose_b, 0.10, enable_anticipation=True)
    interp_no_ant = interpolate_pose(pose_a, pose_b, 0.10, enable_anticipation=False)

    # 蓄力导致下潜位移更大 (body_y_offset 增大)
    assert interp_ant.body_y_offset > interp_no_ant.body_y_offset
    # 蓄力导致挤压变形 (squash < no_ant)
    assert interp_ant.body_squash < interp_no_ant.body_squash


def test_disney_overshoot_damping():
    """验证迪士尼第五原则：招式收尾存在弹簧阻尼超调 (Overshoot Damping)"""
    pose_a = POSE_LIBRARY["idle"]
    pose_b = POSE_LIBRARY["kungfu"]

    # 在 t = 0.88，阻尼弹簧带来微小超调回弹
    interp_over = interpolate_pose(pose_a, pose_b, 0.88, enable_overshoot=True)
    interp_clean = interpolate_pose(pose_a, pose_b, 0.88, enable_overshoot=False)

    # 验证超调产生动态扰动而非僵硬直线
    assert abs(interp_over.body_y_offset - interp_clean.body_y_offset) > 0.01


def test_render_pose_frame_output_dimensions():
    """验证单帧渲染引擎输出的尺寸、通道与颜色保真度"""
    pose = POSE_LIBRARY["kungfu"]
    img = render_pose_frame(pose, width=135, height=240, supersample=2, transparent_bg=False)

    assert isinstance(img, Image.Image)
    assert img.size == (135, 240)
    assert img.mode == "RGBA"

    # 验证透明通道背景模式
    img_trans = render_pose_frame(pose, width=135, height=240, supersample=2, transparent_bg=True)
    assert img_trans.size == (135, 240)
    # 检查角落是否为完全透明 (alpha == 0)
    corner_pixel = img_trans.getpixel((0, 0))
    assert corner_pixel[3] == 0


def test_generate_transition_frames_and_gif():
    """验证多帧连贯生成与 GIF 导出流程"""
    frames = generate_transition_frames("bow", "kungfu", num_frames=8, width=135, height=240)
    assert len(frames) == 8
    for f in frames:
        assert f.size == (135, 240)

    # 测试临时写盘 GIF
    with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        saved_path = save_transition_gif("bow", "kungfu", tmp_path, num_frames=6, fps=12)
        assert os.path.exists(saved_path)
        assert os.path.getsize(saved_path) > 1000
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_character_dna_sheet_integrity():
    """验证 Character DNA 规范字典包含必须的角色视觉不变特征"""
    dna = export_character_dna_sheet()
    assert "positive_prompt_dna" in dna
    assert "negative_prompt_dna" in dna
    assert "visual_invariants" in dna
    assert "action_prompt_templates" in dna

    pos_p = dna["positive_prompt_dna"]
    assert "cadet ren" in pos_p
    assert "red panda" in pos_p
    assert "caramel amber" in pos_p
    assert "tactical vest" in pos_p
    assert "golden paw" in pos_p

    invariants = dna["visual_invariants"]
    assert any("Caramel amber" in inv for inv in invariants)
    assert any("Midnight navy" in inv for inv in invariants)
    assert any("paw emblem" in inv for inv in invariants)


def test_web_cadet_motion_studio_html_integrity():
    """验证 web/cadet_motion_studio.html 网页导播台文件完备性与核心要素"""
    web_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "web", "cadet_motion_studio.html"))
    assert os.path.exists(web_file), "web/cadet_motion_studio.html 必须存在"

    with open(web_file, "r", encoding="utf-8") as f:
        html_src = f.read()

    assert "viewCanvas" in html_src
    assert "sliderProgress" in html_src
    assert "btnPlayPause" in html_src
    assert "POSE_LIB" in html_src
    assert "quinticEaseInOut" in html_src
    assert "interpolatePose" in html_src
    assert "renderCharacter" in html_src


def test_authentic_sample_loading_and_morphing():
    """验证从原始概念原画中精准加载 1:1 样本色彩图与 1-bit 线稿图"""
    sample_bow = load_authentic_sample_data("bow")
    assert sample_bow is not None, "bow 必须具备原画样本资产"
    col, line = sample_bow
    assert col.shape == (240, 135, 3)
    assert line is not None and line.shape == (240, 135)

    # 验证光流与非线性力学合成中间帧
    frames = generate_authentic_sample_transition_frames("bow", "kungfu", num_frames=6)
    assert frames is not None
    assert len(frames) == 6
    for f in frames:
        assert f.size == (135, 240)


def test_authentic_sample_consistency_and_deduplication():
    """验证过渡帧与原画样本逐帧对比的 MSE 低偏差指标与去重有效性"""
    frames = generate_transition_frames("bow", "kungfu", num_frames=8, use_authentic_samples=True)
    audit = compare_and_audit_sample_consistency("bow", "kungfu", frames)

    assert audit["status"] == "audited"
    # 起势与定势必须严格锚定原画 (MSE < 5.0)
    assert audit["mse_start"] < 5.0, f"起势 MSE 偏差过大: {audit['mse_start']}"
    assert audit["mse_end"] < 5.0, f"定势 MSE 偏差过大: {audit['mse_end']}"
    # 消除肢体僵硬与静止卡死：帧间必须具备连续生物位移 (min_diff >= 0.4px)
    assert audit["min_consecutive_diff"] >= 0.4
    assert audit["consistency_passed"] is True
    assert audit["dedup_passed"] is True


def test_character_scale_adaptation_and_volume_preservation():
    """验证动作体量自适应缩放（Volume Preservation）消灭剧烈大小忽大忽小突变"""
    # 验证核心姿态均包含自适应缩放因子
    for p in ["front_idle", "bow", "horse_strike", "taichi", "dragon_punch", "wave_1", "wave_2"]:
        assert p in POSE_SCALE_ADAPTATION
        assert 0.50 <= POSE_SCALE_ADAPTATION[p]["scale"] <= 1.50

    # 加载自适应适配前后的数据对比
    raw_bow_col, _ = load_authentic_sample_data("bow", adapt_scale=False)
    ad_bow_col, _ = load_authentic_sample_data("bow", adapt_scale=True)
    raw_hs_col, _ = load_authentic_sample_data("kungfu", adapt_scale=False)
    ad_hs_col, _ = load_authentic_sample_data("kungfu", adapt_scale=True)

    import numpy as np
    # 测量未适配前 bow (h=193) 与 horse_strike (h=113) 的巨大身高落差 (比值 > 1.65)
    def measure_height(img):
        diff = np.linalg.norm(img.astype(float) - np.array([25, 15, 11]), axis=2)
        mask = (diff > 25)
        mask[:20, :] = False
        mask[218:, :] = False
        ys = np.where(mask)[0]
        return ys.max() - ys.min() + 1 if len(ys) > 0 else 0

    raw_ratio = measure_height(raw_bow_col) / float(measure_height(raw_hs_col))
    ad_ratio = measure_height(ad_bow_col) / float(measure_height(ad_hs_col))

    # 原始未适配存在高达 1.7x 的剧烈忽大忽小突变
    assert raw_ratio > 1.60
    # 经过自适应兼容适配后，两姿态高度比回落到 1.05~1.25 的自然扎马步蹲伏比例
    assert 1.00 <= ad_ratio <= 1.25

