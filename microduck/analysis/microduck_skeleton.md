# Repository Context Package: microduck

> 纯确定性打包生成，严格按 POSIX 路径字典序排列以优化 LLM Prompt Caching 命中率。

## 1. 仓库全景指标
- **文件总数**: 21
- **代码总行数**: 6501
- **预估 Token 数**: ~84,509
- **脱敏凭据数**: 0

## 2. 目录拓扑结构
```text
microduck/
  └── .gitignore (1.3 KB)
  └── AGENTS.md (2.3 KB)
  └── CLAUDE.md (0.0 KB)
  └── CONTRIBUTING.md (9.0 KB)
  └── Cargo.toml (6.2 KB)
  └── LICENSE (11.3 KB)
  └── README.md (5.1 KB)
  ├── btd/
    └── Cargo.toml (3.0 KB)
    ├── src/
      └── bluez.rs (54.7 KB)
      └── chorale.rs (24.1 KB)
      └── lib.rs (2.1 KB)
      └── link.rs (5.4 KB)
      └── main.rs (8.2 KB)
      └── pairing.rs (9.5 KB)
      └── route.rs (53.8 KB)
      └── session.rs (42.6 KB)
      └── upstream.rs (17.3 KB)
    ├── systemd/
      └── btd.service (3.9 KB)
      ├── sysusers.d/
        └── btd.conf (1.2 KB)
  ├── configd/
    └── Cargo.toml (2.4 KB)
    ├── src/
      └── bluez.rs (55.5 KB)
      └── identity.rs (7.2 KB)
      └── lib.rs (1.9 KB)
      └── logs.rs (17.3 KB)
      └── main.rs (25.8 KB)
      └── net.rs (15.1 KB)
      └── nm.rs (37.0 KB)
      └── pad.rs (23.1 KB)
      └── power.rs (2.5 KB)
      └── store.rs (13.6 KB)
      └── units.rs (10.6 KB)
    ├── systemd/
      └── configd.service (5.7 KB)
      ├── sysusers.d/
        └── README (0.4 KB)
  ├── deploy/
    └── README.md (25.3 KB)
    ├── audio/
      └── aic3104-i2c3.dts (3.1 KB)
      └── aic3104-init.sh (2.3 KB)
      ├── aic3x-dkms/
        └── Makefile (0.4 KB)
        └── dkms.conf (0.4 KB)
        └── tlv320aic3x-i2c.c (1.9 KB)
        └── tlv320aic3x.c (64.2 KB)
        └── tlv320aic3x.h (8.9 KB)
      └── i2c3-pihat.dts (2.9 KB)
    ├── dev-key/
      └── README.md (1.4 KB)
      └── team.dev.pub (0.1 KB)
    ├── journald.conf.d/
      └── 10-robot.conf (2.4 KB)
    ├── overlays/
      └── rk3568-npu-enable.dts (1.4 KB)
    └── robotd.toml (28.1 KB)
    ├── trusted_keys/
      └── README.md (2.0 KB)
      └── release-1.pub (0.1 KB)
      └── release-2.pub (0.1 KB)
      └── release-3.pub (0.1 KB)
    └── updater.toml (10.5 KB)
  ├── docs/
    └── README.md (6.7 KB)
    ├── design/
      └── app-path-design.md (63.1 KB)
      └── architecture.md (36.7 KB)
      └── boot-recovery-net.md (13.6 KB)
      └── mobile-app.md (18.6 KB)
      └── policy-channel-design.md (51.6 KB)
      └── remote-access-design.md (83.3 KB)
      └── remote-webrtc.md (36.8 KB)
      └── restart-order.md (27.8 KB)
      └── robotd-design.md (66.8 KB)
      └── simulation.md (20.5 KB)
      └── updater-design.md (88.2 KB)
      └── webrtc-console.md (21.6 KB)
    └── faq.md (4.6 KB)
    ├── ideas/
      └── autonomous_behavior.md (6.7 KB)
    └── policy-manifest.md (9.2 KB)
    ├── project/
      └── ci-setup.md (11.2 KB)
      └── idle-cpu.md (9.3 KB)
      └── install-path-gap.md (36.9 KB)
      └── media-bringup.md (32.6 KB)
      └── npu-bringup.md (11.1 KB)
      └── pad-minimal-pairing.md (12.5 KB)
      └── roadmap.md (24.9 KB)
      └── slice-2-bringup.md (8.1 KB)
      └── tof-on-demand.md (11.0 KB)
      └── update-over-ble.md (10.1 KB)
    └── recurrent-policies.md (4.4 KB)
    ├── robot/
      └── cheatsheet-dev.md (6.2 KB)
      └── cheatsheet.md (49.9 KB)
      └── dev-push.md (12.6 KB)
      └── duckctl.md (23.8 KB)
      └── install-by-hand.md (4.5 KB)
      └── install-dev.md (12.9 KB)
      └── pair-a-gamepad.md (14.8 KB)
      └── simulation.md (12.8 KB)
  ├── duck-ble/
    └── Cargo.toml (1.0 KB)
    ├── src/
      └── adv.rs (5.9 KB)
      └── framing.rs (14.8 KB)
      └── gatt.rs (2.8 KB)
      └── lib.rs (1.4 KB)
  ├── duck-control/
    └── Cargo.toml (2.7 KB)
    ├── examples/
      └── policy-rehearsal.rs (2.9 KB)
    ├── src/
      └── bus.rs (33.2 KB)
      └── fall.rs (11.7 KB)
      └── imu.rs (13.7 KB)
      └── io.rs (15.9 KB)
      └── lib.rs (1.0 KB)
      └── model.rs (12.5 KB)
      └── obs.rs (16.6 KB)
      └── policy.rs (33.3 KB)
      └── safety.rs (39.6 KB)
      └── sim.rs (19.4 KB)
    ├── tests/
      ├── fixtures/
        └── bad_action_count.onnx (0.2 KB)
        └── bad_batch.onnx (2.5 KB)
        └── bad_rank.onnx (0.2 KB)
        └── bad_state_shape.onnx (2.5 KB)
        └── bad_width.onnx (2.5 KB)
        └── dynamic_batch.onnx (2.5 KB)
        └── dynamic_hidden.onnx (2.5 KB)
        └── extra_input.onnx (2.5 KB)
        └── feedforward.onnx (0.2 KB)
        └── generate.py (4.1 KB)
        └── lstm.onnx (2.5 KB)
        └── lstm_changed.onnx (2.5 KB)
        └── missing_state.onnx (2.4 KB)
        └── nan_state.onnx (2.5 KB)
        └── wrong_type.onnx (2.5 KB)
      └── recurrent_policy.rs (5.7 KB)
  ├── duck-detect/
    └── Cargo.toml (1.3 KB)
    ├── src/
      ├── bin/
        └── duck-bench.rs (11.7 KB)
      └── lib.rs (10.5 KB)
      └── onnx.rs (3.8 KB)
      └── rknn.rs (19.7 KB)
  ├── duck-ether/
    └── Cargo.toml (0.6 KB)
    ├── src/
      └── main.rs (17.9 KB)
  ├── duck-ipc-proto/
    └── Cargo.toml (1.1 KB)
  ├── duckctl/
    └── Cargo.toml (4.5 KB)
    ├── examples/
      └── advwatch.rs (9.1 KB)
    ├── src/
      └── main.rs (167.6 KB)
  ├── hooks/
    └── postinstall (9.5 KB)
    └── preinstall.in (10.2 KB)
  ├── kinematics/
    └── Cargo.toml (0.9 KB)
    ├── assets/
      ├── alpha/
        └── robot_walk.xml (6.8 KB)
    ├── src/
      └── hand.rs (16.9 KB)
      └── head.rs (15.7 KB)
      └── lib.rs (14.5 KB)
      └── math.rs (6.2 KB)
      └── mjcf.rs (7.3 KB)
      └── tof.rs (15.7 KB)
    ├── tests/
      ├── fixtures/
        └── fk_alpha.json (165.7 KB)
      └── fk_against_mujoco.rs (2.9 KB)
      └── perf_probe.rs (2.3 KB)
  ├── mediad/
    └── Cargo.toml (10.0 KB)
    ├── src/
      └── camera.rs (22.3 KB)
      └── config.rs (4.5 KB)
      └── detect.rs (16.9 KB)
      └── exposure.rs (32.4 KB)
      └── frame.rs (21.2 KB)
      └── lib.rs (3.4 KB)
      └── main.rs (35.2 KB)
      └── pipeline.rs (126.6 KB)
      └── producer.rs (10.9 KB)
      └── relay.rs (117.7 KB)
      └── route.rs (29.9 KB)
      └── session.rs (31.3 KB)
      └── snapshot.rs (5.4 KB)
      └── stream.rs (42.8 KB)
      └── turn.rs (23.5 KB)
      └── upstream.rs (12.5 KB)
      └── web.rs (15.0 KB)
    ├── systemd/
      └── mediad.service (8.3 KB)
      ├── sysusers.d/
        └── mediad.conf (1.1 KB)
    ├── webclient/
      └── index.html (88.3 KB)
      ├── space/
        └── Dockerfile (1.1 KB)
        └── README.md (2.8 KB)
        └── entrypoint.sh (3.4 KB)
  ├── odometry/
    └── Cargo.toml (0.8 KB)
    ├── src/
      └── anchors.rs (3.3 KB)
      └── lib.rs (17.4 KB)
  ├── pad-imu/
    └── Cargo.toml (0.5 KB)
    ├── src/
      └── lib.rs (22.5 KB)
  ├── padd/
    └── Cargo.toml (2.4 KB)
    ├── src/
      └── main.rs (66.5 KB)
      └── tap.rs (54.9 KB)
    ├── systemd/
      └── padd.service (5.2 KB)
      ├── sysusers.d/
        └── padd.conf (1.1 KB)
  ├── pet-detect/
    └── Cargo.toml (0.9 KB)
    └── README.md (1.6 KB)
    ├── models/
      └── pet_detect.onnx (19.7 KB)
    ├── src/
      ├── bin/
        └── detect.rs (2.7 KB)
        └── features.rs (1.7 KB)
      └── lib.rs (13.7 KB)
      └── worker.rs (21.0 KB)
    ├── training/
      └── train.py (5.8 KB)
  ├── robotctl/
    └── Cargo.toml (2.9 KB)
    ├── src/
      └── camera.rs (13.8 KB)
      └── cells.rs (1.8 KB)
      └── configure.rs (61.1 KB)
      └── duck.rs (36.8 KB)
      └── frame.rs (6.5 KB)
      └── imu_view.rs (11.2 KB)
      └── monitor.rs (207.9 KB)
      └── path_map.rs (13.4 KB)
      └── show.rs (30.3 KB)
  ├── robotd-params/
    └── Cargo.toml (1.4 KB)
    ├── src/
      └── edit.rs (62.1 KB)
      └── lib.rs (154.8 KB)
      └── registry.rs (27.8 KB)
  ├── robotd/
    └── Cargo.toml (2.6 KB)
    ├── src/
      └── chorale.rs (56.0 KB)
      └── control.rs (31.7 KB)
      └── intents.rs (28.9 KB)
      └── params.rs (0.4 KB)
      └── soc.rs (14.8 KB)
      └── sound.rs (41.8 KB)
      └── theremin.rs (20.7 KB)
    ├── systemd/
      └── robotd.service (4.4 KB)
    ├── tests/
      └── single_instance.rs (13.5 KB)
      └── updater_gate.rs (20.4 KB)
  ├── scripts/
    └── bake-duck-mesh.py (9.0 KB)
    └── board-test.sh (58.5 KB)
    └── ci-release-notes.sh (2.7 KB)
    └── cross-sysroot.sh (9.7 KB)
    └── dev-build.Dockerfile (2.1 KB)
    └── dev-push.sh (29.0 KB)
    └── duck-sim (57.5 KB)
    └── install.sh (51.4 KB)
    └── migrate-network.sh (22.9 KB)
    └── pad-link-test.sh (20.1 KB)
    └── pad-stack-report.sh (31.1 KB)
    └── provision-board.sh (44.0 KB)
    └── provision.sh (37.6 KB)
    └── publish-console.sh (5.0 KB)
    └── publish-space.sh (3.7 KB)
    └── rkaiq-modinfo-shim.c (3.5 KB)
    └── robot-boot-check (5.8 KB)
    └── robot-rescue (9.6 KB)
    └── seed-detector.sh (6.3 KB)
    └── seed-policies.sh (11.7 KB)
    └── setup-board.sh (54.7 KB)
    └── setup-gstreamer.sh (32.6 KB)
    └── setup-login.sh (10.1 KB)
    └── setup-npu.sh (12.1 KB)
    └── setup-quiet-boot.sh (4.5 KB)
    └── setup-rkaiq.sh (16.4 KB)
    └── systemd-test.Dockerfile (1.1 KB)
    └── systemd-test.sh (19.7 KB)
  ├── sounds/
    └── Cargo.toml (0.7 KB)
    ├── scores/
      └── duck_strut.mid (2.9 KB)
      └── outer_wilds.mid (4.9 KB)
      └── wistful.duckscore (4.2 KB)
    ├── src/
      ├── chorale/
        └── beat.rs (22.8 KB)
        └── midi.rs (32.2 KB)
        └── mod.rs (62.6 KB)
        └── text.rs (20.4 KB)
      └── lib.rs (7.8 KB)
      └── main.rs (18.0 KB)
      └── personality.rs (7.2 KB)
      └── rng.rs (5.7 KB)
      └── stream.rs (39.2 KB)
      └── synth.rs (8.9 KB)
      └── voices.rs (16.6 KB)
  ├── spaces/
    ├── hello/
      └── Dockerfile (0.8 KB)
      └── README.md (0.6 KB)
      └── app.py (2.4 KB)
      └── requirements.txt (0.0 KB)
    ├── policy-playground/
      └── Dockerfile (1.4 KB)
      └── README.md (4.8 KB)
      └── entrypoint.sh (3.4 KB)
      └── index.html (45.1 KB)
      ├── web/
        └── .gitignore (0.0 KB)
        └── index.html (0.3 KB)
        └── package-lock.json (43.9 KB)
        └── package.json (0.4 KB)
        ├── src/
          └── auth.ts (7.8 KB)
          └── hub.ts (13.6 KB)
          └── main.ts (28.8 KB)
          └── rendezvous.ts (13.6 KB)
          └── style.css (5.1 KB)
        └── tsconfig.json (0.5 KB)
        └── vite.config.ts (1.1 KB)
    ├── shared/
      └── control.py (7.5 KB)
      └── rendezvous.py (11.3 KB)
      └── wire.py (19.2 KB)
    ├── vision-demo/
      └── Dockerfile (3.8 KB)
      └── README.md (5.8 KB)
      └── app.py (23.3 KB)
      └── boot.py (2.1 KB)
      └── control.py (0.0 KB)
      └── filters.py (6.4 KB)
      └── receiver.py (13.6 KB)
      └── rendezvous.py (0.0 KB)
      └── requirements.txt (1.7 KB)
      └── wire.py (0.0 KB)
  ├── test-support/
    └── Cargo.toml (0.6 KB)
    ├── examples/
      └── fake-release.rs (7.1 KB)
      └── systemd-fixture.rs (12.7 KB)
    ├── src/
      └── lib.rs (10.7 KB)
  ├── tof/
    └── Cargo.toml (2.3 KB)
    └── build.rs (4.7 KB)
    ├── src/
      └── config.rs (2.7 KB)
      └── imu.rs (12.0 KB)
      └── lib.rs (7.0 KB)
      └── main.rs (40.2 KB)
      └── sensor.rs (14.7 KB)
      └── status.rs (3.5 KB)
    ├── systemd/
      ├── sysusers.d/
        └── tofd.conf (0.6 KB)
      └── tofd.service (2.0 KB)
    ├── vendor/
      └── LICENSE.txt (0.4 KB)
      └── platform.c (4.2 KB)
      └── probe.c (2.5 KB)
      ├── vl53l5cx/
        └── platform.h (2.2 KB)
        └── shim.c (2.8 KB)
        └── vl53l5cx_api.c (38.2 KB)
        └── vl53l5cx_api.h (27.0 KB)
      ├── vl53l8cx/
        └── platform.h (2.2 KB)
        └── shim.c (2.8 KB)
        └── vl53l8cx_api.c (39.5 KB)
        └── vl53l8cx_api.h (27.5 KB)
  ├── updater/
    └── Cargo.toml (3.1 KB)
    ├── src/
      └── account.rs (8.1 KB)
      └── config.rs (41.1 KB)
      └── engine.rs (182.4 KB)
      └── faults.rs (5.4 KB)
      └── fsutil.rs (3.1 KB)
      └── hooks.rs (21.8 KB)
      └── ipc.rs (49.3 KB)
      └── journal.rs (36.8 KB)
      └── lib.rs (15.6 KB)
      └── main.rs (37.2 KB)
      └── manifest.rs (9.9 KB)
      └── orphan.rs (14.9 KB)
      └── policy.rs (72.6 KB)
      └── preflight.rs (18.6 KB)
      └── reconcile.rs (16.7 KB)
      └── robot.rs (22.6 KB)
      ├── source/
        └── github.rs (25.9 KB)
        └── hf_hub.rs (7.8 KB)
        └── http.rs (16.8 KB)
        └── local.rs (12.4 KB)
        └── mod.rs (4.8 KB)
      └── spawn.rs (6.2 KB)
      └── store.rs (17.6 KB)
      └── transcript.rs (19.0 KB)
      └── unix.rs (2.7 KB)
      └── verify.rs (22.2 KB)
    ├── systemd/
      └── robot-boot-check.service (1.7 KB)
      └── robot-boot-check.timer (1.4 KB)
      ├── sysusers.d/
        └── robot.conf (0.6 KB)
      └── updaterd.service (4.0 KB)
    ├── tests/
      └── apply.rs (107.8 KB)
      └── download.rs (10.5 KB)
      └── install.rs (15.9 KB)
      └── ipc.rs (55.7 KB)
    └── updater.example.toml (10.3 KB)
  ├── uyvy/
    └── Cargo.toml (0.9 KB)
    ├── src/
      └── lib.rs (16.2 KB)
  ├── xtask/
    └── Cargo.toml (1.2 KB)
    ├── src/
      └── main.rs (101.6 KB)
    ├── tests/
      └── artifact.rs (19.4 KB)
      └── rescue.rs (22.2 KB)
      └── sideload.rs (4.9 KB)
```

## 3. 源文件代码包

### File: `.gitignore` (30 lines, ~300 tokens)
```text
# Any level, not just the root: running cargo inside a member directory creates a
# nested one (updater/target), and `/target` would not match it.
target/

# ── never commit signing material ────────────────────────────────────────────
#
# `cargo xtask keygen` refuses to write keys inside the repo, so these patterns are
# belt-and-braces for keys arriving some other way — copied in by hand, dropped by a
# script, left behind by a test. A committed signing key cannot be un-leaked by
# deleting the file: it stays in history, and every robot that trusts it must be
# considered compromised.
*.key
*.pem
secret*
!*.pub

# Release output. Contains artifacts and signatures; regenerate rather than commit.
/dist
/staged

# Playground and scratch state (see updater/examples/playground.rs).
/verify

# Python bytecode from the demo Space, which is source rather than a build here.
__pycache__/

# A venv beside a Space's source, for running one locally. `uv venv` writes its own `.gitignore`
# holding `*` so it self-ignores; this is for the person who reaches for `python -m venv`, which
# does not, and it is the same accident `__pycache__` above was added for.
.venv/

```

### File: `AGENTS.md` (41 lines, ~593 tokens)
```md
# Working in this repository

`CONTRIBUTING.md` is the reference: building, testing, layout, conventions, releasing. This page
is the short list of things that are easy to get backwards, and where the answer lives when they
are not here.

## Docs own mechanisms; one page each

`docs/README.md` assigns every mechanism to one design doc. When a fact belongs to a page listed
there, every other page says one sentence and links. When two pages disagree, the one that does
not own the mechanism is the bug — and when behaviour and a design doc disagree, the doc is the
bug. [`docs/faq.md`](docs/faq.md) is the task-shaped front door for someone building against a
robot rather than changing it.

## A consumer uses WebRTC. `media.stream` is the fallback

The robot publishes H.264 over WebRTC, and that is the default for anything consuming a duck's
camera — it is encrypted end to end, it carries the control channel on the same session, and it
has a return path. It works from a data centre because the robot offers a relay candidate
(`remote-access-design.md` §6).

`media.stream` — the robot dialling an outbound WebSocket and pushing frames to you — is the
fallback for a **program** consuming **frames only** on a **long-running** stream, where relay
metering is the thing that matters. It has no return path and no control channel.

This is worth stating because the repository reads the other way round if you only follow the
code: `media.stream` was built when the relay endpoint was dead and WebRTC genuinely could not
connect from a data centre, so its module doc argues its own case at length. That endpoint is
fixed. Do not conclude from the volume of prose that it is the preferred path.

## Never design around a version difference

One user, one robot. An old component's limits are a question to raise, not something to route
around — bump `API_VERSION` and name the install consequence. A version skew is logged and served,
never refused; only a genuinely missing route or an unknown parameter may refuse.

## Releases are how a fix reaches a robot

`main` being fixed is not a robot being fixed. Robots on the stable channel move when a release is
cut, and a dev build from a branch is superseded by the next `daemon-dev-main` the board's
six-hourly check finds. `docs/design/updater-design.md` owns the mechanism.

```

### File: `CLAUDE.md` (1 lines, ~2 tokens)
```md
AGENTS.md
```

### File: `CONTRIBUTING.md` (181 lines, ~2286 tokens)
```md
# Contributing

For working on the daemons themselves. To use a robot rather than change it, see the
[README](README.md).

## Building and testing

Needs Rust **1.89+** (stable). The robot is aarch64 Linux; you develop on Linux or macOS, and
the two are not quite the same checkout — see below.

```bash
cargo test --workspace
```

No hardware, no network, no Docker. If they pass, your checkout is sound.

**On Linux** that command needs some C libraries first, the same ones CI installs: `padd` binds
`libudev` through `gilrs`, and `mediad`'s pipeline is `cfg(target_os = "linux")`, so a Linux host
compiles GStreamer where a Mac does not.

```bash
sudo apt-get install -y libudev-dev libgstreamer1.0-dev
```

```bash
sudo apt-get install -y libgstreamer-plugins-base1.0-dev libgstreamer-plugins-bad1.0-dev
```

**On macOS** the command above is the whole of it — **942 tests passing**, nothing excluded. Two
of the ToF driver's own tests do not run there, because there is no driver to run them against:
`vendor/platform.c` reaches the bus through `linux/i2c.h`, so `build.rs` compiles it on Linux
targets only and `sensor.rs` offers a `Sensor` that cannot be opened. `tofd` still builds and
`tofd --fake` still serves frames, which is the only way it runs off a board anyway.

Those tests are also where the engine's failure paths are: a bad signature, a release that comes
up unhealthy, a post-install hook that fails, power loss between the swap and the health gate.
Each drives the real engine with the fault injected rather than a mock of it, so
`updater/tests/apply.rs` is the honest answer to "what does this actually guarantee" — more so
than anything you could run by hand.

One crate at a time, and formatting:

```bash
cargo test -p <crate>
```

```bash
cargo fmt --all
```

`configd`'s NetworkManager client and `btd`'s BlueZ client are **Linux-only**, so a host build and
a green test run say nothing about them. Lint against the board's target or the breakage ships:

```bash
RUSTFLAGS="-D warnings" cargo clippy -p configd --all-targets --target aarch64-unknown-linux-gnu
```

`scripts/board-test.sh` runs in CI against the userland we ship: it cross-compiles for the board
and executes 60 assertions — rollback, tampered-artifact refusal, boot-counter recovery, socket
modes, peer-credential authorization, and everything `setup-board.sh` and `install.sh` do to a
board — on Debian 13 (Trixie). `BOARD_IMAGES=` runs it against another.

To run a change on a real robot without publishing it, `scripts/dev-push.sh <user@board>` builds
here and installs there as an ordinary gated update. It cross-compiles with `cargo zigbuild` by
default, or with `--docker` builds inside the board's userland instead, which needs no toolchain
set up at all. Setup, the flags and the failure modes:
[`docs/robot/dev-push.md`](docs/robot/dev-push.md).

## The layout

```
the daemons — one crate each, one unit each, all in the same release artifact
  robotd/         control daemon: the 50 Hz loop, the voice, the theremin, the chorale
  updater/        engine + updaterd
  configd/        wifi · robot name · pairing PIN · reboot · gamepad pairing
  btd/            the BLE front door
  padd/           gamepad → intents — an ordinary socket client, no privileged access
  mediad/         camera, mic, WebRTC, the remote gateway, and the console it serves
  tof/            tofd: the head's 8×8 depth sensor. Publishes frames, reads nothing

the libraries they drive — no sockets, no systemd, nothing starts them
  duck-ipc-proto/ the wire contract
  duck-control/   the control core: model · bus · IMU · observations · policy · safety
  kinematics/     the MJCF model and forward kinematics; head and hand chains
  odometry/       where the robot has been, from foot contacts and the IMU
  sounds/         synthesis, per-robot voice personality, the chorale's score
  pet-detect/     a small CNN that hears head scratches on the onboard mic
  robotd-params/  robotd's startup parameters: schema, defaults, validation

the tools
  robotctl/       the local CLI, including `monitor`
  duckctl/        the laptop-side client — never shipped, never cross-built
  xtask/          package · sign · promote — build tooling, never shipped
  test-support/   signed-release fixtures for tests; never shipped

deploy/         what a robot is configured with: updater.toml, robotd.toml, trust anchor, journald
hooks/          preinstall · postinstall — what runs inside an update, from the artifact,
                and the only thing that runs on every board on every update: anything
                install.sh does to a board belongs here too (updater-design.md §9.1)
