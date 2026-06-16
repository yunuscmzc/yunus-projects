import numpy as np
import pandas as pd

MODEL_STATE = {}

def ewma_cusum_state_init():
    return {"m": 0.0, "v": 0.0, "cnt": 0, "C_prev": 0.0}

def ewma_cusum_update(
    state, x_t,
    lam=0.25, k_ref=0.57,
    min_obs=15, z_cap=5.0, v_floor=1e-6
):
    x_t = float(x_t)

    # Compute CUSUM increment using PREVIOUS baseline
    if state["cnt"] >= min_obs and state["v"] > v_floor:
        sd = np.sqrt(max(state["v"], v_floor))
        z = np.clip((x_t - state["m"]) / sd, -z_cap, z_cap)
        C_t = max(0.0, state["C_prev"] + (z - k_ref))
    else:
        C_t = 0.0

    # EWMA baseline update
    if state["cnt"] == 0:
        state["m"] = x_t
        state["v"] = 0.0
    else:
        m_prev = state["m"]
        state["m"] = lam * x_t + (1 - lam) * m_prev
        dev = x_t - m_prev
        state["v"] = lam * (dev * dev) + (1 - lam) * state["v"]

    state["cnt"] += 1
    state["C_prev"] = C_t
    return C_t

def last_val(df, col):
    if col not in df.columns or df.empty:
        return 0.0
    v = df[col].iloc[-1]
    return 0.0 if pd.isna(v) else float(v)

def push_roll(buf, val, k):
    buf.append(float(val))
    if len(buf) > k:
        buf.pop(0)
    return sum(buf)

def init_match_state(roll=5):
    return {
        "last": {},
        "buf_XA": [], "buf_XD": [],
        "buf_RA": [], "buf_RD": [],
        "buf_ZH": [], "buf_ZA": [],
        "sx": ewma_cusum_state_init(),
        "sy": ewma_cusum_state_init(),
        "t": -1,
        "cooldown_until": -1,
        "armed": True,
        "roll": roll
    }

def predict(test_data, prev_predictions):
    """
    Predict whether an event will occur in the FUTURE (t+1 or later).
    """

    if test_data is None or test_data.empty:
        return 0

    # Identify match
    match_id = (
        test_data["match_id"].iloc[-1]
        if "match_id" in test_data.columns
        else "__single_match__"
    )

    if match_id not in MODEL_STATE:
        MODEL_STATE[match_id] = init_match_state()

    st = MODEL_STATE[match_id]
    st["t"] += 1
    t = st["t"]

    # Parameters (FINAL TUNED)
    hX, hY = 2, 2
    z_limit = 8
    warmup = 20
    cooldown = 11
    hX_off = 1.5 * hX
    hY_off = 1.5 * hY
    z_off = max(0, z_limit - 2)

    # Delta helper
    def delta(col):
        cur = last_val(test_data, col)
        prev = st["last"].get(col, cur)
        st["last"][col] = cur
        return max(0.0, cur - prev)

    # Deltas
    dAh, dAa = delta("ATTACKS - home"), delta("ATTACKS - away")
    dDh, dDa = delta("DANGEROUS_ATTACKS - home"), delta("DANGEROUS_ATTACKS - away")
    dKPh, dKPa = delta("KEY_PASSES - home"), delta("KEY_PASSES - away")
    dCOh, dCOa = delta("CORNERS - home"), delta("CORNERS - away")
    dSTh, dSTa = delta("SHOTS_ON_TARGET - home"), delta("SHOTS_ON_TARGET - away")
    PEN = delta("PENALTIES - home") + delta("PENALTIES - away")

    # X
    X = (
        push_roll(st["buf_XA"], dAh + dAa, st["roll"]) +
        2 * push_roll(st["buf_XD"], dDh + dDa, st["roll"])
    )

    # Y
    eps = 1e-6
    RA = abs(dAh - dAa) / (dAh + dAa + eps)
    RD = abs(dDh - dDa) / (dDh + dDa + eps)
    Y = (
        push_roll(st["buf_RA"], RA, st["roll"]) +
        3 * push_roll(st["buf_RD"], RD, st["roll"])
    )

    # Z (directional rolling chance)
    Zh = push_roll(st["buf_ZH"], 2*dKPh + 1.5*dCOh + 2.5*dSTh, st["roll"])
    Za = push_roll(st["buf_ZA"], 2*dKPa + 1.5*dCOa + 2.5*dSTa, st["roll"])
    Z = max(Zh, Za)

    # Charts
    CX = ewma_cusum_update(st["sx"], X)
    CY = ewma_cusum_update(st["sy"], Y)

    # Warmup / cooldown
    if t <= warmup or t < st["cooldown_until"]:
        return 0

    # Re-arming
    if not st["armed"]:
        if CX < hX_off and CY < hY_off and Z < z_off and PEN == 0:
            st["armed"] = True
        else:
            return 0

    # Trigger (predicts FUTURE event)
    if PEN > 0 or CX > hX or CY > hY or Z >= z_limit:
        st["cooldown_until"] = t + cooldown
        st["armed"] = False
        return 1

    return 0