scripts/        provision-board.sh · dev-push.sh + dev-build.Dockerfile (from your machine) ·
                provision.sh → setup-board.sh → setup-gstreamer.sh · setup-rkaiq.sh ·
                migrate-network.sh · install.sh (on the board) ·
                setup-login.sh · setup-quiet-boot.sh (install.sh and postinstall both run these) ·
                robot-boot-check · robot-rescue (recovery, installed to /usr/local/sbin) ·
                pad-link-test.sh · pad-stack-report.sh (gamepad radio, on the board) ·
                board-test.sh · systemd-test.sh (CI) · cross-sysroot.sh (cross-builds) ·
                bake-duck-mesh.py (the monitor's 3D model, run by hand)
docs/           robot/ (using one) · design/ (how it works) · project/ (roadmap, records) ·
                ideas/ (not designed yet)
```

Services talk over unix sockets, JSON-RPC 2.0 one object per line. The contract lives in
`duck-ipc-proto`, which depends on serde and semver and nothing else — so `btd` and `robotd`
never inherit the update engine's http/tar/crypto tree.

[`docs/design/architecture.md`](docs/design/architecture.md) §1 has what each service is and why it is its own
process. [`docs/project/roadmap.md`](docs/project/roadmap.md) has what actually works today.

## Conventions

- **Comments say why, not what.** The reason a thing is the way it is outlives the code.
- **Every non-obvious decision gets a test**, and the test's comment says which failure it
  exists to prevent. The rollback paths especially: they only ever run when something else has
  already gone wrong, so they are the code most likely to be quietly broken.
- **Reach for an existing crate** before writing it yourself. Dependency count is not the thing
  being optimised; maintenance is.
- Commit trailers use `Assisted-by:`, not `Co-Authored-By:`, for AI assistance.

## Media in the README

The videos and the hero image are **GitHub attachments, not files in this repo**: drop a clip into
the comment box of any issue or pull request and GitHub hands back a
`https://github.com/user-attachments/assets/<id>` URL. Nothing to commit, nothing to keep in sync —
and nothing in a clone either, so those tiles are blank without a network.

Inside the README's `<table>` the URL has to go in an element, because markdown is not parsed in
block HTML and a bare URL there stays text:

```html
<video src="https://github.com/user-attachments/assets/<id>" controls width="100%"></video>
```

**A video cannot autoplay or loop.** Verified against the renderer itself
(`POST https://api.github.com/markdown`): of `src autoplay muted loop controls playsinline preload
poster width`, only `src`, `muted`, `controls` and `width` survive the sanitiser. So a video waits
for a click, and the only media that moves on its own is an animated image — a GIF, or an animated
WebP at a fraction of the size:

```bash
ffmpeg -i clip.mp4 -vf "fps=15,scale=560:-1:flags=lanczos" -loop 0 -q:v 55 walk.webp
```

Two or three seconds, treated as a moving thumbnail. Use a video where sound or length matters.

## Releasing

Releases are signed **in CI**, never locally. The entry point is the GitHub releases page, and the
tag decides what happens:

| you create | what CI does |
|---|---|
| a **pre-release** tagged `daemon-staging-v0.4.0` | builds, signs, verifies through the real update engine, publishes to **staging** |
| a **release** tagged `daemon-v0.4.0` | **promotes** staging 0.4.0 if it exists — the same bytes, re-signed — otherwise builds 0.4.0 directly |

Pushing either tag from a terminal does the same thing:

```bash
git tag daemon-staging-v0.4.0 && git push --tags
```

The canaried path is two steps on purpose: publish the pre-release, install it on a robot, then
create the release. Creating a release with no staging build to promote is allowed and says so in its
own notes — verified in CI, never run on a robot.

Bump the workspace version first. `xtask package` refuses a tag that disagrees with `Cargo.toml`,
which is what stops a robot reporting a version it is not running.

`gh workflow run promote --field version=0.4.0` is the same promotion without a release to create
first, and is where `min_supported` lives.

[`docs/project/ci-setup.md`](docs/project/ci-setup.md) covers key custody, the secrets, and rotation.

```

### File: `Cargo.toml` (110 lines, ~1571 tokens)
```toml
# Workspace root for the robot daemon.
#
# One crate per service or tool, matching the service split in
# docs/design/architecture.md §1. `robotd`, `btd` and `mediad` are all siblings now.
[workspace]
resolver = "3"
members = ["btd", "configd", "duck-ble", "duck-control", "duck-detect", "duck-ether", "duck-ipc-proto", "duckctl", "kinematics", "mediad", "odometry", "pad-imu", "padd", "pet-detect", "sounds", "tof", "updater", "robotctl", "robotd", "robotd-params", "test-support", "uyvy", "xtask"]

# Everything except `duckctl`, and that exception is the whole reason this key exists.
#
# `cargo board --bins` — in `dev-push.sh` and in the release workflow — builds every default
# member for aarch64, which is right for a robot's daemons and wrong for the client a developer
# runs on their own machine: it would cross-compile a Bluetooth stack for a board that must never
# see one, on the release path, for nothing.
#
# The alternative was naming the binaries explicitly at each `--bins` call site. There are two of
# them and they would have to be kept in step by hand, which is the failure this repo keeps
# writing down. One list here, and a new daemon is picked up by both without anybody remembering.
#
# `--workspace` is unaffected, so CI still lints and tests `duckctl` exactly as before.
default-members = ["btd", "configd", "duck-ble", "duck-ble", "duck-control", "duck-detect", "duck-ipc-proto", "kinematics", "mediad", "odometry", "pad-imu", "padd", "pet-detect", "sounds", "tof", "updater", "robotctl", "robotd", "robotd-params", "test-support", "uyvy", "xtask"]

# ONNX Runtime, which robotd dlopens to run a policy. One source of truth: `xtask package`
# bakes these into the release's preinstall hook, and a test asserts scripts/setup-board.sh
# agrees with them. Two copies drifting apart is exactly how a board ended up with 1.20.1
# against an `ort` that panics below 1.23.
#
# `floor` is the minimum `ort` accepts — raise it in step with the `ort` dependency.
# `target` is what we install when a board is below the floor.
[workspace.metadata.onnxruntime]
floor  = "1.23"
target = "1.28.0"

# Rockchip's NPU runtime, which `duck-detect` dlopens to run the duck detector. Same shape as the
# ONNX Runtime pin above and for the same reason — `scripts/setup-npu.sh` is fetched standalone with
# curl and cannot read this file, so it carries a literal and a test asserts the two agree.
#
# The version is a tag in Rockchip's `rknn-toolkit2` repository, which is where the .so lives; it has
# to be at least as new as the model the converter produces, because a runtime older than its model
# fails at `rknn_init` with a number.
[workspace.metadata.rknpu]
runtime = "v2.3.2"

# The official policy set, which `robotd` runs and which lives on the Hugging Face Hub rather
# than in this repository — a gait retrain should not need a daemon release, and a daemon fix
# should not re-ship six megabytes of unchanged weights.
#
# Same shape as the three pins above and for the same reason: `scripts/seed-policies.sh` runs from
# inside a release and cannot read this file, so it carries the literals and a test asserts the
# two agree.
#
# `version` is a tag in the Hub repo, and it is a *minimum*: what a freshly provisioned board
# installs, and the oldest official set this daemon's defaults load — a board below it is moved
# up to it by the post-install hook, one past it is left alone. Moving past it is `robotctl
# policy update`, which needs no daemon release — bumping this does, since it ships inside one,
# and it is bumped when a slot's default names a file only the new set carries.
[workspace.metadata.policies]
repo    = "pollen-robotics/microduck-policies"
version = "v5"

# The duck detector, the same way: trained in pollen-robotics/duck_detector, published on the Hub,
# and seeded onto a board by `scripts/seed-detector.sh` from this pin — a floor, moved past with
# `robotctl duck-detector update`. The model repo shares its name with the *dataset* repo; the robot only
# ever addresses the model (`huggingface.co/<repo>/resolve/…`, `api/models/<repo>`), and the
# dataset lives under `datasets/`, so the shared name cannot be confused on the wire.
[workspace.metadata.detector]
repo    = "pollen-robotics/microduck-duck-detector"
version = "duck-v1"

# The prebuilt GStreamer plugins `mediad` needs, built in CI from pinned upstream sources at
# https://github.com/pollen-robotics/microduck-gst-plugins — `mpph264enc` (hardware H.264 through
# Rockchip MPP) and `webrtcsink`/`webrtcsrc`, neither of which exists in any Debian suite.
#
# One source of truth, for the same reason `[workspace.metadata.onnxruntime]` above is one:
# `scripts/setup-gstreamer.sh` is fetched standalone with curl and cannot read this file, so it
# carries a literal, and a test asserts the two agree. Two copies of a version drifting apart is
# how a board ended up with an ONNX Runtime its `ort` panics on.
[workspace.metadata.gst-plugins]
repo    = "pollen-robotics/microduck-gst-plugins"
version = "v3"

[workspace.package]
version = "0.15.0"
edition = "2024"
# 1.89 for `std::fs::File::try_lock`, which is how the single-flight update lock works
# without a dependency (updater/src/journal.rs). Edition 2024 needs 1.85, so this covers
# both. Declared so a teammate on an older toolchain gets "requires rustc 1.89" instead of
# an error about a method that does not exist.
rust-version = "1.89"
license = "Apache-2.0"

[workspace.dependencies]
serde = { version = "1", features = ["derive"] }
serde_json = "1"
semver = { version = "1", features = ["serde"] }
thiserror = "2"
tokio = "1"
clap = { version = "4", features = ["derive"] }
hound = "3.5"
tracing = "0.1"
tracing-subscriber = "0.3"
tokio-util = "0.7"
async-trait = "0.1"
url = "2"

# No custom [profile.release]. Binary size is not worth optimising for: model artifacts
# will dwarf a few MB of binary, and the tuning cost more than it bought —
# `strip = true` in particular removes the symbol table, turning a panic backtrace in
# journald into bare addresses, which is exactly what you need when diagnosing a robot
# you cannot attach a debugger to. `lto`/`codegen-units` only lengthened builds.

```

### File: `LICENSE` (201 lines, ~2889 tokens)
```text
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright [yyyy] [name of copyright owner]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

```

### File: `README.md` (106 lines, ~1304 tokens)
```md
<p align="center">
  <img src="https://github.com/user-attachments/assets/c2f7c245-8217-46a1-8d1e-e0ba967cd969" alt="microduck" width="820">
</p>

<h1 align="center">Microduck</h1>

<p align="center">
  <em>A tiny biped robot that moves using reinforcement learning policies.</em>
</p>

<p align="center">
  <a href="https://pollen-robotics.com/microduck"><b>Get yours here</b></a> ·
  <a href="docs/robot/cheatsheet.md">Cheat sheet</a> ·
  <a href="https://github.com/pollen-robotics/microduck_rl">Training the policies</a> ·
  <a href="docs/design/architecture.md">How it works</a> ·
  <a href="CONTRIBUTING.md">Contributing</a>
</p>

<p align="center">
  <a href="https://github.com/pollen-robotics/microduck/actions/workflows/ci.yml"><img src="https://github.com/pollen-robotics/microduck/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
</p>

---

**This repo is the duck's brain.** About 25 cm and 800 g of robot, run by a handful of daemons on a
Rockchip RK3566: a 50 Hz control loop driving fifteen servos from neural policies, the radios and
the camera, and the update machinery that gets new software onto a robot without bricking it.

Everything you need to run a Microduck is here. **If you want one,
[get yours here](https://pollen-robotics.com/microduck).**

The policies it runs are trained next door, in
**[microduck_rl](https://github.com/pollen-robotics/microduck_rl)** — MuJoCo and PPO, the sim2real
recipe, and the export to ONNX that this repo loads.

## It does things

<table>
<tr>
<td width="50%">
  <video src="https://github.com/user-attachments/assets/356a6011-8e0d-4b28-bda9-da78646583a3" controls width="100%"></video>
</td>
<td width="50%">
  <video src="https://github.com/user-attachments/assets/abfbf250-1b1c-42cb-8430-00267e2b148a" controls width="100%"></video>

</td>
</tr>
<tr>
<td><b>It walks.</b> Pick up a gamepad and drive.</td>
<td><b>It rolls.</b> Put wheels on, hold D-pad up, and it loads the other brain.</td>
</tr>
<tr>
<td width="50%">
  <video src="https://github.com/user-attachments/assets/7e70c1da-e120-428f-ae0b-f4de62f25984" controls width="100%"></video>
</td>
<td width="50%">
  <video src="https://github.com/user-attachments/assets/3eef63a5-6f84-47cf-90de-e717e6d7f8f0" controls width="100%"></video>
</td>
</tr>
<tr>
<td><b>It picks things up.</b> Beak to the floor, one button.</td>
<td><b>It gets back up.</b> Knock it over and it stands itself up.</td>
</tr>
</table>

It also sits, kicks a ball, rolls forward on command, and quacks in a voice that is its own.

## Where to find things

### You have a duck

| | |
|---|---|
| [Cheat sheet](docs/robot/cheatsheet.md) | Every `robotctl` command: drive, configure, voice, chorale, theremin, wifi, updates, logs. Start here. |
| [Gamepad](docs/robot/cheatsheet.md#gamepad-configd) | The full button mapping, and pairing a pad — [once per pad](docs/robot/pair-a-gamepad.md), plus what to do when it will not bond. |
| [`duckctl`](docs/robot/duckctl.md) | The robot from a laptop over Bluetooth, with no network and no ssh. |
| [Updates](docs/robot/cheatsheet.md#updates-updaterd) | Install, roll back, pin. Every update is verified, health-gated and reversible. |

### You are building on it

| | |
|---|---|
| [microduck_rl](https://github.com/pollen-robotics/microduck_rl) | Where the policies come from: MuJoCo, PPO, domain randomisation, and the ONNX export this repo loads. |
| [How it works](docs/design/architecture.md) | The whole system on one page — the daemons, the bus, how an update reaches a robot — then a page per part. |
| [Set up a dev board](docs/robot/install-dev.md) | From a blank board to a robot that takes branch builds. |
| [Dev cheat sheet](docs/robot/cheatsheet-dev.md) | Branch builds, release candidates, driving from a laptop, and the restart traps after an update. |
| [Push your branch](docs/robot/dev-push.md) | Build on your machine, install over ssh, about a minute. |
| [The simulated duck](docs/robot/simulation.md) | No robot on the desk? `scripts/duck-sim` runs the real daemons against a body in MuJoCo — one duck in a window, or four as machines you log into. |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Building, testing, layout, conventions, releasing. |
| [Docs index](docs/README.md) | Everything, including the design pages and the open problems. |

## Under the hood

Rust, no framework, one workspace. `robotd` owns the control loop and the motor bus; `updaterd`
installs signed releases and rolls them back when a robot comes up unhealthy; `configd` owns wifi
and identity; `btd` is the Bluetooth path a phone uses; `padd` reads the gamepad; `mediad` streams
the camera over WebRTC; `tofd` serves the depth sensor. They talk over one JSON-RPC contract on
Unix sockets, and every client — the app, the console, the gamepad, your script — sends exactly the
same calls.

The interesting decisions are written down: [`docs/design/`](docs/design/) is why things are the
way they are, and [`docs/project/`](docs/project/) is what has gone wrong and what would close it.

## A note on ducks

No duck was harmed in the making of this robot. Several were consulted.

```

### File: `btd/Cargo.toml` (56 lines, ~771 tokens)
```toml
[package]
name = "btd"
version.workspace = true
edition.workspace = true
license.workspace = true
description = "BLE transport adapter — a GATT front door onto the robot's JSON-RPC API"

# A transport adapter and nothing else (architecture.md §4.1): `btd` owns no state. Every
# request it accepts is forwarded verbatim to the service that owns the answer, over that
# service's unix socket. So it depends on the method table and on nothing that implements
# behaviour — no update engine, no control loop, no NetworkManager client.
#
# It is also the process that parses bytes arriving from anyone in radio range, which is why it
# stays unprivileged while `configd` is the one running as root.
[dependencies]
duck-ipc-proto = { path = "../duck-ipc-proto" }
# The wire contract, shared with every client rather than exported to them.
# It used to live here, which made a phone app depend on a daemon to agree
# about chunking — see that crate's manifest.
duck-ble = { path = "../duck-ble" }
serde_json.workspace = true
tokio = { workspace = true, features = ["rt-multi-thread", "macros", "net", "io-util", "time", "sync", "signal"] }
clap.workspace = true
tracing.workspace = true
tracing-subscriber = { workspace = true, features = ["env-filter"] }

# BlueZ, reached over bluetoothd's D-Bus API. Only on Linux, and this only ever *runs* on the
# Radxa — but the crate must still *build* on a macOS laptop, because `cargo test` there is the
# whole onboarding path for a teammate (roadmap, "Organisation"). Those are different claims and
# only the first is true, so the radio sits behind `cfg(target_os = "linux")` while the session
# logic is driven by channels and needs no radio to test.
#
# Pinned rather than floated: bluer is 0.x and breaks across minor versions, and its GATT-server
# API is the part most likely to move.
#
# `dbus/vendored` builds libdbus from source with `cc` instead of linking the target's copy.
# That is what makes this cross-compile: `cargo board` uses cargo-zigbuild, and `zig cc`
# supplies a cross C compiler — the same mechanism that already builds `zstd-sys` — but the
# sysroot has libc, not libdbus. Verified: a full aarch64 release build links clean.
#
# The cost of vendoring is that this libdbus is ours to keep current rather than the distro's.
# Acceptable for a library reached only over a local socket by a daemon we wrote, but it is a
# thing to remember exists.
[target.'cfg(target_os = "linux")'.dependencies]
bluer = { version = "=0.17.4", features = ["bluetoothd"] }
dbus = { version = "0.9", features = ["vendored"] }
futures = "0.3"

[dev-dependencies]
# `every_call()`, shared rather than copied — see `src/route.rs`'s test module.
duck-ipc-proto = { path = "../duck-ipc-proto", features = ["test-support"] }
tempfile = "3.27.0"

# No examples here any more. The laptop-side client and the advertisement watcher both needed
# `btleplug`, and both moved to `duckctl/` — see its manifest for what that bought and for how
# the "never on the robot" guarantee survived the move.

```

### File: `btd/src/bluez.rs` (1004 lines, ~13964 tokens)
```rs
//! The radio. BlueZ via `bluetoothd`'s D-Bus API, Linux only.
//!
//! Everything here is plumbing between BlueZ and [`crate::session`]'s two channels. No decision
//! about the robot is taken in this file, which is the point: the logic that could be wrong is
//! the logic that is tested, and this is the part that needs a radio.
//!
//! It uses `bluer`'s **callback model**, and the alternative was tried on hardware and does not
//! work. `bluer`'s IO model answers BlueZ's `WriteValue` and `StartNotify` with `NotSupported` —
//! it serves only the `AcquireWrite`/`AcquireNotify` fd paths — and a CoreBluetooth central drove
//! the ordinary methods. The result was a robot that advertised, accepted a connection, accepted a
//! subscription, accepted a write, and delivered none of it to this file: no `central connected`
//! line, no pairing prompt, and a client timing out against a service that was working.
//!
//! The IO model was chosen for a benefit that turns out not to exist. It reports
//! `device_address()` on both halves, which looked necessary for pairing a subscription to the
//! session that should feed it — but `bluer` holds **one** `CharacteristicNotifyState` per
//! characteristic, so there is only ever one notification session to pair with. One central at a
//! time is a property of the stack, not a shortcut taken here.
//!
//! So: one session for the service's lifetime, one notify pump, and a write callback that pushes
//! bytes into it.
//!
//! **What the callback model costs is flow control**, and that bill came due the first time a
//! reply was more than a few kilobytes. `notify` hands a D-Bus signal to the connection and
//! returns; nothing here can ask BlueZ whether the radio has caught up, and nothing reports the
//! notification MTU either. Both gaps are worked around rather than solved: the payload is taken
//! from what BlueZ reports on inbound writes (one ATT MTU serves both directions, capped at the
//! 512-byte limit on a characteristic value — see `framing::notification_payload`), and the pump
//! pauses every [`NOTIFY_BURST`] chunks. The IO model has the readiness signal this wants and
//! still cannot be used, for the reason above — it serves only the `Acquire*` paths.

use std::net::Ipv4Addr;
use std::sync::Arc;
use std::time::Duration;

use bluer::adv::{Advertisement, Type};
use bluer::agent::Agent;
// Aliased: `bluer` has two error types called `ReqError`, one for the pairing agent and one for a
// characteristic. Naming this one makes a mix-up a name error rather than a puzzling type error,
// which is how it first presented.
use bluer::gatt::local::ReqError as GattError;
use bluer::gatt::local::{
    Application, Characteristic, CharacteristicNotifier, CharacteristicNotify,
    CharacteristicNotifyMethod, CharacteristicRead, CharacteristicWrite, CharacteristicWriteMethod,
    Service,
};
use futures::FutureExt;
use std::sync::Mutex as StdMutex;
use std::sync::atomic::{AtomicUsize, Ordering};

use tokio::sync::mpsc;

use crate::link::Link;
use crate::session;
use crate::upstream::{NameChoice, Sockets};
use duck_ble::framing::{FLOOR_MTU, notification_payload};
use duck_ble::gatt::{RPC_UUID, SERVICE_UUID};

/// How many notifications to queue before pausing to let the radio drain.
///
/// **This is the only backpressure the callback model offers, and it has to exist.**
/// `CharacteristicNotifier::notify` emits a D-Bus `PropertiesChanged` signal and returns as soon
/// as the signal is queued on the connection — it does not wait for BlueZ, let alone for the
/// controller — so an unpaced pump queues a whole reply in microseconds. Measured on the board:
/// a ~5 KiB reply at the 20-byte floor (≈265 notifications) got through in 1.8 s, and a ~7 KiB one
/// (≈350) killed the notification session 150 ms in, leaving the client waiting out its idle
/// timeout against a robot that had already torn down the session. `bluer`'s IO model has a real
/// readiness signal for this and cannot be used here — it serves only the `Acquire*` fd paths,
/// which a CoreBluetooth central never drives (see this module's header).
///
/// Sixteen chunks is what a connection interval can plausibly carry, so a small reply — an
/// authentication answer is four chunks — never pauses at all.
const NOTIFY_BURST: usize = 16;

/// How long to pause between bursts. Roughly one connection interval.
const NOTIFY_PAUSE: Duration = Duration::from_millis(20);

/// How many times to re-send a chunk the D-Bus connection would not take, and how long to wait
/// between attempts.
///
/// A `notify` that fails while the session is *not* stopped is a queue that is momentarily full,
/// which is recoverable and was being treated as the central having left — the session was torn
/// down mid-reply and the client learned nothing at all. Only an exhausted budget, or a genuinely
/// stopped session, ends the session now.
const NOTIFY_RETRIES: u32 = 5;
const NOTIFY_RETRY_BACKOFF: Duration = Duration::from_millis(20);

/// How often to advertise, and this is the difference between a robot that is found and one that is
/// not.
///
/// Left unset, BlueZ takes the kernel's default of **1.28 s**, and that was measured against this
/// board from a Mac scanning continuously for two minutes: the robot arrived once every 7.5 s on
/// average with silences of 9 s, 14 s, 17 s and once 31 s. Every other radio in the room — a smart
/// plug at −66 dBm, a beacon at −91 dBm — arrived 130 to 212 times over the same window, against the
/// robot's 16, while the robot was the *strongest* signal there at −36 dBm. So it was not range,
/// not interference and not the client: it simply spoke too rarely to be caught.
///
/// A central scans at a low duty cycle, which is what turns "6× slower" into "absent for seconds at
/// a time" — an eight-second scan that lands in one of those silences finds nothing, and roughly
/// half of them did. The large gaps came out as near-integer multiples of 1.28 s, which is what
/// identified the interval from the arrivals rather than from a guess.
///
/// 100-150 ms is the range ordinary peripherals use, and it is 8-12× the default. Not the 20 ms
/// floor the spec allows: one antenna carries this, a gamepad's LE link and wifi, so airtime spent
/// shouting is taken from the things the robot is for. A *range* rather than one value because a
/// fixed interval can keep colliding with the same neighbour's, which the controller avoids by
/// jittering inside the window.
///
/// Measured again with this installed, same Mac and same two minutes: **151 arrivals, one every
/// 0.8 s, worst silence 3.8 s, and not one silence of 8 s or more.** The failure it was diagnosed
/// from cannot happen at that spacing, which is the point — the margin against an eight-second scan
/// is now a factor of two rather than a coin toss.
const ADV_INTERVAL_MIN: Duration = Duration::from_millis(100);
const ADV_INTERVAL_MAX: Duration = Duration::from_millis(150);

/// A task that does not outlive the bring-up that started it.
///
/// The advertisement, the GATT application and the agent all deregister on drop, and the chorale's
/// radio task has to follow the same rule — a task left running against an adapter that is gone
/// would reconnect to `robotd` forever and advertise on nothing.
struct AbortOnDrop(tokio::task::JoinHandle<()>);

impl Drop for AbortOnDrop {
    fn drop(&mut self) {
        self.0.abort();
    }
}

/// How long to wait between attempts to find a usable adapter.
///
/// Measured on the board: `hci0` does not exist until roughly 73 seconds after power-on —
/// `aic-bluetooth.service` attaches the AIC8800's UART late, and `bluetooth.service` itself
/// spends 26s blocked behind `dbus`. A daemon that exited on "no adapter" would be restarted by
/// systemd into the same emptiness for over a minute, so it waits. Same lesson as `robotd`
/// waiting for the motor bus rather than giving up on it.
const ADAPTER_RETRY: Duration = Duration::from_secs(5);

/// How long to wait for `configd` to say what the robot is called, or what address it has.
///
/// Nothing is blocked on the answer — unlike the PIN, where BlueZ holds a pairing exchange open —
/// so this is generous enough to survive a loaded board rather than tuned for a spinner.
///
/// It bounds [`ask_address`] as much as [`ask_name`], and that matters more there: `net.status`
/// costs `configd` a handful of D-Bus round trips to NetworkManager, and NetworkManager mid-scan is
/// slow. A late answer costs one poll's worth of a stale address, which is what the fallback in
/// those two functions is for.
const ASK_TIMEOUT: Duration = Duration::from_secs(5);

/// How often the advertisement is reconciled with what `configd` says — the name, and the address.
///
/// **Polled rather than event-driven, deliberately.** `btd` forwards `system.setName` to `configd`
/// without reading the reply (`upstream::Pool` merges lines for the client, and interpreting them
/// here is exactly what this daemon avoids), so it does not learn a rename by watching. It could
/// re-ask the moment it forwards one, but the write it just forwarded may not have been applied
/// yet, and a second connection has no ordering guarantee against the first.
///
/// Reconciling instead is fewer moving parts and covers every rename path, including
/// `robotctl system set-name` over the unix socket, which never crosses this process at all. The
/// cost is a socket connect and one line every few seconds, forever, which is far below the noise
/// floor of a daemon that already waits 73 seconds for a radio. A `system.*` notification from
/// `configd` would be the tidier answer and is a protocol change nobody needs yet.
///
/// **The address is asked on the same tick, at the same cadence**, which is faster than a DHCP
/// lease could ever move. Two questions rather than one is a second socket connect and a `net.status`
/// that `configd` answers out of NetworkManager, and splitting the cadences would buy back some of
/// that at the price of a second timer and an address that lags a `wifi connect` by half a minute.
/// The robot has just been given a network at that moment, and the address is the thing whoever did
/// it is waiting to read.
const ADV_POLL: Duration = Duration::from_secs(5);

/// How often the reconcile loop reads the session slot, which is faster than it asks `configd`.
///
/// The two questions have nothing in common but the loop that asks them. A name or an address
/// costs a socket connect and a round trip to another daemon, and neither moves quickly enough to
/// be worth asking about more often than [`ADV_POLL`]. Whether a central is being served is a
/// mutex in this process, free to read — and it is the one that should be acted on promptly: it
/// decides whether the robot is taking connections, so a tick spent not noticing that a client has
/// left is a tick in which nobody else can get in.
///
/// A second, faster timer rather than simply lowering [`ADV_POLL`], because lowering that one
/// would multiply the traffic to `configd` by five to buy nothing it answers.
const SESSION_POLL: Duration = Duration::from_secs(1);

/// The live session's inbound sender, or `None` when no central is subscribed.
///
/// Named because two places now read it for different reasons: the write callback, which needs
/// somewhere to put a chunk, and [`reconcile_advertisement`], which needs to know whether the robot
/// is busy. The second is not a new signal — it is the same slot, asked a different question.
type SessionSlot = Arc<StdMutex<Option<mpsc::Sender<Vec<u8>>>>>;

/// Whether a central is being served right now.
///
/// Nothing is held across an await: the lock is taken and released inside this call, because the
/// callers that matter are a callback that may not block and a loop that must not stall the radio.
fn serving(session: &SessionSlot) -> bool {
    session.lock().expect("write slot poisoned").is_some()
}

/// Serve BLE for as long as this process lives, across an adapter that comes and goes.
///
/// Waiting for an adapter to *appear* was never enough. Everything after that wait — powering the
/// adapter, registering the agent, advertising, publishing the GATT application — used to propagate
/// its error out of this function and exit the process, so an adapter that appeared and then
/// misbehaved took `btd` down where an adapter that never appeared did not. On a robot with no
/// network that is the difference between "wifi is unavailable" and "unreachable".
///
/// So the whole bring-up retries in place, on the same 5s cadence as the wait it already did:
///
/// - **radio faults never leave this function.** A `failed` `btd` therefore means a broken binary,
///   which is what admits it to the boot recovery net — see `docs/design/boot-recovery-net.md`;
/// - **and it self-heals.** Exiting non-zero got the same retry from `Restart=always`, but only by
///   spending a process death on it, and only until the day the unit gains a start limit.
///
/// `require_pairing` controls whether writing a request needs an authenticated, encrypted link.
/// It defaults on, because §7 requires it for anything carrying wifi credentials and
/// `net.connect` now does. The opt-out exists for bench work against a client that cannot pair.
pub async fn serve(sockets: Sockets, name: NameChoice, require_pairing: bool) -> bluer::Result<()> {
    loop {
        match serve_on_an_adapter(&sockets, &name, require_pairing).await {
            Ok(()) => tracing::warn!(
                retry_in = ?ADAPTER_RETRY,
                "the adapter is gone; waiting for it to come back"
            ),
            // Not fatal, deliberately: every failure reachable here is a property of the radio or
            // of BlueZ, and none of them is fixed by dying. See this function's own doc comment.
            Err(e) => tracing::warn!(
                error = %e,
                retry_in = ?ADAPTER_RETRY,
                "BLE bring-up failed"
            ),
        }
        tokio::time::sleep(ADAPTER_RETRY).await;
    }
}

/// One bring-up: acquire an adapter, advertise, serve, and return when the adapter goes away.
///
/// The advertisement, GATT application and agent handles all deregister on drop, so returning here
/// is what releases them before the next attempt registers its own.
async fn serve_on_an_adapter(
    sockets: &Sockets,
    name: &NameChoice,
    require_pairing: bool,
) -> bluer::Result<()> {
    let sockets = sockets.clone();
    let name = name.clone();
    let bt = bluer::Session::new().await?;

    // Kept as its own loop rather than folded into the caller's: "no adapter yet" is the ordinary
    // state of a board for its first 73 seconds and reads as progress, while a failure after this
    // point is a fault. Collapsing them would log a fault every 5s during a normal boot.
    let adapter = loop {
        match bt.default_adapter().await {
            Ok(adapter) => break adapter,
            Err(e) => {
                tracing::warn!(error = %e, retry_in = ?ADAPTER_RETRY, "no Bluetooth adapter yet");
                tokio::time::sleep(ADAPTER_RETRY).await;
            }
        }
    };
    adapter.set_powered(true).await?;

    // Pairable only matters while we advertise, and the board reports `Pairable: no` by default.
    // Left open rather than gated behind a window: the PIN carries what a window would add, as
    // long as it is per-robot. See `crate::pairing` for why that was chosen over a button.
    if require_pairing {
        adapter.set_pairable(true).await?;
    }

    // A **just-works** agent: every handler left `None`, which bluer publishes as
    // `NoInputNoOutput`. So the bond needs no interaction and is encrypted but *not*
    // authenticated.
    //
    // This is not the design that was intended. The first version answered BlueZ's passkey request
    // with the stored PIN, which cannot work on a headless robot: in LE passkey entry the roles
    // follow from the declared IO capabilities, so implementing `request_passkey` told macOS "this
    // device can input", and macOS displayed a random code for someone to type into a robot with no
    // keyboard. The reverse is no better — with `DisplayPasskey` the *spec* has BlueZ generate the
    // passkey, so a PIN printed on a sticker cannot be presented at all.
    //
    // The PIN check therefore moved above the link layer: `crate::session` serves nothing until a
    // client passes `system.authenticate`. See `crate::pairing` for the trade that involves.
    let _agent = if require_pairing {
        Some(
            bt.register_agent(Agent {
                request_default: true,
                ..Default::default()
            })
            .await?,
        )
    } else {
        tracing::warn!(
            "pairing NOT required: any device in range can reach the RPC characteristic. The PIN \
             is still enforced by the session. Bench use only."
        );
        None
    };

    // `bd_addr` rather than `address`, because the advertisement now carries an IPv4 one too and a
    // journal with both spelled `address` reads as one field contradicting itself.
    //
    // `max_adv_len` is logged because it is the budget `duck_ble::adv` is written against: the payload
    // fits 31 bytes, and a controller that reports less is the one place that assumption fails. It
    // is the first thing to read if a robot ever advertises its name but no address.
    tracing::warn!(
        adapter = adapter.name(),
        bd_addr = %adapter.address().await?,
        service = %SERVICE_UUID,
        pairing = require_pairing,
        max_adv_len = adapter
            .supported_advertising_capabilities()
            .await
            .ok()
            .flatten()
            .map(|caps| caps.max_advertisement_length),
        "serving BLE"
    );

    // The advertised name is what someone sees in a phone's Bluetooth list, so it is the robot's
    // name rather than the service's — and `configd` owns it. Until this asked, the advertisement
    // carried `/etc/hostname` while `system.setName` wrote a name nothing ever read: every board
    // flashed from one image appeared as `radxa-zero3`, and renaming one changed nothing a phone
    // could see, not even after a restart.
    let advertised = Advertised {
        name: match &name.pinned {
            Some(pinned) => pinned.clone(),
            None => ask_name(&sockets, &name.fallback).await,
        },
        // Asked before the first advertisement rather than left to the first reconcile tick: a
        // robot that boots onto a network it already knows would otherwise broadcast `0.0.0.0` for
        // the first few seconds, and a listing cannot tell that from a robot with no wifi at all.
        address: ask_address(&sockets, None).await,
        // Nothing has been served yet: the GATT application below is not even registered.
        connectable: true,
    };
    let handle = Some(advertise(&adapter, &advertised).await?);

    // The chorale's radio, on its own connection to `robotd` and its own advertising instance. A
    // task rather than part of the session loop: it is not serving a client, and it must not be
    // able to hold up the one thing this daemon exists for. Its failures are its own — a `robotd`
    // that is not up yet is the ordinary case at boot.
    let chorale = {
        let adapter = adapter.clone();
        let robot_socket = sockets.robot.clone();
        tokio::spawn(async move {
            loop {
                if let Err(e) = crate::chorale::run(&adapter, &robot_socket).await {
                    tracing::debug!(error = %e, "chorale: robotd is not answering");
                }
                tokio::time::sleep(ADAPTER_RETRY).await;
            }
        })
    };
    // Aborted when this bring-up ends, so a new adapter gets a new connection rather than one
    // pointing at a radio that has gone.
    let _chorale = AbortOnDrop(chorale);

    // **One session per subscription**, not one per daemon.
    //
    // The first version kept a single session alive for the whole service, which is simpler and
    // wrong: a client that vanishes mid-request leaves a partial line in the reassembler and
    // undelivered chunks in the outbound queue, and the *next* client is handed them. That
    // presented as a reply arriving without its beginning —
    // `":0,"result":{"authenticated":true}}` — which is the tail of a previous run's answer.
    //
    // Created when a central subscribes, torn down when it goes away. Subscribing first is the
    // order every client uses, and a write with no live subscription is refused: there would be
    // nowhere to send the answer.
    //
    // A `std::sync::Mutex` rather than tokio's, deliberately: the write callback must read this
    // without awaiting, because a yield point there lets two chunks swap places. Nothing is held
    // across an await.
    let current: SessionSlot = Arc::new(StdMutex::new(None));
    let for_write = current.clone();
    let for_notify = current.clone();

    // The negotiated payload, written by the write callback and read by the session when it sizes
    // a reply. An atomic rather than a channel or the mutex above, because the write callback may
    // not await and may not block: a yield point there lets two chunks swap places. See
    // [`crate::link::Link::mtu`].
    let mtu = Arc::new(AtomicUsize::new(FLOOR_MTU));
    let write_mtu = mtu.clone();

    // The notify callback below takes ownership of `sockets` for the sessions it spawns, and the
    // reconcile loop at the end outlives it.
    let for_reconcile = sockets.clone();

    let app = Application {
        services: vec![Service {
            uuid: SERVICE_UUID,
            primary: true,
            characteristics: vec![Characteristic {
                uuid: RPC_UUID,
                // A read whose only job is to force a bond before anything is written.
                //
                // §7 requires the characteristic carrying wifi credentials to be paired and
                // encrypted. A read is acknowledged, so an unpaired central gets "insufficient
                // authentication" and starts pairing there and then, which a subscribe cannot do:
                // `CharacteristicNotify` carries no encryption flags at all.
                //
                // NOTE: this is currently the *unencrypted* path in practice — see
                // `docs/design/app-path-design.md` §5.5. Requiring encryption here hangs CoreBluetooth.
                //
                // The value matters less than the fact that reading it needs a bond; the API
                // version is the most useful byte available, and a client that finds a version it
                // does not know can say so before writing anything.
                read: Some(CharacteristicRead {
                    read: true,
                    encrypt_read: require_pairing,
                    fun: Box::new(|req| {
                        // Logged because this read is the pairing trigger, so "did the central get
                        // this far" is the first question when a client hangs.
                        tracing::debug!(peer = %req.device_address, "version read");
                        async move { Ok(vec![duck_ipc_proto::API_VERSION as u8]) }.boxed()
                    }),
                    ..Default::default()
                }),
                write: Some(CharacteristicWrite {
                    write: true,
                    // Write-without-response as well: a chunked request needs no ATT
                    // acknowledgement per chunk. A client that wants a *refusal* to be visible
                    // must use the acknowledged form, which is why `duckctl` does.
                    write_without_response: true,
                    encrypt_write: require_pairing,
                    // No `.await` between receiving a chunk and enqueueing it. BlueZ dispatches
                    // each `WriteValue` as its own task, so a yield point here lets two chunks swap
                    // places — and a reordered chunk corrupts a request silently rather than
                    // failing it. `main` also pins the runtime to one thread for the same reason.
                    method: CharacteristicWriteMethod::Fun(Box::new(move |value, req| {
                        let bytes = value.len();
                        let head =
                            String::from_utf8_lossy(&value[..value.len().min(8)]).to_string();
                        let sender = for_write.lock().expect("write slot poisoned").clone();

                        // What BlueZ says this link negotiated, minus the three bytes of ATT
                        // header a notification cannot use. Stored on every write because it is
                        // free to do so and a central may renegotiate; logged only when it moves,
                        // because the value that matters is the one a reply gets chunked for and
                        // that number had never appeared in the journal at all.
                        let payload = notification_payload(req.mtu);
                        let previous = write_mtu.swap(payload, Ordering::Relaxed);
                        let learned = (previous != payload).then_some(payload);

                        let result = match sender {
                            None => {
                                // Nowhere to send an answer, so accepting the request would be a
                                // lie. Clients subscribe first; this is a client that did not.
                                tracing::warn!(
                                    peer = %req.device_address,
                                    "write with no subscription; refusing"
                                );
                                Err(GattError::Failed)
                            }
                            Some(tx) => match tx.try_send(value) {
                                Ok(()) => Ok(()),
                                Err(mpsc::error::TrySendError::Full(_)) => {
                                    // Refusing is recoverable — the client resends. Dropping the
                                    // chunk is not: the line would reassemble into something that
                                    // parses as the wrong thing.
                                    tracing::warn!(
                                        peer = %req.device_address,
                                        "inbound queue full; refusing the write"
                                    );
                                    Err(GattError::Failed)
                                }
                                Err(mpsc::error::TrySendError::Closed(_)) => {
                                    tracing::warn!("the session has ended; refusing the write");
                                    Err(GattError::Failed)
                                }
                            },
                        };

                        async move {
                            if let Some(payload) = learned {
                                tracing::info!(
                                    payload,
                                    "negotiated notification payload; replies are sized for this"
                                );
                            }
                            // Eight bytes of the chunk, so a reordering is visible in the journal
                            // rather than inferred from a parse error three layers up. Truncated
                            // because a request may carry a wifi passphrase.
                            tracing::debug!(
                                peer = %req.device_address,
                                mtu = req.mtu,
                                bytes,
                                ok = result.is_ok(),
                                head = %head,
                                "write"
                            );
                            result
                        }
                        .boxed()
                    })),
                    ..Default::default()
                }),
                notify: Some(CharacteristicNotify {
                    notify: true,
                    method: CharacteristicNotifyMethod::Fun(Box::new(move |mut notifier| {
                        let slot = for_notify.clone();
                        let sockets = sockets.clone();
                        let mtu = mtu.clone();
                        async move {
                            tokio::spawn(async move {
                                // A fresh session, so nothing from a previous central can leak
                                // into this one.
                                // Back to the floor for a new central: the previous one's MTU is
                                // not this one's, and the first write will report the real value
                                // before any reply is chunked.
                                mtu.store(FLOOR_MTU, Ordering::Relaxed);
                                let (link, inbound, mut outbound) =
                                    Link::pair_sharing_mtu(mtu.clone(), "central");
                                let mine = inbound.clone();
                                {
                                    let mut slot = slot.lock().expect("write slot poisoned");
                                    if slot.is_some() {
                                        // bluer keeps one notify state per characteristic, so this
                                        // replaces rather than shares: two clients through one
                                        // reassembly buffer would interleave their requests.
                                        tracing::warn!(
                                            "another central was subscribed; replacing its session"
                                        );
                                    }
                                    *slot = Some(inbound);
                                }
                                let session = tokio::spawn(session::run(link, sockets));
                                tracing::info!("central subscribed");

                                // Notifications queued since the last pause. See `NOTIFY_BURST`
                                // for why a pump with no readiness signal has to pace itself.
                                let mut queued = 0usize;
                                let mut gone = false;

                                loop {
                                    tokio::select! {
                                        // Biased so a central that has gone away is noticed before
                                        // another chunk is pulled out of the queue and lost in the
                                        // notify that follows.
                                        biased;
                                        // Without this the pump only learns the central is gone
                                        // when a notify fails — which needs a reply to send, so a
                                        // client that disconnects while idle would hold the slot
                                        // until the next request arrives for nobody.
                                        () = notifier.stopped() => {
                                            gone = true;
                                            break;
                                        }
                                        chunk = outbound.recv() => match chunk {
                                            None => break,
                                            Some(chunk) => {
                                                if !notify_chunk(&mut notifier, chunk).await {
                                                    gone = true;
                                                    break;
                                                }
                                                queued += 1;
                                                if queued >= NOTIFY_BURST {
                                                    queued = 0;
                                                    tokio::time::sleep(NOTIFY_PAUSE).await;
                                                }
                                            }
                                        },
                                    }
                                }

                                // Only clear the slot if it is still *ours*. This task can outlive
                                // its subscription — a notify to a vanished central takes as long
                                // as BlueZ takes to give up — and by then a reconnecting central may
                                // have installed a newer session, which a blind `take()` would kill.
                                {
                                    let mut slot = slot.lock().expect("write slot poisoned");
                                    if slot.as_ref().is_some_and(|tx| tx.same_channel(&mine)) {
                                        // Dropping the sender ends the session task, which discards
                                        // its reassembly buffer and its upstream connections.
                                        slot.take();
                                        session.abort();
                                        // Which of the two it was, because they need different
                                        // next moves and the old line said "unsubscribed" for
                                        // both — including for a reply this pump could not
                                        // deliver, which is a robot problem wearing a client's
                                        // clothes.
                                        if gone {
                                            tracing::info!(
                                                "the central is gone; session discarded"
                                            );
                                        } else {
                                            tracing::info!(
                                                "the outbound queue closed; session discarded"
                                            );
                                        }
                                    } else {
                                        tracing::debug!(
                                            "a newer session holds the slot; leaving it alone"
                                        );
                                        session.abort();
                                    }
                                }
                            });
                        }
                        .boxed()
                    })),
                    ..Default::default()
                }),
                ..Default::default()
            }],
            ..Default::default()
        }],
        ..Default::default()
    };
    let _app = adapter.serve_gatt_application(app).await?;

    tracing::info!("GATT application registered; waiting for a central");

    // The advertisement and application handles deregister on drop, so this must not return while
    // the adapter is usable — which used to mean `pending()`, waiting forever. Forever was wrong in
    // one direction: an adapter that disappeared left this task parked on a dead radio, holding
    // handles to nothing and advertising nothing, with no way back short of a restart nobody knew
    // to perform. Returning hands the caller a bring-up on the adapter's next appearance.
    //
    // The advertisement is reconciled *alongside* that wait rather than after it, so losing the
    // adapter ends both: whichever finishes first ends the bring-up, and the reconcile is dropped
    // with the advertisement handle it owns.
    //
    // It runs even when `--name` pins the name, because the address moves on its own and a pinned
    // name never meant a frozen advertisement — before the address was in it, the two were the same
    // thing. So the pin suppresses the *question*, not the loop.
    if name.pinned.is_some() {
        tracing::info!(
            name = %advertised.name,
            "--name pins the advertised name; only the address is reconciled"
        );
    }
    tokio::select! {
        () = watch_adapter(&adapter) => {}
        // Never completes on its own.
        () = reconcile_advertisement(
            &adapter,
            &for_reconcile,
            advertised,
            name.pinned.is_some(),
            handle,
            &current,
        ) => {}
    }
    Ok(())
}

/// Send one chunk, retrying a queue that is momentarily full. `false` means give up on the session.
///
/// **The distinction this function exists to draw**: `notify` returns the same error for "the
/// central unsubscribed" and "the D-Bus connection would not take this signal", and the pump used
/// to read both as the central having left. So a reply too big for one burst tore down the session
/// mid-line, and the client — still connected, as far as CoreBluetooth was concerned — waited out
/// its idle timeout with no error to report and half an answer in its reassembler. That was
/// diagnosed from a board, not from the journal, because the only line it left was a `debug` one
/// blaming the central.
///
/// `is_stopped` tells them apart: it is closed only when the notification session really has
/// ended. Anything else is retried, and the chunk is cloned because `notify` consumes it and a
/// dropped chunk corrupts the line rather than failing it.
async fn notify_chunk(notifier: &mut CharacteristicNotifier, chunk: Vec<u8>) -> bool {
    for attempt in 1..=NOTIFY_RETRIES {
        match notifier.notify(chunk.clone()).await {
            Ok(()) => return true,
            Err(_) if notifier.is_stopped() => {
                tracing::debug!("the notification session ended mid-reply");
                return false;
            }
            Err(e) => {
                tracing::warn!(
                    attempt,
                    error = %e,
                    "the notification queue would not take a chunk; retrying"
                );
                tokio::time::sleep(NOTIFY_RETRY_BACKOFF).await;
            }
        }
    }
    // A warning rather than a silence, which is the whole point: this ends a session, and
    // whoever is holding the client deserves to find out why from the robot's own journal.
    tracing::warn!(
        retries = NOTIFY_RETRIES,
        "gave up on a notification chunk; ending the session rather than sending a corrupt line"
    );
    false
}

/// What the advertisement says about the robot: what it is called, where it is on the network, and
/// whether anyone may connect to it.
///
/// One struct rather than three arguments threaded through the reconcile loop, so that "has
/// anything moved" is one comparison. `connectable` belongs here for exactly that reason: it moves
/// on its own schedule, and keeping it beside the struct would be a second comparison to forget.
/// It costs nothing in the advertisement's 31 bytes — it is the advertisement's *type* rather than
/// a field in it, so `duck_ble::adv`'s budget is untouched.
#[derive(Debug, Clone, PartialEq, Eq)]
struct Advertised {
    name: String,
    /// `None` is a robot with no IPv4 address, which goes out as `0.0.0.0` — see [`duck_ble::adv`] for
    /// why the field is broadcast either way.
    address: Option<Ipv4Addr>,
    /// Whether a central may connect to this. False while one is already being served — see
    /// [`advertise`] for what that changes and why it is not just politeness.
    connectable: bool,
}

impl std::fmt::Display for Advertised {
    /// For the journal, where the interesting line is the one that says what changed.
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self.address {
            Some(address) => write!(f, "{} at {address}", self.name)?,
            None => write!(f, "{} with no address", self.name)?,
        }
        if !self.connectable {
            write!(f, ", not taking connections")?;
        }
        Ok(())
    }
}

/// Advertise the service under this name and address, and make the name the adapter's too.
///
/// The handle deregisters on drop, so the caller holds it for as long as the robot should be
/// visible.
///
/// **Both names, because a robot has two and only one of them used to be set.** The advertisement
/// carries a Local Name; the adapter separately serves a GAP Device Name (`0x2A00`), which BlueZ
/// takes from `Adapter.Alias` and which defaults to the hostname. So a renamed robot advertised
/// `duck-5b21` while answering `radxa-zero3` to anyone who read the characteristic — and a client
/// that read it kept the answer:
///
/// - **BlueZ caches it over the advertised name.** `Device1.Name` is what `btleplug` reports, so
///   on Linux a robot is `duck-5b21` until the first connection and `radxa-zero3` after it, and
///   `duckctl --name duck-5b21` then finds nothing. Two scans a minute apart disagreed;
/// - **CoreBluetooth keeps both**, and `btleplug` joins them as `radxa-zero3 [duck-5b21]`;
/// - **a phone's Bluetooth settings shows the GAP name**, which is the case that matters most and
///   the one nothing in this repo could see.
///
/// Setting the alias is therefore part of naming the robot rather than a nicety, and it belongs
/// here so that no path can publish a name without it: [`reconcile_advertisement`] re-advertises on
/// every rename and comes through this function to do it. The alias persists in BlueZ's own state,
/// so the write is skipped when it already says the right thing.
///
/// A failure to set it is logged and not propagated. The alias is worth less than being visible at
/// all, and returning an error here would take the advertisement down with it.
///
/// **The address field is dropped rather than allowed to fail the registration.** The arithmetic in
/// [`duck_ble::adv`] says the payload fits, but the byte that overflows a legacy advertisement is the
/// controller's to count, not ours — and BlueZ refuses the whole registration when it does not fit.
/// On a robot whose only front door may be BLE, that trade is not close: an advertisement with no
/// address is a robot someone can still reach, and a refused one is a robot that has gone dark. Same
/// reasoning as the alias above, one step further down.
///
/// ## Why a busy robot advertises a *broadcast*
///
/// [`Advertised::connectable`] is false while a central is being served, and then this registers
/// the same payload as a non-connectable advertisement instead of a connectable one. Two separate
/// things make that the right shape, and only one of them is about this hardware:
///
/// - **The daemon serves one central at a time.** `bluer` holds one notification state per
///   characteristic (see this module's header), so a second subscriber does not get a second
///   session — it *replaces* the first one. A connectable advertisement while a client is being
///   served therefore invites something the robot cannot honour, and the client that accepts the
///   invitation is the one that breaks the session someone else was using.
/// - **The radio will not do it anyway.** A connection stops the advertising set that produced it,
///   and Linux will not re-enable a connectable set while a peripheral-role connection is open
///   unless the controller's LE Supported States say it can — `is_advertising_allowed` in
///   `net/bluetooth/hci_sync.c`, which wants states 38 and 21. The board's controller has 20 and 21
///   and not 38, measured: with a phone connected, a non-connectable set carrying this same service
///   UUID was found by a scan from a laptop, and a connectable one registered without ever reaching
///   the air.
///
/// So this is not a workaround dressed as a policy. Going non-connectable is the true statement —
/// *here I am, not available* — and it is also the only statement the controller will broadcast.
/// What it buys is everything a listing answers without connecting: `duckctl scan` finds the robot
/// while the phone app holds it, and the address in the payload is what `duckctl ip`, `ssh`, `scp`
/// and `open` need, none of which take the radio at all.
///
/// The swap back is the one that can fail quietly. BlueZ registers a connectable advertisement
/// whether or not the kernel will enable it, so a central that unsubscribes without disconnecting
/// leaves this holding a handle to an advertisement that is not on the air. That is exactly the
/// state the robot was in before any of this existed, it resolves itself when the link drops — the
/// kernel re-enables the instance on disconnect — and it is the reason [`reconcile_advertisement`]
/// re-registers rather than assuming a handle means visibility.
async fn advertise(
    adapter: &bluer::Adapter,
    advertised: &Advertised,
) -> bluer::Result<bluer::adv::AdvertisementHandle> {
    let name = advertised.name.as_str();
    if adapter.alias().await.ok().as_deref() != Some(name)
        && let Err(e) = adapter.set_alias(name.to_owned()).await
    {
        tracing::warn!(error = %e, name, "cannot set the adapter alias; the GAP name stays stale");
    }

    let advertisement = |address: Option<Vec<u8>>| Advertisement {
        service_uuids: [SERVICE_UUID].into_iter().collect(),
        manufacturer_data: address
            .map(|data| [(duck_ble::adv::COMPANY_ID, data)].into_iter().collect())
            .unwrap_or_default(),
        advertisement_type: if advertised.connectable {
            Type::Peripheral
        } else {
            Type::Broadcast
        },
        // Set only on the connectable variant, because `org.bluez.LEAdvertisement` says this
        // property shall not be set when the type is `broadcast` and BlueZ refuses the whole
        // registration when it is. No loss: the flag it sets is the general-discoverable one, and a
        // scanner finds this by the service UUID, which is in the payload either way.
        discoverable: advertised.connectable.then_some(true),
        local_name: Some(name.to_owned()),
        min_interval: Some(ADV_INTERVAL_MIN),
        max_interval: Some(ADV_INTERVAL_MAX),
        ..Default::default()
    };

    let with_address = advertisement(Some(duck_ble::adv::address_data(advertised.address)));
    match adapter.advertise(with_address).await {
        Ok(handle) => Ok(handle),
        Err(e) => {
            tracing::warn!(
                error = %e,
                "BlueZ refused the advertisement carrying the address; retrying without it, so \
                 `duckctl scan` will show this robot with no address at all"
            );
            adapter.advertise(advertisement(None)).await
        }
    }
}

/// Keep the advertisement in step with the robot — the name and address `configd` reports, and
/// whether a central is being served. Never returns.
///
/// Owns the advertisement handle, because changing any of the three means deregistering one
/// advertisement and registering another — nothing else may be holding it while that happens.
///
/// `pinned_name` is `--name`: the name is then this process's own and there is nobody to ask about
/// it, so only the address is reconciled. The loop still runs, because a pinned name does not pin a
/// DHCP lease — nor a client arriving.
///
/// **Two cadences, one loop.** The tick is [`SESSION_POLL`] and `configd` is asked every
/// [`ADV_POLL`]; the reasoning is on those two constants. Folding them into one loop rather than
/// two tasks is not tidiness: both decide what is on the air, and the handle may only be held by
/// one of them.
async fn reconcile_advertisement(
    adapter: &bluer::Adapter,
    sockets: &Sockets,
    mut advertised: Advertised,
    pinned_name: bool,
    mut handle: Option<bluer::adv::AdvertisementHandle>,
    session: &SessionSlot,
) {
    let mut asked = tokio::time::Instant::now();
    loop {
        tokio::time::sleep(SESSION_POLL).await;

        let due = asked.elapsed() >= ADV_POLL;
        let (name, address) = if due {
            let name = if pinned_name {
                advertised.name.clone()
            } else {
                ask_name(sockets, &advertised.name).await
            };
            let address = ask_address(sockets, advertised.address).await;
            // After the asks rather than before: `ASK_TIMEOUT` is as long as [`ADV_POLL`], so a
            // `configd` that is not answering would otherwise be asked again the moment it timed
            // out, on every tick, for as long as the outage lasted.
            asked = tokio::time::Instant::now();
            (name, address)
        } else {
            (advertised.name.clone(), advertised.address)
        };

        let current = Advertised {
            name,
            address,
            connectable: !serving(session),
        };
        // `handle` is `None` only after a failed re-advertise, and then the robot is invisible —
        // so retry regardless of whether anything moved.
        if current == advertised && handle.is_some() {
            continue;
        }

        // Deregistered before the replacement is registered: BlueZ is being asked to change one
        // advertisement, and holding two while swapping invites it to refuse the second. The gap is
        // brief, and a central that is already connected does not notice — a connection is not an
        // advertisement.
        drop(handle.take());
        match advertise(adapter, &current).await {
            Ok(new) => {
                if current == advertised {
                    tracing::info!(advertising = %current, "advertising again after a failure");
                } else {
                    tracing::info!(from = %advertised, to = %current, "advertisement changed");
                }
                handle = Some(new);
                advertised = current;
            }
            // Left for the next tick rather than fatal, and never propagated: this is inside a
            // bring-up whose whole point is that radio faults do not end the process.
            Err(e) => tracing::error!(error = %e, advertising = %current, "cannot advertise"),
        }
    }
}

/// What `configd` says the robot is called, or `fallback` if it will not say.
///
/// A failure is `debug` rather than `warn`: this runs every few seconds, and a `configd` that is
/// restarting would otherwise fill the journal with a condition that resolves itself. The startup
/// call is the one that matters, and it is logged by the caller through the name it ends up
/// advertising.
async fn ask_name(sockets: &Sockets, fallback: &str) -> String {
    let socket = sockets.path(crate::route::Upstream::Config);
    match crate::upstream::ask(
        "configd",
        socket,
        &duck_ipc_proto::Call::SystemInfo,
        ASK_TIMEOUT,
    )
    .await
    .and_then(|response| {
        response
            .result_as::<duck_ipc_proto::SystemInfoResult>()
            .map_err(|e| e.to_string())
    }) {
        Ok(info) => info.name,
        Err(e) => {
            tracing::debug!(error = %e, fallback, "configd would not say the robot's name");
            fallback.to_owned()
        }
    }
}

/// What `configd` says the robot's IPv4 address is, or `last` if it will not say.
///
/// **The two failures are not the same answer, and conflating them made the advertisement flap.**
/// `configd` reporting no address is a robot that is not on wifi, and that clears the field.
/// `configd` not answering — restarting, or NetworkManager taking longer than [`ASK_TIMEOUT`] —
/// says nothing about the robot's network, and clearing the field on it would deregister and
/// re-register the advertisement on every tick for as long as the outage lasted, with a client
/// watching the address blink. So an outage keeps the last known address, exactly as [`ask_name`]
/// keeps the last known name.
///
/// Only IPv4, because only IPv4 fits — see [`duck_ble::adv`].
///
/// `debug` rather than `warn` for the same reason as [`ask_name`]: this runs every few seconds.
async fn ask_address(sockets: &Sockets, last: Option<Ipv4Addr>) -> Option<Ipv4Addr> {
    let socket = sockets.path(crate::route::Upstream::Config);
    match crate::upstream::ask(
        "configd",
        socket,
        &duck_ipc_proto::Call::NetStatus,
        ASK_TIMEOUT,
    )
    .await
    .and_then(|response| {
        response
            .result_as::<duck_ipc_proto::NetStatusResult>()
            .map_err(|e| e.to_string())
    }) {
        // Parsed rather than trusted: `ip4` is whatever NetworkManager put in `address-data`, and a
        // string this cannot parse is not something to broadcast four bytes of.
        Ok(status) => status.ip4.and_then(|address| match address.parse() {
            Ok(address) => Some(address),
            Err(e) => {
                tracing::warn!(error = %e, address, "configd reported an unparseable IPv4 address");
                None
            }
        }),
        Err(e) => {
            tracing::debug!(error = %e, "configd would not say the robot's address");
            last
        }
    }
}

/// Return once the adapter stops being usable.
///
/// A poll, not an event stream. `bluer` can report adapter removal, but the failure this has to
/// catch is broader than removal — an adapter still on the bus that answers nothing is the case
/// that used to kill the process — and reading one property covers both without depending on which
/// events BlueZ emits for a radio that is wedged rather than absent.
///
/// The interval is [`ADAPTER_RETRY`] because the cost of noticing late is exactly the cost of
/// retrying late: BLE stays dark a few more seconds, on a daemon that is otherwise idle.
async fn watch_adapter(adapter: &bluer::Adapter) {
    loop {
        tokio::time::sleep(ADAPTER_RETRY).await;
        match adapter.is_powered().await {
            Ok(true) => {}
            // Powered off underneath us — by `bluetoothctl power off`, by a driver reset, or by a
            // suspend. The next bring-up powers it again: on a robot whose only front door may be
            // BLE, an unpowered adapter is not a state to preserve out of politeness.
            Ok(false) => {
                tracing::warn!("the adapter is no longer powered");
                return;
            }
            Err(e) => {
                tracing::warn!(error = %e, "the adapter stopped answering");
                return;
            }
        }
    }
}

```

### File: `btd/src/chorale.rs` (494 lines, ~6164 tokens)
```rs
//! The duck chorale's radio: a beacon out, and other ducks' beacons in.
//!
//! **Still a transport adapter.** `btd` owns no chorale state and makes no chorale decisions — it
//! broadcasts bytes it was handed and reports bytes it heard, which is the same job it does for
//! JSON-RPC. Who conducts, who sings what, and when a piece starts are all `robotd`'s, because
//! they are behaviour.
//!
//! It lives here rather than in a daemon of its own because everything it needs is already here:
//! the adapter, `bluer`, the D-Bus permissions, and a connection to `robotd`. A second process
//! contending for the same adapter would be more moving parts for no separation that matters.
//!
//! ## Out: a second advertising instance
//!
//! The board reports five advertising instances with one in use, so the beacon gets its own and
//! **the existing advertisement is not touched.** That is not tidiness. `duck_ble::adv` documents a
//! 31-byte budget, and the controller here reports a 251-byte one — so BlueZ would happily accept
//! a bigger payload on the existing instance and, because it picks legacy against extended PDUs by
//! size, would switch it to extended and make the robot invisible to a legacy-only scanner. Phone
//! discovery would regress and it would look like a Bluetooth fault rather than a chorale one.
//!
//! ## Registered on demand, and this one is load-bearing
//!
//! A controller interleaves its advertising instances, so registering a second one **halves the
//! rate of the first**. `crate::bluez`'s interval was tuned against measurements — the default
//! 1.28 s left a robot absent for up to 31 s at a time, and 100–150 ms fixed it — so permanently
//! halving it would spend that hard-won margin on a feature nobody has asked for yet. The beacon
//! is therefore registered only while a chorale is wanted, and dropped when it is not.
//!
//! ## In: two ways to listen, because the good one is not always there
//!
//! The one to want is BlueZ's advertisement monitor ([`bluer::monitor`]): it filters on a byte
//! pattern *in the controller*, so the host is woken only for advertisements that are already
//! chorale beacons, and it is passive — the duck transmits nothing to listen, which matters when
//! one antenna carries this, the gamepad's link and wifi.
//!
//! **It is not on this board.** `AdvertisementMonitorManager1` is still behind `bluetoothd
//! --experimental` in BlueZ 5.82, and the daemon here runs without it, so `RegisterMonitor` comes
//! back `UnknownMethod` and two ducks sit in a room hearing nothing. Turning `--experimental` on
//! globally would enable a set of other unfinished interfaces underneath the phone's only way in,
//! which is a poor trade for a power saving.
//!
//! So [`watch`] tries the monitor and falls back to ordinary discovery, which has been in every
//! BlueZ forever. The costs of the fallback are real and worth knowing:
//!
//!  - **It scans actively**, so the duck transmits. More airtime taken from the gamepad.
//!  - **It needs `duplicate_data`.** BlueZ suppresses repeated advertisement data by default, and a
//!    beacon's *payload* is the whole signal — without this every beat after the first is invisible
//!    and a follower locks onto nothing.
//!  - Filtering happens in the host rather than the controller, so the byte pattern is applied by
//!    [`beacon_in`] after the fact instead of before the wakeup.
//!
//! Either way the discriminator is the same: manufacturer-data on company id `0xFFFF` beginning
//! with [`ChoraleBeacon::TAG`]. That tag is why the *other* advertising instance's four bytes of
//! IPv4 address are not delivered here as a beat.
//!
//! ## What the arrival time means
//!
//! A sighting is stamped when this process sees it, which is after the controller, the kernel and
//! a D-Bus property change. That path adds a few milliseconds and some jitter — and the design
//! upstream ([`sounds::chorale::beat`], in the `sounds` crate) is built for exactly that: it
//! averages the phase over many beats, so anything random averages out, and anything *constant* is
//! common to every duck on identical hardware and so inaudible. What it cannot absorb is a
//! systematic difference between the conductor's idea of when its beat went out and the
//! followers' — which is why that constant wants measuring on hardware rather than assuming.

use std::collections::HashMap;

use duck_ipc_proto::ChoraleBeacon;

/// The company id chorale beacons ride under — the same one [`duck_ble::adv`] uses, for the same
/// reason: `0xFFFF` is the id the SIG reserves for testing and is the correct choice for a project
/// that has not been assigned one.
pub const COMPANY_ID: u16 = duck_ble::adv::COMPANY_ID;

/// The advertising interval for the beacon.
///
/// Faster than [`crate::bluez`]'s 100–150 ms, and deliberately: this one carries a beat, and how
/// promptly a payload change reaches the air *is* the sync error. It is affordable because the
/// instance only exists while a chorale is running — see the module docs.
pub const BEACON_INTERVAL_MIN: std::time::Duration = std::time::Duration::from_millis(20);
pub const BEACON_INTERVAL_MAX: std::time::Duration = std::time::Duration::from_millis(40);

/// The bytes a scan filter has to match, from the start of the manufacturer-data AD field.
///
/// Little-endian company id, then the beacon's tag. Matching in the controller rather than in the
/// host is what makes the scan cost nothing while nothing is singing.
pub fn scan_pattern() -> Vec<u8> {
    let id = COMPANY_ID.to_le_bytes();
    vec![id[0], id[1], ChoraleBeacon::TAG]
}

/// A beacon as the advertisement's manufacturer-data payload.
///
/// The payload rather than the map, mirroring [`duck_ble::adv::address_data`] — and because the two
/// halves want different containers: `bluer` advertises from a `BTreeMap` and reports a scanned
/// device's data as a `HashMap`.
pub fn beacon_data(beacon: &ChoraleBeacon) -> Vec<u8> {
    beacon.to_bytes()
}

/// The beacon in a device's manufacturer data, if there is one.
///
/// `None` for anything else on the same company id — the address field the other instance
/// broadcasts, or another vendor using `0xFFFF`, which anyone may. The tag is the discriminator;
/// see [`ChoraleBeacon::from_bytes`].
pub fn beacon_in(manufacturer_data: &HashMap<u16, Vec<u8>>) -> Option<ChoraleBeacon> {
    ChoraleBeacon::from_bytes(manufacturer_data.get(&COMPANY_ID)?)
}

#[cfg(target_os = "linux")]
pub use radio::{Sighting, broadcast, run, watch};

#[cfg(target_os = "linux")]
mod radio {
    use std::time::Instant;

    use bluer::adv::{Advertisement, Type};
    use bluer::monitor::{Monitor, MonitorEvent, Pattern, RssiSamplingPeriod};
    use duck_ipc_proto::ChoraleBeacon;
    use futures::StreamExt;
    use tokio::sync::mpsc;

    use super::{BEACON_INTERVAL_MAX, BEACON_INTERVAL_MIN, beacon_data, beacon_in, scan_pattern};

    /// AD type for manufacturer-specific data. What the monitor pattern is matched against.
    const AD_TYPE_MANUFACTURER_DATA: u8 = 0xFF;

    /// One beacon heard from another duck.
    #[derive(Debug, Clone, PartialEq, Eq)]
    pub struct Sighting {
        pub beacon: ChoraleBeacon,
        /// Which duck. Only an identity for de-duplicating — a beacon says nothing about who is
        /// broadcasting it beyond its register and tie-break byte.
        pub from: bluer::Address,
        /// When this process saw it. See the module docs for what that is and is not.
        pub at: Instant,
    }

    /// Put a beacon on the air, on its own advertising instance.
    ///
    /// Dropping the returned handle stops it, which is how the instance is released the moment a
    /// chorale ends — the whole reason it is registered on demand.
    ///
    /// Carries neither the service UUID nor a local name: the scan filters on the manufacturer
    /// data, so an 18-byte UUID would buy nothing and a name would only make the payload big
    /// enough to change PDU type.
    ///
    /// **Non-connectable, which `Advertisement::default()` is not.** `bluer` defaults the type to
    /// `Peripheral`, so this instance used to offer a second way in to a daemon that serves one
    /// central — and, worse, a connectable instance is one Linux will not re-enable while a
    /// peripheral-role connection is open (`is_advertising_allowed` in
    /// `net/bluetooth/hci_sync.c`; see [`crate::bluez::advertise`]). A beacon is re-registered on
    /// every change `robotd` asks for, so that rule meant a chorale went silent for as long as a
    /// phone was connected, and came back only when it left. `Broadcast` is what this always meant.
    pub async fn broadcast(
        adapter: &bluer::Adapter,
        beacon: &ChoraleBeacon,
    ) -> bluer::Result<bluer::adv::AdvertisementHandle> {
        adapter
            .advertise(Advertisement {
                manufacturer_data: [(super::COMPANY_ID, beacon_data(beacon))]
                    .into_iter()
                    .collect(),
                // A beacon, not a way in. The robot's front door is the other advertisement, and
                // it is unchanged. `Discoverable` is left unset rather than set false, because
                // `org.bluez.LEAdvertisement` says it shall not be set on a broadcast at all.
                advertisement_type: Type::Broadcast,
                min_interval: Some(BEACON_INTERVAL_MIN),
                max_interval: Some(BEACON_INTERVAL_MAX),
                ..Default::default()
            })
            .await
    }

    /// Serve the chorale for as long as the adapter lives.
    ///
    /// One connection to `robotd`, carrying both directions: a `chorale.subscribe` stream down
    /// saying what to advertise, and `chorale.heard` notifications up saying what arrived. `robotd`
    /// decides everything; this only holds the radio.
    ///
    /// Returns when the connection or the adapter goes away, so the caller restarts it the same way
    /// [`crate::bluez::serve`] restarts on losing an adapter. A `robotd` that is not there yet — the
    /// ordinary case at boot — is a retry, not a failure.
    pub async fn run(
        adapter: &bluer::Adapter,
        robot_socket: &std::path::Path,
    ) -> std::io::Result<()> {
        use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader};

        let stream = tokio::net::UnixStream::connect(robot_socket).await?;
        let (read_half, mut write_half) = stream.into_split();
        let mut lines = BufReader::new(read_half).lines();

        let request = duck_ipc_proto::Request::call(
            duck_ipc_proto::Id::Number(1),
            &duck_ipc_proto::Call::ChoraleSubscribe,
        );
        let mut line = serde_json::to_string(&request).map_err(std::io::Error::other)?;
        line.push('\n');
        write_half.write_all(line.as_bytes()).await?;

        // Held for as long as `robotd` wants them, and dropped the moment it does not: a second
        // advertising instance halves the first one's rate, and a monitor costs the controller.
        // Held only to be dropped: an `AdvertisementHandle` stops advertising when it goes, which
        // is exactly how the instance is released the moment `robotd` says to stop.
        let mut _advertisement: Option<bluer::adv::AdvertisementHandle> = None;
        let mut listening: Option<tokio::task::JoinHandle<()>> = None;
        let (heard_tx, mut heard_rx) = mpsc::channel::<Sighting>(64);

        loop {
            tokio::select! {
                line = lines.next_line() => {
                    let Some(line) = line? else { return Ok(()) };
                    let Ok(request) = serde_json::from_str::<duck_ipc_proto::Request>(&line) else {
                        continue;
                    };
                    let Ok(duck_ipc_proto::Call::ChoraleBeaconSet(want)) = request.as_call() else {
                        continue;
                    };
                    // Advertise what was asked for, and nothing when nothing was.
                    _advertisement = match &want.beacon {
                        Some(beacon) => match broadcast(adapter, beacon).await {
                            Ok(handle) => Some(handle),
                            Err(e) => {
                                tracing::warn!(error = %e, "chorale: cannot advertise the beacon");
                                None
                            }
                        },
                        None => None,
                    };
                    // And scan only while asked to. Restarting the monitor on every beat would be
                    // absurd, so the task is started once and kept until listening stops.
                    match (want.listening, listening.is_some()) {
                        (true, false) => {
                            let adapter = adapter.clone();
                            let tx = heard_tx.clone();
                            listening = Some(tokio::spawn(async move {
                                if let Err(e) = watch(&adapter, tx).await {
                                    tracing::warn!(error = %e, "chorale: the scan stopped");
                                }
                            }));
                        }
                        (false, true) => {
                            if let Some(task) = listening.take() {
                                task.abort();
                            }
                            tracing::warn!("chorale: no longer listening");
                        }
                        _ => {}
                    }
                }
                Some(sighting) = heard_rx.recv() => {
                    // An *age*, not a timestamp: the two daemons share a machine but not an epoch,
                    // and an age survives the trip down a socket in a way another process's clock
                    // reading does not.
                    let heard = duck_ipc_proto::ChoraleHeard {
                        beacon: sighting.beacon,
                        from: sighting.from.to_string(),
                        age_us: sighting.at.elapsed().as_micros() as u64,
                    };
                    let notify = duck_ipc_proto::Request::notify(
                        &duck_ipc_proto::Call::ChoraleHeard(heard),
                    );
                    let mut line = serde_json::to_string(&notify).map_err(std::io::Error::other)?;
                    line.push('\n');
                    if write_half.write_all(line.as_bytes()).await.is_err() {
                        return Ok(());
                    }
                }
            }
        }
    }

    /// Watch for other ducks' beacons, forever, sending each sighting to `tx`.
    ///
    /// Prefers the controller-offloaded monitor and falls back to ordinary discovery when BlueZ has
    /// no monitor to offer — see the module docs for why that is the common case here and what the
    /// fallback costs.
    pub async fn watch(adapter: &bluer::Adapter, tx: mpsc::Sender<Sighting>) -> bluer::Result<()> {
        match monitor(adapter, tx.clone()).await {
            Ok(()) => Ok(()),
            Err(e) => {
                // Any failure to *register* falls back; a monitor that registered and then died is a
                // different matter and is reported as itself.
                tracing::warn!(
                    error = %e,
                    "chorale: no advertisement monitor (bluetoothd without --experimental?); \
                     falling back to discovery, which scans actively"
                );
                discover(adapter, tx).await
            }
        }
    }

    /// The good path: the controller matches the pattern and only wakes us for beacons.
    async fn monitor(adapter: &bluer::Adapter, tx: mpsc::Sender<Sighting>) -> bluer::Result<()> {
        let manager = adapter.monitor().await?;
        let mut monitor = manager
            .register(Monitor {
                monitor_type: bluer::monitor::Type::OrPatterns,
                patterns: Some(vec![Pattern {
                    data_type: AD_TYPE_MANUFACTURER_DATA,
                    start_position: 0,
                    content: scan_pattern(),
                }]),
                // Every packet, not just the first sighting of a device: the payload is what
                // changes, and a beat we are told about once is not a beat.
                rssi_sampling_period: Some(RssiSamplingPeriod::All),
                ..Default::default()
            })
            .await?;
        tracing::warn!(pattern = ?scan_pattern(), "chorale: listening (monitor)");

        while let Some(event) = monitor.next().await {
            let MonitorEvent::DeviceFound(found) = event else {
                continue;
            };
            if let Ok(device) = adapter.device(found.device) {
                spawn_follow(device, tx.clone());
            }
        }
        Ok(())
    }

    /// The fallback: ordinary discovery, filtered in the host.
    async fn discover(adapter: &bluer::Adapter, tx: mpsc::Sender<Sighting>) -> bluer::Result<()> {
        adapter
            .set_discovery_filter(bluer::DiscoveryFilter {
                transport: bluer::DiscoveryTransport::Le,
                // **Load-bearing.** Without it BlueZ reports a device's advertisement data once and
                // suppresses the repeats — and a beacon's payload is the entire signal, so every
                // beat after the first would be invisible.
                duplicate_data: true,
                ..Default::default()
            })
            .await?;
        let mut events = adapter.discover_devices_with_changes().await?;
        tracing::warn!("chorale: listening (discovery)");

        while let Some(event) = events.next().await {
            let bluer::AdapterEvent::DeviceAdded(address) = event else {
                continue;
            };
            if let Ok(device) = adapter.device(address) {
                spawn_follow(device, tx.clone());
            }
        }
        Ok(())
    }

    /// Watch one duck's advertisement for as long as it keeps changing.
    ///
    /// One task per duck heard: whichever way it was found, the *payload* arriving repeatedly is a
    /// property change on the device, and that is what carries the beat.
    fn spawn_follow(device: bluer::Device, tx: mpsc::Sender<Sighting>) {
        tokio::spawn(async move {
            let address = device.address();
            // Whatever it was already advertising when it was found — the first beat is otherwise
            // missed while waiting for a change that has already happened.
            if let Ok(Some(data)) = device.manufacturer_data().await
                && let Some(beacon) = beacon_in(&data)
                && tx
                    .send(Sighting {
                        beacon,
                        from: address,
                        at: Instant::now(),
                    })
                    .await
                    .is_err()
            {
                return;
            }
            let Ok(mut events) = device.events().await else {
                return;
            };
            while let Some(event) = events.next().await {
                let bluer::DeviceEvent::PropertyChanged(bluer::DeviceProperty::ManufacturerData(
                    data,
                )) = event
                else {
                    continue;
                };
                // Stamped here, as early as this process can: everything after is jitter the phase
                // average has to absorb.
                let at = Instant::now();
                let Some(beacon) = beacon_in(&data) else {
                    continue;
                };
                if tx
                    .send(Sighting {
                        beacon,
                        from: address,
                        at,
                    })
                    .await
                    .is_err()
                {
                    return;
                }
            }
        });
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn beacon() -> ChoraleBeacon {
        ChoraleBeacon {
            piece: 2,
            beat: 91,
            register: 56,
            id: 0x3D,
            roster: vec![(56, 0x3D), (180, 0x11)],
        }
    }

    fn advertised(beacon: &ChoraleBeacon) -> HashMap<u16, Vec<u8>> {
        HashMap::from([(COMPANY_ID, beacon_data(beacon))])
    }

    /// The round trip the broadcasting half and the scanning half both depend on — the same
    /// property `duck_ble::adv` pins for the address field, and for the same reason.
    #[test]
    fn a_beacon_survives_the_advertisement() {
        assert_eq!(beacon_in(&advertised(&beacon())), Some(beacon()));
    }

    /// The trap the tag exists to close: the *other* advertising instance broadcasts four bytes of
    /// IPv4 under the same company id, and a scanner that read those as a beacon would hear a beat
    /// in an address.
    #[test]
    fn the_address_instance_is_not_heard_as_a_beat() {
        let address = HashMap::from([(
            COMPANY_ID,
            duck_ble::adv::address_data(Some(std::net::Ipv4Addr::new(192, 168, 1, 42))),
        )]);
        assert_eq!(beacon_in(&address), None);
        // And the reverse: a beacon is not read as an address, so a scanning `duck-btctl` does not
        // report a robot at some nonsense IP.
        let as_advertised = advertised(&beacon());
        assert_eq!(duck_ble::adv::address_in(&as_advertised), None);
        assert!(
            !duck_ble::adv::has_address_field(&as_advertised),
            "a beacon is not four bytes, so it is not an address field"
        );
    }

    /// The scan filter has to match what the beacon actually broadcasts, byte for byte, or the
    /// controller drops every beat and the failure looks like a radio problem.
    #[test]
    fn the_scan_pattern_matches_what_is_broadcast() {
        let pattern = scan_pattern();
        // The AD field is the little-endian company id followed by the payload.
        let mut field = COMPANY_ID.to_le_bytes().to_vec();
        field.extend(beacon_data(&beacon()));
        assert!(
            field.starts_with(&pattern),
            "pattern {pattern:?} does not prefix the broadcast field {field:?}"
        );
        // Company id first, little-endian, then the tag — the order a controller matches in.
        assert_eq!(pattern, vec![0xFF, 0xFF, ChoraleBeacon::TAG]);
        // An address advertisement must *not* match, or the filter buys nothing.
        let mut address_field = COMPANY_ID.to_le_bytes().to_vec();
        address_field.extend(duck_ble::adv::address_data(None));
        assert!(!address_field.starts_with(&pattern));
    }

    /// Another vendor on the testing company id, or a future beacon this build does not know, is
    /// not a beat. `0xFFFF` is unassigned and anyone may use it.
    #[test]
    fn somebody_elses_payload_is_not_a_beacon() {
        for payload in [vec![], vec![0x01], vec![0xC0], vec![0xC0, 1, 2, 3, 4, 5]] {
            let data = HashMap::from([(COMPANY_ID, payload.clone())]);
            assert_eq!(beacon_in(&data), None, "{payload:?}");
        }
        // A different company id is not ours however well-formed it looks.
        let elsewhere = HashMap::from([(0x004C, beacon().to_bytes())]);
        assert_eq!(beacon_in(&elsewhere), None);
    }

    /// The beacon advertises faster than the front door, and that is only affordable because the
    /// instance is transient. If someone makes it permanent, these numbers are the argument.
    #[test]
    fn the_beacon_is_faster_than_the_front_door() {
        assert!(BEACON_INTERVAL_MIN < BEACON_INTERVAL_MAX);
        // The spec's floor is 20 ms; going under it would be refused by the controller.
        assert!(BEACON_INTERVAL_MIN >= std::time::Duration::from_millis(20));
        // And genuinely faster than the always-on advertisement, or a beat would reach the air no
        // sooner than the robot's name does.
        assert!(BEACON_INTERVAL_MAX < std::time::Duration::from_millis(100));
    }
}

```

### File: `btd/src/lib.rs` (40 lines, ~541 tokens)
```rs
//! `btd` — the BLE front door onto the robot's API.
//!
//! **A transport adapter and nothing else** (`architecture.md` §4.1). `btd` owns no state, and
//! that is load-bearing rather than tidy: if provisioning or config lived here, every other
//! service would depend on `btd`, and an SDK would absurdly have to go through Bluetooth to
//! set a robot's name.
//!
//! So the design is a pipe. A GATT service with one characteristic — written to for requests,
//! subscribed to for answers — carries **the same NDJSON JSON-RPC lines as every other
//! transport** (see [`gatt`] for why one and not two), and `btd`
//! reassembles them, checks the method against [`route`]'s table, forwards them verbatim to
//! the owning service's unix socket, and chunks the replies back. Adding a method to the
//! protocol needs no change here beyond one line in that table.
//!
//! It is also the process that parses bytes from anyone in radio range, which is why it runs
//! unprivileged while `configd` — which only ever sees typed JSON from a peer-credentialled
//! local socket — is the one running as root. Putting the parser on the safe side of that
//! boundary matters more than hardening the dispatcher.
//!
//! ## Layout
//!
//! [`framing`] and [`route`] are pure logic. [`session`] is the whole of the behaviour, and it
//! reaches the radio only through [`link::Link`] — two channels, not a trait — so the tests
//! drive a complete session over real unix sockets with no Bluetooth involved. [`upstream`]
//! holds the connections to the services that own the answers.
//!
//! `net.*` and `system.*` — wifi, name, reboot — go to `configd`, one arm each in [`route`]'s
//! table. The robot's name and its IPv4 address are the two things `btd` reads back rather than
//! only forwarding: both go in the advertisement, so [`bluez`] asks `configd` for them and keeps
//! the advertisement in step. [`adv`] is the layout of the address field, shared with the client
//! that decodes it.

#[cfg(target_os = "linux")]
pub mod bluez;
pub mod chorale;
pub mod link;
pub mod pairing;
pub mod route;
pub mod session;
pub mod upstream;

```

### File: `btd/src/link.rs` (109 lines, ~1367 tokens)
```rs
//! The seam between the radio and everything worth testing.
//!
//! Deliberately **not a trait**. A `GattLink` trait would need an async `recv` and an async
//! `send`, and the session loop has to wait on both at once — which means either splitting the
//! link into halves with associated types, or fighting the borrow checker inside a `select!`.
//! Two channels and a plain struct express the same thing with none of that, and the test
//! constructs one by hand rather than implementing anything.
//!
//! So a backend's whole job is: accept a connection, feed inbound chunks into `inbound`, write
//! whatever appears on `outbound` back to the central, and drop the channels when the central
//! goes away. What happens between those two channels is [`crate::session`], and it never
//! learns whether a radio is involved.

use std::sync::Arc;
use std::sync::atomic::{AtomicUsize, Ordering};

use tokio::sync::mpsc;

/// How many chunks may queue in either direction.
///
/// Sized so that a **maximal inbound line never has to block**, which is a correctness
/// requirement rather than a tuning choice. The radio backend must hand chunks over without
/// awaiting: BlueZ dispatches each write as its own task, so any yield point between receiving a
/// chunk and enqueueing it is a chance for two chunks to swap places — and a reordered chunk
/// silently corrupts a request. Chunk 2 of 3 arriving last once produced
/// `{"id":1,"jsonrpc":"2.info","params":{}}`, which is valid JSON missing a field, and a parse
/// error blaming the client.
///
/// So the queue has to be deep enough that a synchronous `try_send` cannot fail on legitimate
/// traffic: `QUEUE * 20 >= framing::MAX_LINE`, where 20 is the smallest payload BLE guarantees.
/// A test asserts that relationship. Beyond it, a flood gets a clean ATT error rather than a
/// dropped chunk, because failing a write is recoverable and corrupting one is not.
pub const QUEUE: usize = 512;

/// One connected central.
pub struct Link {
    /// Chunks written by the central to the `request` characteristic, in arrival order.
    /// Closed when it disconnects.
    pub inbound: mpsc::Receiver<Vec<u8>>,
    /// Chunks to notify on the `response` characteristic.
    pub outbound: mpsc::Sender<Vec<u8>>,
    /// Usable notification payload — `ATT_MTU - 3` — as negotiated for this connection.
    ///
    /// **A shared cell rather than a number, because the two halves of the link learn it at
    /// different times.** BlueZ reports the negotiated MTU on every inbound write and offers the
    /// notify side no way to ask, so a session begins knowing only the 20-byte floor and learns
    /// the real value from the first write a client makes — which is always `system.authenticate`,
    /// before any reply worth chunking exists. Sizing replies for the floor for the whole session
    /// was a tenfold cost in notifications, and above about 5 KiB it stopped being merely slow:
    /// see the pacing in `bluez`.
    ///
    /// Read once per *line*, never per chunk, which is the invariant that matters — a line chunked
    /// two different ways cannot be reassembled.
    mtu: Arc<AtomicUsize>,
    /// The central's address, for the log line. Never used for authorization — a BLE address
    /// is trivially spoofed, and pairing is what authorizes (`architecture.md` §4.2).
    pub peer: String,
}

impl Link {
    /// A link wired to channels the caller drives, with a payload size that never changes.
    /// Used by tests and by `--fake`.
    pub fn pair(
        mtu: usize,
        peer: impl Into<String>,
    ) -> (Self, mpsc::Sender<Vec<u8>>, mpsc::Receiver<Vec<u8>>) {
        Self::pair_sharing_mtu(Arc::new(AtomicUsize::new(mtu)), peer)
    }

    /// A link whose payload size is written by somebody else — the radio backend, from what
    /// BlueZ reports on each inbound write. See [`Link::mtu`].
    pub fn pair_sharing_mtu(
        mtu: Arc<AtomicUsize>,
        peer: impl Into<String>,
    ) -> (Self, mpsc::Sender<Vec<u8>>, mpsc::Receiver<Vec<u8>>) {
        let (to_robot, inbound) = mpsc::channel(QUEUE);
        let (outbound, from_robot) = mpsc::channel(QUEUE);
        (
            Self {
                inbound,
                outbound,
                mtu,
                peer: peer.into(),
            },
            to_robot,
            from_robot,
        )
    }

    /// The payload to size the next outbound line for.
    pub fn mtu(&self) -> usize {
        self.mtu.load(Ordering::Relaxed)
    }
}

/// The queue must be deep enough that a maximal line never needs a blocking send.
///
/// A compile-time check rather than a test, because it is a relationship between two constants
/// and nothing about it can be true at runtime and false at build time. 20 bytes is the payload
/// every BLE link is required to support, and therefore the smallest chunk a client may use.
///
/// This is the invariant behind the radio backend using a synchronous `try_send`: it may not
/// await, because a yield point between receiving a chunk and enqueueing it lets two chunks swap
/// places, and a reordered chunk corrupts a request rather than failing it.
const _: () = assert!(
    QUEUE * 20 >= duck_ble::framing::MAX_LINE,
    "QUEUE * 20 must be at least framing::MAX_LINE, or a full-length request can fill the \
     inbound queue and be refused"
);

```

### File: `btd/src/main.rs` (189 lines, ~2091 tokens)
```rs
//! `btd` — the BLE front door onto the robot's API.
//!
//! Runs only on the robot. See the crate docs in `lib.rs` for what it is and why it owns
//! nothing; this file is argument parsing, logging and startup.

use std::path::PathBuf;
use std::process::ExitCode;

use btd::upstream::{NameChoice, Sockets};
use clap::Parser;

#[derive(Parser, Debug)]
#[command(
    version,
    about = "BLE transport adapter for the robot API",
    long_about = "Serves a GATT service that carries the same JSON-RPC lines as every other \
                  transport, forwarding each request to the service that owns it. Exposes a \
                  subset: status, update trigger and progress. Never motor control."
)]
struct Args {
    /// `updaterd`'s socket.
    #[arg(long, default_value = duck_ipc_proto::socket::UPDATER)]
    update_socket: PathBuf,

    /// `robotd`'s socket.
    #[arg(long, default_value = duck_ipc_proto::socket::ROBOT)]
    robot_socket: PathBuf,

    /// `configd`'s socket — wifi and the robot's identity.
    #[arg(long, default_value = duck_ipc_proto::socket::CONFIG)]
    config_socket: PathBuf,

    /// Require a paired, encrypted link.
    ///
    /// **Off by default, and that is not where this ends up.** Requiring pairing makes the version
    /// read hang on macOS — CoreBluetooth issues the Read Request, BlueZ refuses it for insufficient
    /// encryption, and nothing resolves it — so a robot serving the secure configuration cannot be
    /// talked to at all (`docs/design/app-path-design.md` §5.5).
    ///
    /// Between a default that is secure and unusable and one that works and is insecure, this is
    /// pre-shipping development tooling and the usable one wins. The cost is real and unhedged:
    /// with pairing off, anyone in radio range can read the PIN as it crosses and write any allowed
    /// request — including `net.connect`, which carries a wifi passphrase. Every robot running this
    /// is a robot whose wifi credentials are readable by a bystander.
    ///
    /// This must flip before anything is handed to anyone. §8.1 is the blocker.
    #[arg(long)]
    require_pairing: bool,

    /// Accepted and ignored: not requiring pairing is now the default.
    ///
    /// Kept only so a board carrying a `--insecure-no-pairing` drop-in — which is how the flag was
    /// used while it existed — does not fail to start on the update that removes it. An unknown
    /// argument would take BLE down on exactly the boards that were using it.
    #[arg(long, hide = true)]
    insecure_no_pairing: bool,

    /// Pin the advertised name, instead of asking `configd` what the robot is called.
    ///
    /// Bench use. The name someone sees in a phone's Bluetooth list is `configd`'s — set with
    /// `robotctl system set-name` or `system.setName` from an app — and passing this stops it being
    /// reconciled, so a rename no longer takes effect until the flag is removed.
    #[arg(long)]
    name: Option<String>,
}

fn hostname() -> String {
    // /etc/hostname rather than the `hostname` crate or a libc call: one file read, no
    // dependency, and it is what the board is actually configured with.
    std::fs::read_to_string("/etc/hostname")
        .map(|s| s.trim().to_owned())
        .ok()
        .filter(|s| !s.is_empty())
        .unwrap_or_else(|| "robot".to_owned())
}

/// **Single-threaded on purpose**, which `bluer`'s own examples also do.
///
/// A chunked request arrives as several `WriteValue` calls, and `dbus-crossroads` dispatches each
/// as its own task. On a multi-threaded runtime those tasks can be invoked out of order, and a
/// reordered chunk does not fail — it reassembles into something that parses as the wrong thing.
/// `{"id":1,"jsonrpc":"2.0","method":"system.info","params":{}}` arriving as chunks 1, 3, 2 becomes
/// `{"id":1,"jsonrpc":"2.info","params":{}}`: valid JSON, missing a field, and a parse error that
/// blames the client. It cost two rounds of debugging on hardware.
///
/// On one thread the dispatcher invokes handlers in the order it reads them off the D-Bus socket,
/// which is the order the client sent them — and the client acknowledges each write before sending
/// the next, so that order is well-defined.
///
/// Affordable because this daemon does no CPU work: it moves bytes between a radio and three unix
/// sockets. Anything blocking added later would stall the whole service, which is a reason to keep
/// it that way rather than an argument against it.
#[tokio::main(flavor = "current_thread")]
async fn main() -> ExitCode {
    tracing_subscriber::fmt()
        .with_env_filter(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| tracing_subscriber::EnvFilter::new("info")),
        )
        .with_writer(std::io::stderr)
        .init();

    let args = Args::parse();
    duck_ipc_proto::log_startup_identity!("btd");

    let sockets = Sockets {
        updater: args.update_socket,
        robot: args.robot_socket,
        config: args.config_socket,
    };
    // The hostname is only a last resort now: `configd` derives a distinguishable default from the
    // board's SoC serial, so `radxa-zero3` appears only when `configd` cannot be reached at all.
    let name = NameChoice {
        pinned: args.name,
        fallback: hostname(),
    };

    if args.insecure_no_pairing {
        tracing::warn!(
            "--insecure-no-pairing is now the default and does nothing; remove it from the unit"
        );
    }
    if !args.require_pairing {
        // Loud, every start, because the whole point of choosing the usable default is that the
        // insecurity stays visible rather than becoming the thing nobody remembers.
        tracing::warn!(
            "serving WITHOUT pairing: the PIN and any wifi passphrase cross this link in clear, \
             readable by anyone in range. Development only — see app-path-design.md §5.5"
        );
    }

    run(sockets, name, args.require_pairing).await
}

#[cfg(target_os = "linux")]
async fn run(sockets: Sockets, name: NameChoice, require_pairing: bool) -> ExitCode {
    tokio::select! {
        // `serve` retries the radio in place and is not expected to return at all: an adapter that
        // is missing, unpowered or wedged is handled there rather than by dying and letting
        // `Restart=always` do it. Both arms are therefore a bug in `serve`, not a radio fault — kept
        // because the signature allows them, and non-zero because a `btd` that has stopped serving
        // BLE must not look healthy.
        result = btd::bluez::serve(sockets, name, require_pairing) => match result {
            Ok(()) => {
                tracing::error!("the BLE service returned; it is supposed to retry instead");
                ExitCode::FAILURE
            }
            Err(e) => {
                tracing::error!(error = %e, "BLE service failed");
                ExitCode::FAILURE
            }
        },
        () = shutdown() => {
            tracing::info!("shutting down");
            ExitCode::SUCCESS
        }
    }
}

/// Off-Linux this daemon has nothing to serve, and says so rather than pretending.
///
/// The crate still builds and tests here, which is the point: `cargo test` on a laptop is the
/// onboarding path, and only the radio is Linux-only.
#[cfg(not(target_os = "linux"))]
async fn run(_sockets: Sockets, _name: NameChoice, _require_pairing: bool) -> ExitCode {
    tracing::error!(
        "btd needs BlueZ, which is Linux-only. This binary exists here so the crate builds \
         and its tests run; it cannot serve BLE on this platform."
    );
    ExitCode::FAILURE
}

/// Resolve on SIGTERM (systemd stop) or SIGINT (Ctrl-C).
#[cfg(target_os = "linux")]
async fn shutdown() {
    use tokio::signal::unix::{SignalKind, signal};

    let mut term = match signal(SignalKind::terminate()) {
        Ok(s) => s,
        Err(e) => {
            tracing::warn!(error = %e, "cannot listen for SIGTERM");
            return std::future::pending().await;
        }
    };
    tokio::select! {
        _ = term.recv() => {}
        _ = tokio::signal::ctrl_c() => {}
    }
}

```

### File: `btd/src/pairing.rs` (192 lines, ~2434 tokens)
```rs
//! Who is allowed to talk to this robot over BLE.
//!
//! §4.2 says BLE authorisation is "physical presence + pairing", and §7 requires the
//! characteristic carrying wifi credentials to be paired and encrypted. Both hold — but the PIN
//! check lives **above** the link layer, and that is forced rather than chosen.
//!
//! ## Why BLE could not do this
//!
//! The first design had the robot answer BlueZ's passkey request with its stored PIN. That cannot
//! work on a headless robot. In LE passkey entry one side *displays* a passkey and the other
//! *inputs* it, and the roles follow from the IO capabilities each side declares. Implementing
//! `request_passkey` declares "this device can input", so macOS took the display role, generated a
//! random six-digit code, and waited for someone to type it into a robot with no keyboard.
//!
//! The reverse fails too: with `DisplayPasskey` the robot takes the display role, but **BlueZ
//! generates the passkey** — the spec has the displaying side choose it at random. A fixed PIN
//! printed on a sticker is simply not expressible in BLE passkey entry.
//!
//! ## So: just-works pairing, plus a PIN the transport checks
//!
//! Pairing is just-works (all agent handlers `None`, which BlueZ reads as `NoInputNoOutput`), so
//! the link is encrypted but **not** authenticated. The read on the RPC characteristic requires
//! encryption, which is what triggers the bond. Then `btd` serves nothing until the client proves
//! the PIN via `system.authenticate`, which is why that call is answered by the transport rather
//! than forwarded.
//!
//! The cost, stated plainly: the PIN crosses an encrypted-but-unauthenticated link, so an attacker
//! present *at the moment of pairing* could capture it. The alternatives were no authentication at
//! all, or an out-of-band QR flow that BlueZ barely supports and no phone app exists to drive. For
//! a robot in a home this is the better trade, and it is revisitable without touching the
//! transport, because the check is ours now rather than the spec's.
//!
//! **The factory PIN is `000000` and everyone can read it in this repository.** So out of the box
//! this proves physical presence and nothing more, which is the same guarantee just-works pairing
//! gives — the difference being that the mechanism, the storage and the six-digit contract are
//! all in place, so making it a real secret is a provisioning change rather than a redesign. A
//! per-robot PIN printed under the robot is what turns this into security, and that is
//! `updater-design.md` §5.7's per-device state.
//!
//! ## No pairing window, and that is decided rather than deferred
//!
//! The robot is pairable whenever it advertises. A physical button-held window is the usual
//! answer, and it was considered and rejected: a **per-robot PIN already carries the property a
//! window would add.** If the PIN is unique and printed under the robot, knowing it requires
//! physical access — and anyone who can read the sticker can also pick the robot up. A window
//! would defend only against someone in range while the factory default is still in place, and
//! the answer to that is a real PIN, not a button.
//!
//! What a button would buy beyond this: a visible consent moment, a recovery path when the PIN is
//! lost, and defence in depth if a sticker is photographed. None is needed for v1, and each is
//! additive later — an enclosure with a button can gate `set_pairable` without changing anything
//! here.
//!
//! So the security of this rests entirely on the PIN being per-robot, which makes it a
//! provisioning obligation rather than a software one: something has to generate it, print it and
//! record what was printed. The robot does now have a per-device identity — `configd::identity`
//! derives one from the SoC serial — but a PIN cannot be derived from it, and that is worth stating
//! rather than rediscovering: the identity is *published*, in an advertisement anyone in range can
//! collect, so a PIN computed from it would be public the moment the derivation is known. Only the
//! name hangs off the identity. A secret still has to be generated, printed and recorded, which is
//! `updater-design.md` §5.7's per-device state.
//!
//! Still open, and smaller: **no bond management.** Every paired phone stays paired and nothing
//! revokes one; `bluetoothctl untrust` is the manual escape until there is an API for it.

use std::time::Duration;

use duck_ipc_proto as proto;

/// How long to wait for `configd` to answer with the PIN.
///
/// Short: BlueZ is holding a pairing exchange open, and a phone shows a spinner while we decide.
/// If `configd` cannot answer in this long it is not going to.
const PIN_TIMEOUT: Duration = Duration::from_secs(3);

/// Ask `configd` for the pairing PIN.
///
/// Fetched **per pairing request** rather than cached at startup, so `robotctl system set-pin`
/// takes effect on the next pairing rather than the next reboot. One socket round-trip during an
/// exchange that already takes a human several seconds.
///
/// Returned whole rather than parsed: the comparison is on the string, because `000042` and `42`
/// are different PINs and a numeric parse would make them the same. `is_default` comes with it so
/// the caller can say out loud that a factory PIN authenticates anyone who read this repository.
///
/// The PIN is never logged. It is barely a secret today, but a per-robot one is meant to be, and
/// the journal is the wrong place for it.
pub async fn pin(config_socket: &std::path::Path) -> Result<proto::PairingPinResult, String> {
    crate::upstream::ask(
        "configd",
        config_socket,
        &proto::Call::SystemPairingPin,
        PIN_TIMEOUT,
    )
    .await?
    .result_as()
    .map_err(|e| e.to_string())
}

#[cfg(test)]
mod tests {
    use super::*;
    use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader};

    /// A PIN with leading zeros must reach BlueZ as the right *number*, since that is the only
    /// form a passkey has on the wire.
    #[test]
    fn a_pin_with_leading_zeros_is_the_right_passkey() {
        for (pin, expected) in [
            ("000000", 0u32),
            ("000042", 42),
            ("123456", 123456),
            ("999999", 999999),
        ] {
            assert_eq!(pin.parse::<u32>().unwrap(), expected, "{pin}");
        }
    }

    /// A missing `configd` must be a reported error rather than a hang: BlueZ is holding a
    /// pairing exchange open, and a phone waiting forever is worse than a refused bond.
    #[tokio::test]
    async fn an_absent_configd_fails_rather_than_hanging() {
        let dir = tempfile::tempdir().unwrap();
        let err = pin(&dir.path().join("absent.sock")).await.unwrap_err();
        assert!(err.contains("cannot reach configd"), "{err}");
    }

    /// The whole path, over a real socket: a fake configd answers and the PIN becomes a passkey.
    #[tokio::test]
    async fn the_pin_is_fetched_over_the_socket() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("configd.sock");
        let listener = tokio::net::UnixListener::bind(&path).unwrap();

        tokio::spawn(async move {
            let (stream, _) = listener.accept().await.unwrap();
            let (read, mut write) = stream.into_split();
            let mut lines = BufReader::new(read).lines();
            let request = lines.next_line().await.unwrap().unwrap();
            // The request must be the PIN method and nothing else.
            assert!(
                request.contains(proto::method::SYSTEM_PAIRING_PIN),
                "{request}"
            );

            let response = proto::Response::ok(
                Some(proto::Id::Number(1)),
                &proto::PairingPinResult {
                    pin: "000042".into(),
                    is_default: false,
                },
            );
            let mut line = serde_json::to_vec(&response).unwrap();
            line.push(b'\n');
            write.write_all(&line).await.unwrap();
            write.flush().await.unwrap();
        });

        let result = pin(&path).await.unwrap();
        // Compared as a *string*, so a leading zero is part of the secret rather than lost to a
        // numeric parse. `000042` and `42` must not be the same PIN.
        assert_eq!(result.pin, "000042");
        assert!(!result.is_default);
    }

    /// A refusal from `configd` is reported, not swallowed into a default passkey — which would
    /// silently let anyone pair with `000000`.
    #[tokio::test]
    async fn a_refusal_is_not_treated_as_a_default_pin() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("configd.sock");
        let listener = tokio::net::UnixListener::bind(&path).unwrap();

        tokio::spawn(async move {
            let (stream, _) = listener.accept().await.unwrap();
            let (read, mut write) = stream.into_split();
            let mut lines = BufReader::new(read).lines();
            let _ = lines.next_line().await;
            let response = proto::Response::err(
                Some(proto::Id::Number(1)),
                proto::Error::new(proto::code::PERMISSION_DENIED, "nope"),
            );
            let mut line = serde_json::to_vec(&response).unwrap();
            line.push(b'\n');
            write.write_all(&line).await.unwrap();
            write.flush().await.unwrap();
        });

        let err = pin(&path).await.unwrap_err();
        assert!(err.contains("refused"), "{err}");
    }
}

```

### File: `btd/src/route.rs` (1020 lines, ~13628 tokens)
```rs
//! Which calls BLE may make, and which of a service's connections carries them.
//!
//! BLE exposes a **subset** of the robot API (`architecture.md` §4.1): provisioning, status,
//! and the update commands with their progress. It is too slow and too constrained for the full
//! surface, and — more to the point — a radio anybody within a few metres can talk to is not
//! the transport over which to offer "reset this robot to factory state".
//!
//! **Two questions, and only one of them is BLE's.** *Which service answers a call, and how long
//! answering holds a connection* is a property of the call, and lives in
//! [`proto::Call::destination`] where every transport reads the same answer. *Whether BLE may make
//! it* is this file. They were one table until a second transport needed the first half and none
//! of the second; `docs/design/remote-webrtc.md` §5 records the split.
//!
//! **The permission match is deliberately exhaustive.** Adding a variant to [`proto::Call`] makes
//! this file fail to compile, so a new method cannot reach the radio because someone forgot this
//! file existed. A `_ => false` wildcard would be the safe default in the moment and the wrong one
//! over time: it would silently deny new methods, and the first symptom would be a phone app that
//! cannot see a feature nobody remembered to route. Every transport needs its own such match for
//! the same reason — a shared one with a wildcard would be the hole in all of them at once.

use duck_ipc_proto as proto;

/// How long a call holds a connection. Defined once, in the protocol crate.
pub use proto::Lane;

/// The service that owns the answer to a call, restricted to the three `btd` holds sockets to.
///
/// Narrower than [`proto::Service`] on purpose. `padd` and `tofd` answer calls too, and `btd` has
/// no connection to either: `padd` is the unprivileged client whose whole value is having no
/// special access, and giving the BLE transport a socket to it would be the first thing to make
/// that untrue. The conversion below therefore *fails* for them, which turns a comment into
/// something the compiler enforces.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum Upstream {
    /// `updaterd`, at `proto::DEFAULT_SOCKET`.
    Updater,
    /// `robotd`.
    Robot,
    /// `configd` — wifi and the robot's identity.
    Config,
}

impl TryFrom<proto::Service> for Upstream {
    type Error = ();

    fn try_from(service: proto::Service) -> Result<Self, Self::Error> {
        match service {
            proto::Service::Updater => Ok(Upstream::Updater),
            proto::Service::Robot => Ok(Upstream::Robot),
            proto::Service::Config => Ok(Upstream::Config),
            // Not sockets `btd` holds. Unreachable in practice, because `permits` refuses every
            // call these answer — and an error rather than a panic so that staying true is not
            // something this file has to be careful about.
            proto::Service::Pad | proto::Service::Tof => Err(()),
        }
    }
}

/// What happens to a call that arrives over BLE.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Route {
    /// Forwarded verbatim to a service, on that service's connection for this lane.
    To(Upstream, Lane),
    /// Answered by `btd` itself. Only `system.authenticate`: the PIN check belongs to the
    /// transport, because BLE cannot express a fixed printed passkey and the check therefore had
    /// to move up a layer (`docs/design/app-path-design.md` §5).
    Local,
    /// Not available over this transport.
    Refused,
}

/// May a call arriving over BLE be served at all?
///
/// Read the `false` arms as the security boundary: each one is a deliberate decision that a
/// phone in the room does not get to do this.
fn permits(call: &proto::Call) -> bool {
    use proto::Call::*;
    match call {
        // The version handshake. Must be reachable or no client can establish anything.
        Hello(_) => true,

        // Answered by `btd` itself rather than forwarded. Permitted because it is the one call a
        // session must be able to make before it has made any other.
        SystemAuthenticate(_) => true,

        // ── the update subset §4.1 names ────────────────────────────────────
        //
        // `Apply` is intended: BLE implies physical presence plus pairing (§4.2), and "update
        // the robot from the phone" is M6's headline. It also has to pass `updaterd`'s own peer
        // policy, and does — `deploy/updater.toml` names `btd` in `allow_users`, which is a
        // narrower claim than granting the robot group. Routing it here without that grant would
        // have produced a phone button that always returned PERMISSION_DENIED.
        Apply(_) => true,
        Check(_) => true,
        Status => true,
        Subscribe => true,
        // Read-only, and what support asks for first. `update.log` is the record that
        // survives a wiped journal (§8.2), so a phone able to read it is worth having.
        Log(_) => true,
        // The detail behind one of those log lines, and the same claim: read-only, and the
        // question an owner whose update failed actually has. Bigger than every other reply here
        // — a few kilobytes for an ordinary run, since `hooks::MAX_OUTPUT` bounds the largest
        // part of it, against a `updater::transcript` ceiling of two megabytes for a pathological
        // one — so an app should ask for it on a tap rather than on a refresh. That is the app's
        // decision to make: what this function decides is whether a phone in the room may see it,
        // and a phone that may read the log may read what is behind it.
        Show(_) => true,
        ListInstalled(_) => true,

        // Going back. Both are permitted, and both are less consequential than the `Apply`
        // above them: they move the robot to a release that has already run on this board,
        // download nothing, and are gated and auto-reverted like any other transition
        // (`Engine::rollback` and `Engine::select` both go through `transition_to`).
        //
        // They were refused until the update path was driven from a phone, on the reasoning that
        // the engine reverts a bad release on its own. It does — the one that fails its health
        // gate. That is not the case an owner reaches for a phone about, which is a release that
        // installs, passes its gate, and then behaves *worse*: a policy that walks unsteadily
        // rather than not at all, a pad that stops reconnecting. Nothing reverts that but a
        // person, and the person is holding a phone and has no ssh.
        //
        // `Rollback` is the undo — the previous release, no arguments, one tap. `Select` is the
        // same authority plus a version number, and it is what a list of installed releases is
        // *for*: `ListInstalled` is already routed above, so an app can show them, and being able
        // to show them without being able to choose one would be the odd half.
        Rollback(_) => true,
        Select(_) => true,

        // Is the robot alright? The one `robot.*` call an app has any use for.
        RobotHealth => true,

        // ── provisioning, which is what §4.1 puts BLE here for ──────────────
        //
        // This is the case the whole transport exists to serve: a robot that has never seen a
        // network cannot be configured over that network, so BLE is the only way in. All four
        // are permitted, including the two that change things.
        NetStatus => true,
        NetScan => true,
        // Carries a wifi passphrase, and this arm used to claim that travels over a paired,
        // authenticated link. It does not, and the claim was wrong in both halves.
        //
        // The characteristic sets `encrypt_write`, not `encrypt_authenticated_write`
        // (`crate::bluez`) — and it sets it from `--require-pairing`, which is **off by default**,
        // so on an ordinary board there is no encryption on this link at all. Nor could the
        // stronger flag be satisfied if it were set: the agent leaves every handler `None`, which
        // BlueZ publishes as `NoInputNoOutput`, so the bond is just-works and therefore encrypted
        // but *unauthenticated*. `crate::pairing` records why a headless robot cannot do better,
        // and `docs/design/app-path-design.md` §5.5 is the state of it.
        //
        // So what actually stands behind this route today is the PIN check in `crate::session` and
        // the ten metres of radio range, and the passphrase crosses in clear. That is a known,
        // accepted, pre-shipping cost — `btd` warns about it at every start — and §8.1 is the
        // blocker that has to close before a robot goes to anyone. Routed anyway because a robot
        // with no network cannot be given one any other way, which is what this transport is for.
        NetConnect(_) => true,
        NetForget(_) => true,

        // Name and identity. Renaming from the app is the reason `system.setName` exists.
        SystemInfo => true,
        SystemSetName(_) => true,

        // Which daemons are up and which release each is running. Routed because an app that can
        // trigger an update should be able to show whether it took — and because the one daemon it
        // cannot report on this way is `btd` itself, which answering at all proves is running.
        SystemServices => true,

        // The tail of one daemon's journal, and the next question after the line above: a unit
        // reported as `failed` is a diagnosis nobody can act on without the reason it failed.
        //
        // Permitted because BLE is where the question is asked. A robot with no network cannot be
        // reached by ssh, and that robot — one whose wifi never came up, whose `robotd` died on
        // boot — is exactly the one whose journal somebody needs. Refusing here would mean the
        // logs are readable over every transport except the one available when things are broken.
        //
        // Read-only, and bounded on the other side rather than trusted: `configd` picks the unit
        // from a fixed list and refuses anything else, so this grants "the tail of a daemon this
        // project ships", not `journalctl`. What a phone in the room learns is what that phone
        // could already learn by watching the robot fail, in words it can put in a support ticket.
        //
        // The one thing worth naming as a cost: a journal line can carry more than a status. Ours
        // are reviewed for that where it matters — `net.connect`'s passphrase is redacted by a
        // hand-written `Debug` with a test pinning it (`proto::NetConnectParams`) — and this
        // routing is the second reason that redaction is load-bearing rather than tidy.
        SystemLogs(_) => true,

        // Rebooting is drastic but recoverable, and it is what an app offers when a robot is
        // confused — the alternative being "unplug it", which for a walking robot is worse.
        // Unlike `resetToGolden` it discards nothing.
        SystemReboot => true,

        // ── the gamepad ─────────────────────────────────────────────────────
        //
        // Pairing a controller from the phone, which is where it belongs: whoever is holding the
        // robot is holding the pad, and the alternative is an ssh session. The same physical-presence
        // argument §4.2 makes for `net.connect` covers it — a pad has to be in the room, in pairing
        // mode, in a fifteen-second window — and it is `configd` that does the work either way.
        //
        // `pad.pair` is the more consequential of the two, because a bonded pad can enable the
        // policy afterwards. That is deliberate: it is the same authority as standing next to the
        // robot with a controller, and the PIN gate is what stands in front of it.
        PadStatus => true,
        PadPair(_) => true,
        PadForget(_) => true,

        // ── refused ─────────────────────────────────────────────────────────

        // The pairing PIN, and the one refusal in this file that is load-bearing rather than
        // conservative: a PIN readable by an unpaired peer authorises nothing at all. `btd`
        // reads it over the unix socket to answer BlueZ's passkey request, and BLE never can.
        SystemPairingPin | SystemSetPairingPin(_) => false,

        // Pinning, and it stays refused while `Select` above it does not. The difference is what
        // the mistake looks like afterwards: a wrong `select` is one release away from being
        // undone and the robot says which release it is on, whereas a robot pinned by a mistap
        // refuses every later update and reports itself as up to date. That is the one failure
        // here that looks exactly like correct behaviour, and it needs `robotctl` and a person
        // who meant it.
        Pin(_) => false,

        // Factory reset in all but name: back to the golden image, discarding every release
        // since. Never over a radio — and note that `Rollback` and `Select` being routed does
        // not weaken this, because neither discards anything.
        ResetToGolden(_) => false,

        // `updaterd`'s private questions to `robotd` — may I restart the control loop, which
        // model API is this, is a telepresence session live. Internal plumbing of the update
        // decision, of no use to a client and misleading if exposed: a phone reading
        // `safeToRestart` would learn nothing it could act on.
        RobotSafeToRestart | RobotModelApi | RobotRemoteSessionActive => false,

        // Teleop. **Never over BLE**, which is what §4.1 means by a subset: BLE is too slow and
        // too constrained for the full surface, and teleop belongs on WebRTC's datachannel
        // (`docs/design/remote-webrtc.md` §2). A 20-byte notification budget and a link that does
        // not exist for the first ~73s of a boot is not a control transport. The body pose and
        // the mouth ride with it: all of these are a stream of small updates, and the argument is
        // about the stream, not about any one of them.
        RobotMove(_) | RobotHead(_) | RobotLook(_) | RobotPose(_) | RobotMouth(_) => false,

        // **Not teleop either, and it sat in that group for the same reason a skill did**: it was
        // next to them in a match arm rather than because anybody argued it belonged. It is one
        // request — start driving, or stop — not fifty a second, so the notification budget and
        // the latency argument above do not reach it.
        //
        // What makes it necessary is what `robot.init` alone turned out not to do. Standing a
        // robot up is the *first* of the two things the gamepad's Start button does; the second
        // is this, and without it the app could stand a robot up and then be told by every skill
        // it asked for that the policy is not driving — press Start on the pad. Half a path is
        // worse than none, because it looks like the whole one until it stops.
        //
        // `toggle` rather than a state this side chose: `padd` keeps no belief about whether the
        // policy is driving, for the reason its own comment gives — a local on/off drifts from
        // the robot's the moment anything else moves it, and a stale belief turns the button into
        // one that does nothing every other press. The robot owns the state and names the one it
        // ended in, so a client shows the answer instead of predicting it.
        RobotEnable(_) => true,

        // **A skill is not teleop**, and it sat in that group for longer than it deserved. It is
        // one request — "do the bow" — not fifty a second, so the notification budget and the
        // latency argument above simply do not reach it. Nor does it need a control link at all:
        // the deadman zeroes the twist by itself, so a robot with nothing driving it stands still
        // and bows.
        //
        // What the refusals in this file mostly turn on is who is *watching*, and BLE answers
        // that better than anything else here does — the radio reaches about ten metres, so a
        // phone that can send this is in the room with the robot by construction. It is also the
        // authenticated transport: the characteristic takes `encrypt_authenticated_write` and the
        // bond is PIN-checked, which WebRTC has no equivalent of (`remote-webrtc.md` §4).
        //
        // Which skills a robot has is config, so a client asks `robot.policies` rather than
        // assuming a list; an unknown name is refused with the names it does know.
        RobotDo(_) => true,

        // Harmless and rather charming from a phone — but it rides the same refusal as the
        // rest of robot.* until the app path exists to want it: opening one call to the
        // radio ahead of a client that can use it buys nothing and widens the surface.
        //
        // The theremin sits here rather than with motor control even though it moves the
        // mouth, because what it is is a sound: the mouth is following the note. Same
        // refusal either way, and the same reason to lift it — an app that can play the duck.
        RobotSound(_) | RobotTheremin(_) | RobotChorale(_) => false,

        // The chorale's own namespace is between `btd` and `robotd` — it is how this daemon is told
        // what to advertise and how it reports what it heard. Not a client surface at all, so a
        // phone asking for it is asking for something that does not exist for it.
        ChoraleSubscribe | ChoraleBeaconSet(_) | ChoraleHeard(_) => false,

        // Powering the machine off from a phone in the room is `system.reboot` without the
        // coming back. The sit-then-power-off flow wants whoever asked to be watching the
        // robot, and that is `robotctl` or the pad's long-press, deliberately.
        RobotShutdown => false,

        // Only a stick-mapping hint for local clients like `padd`. An app gets the same answer
        // through `system.info` territory when it ever needs one; no reason to open another read
        // to the radio today.
        RobotMode => false,

        // Switching modes means the robot goes home, loads other policies and drives differently
        // — and the reason to switch is that somebody just put wheels on it. That is a decision
        // made in the room, holding the pad, the same place `robot.shutdown` is refused for.
        RobotSetMode(_) => false,

        // Loading a policy is `robot.setMode` with a wider blast radius: it puts an arbitrary
        // `.onnx` in charge of fifteen servos, and that file can come from a stranger on the Hub.
        // Everything that makes it survivable — the shape gate, the clamps, the fall reflex — is
        // unchanged whoever asked, so this was never about danger; it was that trying a gait
        // means watching the robot try it, and there was no client that did.
        //
        // Both halves have since turned. There is a client, and BLE is the transport that best
        // meets the watching condition: ten metres of radio range means whoever tapped it is
        // looking at the robot, and the bond is PIN-authenticated. A load that fails keeps the
        // controller that was running, so the failure mode is "nothing happened", not "gaitless
        // robot on the floor".
        //
        // **This method persists.** `robotd` writes the slot key into `robotd.toml` before it
        // queues the swap, so a gait chosen from a phone is the gait the robot boots into. It
        // used to be `robotctl`'s half alone, which made the command and the method the same
        // words with different durability depending on who asked — the ephemeral "try it until
        // reboot" mode `policy-channel-design.md` §3 rejected, arrived at by accident.
        //
        // So this is a durable remote change, like `pad.bind` below, and belongs on the
        // PIN-bonded transport for that reason as much as for the watching one. Undoing it is
        // `robot.loadPolicy` with no path, which is reachable from the same phone.
        RobotLoadPolicy(_) => true,

        // Which button runs which skill, and changing one. **This is the transport those exist
        // for**: `robotctl pad bind` is for whoever is holding the robot, and a phone that can
        // already ask for a skill is the obvious place to decide which button asks for it.
        //
        // `pad.bind` writes the config file, and has to: `padd` re-reads `[pad]` every second,
        // so a binding held in memory would be reverted before the caller let go of the phone.
        //
        // A name is checked against the skills this robot has before anything is written, so the
        // failure mode is a refusal naming them rather than a button that does nothing.
        PadBindings | PadBind(_) => true,

        // The skill table: what this robot can be asked to do, and adding to it. The last thing
        // in the policy path that only a terminal on the robot could reach — `[[policy.skill]]`
        // is a repeating table, so `robotctl policy add` wrote it directly and there was nothing
        // to route.
        //
        // `robotd` writes the file and reloads itself, so one call is the whole operation. A
        // client that had to remember a second one and forgot would leave a robot whose config
        // and behaviour disagree until the next restart.
        RobotSkills | RobotSetSkill(_) | RobotRemoveSkill(_) => true,

        // What each slot is running, and which skills this robot has. Read-only, and the read a
        // client makes before it can offer either of the two above: there is no compiled-in list
        // of skills to assume any more, so this is how a phone knows there is a bow to ask for.
        RobotPolicies => true,

        // Static geometry, read-only; the same class of read as the one above.
        RobotModel => true,

        // Re-reading the slots after something else edited the config. Same blast radius as
        // `robot.loadPolicy` and the same answer, and a client that can load wants this for the
        // case where the file changed underneath it.
        RobotReloadPolicies => true,

        // Is there a newer official policy set, and what else is on the Hub. Both reach the
        // network, and neither changes anything on the robot — the same kind of question as
        // `update.check`, which has been routed here since the update path was driven from a
        // phone.
        //
        // They were refused on the grounds that answering "yes, there is a newer gait" for a
        // client that could not then install one is an odd thing to offer. That was fair while it
        // was true and stops being an argument the moment `policy.install` is routed, which is
        // the next arm.
        PolicyCheck | PolicySearch(_) => true,

        // And installing one. This is the most obviously *appealing* thing in this file: a
        // stranger's gait, from a phone, onto the robot in front of you.
        //
        // What makes it survivable is unchanged and was always the point — the manifest gate
        // before the download, the shape gate at load, the joint clamps, the fall reflex — so
        // this was never about danger. It was about who is *watching*, and BLE answers that
        // better than anything else here: ten metres of radio range means whoever tapped it is
        // looking at the robot, and the bond is PIN-checked.
        //
        // `policy.install` is `is_mutating`, so `updaterd` authorises it against the peer's
        // uid — which is `btd`'s, not the phone's, exactly as it already is for `update.apply`.
        // The transport is the gate here, not the credential.
        PolicyFetch(_) | PolicyInstall(_) => true,

        // The detector's set, by the same argument: a read that reaches the network, and an
        // install whoever tapped it is standing next to.
        DetectorCheck | DetectorInstall(_) => true,

        // ── the account, which BLE is the right transport for ────────────────
        //
        // Signing the robot in to a Hugging Face account is what makes it reachable from outside
        // the LAN at all, and this is the transport that should carry it — for the reason
        // `remote-webrtc.md` §4 gives about BLE generally: it is PIN-bonded, and ten metres of
        // radio range means whoever tapped the button is in the room with the robot.
        //
        // It also happens to be the *only* transport that can do it on a robot fresh out of a
        // box. A duck with no wifi has no console to open and no LAN to open it from, and BLE is
        // already how such a robot is given a network — so a wizard that joins the wifi and then
        // signs the robot in is one flow on one transport, which is what the mini's app does.
        //
        // The code the flow produces has to be *read by a person*, so the reply carrying it is
        // the point: this call sends about eighty bytes back, well inside what framing chunks,
        // and needs no link at all while the user is off approving it — see
        // `duck_ipc_proto::API_VERSION`'s v23 note on why `login` answers with a code and not
        // with a token. That is what makes an iPhone dropping the GATT link mid-flow a
        // non-event rather than a lost login.
        AccountLogin(_) | AccountStatus | AccountLogout => true,

        // **Standing the robot up, which is how anything else here starts.**
        //
        // Refused until the phone app was used, on the grounds that standing a robot up moves
        // every joint at once and wants the person doing it to be looking at the robot rather
        // than at a screen. The second half of that is the argument this file makes *for*
        // routing things — ten metres of radio range means whoever tapped it is looking at the
        // robot — and it is what lets `robot.do`, `robot.loadPolicy` and `policy.install`
        // through. It was never a reason to refuse this one.
        //
        // What made it worth changing is what the refusal cost: a robot that has not been
        // started ignores every other call this transport carries, so the app could show a
        // robot's health, its wifi and its gaits and not make it move — and the way out was to
        // go and find the gamepad. That is the opposite of what the app is for.
        //
        // `robotd` already publishes what a client needs to choose correctly: `homed` and
        // `sitting` on `robot.policies`, added in API v30 and v31 for exactly this — a duck on
        // its feet stands with `init`, a duck in its seat is held there by the `sit_toggle`
        // latch and `init` argues with it rather than winning. A client that has those does not
        // have to guess.
        RobotInit => true,

        // **The way back from a latched servo error, which is where a phone is the only tool.**
        //
        // It was refused beside `relax`, on the reading that cycling the servo bus while the
        // robot is standing is the same fall by another route. That is true of the instruction
        // and wrong about the situation: a servo that has latched overload, overheating or
        // electrical shock is holding nothing already, and nothing else clears it but pulling
        // the battery. So the call an owner needs is refused exactly when the robot is on the
        // floor with a dead joint and there is nothing to fall.
        //
        // What made it worth changing is that no other way back reaches a phone. Standing up is
        // `init`, routed above — and `init` on a robot with a latched servo does nothing but
        // fail again, which is the state the app can now see (`robot.health` names the joint)
        // and could not leave. The rest of the path is already here: torque goes off on every
        // joint first, the servos come back limp with their gains restored on the next write,
        // and `init` brings it up from there.
        //
        // The hazard is real for the robot that *is* standing, and it is the one the app is
        // asked to state: this drops the joints, so have the robot down or hold it. That is the
        // same claim `robot.do` and `robot.loadPolicy` are routed on — ten metres of radio range
        // means whoever tapped it is looking at the robot.
        RobotRebootMotors(_) => true,

        // **`relax` stays refused, and the asymmetry is the point.** Standing up is controlled:
        // the joints go where they are told. Relaxing is a robot that was holding itself up and
        // now is not, which on a phone is a button whose failure mode is the floor, and its
        // whole purpose is to produce that fall — unlike the reboot above, which exists to
        // recover a robot that has already stopped holding itself. `init` has no such mode, and
        // a refusal that covered all three was treating "moves the joints" as the hazard when
        // the hazard is "stops holding them for nothing in return".
        RobotRelax => false,

        // `robot.stop` deserves its own line, because refusing it looks wrong. An emergency stop
        // in the app is exactly what someone reaches for, and §6 does say local should preempt
        // remote — but a stop button that works over an unbonded, high-latency, sometimes-absent
        // radio is worse than no button, because it *looks* like an e-stop and is not one. The
        // deadman in `robotd` already stops the robot when intents stop arriving, which is the
        // mechanism that does not depend on a phone being in range. A real e-stop is physical.
        // Reconsider deliberately if the app ever needs it, with that caveat stated in the UI.
        RobotStop => false,

        // High-rate telemetry. `robot.subscribe` streams state at up to the control rate; over
        // BLE that is a firehose into a 20-byte pipe, and a client would get a decimated,
        // unpredictably-lagged view it could not reason about. `robot.health` is the question an
        // app actually has.
        RobotSubscribe(_) => false,

        // The same objection as `robot.subscribe`, only more so: this is every evdev event the pad
        // sends, over a hundred reports a second, and it exists to *measure the cadence of its own
        // delivery*. Carried over BLE the measurement would be of the phone's link rather than the
        // pad's, which is worse than refusing — it would be a number that looks like an answer.
        //
        // It is also not `btd`'s to forward: `padd` is deliberately not one of the sockets `btd`
        // holds, which `Upstream`'s conversion now enforces rather than merely documents.
        PadInput => false,

        // Depth frames, and the same two objections as the pad tap. A 64-zone frame
        // fifteen times a second is a firehose into a 20-byte pipe; and it is served by
        // `tofd`, which is not one of the sockets `btd` holds. When a phone has a
        // reason to see what the robot sees, it will be through `mediad`'s video path
        // (`architecture.md` §5.2), where depth belongs next to the frame it annotates.
        TofStream => false,
        // Same as the ToF: the head IMU is tofd's, reached over mediad's video path, not BLE.
        HeadImuStream => false,
    }
}

/// Where this call goes and on which connection, or `None` if BLE may not make it — or if no
/// service answers it, which for `system.authenticate` is the same answer with a different reason.
/// [`route_for`] tells those two apart.
pub fn destination_for(call: &proto::Call) -> Option<(Upstream, Lane)> {
    if !permits(call) {
        return None;
    }
    let (service, lane) = call.destination()?;
    Some((Upstream::try_from(service).ok()?, lane))
}

/// The service that answers a call, ignoring which connection carries it.
///
/// The permission question on its own, which is what most callers and every test about the
/// security boundary are asking.
pub fn upstream_for(call: &proto::Call) -> Option<Upstream> {
    destination_for(call).map(|(upstream, _)| upstream)
}

/// The full routing decision, including the one call the transport answers itself.
pub fn route_for(call: &proto::Call) -> Route {
    match call {
        proto::Call::SystemAuthenticate(_) => Route::Local,
        other => match destination_for(other) {
            Some((upstream, lane)) => Route::To(upstream, lane),
            None => Route::Refused,
        },
    }
}

/// The JSON-RPC error to answer a refused call with.
///
/// [`proto::code::PERMISSION_DENIED`] rather than `METHOD_NOT_FOUND`, because the two mean
/// different things to whoever is holding the phone: this method exists and this transport
/// may not use it — "try `robotctl`", not "upgrade your app".
pub fn refusal(call: &proto::Call) -> proto::Error {
    proto::Error::new(
        proto::code::PERMISSION_DENIED,
        format!(
            "{} is not available over Bluetooth; use robotctl on the robot",
            call.method()
        ),
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    // The shared list, not a local copy. Two copies of this had already drifted — 115 lines here
    // against 82 — which is how `pad.input` came to be missing from one of them.
    use duck_ipc_proto::test_support::every_call;
    use duck_ipc_proto::{ComponentId, semver};

    fn component() -> ComponentId {
        ComponentId::new("daemon")
    }

    /// Exactly which mutating calls BLE may make, named one by one.
    ///
    /// The list is the security boundary, so it is spelled out rather than counted: adding a
    /// mutating method and routing it should have to change this line and say why in the
    /// commit. `update.apply` is the update trigger §4.1 names; the rest are provisioning,
    /// which is what BLE is *for* — a robot that has never seen a network cannot be configured
    /// over that network.
    #[test]
    fn only_these_mutating_calls_are_reachable_over_ble() {
        let mutating_and_allowed: Vec<&str> = every_call()
            .iter()
            .filter(|c| c.is_mutating() && upstream_for(c).is_some())
            .map(proto::Call::method)
            .collect();

        assert_eq!(
            mutating_and_allowed,
            vec![
                proto::method::APPLY,
                // Going back, both of them. Routed when the update path was driven from a phone:
                // an owner whose robot got worse after an update has no other way to undo it, and
                // neither call discards anything or downloads anything.
                proto::method::ROLLBACK,
                proto::method::SELECT,
                // Replacing the policy set, and fetching a stranger's policy onto the board.
                // Routed for the reason provisioning is: BLE's physical-presence claim (§4.2)
                // holds — ten metres of radio range, a PIN-checked bond — and trying a gait is
                // the thing that most wants whoever asked to be looking at the robot. Everything
                // that makes it survivable is the same whoever asked: the manifest gate before
                // the download, the shape gate at load, the clamps, the fall reflex.
                proto::method::POLICY_INSTALL,
                proto::method::POLICY_FETCH,
                // Replacing the detector, by the same argument as the policy set.
                proto::method::DETECTOR_INSTALL,
                // Binding the robot to a Hugging Face account, and unbinding it. Provisioning,
                // like the two below it and for the same reason: a robot out of a box has no
                // network, so it has no console and no LAN to open one from, and this is the
                // transport that reaches it. Physical presence is not stretched either — the
                // person approving the code is holding the phone that is bonded to the robot.
                proto::method::ACCOUNT_LOGIN,
                proto::method::ACCOUNT_LOGOUT,
                proto::method::NET_CONNECT,
                proto::method::NET_FORGET,
                proto::method::SYSTEM_SET_NAME,
                proto::method::SYSTEM_REBOOT,
                // Bonding a gamepad, which afterwards can enable the walking policy. Allowed for
                // the same reason as provisioning: it takes a pad held in pairing mode next to the
                // robot, so BLE's physical-presence claim (§4.2) is not being stretched — and the
                // alternative is an ssh session, which is not a thing an owner has.
                proto::method::PAD_PAIR,
                proto::method::PAD_FORGET,
            ]
        );
    }

    /// Pairing a controller from the phone reaches `configd`, which is the service that owns the
    /// radio's configuration. `btd` must not answer this itself: it owns nothing (§4.1).
    #[test]
    fn a_pad_can_be_paired_from_the_phone() {
        for call in [
            proto::Call::PadStatus,
            proto::Call::PadPair(proto::PadPairParams::default()),
            proto::Call::PadForget(proto::PadForgetParams {
                mac: "78:86:2E:BB:13:28".into(),
            }),
        ] {
            assert_eq!(
                upstream_for(&call),
                Some(Upstream::Config),
                "{}",
                call.method()
            );
        }
    }

    /// The PIN must never be readable or writable over the radio.
    ///
    /// This is the one refusal here that is not merely cautious: pairing is what authorises a
    /// BLE client at all (§4.2), and a passkey an unpaired peer could ask for — or worse,
    /// overwrite — would make the whole mechanism theatre. `btd` gets it over the unix socket.
    #[test]
    fn the_pairing_pin_is_not_reachable_over_ble() {
        assert_eq!(upstream_for(&proto::Call::SystemPairingPin), None);
        assert_eq!(
            upstream_for(&proto::Call::SystemSetPairingPin(
                proto::SetPairingPinParams {
                    pin: "000000".into()
                }
            )),
            None
        );
    }

    /// Provisioning must be reachable, and reach `configd` — the case BLE exists for.
    #[test]
    fn provisioning_reaches_configd() {
        for call in [
            proto::Call::NetStatus,
            proto::Call::NetScan,
            proto::Call::NetConnect(proto::NetConnectParams {
                ssid: "Home".into(),
                psk: None,
            }),
            proto::Call::NetForget(proto::NetForgetParams {
                ssid: "Home".into(),
            }),
            proto::Call::SystemInfo,
            proto::Call::SystemSetName(proto::SetNameParams {
                name: "duck".into(),
            }),
            proto::Call::SystemReboot,
        ] {
            assert_eq!(
                upstream_for(&call),
                Some(Upstream::Config),
                "{}",
                call.method()
            );
        }
    }

    /// The refusals, named individually. If a future change makes one of these reachable it
    /// should have to delete a line here and say why in the commit.
    ///
    /// Two lines were deleted from it when the update path was driven from a phone —
    /// `update.rollback` and `update.select` — and the reasoning is on their arms in
    /// `destination_for`. What is left is a factory reset, a pin whose mistake looks like correct
    /// behaviour, and `updaterd`'s private questions to `robotd`.
    #[test]
    fn the_refused_calls_stay_refused() {
        for call in [
            proto::Call::ResetToGolden(proto::ComponentParams {
                component: component(),
            }),
            proto::Call::Pin(proto::PinParams {
                component: component(),
                version: None,
            }),
            proto::Call::RobotSafeToRestart,
            proto::Call::RobotModelApi,
            proto::Call::RobotRemoteSessionActive,
        ] {
            assert_eq!(upstream_for(&call), None, "{}", call.method());
        }
    }

    /// A phone must be able to establish a session, see the robot's state, start an update
    /// and watch it. Without all four the transport is not useful for what it exists to do.
    #[test]
    fn the_app_path_is_reachable() {
        let expected = [
            (
                proto::Call::Hello(proto::HelloParams {
                    api_version: proto::API_VERSION,
                }),
                Upstream::Updater,
            ),
            (proto::Call::Status, Upstream::Updater),
            (proto::Call::Subscribe, Upstream::Updater),
            (proto::Call::RobotHealth, Upstream::Robot),
        ];
        for (call, want) in expected {
            assert_eq!(upstream_for(&call), Some(want), "{}", call.method());
        }
    }

    /// **A phone can ask for a skill, see what the robot has, and change what it runs.**
    ///
    /// The three together, because none of them is much use alone: `robot.policies` is how a
    /// client learns there is a bow to ask for — which skills exist is config, so there is no
    /// list to compile in — and `robot.do` is the asking.
    #[test]
    fn a_phone_can_run_a_skill_and_change_a_policy() {
        let expected = [
            proto::Call::RobotPolicies,
            proto::Call::RobotDo(proto::DoParams {
                skill: "polite-bow".to_owned(),
            }),
            proto::Call::RobotLoadPolicy(proto::LoadPolicyParams {
                slot: Some("walk".to_owned()),
                path: Some("/opt/robot/policies/current/alpha_walking.onnx".to_owned()),
            }),
            proto::Call::RobotReloadPolicies,
            // The pair `robotctl pad bind` had no wire surface for at all.
            proto::Call::PadBindings,
            proto::Call::PadBind(proto::PadBindParams {
                button: "x".to_owned(),
                skill: Some("polite-bow".to_owned()),
            }),
            // The skill table — the last thing here only a terminal on the robot could reach.
            proto::Call::RobotSkills,
            proto::Call::RobotSetSkill(proto::SkillParams::default()),
            proto::Call::RobotRemoveSkill(proto::SkillNameParams {
                name: "polite-bow".to_owned(),
            }),
        ];
        for call in expected {
            assert_eq!(
                upstream_for(&call),
                Some(Upstream::Robot),
                "{}",
                call.method()
            );
        }
    }

    /// **A phone can get a robot back on its feet, and cannot put it on the floor.**
    ///
    /// The asymmetry in one test, because the two arms only make sense read together: `init`
    /// stands it up, `rebootMotors` clears a latched servo error so that `init` can — and
    /// `relax` stays refused, since its only outcome is a robot that was holding itself up and
    /// now is not. Making that one reachable should have to delete a line here and say why.
    #[test]
    fn a_phone_can_recover_a_robot_but_not_drop_it() {
        for call in [
            proto::Call::RobotInit,
            proto::Call::RobotRebootMotors(proto::RebootMotorsParams { ids: vec![] }),
            proto::Call::RobotRebootMotors(proto::RebootMotorsParams { ids: vec![3, 11] }),
        ] {
            assert_eq!(
                upstream_for(&call),
                Some(Upstream::Robot),
                "{}",
                call.method()
            );
        }
        assert_eq!(upstream_for(&proto::Call::RobotRelax), None);
    }

    /// **The Hub, from a phone.** What is out there, whether the official set has moved, and
    /// installing one — the four that reach the network, all on `updaterd` beside `update.check`.
    ///
    /// `policy.install` and `policy.fetch` are mutating, so they are also named one by one in
    /// [`only_these_mutating_calls_are_reachable_over_ble`]; this is the half that says they
    /// arrive somewhere.
    #[test]
    fn a_phone_can_browse_and_install_from_the_hub() {
        for call in [
            proto::Call::PolicyCheck,
            proto::Call::PolicySearch(proto::PolicySearchParams {
                query: "microduck".to_owned(),
            }),
            proto::Call::PolicyInstall(proto::PolicyInstallParams::default()),
            proto::Call::DetectorCheck,
            proto::Call::DetectorInstall(proto::PolicyInstallParams::default()),
        ] {
            assert_eq!(
                upstream_for(&call),
                Some(Upstream::Updater),
                "{}",
                call.method()
            );
        }
    }

    /// **A skill is not teleop, and teleop is still refused.**
    ///
    /// `robot.do` spent a while grouped with these, and the distinction is the whole reason it
    /// could be opened: one request against a stream of fifty a second. If somebody ever moves
    /// `robot.move` into that arm by widening a pattern, this is what says no.
    #[test]
    fn teleop_stays_off_the_radio() {
        for call in [
            proto::Call::RobotMove(proto::MoveParams {
                vx: 0.0,
                vy: 0.0,
                vyaw: 0.0,
            }),
            proto::Call::RobotHead(proto::HeadParams {
                neck_pitch: 0.0,
                head_pitch: 0.0,
                head_yaw: 0.0,
                head_roll: 0.0,
            }),
        ] {
            assert_eq!(upstream_for(&call), None, "{}", call.method());
        }
    }

    /// **Starting the policy is not teleop either**, and it left that arm for the same reason
    /// `robot.do` did: one request, not a stream. It was pinned as refused here until the phone
    /// app stood a robot up and found every skill answering "the policy is not driving — press
    /// Start on the pad", which is the half-path `robot.init` alone leaves behind.
    #[test]
    fn starting_the_policy_is_reachable() {
        let call = proto::Call::RobotEnable(proto::EnableParams {
            on: false,
            toggle: true,
        });
        assert!(upstream_for(&call).is_some(), "{}", call.method());
    }

    /// A refusal must be distinguishable from "no such method", because the two ask the user
    /// for different things.
    #[test]
    fn a_refusal_says_permission_denied_and_names_the_method() {
        let call = proto::Call::ResetToGolden(proto::ComponentParams {
            component: component(),
        });
        let err = refusal(&call);

        assert_eq!(err.code, proto::code::PERMISSION_DENIED);
        assert!(
            err.message.contains(proto::method::RESET_TO_GOLDEN),
            "{}",
            err.message
        );
    }

    /// Nothing a phone does during an update may share a connection with the update.
    ///
    /// This is the defect the lanes exist for, and it is asserted as a property rather than as a
    /// table: whatever else changes, `update.apply` must not be able to block a status poll, a
    /// check, or the progress stream, because every daemon here serves one connection one request
    /// at a time. The three calls below are the three an app makes *while* an update runs.
    #[test]
    fn an_apply_shares_its_connection_with_nothing_a_client_does_during_one() {
        let apply = destination_for(&proto::Call::Apply(proto::ApplyParams {
            component: component(),
            target: proto::Target::Latest,
            options: proto::ApplyOptions::default(),
        }))
        .expect("apply is routed");

        for call in [
            proto::Call::Status,
            proto::Call::Subscribe,
            proto::Call::Check(proto::ComponentParams {
                component: component(),
            }),
        ] {
            let during = destination_for(&call).expect("routed");
            assert_eq!(during.0, apply.0, "{} is served by updaterd", call.method());
            assert_ne!(
                during.1,
                apply.1,
                "{} would queue behind an apply",
                call.method()
            );
        }
    }

    /// The progress stream must be alone on its lane, which is a stronger claim than the test
    /// above: a connection handed to `stream_progress` reads no further requests *ever*, so a
    /// second call sharing it is not delayed but lost.
    #[test]
    fn nothing_else_travels_on_the_stream_lane() {
        let others: Vec<&str> = every_call()
            .iter()
            .filter(|c| !matches!(c, proto::Call::Subscribe))
            .filter(|c| destination_for(c).is_some_and(|(_, lane)| lane == Lane::Stream))
            .map(proto::Call::method)
            .collect();

        assert_eq!(others, Vec::<&str>::new());
        assert_eq!(
            destination_for(&proto::Call::Subscribe).map(|(_, lane)| lane),
            Some(Lane::Stream)
        );
    }

    /// A call that holds its connection for as long as the robot needs is never on the lane the
    /// quick answers use. Named one by one, because the cost of getting one wrong is a session
    /// that stops answering and the fix is one word.
    #[test]
    fn the_calls_that_take_their_time_are_off_the_prompt_lane() {
        for call in [
            proto::Call::Apply(proto::ApplyParams {
                component: component(),
                target: proto::Target::Latest,
                options: proto::ApplyOptions::default(),
            }),
            proto::Call::Rollback(proto::ComponentParams {
                component: component(),
            }),
            proto::Call::Select(proto::SelectParams {
                component: component(),
                version: semver::Version::new(1, 0, 0),
            }),
            proto::Call::Check(proto::ComponentParams {
                component: component(),
            }),
            proto::Call::NetScan,
            proto::Call::NetConnect(proto::NetConnectParams {
                ssid: "Home".into(),
                psk: None,
            }),
            proto::Call::PadPair(proto::PadPairParams::default()),
        ] {
            let (_, lane) = destination_for(&call).expect("routed");
            assert_ne!(lane, Lane::Prompt, "{}", call.method());
        }
    }

    /// Going back is reachable, and reaches `updaterd`. The pair of them is what §2.4 of
    /// `docs/project/update-over-ble.md` decided.
    #[test]
    fn going_back_is_reachable_from_the_phone() {
        for call in [
            proto::Call::Rollback(proto::ComponentParams {
                component: component(),
            }),
            proto::Call::Select(proto::SelectParams {
                component: component(),
                version: semver::Version::new(0, 5, 1),
            }),
        ] {
            assert_eq!(
                destination_for(&call),
                Some((Upstream::Updater, Lane::Operation)),
                "{}",
                call.method()
            );
        }
    }

    /// A permitted call must be one `btd` can actually deliver.
    ///
    /// This is the test the split made necessary. Permission and destination are now decided in
    /// two places, so it became possible to permit a call that `btd` holds no socket for —
    /// `pad.input` and `tof.stream` are served by `padd` and `tofd`, and `btd` connects to
    /// neither. Before, one table answered both questions and the mistake could not be written.
    ///
    /// `system.authenticate` is the deliberate exception: permitted, and answered by `btd` itself
    /// rather than forwarded, which is exactly what `route_for` reports as `Local`.
    #[test]
    fn everything_permitted_is_deliverable() {
        for call in every_call() {
            if !permits(&call) {
                continue;
            }
            if matches!(call, proto::Call::SystemAuthenticate(_)) {
                assert_eq!(
                    route_for(&call),
                    Route::Local,
                    "system.authenticate must be answered by btd itself"
                );
                continue;
            }
            assert!(
                destination_for(&call).is_some(),
                "{} is permitted over BLE but btd cannot deliver it — it is served by a socket \
                 btd does not hold, so either permit it and give btd that socket, or refuse it",
                call.method()
            );
        }
    }

    /// And the converse: a refused call must not be deliverable, whatever the shared table says.
    ///
    /// Cheap, and it pins the composition order. `destination_for` consulting the shared
    /// destination *before* the permission check would pass every other test in this file and
    /// quietly route the whole API to the radio.
    #[test]
    fn nothing_refused_is_deliverable() {
        for call in every_call() {
            if permits(&call) {
                continue;
            }
            assert_eq!(
                destination_for(&call),
                None,
                "{} is refused over BLE but destination_for offered a route",
                call.method()
            );
            assert_eq!(route_for(&call), Route::Refused, "{}", call.method());
        }
    }
}

```

### File: `btd/src/session.rs` (1022 lines, ~10883 tokens)
```rs
//! One connected central, from `hello` to disconnect.
//!
//! This is the whole of `btd`'s behaviour, and it holds no state about the robot — only about
//! the conversation: a reassembly buffer and whichever upstream sockets this session has had
//! reason to open.
//!
//! A request is forwarded **verbatim**. `btd` parses each line only far enough to answer two
//! questions — is this method allowed here, and which socket owns it — and then passes the
//! original bytes on. It never rewrites `id`, never re-serialises params, and never invents a
//! result. That is what keeps it a transport rather than a second implementation of the API,
//! and it is why adding a protocol method costs one line in [`crate::route`] and nothing here.

use duck_ipc_proto as proto;
use tokio::sync::mpsc;

use crate::link::{Link, QUEUE};
use crate::pairing;
use crate::route::{self, Route};
use crate::upstream::{Pool, Sockets};
use duck_ble::framing::{self, Reassembler};

/// How many wrong PINs a session may offer before it is closed.
///
/// A six-digit PIN is a million guesses, and the link is encrypted but not authenticated, so
/// rationing attempts is the only thing standing between a peer in radio range and brute force.
/// Three, then the session ends: reconnecting costs a full BLE connect and bond, which turns an
/// afternoon of guessing into something far longer while staying invisible to a legitimate client
/// that mistypes twice.
const PIN_ATTEMPTS: u32 = 3;

/// Serve one central until it disconnects or breaks framing.
pub async fn run(mut link: Link, sockets: Sockets) {
    let peer = link.peer.clone();
    tracing::info!(peer = %peer, mtu = link.mtu(), "session opened; mtu is the floor \
     until the first write reports the negotiated one");

    let (replies_tx, mut replies) = mpsc::channel::<String>(QUEUE);
    let config_socket = sockets.config.clone();
    let mut pool = Pool::new(sockets, replies_tx);
    let mut inbound = Reassembler::new();

    // Nothing but `hello` and `system.authenticate` is served until the client proves the PIN.
    // See `crate::pairing` for why this is here rather than in the bond.
    let mut authenticated = false;
    let mut attempts_left = PIN_ATTEMPTS;

    loop {
        tokio::select! {
            // Bytes from the radio.
            chunk = link.inbound.recv() => {
                let Some(chunk) = chunk else { break };

                let lines = match inbound.push(&chunk) {
                    Ok(lines) => lines,
                    Err(e) => {
                        // Framing failures end the session rather than being answered. There
                        // is no id to answer *to* — we never saw a complete request — and a
                        // peer that cannot frame will not be helped by a JSON error it also
                        // cannot parse.
                        tracing::warn!(peer = %peer, error = ?e, "framing failed; closing session");
                        break;
                    }
                };

                for line in lines {
                    let outcome = dispatch(
                        &mut pool,
                        &config_socket,
                        &line,
                        &mut authenticated,
                        &mut attempts_left,
                    )
                    .await;

                    if let Some(response) = outcome.response
                        && send_line(&link, &response).await.is_err()
                    {
                        return;
                    }
                    if outcome.close {
                        tracing::warn!(peer = %peer, "closing the session: too many bad PINs");
                        return;
                    }
                }
            }

            // A reply or a notification from a service.
            line = replies.recv() => {
                // The channel is held by `pool`, which lives as long as this loop, so `None`
                // is unreachable — but treat it as end-of-session rather than panicking.
                let Some(line) = line else { break };
                if send_line(&link, &line).await.is_err() {
                    return;
                }
            }
        }
    }

    if inbound.pending() > 0 {
        // Worth a line: it distinguishes "client finished and left" from "client vanished
        // mid-message", which is the difference between a normal disconnect and a bug.
        tracing::debug!(peer = %peer, pending = inbound.pending(), "session ended mid-line");
    }
    tracing::info!(peer = %peer, "session closed");
}

/// What handling one line produced.
struct Outcome {
    /// A response `btd` must send itself. `None` means an upstream will answer — the ordinary path.
    response: Option<String>,
    /// End the session after sending. Only ever set by exhausting the PIN attempts.
    close: bool,
}

impl Outcome {
    fn nothing() -> Self {
        Self {
            response: None,
            close: false,
        }
    }
    fn reply(response: String) -> Self {
        Self {
            response: Some(response),
            close: false,
        }
    }
}

/// Handle one complete line.
async fn dispatch(
    pool: &mut Pool,
    config_socket: &std::path::Path,
    line: &str,
    authenticated: &mut bool,
    attempts_left: &mut u32,
) -> Outcome {
    let request: proto::Request = match serde_json::from_str(line) {
        Ok(request) => request,
        Err(e) => {
            // No id is recoverable from an unparseable line, so the response carries `null` —
            // which the spec requires and every client already handles.
            return Outcome::reply(encode(&proto::Response::err(
                None,
                proto::Error::new(proto::code::PARSE_ERROR, e.to_string()),
            )));
        }
    };

    // A notification — no id — expects no reply, so a refused one is dropped silently. It is
    // still not forwarded: the allowlist is not advisory.
    let id = request.id.clone();

    let call = match request.as_call() {
        Ok(call) => call,
        Err(e) => {
            return match id.map(|id| encode(&proto::Response::err(Some(id), e))) {
                Some(r) => Outcome::reply(r),
                None => Outcome::nothing(),
            };
        }
    };

    // The PIN gate. `hello` is allowed through because it only reports versions — the same
    // information the GATT read already gives an unauthenticated client — and refusing it would
    // leave a mismatched client unable to learn why nothing works.
    if !*authenticated
        && !matches!(
            call,
            proto::Call::SystemAuthenticate(_) | proto::Call::Hello(_)
        )
    {
        tracing::info!(method = call.method(), "refused: not authenticated");
        let error = proto::Error::new(
            proto::code::PERMISSION_DENIED,
            format!(
                "{} needs authentication first: send system.authenticate with the robot's PIN \
                 (`robotctl system pin` on the robot)",
                call.method()
            ),
        );
        return match id.map(|id| encode(&proto::Response::err(Some(id), error))) {
            Some(r) => Outcome::reply(r),
            None => Outcome::nothing(),
        };
    }

    let (upstream, lane) = match route::route_for(&call) {
        Route::To(upstream, lane) => (upstream, lane),
        Route::Local => {
            let proto::Call::SystemAuthenticate(params) = &call else {
                // `route_for` returns `Local` for exactly one variant; anything else here is a
                // routing table that grew a local method without teaching this function about it.
                tracing::error!(method = call.method(), "routed locally with no handler");
                let error = proto::Error::new(
                    proto::code::INTERNAL_ERROR,
                    "routed locally with no handler",
                );
                return match id.map(|id| encode(&proto::Response::err(Some(id), error))) {
                    Some(r) => Outcome::reply(r),
                    None => Outcome::nothing(),
                };
            };
            return authenticate(config_socket, params, authenticated, attempts_left, id).await;
        }
        Route::Refused => {
            tracing::info!(method = call.method(), "refused over BLE");
            return match id.map(|id| encode(&proto::Response::err(Some(id), route::refusal(&call))))
            {
                Some(r) => Outcome::reply(r),
                None => Outcome::nothing(),
            };
        }
    };

    if let Err(e) = pool.send(upstream, lane, line).await {
        tracing::warn!(method = call.method(), upstream = ?upstream, error = %e, "upstream unreachable");
        // Naming the service is what makes this diagnosable from a phone screenshot: "robotd
        // is not answering" is a different problem from "the robot refused".
        let error = proto::Error::new(
            proto::code::INTERNAL_ERROR,
            format!("{upstream:?} is not answering: {e}"),
        );
        return match id.map(|id| encode(&proto::Response::err(Some(id), error))) {
            Some(r) => Outcome::reply(r),
            None => Outcome::nothing(),
        };
    }
    Outcome::nothing()
}

/// Check the PIN, and ration the attempts.
///
/// Fetched from `configd` per attempt rather than cached, so `robotctl system set-pin` takes effect
/// on the next try rather than the next reboot — and so a `configd` that cannot answer means the
/// session is refused rather than admitted.
///
/// The comparison is on the string, not a number: `000042` and `42` are different PINs, and a
/// numeric parse would make them the same.
async fn authenticate(
    config_socket: &std::path::Path,
    params: &proto::AuthenticateParams,
    authenticated: &mut bool,
    attempts_left: &mut u32,
    id: Option<proto::Id>,
) -> Outcome {
    let expected = match pairing::pin(config_socket).await {
        Ok(expected) => expected,
        Err(e) => {
            tracing::warn!(error = %e, "cannot read the PIN; refusing to authenticate");
            let error = proto::Error::new(
                proto::code::INTERNAL_ERROR,
                "cannot check the PIN: configd is not answering",
            );
            return match id.map(|id| encode(&proto::Response::err(Some(id), error))) {
                Some(r) => Outcome::reply(r),
                None => Outcome::nothing(),
            };
        }
    };

    // Constant-time-ish: compare whole strings of equal length rather than returning early on the
    // first differing digit. Over BLE the timing signal is buried in milliseconds of radio, so this
    // is hygiene rather than a defence — but it costs nothing.
    let ok = expected.pin.len() == params.pin.len()
        && expected
            .pin
            .bytes()
            .zip(params.pin.bytes())
            .fold(0u8, |acc, (a, b)| acc | (a ^ b))
            == 0;

    if ok {
        *authenticated = true;
        tracing::info!(default_pin = expected.is_default, "authenticated");
        if expected.is_default {
            // Worth saying every time: a factory PIN authenticates anyone who read this repository.
            tracing::warn!(
                "authenticated with the FACTORY PIN, which is public. Set a per-robot one: \
                 robotctl system set-pin <6 digits>"
            );
        }
        let result = proto::AuthenticateResult {
            authenticated: true,
            attempts_remaining: PIN_ATTEMPTS,
        };
        return match id.map(|id| encode(&proto::Response::ok(Some(id), &result))) {
            Some(r) => Outcome::reply(r),
            None => Outcome::nothing(),
        };
    }

    *attempts_left = attempts_left.saturating_sub(1);
    tracing::warn!(attempts_left = *attempts_left, "wrong PIN");

    let result = proto::AuthenticateResult {
        authenticated: false,
        attempts_remaining: *attempts_left,
    };
    let response = id.map(|id| encode(&proto::Response::ok(Some(id), &result)));
    Outcome {
        response,
        close: *attempts_left == 0,
    }
}

/// Chunk one line out to the central.
async fn send_line(link: &Link, line: &str) -> Result<(), ()> {
    // Read once here, so one line is chunked one way even if a write reports a new MTU
    // meanwhile. See `Link::mtu`.
    for chunk in framing::chunks(line, link.mtu()) {
        if link.outbound.send(chunk).await.is_err() {
            // The backend dropped its half: the central is gone.
            return Err(());
        }
    }
    Ok(())
}

fn encode(response: &proto::Response) -> String {
    // A Response is plain strings, ints and enums; this cannot fail. If it somehow did,
    // sending nothing would hang the client, so send something it can parse as an error.
    serde_json::to_string(response).unwrap_or_else(|_| {
        r#"{"jsonrpc":"2.0","id":null,"error":{"code":-32603,"message":"internal error"}}"#
            .to_owned()
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::PathBuf;
    use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader};
    use tokio::net::UnixListener;
    use tokio::sync::mpsc::{Receiver, Sender};

    /// A stand-in for one daemon: accepts a connection, records the lines it receives, and
    /// replies with whatever the test queued.
    ///
    /// A real unix socket rather than a mock, because the framing between `btd` and a daemon is
    /// part of what is under test — the same reason `robotd`'s own tests speak over a socket.
    struct FakeDaemon {
        path: PathBuf,
        seen: Sender<String>,
        replies: Vec<String>,
    }

    impl FakeDaemon {
        fn spawn(
            dir: &std::path::Path,
            name: &str,
            replies: Vec<String>,
        ) -> (PathBuf, Receiver<String>) {
            let path = dir.join(name);
            let (seen, seen_rx) = mpsc::channel(16);
            let daemon = FakeDaemon {
                path: path.clone(),
                seen,
                replies,
            };

            let listener = UnixListener::bind(&daemon.path).expect("bind");
            tokio::spawn(async move {
                while let Ok((stream, _)) = listener.accept().await {
                    let seen = daemon.seen.clone();
                    let replies = daemon.replies.clone();
                    tokio::spawn(async move {
                        let (read, mut write) = stream.into_split();
                        let mut lines = BufReader::new(read).lines();
                        while let Ok(Some(line)) = lines.next_line().await {
                            let _ = seen.send(line).await;
                            for reply in &replies {
                                let _ = write.write_all(format!("{reply}\n").as_bytes()).await;
                            }
                            let _ = write.flush().await;
                        }
                    });
                }
            });
            (path, seen_rx)
        }
    }

    /// Collect notified chunks and reassemble them the way a client would.
    async fn read_reply(from_robot: &mut Receiver<Vec<u8>>) -> String {
        let mut r = Reassembler::new();
        loop {
            let chunk = tokio::time::timeout(std::time::Duration::from_secs(2), from_robot.recv())
                .await
                .expect("client saw no reply")
                .expect("link closed");
            if let Some(line) = r.push(&chunk).expect("framing").into_iter().next() {
                return line;
            }
        }
    }

    /// Like [`read_reply`], and also says how the line was cut up on the way out.
    async fn read_reply_in_chunks(from_robot: &mut Receiver<Vec<u8>>) -> (String, Vec<usize>) {
        let mut r = Reassembler::new();
        let mut sizes = Vec::new();
        loop {
            let chunk = tokio::time::timeout(std::time::Duration::from_secs(2), from_robot.recv())
                .await
                .expect("client saw no reply")
                .expect("link closed");
            sizes.push(chunk.len());
            if let Some(line) = r.push(&chunk).expect("framing").into_iter().next() {
                return (line, sizes);
            }
        }
    }

    /// The reply a fake `configd` gives to `system.pairingPin`.
    fn pin_reply(pin: &str) -> String {
        serde_json::to_string(&proto::Response::ok(
            Some(proto::Id::Number(1)),
            &proto::PairingPinResult {
                pin: pin.to_owned(),
                is_default: false,
            },
        ))
        .unwrap()
    }

    /// Do what a real client must now do first: prove the PIN.
    ///
    /// Every test goes through this, which means every test also exercises the gate — a session
    /// that stopped authenticating would fail all of them rather than silently serve everything.
    async fn authenticate(to_robot: &Sender<Vec<u8>>, from_robot: &mut Receiver<Vec<u8>>) {
        let request =
            r#"{"jsonrpc":"2.0","id":99,"method":"system.authenticate","params":{"pin":"424242"}}"#;
        to_robot
            .send(format!("{request}\n").into_bytes())
            .await
            .unwrap();
        let reply = read_reply(from_robot).await;
        assert!(
            reply.contains(r#""authenticated":true"#),
            "the handshake failed: {reply}"
        );
    }

    fn sockets(dir: &std::path::Path, updater: &str, robot: &str) -> Sockets {
        Sockets {
            updater: dir.join(updater),
            robot: dir.join(robot),
            // Not exercised by these tests; `configd` gets its own once it has a fake.
            config: dir.join("configd.sock"),
        }
    }

    /// The ordinary path: an allowed call reaches the right daemon **byte for byte**, and its
    /// reply comes back. Verbatim forwarding is the property that keeps btd a transport.
    #[tokio::test]
    async fn an_allowed_call_is_forwarded_verbatim_and_answered() {
        let dir = tempdir();
        let (_, _) = FakeDaemon::spawn(dir.path(), "configd.sock", vec![pin_reply("424242")]);
        let (_, mut seen) = FakeDaemon::spawn(dir.path(), "updaterd.sock",
            vec![r#"{"jsonrpc":"2.0","id":1,"result":{"api_version":2,"daemon_version":"0.1.4","revision":null}}"#.into()]);
        let (_, _) = FakeDaemon::spawn(dir.path(), "robotd.sock", vec![]);

        let (link, to_robot, mut from_robot) = Link::pair(23, "AA:BB");
        tokio::spawn(run(
            link,
            sockets(dir.path(), "updaterd.sock", "robotd.sock"),
        ));
        authenticate(&to_robot, &mut from_robot).await;

        let request = r#"{"jsonrpc":"2.0","id":1,"method":"hello","params":{"api_version":2}}"#;
        to_robot.send(request.as_bytes().to_vec()).await.unwrap();
        to_robot.send(b"\n".to_vec()).await.unwrap();

        assert_eq!(
            seen.recv().await.unwrap(),
            request,
            "not forwarded byte for byte"
        );
        assert!(
            read_reply(&mut from_robot)
                .await
                .contains(r#""api_version":2"#)
        );
    }

    /// A refused call must never touch the upstream. Answering correctly is not enough — the
    /// point of the allowlist is that the daemon never sees it.
    #[tokio::test]
    async fn a_refused_call_never_reaches_the_daemon() {
        let dir = tempdir();
        let (_, _) = FakeDaemon::spawn(dir.path(), "configd.sock", vec![pin_reply("424242")]);
        let (_, mut seen) = FakeDaemon::spawn(dir.path(), "updaterd.sock", vec![]);
        let (_, _) = FakeDaemon::spawn(dir.path(), "robotd.sock", vec![]);

        let (link, to_robot, mut from_robot) = Link::pair(23, "AA:BB");
        tokio::spawn(run(
            link,
            sockets(dir.path(), "updaterd.sock", "robotd.sock"),
        ));
        authenticate(&to_robot, &mut from_robot).await;

        to_robot.send(
            format!("{}\n", r#"{"jsonrpc":"2.0","id":9,"method":"update.resetToGolden","params":{"component":"daemon"}}"#)
                .into_bytes(),
        ).await.unwrap();

        let reply = read_reply(&mut from_robot).await;
        assert!(
            reply.contains(&proto::code::PERMISSION_DENIED.to_string()),
            "{reply}"
        );

        // Nothing arrived at the daemon, and "nothing" needs a moment to be provable.
        tokio::time::sleep(std::time::Duration::from_millis(150)).await;
        assert!(seen.try_recv().is_err(), "a refused call was forwarded");
    }

    /// `robot.*` goes to `robotd` and not to `updaterd`. One table drives routing and
    /// permission, so a mistake here would send an update trigger to the control daemon.
    #[tokio::test]
    async fn robot_calls_go_to_robotd() {
        let dir = tempdir();
        let (_, _) = FakeDaemon::spawn(dir.path(), "configd.sock", vec![pin_reply("424242")]);
        let (_, mut updater_seen) = FakeDaemon::spawn(dir.path(), "updaterd.sock", vec![]);
        let (_, mut robot_seen) = FakeDaemon::spawn(
            dir.path(),
            "robotd.sock",
            vec![r#"{"jsonrpc":"2.0","id":2,"result":{"healthy":true}}"#.into()],
        );

        let (link, to_robot, mut from_robot) = Link::pair(185, "AA:BB");
        tokio::spawn(run(
            link,
            sockets(dir.path(), "updaterd.sock", "robotd.sock"),
        ));
        authenticate(&to_robot, &mut from_robot).await;

        to_robot
            .send(b"{\"jsonrpc\":\"2.0\",\"id\":2,\"method\":\"robot.health\"}\n".to_vec())
            .await
            .unwrap();

        assert!(robot_seen.recv().await.unwrap().contains("robot.health"));
        assert!(
            read_reply(&mut from_robot)
                .await
                .contains(r#""healthy":true"#)
        );
        assert!(
            updater_seen.try_recv().is_err(),
            "robotd's call went to updaterd"
        );
    }

    /// **A reply is sized for the MTU the link has learned, and a session starts knowing only
    /// the floor.**
    ///
    /// This is the mechanism behind `bluez`'s shared MTU cell, tested here because that file needs
    /// a radio and this one does not. What it pins is the ordering that makes the trick sound: a
    /// central subscribes before it writes, so a session opens at the 20-byte floor and learns the
    /// real payload from the first write — which is always `system.authenticate`, before any reply
    /// worth chunking exists.
    ///
    /// Sizing every reply for the floor was not merely slow. Ten times the notifications is ten
    /// times the queue depth in BlueZ, and past roughly 5 KiB the notification session was torn
    /// down mid-reply — a `system.logs` tail was the first reply big enough to find it.
    #[tokio::test]
    async fn a_reply_is_chunked_for_the_mtu_the_link_has_learned() {
        let dir = tempdir();
        let (_, _) = FakeDaemon::spawn(dir.path(), "configd.sock", vec![pin_reply("424242")]);
        let (_, _) = FakeDaemon::spawn(dir.path(), "updaterd.sock", vec![]);
        let (_, _) = FakeDaemon::spawn(
            dir.path(),
            "robotd.sock",
            vec![r#"{"jsonrpc":"2.0","id":2,"result":{"healthy":true}}"#.into()],
        );

        let mtu = std::sync::Arc::new(std::sync::atomic::AtomicUsize::new(20));
        let (link, to_robot, mut from_robot) = Link::pair_sharing_mtu(mtu.clone(), "AA:BB");
        tokio::spawn(run(
            link,
            sockets(dir.path(), "updaterd.sock", "robotd.sock"),
        ));

        // At the floor, so the authentication answer goes out in 20-byte pieces.
        to_robot
            .send(
                b"{\"jsonrpc\":\"2.0\",\"id\":0,\"method\":\"system.authenticate\",\"params\":{\"pin\":\"424242\"}}\n"
                    .to_vec(),
            )
            .await
            .unwrap();
        let (reply, sizes) = read_reply_in_chunks(&mut from_robot).await;
        assert!(reply.contains(r#""authenticated":true"#), "{reply}");
        assert!(
            sizes.len() > 1,
            "a floor-sized reply arrived whole: {sizes:?}"
        );
        assert!(
            sizes.iter().all(|&n| n <= 20),
            "a chunk exceeded the floor: {sizes:?}"
        );

        // What the write callback does on a real link, once BlueZ has reported the MTU.
        mtu.store(182, std::sync::atomic::Ordering::Relaxed);

        to_robot
            .send(b"{\"jsonrpc\":\"2.0\",\"id\":2,\"method\":\"robot.health\"}\n".to_vec())
            .await
            .unwrap();
        let (reply, sizes) = read_reply_in_chunks(&mut from_robot).await;
        assert!(reply.contains(r#""healthy":true"#), "{reply}");
        assert_eq!(
            sizes.len(),
            1,
            "the reply was still cut up for the floor: {sizes:?}"
        );
    }

    /// A subscription is a stream of notifications on an open connection, and every one has to
    /// reach the central. This is the case that would break if replies were correlated to
    /// requests rather than forwarded as they arrive.
    #[tokio::test]
    async fn every_notification_in_a_stream_reaches_the_client() {
        let dir = tempdir();
        let (_, _) = FakeDaemon::spawn(dir.path(), "configd.sock", vec![pin_reply("424242")]);
        let progress: Vec<String> = (0..3)
            .map(|i| format!(
                r#"{{"jsonrpc":"2.0","method":"update.progress","params":{{"component":"daemon","phase":"downloading","percent":{},"detail":null}}}}"#,
                i * 50
            ))
            .collect();
        let (_, _) = FakeDaemon::spawn(dir.path(), "updaterd.sock", progress);
        let (_, _) = FakeDaemon::spawn(dir.path(), "robotd.sock", vec![]);

        let (link, to_robot, mut from_robot) = Link::pair(23, "AA:BB");
        tokio::spawn(run(
            link,
            sockets(dir.path(), "updaterd.sock", "robotd.sock"),
        ));
        authenticate(&to_robot, &mut from_robot).await;

        to_robot
            .send(b"{\"jsonrpc\":\"2.0\",\"id\":3,\"method\":\"update.subscribe\"}\n".to_vec())
            .await
            .unwrap();

        // A 23-byte MTU means each of these arrives in several chunks, so this also proves
        // reassembly survives back-to-back messages.
        for expected in [0, 50, 100] {
            let line = read_reply(&mut from_robot).await;
            assert!(line.contains(&format!(r#""percent":{expected}"#)), "{line}");
        }
    }

    /// Garbage gets an error with a null id, not a dropped session: a client that sent one bad
    /// line should be able to carry on.
    #[tokio::test]
    async fn an_unparseable_line_is_answered_and_the_session_survives() {
        let dir = tempdir();
        let (_, _) = FakeDaemon::spawn(dir.path(), "configd.sock", vec![pin_reply("424242")]);
        let (_, _) = FakeDaemon::spawn(dir.path(), "updaterd.sock",
            vec![r#"{"jsonrpc":"2.0","id":1,"result":{"api_version":2,"daemon_version":null,"revision":null}}"#.into()]);
        let (_, _) = FakeDaemon::spawn(dir.path(), "robotd.sock", vec![]);

        let (link, to_robot, mut from_robot) = Link::pair(185, "AA:BB");
        tokio::spawn(run(
            link,
            sockets(dir.path(), "updaterd.sock", "robotd.sock"),
        ));
        authenticate(&to_robot, &mut from_robot).await;

        to_robot.send(b"not json at all\n".to_vec()).await.unwrap();
        let reply = read_reply(&mut from_robot).await;
        assert!(
            reply.contains(&proto::code::PARSE_ERROR.to_string()),
            "{reply}"
        );
        assert!(reply.contains(r#""id":null"#), "{reply}");

        // Still usable.
        to_robot.send(b"{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"hello\",\"params\":{\"api_version\":2}}\n".to_vec()).await.unwrap();
        assert!(
            read_reply(&mut from_robot)
                .await
                .contains(r#""api_version":2"#)
        );
    }

    /// A daemon that is not running must produce a diagnosable error naming it, rather than a
    /// hang. `robotd` is missing precisely when an update has just restarted it, which is when
    /// someone is most likely to be looking at a phone.
    #[tokio::test]
    async fn a_dead_daemon_is_reported_rather_than_hanging() {
        let dir = tempdir();
        let (_, _) = FakeDaemon::spawn(dir.path(), "configd.sock", vec![pin_reply("424242")]);
        let (_, _) = FakeDaemon::spawn(dir.path(), "updaterd.sock", vec![]);
        // No robotd socket at all.

        let (link, to_robot, mut from_robot) = Link::pair(185, "AA:BB");
        tokio::spawn(run(
            link,
            sockets(dir.path(), "updaterd.sock", "absent.sock"),
        ));
        authenticate(&to_robot, &mut from_robot).await;

        to_robot
            .send(b"{\"jsonrpc\":\"2.0\",\"id\":4,\"method\":\"robot.health\"}\n".to_vec())
            .await
            .unwrap();

        let reply = read_reply(&mut from_robot).await;
        assert!(reply.contains("Robot is not answering"), "{reply}");
    }

    /// A notification (no id) gets no reply even when refused — the spec says so, and a client
    /// waiting for one would wait forever.
    #[tokio::test]
    async fn a_refused_notification_is_answered_with_silence() {
        let dir = tempdir();
        let (_, _) = FakeDaemon::spawn(dir.path(), "configd.sock", vec![pin_reply("424242")]);
        let (_, mut seen) = FakeDaemon::spawn(dir.path(), "updaterd.sock", vec![]);
        let (_, _) = FakeDaemon::spawn(dir.path(), "robotd.sock", vec![]);

        let (link, to_robot, mut from_robot) = Link::pair(185, "AA:BB");
        tokio::spawn(run(
            link,
            sockets(dir.path(), "updaterd.sock", "robotd.sock"),
        ));
        authenticate(&to_robot, &mut from_robot).await;

        to_robot.send(
            format!("{}\n", r#"{"jsonrpc":"2.0","method":"update.resetToGolden","params":{"component":"daemon"}}"#)
                .into_bytes(),
        ).await.unwrap();

        tokio::time::sleep(std::time::Duration::from_millis(150)).await;
        assert!(
            from_robot.try_recv().is_err(),
            "a notification was answered"
        );
        assert!(
            seen.try_recv().is_err(),
            "a refused notification was forwarded"
        );
    }

    /// The gate. An unauthenticated call is refused, and the message says what to do about it —
    /// this is the first thing a phone app author will hit.
    #[tokio::test]
    async fn nothing_is_served_before_the_pin() {
        let dir = tempdir();
        let (_, _) = FakeDaemon::spawn(dir.path(), "configd.sock", vec![pin_reply("424242")]);
        let (_, mut seen) = FakeDaemon::spawn(dir.path(), "updaterd.sock", vec![]);
        let (_, _) = FakeDaemon::spawn(dir.path(), "robotd.sock", vec![]);

        let (link, to_robot, mut from_robot) = Link::pair(185, "AA:BB");
        tokio::spawn(run(
            link,
            sockets(dir.path(), "updaterd.sock", "robotd.sock"),
        ));
        // Deliberately NOT authenticated.

        to_robot
            .send(b"{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"update.status\"}\n".to_vec())
            .await
            .unwrap();

        let reply = read_reply(&mut from_robot).await;
        assert!(
            reply.contains(&proto::code::PERMISSION_DENIED.to_string()),
            "{reply}"
        );
        assert!(
            reply.contains("system.authenticate"),
            "the refusal must say how to proceed: {reply}"
        );

        // And it never reached the daemon: the gate is not advisory.
        tokio::time::sleep(std::time::Duration::from_millis(150)).await;
        assert!(
            seen.try_recv().is_err(),
            "an unauthenticated call was forwarded"
        );
    }

    /// `hello` is the one exception, because it reports only versions — the same thing the GATT
    /// read already tells an unauthenticated client — and refusing it would leave a mismatched
    /// client unable to learn why nothing works.
    #[tokio::test]
    async fn hello_is_allowed_before_the_pin() {
        let dir = tempdir();
        let (_, _) = FakeDaemon::spawn(dir.path(), "configd.sock", vec![pin_reply("424242")]);
        let (_, _) = FakeDaemon::spawn(
            dir.path(),
            "updaterd.sock",
            vec![r#"{"jsonrpc":"2.0","id":1,"result":{"api_version":4,"daemon_version":null,"revision":null}}"#.into()],
        );
        let (_, _) = FakeDaemon::spawn(dir.path(), "robotd.sock", vec![]);

        let (link, to_robot, mut from_robot) = Link::pair(185, "AA:BB");
        tokio::spawn(run(
            link,
            sockets(dir.path(), "updaterd.sock", "robotd.sock"),
        ));

        to_robot
            .send(b"{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"hello\",\"params\":{\"api_version\":4}}\n".to_vec())
            .await
            .unwrap();
        assert!(read_reply(&mut from_robot).await.contains("api_version"));
    }

    /// A wrong PIN counts down and then closes the session. A six-digit PIN is a million guesses
    /// over a link that is encrypted but not authenticated, so rationing the attempts is the only
    /// thing making brute force expensive.
    #[tokio::test]
    async fn wrong_pins_are_rationed_and_then_the_session_closes() {
        let dir = tempdir();
        let (_, _) = FakeDaemon::spawn(dir.path(), "configd.sock", vec![pin_reply("424242")]);
        let (_, _) = FakeDaemon::spawn(dir.path(), "updaterd.sock", vec![]);
        let (_, _) = FakeDaemon::spawn(dir.path(), "robotd.sock", vec![]);

        let (link, to_robot, mut from_robot) = Link::pair(185, "AA:BB");
        tokio::spawn(run(
            link,
            sockets(dir.path(), "updaterd.sock", "robotd.sock"),
        ));

        let wrong =
            r#"{"jsonrpc":"2.0","id":1,"method":"system.authenticate","params":{"pin":"000000"}}"#;
        for expected_left in [2, 1, 0] {
            to_robot
                .send(format!("{wrong}\n").into_bytes())
                .await
                .unwrap();
            let reply = read_reply(&mut from_robot).await;
            assert!(reply.contains(r#""authenticated":false"#), "{reply}");
            assert!(
                reply.contains(&format!(r#""attempts_remaining":{expected_left}"#)),
                "a client must be able to say how many tries are left: {reply}"
            );
        }

        // The third failure ends the session, so the link closes rather than accepting a fourth.
        tokio::time::sleep(std::time::Duration::from_millis(150)).await;
        assert!(
            to_robot
                .send(format!("{wrong}\n").into_bytes())
                .await
                .is_err()
                || from_robot.try_recv().is_err(),
            "the session should have closed after exhausting the attempts"
        );
    }

    /// A PIN differing only in a leading zero must not authenticate. The stored form is a string
    /// precisely so that `042042` and `42042` are different secrets.
    #[tokio::test]
    async fn a_leading_zero_is_part_of_the_pin() {
        let dir = tempdir();
        let (_, _) = FakeDaemon::spawn(dir.path(), "configd.sock", vec![pin_reply("042042")]);
        let (_, _) = FakeDaemon::spawn(dir.path(), "updaterd.sock", vec![]);
        let (_, _) = FakeDaemon::spawn(dir.path(), "robotd.sock", vec![]);

        let (link, to_robot, mut from_robot) = Link::pair(185, "AA:BB");
        tokio::spawn(run(
            link,
            sockets(dir.path(), "updaterd.sock", "robotd.sock"),
        ));

        let without =
            r#"{"jsonrpc":"2.0","id":1,"method":"system.authenticate","params":{"pin":"42042"}}"#;
        to_robot
            .send(format!("{without}\n").into_bytes())
            .await
            .unwrap();
        assert!(
            read_reply(&mut from_robot)
                .await
                .contains(r#""authenticated":false"#),
            "a PIN missing its leading zero must not authenticate"
        );
    }

    /// A stand-in with `updaterd`'s connection model, which is the whole reason lanes exist:
    /// **one request at a time per connection**, and a connection handed to `update.subscribe`
    /// never reads another line (`Server::stream_progress` owns it until the peer goes away).
    ///
    /// Every line it receives is reported as `<connection number> <line>`, so a test can assert
    /// which calls travelled together rather than only that they arrived.
    fn spawn_serial_updaterd(dir: &std::path::Path) -> (PathBuf, Receiver<String>) {
        let path = dir.join("updaterd.sock");
        let (seen, seen_rx) = mpsc::channel(16);
        let listener = UnixListener::bind(&path).expect("bind");

        tokio::spawn(async move {
            let mut connection = 0u32;
            while let Ok((stream, _)) = listener.accept().await {
                connection += 1;
                let seen = seen.clone();
                let n = connection;
                tokio::spawn(async move {
                    // Held for the task's life: dropping the stream would close the socket, and a
                    // client that learns of a swallowed request by disconnection has not
                    // reproduced the bug — it would reconnect and recover.
                    let (read, _write) = stream.into_split();
                    let mut lines = BufReader::new(read).lines();
                    while let Ok(Some(line)) = lines.next_line().await {
                        let subscribe = line.contains(proto::method::SUBSCRIBE);
                        let _ = seen.send(format!("{n} {line}")).await;
                        if subscribe {
                            std::future::pending::<()>().await;
                        }
                    }
                });
            }
        });
        (path, seen_rx)
    }

    async fn next_line(seen: &mut Receiver<String>, what: &str) -> String {
        tokio::time::timeout(std::time::Duration::from_secs(2), seen.recv())
            .await
            .unwrap_or_else(|_| panic!("updaterd never saw the {what}"))
            .expect("daemon gone")
    }

    /// Subscribing must not swallow the update that follows it.
    ///
    /// This is the failure the lanes were added for, and it is the worst one in the transport:
    /// with a single connection per service, the apply was written into a socket that
    /// `stream_progress` had stopped reading. No reply, no error, no update — an owner tapping
    /// "update" and a robot doing nothing at all. Nothing else in this file would have caught it,
    /// because every other test makes one call.
    #[tokio::test]
    async fn an_apply_still_reaches_updaterd_while_a_progress_stream_is_open() {
        let dir = tempdir();
        let (_, _) = FakeDaemon::spawn(dir.path(), "configd.sock", vec![pin_reply("424242")]);
        let (_, mut seen) = spawn_serial_updaterd(dir.path());
        let (_, _) = FakeDaemon::spawn(dir.path(), "robotd.sock", vec![]);

        let (link, to_robot, mut from_robot) = Link::pair(23, "AA:BB");
        tokio::spawn(run(
            link,
            sockets(dir.path(), "updaterd.sock", "robotd.sock"),
        ));
        authenticate(&to_robot, &mut from_robot).await;

        let subscribe = r#"{"jsonrpc":"2.0","id":1,"method":"update.subscribe","params":{}}"#;
        to_robot
            .send(format!("{subscribe}\n").into_bytes())
            .await
            .unwrap();
        let streaming = next_line(&mut seen, "subscribe").await;

        let apply = r#"{"jsonrpc":"2.0","id":2,"method":"update.apply","params":{"component":"daemon","target":"latest"}}"#;
        to_robot
            .send(format!("{apply}\n").into_bytes())
            .await
            .unwrap();
        let applying = next_line(&mut seen, "apply").await;

        assert!(
            applying.contains(apply),
            "not forwarded verbatim: {applying}"
        );
        // And on its own connection, which is *why* it arrived.
        let connection = |line: &str| line.split(' ').next().unwrap().to_owned();
        assert_ne!(connection(&streaming), connection(&applying));
    }

    /// A status poll during an update must not queue behind it.
    ///
    /// `updaterd` goes to some trouble to answer `update.status` while the engine is busy — a
    /// cached snapshot with the live phase patched in — and all of it is wasted if the request
    /// sits unread in a socket for the minutes an update takes. The assertion is that the two
    /// calls travel on different connections, because that is the property the daemon's effort
    /// depends on.
    #[tokio::test]
    async fn a_status_poll_does_not_travel_behind_an_apply() {
        let dir = tempdir();
        let (_, _) = FakeDaemon::spawn(dir.path(), "configd.sock", vec![pin_reply("424242")]);
        let (_, mut seen) = spawn_serial_updaterd(dir.path());
        let (_, _) = FakeDaemon::spawn(dir.path(), "robotd.sock", vec![]);

        let (link, to_robot, mut from_robot) = Link::pair(23, "AA:BB");
        tokio::spawn(run(
            link,
            sockets(dir.path(), "updaterd.sock", "robotd.sock"),
        ));
        authenticate(&to_robot, &mut from_robot).await;

        for request in [
            r#"{"jsonrpc":"2.0","id":1,"method":"update.apply","params":{"component":"daemon","target":"latest"}}"#,
            r#"{"jsonrpc":"2.0","id":2,"method":"update.status","params":{}}"#,
        ] {
            to_robot
                .send(format!("{request}\n").into_bytes())
                .await
                .unwrap();
        }

        let applying = next_line(&mut seen, "apply").await;
        let polling = next_line(&mut seen, "status poll").await;
        let connection = |line: &str| line.split(' ').next().unwrap().to_owned();
        assert_ne!(
            connection(&applying),
            connection(&polling),
            "the status poll shares the apply's queue"
        );
    }

    /// Sockets live in a temp directory, and unix socket paths are short by necessity — a
    /// long temp path would exceed `sun_path` and fail to bind for reasons unrelated to btd.
    fn tempdir() -> tempfile::TempDir {
        tempfile::Builder::new()
            .prefix("btd")
            .tempdir()
            .expect("tempdir")
    }
}

```

### File: `btd/src/upstream.rs` (420 lines, ~4434 tokens)
```rs
//! Connections to the services that actually own the answers.
//!
//! One socket per service, connected directly — with four services there is no case for a
//! broker, and a bus would be another component that can fail (`architecture.md` §2.2).
//!
//! Every operation here is timeout-bounded, without exception. Any peer may be dead, and a
//! closed or silent socket is a normal answer rather than an error worth retrying forever —
//! `robotd` in particular is the service most likely to be missing, since it is the one an
//! update restarts.

use std::collections::HashMap;
use std::io;
use std::path::{Path, PathBuf};
use std::time::Duration;

use duck_ipc_proto as proto;
use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader};
use tokio::net::UnixStream;
use tokio::sync::mpsc;

use crate::route::{Lane, Upstream};

/// Long enough for a loaded board, short enough that a phone gets an answer rather than a
/// spinner. A unix socket connect either succeeds immediately or the daemon is not there.
const CONNECT_TIMEOUT: Duration = Duration::from_secs(3);

/// Cap on a single write. A blocked write means the daemon has stopped reading, which is a
/// dead peer rather than a slow one.
const WRITE_TIMEOUT: Duration = Duration::from_secs(5);

/// What to advertise the robot as.
///
/// The name belongs to `configd` (`architecture.md` §4.1) — an SDK should not have to go through
/// Bluetooth to set it — so `btd` asks rather than decides. Here rather than in `bluez` so the
/// crate's entry point has the same shape off-Linux, where there is no radio to advertise on.
#[derive(Debug, Clone)]
pub struct NameChoice {
    /// `--name`, which pins the advertised name and turns reconciliation off. Bench use: it exists
    /// so a board can be given a known name without touching its stored config.
    pub pinned: Option<String>,
    /// Used when `configd` cannot be reached. `btd` is on the recovery path and must answer when
    /// the rest of the robot does not (`systemd/btd.service`), so an unreachable `configd` costs
    /// the derived name and nothing more.
    pub fallback: String,
}

/// Where each service listens.
#[derive(Debug, Clone)]
pub struct Sockets {
    pub updater: PathBuf,
    pub robot: PathBuf,
    pub config: PathBuf,
}

impl Sockets {
    pub fn path(&self, upstream: Upstream) -> &Path {
        match upstream {
            Upstream::Updater => &self.updater,
            Upstream::Robot => &self.robot,
            Upstream::Config => &self.config,
        }
    }
}

/// Ask one service one question, on `btd`'s own behalf.
///
/// A one-shot connection rather than a [`Pool`] entry, because this is not forwarding: nothing
/// here belongs to a client's session. `btd` asks two questions of its own — the PIN during a
/// pairing exchange, and the robot's name to advertise — and both want a single answer now rather
/// than a merged stream of lines. With exactly one reply in flight there is nothing to correlate,
/// so the `id` is a constant.
///
/// Timeout-bounded like everything else in this module. The caller picks the timeout because the
/// deadlines differ by an order of magnitude: BlueZ holds a pairing exchange open while a phone
/// shows a spinner, whereas nothing is waiting on a name.
///
/// Returns the response with its error already turned into `Err`, so a caller only has to
/// deserialise the result it expected.
pub async fn ask(
    service: &str,
    socket: &Path,
    call: &proto::Call,
    timeout: Duration,
) -> Result<proto::Response, String> {
    tokio::time::timeout(timeout, ask_now(service, socket, call))
        .await
        .map_err(|_| format!("{service} did not answer in time"))?
}

async fn ask_now(
    service: &str,
    socket: &Path,
    call: &proto::Call,
) -> Result<proto::Response, String> {
    let stream = UnixStream::connect(socket)
        .await
        .map_err(|e| format!("cannot reach {service} at {}: {e}", socket.display()))?;
    let (read, mut write) = stream.into_split();
    let mut lines = BufReader::new(read).lines();

    let request = proto::Request::call(proto::Id::Number(1), call);
    let mut line = serde_json::to_vec(&request).map_err(|e| e.to_string())?;
    line.push(b'\n');
    write.write_all(&line).await.map_err(|e| e.to_string())?;
    write.flush().await.map_err(|e| e.to_string())?;

    let reply = lines
        .next_line()
        .await
        .map_err(|e| e.to_string())?
        .ok_or_else(|| format!("{service} closed the connection without answering"))?;

    let response: proto::Response = serde_json::from_str(&reply).map_err(|e| e.to_string())?;
    if let Some(error) = response.error {
        return Err(format!("{service} refused: {error}"));
    }
    Ok(response)
}

/// The write half of a live connection. The read half lives in a spawned task.
struct Conn {
    write: tokio::net::unix::OwnedWriteHalf,
}

/// Connections opened so far in one BLE session, made on demand.
///
/// Lazy rather than eager because most sessions touch one service: a phone asking for the
/// version has no reason to make `robotd` accept a connection it will never use. And because
/// connecting eagerly would mean a dead `robotd` delayed or failed a session that did not need
/// it.
///
/// **Keyed on the lane as well as the service**, which is what keeps a minutes-long update from
/// silencing everything else the client asks. Every daemon here serves one connection one request
/// at a time, so calls that share a connection share a queue — see [`Lane`] for the two orderings
/// a single connection per service broke. At most four sockets per service per session, and in
/// practice two.
pub struct Pool {
    sockets: Sockets,
    conns: HashMap<(Upstream, Lane), Conn>,
    /// Every reply and notification from every upstream, merged. Merging is safe because
    /// JSON-RPC correlates by `id`, which is the client's business — `btd` forwards lines
    /// without reading them.
    replies: mpsc::Sender<String>,
}

impl Pool {
    pub fn new(sockets: Sockets, replies: mpsc::Sender<String>) -> Self {
        Self {
            sockets,
            conns: HashMap::new(),
            replies,
        }
    }

    /// Send one line to `upstream` on `lane`'s connection, connecting first if needed.
    ///
    /// A daemon that restarted between two requests is ordinary here: `robotd` is the one an
    /// update restarts, and `updaterd` restarts itself from a release's postinstall hook. The
    /// connection from before the restart is still in the pool, its reader has already seen the
    /// socket close, and the first write into it fails. Those bytes never left, so they are written
    /// again on a fresh connection rather than reported. Reporting them told a phone that a daemon
    /// listening on a fresh socket was not answering, once per lane, after every update. Once and
    /// not in a loop: a daemon that is genuinely gone fails the reconnect, and that is the error
    /// worth reporting.
    pub async fn send(&mut self, upstream: Upstream, lane: Lane, line: &str) -> io::Result<()> {
        let key = (upstream, lane);
        let mut bytes = line.as_bytes().to_vec();
        bytes.push(b'\n');

        if !self.conns.contains_key(&key) {
            let conn = self.open(upstream, lane).await?;
            self.conns.insert(key, conn);
        }
        match self.write(key, &bytes).await {
            Err(e) if peer_is_gone(&e) => {
                let conn = self.open(upstream, lane).await?;
                self.conns.insert(key, conn);
                self.write(key, &bytes).await
            }
            done => done,
        }
    }

    /// One bounded write on the connection for `key`. Any failure drops that connection, so
    /// nothing keeps writing into a dead socket. This lane's only: the others may be perfectly
    /// alive, and a restart that broke one breaks the next write to each of them anyway.
    async fn write(&mut self, key: (Upstream, Lane), bytes: &[u8]) -> io::Result<()> {
        // Unwrap is sound: the caller inserted it, or `contains_key` held.
        let conn = self.conns.get_mut(&key).expect("connection present");
        let write = async {
            conn.write.write_all(bytes).await?;
            conn.write.flush().await
        };
        match tokio::time::timeout(WRITE_TIMEOUT, write).await {
            Ok(Ok(())) => Ok(()),
            Ok(Err(e)) => {
                self.conns.remove(&key);
                Err(e)
            }
            Err(_) => {
                self.conns.remove(&key);
                Err(io::Error::new(
                    io::ErrorKind::TimedOut,
                    "upstream write timed out",
                ))
            }
        }
    }

    async fn open(&self, upstream: Upstream, lane: Lane) -> io::Result<Conn> {
        let path = self.sockets.path(upstream);
        let stream = tokio::time::timeout(CONNECT_TIMEOUT, UnixStream::connect(path))
            .await
            .map_err(|_| io::Error::new(io::ErrorKind::TimedOut, "connect timed out"))??;

        let (read, write) = stream.into_split();
        let replies = self.replies.clone();
        // The lane is in the label because there are now several connections to each service,
        // and "Updater closed" without it names four possible sockets — including the progress
        // stream, whose closing is ordinary, and the operation lane, whose closing is not.
        let label = format!("{upstream:?}/{lane:?}");

        // The read half is pumped for the session's lifetime. Responses and notifications are
        // the same thing to us: a line to forward. That is what makes `update.subscribe`'s
        // progress stream work without any special case.
        tokio::spawn(async move {
            let mut lines = BufReader::new(read).lines();
            loop {
                match lines.next_line().await {
                    Ok(Some(line)) => {
                        // A full queue means the central cannot keep up. Give up on the line
                        // rather than the session: progress is advisory, and blocking here
                        // would stall every other upstream too.
                        if replies.try_send(line).is_err() {
                            tracing::debug!(upstream = %label, "dropped a line; client is behind");
                        }
                    }
                    Ok(None) => break,
                    Err(e) => {
                        tracing::debug!(upstream = %label, error = %e, "upstream read failed");
                        break;
                    }
                }
            }
            tracing::debug!(upstream = %label, "upstream closed");
        });

        tracing::debug!(upstream = ?upstream, lane = ?lane, path = %path.display(), "connected");
        Ok(Conn { write })
    }
}

/// Whether a write failed because the peer went away, rather than being slow or refusing. Only
/// these are worth one more try, because only these mean the bytes went to a daemon that is no
/// longer there. A timeout is a daemon that is there and stuck, and that is not retried.
fn peer_is_gone(e: &io::Error) -> bool {
    matches!(
        e.kind(),
        io::ErrorKind::BrokenPipe
            | io::ErrorKind::ConnectionReset
            | io::ErrorKind::ConnectionAborted
            | io::ErrorKind::NotConnected
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader};

    const TIMEOUT: Duration = Duration::from_secs(5);

    /// A fake `configd` that answers one request with `response` and hangs up.
    fn serve_once(path: &Path, response: proto::Response) -> tokio::task::JoinHandle<String> {
        let listener = tokio::net::UnixListener::bind(path).unwrap();
        tokio::spawn(async move {
            let (stream, _) = listener.accept().await.unwrap();
            let (read, mut write) = stream.into_split();
            let request = BufReader::new(read)
                .lines()
                .next_line()
                .await
                .unwrap()
                .unwrap();

            let mut line = serde_json::to_vec(&response).unwrap();
            line.push(b'\n');
            write.write_all(&line).await.unwrap();
            write.flush().await.unwrap();
            request
        })
    }

    /// The whole path `bluez` uses to learn what to advertise: ask `configd`, get a name back.
    #[tokio::test]
    async fn a_question_is_asked_and_the_answer_deserialised() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("configd.sock");
        let fake = serve_once(
            &path,
            proto::Response::ok(
                Some(proto::Id::Number(1)),
                &proto::SystemInfoResult {
                    name: "duck-7f3a".into(),
                    serial: Some("bb7b734a7717ac41".into()),
                    uptime_seconds: 12,
                    simulated: false,
                },
            ),
        );

        let info: proto::SystemInfoResult =
            ask("configd", &path, &proto::Call::SystemInfo, TIMEOUT)
                .await
                .unwrap()
                .result_as()
                .unwrap();
        assert_eq!(info.name, "duck-7f3a");

        // And the method on the wire was the one asked for, not merely something that parsed.
        let request = fake.await.unwrap();
        assert!(request.contains(proto::method::SYSTEM_INFO), "{request}");
    }

    /// `btd` is on the recovery path and must come up when the rest of the robot has not, so an
    /// absent `configd` is a reported error rather than a hang or a panic.
    #[tokio::test]
    async fn an_absent_service_is_an_error_naming_it() {
        let dir = tempfile::tempdir().unwrap();
        let err = ask(
            "configd",
            &dir.path().join("absent.sock"),
            &proto::Call::SystemInfo,
            TIMEOUT,
        )
        .await
        .unwrap_err();
        assert!(err.contains("cannot reach configd"), "{err}");
    }

    /// A service that refuses must not read as an answer: the caller would otherwise advertise
    /// whatever `result_as` makes of a null result.
    #[tokio::test]
    async fn a_refusal_is_an_error_rather_than_an_empty_answer() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("configd.sock");
        let _fake = serve_once(
            &path,
            proto::Response::err(
                Some(proto::Id::Number(1)),
                proto::Error::new(proto::code::INTERNAL_ERROR, "no"),
            ),
        );

        let err = ask("configd", &path, &proto::Call::SystemInfo, TIMEOUT)
            .await
            .unwrap_err();
        assert!(err.contains("configd refused"), "{err}");
    }
    /// The daemon restarted between two requests.
    ///
    /// The comment on the write path says a broken pipe is ordinary, the daemon restarted, and
    /// the next call reconnects. It is the call *after* the next: the first write after a restart
    /// went into the socket the old daemon closed, failed, and the phone was told the service was
    /// not answering while it was listening on a fresh socket the whole time. The pool's own
    /// reader had already seen the socket close and told nobody.
    ///
    /// On the BLE update path this is `updaterd` restarting itself from the release's postinstall
    /// hook, and the phone's next `update.status` failing for it.
    #[tokio::test]
    async fn a_restarted_daemon_gets_the_next_request_not_the_one_after() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("updaterd.sock");
        let sockets = Sockets {
            updater: path.clone(),
            robot: dir.path().join("robotd.sock"),
            config: dir.path().join("configd.sock"),
        };
        let (replies, mut forwarded) = mpsc::channel(8);
        let mut pool = Pool::new(sockets, replies);

        let before = serve_once(
            &path,
            proto::Response::ok(Some(proto::Id::Number(1)), &serde_json::json!({})),
        );
        pool.send(
            Upstream::Updater,
            Lane::Prompt,
            r#"{"jsonrpc":"2.0","id":1,"method":"update.status"}"#,
        )
        .await
        .unwrap();
        assert!(
            forwarded.recv().await.is_some(),
            "the first answer is forwarded"
        );
        // The daemon has answered and hung up: it is restarting.
        before.await.unwrap();

        // And it is back, listening on a fresh socket at the same path.
        std::fs::remove_file(&path).unwrap();
        let after = serve_once(
            &path,
            proto::Response::ok(Some(proto::Id::Number(2)), &serde_json::json!({})),
        );
        pool.send(
            Upstream::Updater,
            Lane::Prompt,
            r#"{"jsonrpc":"2.0","id":2,"method":"update.status"}"#,
        )
        .await
        .expect("a daemon that is back must get the request, not a broken pipe");
        let request = after.await.unwrap();
        assert!(request.contains(r#""id":2"#), "{request}");
        assert!(
            forwarded.recv().await.is_some(),
            "and its answer is forwarded"
        );
    }
}

```

### File: `btd/systemd/btd.service` (93 lines, ~994 tokens)
```service
# btd — the BLE front door onto the robot API.
#
# Install to /etc/systemd/system/btd.service.
#
# Two properties follow from btd being part of the recovery path (docs/architecture.md §1.1)
# and must be preserved:
#
#   1. NO dependency on robotd or updaterd, in either direction. btd must answer when the
#      robot does not — that is most of why it exists. It reaches both over their sockets,
#      and a missing socket is a normal answer it reports rather than a reason not to start.
#   2. It stays UNPRIVILEGED. btd is the process that parses bytes from anyone in radio
#      range; configd is the one that runs as root. Putting the parser on the safe side of
#      that boundary matters more than hardening the dispatcher.

[Unit]
Description=Robot BLE transport adapter
Documentation=file:///opt/robot/daemon/current/docs/architecture.md

# bluetoothd is a hard requirement — btd speaks to BlueZ over D-Bus and has nothing to do
# without it. `Wants` rather than `Requires`: if bluetoothd is slow or restarts, btd waits
# and retries for an adapter rather than failing (see ADAPTER_RETRY in src/bluez.rs).
#
# On the Radxa, hci0 does not exist until ~73s after power-on: aic-bluetooth.service attaches
# the AIC8800's UART late, and bluetooth.service itself spends ~26s blocked behind dbus. So
# ordering after bluetooth.service is necessary but nowhere near sufficient, and the retry
# loop is what actually makes startup work.
After=dbus.service bluetooth.service
Wants=bluetooth.service

# No network dependency: BLE is the transport that has to work when the network does not.
After=local-fs.target

[Service]
Type=exec
ExecStart=/opt/robot/daemon/current/bin/btd

# Unprivileged, unlike robotd — btd touches no hardware directly, only D-Bus and two unix
# sockets, so there is no excuse for root here.
#
# `robot` is what gets it through the 0660 sockets updaterd and robotd listen on.
#
# `bluetooth` is what should get it through BlueZ's D-Bus policy — but VERIFY THAT ON THE
# BOARD before trusting it: Debian's /usr/share/dbus-1/system.d/bluetooth.conf grants
# send_destination="org.bluez" to root and to at_console, and whether a group covers a
# session-less daemon differs between images. If btd logs a D-Bus permission error on
# startup, a drop-in policy granting this user access to org.bluez is the fix — not running
# it as root.
#
# The users and groups must exist or the unit fails to start; see sysusers.d/btd.conf,
# installed alongside.
User=btd
Group=btd
SupplementaryGroups=robot bluetooth

Restart=always
RestartSec=5s

# Tighter than robotd can be, because this process has no hardware to reach. It needs D-Bus
# (a unix socket) and two unix sockets, and nothing else.
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes
PrivateDevices=yes
ProtectKernelTunables=yes
ProtectKernelModules=yes
ProtectControlGroups=yes
RestrictSUIDSGID=yes
RestrictAddressFamilies=AF_UNIX
RestrictNamespaces=yes
LockPersonality=yes
MemoryDenyWriteExecute=yes
SystemCallFilter=@system-service
SystemCallErrorNumber=EPERM
CapabilityBoundingSet=

# stderr → journal; level via RUST_LOG. The startup identity line (version, revision, exe
# path) is at `warn`, so it survives RUST_LOG=warn on a long-running board.
Environment=RUST_LOG=info
StandardOutput=journal
StandardError=journal

# Where this daemon publishes what it is running: /run/btd/identity.json, read by
# `robotctl health` and by updaterd's startup check.
#
# `RuntimeDirectory=` rather than a path this unit is granted: it is the only mechanism that both
# creates the directory owned by this unit's User= *and* survives ProtectSystem=strict, which
# otherwise leaves the whole filesystem read-only. systemd also removes it when the unit stops, so a
# stopped daemon cannot leave behind an identity claiming to be running.
RuntimeDirectory=btd

[Install]
WantedBy=multi-user.target

```

### File: `btd/systemd/sysusers.d/btd.conf` (22 lines, ~311 tokens)
```conf
# Creates the `btd` system user and group.
#
# Install to /usr/lib/sysusers.d/btd.conf; systemd-sysusers creates them at boot, or run
# `systemd-sysusers` once by hand.
#
# btd runs as its own unprivileged user rather than root, because it is the process that
# parses bytes arriving from anyone in radio range (docs/architecture.md §1.1). Its access
# comes entirely from group membership, granted in btd.service:
#
#   robot      — reaches updaterd's, robotd's and configd's 0660 sockets
#   bluetooth  — should reach org.bluez over D-Bus; verify on the image
#
# Note what group membership deliberately does NOT confer: being in `robot` lets btd *talk* to
# those daemons, not change anything. Change authority is granted per service and by name —
# `allow_users = ["btd"]` in updater.toml, `--allow-user btd` in configd.service.
#
# Naming this service is a narrow claim: "btd may relay a request from the app". Naming the
# `robot` group instead would collapse "may read status" and "may replace the firmware" into one
# permission, and both services have a test refusing exactly that (§2.2, btd/src/route.rs).
#
# btd.service will fail to start if this user does not exist.
u btd - "Robot BLE transport adapter" - -

```

### File: `configd/Cargo.toml` (48 lines, ~608 tokens)
```toml
[package]
name = "configd"
version.workspace = true
edition.workspace = true
license.workspace = true
description = "Wifi and robot identity — the config service"

# Its own service rather than part of robotd, because config must be reachable when robotd is
# dead: provisioning wifi is exactly what a client needs when things are broken
# (architecture.md §3.1). And not part of btd, because btd owns nothing (§4.1) — an SDK should
# not have to go through Bluetooth to set a robot's name.
#
# It stores no credentials. NetworkManager owns those.
[dependencies]
duck-ipc-proto = { path = "../duck-ipc-proto" }
serde.workspace = true
serde_json.workspace = true
# `process` is for reading the journal: `logs` spawns `journalctl` rather than linking libsystemd
# for one read-only query. See that module for why.
tokio = { workspace = true, features = ["rt-multi-thread", "macros", "net", "io-util", "time", "sync", "signal", "process"] }
clap.workspace = true
tracing.workspace = true
tracing-subscriber = { workspace = true, features = ["env-filter"] }
async-trait.workspace = true
libc = "0.2"

# For the default name derived from the SoC serial (see `identity`). A digest rather than std's
# hasher because std's output is not stable across Rust releases, and a toolchain bump must not
# rename every robot. Already in the graph via the updater's release verification.
sha2 = "0.11.0"

# NetworkManager and logind, both Linux-only. As with btd, the crate must still build and test on
# a macOS laptop — `cargo test` there is the onboarding path — so the backend sits behind a trait
# with an in-memory fake and the D-Bus client is not in the graph off-Linux.
#
# `zbus` rather than the `dbus` crate: pure Rust, so no vendored C to cross-compile, and NM's
# settings are a nested a{sa{sv}} that zvariant expresses without ceremony. The cost is that the
# shipped artifact carries two D-Bus stacks, since btd links libdbus through bluer. Worth
# revisiting if bluer ever grows a zbus backend.
[target.'cfg(target_os = "linux")'.dependencies]
zbus = "5"
# For `StreamExt` over zbus's signal streams. zbus 5 re-exports `futures_core` (the `Stream` trait)
# but not `futures_util` (the combinators), and the connect path has to consume NM's `StateChanged`
# signal to learn *why* an activation failed. Already in the graph via btd.
futures = "0.3"

[dev-dependencies]
tempfile = "3.27.0"

```

### File: `configd/src/bluez.rs` (1122 lines, ~14160 tokens)
```rs
//! Gamepad pairing, over BlueZ's D-Bus API. Linux only.
//!
//! `zbus` rather than `bluer`, which `btd` uses: `bluer` links libdbus (vendored, built with `cc`)
//! and this crate already has a pure-Rust D-Bus stack for NetworkManager. Adding `bluer` here would
//! put a second C dependency in `configd` to make four method calls.
//!
//! ## The order, and why the state decides rather than the return values
//!
//! **Which order depends on the transport**, and the two are opposite:
//!
//!  - an **LE** pad (Xbox): `connect` **before** `pair`, and `trust` after both. Leading with
//!    `Pair()` on an Xbox controller returns `AuthenticationCanceled`; that ordering comes from
//!    `microduck_runtime`'s notes and is the one that works on this board.
//!  - a **BR/EDR** pad (a "Pro Controller" Switch clone, and by the specification a DualShock or a
//!    DualSense): `pair` **before** `connect`, then `trust`. See [the transport section](#which-transport-and-what-that-leaves-untested)
//!    for what the other order does to it.
//!
//! `Snapshot::is_classic` decides, on whether BlueZ reports a `Class`. The rule used to live in a
//! provisioning script's comments and in whoever had done it before; now it is here, once, with the
//! reason attached.
//!
//! On the LE path the order is **tried, not enforced**, because BlueZ's replies do not describe what
//! happened:
//!
//!  - `Connect()` on a device BlueZ has never bonded with can answer
//!    `br-connection-profile-unavailable` — there is no profile to connect to *yet*. Refusing there
//!    would reject a pad that `Pair()` would have bonded a moment later, so it is soft-failed. The
//!    `br-` prefix is BlueZ trying BR/EDR first and finding nothing there; the pad this was seen
//!    against bonds over LE, so that error names a transport which was never going to carry it.
//!  - `Connect()` on a pad that *does* bond **returns before the bond has completed.** A HID profile
//!    requires an encrypted link, so connecting triggers bonding, and it lands a moment afterwards.
//!  - `Pair()` on a bond already in flight **never answers.** Not `AlreadyExists` — outstanding,
//!    until the timeout.
//!
//! Those last two compose into the failure this was shipped with: read `Paired` straight after
//! `Connect()`, see `false` about a bond in flight, call `Pair()`, wait 30 seconds for a reply that
//! is never coming, and return a timeout about a pad that is by then paired — having never reached
//! `set_trusted`. It presented as "the first pair times out, the second works instantly", the second
//! being fast because the bond was already there.
//!
//! So `Paired` turning true is the ground truth for "this worked". `Connect()` gets
//! [`BOND_SETTLE`] to produce it on its own, and the `Pair()` that follows is raced against the same
//! property rather than believed.
//!
//! Discovery is stopped before connecting, deliberately: BlueZ will accept a `Connect()` during an
//! active scan and it fails intermittently, which presents as a pad that pairs on the second
//! attempt and looks like flaky hardware.
//!
//! ## The agent, and why it claims the default role
//!
//! Pairing needs an agent — something for bluetoothd to ask "is this allowed" — and `btd` already
//! registers one as the **default** agent for the phone path. This registers a second agent scoped
//! to the pad being paired, and takes the default role for the length of the pairing window.
//!
//! Taking the role is not optional, for two reasons that compound. bluetoothd pushes an IO
//! capability down to the adapter from the default agent only, so a non-default `NoInputNoOutput`
//! leaves the adapter declaring input and display — which puts MITM in the pairing request and makes
//! SMP choose numeric comparison over just-works. And bluetoothd prefers the agent belonging to the
//! connection that called `Pair()`, which on the path that works is nobody: `Connect()` bonds the pad
//! on its own and the `Pair()` fallback below never runs. So the confirmation is raised against the
//! default agent, and a `configd` that had not claimed the role would never see it — the pad waits
//! out the link supervision timeout and BlueZ reports `AuthenticationCanceled`.
//!
//! `unregister_agent` hands the role back, and `btd` only holds it when pairing is required at all,
//! so `configd` answers for the pairings it starts and `btd` keeps answering for everything else.
//!
//! It is scoped to one device path and rejects anything else, so a pairing request arriving from an
//! unrelated device while the window is open is refused rather than auto-accepted. A pad is
//! just-works — there is no passkey to check — so "accept this one device, for these few seconds,
//! because a human asked" is the entire authorisation, and narrowing it to the device is the only
//! part of that this code controls.
//!
//! ## The board setting that decides whether any of this can work
//!
//! `Privacy` in `/etc/bluetooth/main.conf`, which `scripts/setup-board.sh` sets to `device`.
//!
//! BlueZ defaults to `off`, and `off` works on some Radxa Zero 3W units. On the others a pad will
//! not bond under `off` at all, and only `device` does. Nothing measurable separates the two
//! populations, so `device` is set on every board.
//!
//! Under `device`, a pad cannot form a **new** bond while `btd` advertises. An existing bond is
//! unaffected, which is why `robotctl pad pair` stops `btd` for the pairing window rather than
//! anything here changing — see `BtdPaused` in `robotctl/src/main.rs`, and
//! `docs/project/pad-minimal-pairing.md` for the bisect.
//!
//! The failure that looks like this file is at fault, and is not:
//!
//! ```text
//! SMP: Pairing Public Key ×2 · Confirm · Random ×2 · DHKey Check
//! > ACL Data RX: SMP: Pairing Failed — Reason: DHKey check failed (0x0b)
//! ```
//!
//! The DHKey check is computed over both devices' addresses, and privacy makes the adapter pair from
//! a resolvable private one — while `btd` advertises from the same adapter. That is the interaction
//! above, seen from SMP. It was once read as evidence that `device` itself broke pairing, which is
//! how this tree came to set `off` and break a pad on every board provisioned after.
//!
//! Worth knowing because the symptom is indistinguishable from the ones this file *can* cause:
//! retrying does not help, `JustWorksRepairing` does not help, and neither does clearing the bond on
//! either side. `bluetoothctl` fails identically, which is what places it below anything here.
//!
//! And one more thing that mimics it exactly: an Xbox pad holds **one** host bond, so a
//! half-completed attempt leaves it holding a key this adapter no longer has. Reset the pad against
//! a laptop before concluding anything about a board.
//!
//! It is also the first clue about which transport is in play: resolvable private addresses are an LE
//! mechanism, so a setting that breaks bonding this way can only be breaking an LE bond.
//!
//! ## Which transport, and what that leaves untested
//!
//! Nothing here picks one. `StartDiscovery()` runs with no filter, so BlueZ's default `auto` sweeps
//! BR/EDR and LE together, and every property `Snapshot` reads is optional partly because the two
//! transports present different ones.
//!
//! The Xbox pad is **LE-only**. Its bond stores long-term keys and no `[LinkKey]`, and BlueZ reports
//! no `Class` for it at all:
//!
//! ```text
//! # /var/lib/bluetooth/<adapter>/<pad>/info
//! SupportedTechnologies=LE;
//! [IdentityResolvingKey]
//! [PeripheralLongTermKey]
//! ```
//!
//! The first **BR/EDR** pad arrived on 2026-09-09: a no-name "Pro Controller", a clone of Nintendo's
//! Switch Pro Controller down to the modalias (`usb:v057Ep2009`), which is what makes the kernel's
//! `hid-nintendo` bind it and expose it as "Nintendo Switch Pro Controller" on evdev. BlueZ reports
//! it with `Class: 0x2508` — peripheral, gamepad — and derives `Icon: input-gaming` from that, so
//! [`looks_like_a_gamepad`] recognises it on two signals, and the class-of-device branch has now
//! fired on hardware. Only the HID and PnP UUIDs, no LE at all.
//!
//! What the LE order does to it, from `configd`'s own journal (2026-09-07, an earlier unit of the
//! same pad): `Connect()` on the unbonded pad spends ten seconds and answers
//! `br-connection-create-socket`; the `Pair()` fallback then answers
//! `ConnectionAttemptFailed: Page Timeout`. The pad has left pairing mode — a rejected classic
//! connection is enough to make it stop page-scanning — and every retry repeats the pair. Reproduced
//! by hand, the same order (`bluetoothctl connect`, which bonds as a side effect, then `trust`) goes
//! one step further and ends in the state that is hardest to read: `Paired: yes`, `Connected: yes`,
//! a solid light on the pad, `pad status` saying connected — and **no input device**, so `padd` waits
//! for a pad that BlueZ insists is there. `pair` → `connect` → `trust` works every time, so that is
//! what `bond` does when `Class` is present. A pad already in the broken state is recovered with
//! `pad forget` and a fresh `pad pair`.
//!
//! **The clone is also two devices at once.** In pairing mode it advertises an LE face,
//! `BLE Controller_280609` at `98:B6:ED:28:06:09` — no class, no appearance, matched by the name
//! heuristic alone — and the BR/EDR face, `Pro Controller` at `98:B6:E9:28:06:09`. The LE face is
//! reported first — and, after the adapter power cycle `pad pair` performs on this board, several
//! seconds first. The first `robotctl pad pair` on this branch (2026-09-09) stopped on it, took the
//! LE order, hung [`BOND_TIMEOUT`] in `Connect()`, and by the time `Pair()` was tried the temporary
//! object was gone: `UnknownObject: Method "Pair" ... doesn't exist`. A two-second grace after the
//! first match did not help; the BR/EDR face was still not in the tree. So `find` now ends the
//! search early only on a match the radio classified — the LE face's name-only match is kept as a
//! fallback but never stops the sweep — and `one_face_per_pad` folds candidates that share their
//! unit octets into the classic one before the ambiguity rule sees them.
//!
//! Discovery stays on `auto`, so BlueZ sweeps both transports and a Pro Controller and an Xbox pad
//! are both found by the same search.
//!
//! Once bonded, a classic pad's reports are the kernel's business and not bluetoothd's:
//! `scripts/setup-board.sh` sets `UserspaceHID=false` in `input.conf`, because the default relays
//! this pad's ~200 packets/s of IMU through bluetoothd and uhid at 16% of a core. Nothing in this
//! file depends on which path is in use; it is noted here because it is the other half of what
//! "supporting a classic pad" turned out to mean.
//!
//! ## Where this has and has not run
//!
//! **Run against a real BlueZ on a Radxa Zero 3W with an Xbox Wireless Controller**, which is where
//! everything above about asynchronous bonding comes from. What has been seen work: discovery finds
//! the pad and the heuristic identifies it — on `Icon`, which BlueZ derived from the LE appearance —
//! the bond completes, `Trusted` sticks, the pad reconnects by itself across a reboot, `padd` drives
//! from it, and `pad forget` drops it.
//!
//! That reconnection is worth naming rather than assuming, because over LE the *robot* is the one
//! that re-initiates: the adapter scans as a central for a bonded peripheral while `btd` advertises
//! as a peripheral itself. Both roles at once hold on this board's radio.
//!
//! **And against the Pro Controller clone**, 2026-09-09, on the board above: `pad pair` with the pad
//! in pairing mode found the classic face, bonded it and connected it in eight seconds — `bonded
//! (classic)`, `connected`, `gamepad paired and trusted` — and `padd` drove from it. An Xbox pad
//! paired a minute later through the unchanged LE path.
//!
//! What has **not** been exercised on hardware: a DualSense, two pads in pairing mode at once, and
//! pairing by explicit address.
//!
//! And one case that cannot be fixed from here: `pad forget` removes only the robot's half of the
//! bond. A pad that still holds its half will not pair again until it is put back into pairing mode
//! or bonded to something else, and it reports the same `AuthenticationFailed` as everything above.

use std::collections::HashMap;
use std::time::Duration;

use async_trait::async_trait;
use duck_ipc_proto as proto;
use zbus::names::OwnedInterfaceName;
use zbus::zvariant::{ObjectPath, OwnedObjectPath, OwnedValue};

use crate::pad::{Evidence, PadResult, Pads, gamepad_evidence, same_pad};

/// Where our pairing agent lives on the bus. Any path we own will do; this one says whose it is.
const AGENT_PATH: &str = "/com/pollenrobotics/configd/pad_agent";

/// `NoInputNoOutput` — the robot has no keypad and no display, which is a fact about the hardware
/// rather than a choice. It is also what makes a pad's pairing just-works.
const AGENT_CAPABILITY: &str = "NoInputNoOutput";

/// How long BlueZ gets to finish bonding once a pad has been found.
///
/// Separate from the caller's discovery window, because they measure different things: the window
/// is how long to wait for a human to hold the sync button, this is how long the radio gets after
/// the device is already in hand. BlueZ's own pairing timeout is 60s; this stays inside it so the
/// answer comes from here rather than from a dropped D-Bus call.
const BOND_TIMEOUT: Duration = Duration::from_secs(30);

/// How long to let a bond triggered by `Connect()` finish on its own before asking for one.
///
/// Bonding is asynchronous and lands a moment after `Connect()` returns, so this is the window in
/// which "it is already happening" is distinguished from "it is not going to". Measured against a
/// real Xbox controller, it completes inside a second; five is margin, and the cost of it being too
/// short is a `Pair()` call on a bond in flight, which never answers.
const BOND_SETTLE: Duration = Duration::from_secs(5);

/// How often to re-read `Paired` while waiting for a bond.
const BOND_POLL: Duration = Duration::from_millis(200);

/// How long to keep sweeping after the first classified, unbonded pad turns up, for the rest of it.
///
/// A pad can be two devices — the Pro Controller clones advertise an LE face and a BR/EDR face.
/// The classified one is the one worth having, and this is a short courtesy for the case where the
/// two arrive close together and the other happens to be classified too. It is **not** what
/// protects against the LE face: that face has nothing but a name, and a name-only match never
/// ends the search early at all — see `find`. Measured: after the adapter power cycle `pad pair`
/// performs on this board, the LE face was in BlueZ's tree within two seconds and the BR/EDR face
/// was not, so no grace short enough to be free would have caught it.
const SIBLING_GRACE: Duration = Duration::from_secs(1);

/// How often to re-read the object tree while looking for a pad.
///
/// Polling rather than `InterfacesAdded`, which sounds like the right signal and is not: BlueZ emits
/// it only for devices it has never seen, so a pad that was paired and forgotten — the exact case
/// someone is retrying — stays in the cache and never announces itself again.
const DISCOVERY_POLL: Duration = Duration::from_millis(500);

#[zbus::proxy(interface = "org.bluez.Adapter1", default_service = "org.bluez")]
trait Adapter {
    fn start_discovery(&self) -> zbus::Result<()>;
    fn stop_discovery(&self) -> zbus::Result<()>;
    fn remove_device(&self, device: &ObjectPath<'_>) -> zbus::Result<()>;

    #[zbus(property)]
    fn powered(&self) -> zbus::Result<bool>;
    #[zbus(property)]
    fn set_powered(&self, on: bool) -> zbus::Result<()>;
}

#[zbus::proxy(interface = "org.bluez.Device1", default_service = "org.bluez")]
trait Device {
    fn connect(&self) -> zbus::Result<()>;
    fn pair(&self) -> zbus::Result<()>;

    #[zbus(property)]
    fn set_trusted(&self, on: bool) -> zbus::Result<()>;
}

#[zbus::proxy(
    interface = "org.bluez.AgentManager1",
    default_service = "org.bluez",
    default_path = "/org/bluez"
)]
trait AgentManager {
    fn register_agent(&self, agent: &ObjectPath<'_>, capability: &str) -> zbus::Result<()>;
    fn unregister_agent(&self, agent: &ObjectPath<'_>) -> zbus::Result<()>;
    fn request_default_agent(&self, agent: &ObjectPath<'_>) -> zbus::Result<()>;
}

/// An agent that says yes to exactly one device.
///
/// Every handler that could authorise something checks the path it was called about. The ones that
/// would need a keypad refuse: this robot cannot enter a passkey, and answering `0000` on its behalf
/// would be inventing a credential.
struct PairingAgent {
    device: OwnedObjectPath,
}

impl PairingAgent {
    fn permit(&self, device: &ObjectPath<'_>, what: &str) -> zbus::fdo::Result<()> {
        if device.as_str() == self.device.as_str() {
            tracing::info!(device = device.as_str(), what, "authorising, as asked");
            return Ok(());
        }
        // Not the pad someone is pairing. Refusing is the point of scoping the agent: an open
        // pairing window on a robot in a room full of Bluetooth devices should not accept them all.
        tracing::warn!(
            device = device.as_str(),
            expected = self.device.as_str(),
            what,
            "refusing: not the device being paired"
        );
        Err(zbus::fdo::Error::AccessDenied(
            "this robot is not pairing with that device".into(),
        ))
    }
}

#[zbus::interface(name = "org.bluez.Agent1")]
impl PairingAgent {
    fn release(&self) {
        tracing::debug!("pairing agent released");
    }

    /// The one BlueZ actually calls for a just-works bond.
    fn request_authorization(&self, device: ObjectPath<'_>) -> zbus::fdo::Result<()> {
        self.permit(&device, "bond")
    }

    /// Asked per profile once bonded — HID, in a pad's case.
    fn authorize_service(&self, device: ObjectPath<'_>, uuid: String) -> zbus::fdo::Result<()> {
        tracing::debug!(uuid, "service authorisation requested");
        self.permit(&device, "service")
    }

    /// Numeric comparison, when the remote end has a display. Nothing here can compare anything, so
    /// accepting is the only answer that lets a pad bond — and the passkey is logged so it is at
    /// least on the record.
    fn request_confirmation(&self, device: ObjectPath<'_>, passkey: u32) -> zbus::fdo::Result<()> {
        tracing::info!(passkey, "confirmation requested with no way to compare it");
        self.permit(&device, "confirmation")
    }

    /// Refused rather than answered with a guess. With `NoInputNoOutput` declared, BlueZ should
    /// never ask — and if it does, the device wants a credential this robot does not have. Sending
    /// `0000` would be inventing one, and it would fail anyway on anything made this decade.
    fn request_pin_code(&self, device: ObjectPath<'_>) -> zbus::fdo::Result<String> {
        tracing::warn!(
            device = device.as_str(),
            "a PIN was requested; this robot has no keypad"
        );
        Err(zbus::fdo::Error::NotSupported(
            "this robot cannot enter a PIN".into(),
        ))
    }

    /// As above, for LE passkey entry. See `btd::pairing` for the long version of why a headless
    /// robot cannot take part in it.
    fn request_passkey(&self, device: ObjectPath<'_>) -> zbus::fdo::Result<u32> {
        tracing::warn!(
            device = device.as_str(),
            "a passkey was requested; this robot has no keypad"
        );
        Err(zbus::fdo::Error::NotSupported(
            "this robot cannot enter a passkey".into(),
        ))
    }

    /// Display handlers: nothing to display on, so they only reach the journal. Implemented rather
    /// than omitted, because a missing method makes BlueZ fail the bond with a D-Bus error that
    /// says nothing about the cause.
    fn display_passkey(&self, device: ObjectPath<'_>, passkey: u32, entered: u16) {
        tracing::info!(
            device = device.as_str(),
            passkey,
            entered,
            "passkey to display, on a robot with no display"
        );
    }

    fn display_pin_code(&self, device: ObjectPath<'_>, pincode: String) {
        tracing::info!(
            device = device.as_str(),
            pincode,
            "PIN to display, on a robot with no display"
        );
    }

    fn cancel(&self) {
        tracing::warn!("the remote end cancelled pairing");
    }
}

/// One object's interfaces, as `GetManagedObjects` reports them: interface name to properties.
type Interfaces = HashMap<OwnedInterfaceName, HashMap<String, OwnedValue>>;

/// One interface's properties, by name.
///
/// A scan rather than a lookup: the keys are `OwnedInterfaceName`, which cannot be borrowed as a
/// `&str` for `HashMap::get`, and an object carries three or four interfaces.
fn interface<'a>(
    interfaces: &'a Interfaces,
    name: &str,
) -> Option<&'a HashMap<String, OwnedValue>> {
    interfaces
        .iter()
        .find(|(iface, _)| iface.as_str() == name)
        .map(|(_, props)| props)
}

/// What BlueZ currently knows about one device.
///
/// A snapshot from `GetManagedObjects` rather than a live proxy: every field is read together, in
/// one round trip, and there is no cache to be stale. The properties are all optional because BlueZ
/// omits what it does not know — a device seen in discovery but never queried has no `Name`.
#[derive(Debug, Clone)]
struct Snapshot {
    path: OwnedObjectPath,
    mac: String,
    name: String,
    icon: Option<String>,
    class: Option<u32>,
    appearance: Option<u16>,
    paired: bool,
    trusted: bool,
    connected: bool,
}

impl Snapshot {
    fn read(path: &OwnedObjectPath, props: &HashMap<String, OwnedValue>) -> Option<Self> {
        let get = |key: &str| props.get(key).cloned();
        let text = |key: &str| get(key).and_then(|v| String::try_from(v).ok());
        let flag = |key: &str| {
            get(key)
                .and_then(|v| bool::try_from(v).ok())
                .unwrap_or(false)
        };

        Some(Self {
            path: path.clone(),
            // No address, no device: everything here is keyed on it, and a client cannot act on a
            // pad it cannot name.
            mac: text("Address")?,
            // `Alias` is what BlueZ shows and falls back to `Name`, so it is the better of the two
            // — but it is also what a rename would have changed, and either is better than empty.
            name: text("Alias").or_else(|| text("Name")).unwrap_or_default(),
            icon: text("Icon"),
            class: get("Class").and_then(|v| u32::try_from(v).ok()),
            appearance: get("Appearance").and_then(|v| u16::try_from(v).ok()),
            paired: flag("Paired"),
            trusted: flag("Trusted"),
            connected: flag("Connected"),
        })
    }

    /// Does this pad bond over BR/EDR rather than LE?
    ///
    /// `Class` is the tell: it is the classic class-of-device, which an LE-only device has no way
    /// to present, and BlueZ reports it from the inquiry response before anything else is known
    /// about the device. `AddressType` does not separate the two — an Xbox pad's is `public` too.
    /// The order `bond` tries depends on this, and the module docs say why.
    fn is_classic(&self) -> bool {
        self.class.is_some()
    }

    fn evidence(&self) -> Option<Evidence> {
        gamepad_evidence(
            &self.name,
            self.icon.as_deref(),
            self.class,
            self.appearance,
        )
    }

    fn is_gamepad(&self) -> bool {
        self.evidence().is_some()
    }

    /// Unbonded, and a pad on the radio's word rather than its name's — the only kind of match the
    /// search ends early on.
    fn is_fresh_and_classified(&self) -> bool {
        !self.paired && self.evidence() == Some(Evidence::Classified)
    }

    fn as_pad(&self) -> proto::Pad {
        proto::Pad {
            mac: self.mac.clone(),
            name: self.name.clone(),
            paired: self.paired,
            trusted: self.trusted,
            connected: self.connected,
        }
    }
}

/// The result of one search: what looked like a pad, and everything the radio saw.
struct Found {
    matches: Vec<Snapshot>,
    seen: Vec<Snapshot>,
}

/// Pads, through bluetoothd.
pub struct BlueZ {
    bus: zbus::Connection,
    /// One pairing at a time. Two concurrent ones would fight over discovery and over the agent
    /// path, and there is only one adapter and one human holding one pad.
    pairing: tokio::sync::Mutex<()>,
}

impl BlueZ {
    pub async fn new() -> Result<Self, String> {
        let bus = zbus::Connection::system()
            .await
            .map_err(|e| e.to_string())?;
        Ok(Self {
            bus,
            pairing: tokio::sync::Mutex::new(()),
        })
    }

    /// Everything bluetoothd is managing, by object path and interface.
    async fn objects(&self) -> PadResult<HashMap<OwnedObjectPath, Interfaces>> {
        let manager = zbus::fdo::ObjectManagerProxy::new(&self.bus, "org.bluez", "/")
            .await
            .map_err(|e| format!("cannot reach bluetoothd on the system bus: {e}"))?;
        manager
            .get_managed_objects()
            .await
            .map_err(|e| format!("bluetoothd would not list its objects: {e}"))
    }

    /// The first adapter, powered on.
    ///
    /// "First" rather than "hci0 by name": the board has one adapter and naming it would be a
    /// guess that happens to be right. An absent adapter is a normal answer early in a boot — on
    /// this board `hci0` does not exist until roughly 73 seconds after power-on.
    async fn adapter(&self) -> PadResult<Option<AdapterProxy<'static>>> {
        let mut paths: Vec<OwnedObjectPath> = self
            .objects()
            .await?
            .into_iter()
            .filter(|(_, interfaces)| interface(interfaces, "org.bluez.Adapter1").is_some())
            .map(|(path, _)| path)
            .collect();
        // Sorted so "the first adapter" means the same one on every call rather than whatever the
        // hash map yielded.
        paths.sort_by(|a, b| a.as_str().cmp(b.as_str()));

        let Some(path) = paths.into_iter().next() else {
            return Ok(None);
        };

        let adapter = AdapterProxy::builder(&self.bus)
            .path(path)
            .map_err(|e| e.to_string())?
            .build()
            .await
            .map_err(|e| e.to_string())?;

        // An adapter that is present but off finds nothing, and reports it as "no pad" — which
        // sends someone looking at the pad instead of at the radio.
        if !adapter.powered().await.unwrap_or(false) {
            adapter
                .set_powered(true)
                .await
                .map_err(|e| format!("cannot power on the Bluetooth adapter: {e}"))?;
        }
        Ok(Some(adapter))
    }

    /// Devices bluetoothd knows about, newest state each call.
    async fn devices(&self) -> PadResult<Vec<Snapshot>> {
        let objects = self.objects().await?;
        Ok(objects
            .iter()
            .filter_map(|(path, interfaces)| {
                Snapshot::read(path, interface(interfaces, "org.bluez.Device1")?)
            })
            .collect())
    }

    /// Look for a gamepad until `deadline`, then give up.
    ///
    /// **An unbonded pad wins, and the search waits for one.** A robot that already has a pad bonded
    /// still sees it in every sweep — it is in BlueZ's cache whether or not anyone touched it — so
    /// returning on the first match would answer "you already have a pad" to someone standing there
    /// with a second one in pairing mode. That made adding a pad impossible without forgetting the
    /// first, which is the wrong shape: a robot may have several pads bonded, and `padd` drives
    /// whichever connects.
    ///
    /// So with no address given, the sweep only ends early on a candidate that is **not yet paired
    /// and classified by the radio** — icon, class or appearance, not its name alone. A name-only
    /// match is kept and used if nothing better arrives by the deadline, but it does not stop the
    /// search: the Pro Controller clone's LE face is exactly such a match, it is reported seconds
    /// before the BR/EDR face that actually pairs, and stopping on it cost every attempt a
    /// thirty-second hang and a dead object. Otherwise the sweep runs to the deadline and reports
    /// what it has, which may be the pad already bonded. The cost is that re-running `pad pair` with nothing new in pairing mode takes the whole
    /// window before saying "already paired" — `--timeout` shortens it.
    ///
    /// An explicit address ends the sweep as soon as it appears, paired or not: the caller has named
    /// what they want and there is nothing to prefer.
    ///
    /// Also returns **everything else it saw**, which matters more than it looks: BlueZ reports a
    /// freshly-discovered device with an address and often nothing else — no `Name`, no `Class`, no
    /// `Icon` — because those need a further exchange. A pad that never resolves any of them is
    /// invisible to [`Snapshot::is_gamepad`], and a bare "no gamepad found" would leave someone with
    /// no way to learn the address that `--mac` needs. So the refusal carries the list.
    async fn find(&self, mac: Option<&str>, timeout: Duration) -> PadResult<Found> {
        let deadline = tokio::time::Instant::now() + timeout;
        // When the first classified, unbonded candidate was seen, so the sweep can run
        // [`SIBLING_GRACE`] past it before deciding.
        let mut first_fresh: Option<tokio::time::Instant> = None;
        loop {
            let seen = self.devices().await?;
            let matches: Vec<Snapshot> = seen
                .iter()
                .filter(|device| match mac {
                    // An explicit address bypasses the heuristic entirely. That is the escape hatch
                    // for hardware this does not recognise, and it must not be second-guessed.
                    Some(wanted) => wanted.eq_ignore_ascii_case(&device.mac),
                    None => device.is_gamepad(),
                })
                .cloned()
                .collect();

            let now = tokio::time::Instant::now();
            let worth_stopping_for = match mac {
                Some(_) => !matches.is_empty(),
                None => {
                    if matches.iter().any(Snapshot::is_fresh_and_classified) {
                        let since = *first_fresh.get_or_insert(now);
                        now - since >= SIBLING_GRACE
                    } else {
                        false
                    }
                }
            };
            if worth_stopping_for || now >= deadline {
                return Ok(Found { matches, seen });
            }
            tokio::time::sleep(DISCOVERY_POLL.min(deadline - tokio::time::Instant::now())).await;
        }
    }

    /// Watch `Paired` until it turns true, or `within` elapses.
    ///
    /// The property, not a method's return value, because bonding is asynchronous: `Connect()` comes
    /// back before the bond it triggered has completed, and `Pair()` on a bond already in flight
    /// simply never answers. `Paired` is the one thing that says whether this worked.
    async fn wait_until_paired(&self, mac: &str, within: Duration) -> bool {
        let deadline = tokio::time::Instant::now() + within;
        loop {
            let state = self
                .devices()
                .await
                .ok()
                .and_then(|all| all.into_iter().find(|d| d.mac.eq_ignore_ascii_case(mac)));
            if let Some(state) = &state
                && state.paired
            {
                tracing::info!(connected = state.connected, "bonded");
                return true;
            }
            if tokio::time::Instant::now() >= deadline {
                tracing::info!(
                    paired = false,
                    connected = state.is_some_and(|s| s.connected),
                    "still not bonded"
                );
                return false;
            }
            tokio::time::sleep(BOND_POLL.min(deadline - tokio::time::Instant::now())).await;
        }
    }

    /// Connect, pair, trust — in that order, for the reasons in this module's docs.
    async fn bond(&self, device: &Snapshot) -> Result<(), (proto::PadPairFailure, String)> {
        let proxy = DeviceProxy::builder(&self.bus)
            .path(device.path.as_ref())
            .map_err(|e| (proto::PadPairFailure::Other, e.to_string()))?
            .build()
            .await
            .map_err(|e| (proto::PadPairFailure::Other, e.to_string()))?;

        if !device.paired && device.is_classic() {
            // A BR/EDR pad: `Pair()` first, then `Connect()`. The other order — the one below, which
            // an LE pad needs — does not work on classic HID and leaves things worse than it found
            // them. Seen against a "Pro Controller" (a Switch Pro clone, class 0x2508):
            // `Connect()` on the unbonded pad spends ten seconds and answers
            // `br-connection-create-socket`, and the `Pair()` after it answers
            // `ConnectionAttemptFailed: Page Timeout` — the pad has stopped page-scanning by then,
            // and the person has to put it back into pairing mode. Done by hand in the same order,
            // `bluetoothctl connect` then `trust`, the pad ends up *Paired and Connected* with no
            // input device behind it: the light on the pad goes solid, `pad status` says connected,
            // and `padd` has nothing to open. `pair` → `connect` → `trust` is the sequence that
            // works, so it is the one this takes.
            //
            // `Pair()` on BR/EDR is synchronous and answers when the bond is done — but it is still
            // raced against `Paired`, as below, because that property is the ground truth and the
            // reply is only one way to learn it.
            let paired = tokio::select! {
                outcome = tokio::time::timeout(BOND_TIMEOUT, proxy.pair()) => match outcome {
                    Ok(Ok(())) => { tracing::info!("bonded (classic)"); true }
                    Ok(Err(e)) if is_already_paired(&e) => { tracing::info!("already bonded"); true }
                    Ok(Err(e)) => return Err((proto::PadPairFailure::Rejected, e.to_string())),
                    Err(_) => false,
                },
                bonded = self.wait_until_paired(&device.mac, BOND_TIMEOUT) => bonded,
            };
            if !paired {
                return Err((
                    proto::PadPairFailure::Timeout,
                    "the pad did not finish pairing".to_owned(),
                ));
            }

            // Now connect, which is what brings up the HID channel and hands the pad to the kernel
            // driver — `hid-nintendo`, for the clone above — so an input device appears. Soft: a
            // bonded and trusted pad reconnects by itself, so a refusal here is not worth failing a
            // pairing that succeeded. Logged at warn rather than info, though, because a classic
            // pad that bonded and will not connect is the "connected light, no input" state from
            // the other order, and worth a line in the journal.
            match tokio::time::timeout(BOND_TIMEOUT, proxy.connect()).await {
                Ok(Ok(())) => tracing::info!("connected"),
                Ok(Err(e)) => tracing::warn!(error = %e, "bonded but not connected yet"),
                Err(_) => tracing::warn!("bonded; connect did not answer in time"),
            }
        } else if !device.paired {
            // An LE pad. `Connect()` first, which is the order that works on this board — leading
            // with `Pair()` on an Xbox controller returns `AuthenticationCanceled`.
            //
            // But **soft-failed**, deliberately. A device BlueZ has never bonded with has no known
            // profile to connect to, so `Connect()` can answer
            // `br-connection-profile-unavailable` before pairing has happened — and treating that
            // as the end would refuse a pad that `Pair()` would have bonded a moment later. So the
            // preferred order is tried first and the fallback is still available, rather than the
            // order being enforced against the radio.
            let connected = match tokio::time::timeout(BOND_TIMEOUT, proxy.connect()).await {
                Ok(Ok(())) => {
                    tracing::info!("connected");
                    true
                }
                Ok(Err(e)) => {
                    tracing::info!(error = %e, "connect first failed; asking to pair");
                    false
                }
                Err(_) => {
                    tracing::info!("connect did not answer in time; asking to pair");
                    false
                }
            };

            // Did that bond it on its own? It usually does — a HID profile requires an encrypted
            // link, so connecting triggers bonding — but **it finishes a moment after `Connect()`
            // returns**, not before. Reading `Paired` immediately therefore says `false` about a
            // bond that is already in flight, and the `Pair()` that follows never answers: BlueZ
            // leaves it outstanding rather than reporting `AlreadyExists`.
            //
            // That is the whole of the "first pair times out, second one works instantly" report:
            // the first call bonded the pad, waited 30s for a reply that was never coming, and
            // returned a timeout before it could set `Trusted`.
            // Wait for a bond to land **only if a connect succeeded**, because that is the only case
            // where one is in flight. After a failed connect the wait is dead time, and dead time
            // here does damage: a pad holds pairing mode for a limited window, and spending five
            // seconds of it waiting for something that was never started is how a fresh pairing ends
            // in `AuthenticationFailed`.
            let settle = if connected {
                BOND_SETTLE
            } else {
                Duration::ZERO
            };
            if !self.wait_until_paired(&device.mac, settle).await {
                // Genuinely not bonding on its own, so ask. **Raced against the state**, not
                // trusted to answer: `Paired` turning true is the ground truth for "this worked",
                // and `Pair()`'s reply is only one of the two ways to learn it.
                let paired = tokio::select! {
                    outcome = tokio::time::timeout(BOND_TIMEOUT, proxy.pair()) => match outcome {
                        Ok(Ok(())) => { tracing::info!("bonded"); true }
                        // Something bonded it between the two calls — success, not a failure.
                        Ok(Err(e)) if is_already_paired(&e) => { tracing::info!("already bonded"); true }
                        Ok(Err(e)) => return Err((proto::PadPairFailure::Rejected, e.to_string())),
                        Err(_) => false,
                    },
                    bonded = self.wait_until_paired(&device.mac, BOND_TIMEOUT) => bonded,
                };
                if !paired {
                    return Err((
                        proto::PadPairFailure::Timeout,
                        "the pad did not finish pairing".to_owned(),
                    ));
                }

                // Connect again now that a bond exists, for the case the first attempt failed for
                // want of one. Soft too: a bonded pad reconnects by itself, so failing here is not
                // worth refusing a pairing that succeeded.
                if let Ok(Err(e)) = tokio::time::timeout(BOND_TIMEOUT, proxy.connect()).await {
                    tracing::info!(error = %e, "bonded but not connected yet");
                }
            }
        }

        // Trust is what makes the pad work after a reboot with nobody logged in: an untrusted
        // device's reconnection needs an agent to approve it, and at boot there is none. This is the
        // line whose absence looks like "it paired fine yesterday and does nothing today".
        proxy
            .set_trusted(true)
            .await
            .map_err(|e| (proto::PadPairFailure::Other, e.to_string()))?;
        Ok(())
    }
}

/// Collapse a pad that presents as two devices into the one worth bonding.
///
/// Candidates that share their unit octets — [`same_pad`] — are one pad seen over two transports,
/// and the classic face is the one to keep: it is the one that carries HID to the kernel and the one
/// `bond` knows the order for. Among faces of the same kind the lowest address wins, for the same
/// determinism the caller applies to bonded pads. Candidates that share nothing pass through, so a
/// genuine second pad in pairing mode is still refused as ambiguous.
fn one_face_per_pad(fresh: Vec<&Snapshot>) -> Vec<&Snapshot> {
    let mut kept: Vec<&Snapshot> = Vec::new();
    for candidate in fresh {
        match kept.iter_mut().find(|k| same_pad(&k.mac, &candidate.mac)) {
            Some(face) => {
                let better = match (candidate.is_classic(), face.is_classic()) {
                    (true, false) => true,
                    (false, true) => false,
                    _ => candidate.mac < face.mac,
                };
                if better {
                    tracing::info!(
                        kept = %candidate.mac,
                        dropped = %face.mac,
                        "one pad, two faces: keeping the classic one"
                    );
                    *face = candidate;
                }
            }
            None => kept.push(candidate),
        }
    }
    kept
}

/// Did BlueZ refuse this because the bond already exists?
fn is_already_paired(error: &zbus::Error) -> bool {
    matches!(error, zbus::Error::MethodError(name, _, _)
        if name.as_str() == "org.bluez.Error.AlreadyExists")
}

#[async_trait]
impl Pads for BlueZ {
    async fn status(&self) -> PadResult<Vec<proto::Pad>> {
        let mut pads: Vec<proto::Pad> = self
            .devices()
            .await?
            .into_iter()
            // Bonded pads only. Everything else BlueZ has ever seen in a scan is noise here: the
            // question this answers is "what can drive this robot", not "what is in range".
            .filter(|device| device.paired && device.is_gamepad())
            .map(|device| device.as_pad())
            .collect();
        // Connected first, then by name, so the pad someone is holding is the first line.
        pads.sort_by(|a, b| b.connected.cmp(&a.connected).then(a.name.cmp(&b.name)));
        Ok(pads)
    }

    async fn pair(&self, mac: Option<&str>, timeout: Duration) -> PadResult<proto::PadPairResult> {
        let _one_at_a_time = self.pairing.lock().await;

        let Some(adapter) = self.adapter().await? else {
            return Ok(proto::PadPairResult::Failed {
                reason: proto::PadPairFailure::NoAdapter,
                detail: Some(
                    "no Bluetooth adapter. On this board hci0 appears about 73s after power-on."
                        .to_owned(),
                ),
            });
        };

        // No short-circuit on "a pad is already bonded", deliberately. That reads as an obvious
        // optimisation and it made **adding a second pad impossible**: the bonded one is in BlueZ's
        // cache every sweep, so it always won, and the only way to pair a new pad was to forget the
        // working one first. A robot may have several pads bonded — `padd` drives whichever connects
        // — so the search runs, and `find` prefers a pad that is not yet paired.
        //
        // Idempotence is kept where it belongs instead: if the pad that turns up is already bonded,
        // `bond` skips connecting and pairing and only re-asserts `Trusted`.

        // Discovery has to be running for a first-time bond to resolve an address. A failure here
        // is worth reporting rather than working around: without it the search below can only ever
        // find devices already in BlueZ's cache.
        adapter
            .start_discovery()
            .await
            .map_err(|e| format!("cannot start Bluetooth discovery: {e}"))?;
        tracing::info!(?timeout, "looking for a gamepad in pairing mode");

        let found = self.find(mac, timeout).await;

        // Stop discovery before connecting, always — including on the error path, so a failed
        // search does not leave the adapter scanning.
        if let Err(e) = adapter.stop_discovery().await {
            tracing::warn!(error = %e, "could not stop discovery");
        }

        let found = found?;
        let device = match found.matches.as_slice() {
            [] => {
                // Name what the radio *did* see, unpaired devices first. Without this the answer is
                // "no gamepad found" and the only escape — naming an address — needs an address
                // nobody has. A pad that advertises no name and no class is invisible to the
                // heuristic and perfectly pairable by address, so this list is the difference
                // between a dead end and one more command.
                let mut others: Vec<&Snapshot> =
                    found.seen.iter().filter(|d| !d.is_gamepad()).collect();
                others.sort_by(|a, b| a.paired.cmp(&b.paired).then(a.mac.cmp(&b.mac)));
                let detail = if others.is_empty() {
                    "nothing at all turned up, not even a device this does not recognise. The pad \
                     is probably not in pairing mode: its light has to be flashing quickly."
                        .to_owned()
                } else {
                    let listed: Vec<String> = others
                        .iter()
                        .take(8)
                        .map(|d| {
                            let name = if d.name.is_empty() {
                                "(no name yet)"
                            } else {
                                &d.name
                            };
                            format!("{} {name}", d.mac)
                        })
                        .collect();
                    format!(
                        "nothing that looks like a gamepad turned up. These were in range — if one \
                         of them is the pad, pair it by address:\n  {}",
                        listed.join("\n  ")
                    )
                };
                tracing::warn!(seen = found.seen.len(), "no gamepad found");
                return Ok(proto::PadPairResult::Failed {
                    reason: proto::PadPairFailure::NotFound,
                    detail: Some(detail),
                });
            }
            [only] => only.clone(),
            several => {
                // Prefer the pads that are **not** already bonded: those are the ones someone just
                // put into pairing mode, and a pad this robot already has is not a competing answer.
                // Without this, adding a second pad in a room where the first is in range would be
                // refused as ambiguous forever.
                let fresh: Vec<&Snapshot> = several.iter().filter(|d| !d.paired).collect();
                let fresh = one_face_per_pad(fresh);
                match fresh.as_slice() {
                    [only] => (*only).clone(),
                    // Nothing new: report the bonded one, and let `bond` re-assert `Trusted`. This is
                    // the idempotent re-run, and the one case where several bonded pads are in range
                    // — either is a correct answer, so take the first by address for determinism.
                    [] => several
                        .iter()
                        .min_by(|a, b| a.mac.cmp(&b.mac))
                        .expect("several is non-empty")
                        .clone(),
                    _ => {
                        let names: Vec<String> = fresh
                            .iter()
                            .map(|d| format!("{} ({})", d.name, d.mac))
                            .collect();
                        return Ok(proto::PadPairResult::Failed {
                            reason: proto::PadPairFailure::Ambiguous,
                            detail: Some(format!(
                                "more than one pad is in pairing mode: {}",
                                names.join(", ")
                            )),
                        });
                    }
                }
            }
        };

        // The agent, alive only for this bond and scoped to this device. Registered *after* the
        // device is known, which is what makes scoping possible at all.
        let agent_path = ObjectPath::try_from(AGENT_PATH).map_err(|e| e.to_string())?;
        self.bus
            .object_server()
            .at(
                &agent_path,
                PairingAgent {
                    device: device.path.clone(),
                },
            )
            .await
            .map_err(|e| format!("cannot serve a pairing agent: {e}"))?;

        let manager = AgentManagerProxy::new(&self.bus)
            .await
            .map_err(|e| e.to_string())?;
        let registered = manager.register_agent(&agent_path, AGENT_CAPABILITY).await;
        if let Err(e) = &registered {
            // Not fatal. A pad is just-works, so bluetoothd may never need to ask anyone — and if
            // it does, `btd`'s default agent is still there to answer.
            tracing::warn!(error = %e, "could not register a pairing agent; relying on the default");
        }

        // Becoming the *default* agent is what makes `NoInputNoOutput` reach the controller.
        // bluetoothd pushes an IO capability down to the adapter from the default agent only;
        // registering an agent without claiming that role leaves the adapter on the kernel's
        // default, `DisplayYesNo`. That capability puts MITM in the pairing request, which makes
        // SMP choose numeric comparison over just-works — so bluetoothd raises a
        // `RequestConfirmation` that arrives at no agent at all, and the pad waits until the link
        // supervision times out. Observed as `AuthenticationCanceled` after ~17s, with an
        // unanswered `User Confirmation Request` in `btmon` and nothing in this daemon's log.
        //
        // Claiming it for the pairing window is safe even while `btd` serves phones: this agent
        // answers a phone's bond the same just-works way `btd`'s own does, `unregister_agent`
        // below hands the role back, and `btd` only holds it when pairing is required at all.
        if registered.is_ok()
            && let Err(e) = manager.request_default_agent(&agent_path).await
        {
            tracing::warn!(
                error = %e,
                "could not become the default pairing agent; a pad that needs confirmation will \
                 stall"
            );
        }

        let outcome = self.bond(&device).await;

        if registered.is_ok()
            && let Err(e) = manager.unregister_agent(&agent_path).await
        {
            tracing::warn!(error = %e, "could not unregister the pairing agent");
        }
        if let Err(e) = self
            .bus
            .object_server()
            .remove::<PairingAgent, _>(&agent_path)
            .await
        {
            tracing::warn!(error = %e, "could not withdraw the pairing agent");
        }

        if let Err((reason, detail)) = outcome {
            tracing::warn!(mac = %device.mac, ?reason, %detail, "pairing failed");
            return Ok(proto::PadPairResult::Failed {
                reason,
                detail: Some(detail),
            });
        }

        // Re-read rather than assume: what BlueZ ended up with is what the caller should be told,
        // including a pad that bonded but has not connected yet.
        let pad = self
            .devices()
            .await?
            .into_iter()
            .find(|d| d.mac.eq_ignore_ascii_case(&device.mac))
            .map(|d| d.as_pad())
            .unwrap_or_else(|| proto::Pad {
                paired: true,
                trusted: true,
                ..device.as_pad()
            });
        tracing::warn!(mac = %pad.mac, name = %pad.name, "gamepad paired and trusted");
        Ok(proto::PadPairResult::Paired { pad })
    }

    async fn forget(&self, mac: &str) -> PadResult<proto::PadForgetResult> {
        let Some(adapter) = self.adapter().await? else {
            // No adapter, so nothing is bonded to it as far as anyone can tell. `removed: false` is
            // the honest answer and matches what forgetting an unknown pad returns.
            return Ok(proto::PadForgetResult { removed: false });
        };

        let Some(device) = self
            .devices()
            .await?
            .into_iter()
            .find(|d| d.mac.eq_ignore_ascii_case(mac))
        else {
            return Ok(proto::PadForgetResult { removed: false });
        };

        adapter
            .remove_device(&device.path.as_ref())
            .await
            .map_err(|e| format!("bluetoothd would not remove {mac}: {e}"))?;
        tracing::info!(mac, "pad forgotten");
        Ok(proto::PadForgetResult { removed: true })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn face(mac: &str, name: &str, class: Option<u32>) -> Snapshot {
        Snapshot {
            path: OwnedObjectPath::try_from(format!(
                "/org/bluez/hci0/dev_{}",
                mac.replace(':', "_")
            ))
            .unwrap(),
            mac: mac.to_owned(),
            name: name.to_owned(),
            icon: None,
            class,
            appearance: None,
            paired: false,
            trusted: false,
            connected: false,
        }
    }

    /// The Pro Controller clone as the radio reports it: an LE face first, the classic one after.
    /// One pad comes out, and it is the classic one whichever order they arrived in.
    #[test]
    fn a_pad_with_two_faces_is_one_candidate_and_the_classic_face_wins() {
        let le = face("98:B6:ED:28:06:09", "BLE Controller_280609", None);
        let classic = face("98:B6:E9:28:06:09", "Pro Controller", Some(0x2508));

        for order in [vec![&le, &classic], vec![&classic, &le]] {
            let kept = one_face_per_pad(order);
            assert_eq!(kept.len(), 1);
            assert_eq!(kept[0].mac, classic.mac);
        }
    }

    /// Two different pads stay two candidates — the ambiguity refusal downstream depends on it.
    #[test]
    fn two_pads_stay_two_candidates() {
        let a = face("98:B6:E9:28:06:09", "Pro Controller", Some(0x2508));
        let b = face("78:86:2E:BB:13:28", "Xbox Wireless Controller", None);
        assert_eq!(one_face_per_pad(vec![&a, &b]).len(), 2);
    }
}

```
